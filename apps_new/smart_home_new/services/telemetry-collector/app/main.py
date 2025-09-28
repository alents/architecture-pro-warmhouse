import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import date, datetime
from typing import List
from .db import get_session
from .schemas import SensorEvent
from .rabbitmq import consume_telemetry

logging.basicConfig(level=logging.INFO)  # включаем INFO логи глобально
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # стартуем консьюмера
    task = asyncio.create_task(consume_telemetry())
    logger.info("Started rabbitmq consumer task")
    try:
        yield
    finally:
        logger.info("Shutting down rabbitmq consumer task")
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            logger.info("Consumer task cancelled cleanly")
        except Exception:
            logger.exception("Consumer task finished with exception")

app = FastAPI(lifespan=lifespan)

@app.get("/api/v1/telemetry/{sensor_id}", response_model=List[SensorEvent])
async def get_telemetry(sensor_id: int, session: AsyncSession = Depends(get_session)):
    today = date.today()
    result = await session.execute(
        text("""
             SELECT sensor_id, value, value_timestamp
             FROM telemetry
             WHERE sensor_id = :sensor_id
               AND value_timestamp >= :start
             ORDER BY value_timestamp
             """),
        {
            "sensor_id": sensor_id,
            "start": datetime.combine(today, datetime.min.time())
        }
    )
    rows = result.all()

    return [
        SensorEvent(
            sensorId=row.sensor_id,
            value=row.value,
            timestamp=row.value_timestamp.isoformat(),
        )
        for row in rows
    ]
