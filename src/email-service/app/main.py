"""
Email Service Main Entry Point

A production-ready Kafka-based email service for sending transactional emails.
Supports verification emails, password resets, and more.

Features:
- Kafka consumer for email events
- Retry logic for failed emails
- Health monitoring and metrics
- Graceful shutdown handling
- Comprehensive logging
- Industry-standard error handling

Author: PicASpot Team
Version: 1.0.0
"""

import asyncio
import logging
import signal
import sys
from typing import NoReturn

from .consumer import EmailConsumer
from .logging_config import setup_logging
from .settings import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Main email service orchestrator."""

    def __init__(self):
        """Initialize the email service."""
        self.consumer: EmailConsumer | None = None
        self._shutdown_requested = False

    async def start(self) -> None:
        """Start the email service."""
        try:
            # Print banner
            self._print_banner()

            # Validate configuration
            self._validate_config()

            # Initialize and run consumer
            self.consumer = EmailConsumer()
            await self.consumer.run()

        except KeyboardInterrupt:
            logger.info("Service interrupted by user")
        except Exception as e:
            logger.critical("Failed to start email service: %s", str(e), exc_info=True)
            sys.exit(1)

    async def shutdown(self) -> None:
        """Gracefully shutdown the email service."""
        if self._shutdown_requested:
            logger.warning("Shutdown already in progress, forcing exit...")
            sys.exit(0)

        self._shutdown_requested = True
        logger.info("Initiating graceful shutdown...")

        if self.consumer:
            await self.consumer.stop()

    def _print_banner(self) -> None:
        """Print service startup banner."""
        banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║               EMAIL SERVICE - {settings.VERSION}                      ║
║                                                              ║
║  A production-ready Kafka-based email service                ║
║  Built with Python, FastAPI-Mail, and aiokafka              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

Configuration:
  • Service: {settings.SERVICE_NAME}
  • Version: {settings.VERSION}
  • Debug Mode: {settings.DEBUG}
  • Kafka Brokers: {", ".join(settings.KAFKA_BOOTSTRAP_SERVERS)}
  • Email Topic: {settings.KAFKA_EMAIL_TOPIC}
  • Consumer Group: {settings.KAFKA_CONSUMER_GROUP}
  • SMTP Server: {settings.SMTP_HOST}:{settings.SMTP_PORT}
  • Max Retries: {settings.EMAIL_MAX_RETRIES}

"""
        print(banner)
        logger.info("Email service initializing...")

    def _validate_config(self) -> None:
        """Validate critical configuration settings."""
        logger.info("Validating configuration...")

        required_settings = {
            "SMTP_USER": settings.SMTP_USER,
            "SMTP_PASSWORD": settings.SMTP_PASSWORD,
            "SMTP_HOST": settings.SMTP_HOST,
            "SMTP_PORT": settings.SMTP_PORT,
            "EMAIL_FROM_NAME": settings.EMAIL_FROM_NAME,
        }

        missing_settings = [
            key for key, value in required_settings.items() if not value
        ]

        if missing_settings:
            error_msg = f"Missing required settings: {', '.join(missing_settings)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Validate template folder exists
        if not settings.TEMPLATE_FOLDER.exists():
            error_msg = f"Template folder not found: {settings.TEMPLATE_FOLDER}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        logger.info("✓ Configuration validated successfully")


def setup_signal_handlers(service: EmailService) -> None:
    """
    Setup signal handlers for graceful shutdown.

    Args:
        service: The email service instance
    """
    loop = asyncio.get_event_loop()

    def handle_signal(sig: signal.Signals) -> None:
        """Handle shutdown signals."""
        logger.info("Received signal %s, initiating shutdown...", sig.name)
        asyncio.create_task(service.shutdown())

    # Register signal handlers for graceful shutdown
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, lambda s=sig: handle_signal(s))
        except NotImplementedError:
            # Windows doesn't support add_signal_handler
            signal.signal(sig, lambda s, f: handle_signal(signal.Signals(s)))


async def async_main() -> None:
    """Async main entry point."""
    # Setup logging
    setup_logging()

    # Create and configure service
    service = EmailService()

    # Setup signal handlers for graceful shutdown
    setup_signal_handlers(service)

    # Start the service
    await service.start()


def main() -> NoReturn:
    """
    Main entry point for the email service.

    This function initializes the service and runs the event loop.
    It handles graceful shutdown on SIGTERM and SIGINT signals.
    """
    try:
        # Run the async main function
        asyncio.run(async_main())
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.critical("Service crashed: %s", str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
