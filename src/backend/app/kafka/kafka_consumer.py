import asyncio
import json
import logging
import uuid

from aiokafka import AIOKafkaConsumer
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.manager import async_session_maker
from app.landmark.models import Landmark
from app.landmark.repository import LandmarkRepository
from app.settings import settings
from app.unlock.models import Unlock
from app.unlock.repository import UnlockRepository

from .schemas import UnlockVerifyResult

logger = logging.getLogger(__name__)


class KafkaConsumer:
    """Asynchronous Kafka consumer for processing verification results.

    This consumer handles image verification results from the image-service
    and creates/updates unlock records accordingly.
    """

    def __init__(self):
        """Initialize the Kafka consumer."""
        self.consumer: AIOKafkaConsumer | None = None
        self.running = False
        self._task: asyncio.Task | None = None

    async def start(self, max_retries: int = 5, retry_delay: int = 2):
        """Start the Kafka consumer and subscribe to topics.

        Args:
            max_retries: Maximum number of connection attempts.
            retry_delay: Delay in seconds between retry attempts.

        Raises:
            Exception: If the consumer fails to start after all retry attempts.
        """
        for attempt in range(max_retries + 1):
            try:
                logger.info(
                    "Starting Kafka consumer",
                    extra={
                        "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                        "consumer_group": settings.KAFKA_BACKEND_CONSUMER_GROUP,
                        "topics": [settings.KAFKA_VERIFY_IMAGE_RESULT_TOPIC],
                    },
                )
                self.consumer = AIOKafkaConsumer(
                    settings.KAFKA_VERIFY_IMAGE_RESULT_TOPIC,
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    group_id=settings.KAFKA_BACKEND_CONSUMER_GROUP,
                    auto_offset_reset="earliest",
                    enable_auto_commit=False,
                )

                await self.consumer.start()
                logger.info(
                    "Kafka consumer started successfully",
                    extra={"consumer_group": settings.KAFKA_BACKEND_CONSUMER_GROUP},
                )
                break
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(
                        f"Attempt {attempt + 1} failed, retrying in {retry_delay} seconds",
                        extra={"error": str(e)},
                    )
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(
                        "Failed to start Kafka consumer after all retries",
                        exc_info=True,
                        extra={
                            "error": str(e),
                            "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                        },
                    )
                    raise

    async def stop(self):
        """Stop the Kafka consumer gracefully."""
        logger.info("Stopping Kafka consumer")
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
                logger.debug("Consumer task cancelled successfully")
            except asyncio.CancelledError:
                logger.debug("Consumer task cancellation acknowledged")

        if self.consumer:
            try:
                await self.consumer.stop()
                logger.info("Kafka consumer stopped successfully")
            except Exception as e:
                logger.error(
                    "Error stopping Kafka consumer",
                    exc_info=True,
                    extra={"error": str(e)},
                )

    async def process_message(self, msg, session: AsyncSession):
        """Process a single Kafka message.

        Args:
            msg: The Kafka message object.
            session: Database session for creating unlock records.
        """
        try:
            message_data = json.loads(msg.value.decode("utf-8"))
            logger.info(
                f"Received verification result from topic: {msg.topic}",
                extra={"data": message_data},
            )

            if msg.topic == settings.KAFKA_VERIFY_IMAGE_RESULT_TOPIC:
                try:
                    result = UnlockVerifyResult(**message_data)
                except ValidationError as e:
                    logger.error(
                        f"Invalid message format: {e}",
                        extra={"data": message_data},
                    )
                    return

                await self._handle_verification_result(result, session)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON message: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)

    async def _handle_verification_result(
        self, result: UnlockVerifyResult, session: AsyncSession
    ):
        """Handle verification result by creating/rejecting unlock.

        Args:
            result: The verification result from image-service.
            session: Database session.
        """
        user_id = uuid.UUID(result.user_id)
        landmark_id = uuid.UUID(result.landmark_id)

        # Get landmark and unlock repositories
        landmark_repo = LandmarkRepository(session, Landmark)
        unlock_repo = UnlockRepository(session, Unlock)

        # Check if unlock already exists
        existing_unlock = await unlock_repo.get_by_user_and_landmark(
            user_id=user_id, landmark_id=landmark_id
        )

        if existing_unlock:
            logger.warning(
                "Unlock already exists, skipping",
                extra={
                    "user_id": str(user_id),
                    "landmark_id": str(landmark_id),
                },
            )
            return

        if result.success:
            # Get landmark to get area_id
            landmark = await landmark_repo.get_by_id(landmark_id)
            if not landmark:
                logger.error(
                    "Landmark not found for successful verification",
                    extra={"landmark_id": str(landmark_id)},
                )
                return

            # Create unlock record
            unlock = Unlock(
                user_id=user_id,
                landmark_id=landmark_id,
                area_id=landmark.area_id,
                photo_url=result.photo_url,
            )
            session.add(unlock)
            await session.commit()

            logger.info(
                "Unlock created successfully",
                extra={
                    "user_id": str(user_id),
                    "landmark_id": str(landmark_id),
                    "similarity_score": result.similarity_score,
                },
            )
        else:
            # Handle failed verification
            logger.info(
                "Verification failed, unlock not created",
                extra={
                    "user_id": str(user_id),
                    "landmark_id": str(landmark_id),
                    "similarity_score": result.similarity_score,
                    "error": result.error,
                },
            )
            # TODO: Optionally delete the uploaded photo or notify user

    async def consume_messages(self):
        """Start consuming messages from Kafka topics."""
        self.running = True
        self._task = asyncio.create_task(self._consume_loop())
        logger.info("Starting message consumer loop")

    async def _consume_loop(self):
        """Main message consumption loop."""
        try:
            async for msg in self.consumer:
                if not self.running:
                    break
                try:
                    # Get a fresh database session for each message
                    async with async_session_maker() as session:
                        await self.process_message(msg, session)
                        await self.consumer.commit()
                except Exception as e:
                    logger.error(f"Failed to process message, skipping commit: {e}")
        except Exception as e:
            logger.exception(f"Error in consumption loop: {e}")
        finally:
            if self.consumer:
                await self.consumer.stop()


kafka_consumer = KafkaConsumer()
