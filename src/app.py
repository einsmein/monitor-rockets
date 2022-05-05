from collections import defaultdict

import fastapi
from fastapi.responses import Response

from src import schemas

rockets = defaultdict(schemas.Rocket)

def create_app():
    app = fastapi.FastAPI()

    @app.get("/")
    async def root():
        return "Hello Moon!"


    @app.post("/messages")
    async def receive_message(metadata: schemas.MessageMetadata, message: dict):
        rocket = rockets[metadata.channel]
        if metadata.messageNumber in rocket.processed_msg_num:
            return Response(status_code=204)

        message = getattr(schemas.MessageType, metadata.messageType)(**message)

        if isinstance(message, schemas.MessageType.RocketLaunched):
            rocket.type, rocket.speed, rocket.mission, _ = (
                message.type,
                rocket.speed + message.launchSpeed,
                message.mission,
                rocket.processed_msg_num.add(metadata.messageNumber),
            )

        if isinstance(message, schemas.MessageType.RocketSpeedIncreased):
            rocket.speed, _ = rocket.speed + message.by, rocket.processed_msg_num.add(
                metadata.messageNumber
            )

        if isinstance(message, schemas.MessageType.RocketSpeedDecreased):
            rocket.speed, _ = rocket.speed - message.by, rocket.processed_msg_num.add(
                metadata.messageNumber
            )

        if isinstance(message, schemas.MessageType.RocketExploded):
            rocket.exploded_reason, _ = message.reason, rocket.processed_msg_num.add(
                metadata.messageNumber
            )

        if isinstance(message, schemas.MessageType.RocketMissionChanged):
            rocket.mission, _ = message.newMission, rocket.processed_msg_num.add(
                metadata.messageNumber
            )

        return rocket


    @app.get("/state/{channel}")
    async def get_rocket_state(channel: str):
        return rockets[channel]


    @app.get("/list")
    async def get_rockets():
        return list(rockets.keys())

    @app.exception_handler(Exception)
    def handle_exception_object(_req, exception):
        return Response(str(exception.args), status_code=500)

    return app
