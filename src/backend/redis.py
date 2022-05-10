"""
Redis store
"""

from contextlib import contextmanager
from datetime import datetime

from redis import Redis

from src import schemas

_redis = Redis(host="localhost", port=6379, decode_responses=True)


def _get_processed_cache_key(channel):
    """Get redis key that keeps processed message number for a given `channel`"""
    return f"{channel}-processed"


@contextmanager
def _process_message(metadata):
    """
    Context manager to process a message as transactions,
    update channel's latest update timestamp and processed message numbers
    """
    pipe = _redis.pipeline()
    yield pipe
    pipe.hmset("latest_update_timestamp", {metadata.channel: metadata.messageTime})
    pipe.sadd(_get_processed_cache_key(metadata.channel), metadata.messageNumber)
    pipe.execute()


def get_channels():
    """
    Get all channels. The result is sorted by latest update
    timestamp in an ascending order.
    """
    latest = _redis.hgetall("latest_update_timestamp")
    return [
        channel
        for channel, latest_update in sorted(
            latest.items(), key=lambda t: datetime.fromisoformat(t[1])
        )
    ]


def get(channel: str):
    """Get state of a rocket on the given `channel`"""
    timestamp = _redis.hmget("latest_update_timestamp", channel)[0]
    rocket = schemas.Rocket(latest_update=timestamp or "", **_redis.hgetall(channel))
    return rocket


def is_processed(channel: str, message_number: int):
    """Check if the message with number `message_num` on the given channel has been processed"""
    return _redis.sismember(_get_processed_cache_key(channel), message_number)


def update_type(metadata: schemas.MessageMetadata, rocket_type: str):
    with _process_message(metadata) as pipe:
        pipe.hmset(
            metadata.channel,
            {
                "type": rocket_type,
            },
        )


def update_speed(metadata: schemas.MessageMetadata, speed: int):
    rocket = get(metadata.channel)
    with _process_message(metadata) as pipe:
        pipe.hmset(
            metadata.channel,
            {
                "speed": rocket.speed + speed,
            },
        )


def update_exploded_reason(metadata: schemas.MessageMetadata, reason: str):
    with _process_message(metadata) as pipe:
        pipe.hmset(
            metadata.channel,
            {
                "exploded_reason": reason,
                "latest_exploded_msg": metadata.messageNumber,
            },
        )


def update_mission(metadata: schemas.MessageMetadata, mission: str):
    with _process_message(metadata) as pipe:
        pipe.hmset(
            metadata.channel,
            {
                "mission": mission,
                "latest_mission_msg": metadata.messageNumber,
            },
        )
