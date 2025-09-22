from aiokafka import AIOKafkaConsumer

from config import KAFKA_BOOTSTRAP_SERVERS


class KafkaClient:
    def __init__(self, bootstrap_servers: str = KAFKA_BOOTSTRAP_SERVERS):
        self.consumer = AIOKafkaConsumer(bootstrap_servers=bootstrap_servers)

    async def consume(self, topic: str):
        await self.consumer.start()
        async for message in self.consumer:
            yield message.value.decode('utf-8')
