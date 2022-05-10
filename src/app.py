import logging

import fastapi
from fastapi.responses import Response

from src import schemas
from src.backend import store

logging.basicConfig(filename="server.log", level=logging.INFO)


def create_app():
    app = fastapi.FastAPI()

    @app.get("/")
    async def root():
        return "Hello Moon!"

    @app.post("/messages")
    async def receive_message(metadata: schemas.MessageMetadata, message: dict):
        logging.info({"metadata": metadata, "message": message})

        rocket = store.get(metadata.channel)

        if rocket and store.is_processed(metadata.channel, metadata.messageNumber):
            return Response(status_code=204)

        message = getattr(schemas.MessageType, metadata.messageType)(**message)

        if isinstance(message, schemas.MessageType.RocketLaunched):
            store.update_type(metadata, message.type)
            if rocket.latest_mission_msg < metadata.messageNumber:
                store.update_mission(metadata, message.mission)
            store.update_speed(metadata, message.launchSpeed)

        if isinstance(message, schemas.MessageType.RocketSpeedIncreased):
            store.update_speed(metadata, message.by)

        if isinstance(message, schemas.MessageType.RocketSpeedDecreased):
            store.update_speed(metadata, -message.by)

        if isinstance(message, schemas.MessageType.RocketExploded):
            if rocket.latest_exploded_msg < metadata.messageNumber:
                store.update_exploded_reason(metadata, message.reason)

        if isinstance(message, schemas.MessageType.RocketMissionChanged):
            if rocket.latest_mission_msg < metadata.messageNumber:
                store.update_mission(metadata, message.newMission)

    @app.get("/state/{channel}", response_model=schemas.Rocket)
    async def get_rocket_state(channel: str):
        rocket = store.get(channel)
        if not rocket.latest_update:
            return Response(
                f"No state is received on channel '{channel}'.", status_code=404
            )
        return rocket

    @app.get("/list")
    async def list_all_channels():
        return store.get_channels()

    @app.exception_handler(Exception)
    def handle_exception_object(_req, exception):
        return Response(str(exception.args), status_code=500)

    return app


APP = create_app()
