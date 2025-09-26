import os
import json
from pathlib import Path
from datetime import datetime, timezone
import requests

BRS_URL = "https://brsapi.ir/Api/Market/Gold_Currency.php"
TIMEOUT = 8
STORE_PATH = Path("data/brs_usage.json")
DAILY_LIMIT = 1500

class BrsRateLimitError(Exception):
    pass

def _load_usage():
    if STORE_PATH.exists():
        try:
            return json.loads(STORE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def _save_usage(data):
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STORE_PATH.write_text(json.dumps(data), encoding="utf-8")

def _check_and_increment():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    data = _load_usage()
    day_info = data.get(today, {"count": 0})
    if day_info["count"] >= DAILY_LIMIT:
        raise BrsRateLimitError("Daily BRS API limit reached")
    day_info["count"] += 1
    data[today] = day_info
    _save_usage(data)

def fetch_brs():
    key = os.environ.get("BRS_API_KEY")
    if not key:
        return None  # optional: silently skip if no key set
    _check_and_increment()
    params = {"key": key}
    resp = requests.get(BRS_URL, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()
