import asyncio
import json
import logging
from typing import Any

from aiokafka import AIOKafkaProducer

from app.settings import settings

from .schemas import (
    ResetPasswordEmailMessage,
    UnlockVerifyMessage,
    VerificationEmailMessage,
)

logger = logging.getLogger(__name__)


class KafkaProducer:
    """Asynchronous Kafka producer for sending email-related messages.

    This class manages the lifecycle of a Kafka producer, including connection
    management, message sending, and health monitoring. It implements retry logic
    for resilient connections and provides type-safe methods for different message types.

    Attributes:
        producer (AIOKafkaProducer | None): The underlying aiokafka producer instance.
        _started (bool): Internal flag indicating whether the producer has been started.

    Note:
        The producer must be started with `start()` before sending messages and
        should be properly stopped with `stop()` when done.
    """

    def __init__(self):
        """Initialize the Kafka producer.

        Creates a new KafkaProducer instance with uninitialized producer and
        started flag set to False. The actual connection is established when
        calling `start()`.
        """
        self.producer: AIOKafkaProducer | None = None
        self._started = False

    async def start(self, max_retries: int = 5, retry_delay: int = 2):
        """Start the Kafka producer with retry logic.

        Establishes connection to the Kafka cluster with exponential backoff retry
        mechanism. If the producer is already started, this method returns immediately.

        Args:
            max_retries (int, optional): Maximum number of connection attempts.
                Defaults to 5.
            retry_delay (int, optional): Delay in seconds between retry attempts.
                Defaults to 2.

        Raises:
            RuntimeError: If the producer fails to connect after all retry attempts.

        Note:
            The method will log warnings for failed attempts and an error for the
            final failure before raising RuntimeError.
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

    async def stop(self):
        """Stop the Kafka producer gracefully.

        Closes the connection to the Kafka cluster and releases resources.
        This method is idempotent and safe to call multiple times.

        Note:
            After stopping, the producer can be restarted by calling `start()` again.
        """
        if self.producer and self._started:
            await self.producer.stop()
            self._started = False
            logger.info("Kafka producer stopped successfully")
        else:
            logger.info("Kafka producer is not started or already stopped")

    async def health_check(self) -> bool:
        """Check if the Kafka producer is healthy and connected.

        Performs a health check by attempting to fetch cluster metadata.
        This is useful for monitoring and readiness checks.

        Returns:
            bool: True if the producer is healthy and can communicate with the
                Kafka cluster, False otherwise.

        Note:
            This method will return False if the producer is not started or if
            there's any connectivity issue with the Kafka cluster.
        """
        if not self.producer or not self._started:
            return False
        try:
            if not await self.producer.client.fetch_all_metadata():
                return False
            return True
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False

    async def _send_message(self, topic: str, value: dict[str, Any]) -> bool:
        """Send a message to the specified Kafka topic.

        Internal method that handles the actual message serialization and sending.
        Messages are JSON-encoded and sent with guaranteed delivery (send_and_wait).

        Args:
            topic (str): The Kafka topic name to send the message to.
            value (dict[str, Any]): The message payload as a dictionary.

        Returns:
            bool: True if the message was successfully sent, False if an error occurred.

        Raises:
            RuntimeError: If the producer is not started.

        Note:
            This is an internal method. Use the type-safe public methods like
            `send_verification_email_message()` instead.
        """
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
        """Send a password reset email message to Kafka.

        Publishes a password reset message to the configured Kafka topic for
        asynchronous processing by the email service.

        Args:
            message (ResetPasswordEmailMessage): The password reset message containing
                recipient email, username, and reset link.

        Returns:
            bool: True if the message was successfully sent to Kafka, False otherwise.

        Example:
            >>> message = ResetPasswordEmailMessage(
            ...     email="user@example.com",
            ...     username="johndoe",
            ...     link="https://example.com/reset?token=xyz789"
            ... )
            >>> success = await kafka_producer.send_password_reset_message(message)

        Note:
            The producer must be started before calling this method.
        """
        return await self._send_message(
            topic=settings.KAFKA_RESET_PASSWORD_EMAIL_TOPIC,
            value=message.model_dump(),
        )

    async def send_verification_email_message(
        self, message: VerificationEmailMessage
    ) -> bool:
        """Send a verification email message to Kafka.

        Publishes a verification message to the configured Kafka topic for
        asynchronous processing by the email service.

        Args:
            message (VerificationEmailMessage): The verification message containing
                recipient email, username, and verification link.

        Returns:
            bool: True if the message was successfully sent to Kafka, False otherwise.

        Example:
            >>> message = VerificationEmailMessage(
            ...     email="newuser@example.com",
            ...     username="janedoe",
            ...     link="https://example.com/verify?token=abc123"
            ... )
            >>> success = await kafka_producer.send_verification_email_message(message)

        Note:
            The producer must be started before calling this method.
        """
        return await self._send_message(
            topic=settings.KAFKA_VERIFICATION_EMAIL_TOPIC,
            value=message.model_dump(),
        )

    async def send_unlock_verify_message(self, message: UnlockVerifyMessage) -> bool:
        """Send an unlock verification request message.

        Publishes an unlock verification message to the configured Kafka topic for
        asynchronous processing by the email service.

        Args:
            message (UnlockVerifyMessage): The unlock verification message containing
                recipient email, username, and verification link.

        Returns:
            bool: True if the message was successfully sent to Kafka, False otherwise.

        Example:
            >>> message = UnlockVerifyMessage(
            ...     email="user@example.com",
            ...     username="johndoe",
            ...     link="https://example.com/verify-unlock?token=xyz789"
            ... )
            >>> success = await kafka_producer.send_unlock_verify_message(message)

        Note:
            The producer must be started before calling this method.
        """
        return await self._send_message(
            topic=settings.KAFKA_VERIFY_IMAGE_TOPIC,
            value=message.model_dump(),
        )


kafka_producer = KafkaProducer()
