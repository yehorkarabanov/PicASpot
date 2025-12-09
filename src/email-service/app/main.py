from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.kafka import kafka_consumer
from app.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await kafka_consumer.start()

        await kafka_consumer.consume_messages()
    except Exception as e:
        # Handle startup exceptions here
        raise e

    yield

    try:
        kafka_consumer.stop()
    except Exception as e:
        # Handle shutdown exceptions here
        raise e


app = FastAPI(title=settings.SERVICE_NAME, lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": f"{settings.SERVICE_NAME} is running."}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.SERVICE_NAME, "version": "1.0.0"}
