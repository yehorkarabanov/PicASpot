"""Integration tests for EmailConsumer."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from aiokafka.errors import KafkaConnectionError
from app.consumer import EmailConsumer
from app.schemas import EmailEvent, EmailType


@pytest.fixture
def email_consumer():
    """Fixture for EmailConsumer instance."""
    return EmailConsumer()


@pytest.mark.asyncio
@patch("app.consumer.AIOKafkaConsumer")
async def test_consumer_start_success(mock_kafka_consumer_class, email_consumer):
    """Test successful consumer start."""
    mock_consumer = MagicMock()
    mock_consumer.start = AsyncMock()
    mock_kafka_consumer_class.return_value = mock_consumer

    await email_consumer.start()

    assert email_consumer.running is True
    assert email_consumer.consumer is not None
    mock_consumer.start.assert_called_once()


@pytest.mark.asyncio
@patch("app.consumer.AIOKafkaConsumer")
async def test_consumer_start_kafka_connection_error_retry_success(mock_kafka_consumer_class, email_consumer):
    """Test consumer start with Kafka connection error and successful retry."""
    mock_consumer = MagicMock()
    mock_consumer.start = AsyncMock(side_effect=[KafkaConnectionError("Connection failed"), None])
    mock_kafka_consumer_class.return_value = mock_consumer

    await email_consumer.start()

    assert email_consumer.running is True
    assert mock_consumer.start.call_count == 2


@pytest.mark.asyncio
async def test_consumer_stop(email_consumer):
    """Test consumer stop."""
    import asyncio

    mock_consumer = MagicMock()
    mock_consumer.stop = AsyncMock()
    email_consumer.consumer = mock_consumer

    # Create a real asyncio task that can be cancelled
    async def dummy_health_check():
        """Dummy coroutine that runs forever until cancelled."""
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            raise

    # Create actual task
    email_consumer._health_check_task = asyncio.create_task(dummy_health_check())

    await email_consumer.stop()

    mock_consumer.stop.assert_called_once()
    assert email_consumer.running is False
    assert email_consumer._health_check_task.cancelled()


@pytest.mark.asyncio
async def test_consumer_process_valid_message(email_consumer):
    """Test processing a valid email message."""
    event = EmailEvent(
        email_type=EmailType.VERIFICATION,
        recipient="test@example.com",
        username="testuser",
        link="https://example.com/verify",
    )

    mock_msg = MagicMock()
    mock_msg.value = event.model_dump()
    mock_msg.topic = "email-events"
    mock_msg.partition = 0
    mock_msg.offset = 1

    # Create an async iterator that yields message then stops
    async def async_message_generator():
        yield mock_msg
        # After yielding, set running to False to exit the loop
        email_consumer.running = False

    email_consumer.running = True  # Set to True so consume loop processes messages
    email_consumer.consumer = MagicMock()
    email_consumer.consumer.__aiter__ = lambda self: async_message_generator()

    with patch.object(email_consumer.email_manager, "process_email_event", new_callable=AsyncMock) as mock_process:
        await email_consumer.consume()

        mock_process.assert_called_once()
        assert email_consumer.messages_processed == 1


@pytest.mark.asyncio
async def test_consumer_process_invalid_message(email_consumer):
    """Test processing an invalid email message."""
    mock_msg = MagicMock()
    mock_msg.value = {"invalid": "data"}
    mock_msg.offset = 1
    mock_msg.topic = "email-events"
    mock_msg.partition = 0

    # Create an async iterator that yields message then stops
    async def async_message_generator():
        yield mock_msg
        # After yielding, set running to False to exit the loop
        email_consumer.running = False

    email_consumer.running = True  # Set to True so consume loop processes messages
    email_consumer.consumer = MagicMock()
    email_consumer.consumer.__aiter__ = lambda self: async_message_generator()

    with patch("app.consumer.logger") as mock_logger:
        await email_consumer.consume()

        mock_logger.error.assert_called()
        assert email_consumer.messages_failed == 1
