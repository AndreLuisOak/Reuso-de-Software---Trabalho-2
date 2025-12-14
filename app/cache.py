import time
from typing import Any, Dict, Tuple


class TTLCache:
    """
    Cache simples com tempo de expiração (TTL).
    """

    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self._store: Dict[Tuple, Tuple[float, Any]] = {}

    def get(self, key: Tuple):
        entry = self._store.get(key)
        if not entry:
            return None

        timestamp, value = entry
        if time.time() - timestamp > self.ttl_seconds:
            del self._store[key]
            return None

        return value

    def set(self, key: Tuple, value: Any):
        self._store[key] = (time.time(), value)
