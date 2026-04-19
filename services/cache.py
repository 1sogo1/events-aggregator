from cachetools import TTLCache


class SeatsCache:
    def __init__(self, ttl_seconds: int = 30):
        self.cache = TTLCache(maxsize=100, ttl=ttl_seconds)
    
    def _make_key(self, event_id: str) -> str:
        return f"seats:{event_id}"
    
    def get(self, event_id: str):
        key = self._make_key(event_id)
        return self.cache.get(key)
    
    def set(self, event_id: str, seats_data: dict):
        key = self._make_key(event_id)
        self.cache[key] = seats_data
    
    def clear(self, event_id: str):
        key = self._make_key(event_id)
        if key in self.cache:
            del self.cache[key]
    
    