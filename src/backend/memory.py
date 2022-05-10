"""
In-memory store
"""
from collections import defaultdict
from datetime import datetime

from src import schemas

_rockets = {}
_processed_message_num = defaultdict(set)


def get_channels():
    """
    Get all channels. The result is sorted by latest update
    timestamp in an ascending order.
    """
    return [
        channel
        for channel, rocket in sorted(
            _rockets.items(), key=lambda t: datetime.fromisoformat(t[1].latest_update)
        )
    ]


def get(channel: str):
    """Get state of a rocket on the given `channel`"""
    if channel not in _rockets:
        return schemas.Rocket()
    return _rockets[channel]


def is_processed(channel: str, message_num: int):
    """Check if the message with number `message_num` on the given channel has been processed"""
    return message_num in _processed_message_num[channel]


def update_type(metadata: schemas.MessageMetadata, rocket_type: str):
    rocket = get(metadata.channel)
    rocket.type, rocket.latest_update, _ = (
        rocket_type,
        metadata.messageTime,
        _processed_message_num[metadata.channel].add(metadata.messageNumber),
    )
    _rockets[metadata.channel] = rocket


def update_speed(metadata: schemas.MessageMetadata, speed: int):
    rocket = get(metadata.channel)
    rocket.speed, rocket.latest_update, _ = (
        rocket.speed + speed,
        metadata.messageTime,
        _processed_message_num[metadata.channel].add(metadata.messageNumber),
    )
    _rockets[metadata.channel] = rocket


def update_exploded_reason(metadata: schemas.MessageMetadata, reason: str):
    rocket = get(metadata.channel)
    rocket.exploded_reason, rocket.latest_update, _ = (
        reason,
        metadata.messageTime,
        _processed_message_num[metadata.channel].add(metadata.messageNumber),
    )
    _rockets[metadata.channel] = rocket


def update_mission(metadata: schemas.MessageMetadata, mission: str):
    rocket = get(metadata.channel)
    rocket.mission, rocket.latest_update, rocket.latest_mission_msg, _ = (
        mission,
        metadata.messageTime,
        metadata.messageNumber,
        _processed_message_num[metadata.channel].add(metadata.messageNumber),
    )
    _rockets[metadata.channel] = rocket
