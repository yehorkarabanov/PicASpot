"""
Kafka producer manager with lifecycle management.

Provides a singleton producer instance with proper initialization,
connection management, and graceful shutdown.
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Any

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError, KafkaError

from .config import kafka_config

logger = logging.getLogger(__name__)


class KafkaManager:
    """
    Manager for Kafka producer lifecycle and operations.

    Implements singleton pattern to ensure single producer instance.
    Handles connection pooling, graceful shutdown, and automatic reconnection.
    """

    _instance: "KafkaManager | None" = None
    _lock = asyncio.Lock()

    def __new__(cls) -> "KafkaManager":
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the Kafka manager."""
        if self._initialized:
            return

        self.producer: AIOKafkaProducer | None = None
        self._is_connected = False
        self._shutdown = False
        self._initialized = True
        logger.info("Kafka manager initialized")

    async def start(self) -> None:
        """
        Start the Kafka producer with retry logic.

        Raises:
            KafkaConnectionError: If unable to connect after retries
        """
        async with self._lock:
            if self._is_connected and self.producer:
                logger.debug("Kafka producer already started")
                return

            if self._shutdown:
                logger.warning("Cannot start producer after shutdown")
                return

            for attempt in range(kafka_config.max_connection_retries):
                try:
                    self.producer = AIOKafkaProducer(
                        bootstrap_servers=kafka_config.bootstrap_servers,
                        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                        # Performance and reliability settings
                        compression_type=kafka_config.compression_type,
                        # Batching for better throughput
                        linger_ms=kafka_config.linger_ms,
                        # Timeout settings
                        request_timeout_ms=kafka_config.request_timeout_ms,
                    )

                    await self.producer.start()
                    self._is_connected = True
                    logger.info(
                        "✓ Kafka producer started successfully (brokers: %s)",
                        kafka_config.bootstrap_servers_string,
                    )
                    return

                except KafkaConnectionError as e:
                    logger.warning(
                        "Failed to connect Kafka producer (attempt %d/%d): %s",
                        attempt + 1,
                        kafka_config.max_connection_retries,
                        str(e),
                    )
                    if attempt < kafka_config.max_connection_retries - 1:
                        await asyncio.sleep(
                            kafka_config.retry_delay_seconds * (attempt + 1)
                        )
                    else:
                        logger.error(
                            "Failed to start Kafka producer after %d attempts",
                            kafka_config.max_connection_retries,
                        )
                        raise

                except Exception as e:
                    logger.error("Unexpected error starting Kafka producer: %s", str(e))
                    raise

    async def stop(self) -> None:
        """Stop the Kafka producer gracefully."""
        async with self._lock:
            if not self._is_connected or not self.producer:
                logger.debug("Kafka producer not running")
                return

            self._shutdown = True
            try:
                # Flush any pending messages
                await self.producer.flush()
                await self.producer.stop()
                logger.info("✓ Kafka producer stopped gracefully")
            except Exception as e:
                logger.error("Error stopping Kafka producer: %s", str(e))
            finally:
                self.producer = None
                self._is_connected = False

    async def send_event(
        self,
        topic: str,
        event: dict[str, Any],
        key: str | None = None,
    ) -> None:
        """
        Send an event to a Kafka topic.

        Args:
            topic: The Kafka topic to send to
            event: Event data to send (will be JSON serialized)
            key: Optional message key for partitioning

        Raises:
            RuntimeError: If producer is not started
            KafkaError: If send fails after retries
        """
        if not self._is_connected or not self.producer:
            raise RuntimeError(
                "Kafka producer not started. Call start() before sending events."
            )

        try:
            # Convert key to bytes if provided
            key_bytes = key.encode("utf-8") if key else None

            # Send and wait for acknowledgment
            metadata = await self.producer.send_and_wait(
                topic=topic,
                value=event,
                key=key_bytes,
            )

            logger.debug(
                "Event sent to Kafka topic=%s partition=%d offset=%d",
                topic,
                metadata.partition,
                metadata.offset,
            )

        except KafkaError as e:
            logger.error(
                "Failed to send event to Kafka topic=%s: %s",
                topic,
                str(e),
                exc_info=True,
            )
            raise

        except Exception as e:
            logger.error(
                "Unexpected error sending event to Kafka: %s", str(e), exc_info=True
            )
            raise

    @property
    def is_connected(self) -> bool:
        """Check if producer is connected."""
        return self._is_connected


# Global manager instance
kafka_manager = KafkaManager()


@asynccontextmanager
async def get_kafka_manager():
    """
    Context manager for Kafka manager lifecycle.

    Usage:
        async with get_kafka_manager() as manager:
            await manager.send_event("topic", {"data": "value"})
    """
    if not kafka_manager.is_connected:
        await kafka_manager.start()

    try:
        yield kafka_manager
    except Exception as e:
        logger.error("Error in Kafka manager context: %s", str(e))
        raise

