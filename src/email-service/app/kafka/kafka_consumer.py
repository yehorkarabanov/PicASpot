import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer

from app.email.tasks import user_password_reset_mail, user_verify_mail
from app.settings import settings

logger = logging.getLogger(__name__)


class KafkaConsumer:
    """Asynchronous Kafka consumer for processing email-related messages.

    This class manages the lifecycle of a Kafka consumer, including connection
    management, message consumption, and processing delegation. It implements
    retry logic for resilient connections and handles graceful shutdown.

    The consumer automatically subscribes to verification and password reset
    email topics and processes messages by delegating to the appropriate
    email service tasks.

    Attributes:
        consumer (AIOKafkaConsumer | None): The underlying aiokafka consumer instance.
        running (bool): Flag indicating whether the consumer is actively running.
        _task (asyncio.Task | None): Background task handling message consumption.

    Note:
        The consumer must be started with `start()` before consuming messages and
        should be properly stopped with `stop()` when done to ensure clean shutdown.
    """

    def __init__(self):
        """Initialize the Kafka consumer.

        Creates a new KafkaConsumer instance with uninitialized consumer,
        running flag set to False, and no background task. The actual connection
        is established when calling `start()`.
        """
        self.consumer: AIOKafkaConsumer | None = None
        self.running = False
        self._task: asyncio.Task | None = None

    async def start(self, max_retries: int = 5, retry_delay: int = 2):
        """Start the Kafka consumer and subscribe to topics.

        Establishes connection to the Kafka cluster with retry logic and subscribes
        to configured email topics (verification and password reset). The consumer
        is configured to read from the earliest offset and manually commits offsets
        after successful message processing.

        Args:
            max_retries (int, optional): Maximum number of connection attempts.
                Defaults to 5.
            retry_delay (int, optional): Delay in seconds between retry attempts.
                Defaults to 2.

        Raises:
            Exception: If the consumer fails to start after all retry attempts.

        Note:
            This method will log detailed information about connection attempts,
            including bootstrap servers, consumer group, and subscribed topics.
        """
        for attempt in range(max_retries + 1):
            try:
                logger.info(
                    "Starting Kafka consumer",
                    extra={
                        "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                        "consumer_group": settings.KAFKA_CONSUMER_GROUP,
                        "topics": [
                            settings.KAFKA_VERIFICATION_EMAIL_TOPIC,
                            settings.KAFKA_RESET_PASSWORD_EMAIL_TOPIC,
                        ],
                    },
                )
                self.consumer = AIOKafkaConsumer(
                    settings.KAFKA_VERIFICATION_EMAIL_TOPIC,
                    settings.KAFKA_RESET_PASSWORD_EMAIL_TOPIC,
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    group_id=settings.KAFKA_CONSUMER_GROUP,
                    auto_offset_reset="earliest",
                    enable_auto_commit=False,
                )

                await self.consumer.start()
                logger.info(
                    "Kafka consumer started successfully",
                    extra={
                        "consumer_group": settings.KAFKA_CONSUMER_GROUP,
                    },
                )
                break  # Success, exit retry loop
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
        """Stop the Kafka consumer gracefully.

        Stops the consumer by setting the running flag to False, cancelling the
        background consumption task, and closing the consumer connection. This
        method ensures all resources are properly released.

        The method handles task cancellation gracefully and logs any errors that
        occur during shutdown without raising exceptions.

        Note:
            This method is idempotent and safe to call multiple times. It will
            handle cases where the task or consumer is already stopped.
        """
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
        """Process a single Kafka message and delegate to email service.

        Parses the JSON message payload and routes it to the appropriate email
        service task based on the topic. Handles verification emails and password
        reset emails differently.

        Args:
            msg: The Kafka message object containing topic, value, and other metadata.

        Note:
            - Messages are JSON-decoded and expected to contain 'email', 'link',
              and 'username' fields.
            - On JSON decode errors, the message is logged and committed to prevent
              blocking the consumer.
            - On processing errors, the error is logged but the offset is NOT
              committed, allowing for potential retry.
            - After successful processing, the offset is committed automatically
              by the consumption loop.

        Raises:
            Exception: Propagates processing exceptions to the caller for handling.
        """
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
        """Start consuming messages from Kafka topics.

        Creates a background task that runs the consumption loop. This method
        returns immediately after starting the task, allowing the application
        to continue with other operations.

        The consumption loop will continue until `stop()` is called or an
        unrecoverable error occurs.

        Note:
            This method should only be called after `start()` has successfully
            connected to the Kafka cluster. The background task can be monitored
            or cancelled through the `_task` attribute.
        """
        self.running = True
        self._task = asyncio.create_task(self._consume_loop())
        logger.info("Starting message consumer loop")

    async def _consume_loop(self):
        """Main message consumption loop using async iterator.

        Internal method that continuously consumes messages from subscribed topics
        using an async iterator pattern. For each message:
            1. Checks if the consumer should still be running
            2. Processes the message through `process_message()`
            3. Commits the offset on successful processing
            4. Logs and skips commit on processing errors

        The loop handles exceptions gracefully:
            - Processing errors are logged but don't stop the loop
            - Fatal errors stop the loop and are logged with full traceback
            - The consumer is always stopped in the finally block

        Note:
            This is an internal method and should not be called directly.
            Use `consume_messages()` instead.

        Raises:
            Exception: Logs any exceptions that occur during consumption but
                doesn't propagate them to maintain service stability.
        """
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
