from pydantic import BaseModel

class SensorEvent(BaseModel):
    sensorId: int
    value: float
    timestamp: str
