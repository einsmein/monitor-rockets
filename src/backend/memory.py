from collections import defaultdict
from src import schemas

_rockets = defaultdict(schemas.Rocket)
_processed_message_num = defaultdict(set)


def get_channels():
    return list(_rockets.keys())


def get(channel: str):
    """Get status of a rocket on the given `channel`"""
    r = _rockets[channel]
    return r


def is_processed(channel: str, message_num: int):
    """Check if the message with number `message_num` on the given channel has been processed"""
    return message_num in _processed_message_num[channel]


def process_message_launched(
    rocket: schemas.Rocket,
    metadata: schemas.MessageMetadata,
    message: schemas.MessageType.RocketLaunched,
):
    rocket.type, rocket.speed, rocket.mission, rocket.latest_update, _ = (
        message.type,
        rocket.speed + message.launchSpeed,
        message.mission,
        metadata.messageTime,
        _processed_message_num[metadata.channel].add(metadata.messageNumber),
    )


def process_message_speed_increased(
    rocket: schemas.Rocket,
    metadata: schemas.MessageMetadata,
    message: schemas.MessageType.RocketSpeedIncreased,
):
    rocket.speed, rocket.latest_update, _ = (
        rocket.speed + message.by,
        metadata.messageTime,
        _processed_message_num[metadata.channel].add(metadata.messageNumber),
    )


def process_message_speed_decreased(
    rocket: schemas.Rocket,
    metadata: schemas.MessageMetadata,
    message: schemas.MessageType.RocketSpeedIncreased,
):
    rocket.speed, rocket.latest_update, _ = (
        rocket.speed - message.by,
        metadata.messageTime,
        _processed_message_num[metadata.channel].add(metadata.messageNumber),
    )


def process_message_exploded(
    rocket: schemas.Rocket,
    metadata: schemas.MessageMetadata,
    message: schemas.MessageType.RocketSpeedIncreased,
):
    rocket.exploded_reason, rocket.latest_update, _ = (
        message.reason,
        metadata.messageTime,
        _processed_message_num[metadata.channel].add(metadata.messageNumber),
    )


def process_message_mission_changed(
    rocket: schemas.Rocket,
    metadata: schemas.MessageMetadata,
    message: schemas.MessageType.RocketSpeedIncreased,
):
    rocket.mission, rocket.latest_update, _ = (
        message.newMission,
        metadata.messageTime,
        _processed_message_num[metadata.channel].add(metadata.messageNumber),
    )
