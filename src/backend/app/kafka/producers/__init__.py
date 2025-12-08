"""
Kafka event publishers.

High-level publisher services for different event types.
Each publisher handles a specific domain and provides
type-safe methods for publishing events.
"""

from .email_publisher import EmailPublisher

__all__ = [
    "EmailPublisher",
]

