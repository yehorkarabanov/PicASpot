import asyncio
import json
import logging

from aiokafka import AIOKafkaProducer

from app.settings import settings

from .schemas import UnlockVerifyResult

logger = logging.getLogger(__name__)


class KafkaProducer:
    """Asynchronous Kafka producer for sending verification results.

    This class manages the lifecycle of a Kafka producer, including connection
    management, message sending, and health monitoring.

    Attributes:
        producer (AIOKafkaProducer | None): The underlying aiokafka producer instance.
        _started (bool): Flag indicating whether the producer has been started.
    """

    def __init__(self):
        """Initialize the Kafka producer."""
        self.producer: AIOKafkaProducer | None = None
        self._started = False

    async def start(self, max_retries: int = 5, retry_delay: int = 2) -> None:
        """Start the Kafka producer with retry logic.

        Args:
            max_retries: Maximum number of connection attempts.
            retry_delay: Delay in seconds between retry attempts.

        Raises:
            RuntimeError: If the producer fails to connect after all retry attempts.
        """
        if self._started:
            logger.info("Kafka producer is already started")
            return

        for attempt in range(max_retries):
            try:
                self.producer = AIOKafkaProducer(
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                )
                await self.producer.start()
                self._started = True
                logger.info("Kafka producer started successfully")
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Kafka producer initialization failed (attempt {attempt + 1}/{max_retries}): {e}"
                    )
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(
                        f"Kafka producer initialization failed after {max_retries} attempts: {e}"
                    )
                    raise RuntimeError("Failed to initialize Kafka producer") from e

    async def stop(self) -> None:
        """Stop the Kafka producer gracefully."""
        if self.producer and self._started:
            await self.producer.stop()
            self._started = False
            logger.info("Kafka producer stopped successfully")
        else:
            logger.info("Kafka producer is not started or already stopped")

    async def health_check(self) -> bool:
        """Check if the Kafka producer is healthy and connected."""
        if not self.producer or not self._started:
            return False
        try:
            if not await self.producer.client.fetch_all_metadata():
                return False
            return True
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False

    async def send_verification_result(self, result: UnlockVerifyResult) -> bool:
        """Send a verification result message to Kafka.

        Args:
            result: The verification result to send.

        Returns:
            bool: True if the message was successfully sent, False otherwise.

        Raises:
            RuntimeError: If the producer is not started.
        """
        if not self.producer or not self._started:
            raise RuntimeError("Kafka producer is not started")

        try:
            await self.producer.send_and_wait(
                topic=settings.KAFKA_VERIFY_IMAGE_RESULT_TOPIC,
                value=json.dumps(result.model_dump()).encode("utf-8"),
            )
            logger.info(
                f"Verification result sent to topic {settings.KAFKA_VERIFY_IMAGE_RESULT_TOPIC}",
                extra={
                    "user_id": result.user_id,
                    "landmark_id": result.landmark_id,
                    "success": result.success,
                },
            )
            return True
        except Exception as e:
            logger.error(
                f"Failed to send verification result: {e}",
                extra={
                    "user_id": result.user_id,
                    "landmark_id": result.landmark_id,
                },
            )
            return False


kafka_producer = KafkaProducer()
