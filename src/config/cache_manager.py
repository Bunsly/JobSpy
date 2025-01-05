from cachebox import LRUCache


class CacheboxCacheManager:
    def __init__(self):
        self._cache = LRUCache(50)

    def find(self, cache_id: str):
        """Finding cached data by id, else None"""
        return self._cache.get(cache_id)

    def save(self, cache_id: str, data):
        """Finding cached data by id, else None"""
        self._cache.insert(cache_id, data)


cache_manager = CacheboxCacheManager()
