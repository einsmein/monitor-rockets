from enum import Enum
from datetime import datetime

from pydantic import BaseModel

class messageType(Enum):
    Launched = "RocketLaunched"
    SpeedIncreased = "RocketSpeedIncreased"
    SpeedDecreased = "RocketSpeedDecreased"
    Exploded = "RocketExploded"
    MissionChanged = "RocketMissionChanged"

class MessageMetadata(BaseModel):
    channel: str
    messageNumber: int
    messageTime: datetime
    messageType: str
