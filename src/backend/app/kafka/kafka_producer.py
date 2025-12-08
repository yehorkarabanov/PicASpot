import asyncio
import json
import logging
from typing import Any

from aiokafka import AIOKafkaProducer

from app.settings import settings

from .schemas import ResetPasswordEmailMessage, VerificationEmailMessage

logger = logging.getLogger(__name__)


class KafkaProducer:
    """Asynchronous Kafka producer for sending email-related messages."""

    def __init__(self):
        self.producer: AIOKafkaProducer | None = None
        self._started = False

    async def start(self, max_retries: int = 5, retry_delay: int = 2):
        """Start the Kafka producer with retry logic."""
        if self._started:
            logger.info("Kafka producer is already started")
            return

        for attempt in range(max_retries):
            try:
                self.producer = AIOKafkaProducer(
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS_STRING,
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

    async def stop(self):
        """Stop the Kafka producer."""
        if self.producer and self._started:
            await self.producer.stop()
            self._started = False
            logger.info("Kafka producer stopped successfully")

    async def health_check(self) -> bool:
        """Check if the Kafka producer is healthy and connected."""
        if not self.producer or not self._started:
            return False
        try:
            return self.producer.bootstrap_connected()
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False

    async def _send_message(self, topic: str, value: dict[str, Any]) -> bool:
        """Send a message to the specified Kafka topic."""
        if not self.producer or not self._started:
            raise RuntimeError("Kafka producer is not started")

        try:
            await self.producer.send_and_wait(
                topic=topic, value=json.dumps(value).encode("utf-8")
            )
            logger.info(f"Message sent to topic {topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message to topic {topic}: {e}")
            return False

    async def send_password_reset_message(
        self, message: ResetPasswordEmailMessage
    ) -> bool:
        """Send a password reset email message."""
        return await self._send_message(
            topic=settings.KAFKA_RESET_PASSWORD_EMAIL_TOPIC,
            value=message.model_dump(),
        )

    async def send_verification_email_message(
        self, message: VerificationEmailMessage
    ) -> bool:
        """Send a verification email message."""
        return await self._send_message(
            topic=settings.KAFKA_VERIFICATION_EMAIL_TOPIC,
            value=message.model_dump(),
        )


kafka_producer = KafkaProducer()
