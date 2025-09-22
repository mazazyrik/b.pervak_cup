import json
from logging import getLogger

from aiokafka import AIOKafkaProducer

from app.src.config import KAFKA_BOOTSTRAP_SERVERS

logger = getLogger(__name__)
logger.setLevel("DEBUG")

producer: AIOKafkaProducer | None = None


async def start_kafka_producer():
    global producer
    if producer is not None:
        logger.debug(
            "Kafka producer already started, stopping it before starting again"
        )
        await producer.stop()
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    logger.debug("Kafka producer started")


async def stop_kafka_producer():
    global producer
    if producer is not None:
        await producer.stop()
        logger.debug("Kafka producer stopped")


async def send_message_to_kafka(message_dict: dict, topic: str):
    if producer is None:
        raise RuntimeError("Kafka producer is not started")
    value = json.dumps(message_dict).encode("utf-8")
    await producer.send_and_wait(topic, value=value)
    logger.debug(f"Produced message to Kafka: {message_dict}")
