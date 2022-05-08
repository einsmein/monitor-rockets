"""
Redis backend

Status of rockets: Hashmap
"<channel>":
  {"type": str, "speed": int, "exploded_reason": str, "mission": str, "latest_update": str}

Processed messages: Sets
"<channel>-processed": set()

Channels: Sets
"channels": set()

"""
from src import schemas
from redis import Redis


_redis = Redis(host="localhost", port=6379, decode_responses=True)


def _get_processed_cache_key(channel):
    return f"{channel}-processed"


def get_channels():
    return _redis.smembers("channels")


def get(channel):
    _redis.sadd("channels", channel)
    rocket = schemas.Rocket(**_redis.hgetall(channel))
    print(rocket)
    raise
    return rocket

def is_processed(channel: str, message_number: int):
    return _redis.sismember(_get_processed_cache_key(channel), message_number)

def process_message_launched(
    rocket: schemas.Rocket,
    metadata: schemas.MessageMetadata,
    message: schemas.MessageType.RocketLaunched,
):
    rocket.type, rocket.speed, rocket.mission, rocket.latest_update = (
        message.type,
        rocket.speed + message.launchSpeed,
        message.mission,
        metadata.messageTime.isoformat(),
    )

    pipe = _redis.pipeline()
    pipe.hmset(metadata.channel, rocket.dict())
    pipe.sadd(_get_processed_cache_key(metadata.channel), metadata.messageNumber)
    pipe.execute()


def process_message_speed_increased(
    rocket: schemas.Rocket,
    metadata: schemas.MessageMetadata,
    message: schemas.MessageType.RocketSpeedIncreased,
):
    pass


def process_message_speed_decreased(
    rocket: schemas.Rocket,
    metadata: schemas.MessageMetadata,
    message: schemas.MessageType.RocketSpeedIncreased,
):
    pass


def process_message_exploded(
    rocket: schemas.Rocket,
    metadata: schemas.MessageMetadata,
    message: schemas.MessageType.RocketSpeedIncreased,
):
    pass


def process_message_mission_changed(
    rocket: schemas.Rocket,
    metadata: schemas.MessageMetadata,
    message: schemas.MessageType.RocketSpeedIncreased,
):
    pass
