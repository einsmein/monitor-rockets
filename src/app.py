import logging

import fastapi
from fastapi.responses import Response

from src import schemas
from src.backend import store

def create_app():
    app = fastapi.FastAPI()

    @app.get("/")
    async def root():
        return "Hello Moon!"

    @app.post("/messages", response_model=schemas.Rocket)
    async def receive_message(metadata: schemas.MessageMetadata, message: dict):

        logging.error({"metadata": metadata, "message": message})
        rocket = store.get(metadata.channel)

        if rocket and store.is_processed(metadata.channel, metadata.messageNumber):
            return Response(status_code=204)

        message = getattr(schemas.MessageType, metadata.messageType)(**message)

        if isinstance(message, schemas.MessageType.RocketLaunched):
            store.process_message_launched(rocket, metadata, message)

        if isinstance(message, schemas.MessageType.RocketSpeedIncreased):
            store.process_message_speed_increased(rocket, metadata, message)

        if isinstance(message, schemas.MessageType.RocketSpeedDecreased):
            store.process_message_speed_decreased(rocket, metadata, message)

        if isinstance(message, schemas.MessageType.RocketExploded):
            store.process_message_exploded(rocket, metadata, message)

        if isinstance(message, schemas.MessageType.RocketMissionChanged):
            store.process_message_mission_changed(rocket, metadata, message)

        # return rocket

    @app.get("/state/{channel}")
    async def get_rocket_state(channel: str):
        return store.get(channel)

    @app.get("/list")
    async def list_all_channels():
        return store.get_channels()

    @app.exception_handler(Exception)
    def handle_exception_object(_req, exception):
        return Response(str(exception.args), status_code=500)

    return app


APP = create_app()
