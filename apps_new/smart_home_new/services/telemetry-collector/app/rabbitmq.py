import os
import asyncio
import logging
from datetime import datetime

import aio_pika
from aio_pika import ExchangeType
from sqlalchemy import text

from .schemas import SensorEvent
from .db import async_session

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
QUEUE_NAME = os.getenv("TELEMETRY_QUEUE", "telemetry_service_queue")
EXCHANGE_NAME = "sensor_telemetry"
ROUTING_KEY = "sensor_changed"


async def save_telemetry(event: SensorEvent):
    """Сохраняем через SQL (SQLAlchemy Core)."""
    try:
        async with async_session() as session:
            await session.execute(
                text(
                    """
                    INSERT INTO telemetry (sensor_id, value, value_timestamp)
                    VALUES (:sensor_id, :value, :ts)
                    """
                ),
                {
                    "sensor_id": event.sensorId,
                    "value": event.value,
                    "ts": datetime.fromisoformat(event.timestamp),
                },
            )
            await session.commit()
        logger.info("Saved telemetry sensor=%s value=%s ts=%s", event.sensorId, event.value, event.timestamp)
    except Exception:
        logger.exception("DB insert failed")


async def _on_message(message: aio_pika.IncomingMessage):
    async with message.process(ignore_processed=True):  # ack on success, nack on exception
        logger.debug("Message received: %s", message.body)
        try:
            # пытаемся распарсить JSON в объект
            data = SensorEvent.parse_raw(message.body)
        except Exception:
            logger.exception("Failed to parse message body (not valid SensorEvent JSON)")
            # если парсинг упал — nack и не requeue
            raise

        await save_telemetry(data)


async def consume_telemetry():
    while True:
        try:
            logger.info("Connecting to RabbitMQ: %s", RABBITMQ_URL)
            connection = await aio_pika.connect_robust(RABBITMQ_URL)
            async with connection:
                logger.info("Connected to RabbitMQ")
                channel = await connection.channel()
                await channel.set_qos(prefetch_count=50)

                # объявляем exchange и очередь (durable=True чтобы очередь была видна в management UI)
                exchange = await channel.declare_exchange(EXCHANGE_NAME, ExchangeType.TOPIC, durable=True)
                queue = await channel.declare_queue(QUEUE_NAME, durable=True)  # named durable queue
                await queue.bind(exchange, routing_key=ROUTING_KEY)
                logger.info("Queue %s bound to %s with routing_key=%s", QUEUE_NAME, EXCHANGE_NAME, ROUTING_KEY)

                backoff = 1  # успешное подключение — сброс backoff
                # начинаем итератор — блокирующая конструкция пока коннекшен жив
                async with queue.iterator() as q_iter:
                    async for message in q_iter:
                        try:
                            await _on_message(message)
                        except Exception:
                            # _on_message уже логирует; но ловим чтобы цикл не ломался
                            logger.exception("Error while processing message")
        except asyncio.CancelledError:
            logger.info("consume_telemetry cancelled, exiting")
            raise
        except Exception:
            logger.exception("RabbitMQ consumer error — reconnecting in %s sec", backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 30)
