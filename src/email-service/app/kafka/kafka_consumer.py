import asyncio

from aiokafka import AIOKafkaConsumer
from app.settings import settings


class KafkaConsumer:
    def __init__(self):
        self.consumer: AIOKafkaConsumer | None = None
        self.running = False
        self._task: asyncio.Task | None = None

    async def start(self):
        try:
            self.consumer = AIOKafkaConsumer(
                settings.KAFKA_VERIFICATION_EMAIL_TOPIC,
                settings.KAFKA_RESET_PASSWORD_EMAIL_TOPIC,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=settings.KAFKA_EMAIL_CONSUMER_GROUP,
                auto_offset_reset="earliest",
                enable_auto_commit=False,
            )

            await self.consumer.start()
        except Exception:
            raise

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def consume_messages(self):
        if not self.consumer:
            raise RuntimeError("Kafka consumer is not started.")

        self.running = True
        try:
            async for msg in self.consumer:
                # Process the message here
                print(f"Consumed message: {msg.value.decode('utf-8')} from topic: {msg.topic}")


kafka_consumer = KafkaConsumer()
