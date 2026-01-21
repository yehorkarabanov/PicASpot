import asyncio
import json
import logging
import uuid

from aiokafka import AIOKafkaConsumer
from fastapi_injectable import async_get_injected_obj
from pydantic import ValidationError

from app.settings import settings

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

    async def process_message(self, msg):
        """Process a single Kafka message.

        Args:
            msg: The Kafka message object.
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

                await self._handle_verification_result(result)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON message: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)

    async def _handle_verification_result(self, result: UnlockVerifyResult):
        """Handle verification result by creating/rejecting unlock.

        Args:
            result: The verification result from image-service.
            session: Database session.
        """
        from app.unlock.dependencies import get_unlock_service

        unlock_service = await async_get_injected_obj(get_unlock_service)
        await unlock_service.handle_verification_result(
            attempt_id=uuid.UUID(result.attempt_id),
            success=result.success,
            photo_url=result.photo_url,
            similarity_score=result.similarity_score,
            error=result.error,
        )

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
                    await self.process_message(msg)
                    await self.consumer.commit()
                except Exception as e:
                    logger.error(f"Failed to process message, skipping commit: {e}")
        except Exception as e:
            logger.exception(f"Error in consumption loop: {e}")
        finally:
            if self.consumer:
                await self.consumer.stop()


kafka_consumer = KafkaConsumer()
