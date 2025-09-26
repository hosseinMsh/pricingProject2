import json
from pathlib import Path

STORE_PATH = Path("data/users.json")

DEFAULT_MODE = "important"  # all | important | custom
DEFAULT_CUSTOM = [
    "coin_emami", "coin_1g", "usd", "usdt_irt", "xauusd",  # BRS
    "btc", "eth", "trx", "usdt"                            # BRS-crypto short set
]

def _load():
    if STORE_PATH.exists():
        try:
            return json.loads(STORE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def _save(data):
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STORE_PATH.write_text(json.dumps(data), encoding="utf-8")

def get_user_prefs(chat_id: int):
    data = _load()
    key = str(chat_id)
    user = data.get(key, {})
    mode = user.get("mode", DEFAULT_MODE)
    custom = user.get("custom", DEFAULT_CUSTOM.copy())
    return {"mode": mode, "custom": custom}

def set_user_mode(chat_id: int, mode: str):
    data = _load()
    key = str(chat_id)
    user = data.get(key, {})
    user["mode"] = mode
    if "custom" not in user:
        user["custom"] = DEFAULT_CUSTOM.copy()
    data[key] = user
    _save(data)

def toggle_custom(chat_id: int, symbol_key: str):
    data = _load()
    key = str(chat_id)
    user = data.get(key, {})
    cur = set(user.get("custom", DEFAULT_CUSTOM.copy()))
    if symbol_key in cur:
        cur.remove(symbol_key)
    else:
        cur.add(symbol_key)
    user["custom"] = sorted(cur)
    user["mode"] = "custom"
    data[key] = user
    _save(data)
    return user["custom"]
