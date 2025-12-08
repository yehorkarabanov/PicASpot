"""
Kafka configuration and constants.

Centralized configuration for Kafka producers, consumers, and topics.
"""

from enum import Enum

from pydantic import Field
from pydantic_settings import BaseSettings


class KafkaTopics(str, Enum):
    """Enumeration of Kafka topics used in the application."""

    EMAIL_EVENTS = "email-events"
    USER_EVENTS = "user-events"
    NOTIFICATION_EVENTS = "notification-events"


class KafkaConfig(BaseSettings):
    """
    Kafka-specific configuration.

    Separates Kafka settings from main application settings
    for better organization and testing.
    """

    # Broker configuration
    bootstrap_servers: list[str] = Field(
        default=["kafka-0:9092", "kafka-1:9092", "kafka-2:9092"]
    )

    # Producer settings
    compression_type: str = Field(default="gzip")
    acks: str = Field(default="all")  # Wait for all replicas
    retries: int = Field(default=3)
    max_in_flight_requests: int = Field(default=5)
    linger_ms: int = Field(default=10)  # Batch messages for 10ms
    batch_size: int = Field(default=16384)  # 16KB
    request_timeout_ms: int = Field(default=30000)

    # Connection retry settings
    max_connection_retries: int = Field(default=5)
    retry_delay_seconds: int = Field(default=2)

    @property
    def bootstrap_servers_string(self) -> str:
        """Returns bootstrap servers as comma-separated string."""
        return ",".join(self.bootstrap_servers)


# Global config instance
kafka_config = KafkaConfig()

