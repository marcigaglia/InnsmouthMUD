"""
bot.py — Entry point del MUD Bot Telegram.
Motore narrativo classico, nessuna AI esterna.

Avvio:
    export TELEGRAM_TOKEN="il_tuo_token"
    python bot.py
"""

import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from game import (
    get_session, reset_session, move_player, pick_up_item,
    describe_location, describe_move, resolve_action,
    LOCATIONS,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

DIRECTION_EMOJI = {
    "nord": "⬆️ Nord",
    "sud": "⬇️ Sud",
    "est": "➡️ Est",
    "ovest": "⬅️ Ovest",
}


def build_keyboard(state) -> InlineKeyboardMarkup:
    loc = state.current_location()
    buttons = []

    exit_row = []
    for direction in loc["exits"]:
        label = DIRECTION_EMOJI.get(direction, direction.capitalize())
        exit_row.append(InlineKeyboardButton(label, callback_data=f"move:{direction}"))
    if exit_row:
        buttons.append(exit_row)

    if loc["items"]:
        item_row = []
        for item in list(loc["items"].keys())[:3]:
            short = item[:15] + "…" if len(item) > 15 else item
            item_row.append(InlineKeyboardButton(f"🖐 {short}", callback_data=f"pick:{item}"))
        buttons.append(item_row)

    buttons.append([
        InlineKeyboardButton("🎒 Inventario", callback_data="inventory"),
        InlineKeyboardButton("❤️ Stato", callback_data="status"),
        InlineKeyboardButton("👁 Osserva", callback_data="look"),
    ])

    return InlineKeyboardMarkup(buttons)


def status_bar(state) -> str:
    hp_bar = "█" * (state.hp // 10) + "░" * (10 - state.hp // 10)
    san_bar = "█" * (state.sanity // 10) + "░" * (10 - state.sanity // 10)
    return (
        f"❤️ `{hp_bar}` {state.hp}/100\n"
        f"🧠 `{san_bar}` {state.sanity}/100"
    )


async def send_scene(update: Update, state, text: str, answer_callback: bool = False):
    keyboard = build_keyboard(state)
    loc = state.current_location()
    full_text = (
        f"📍 *{loc['name']}*\n"
        f"{'─' * 28}\n"
        f"{text}\n\n"
        f"{status_bar(state)}"
    )

    if answer_callback and update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            full_text,
            reply_markup=keyboard,
            parse_mode="Markdown",
        )
    elif update.message:
        await update.message.reply_text(
            full_text,
            reply_markup=keyboard,
            parse_mode="Markdown",
        )


async def check_game_over(update: Update, state, user_id: int) -> bool:
    if state.hp <= 0:
        await update.message.reply_text(
            "💀 *Il tuo cuore si ferma.*\n\nInnsmouth ha reclamato un'altra anima.\n\nUsa /start per ricominciare.",
            parse_mode="Markdown",
        )
        reset_session(user_id)
        return True
    if state.sanity <= 0:
        await update.message.reply_text(
            "🌀 *La tua mente si spezza.*\n\nL'orrore cosmico ha consumato la tua ragione.\n\nUsa /start per ricominciare.",
            parse_mode="Markdown",
        )
        reset_session(user_id)
        return True
    return False


# ─────────────────────────────────────────────
# Comandi
# ─────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = reset_session(user_id)

    intro = (
        "🌊 *Benvenuto a Innsmouth.*\n\n"
        "L'autobus ti ha lasciato all'imbocco del molo. Il conducente aveva "
        "la fronte sudata e non ti ha mai guardato in faccia. "
        "Ora sei solo, con una valigia consumata e un indirizzo che potrebbe non esistere.\n\n"
        "Il mare batte sulla roccia con un ritmo irregolare — quasi un linguaggio.\n\n"
        "_Usa i pulsanti per muoverti, raccogliere oggetti o osservare l'ambiente. "
        "Puoi anche scrivere liberamente azioni come: 'esamina mare', 'ascolta', 'apri porta'._"
    )

    keyboard = build_keyboard(state)
    await update.message.reply_text(intro, reply_markup=keyboard, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🕯 *Comandi disponibili*\n\n"
        "/start — Inizia (o ricomincia) l'avventura\n"
        "/look — Osserva l'ambiente\n"
        "/inventory — Controlla l'inventario\n"
        "/status — Stato del personaggio\n\n"
        "*Azioni in testo libero:*\n"
        "`esamina mare`, `ascolta`, `apri porta`,\n"
        "`leggi appunti`, `esamina mappa`, `segui luci`…\n\n"
        "Ogni stanza ha azioni specifiche da scoprire."
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def look(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = get_session(user_id)
    # Forza una nuova descrizione random (non first_visit)
    loc = state.current_location()
    import random
    narration = random.choice(loc["descriptions"])
    await send_scene(update, state, narration)


async def inventory_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = get_session(user_id)

    if state.inventory:
        items = "\n".join(f"  • {item}" for item in state.inventory)
        text = f"🎒 *Il tuo zaino contiene:*\n{items}"
    else:
        text = "🎒 Il tuo zaino è vuoto. Forse è meglio così."

    await update.message.reply_text(text, parse_mode="Markdown")


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = get_session(user_id)
    loc = state.current_location()
    luoghi_visitati = len(state.visited)

    text = (
        f"📊 *Stato del personaggio*\n\n"
        f"📍 Sei a: {loc['name']}\n"
        f"🔄 Turno: {state.turn}\n"
        f"🗺 Luoghi visitati: {luoghi_visitati}/5\n\n"
        f"{status_bar(state)}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# ─────────────────────────────────────────────
# Azioni libere
# ─────────────────────────────────────────────

async def free_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = get_session(user_id)
    action = update.message.text.strip()

    if not action:
        return

    result = resolve_action(state, action)
    narration = result["narration"]

    state.sanity = max(0, min(100, state.sanity + result.get("sanity_change", 0)))
    state.hp = max(0, min(100, state.hp + result.get("hp_change", 0)))
    state.turn += 1

    if await check_game_over(update, state, user_id):
        return

    await send_scene(update, state, narration)


# ─────────────────────────────────────────────
# Pulsanti
# ─────────────────────────────────────────────

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    state = get_session(user_id)
    data = query.data

    if data.startswith("move:"):
        direction = data.split(":", 1)[1]
        old_loc = move_player(state, direction)

        if old_loc is not None:
            transition = describe_move(old_loc, state.location)
            arrival = describe_location(state)
            narration = f"{transition}\n\n{arrival}"
            await send_scene(update, state, narration, answer_callback=True)
        else:
            await query.answer("Non puoi andare in quella direzione.", show_alert=True)

    elif data.startswith("pick:"):
        item = data.split(":", 1)[1]
        description = pick_up_item(state, item)

        if description:
            narration = f"Raccogli *{item}*.\n\n_{description}_"
            await send_scene(update, state, narration, answer_callback=True)
        else:
            await query.answer("Non trovi quell'oggetto.", show_alert=True)

    elif data == "look":
        import random
        loc = state.current_location()
        narration = random.choice(loc["descriptions"])
        await send_scene(update, state, narration, answer_callback=True)

    elif data == "inventory":
        if state.inventory:
            items = "\n".join(f"• {i}" for i in state.inventory)
            await query.answer(f"Zaino:\n{items}", show_alert=True)
        else:
            await query.answer("Il tuo zaino è vuoto.", show_alert=True)

    elif data == "status":
        loc = state.current_location()
        await query.answer(
            f"❤️ HP: {state.hp}/100\n🧠 Sanità: {state.sanity}/100\n📍 {loc['name']}\n🔄 Turno: {state.turn}",
            show_alert=True,
        )


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("Imposta la variabile d'ambiente TELEGRAM_TOKEN")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("look", look))
    app.add_handler(CommandHandler("inventory", inventory_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, free_action))

    logger.info("Bot avviato. In ascolto...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
