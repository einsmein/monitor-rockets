from typing import Literal

from pydantic import BaseModel


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
    messageTime: str
    messageType: Literal[
        MessageType.RocketLaunched.__name__,
        MessageType.RocketSpeedIncreased.__name__,
        MessageType.RocketSpeedDecreased.__name__,
        MessageType.RocketExploded.__name__,
        MessageType.RocketMissionChanged.__name__,
    ]


class Rocket(BaseModel):
    """
    Schema of rocket state.
    `lastest_mission_msg` is the latest RocketMissionChanged message number.
    `lastest_exploded_msg` is the latest RocketExploeded message number.
    """

    type: str = ""
    speed: int = 0
    mission: str = ""
    exploded_reason: str = ""
    latest_mission_msg: int = -1
    latest_exploded_msg: int = -1
    latest_update: str = ""
