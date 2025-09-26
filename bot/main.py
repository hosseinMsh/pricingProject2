import os
import logging
from telegram import Update, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from fetcher import fetch_markets
from formatter import format_markets
from brs_fetcher import fetch_brs, BrsRateLimitError
from brs_formatter import format_brs, BRS_KEYS
from storage import get_user_prefs, set_user_mode, toggle_custom
import dotenv
dotenv.load_dotenv()
logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
LABEL_PRICE_FA = os.environ.get("LABEL_PRICE_FA", "قیمت")

def _reply_kbd():
    return ReplyKeyboardMarkup([[KeyboardButton(LABEL_PRICE_FA)]], resize_keyboard=True)

def _mode_menu(mode: str):
    kb = [
        [
            InlineKeyboardButton("All", callback_data="mode:all"),
            InlineKeyboardButton("Important", callback_data="mode:important"),
            InlineKeyboardButton("Custom", callback_data="mode:custom"),
        ],
        [InlineKeyboardButton("Customize…", callback_data="custom:open")],
        [InlineKeyboardButton("Refresh", callback_data="action:refresh")],
    ]
    return InlineKeyboardMarkup(kb)

def _custom_menu(selected: set[str], page: int = 0, page_size: int = 8):
    # Build paginated toggle buttons from BRS_KEYS
    keys = sorted(BRS_KEYS.keys())
    start = page * page_size
    chunk = keys[start:start+page_size]
    rows = []
    for k in chunk:
        mark = "✅" if k in selected else "⬜️"
        rows.append([InlineKeyboardButton(f"{mark} {k}", callback_data=f"toggle:{k}")])
    nav = []
    if start > 0:
        nav.append(InlineKeyboardButton("Prev", callback_data=f"page:{page-1}"))
    if start + page_size < len(keys):
        nav.append(InlineKeyboardButton("Next", callback_data=f"page:{page+1}"))
    rows.append(nav or [InlineKeyboardButton("Back", callback_data="custom:back")])
    rows.append([InlineKeyboardButton("Back", callback_data="custom:back")])
    return InlineKeyboardMarkup(rows)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! از /gheymat یا دکمهٔ زیر استفاده کن. می‌تونی حالت نمایش رو هم تغییر بدی.",
        reply_markup=_reply_kbd()
    )

async def gheymat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    prefs = get_user_prefs(chat_id)
    await _send_prices(update, context, prefs["mode"], set(prefs["custom"]), show_menu=True)

async def price_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text == LABEL_PRICE_FA:
        await gheymat(update, context)

async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data or ""
    chat_id = update.effective_chat.id
    prefs = get_user_prefs(chat_id)

    if data.startswith("mode:"):
        mode = data.split(":", 1)[1]
        set_user_mode(chat_id, mode)
        prefs = get_user_prefs(chat_id)
        await query.answer(f"Mode set to {mode}")
        await _edit_prices(query, context, prefs["mode"], set(prefs["custom"]))
        return

    if data == "custom:open":
        await query.answer("Customize")
        selected = set(prefs["custom"])
        await query.edit_message_reply_markup(reply_markup=_custom_menu(selected, page=0))
        return

    if data.startswith("toggle:"):
        key = data.split(":", 1)[1]
        sel = set(toggle_custom(chat_id, key))
        await query.answer(f"Toggled {key}")
        # keep current page if present
        page = int(context.user_data.get("page", 0))
        await query.edit_message_reply_markup(reply_markup=_custom_menu(sel, page=page))
        return

    if data.startswith("page:"):
        page = int(data.split(":", 1)[1])
        context.user_data["page"] = page
        sel = set(prefs["custom"])
        await query.edit_message_reply_markup(reply_markup=_custom_menu(sel, page=page))
        return

    if data == "custom:back":
        await query.answer("Back")
        await _edit_prices(query, context, prefs["mode"], set(prefs["custom"]))
        return

    if data == "action:refresh":
        await query.answer("Refreshing…")
        await _edit_prices(query, context, prefs["mode"], set(prefs["custom"]))
        return

async def _compose_message(mode: str, custom: set[str]):
    # Bitpin (optional filtering via keep_codes if you want; here we keep default)
    bitpin = fetch_markets()
    bitpin_msg = format_markets(bitpin)

    brs_msg = ""
    try:
        from brs_fetcher import fetch_brs
        brs = fetch_brs()
        brs_msg = format_brs(brs, filters=custom if mode=="custom" else None, mode=mode)
    except BrsRateLimitError:
        brs_msg = "🏅 *Gold & Currency (BRS)*\nDaily request limit reached."

    if brs_msg:
        return f"{bitpin_msg}\n\n{brs_msg}"
    return bitpin_msg

async def _send_prices(update_or_query, context, mode: str, custom: set[str], show_menu: bool = False):
    msg = await _compose_message(mode, custom)
    if hasattr(update_or_query, "message") and update_or_query.message:
        await update_or_query.message.reply_text(
            msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=_mode_menu(mode) if show_menu else _reply_kbd()
        )
    else:
        await update_or_query.edit_message_text(
            msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=_mode_menu(mode)
        )

async def _edit_prices(query, context, mode: str, custom: set[str]):
    await _send_prices(query, context, mode, custom, show_menu=True)

def run_bot():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN env is required")
    app = Application.builder().token(BOT_TOKEN).build()

    app.bot.set_my_commands([
        BotCommand("gheymat", "Show prices (with menu)"),
        BotCommand("start", "Start the bot"),
    ])

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gheymat", gheymat))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, price_button))

    app.run_polling()

if __name__ == "__main__":
    run_bot()
