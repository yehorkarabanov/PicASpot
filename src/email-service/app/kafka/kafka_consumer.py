import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer

from app.email.tasks import user_password_reset_mail, user_verify_mail
from app.settings import settings

logger = logging.getLogger(__name__)


class KafkaConsumer:
    def __init__(self):
        self.consumer: AIOKafkaConsumer | None = None
        self.running = False
        self._task: asyncio.Task | None = None

    async def start(self):
        """Start the Kafka consumer and subscribe to topics."""
        logger.info(
            "Starting Kafka consumer",
            extra={
                "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                "consumer_group": settings.KAFKA_EMAIL_CONSUMER_GROUP,
                "topics": [
                    settings.KAFKA_VERIFICATION_EMAIL_TOPIC,
                    settings.KAFKA_RESET_PASSWORD_EMAIL_TOPIC,
                ],
            },
        )
        try:
            self.consumer = AIOKafkaConsumer(
                settings.KAFKA_VERIFICATION_EMAIL_TOPIC,
                settings.KAFKA_RESET_PASSWORD_EMAIL_TOPIC,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=settings.KAFKA_EMAIL_CONSUMER_GROUP,
                auto_offset_reset="earliest",
                enable_auto_commit=False,
            )

            await self.consumer.start()
            logger.info(
                "Kafka consumer started successfully",
                extra={
                    "consumer_group": settings.KAFKA_EMAIL_CONSUMER_GROUP,
                },
            )
        except Exception as e:
            logger.error(
                "Failed to start Kafka consumer",
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
                pass

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
        try:
            message_data = json.loads(msg.value.decode("utf-8"))
            logger.info(f"Received message from topic: {msg.topic}")

            if msg.topic == settings.KAFKA_VERIFICATION_EMAIL_TOPIC:
                await user_verify_mail(
                    recipient=message_data["email"],
                    link=message_data["link"],
                    username=message_data["username"],
                )
            elif msg.topic == settings.KAFKA_RESET_PASSWORD_EMAIL_TOPIC:
                await user_password_reset_mail(
                    recipient=message_data["email"],
                    link=message_data["link"],
                    username=message_data["username"],
                )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON message: {e}")
            await self.consumer.commit()
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def consume_messages(self):
        self.running = True
        self._task = asyncio.create_task(self._consume_loop())
        logger.info("Starting message consumer loop")

    async def _consume_loop(self):
        """Main message consumption loop using async iterator."""
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
            await self.consumer.stop()


kafka_consumer = KafkaConsumer()
