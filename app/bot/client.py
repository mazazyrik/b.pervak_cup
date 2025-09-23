import asyncio
from aiokafka import AIOKafkaConsumer

from config import KAFKA_BOOTSTRAP_SERVERS


class KafkaClient:
    def __init__(self, bootstrap_servers: str = KAFKA_BOOTSTRAP_SERVERS):
        self._bootstrap = bootstrap_servers
        self.consumer: AIOKafkaConsumer | None = None

    async def consume(self, topic: str):
        while True:
            try:
                if self.consumer is not None:
                    await self.close()
                self.consumer = AIOKafkaConsumer(
                    topic,
                    bootstrap_servers=self._bootstrap,
                    enable_auto_commit=True,
                    auto_offset_reset='latest',
                )
                await self.consumer.start()
                async for message in self.consumer:
                    yield message.value.decode('utf-8')
            except Exception:
                await asyncio.sleep(2)
            finally:
                if self.consumer is not None:
                    try:
                        await self.consumer.stop()
                    except Exception:
                        pass
                    self.consumer = None

    async def close(self):
        if self.consumer is not None:
            try:
                await self.consumer.stop()
            finally:
                self.consumer = None
