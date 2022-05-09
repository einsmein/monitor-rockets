# Rocket monitoring

## Quickstart

Run `pipenv install --sync` to install required python packages and
call `./run`. Use an option `-r` to use redis as a storage backend.

## Implementation summary

Rocket state contains a _type_, _speed_, _mission_ and _reason_ for explosion if it has exploded.
Speed is accumulated across all speed-related messages. 
Order does not matter since the response is best-effort (see design decision below).
Some extra information is stored along with the state i.e. 
`latest_mission_msg` and `latest_exploded_msg` which keep track of 
the latest message number related to mission and explosion. 
This is so that the latest information does not get overwritten by an older message 
that arrives late.

## Design decision

### Best-effort response
State of the rockets tracked by the application is best-effort rather than exact.
In other words, it will return the state that it believe the rocket is in
according to the messages it has processed. 
_An alternative would be to return the exact knowledge, meaning that the application
only returns information collected from messages in-order.
Messages that arrive out of order can be cached in a min-heap, and get processed when the
missing messages arrive._

### Store backend
The underlying store of information is plugged in as backend modules
to decouple application code from the actual storage implementation.
Two backends are supported here: in-memory and redis.

#### Redis data structure
Redis is a key-value store, where value can be of various types e.g. hash, set, string.
This application defined three types of entries.

1. **A state of a rocket** is kept as hash value, with _channel_ as key.
The state contains _type_, _speed_, _exploded_reason_ 
(empty if the rocket has not exploded), and _mission_ (current mission).
```
"<channel>": {"type": str, "speed": int, "exploded_reason": str, "mission": str}
```

2. **A list of processed message numbers** for each channel are kept in a set.
The key is the channel name followed py `-process`.
```
"<channel>-processed": set()
```
_Note: Currently the set keeps every message number ever processed, which doesn't scale well.
One solution is to keep track of the highest number of a complete sequence,
and discard everything below that number. For example, if messages (1,2,3,4,6,7,...) has been processed,
then we only store (4,6,7,...). We can then ignore any message with number <= 4._

3. **Timestamp of latest update** for all channel is saved as one entry with the key
`latest_update_timestamp`. It is a value within a hash whose fields are channel names.
```
"latest_update_timestamp": {"<channel>": "<latest_update_timestamp>"}
```

