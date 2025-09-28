import random
import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/temperature/{sensor_id}")
def get_temperature():
        return {"value": random.uniform(15, 30),
                "status": "active"}

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=True)