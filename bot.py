"""
bot.py — Entry point del MUD Bot Telegram.
Le quest vengono caricate automaticamente dalla cartella quests/.

Avvio:
    export TELEGRAM_TOKEN="il_tuo_token"
    python bot.py
"""

import logging
import os
import random
import importlib
import pkgutil
import quests

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
    use_item, render_map,
    LOCATIONS,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Caricamento automatico quest
# ─────────────────────────────────────────────

def load_quests() -> list:
    """
    Carica automaticamente tutte le quest dalla cartella quests/.
    Ogni file deve esporre una variabile 'quest' istanza di BaseQuest.
    I file che iniziano con _ o TEMPLATE vengono ignorati.
    """
    loaded = []
    for module_info in pkgutil.iter_modules(quests.__path__):
        name = module_info.name
        if name.startswith("_") or name == "base" or name.upper().startswith("TEMPLATE"):
            continue
        try:
            module = importlib.import_module(f"quests.{name}")
            if hasattr(module, "quest"):
                loaded.append(module.quest)
                logger.info(f"Quest caricata: {module.quest.QUEST_NAME}")
            else:
                logger.warning(f"quests/{name}.py non espone una variabile 'quest' — ignorato.")
        except Exception as e:
            logger.error(f"Errore caricando quests/{name}.py: {e}")
    return loaded

ACTIVE_QUESTS = load_quests()


def init_quest_data(state):
    """Assicura che state.quest_data esista."""
    if not hasattr(state, "quest_data"):
        state.quest_data = {}


# ─────────────────────────────────────────────
# UI helpers
# ─────────────────────────────────────────────

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
        InlineKeyboardButton("📜 Quest", callback_data="quest"),
    ])

    if state.inventory:
        use_row = []
        for inv_item in state.inventory[:3]:
            short = inv_item[:12] + "…" if len(inv_item) > 12 else inv_item
            use_row.append(InlineKeyboardButton(f"✨ {short}", callback_data=f"use:{inv_item}"))
        buttons.append(use_row)

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
            full_text, reply_markup=keyboard, parse_mode="Markdown"
        )
    elif update.message:
        await update.message.reply_text(
            full_text, reply_markup=keyboard, parse_mode="Markdown"
        )


async def check_game_over(update: Update, state, user_id: int) -> bool:
    msg = update.callback_query.message if update.callback_query else update.message
    if state.hp <= 0:
        await msg.reply_text(
            "💀 *Il tuo cuore si ferma.*\n\nInnsmouth ha reclamato un'altra anima.\n\nUsa /start per ricominciare.",
            parse_mode="Markdown",
        )
        reset_session(user_id)
        return True
    if state.sanity <= 0:
        await msg.reply_text(
            "🌀 *La tua mente si spezza.*\n\nL'orrore cosmico ha consumato la tua ragione.\n\nUsa /start per ricominciare.",
            parse_mode="Markdown",
        )
        reset_session(user_id)
        return True
    return False


# ─────────────────────────────────────────────
# Logica quest
# ─────────────────────────────────────────────

async def process_quest_clues(update: Update, state, action: str) -> bool:
    """
    Controlla tutte le quest per indizi sbloccabili con questa azione.
    Ritorna True se un indizio è stato trovato (l'azione è "consumata").
    """
    init_quest_data(state)
    for q in ACTIVE_QUESTS:
        clue_text = q.check_clue(state, action)
        if clue_text:
            found = len(state.quest_data.get(f"{q.QUEST_ID}_found", set()))
            total = len(q.clues)
            suffix = f"\n\n📜 _Indizi [{q.QUEST_NAME}]: {found}/{total}_"
            if found == total:
                suffix += "\n_Hai tutti gli indizi. Torna al luogo indicato..._"
            await send_scene(update, state, clue_text + suffix)
            return True
    return False


async def process_quest_finales(update: Update, state) -> bool:
    """
    Controlla se una quest ha il finale attivabile nella stanza corrente.
    Ritorna True se il finale è stato attivato.
    """
    init_quest_data(state)
    msg = update.callback_query.message if update.callback_query else update.message
    for q in ACTIVE_QUESTS:
        if q.is_finale_triggered(state):
            finale_text = q.complete(state)
            await msg.reply_text(finale_text, parse_mode="Markdown")
            await send_scene(update, state, "Il silenzio cala su di te. Hai scoperto qualcosa che non potrà essere dimenticato.")
            return True
    return False


def all_quests_status(state) -> str:
    init_quest_data(state)
    if not ACTIVE_QUESTS:
        return "Nessuna quest disponibile."
    return "\n\n".join(q.status(state) for q in ACTIVE_QUESTS)


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
        "_Usa i pulsanti per muoverti e raccogliere oggetti. "
        "Scrivi liberamente azioni come: 'esamina mare', 'ascolta', 'apri porta'. "
        "Nella capanna del pescatore trovi una mappa — usala con ✨ per orientarti._"
    )
    await update.message.reply_text(intro, reply_markup=build_keyboard(state), parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quest_list = "\n".join(f"  • {q.QUEST_NAME}" for q in ACTIVE_QUESTS) or "  Nessuna"
    text = (
        "🕯 *Comandi disponibili*\n\n"
        "/start — Inizia (o ricomincia) l'avventura\n"
        "/look — Osserva l'ambiente\n"
        "/inventory — Controlla l'inventario\n"
        "/usa `oggetto` — Usa un oggetto\n"
        "/quest — Stato delle quest\n"
        "/status — Stato del personaggio\n\n"
        "*Azioni in testo libero:*\n"
        "`esamina mare`, `ascolta`, `apri porta`,\n"
        "`leggi appunti`, `segui luci`…\n\n"
        f"*Quest attive:*\n{quest_list}\n\n"
        "✨ I pulsanti con ✨ usano gli oggetti nell'inventario."
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def look(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_session(update.effective_user.id)
    narration = random.choice(state.current_location()["descriptions"])
    await send_scene(update, state, narration)


async def inventory_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_session(update.effective_user.id)
    if state.inventory:
        items = "\n".join(f"  • {item}" for item in state.inventory)
        text = f"🎒 *Il tuo zaino contiene:*\n{items}\n\n_Usa ✨ per usare un oggetto._"
    else:
        text = "🎒 Il tuo zaino è vuoto. Forse è meglio così."
    await update.message.reply_text(text, parse_mode="Markdown")


async def usa_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_session(update.effective_user.id)
    args = context.args
    if not args:
        if not state.inventory:
            await update.message.reply_text("Non hai nulla da usare.")
            return
        items = "\n".join(f"  • {i}" for i in state.inventory)
        await update.message.reply_text(f"Cosa vuoi usare?\n\n{items}", parse_mode="Markdown")
        return
    item_name = " ".join(args)
    result = use_item(state, item_name)
    if result is None:
        await update.message.reply_text(f"Non hai '{item_name}' nell'inventario.")
    elif result.startswith("```"):
        await update.message.reply_text(result, parse_mode="Markdown")
    else:
        await send_scene(update, state, result)


async def quest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_session(update.effective_user.id)
    await update.message.reply_text(all_quests_status(state), parse_mode="Markdown")


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_session(update.effective_user.id)
    loc = state.current_location()
    text = (
        f"📊 *Stato del personaggio*\n\n"
        f"📍 Sei a: {loc['name']}\n"
        f"🔄 Turno: {state.turn}\n"
        f"🗺 Luoghi visitati: {len(state.visited)}/5\n\n"
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

    # Intercetta "usa ..."
    action_lower = action.lower()
    if action_lower.startswith("usa ") or action_lower.startswith("use "):
        item_name = action_lower.split(" ", 1)[1]
        result = use_item(state, item_name)
        if result is not None:
            if result.startswith("```"):
                await update.message.reply_text(result, parse_mode="Markdown")
            else:
                await send_scene(update, state, result)
            return

    # Controlla indizi quest
    if await process_quest_clues(update, state, action):
        return

    # Azione generica
    result = resolve_action(state, action)
    state.sanity = max(0, min(100, state.sanity + result.get("sanity_change", 0)))
    state.hp = max(0, min(100, state.hp + result.get("hp_change", 0)))
    state.turn += 1

    if await check_game_over(update, state, user_id):
        return

    await send_scene(update, state, result["narration"])


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
            # Controlla finali quest
            if await process_quest_finales(update, state):
                return
            await send_scene(update, state, narration, answer_callback=True)
        else:
            await query.answer("Non puoi andare in quella direzione.", show_alert=True)

    elif data.startswith("pick:"):
        item = data.split(":", 1)[1]
        description = pick_up_item(state, item)
        if description:
            await send_scene(update, state, f"Raccogli *{item}*.\n\n_{description}_", answer_callback=True)
        else:
            await query.answer("Non trovi quell'oggetto.", show_alert=True)

    elif data.startswith("use:"):
        item = data.split(":", 1)[1]
        result = use_item(state, item)
        if result is None:
            await query.answer("Non hai quell'oggetto.", show_alert=True)
        elif result.startswith("```"):
            await query.answer()
            await query.message.reply_text(result, parse_mode="Markdown")
        else:
            await send_scene(update, state, result, answer_callback=True)

    elif data == "look":
        narration = random.choice(state.current_location()["descriptions"])
        await send_scene(update, state, narration, answer_callback=True)

    elif data == "quest":
        await query.answer()
        await query.message.reply_text(all_quests_status(state), parse_mode="Markdown")

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
    app.add_handler(CommandHandler("usa", usa_cmd))
    app.add_handler(CommandHandler("quest", quest_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, free_action))

    logger.info(f"Bot avviato con {len(ACTIVE_QUESTS)} quest: {[q.QUEST_NAME for q in ACTIVE_QUESTS]}")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
