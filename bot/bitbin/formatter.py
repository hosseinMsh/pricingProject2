from datetime import datetime, timezone

def _arrow(change):
    try:
        c = float(change)
    except Exception:
        return "➖ 0%"
    if c > 0:
        return f"🟢 ▲ {c:.2f}%"
    if c < 0:
        return f"🔴 ▼ {abs(c):.2f}%"
    return "➖ 0%"

def _sep(n):
    try:
        return f"{int(float(n)):,}"
    except Exception:
        return str(n)

def format_markets(results, keep_codes=None):
    lines = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    header = f"💹 *Bitpin IRT Markets*  \n_{now}_\n"
    lines.append(header)

    for r in results:
        code_full = r.get("code", "N/A")
        code = code_full.replace("_IRT", "")
        if keep_codes and code not in keep_codes:
            continue

        c1 = r.get("currency1", {})
        name = c1.get("title", r.get("name", "N/A"))
        price = r.get("price_info", {}).get("price", "-")
        change = r.get("price_info", {}).get("change", 0)
        mn = r.get("price_info", {}).get("min", "-")
        mx = r.get("price_info", {}).get("max", "-")

        line = (
            f"*{name}* (`{code}`)\n"
            f"  • Price: `{_sep(price)}` IRT  {_arrow(change)}\n"
            f"  • 24h Min/Max: `{_sep(mn)}` / `{_sep(mx)}`\n"
        )
        lines.append(line)

    lines.append("\n— source: Bitpin API")
    return "\n".join(lines)
