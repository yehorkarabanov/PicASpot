"""Kafka consumer for email events."""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Any

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError, KafkaError
from pydantic import ValidationError

from .core.logging_config import setup_logging
from .handlers.email_manager import EmailManager, metrics
from .schemas import EmailEvent
from .settings import settings

setup_logging()
logger = logging.getLogger(__name__)


class EmailConsumer:
    """Kafka consumer for processing email events."""

    def __init__(self):
        """Initialize the email consumer."""
        self.consumer: AIOKafkaConsumer | None = None
        self.email_manager = EmailManager()
        self.running = False
        self.started_at: datetime | None = None
        self.messages_processed = 0
        self.messages_failed = 0
        self._shutdown_event = asyncio.Event()
        self._health_check_task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start the Kafka consumer with connection retry logic."""
        logger.info("=" * 60)
        logger.info("Starting Email Service Consumer")
        logger.info("=" * 60)
        logger.info("Service: %s v%s", settings.SERVICE_NAME, settings.VERSION)
        logger.info("Kafka brokers: %s", settings.KAFKA_BOOTSTRAP_SERVERS)
        logger.info("Topic: %s", settings.KAFKA_EMAIL_TOPIC)
        logger.info("Consumer group: %s", settings.KAFKA_CONSUMER_GROUP)
        logger.info("Debug mode: %s", settings.DEBUG)

        max_retries = 5
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                self.consumer = AIOKafkaConsumer(
                    settings.KAFKA_EMAIL_TOPIC,
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    group_id=settings.KAFKA_CONSUMER_GROUP,
                    auto_offset_reset=settings.KAFKA_AUTO_OFFSET_RESET,
                    enable_auto_commit=True,
                    max_poll_records=settings.KAFKA_MAX_POLL_RECORDS,
                    session_timeout_ms=settings.KAFKA_SESSION_TIMEOUT_MS,
                    heartbeat_interval_ms=settings.KAFKA_HEARTBEAT_INTERVAL_MS,
                    max_poll_interval_ms=settings.KAFKA_MAX_POLL_INTERVAL_MS,
                    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                )

                await self.consumer.start()
                self.running = True
                self.started_at = datetime.now()
                logger.info("✓ Email service consumer started successfully")
                logger.info("=" * 60)
                return

            except KafkaConnectionError as e:
                logger.warning(
                    "Failed to connect to Kafka (attempt %d/%d): %s",
                    attempt + 1,
                    max_retries,
                    str(e),
                )
                if attempt < max_retries - 1:
                    logger.info("Retrying in %d seconds...", retry_delay)
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(
                        "Failed to connect to Kafka after %d attempts", max_retries
                    )
                    raise

    async def stop(self) -> None:
        """Stop the Kafka consumer gracefully."""
        logger.info("=" * 60)
        logger.info("Shutting down email service consumer...")
        self.running = False

        # Cancel health check task
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        # Stop consumer
        if self.consumer:
            try:
                await self.consumer.stop()
                logger.info("✓ Kafka consumer stopped")
            except Exception as e:
                logger.error("Error stopping consumer: %s", str(e))

        # Log final statistics
        uptime = (
            (datetime.now() - self.started_at).total_seconds() if self.started_at else 0
        )
        email_stats = metrics.get_stats()

        logger.info("=" * 60)
        logger.info("Final Statistics:")
        logger.info("  Uptime: %.2f seconds", uptime)
        logger.info("  Messages processed: %d", self.messages_processed)
        logger.info("  Messages failed: %d", self.messages_failed)
        logger.info("  Emails sent: %d", email_stats["emails_sent"])
        logger.info("  Emails failed: %d", email_stats["emails_failed"])
        logger.info("  Emails retried: %d", email_stats["emails_retried"])
        logger.info("=" * 60)
        logger.info("Email service consumer stopped")

    async def health_check_loop(self) -> None:
        """Periodic health check and statistics logging."""
        while self.running:
            try:
                await asyncio.sleep(60)  # Log stats every minute
                if not self.running:
                    break

                uptime = (
                    (datetime.now() - self.started_at).total_seconds()
                    if self.started_at
                    else 0
                )
                email_stats = metrics.get_stats()

                logger.info(
                    "Health check - Uptime: %.0fs | Processed: %d | Failed: %d | Emails sent: %d",
                    uptime,
                    self.messages_processed,
                    self.messages_failed,
                    email_stats["emails_sent"],
                )
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in health check: %s", str(e))

    async def consume(self) -> None:
        """Consume and process email events from Kafka."""
        logger.info("Starting to consume messages from Kafka...")

        try:
            async for msg in self.consumer:
                if not self.running:
                    logger.info("Consumer stopped, breaking message loop")
                    break

                start_time = datetime.now()

                try:
                    logger.debug(
                        "Received message: topic=%s, partition=%s, offset=%s",
                        msg.topic,
                        msg.partition,
                        msg.offset,
                    )

                    # Parse and validate the event
                    event_data = msg.value
                    event = EmailEvent.model_validate(event_data)

                    logger.info(
                        "Processing email: type=%s, recipient=%s",
                        event.email_type,
                        event.recipient,
                    )

                    # Process the email event
                    await self.email_manager.process_email_event(event)

                    processing_time = (datetime.now() - start_time).total_seconds()
                    self.messages_processed += 1

                    logger.info(
                        "✓ Email processed successfully in %.2fs (total processed: %d)",
                        processing_time,
                        self.messages_processed,
                    )

                except ValidationError as e:
                    self.messages_failed += 1
                    logger.error(
                        "Invalid message format: %s",
                        str(e),
                        extra={"message_data": event_data},
                    )
                    # Skip invalid messages

                except Exception as e:
                    self.messages_failed += 1
                    logger.error(
                        "Error processing message (offset %s): %s",
                        msg.offset,
                        str(e),
                        exc_info=True,
                    )
                    # Continue processing other messages even if one fails

        except KafkaError as e:
            logger.error("Kafka error occurred: %s", str(e), exc_info=True)
            raise
        except Exception as e:
            logger.error("Unexpected error in consume loop: %s", str(e), exc_info=True)
            raise

    async def run(self) -> None:
        """Run the email consumer with graceful shutdown support."""
        try:
            await self.start()

            # Start health check task
            self._health_check_task = asyncio.create_task(self.health_check_loop())

            # Start consuming messages
            await self.consume()

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error("Fatal error in email consumer: %s", str(e), exc_info=True)
            sys.exit(1)
        finally:
            await self.stop()

    def handle_shutdown(self, signum: int, frame: Any) -> None:
        """Handle shutdown signals."""
        logger.info("Received shutdown signal %s", signum)
        self.running = False
        self._shutdown_event.set()


if __name__ == "__main__":
    # If run directly, import and use main module
    from .main import main

    main()
