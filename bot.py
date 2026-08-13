"""
bot.py — Entry point del MUD Bot Telegram.

Avvio:
    export TELEGRAM_TOKEN="il_tuo_token"
    export ANTHROPIC_API_KEY="la_tua_chiave"
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

from game import get_session, reset_session, move_player, pick_up_item, LOCATIONS
from ai_narrator import narrate, narrate_arrival

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

DIRECTION_EMOJI = {
    "nord": "⬆️ Nord",
    "sud": "⬇️ Sud",
    "est": "➡️ Est",
    "ovest": "⬅️ Ovest",
}


def build_keyboard(state) -> InlineKeyboardMarkup:
    """Costruisce la tastiera inline con le azioni disponibili."""
    loc = state.current_location()
    buttons = []

    # Pulsanti movimento
    exit_row = []
    for direction in loc["exits"]:
        label = DIRECTION_EMOJI.get(direction, direction.capitalize())
        exit_row.append(InlineKeyboardButton(label, callback_data=f"move:{direction}"))
    if exit_row:
        buttons.append(exit_row)

    # Pulsanti raccolta oggetti
    if loc["items"]:
        item_row = []
        for item in loc["items"][:3]:  # max 3 oggetti per riga
            short = item[:15] + "…" if len(item) > 15 else item
            item_row.append(InlineKeyboardButton(f"🖐 {short}", callback_data=f"pick:{item}"))
        buttons.append(item_row)

    # Pulsanti fissi
    buttons.append([
        InlineKeyboardButton("🎒 Inventario", callback_data="inventory"),
        InlineKeyboardButton("❤️ Stato", callback_data="status"),
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
    """Invia la scena al giocatore con tastiera e barra di stato."""
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
        await update.callback_query.edit_message_text(
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


# ─────────────────────────────────────────────
# Handlers comandi
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
        "_Cosa fai?_"
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
        "Puoi anche digitare liberamente azioni come:\n"
        "`esamina la lanterna`, `guardo fuori dalla finestra`, `ascolto i rumori`\n\n"
        "Usa i pulsanti per muoverti e raccogliere oggetti."
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def look(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = get_session(user_id)
    loc = state.current_location()

    result = narrate("Il giocatore esamina attentamente l'ambiente circostante", state.to_context())
    narration = result.get("narration", loc["description"])

    state.sanity = max(0, state.sanity + result.get("sanity_change", 0))
    state.hp = max(0, state.hp + result.get("hp_change", 0))
    state.add_history(f"Osserva il luogo: {narration[:80]}…")

    await send_scene(update, state, narration)


async def inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    text = (
        f"📊 *Stato del personaggio*\n\n"
        f"📍 Sei a: {loc['name']}\n"
        f"🔄 Turno: {state.turn}\n\n"
        f"{status_bar(state)}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# ─────────────────────────────────────────────
# Handler messaggi liberi
# ─────────────────────────────────────────────

async def free_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce azioni in testo libero."""
    user_id = update.effective_user.id
    state = get_session(user_id)
    action = update.message.text.strip()

    if not action:
        return

    result = narrate(action, state.to_context())
    narration = result.get("narration", "Non succede nulla di rilevante.")

    state.sanity = max(0, min(100, state.sanity + result.get("sanity_change", 0)))
    state.hp = max(0, min(100, state.hp + result.get("hp_change", 0)))
    state.add_history(f"[{action}]: {narration[:80]}…")
    state.turn += 1

    # Controlla morte / follia
    if state.hp <= 0:
        await update.message.reply_text(
            "💀 *Il tuo cuore si ferma.*\n\nInnsmouth ha reclamato un'altra anima.\n\nUsa /start per ricominciare.",
            parse_mode="Markdown",
        )
        reset_session(user_id)
        return

    if state.sanity <= 0:
        await update.message.reply_text(
            "🌀 *La tua mente si spezza.*\n\nL'orrore cosmico ha consumato la tua ragione.\n\nUsa /start per ricominciare.",
            parse_mode="Markdown",
        )
        reset_session(user_id)
        return

    await send_scene(update, state, narration)


# ─────────────────────────────────────────────
# Handler callback pulsanti
# ─────────────────────────────────────────────

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    state = get_session(user_id)
    data = query.data

    if data.startswith("move:"):
        direction = data.split(":", 1)[1]
        new_loc = move_player(state, direction)

        if new_loc:
            loc_name = LOCATIONS[new_loc]["name"]
            narration = narrate_arrival(loc_name, state.to_context())
            state.add_history(f"Si sposta verso {direction}: arriva a {loc_name}.")
            await send_scene(update, state, narration, answer_callback=True)
        else:
            await query.answer("Non puoi andare in quella direzione.", show_alert=True)

    elif data.startswith("pick:"):
        item = data.split(":", 1)[1]
        success = pick_up_item(state, item)

        if success:
            result = narrate(f"Raccoglie: {item}", state.to_context())
            narration = result.get("narration", f"Prendi {item} e lo metti nello zaino.")
            state.sanity = max(0, state.sanity + result.get("sanity_change", 0))
            state.add_history(f"Raccoglie {item}.")
            await send_scene(update, state, narration, answer_callback=True)
        else:
            await query.answer("Non trovi quell'oggetto.", show_alert=True)

    elif data == "inventory":
        if state.inventory:
            items = "\n".join(f"• {i}" for i in state.inventory)
            await query.answer(f"Zaino:\n{items}", show_alert=True)
        else:
            await query.answer("Il tuo zaino è vuoto.", show_alert=True)

    elif data == "status":
        loc = state.current_location()
        await query.answer(
            f"❤️ HP: {state.hp}/100\n🧠 Sanità: {state.sanity}/100\n📍 {loc['name']}",
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
    app.add_handler(CommandHandler("inventory", inventory))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, free_action))

    logger.info("Bot avviato. In ascolto...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
