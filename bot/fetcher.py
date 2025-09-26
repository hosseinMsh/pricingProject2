import requests

BITPIN_URL = "https://api.bitpin.ir/v5/mkt/markets/?quote=IRT&limit=6"
TIMEOUT = 8

def fetch_markets():
    resp = requests.get(BITPIN_URL, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    return data.get("results", [])
