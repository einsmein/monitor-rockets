from enum import Enum
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class MessageType:
    class RocketLaunched(BaseModel):
        type: str
        launchSpeed: int
        mission: str

    class RocketSpeedIncreased(BaseModel):
        by: int

    class RocketSpeedDecreased(BaseModel):
        by: int

    class RocketExploded(BaseModel):
        reason: str

    class RocketMissionChanged(BaseModel):
        newMission: str


class MessageMetadata(BaseModel):
    channel: str
    messageNumber: int
    messageTime: datetime
    messageType: Literal[
        MessageType.RocketLaunched.__name__,
        MessageType.RocketSpeedIncreased.__name__,
        MessageType.RocketSpeedDecreased.__name__,
        MessageType.RocketExploded.__name__,
        MessageType.RocketMissionChanged.__name__,
    ]


class Packet(BaseModel):
    metadata: MessageMetadata
    message: dict


class Rocket(BaseModel):
    type: str = ""
    speed: int = 0
    mission: str = ""
    exploded_reason: str = ""
    latest_update: str = ""
