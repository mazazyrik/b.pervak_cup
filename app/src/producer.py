import json
import asyncio
from logging import getLogger

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError

from app.src.config import KAFKA_BOOTSTRAP_SERVERS

logger = getLogger(__name__)
logger.setLevel('DEBUG')

producer: AIOKafkaProducer | None = None


async def start_kafka_producer():
    global producer
    if producer is not None:
        logger.debug(
            'Kafka producer already started, stopping it before starting again'
        )
        await producer.stop()
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

    max_attempts = 20
    for attempt in range(1, max_attempts + 1):
        try:
            await producer.start()
            logger.debug('Kafka producer started')
            return
        except (KafkaConnectionError, OSError) as e:
            wait_s = min(1.0 * attempt, 5.0)
            logger.debug(
                f'Kafka bootstrap failed (attempt {attempt}/{max_attempts}): {e}. Retry in {wait_s}s')
            await asyncio.sleep(wait_s)
        except Exception:
            # неизвестная ошибка — пробрасываем после аккуратной остановки
            try:
                await producer.stop()
            except Exception:
                pass
            producer = None
            raise

    # если все попытки исчерпаны — аккуратно остановим и бросим исключение
    try:
        await producer.stop()
    except Exception:
        pass
    producer = None
    raise KafkaConnectionError(
        f'Unable to bootstrap from {KAFKA_BOOTSTRAP_SERVERS}')


async def stop_kafka_producer():
    global producer
    if producer is not None:
        await producer.stop()
        logger.debug('Kafka producer stopped')
        producer = None


async def send_message_to_kafka(message_dict: dict, topic: str):
    global producer
    if producer is None:
        raise RuntimeError('Kafka producer is not started')
    value = json.dumps(message_dict).encode('utf-8')
    await producer.send_and_wait(topic, value=value)
    logger.debug(f'Produced message to Kafka: {message_dict}')
