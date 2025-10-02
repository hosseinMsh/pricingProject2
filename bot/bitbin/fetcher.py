import time
import requests

BITPIN_URL = "https://api.bitpin.ir/v5/mkt/markets/?quote=IRT&limit=6"
TIMEOUT = 8
_TTL = 30  # seconds
_CACHE = {"ts": 0.0, "data": []}

def fetch_markets():
    now = time.time()
    if now - _CACHE["ts"] <= _TTL and _CACHE["data"]:
        return _CACHE["data"]
    resp = requests.get(BITPIN_URL, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json().get("results", [])
    _CACHE["data"] = data
    _CACHE["ts"] = now
    return data
