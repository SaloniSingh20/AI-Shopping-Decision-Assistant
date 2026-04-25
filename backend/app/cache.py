from threading import Lock

from cachetools import TTLCache

from app.config import get_settings

_settings = get_settings()
_cache = TTLCache(maxsize=_settings.cache_maxsize, ttl=_settings.cache_ttl_seconds)
_lock = Lock()


def get_cache(key: str):
    with _lock:
        return _cache.get(key)


def set_cache(key: str, value):
    with _lock:
        _cache[key] = value


def clear_cache():
    """Clear all cached responses."""
    with _lock:
        _cache.clear()

