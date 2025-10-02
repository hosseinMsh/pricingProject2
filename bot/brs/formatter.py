from datetime import datetime, timezone

def _sep(n):
    try:
        return f"{int(float(n)):,}"
    except Exception:
        return str(n)

def _arrow(change_percent):
    try:
        c = float(change_percent)
    except Exception:
        return "➖ 0%"
    if c > 0:
        return f"🟢 ▲ {c:.2f}%"
    if c < 0:
        return f"🔴 ▼ {abs(c):.2f}%"
    return "➖ 0%"

def _fmt_row(name, price, unit, change_percent):
    u = unit if unit else ""
    return f"• {name}: `{_sep(price)}` {u}  {_arrow(change_percent)}"

# map keys for filtering
BRS_KEYS = {
    # gold/coins
    "gold_18k": "IR_GOLD_18K",
    "gold_24k": "IR_GOLD_24K",
    "gold_melted": "IR_GOLD_MELTED",
    "xauusd": "XAUUSD",
    "coin_1g": "IR_COIN_1G",
    "coin_quarter": "IR_COIN_QUARTER",
    "coin_half": "IR_COIN_HALF",
    "coin_emami": "IR_COIN_EMAMI",
    "coin_bahar": "IR_COIN_BAHAR",
    # currency
    "usdt_irt": "USDT_IRT",
    "usd": "USD",
    "eur": "EUR",
    "aed": "AED",
    "gbp": "GBP",
    # crypto (USD)
    "btc": "BTC",
    "eth": "ETH",
    "trx": "TRX",
    "usdt": "USDT",
}

def _want(symbol: str, filters: set | None, default_allow: bool):
    if filters is None:
        return default_allow
    # inverse lookup: symbol (like "USD") present in filters via key
    return any(BRS_KEYS.get(k) == symbol for k in filters)

def format_brs(brs, filters: set | None = None, mode: str = "important"):
    if not brs:
        return None
    lines = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines.append(f"🏅 *Gold & Currency (BRS)*  \n_{now}_")

    gold = brs.get("gold", []) or []
    cur = brs.get("currency", []) or []
    crypto = brs.get("cryptocurrency", []) or []

    # default_allow: all→True, important→False (we manually choose), custom→False (use filters)
    default_allow = True if mode == "all" else False

    gold_lines = []
    for g in gold:
        sym = g.get("symbol")
        allow = False
        if mode == "important":
            allow = sym in {"IR_GOLD_18K", "IR_GOLD_24K", "IR_COIN_EMAMI", "IR_COIN_1G", "XAUUSD"}
        else:
            allow = _want(sym, filters, default_allow)
        if allow:
            name = g.get("name_en") or g.get("name") or sym
            gold_lines.append(_fmt_row(name, g.get("price"), g.get("unit"), g.get("change_percent")))
    if gold_lines:
        lines.append("\n*Gold / Coins*")
        lines.extend(gold_lines)

    cur_lines = []
    for c in cur:
        sym = c.get("symbol")
        allow = False
        if mode == "important":
            allow = sym in {"USD", "USDT_IRT", "EUR", "AED"}
        else:
            allow = _want(sym, filters, default_allow)
        if allow:
            name = c.get("name_en") or c.get("name") or sym
            cur_lines.append(_fmt_row(name, c.get("price"), c.get("unit"), c.get("change_percent")))
    if cur_lines:
        lines.append("\n*Currency*")
        lines.extend(cur_lines)

    cr_lines = []
    for r in crypto:
        sym = r.get("symbol")
        allow = False
        if mode == "important":
            allow = sym in {"BTC", "ETH", "TRX", "USDT"}
        else:
            allow = _want(sym, filters, default_allow)
        if allow:
            name = r.get("name_en") or r.get("name") or sym
            cr_lines.append(_fmt_row(name, r.get("price"), r.get("unit"), r.get("change_percent")))
    if cr_lines:
        lines.append("\n*Crypto (USD)*")
        lines.extend(cr_lines)

    lines.append(f"\n— source: BRS API ({'mode: '+mode})")
    return "\n".join(lines)
