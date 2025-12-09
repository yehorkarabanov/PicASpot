import asyncio
import logging

from aiokafka import AIOKafkaConsumer

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

    async def consume_messages(self):
        """Consume and process messages from Kafka topics."""
        if not self.consumer:
            logger.error("Cannot consume messages: Kafka consumer is not started")
            raise RuntimeError("Kafka consumer is not started.")

        self.running = True
        logger.info(
            "Starting message consumption loop",
            extra={"consumer_group": settings.KAFKA_EMAIL_CONSUMER_GROUP},
        )

        try:
            async for msg in self.consumer:
                try:
                    message_value = msg.value.decode("utf-8")
                    logger.info(
                        "Received Kafka message",
                        extra={
                            "topic": msg.topic,
                            "partition": msg.partition,
                            "offset": msg.offset,
                            "key": msg.key.decode("utf-8") if msg.key else None,
                            "message_size": len(msg.value),
                        },
                    )
                    logger.debug(
                        "Message content",
                        extra={
                            "topic": msg.topic,
                            "message": message_value,
                        },
                    )

                    # Process the message here
                    # TODO: Implement message processing logic

                    # Commit offset after successful processing
                    await self.consumer.commit()
                    logger.debug(
                        "Message processed and offset committed",
                        extra={
                            "topic": msg.topic,
                            "partition": msg.partition,
                            "offset": msg.offset,
                        },
                    )

                except Exception as e:
                    logger.error(
                        "Error processing Kafka message",
                        exc_info=True,
                        extra={
                            "topic": msg.topic,
                            "partition": msg.partition,
                            "offset": msg.offset,
                            "error": str(e),
                        },
                    )
                    # Decide whether to commit offset on error
                    # For now, we'll continue to next message
                    continue

        except asyncio.CancelledError:
            logger.info("Message consumption cancelled")
            raise
        except Exception as e:
            logger.error(
                "Fatal error in message consumption loop",
                exc_info=True,
                extra={"error": str(e)},
            )
            raise
        finally:
            logger.info("Message consumption loop ended")


kafka_consumer = KafkaConsumer()
