import os, time, json, hashlib
from typing import Any, Optional, Tuple
try:
    import redis
    HAS_REDIS=True
except Exception:
    HAS_REDIS=False

TTL_DEFAULT = int(os.getenv("CACHE_TTL_INSTRUMENT","30"))

class SimpleCache:
    def __init__(self):
        self.mem = {}
    def get(self, k:str)->Optional[Any]:
        x = self.mem.get(k); 
        if not x: return None
        v,exp = x
        if exp and exp<time.time(): 
            self.mem.pop(k, None); 
            return None
        return v
    def set(self, k:str, v:Any, ttl:int=TTL_DEFAULT):
        self.mem[k]=(v, time.time()+ttl if ttl>0 else None)

_cache = SimpleCache()
_redis: Optional["redis.Redis"] = None

def use_redis()->bool:
    return os.getenv("REDIS_URL") and HAS_REDIS

def r()->Optional["redis.Redis"]:
    global _redis
    if _redis is None and use_redis():
        _redis = redis.from_url(os.getenv("REDIS_URL"))
    return _redis

def cache_get(key:str)->Optional[str]:
    if use_redis() and r():
        v = r().get(key)
        return v.decode() if v else None
    v = _cache.get(key)
    return json.dumps(v) if v is not None else None

def cache_set(key:str, value:Any, ttl:int=TTL_DEFAULT):
    if use_redis() and r():
        r().setex(key, ttl, json.dumps(value))
    else:
        _cache.set(key, value, ttl)

def make_etag(payload:Any)->str:
    raw = json.dumps(payload, separators=(",",":"), ensure_ascii=False)
    return '"' + hashlib.sha1(raw.encode()).hexdigest() + '"'
