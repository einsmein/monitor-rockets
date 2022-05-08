import os

backend = os.getenv("STORE_BACKEND", "redis")
if backend == "redis":
    import src.backend.redis as store
elif backend == "memory":
    import src.backend.memory as store
else:
    raise RuntimeError(
        f"Supported data backend are 'redis' and 'memory', got {backend}"
    )
