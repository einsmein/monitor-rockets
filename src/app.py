from collections import defaultdict
import fastapi

from . import schemas

app = fastapi.FastAPI()

rockets = defaultdict()

@app.get("/")
async def root():
    return "Hello world"

@app.post("/messages")
async def receive_message(
    metadata: schemas.MessageMetadata,
    message: dict
):
    rockets[metadata.channel] = 0
    return {"metadata": metadata, "message": message}

@app.get("/state/{channel}")
async def get_rocket_state(channel: str):
    rockets[channel]
    pass

@app.get("/list")
async def get_rockets():
    return list(rockets.keys())
