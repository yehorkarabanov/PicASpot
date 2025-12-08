"""Unit tests for EmailManager."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.handlers.email_manager import EmailManager, metrics
from app.models.schemas import EmailEvent, EmailType


@pytest.fixture
def email_manager():
    """Fixture for EmailManager instance."""
    return EmailManager()


@pytest.fixture
def sample_verification_event():
    """Sample verification email event."""
    return EmailEvent(
        email_type=EmailType.VERIFICATION,
        recipient="test@example.com",
        username="testuser",
        link="https://example.com/verify?token=abc123",
    )


@pytest.fixture
def sample_password_reset_event():
    """Sample password reset email event."""
    return EmailEvent(
        email_type=EmailType.PASSWORD_RESET,
        recipient="test@example.com",
        username="testuser",
        link="https://example.com/reset?token=abc123",
    )


@pytest.mark.asyncio
@patch("app.handlers.email_manager.mail")
async def test_send_verification_email_success(mock_mail, email_manager, sample_verification_event):
    """Test successful verification email sending."""
    mock_mail.send_message = AsyncMock()

    await email_manager.send_verification_email(sample_verification_event)

    mock_mail.send_message.assert_called_once()
    assert metrics.get_stats()["emails_sent"] == 1


@pytest.mark.asyncio
@patch("app.handlers.email_manager.mail")
async def test_send_password_reset_email_success(mock_mail, email_manager, sample_password_reset_event):
    """Test successful password reset email sending."""
    mock_mail.send_message = AsyncMock()

    await email_manager.send_password_reset_email(sample_password_reset_event)

    mock_mail.send_message.assert_called_once()
    assert metrics.get_stats()["emails_sent"] == 1


@pytest.mark.asyncio
@patch("app.handlers.email_manager.mail")
async def test_send_email_with_retry_success_after_failure(mock_mail, email_manager, sample_verification_event):
    """Test email sending with retry logic - success after failure."""
    mock_mail.send_message = AsyncMock(side_effect=[Exception("SMTP error"), None])

    await email_manager.send_verification_email(sample_verification_event)

    assert mock_mail.send_message.call_count == 2
    assert metrics.get_stats()["emails_retried"] == 1
    assert metrics.get_stats()["emails_sent"] == 1


@pytest.mark.asyncio
@patch("app.handlers.email_manager.mail")
async def test_send_email_retry_exhausted(mock_mail, email_manager, sample_verification_event):
    """Test email sending when all retries are exhausted."""
    mock_mail.send_message = AsyncMock(side_effect=Exception("SMTP error"))

    with pytest.raises(Exception, match="SMTP error"):
        await email_manager.send_verification_email(sample_verification_event)

    assert mock_mail.send_message.call_count == 3  # Default max retries
    assert metrics.get_stats()["emails_failed"] == 1


@pytest.mark.asyncio
async def test_process_email_event_verification(email_manager, sample_verification_event):
    """Test processing verification email event."""
    with patch.object(email_manager, "send_verification_email", new_callable=AsyncMock) as mock_send:
        await email_manager.process_email_event(sample_verification_event)
        mock_send.assert_called_once_with(sample_verification_event)


@pytest.mark.asyncio
async def test_process_email_event_password_reset(email_manager, sample_password_reset_event):
    """Test processing password reset email event."""
    with patch.object(email_manager, "send_password_reset_email", new_callable=AsyncMock) as mock_send:
        await email_manager.process_email_event(sample_password_reset_event)
        mock_send.assert_called_once_with(sample_password_reset_event)


@pytest.mark.asyncio
async def test_process_email_event_unknown_type(email_manager):
    """Test processing email event with unknown type."""
    event = EmailEvent(
        email_type="unknown",
        recipient="test@example.com",
        username="testuser",
        link="https://example.com",
    )

    with patch("app.handlers.email_manager.logger") as mock_logger:
        await email_manager.process_email_event(event)
        mock_logger.error.assert_called_once_with("Unknown email type: %s", "unknown")
