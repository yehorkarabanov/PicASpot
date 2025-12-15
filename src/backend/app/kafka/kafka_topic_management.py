import asyncio
import logging

from aiokafka.admin import AIOKafkaAdminClient, NewTopic

from app.settings import settings

logger = logging.getLogger("KafkaTopics")


async def wait_for_kafka_ready(max_retries: int = 30, retry_delay: int = 2) -> None:
    """Performs health checks on the Kafka cluster by attempting to connect and
    list topics. This ensures the cluster is operational before attempting
    to create topics or start producers/consumers.

    Args:
        max_retries (int, optional): Maximum number of connection attempts.
            Defaults to 30.
        retry_delay (int, optional): Delay in seconds between retry attempts.
            Defaults to 2.

    Raises:
        Exception: If Kafka cluster is not ready after max_retries attempts.

    Note:
        This function will log warnings for failed attempts and raise an
        exception after exhausting all retries. It's designed to be called
        during application startup.
    """
    logger.info("Waiting for Kafka cluster to be ready...")

    for attempt in range(max_retries):
        try:
            admin = AIOKafkaAdminClient(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                request_timeout_ms=5000,
            )

            await admin.start()
            await admin.list_topics()
            await admin.close()

            logger.info("Kafka cluster is ready")
            return

        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(
                    f"Kafka not ready (attempt {attempt + 1}/{max_retries}): {e}"
                )
                await asyncio.sleep(retry_delay)
            else:
                logger.error("Kafka cluster failed to become ready")
                raise


async def create_kafka_topics():
    """
    Waits for Kafka cluster readiness, then creates required email topics
    with configured partitioning and replication. This function is idempotent
    and safe to call multiple times - it will only create topics that don't
    already exist.

    Topics created:
        - Verification email topic (3 partitions, replication factor 1)
        - Password reset email topic (3 partitions, replication factor 1)

    The function will:
        1. Wait for Kafka cluster to be ready
        2. Connect to the cluster as an admin client
        3. Check for existing topics
        4. Create only missing topics
        5. Log success or warnings about any issues

    Raises:
        Exception: Logs exceptions but doesn't raise them to allow the
            application to continue (topics might exist from previous runs).

    Note:
        This function should be called during application startup. It gracefully
        handles cases where topics already exist and will log appropriate messages.
    """
    await wait_for_kafka_ready()

    admin = AIOKafkaAdminClient(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)

    topics = [
        NewTopic(
            name=settings.KAFKA_VERIFICATION_EMAIL_TOPIC,
            num_partitions=3,
            replication_factor=1,
        ),
        NewTopic(
            name=settings.KAFKA_RESET_PASSWORD_EMAIL_TOPIC,
            num_partitions=3,
            replication_factor=1,
        ),
        NewTopic(
            name=settings.KAFKA_VERIFY_IMAGE_TOPIC,
            num_partitions=3,
            replication_factor=1,
        ),
    ]

    try:
        await admin.start()

        existing_topics = await admin.list_topics()
        topics_to_create = [
            topic for topic in topics if topic.name not in existing_topics
        ]

        if topics_to_create:
            await admin.create_topics(
                new_topics=topics_to_create,
                validate_only=False,
            )
            logger.info("Kafka topics created successfully")
        else:
            logger.info("Kafka topics already exist")

    except Exception as e:
        logger.warning(f"Kafka topics creation issue: {e}")
    finally:
        await admin.close()


async def ensure_topics_exist():
    """Ensure required Kafka topics exist using async aiokafka.

    High-level function that ensures all required Kafka topics are created
    and available before the application starts. This is the main entry point
    for topic management during application startup.

    This function delegates to `create_kafka_topics()` which handles:
        - Waiting for Kafka cluster availability
        - Creating verification email topic
        - Creating password reset email topic
        - Idempotent creation (safe to call multiple times)

    Example:
        >>> # In your application startup (e.g., main.py)
        >>> from app.kafka.kafka_topic_management import ensure_topics_exist
        >>>
        >>> @app.on_event("startup")
        >>> async def startup_event():
        ...     await ensure_topics_exist()
        ...     await kafka_producer.start()

    Note:
        This should be called before starting any Kafka producers or consumers
        to ensure topics are available for message publishing and consumption.
    """
    await create_kafka_topics()
