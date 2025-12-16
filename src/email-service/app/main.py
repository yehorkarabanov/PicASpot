import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging import setup_logging, shutdown_logging
from app.kafka import kafka_consumer
from app.settings import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup logging configuration
    setup_logging(use_file_logging=True)
    logger.info(
        "Email service starting up",
        extra={
            "service": settings.SERVICE_NAME,
            "debug_mode": settings.DEBUG,
        },
    )

    try:
        await kafka_consumer.start()

        await kafka_consumer.consume_messages()
    except Exception as e:
        logger.error(
            "Failed to start email service",
            exc_info=True,
            extra={"error": str(e)},
        )
        raise

    yield

    logger.info("Email service shutting down")
    try:
        await kafka_consumer.stop()
    except Exception as e:
        logger.error(
            "Error during email service shutdown",
            exc_info=True,
            extra={"error": str(e)},
        )
    finally:
        # Gracefully shutdown logging
        shutdown_logging()
        logger.info("Email service stopped")


app = FastAPI(title=settings.SERVICE_NAME, lifespan=lifespan)


@app.get("/")
async def root():
    logger.debug("Root endpoint accessed")
    return {"message": f"{settings.SERVICE_NAME} is running."}


@app.get("/health")
async def health_check():
    logger.debug("Health check endpoint accessed")
    return {"status": "healthy", "service": settings.SERVICE_NAME, "version": "1.0.0"}
