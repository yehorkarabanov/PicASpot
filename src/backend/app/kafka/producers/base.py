"""
Base publisher class for Kafka events.

Provides common functionality for all event publishers.
"""

import logging
from typing import Any

from ..config import KafkaTopics
from ..manager import kafka_manager

logger = logging.getLogger(__name__)


class BasePublisher:
    """
    Base class for Kafka event publishers.

    Provides common methods for publishing events to Kafka topics.
    """

    def __init__(self, topic: KafkaTopics):
        """
        Initialize the base publisher.

        Args:
            topic: The Kafka topic to publish to
        """
        self.topic = topic.value
        self.manager = kafka_manager

    async def publish(
        self,
        event: dict[str, Any],
        key: str | None = None,
    ) -> None:
        """
        Publish an event to the configured topic.

        Args:
            event: Event data to publish
            key: Optional partition key

        Raises:
            Exception: If publishing fails
        """
        try:
            await self.manager.send_event(
                topic=self.topic,
                event=event,
                key=key,
            )
            logger.debug("Event published to topic=%s", self.topic)

        except Exception as e:
            logger.error(
                "Failed to publish event to topic=%s: %s",
                self.topic,
                str(e),
                exc_info=True,
            )
            raise

