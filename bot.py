"""
bot.py — Entry point del MUD Bot Telegram.
- Quest caricate automaticamente da quests/
- Edifici caricati automaticamente da buildings/

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
import buildings

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
    use_item, render_map, check_item_combo,
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

def load_modules(package, attr_name: str) -> dict:
    """
    Carica automaticamente tutti i moduli da un package.
    Ritorna un dizionario {id: istanza} per i moduli che espongono `attr_name`.
    Ignora file che iniziano con _ o TEMPLATE.
    """
    loaded = {}
    for module_info in pkgutil.iter_modules(package.__path__):
        name = module_info.name
        if name.startswith("_") or name == "base" or name.upper().startswith("TEMPLATE"):
            continue
        try:
            module = importlib.import_module(f"{package.__name__}.{name}")
            if hasattr(module, attr_name):
                obj = getattr(module, attr_name)
                key = getattr(obj, "QUEST_ID", None) or getattr(obj, "BUILDING_ID", None)
                loaded[key] = obj
                display = getattr(obj, "QUEST_NAME", None) or getattr(obj, "BUILDING_NAME", None)
                logger.info(f"[{package.__name__}] Caricato: {display}")
        except Exception as e:
            logger.error(f"Errore caricando {package.__name__}/{name}.py: {e}")
    return loaded

ACTIVE_QUESTS = list(load_modules(quests, "quest").values())
ACTIVE_BUILDINGS = load_modules(buildings, "building")  # {BUILDING_ID: building}


def get_building_for_location(location_id: str):
    """Ritorna l'edificio collegato alla location, se esiste."""
    return ACTIVE_BUILDINGS.get(location_id)


def get_current_building(state):
    """Ritorna l'edificio in cui si trova il giocatore, o None."""
    if state.current_building:
        return ACTIVE_BUILDINGS.get(state.current_building)
    return None


# ─────────────────────────────────────────────
# UI helpers
# ─────────────────────────────────────────────

DIRECTION_EMOJI = {
    "nord": "⬆️ Nord",
    "sud": "⬇️ Sud",
    "est": "➡️ Est",
    "ovest": "⬅️ Ovest",
    "su": "🔼 Su",
    "giu": "🔽 Giù",
}


def build_keyboard(state) -> InlineKeyboardMarkup:
    buttons = []

    if state.current_building:
        # ── Dentro un edificio ──
        building = get_current_building(state)
        room = building.get_room(state.current_room) if building else None

        if room:
            # Pulsanti direzioni interne (include uscite dinamiche)
            exit_row = []
            for direction in building.get_exits(state.current_room, state):
                label = DIRECTION_EMOJI.get(direction, direction.capitalize())
                exit_row.append(InlineKeyboardButton(label, callback_data=f"room_move:{direction}"))
            if exit_row:
                buttons.append(exit_row)

            # Oggetti raccoglibili nella stanza
            if room.items:
                item_row = []
                for item in list(room.items.keys())[:3]:
                    short = item[:15] + "…" if len(item) > 15 else item
                    item_row.append(InlineKeyboardButton(f"🖐 {short}", callback_data=f"room_pick:{item}"))
                buttons.append(item_row)

        # Azioni fisse interno
        action_row = [
            InlineKeyboardButton("🎒 Inventario", callback_data="inventory"),
            InlineKeyboardButton("👁 Osserva", callback_data="room_look"),
            InlineKeyboardButton("📜 Quest", callback_data="quest"),
        ]
        # Esci solo se sei nella stanza di ingresso
        if building and state.current_room == building.ENTRY_ROOM:
            action_row.insert(0, InlineKeyboardButton("🚪 Esci", callback_data="building_exit"))
        buttons.append(action_row)

    else:
        # ── Mappa esterna ──
        loc = LOCATIONS[state.location]
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

        # Pulsante Entra se c'è un edificio collegato
        building = get_building_for_location(state.location)
        action_row = [
            InlineKeyboardButton("🎒 Inventario", callback_data="inventory"),
            InlineKeyboardButton("❤️ Stato", callback_data="status"),
            InlineKeyboardButton("👁 Osserva", callback_data="look"),
            InlineKeyboardButton("📜 Quest", callback_data="quest"),
        ]
        if building:
            action_row.insert(0, InlineKeyboardButton(f"🚪 Entra", callback_data="building_enter"))
        buttons.append(action_row)

    # Oggetti usabili dall'inventario
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


def location_header(state) -> str:
    if state.current_building:
        building = get_current_building(state)
        room = building.get_room(state.current_room) if building else None
        room_name = room.name if room else "???"
        return f"🏛 *{building.BUILDING_NAME}* › {room_name}"
    else:
        return f"📍 *{LOCATIONS[state.location]['name']}*"


async def send_scene(update: Update, state, text: str, answer_callback: bool = False):
    keyboard = build_keyboard(state)
    full_text = (
        f"{location_header(state)}\n"
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
    msg = update.callback_query.message if update.callback_query else update.message
    for q in ACTIVE_QUESTS:
        if q.is_finale_triggered(state):
            finale_text = q.complete(state)
            await msg.reply_text(finale_text, parse_mode="Markdown")
            await send_scene(update, state, "Il silenzio cala su di te. Hai scoperto qualcosa che non potrà essere dimenticato.")
            return True
    return False


def all_quests_status(state) -> str:
    if not ACTIVE_QUESTS:
        return "Nessuna quest disponibile."
    return "\n\n".join(q.status(state) for q in ACTIVE_QUESTS)


# ─────────────────────────────────────────────
# Comandi
# ─────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = reset_session(user_id)
    buildings_list = ", ".join(b.BUILDING_NAME for b in ACTIVE_BUILDINGS.values())
    intro = (
        "🌊 *Benvenuto a Innsmouth.*\n\n"
        "L'autobus ti ha lasciato all'imbocco del molo. Il conducente aveva "
        "la fronte sudata e non ti ha mai guardato in faccia. "
        "Ora sei solo, con una valigia consumata e un indirizzo che potrebbe non esistere.\n\n"
        "Il mare batte sulla roccia con un ritmo irregolare — quasi un linguaggio.\n\n"
        "_Usa i pulsanti per muoverti. Quando sei davanti a un edificio appare 🚪 Entra. "
        "Scrivi liberamente azioni come: 'ascolta', 'esamina', 'guarda'._"
    )
    await update.message.reply_text(intro, reply_markup=build_keyboard(state), parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quest_list = "\n".join(f"  • {q.QUEST_NAME}" for q in ACTIVE_QUESTS) or "  Nessuna"
    buildings_list = "\n".join(f"  • {b.BUILDING_NAME}" for b in ACTIVE_BUILDINGS.values()) or "  Nessuno"
    text = (
        "🕯 *Comandi disponibili*\n\n"
        "/start — Inizia (o ricomincia) l'avventura\n"
        "/look — Osserva l'ambiente\n"
        "/inventory — Controlla l'inventario\n"
        "/usa `oggetto` — Usa un oggetto\n"
        "/quest — Stato delle quest\n"
        "/status — Stato del personaggio\n\n"
        "*Azioni in testo libero:*\n"
        "`esamina`, `ascolta`, `apri porta`, `leggi`…\n\n"
        f"*Quest attive:*\n{quest_list}\n\n"
        f"*Edifici esplorabili:*\n{buildings_list}\n\n"
        "🚪 = Entra/Esci da edificio  ✨ = Usa oggetto"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def look(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_session(update.effective_user.id)
    if state.current_building:
        building = get_current_building(state)
        narration = random.choice(building.get_room(state.current_room).descriptions)
    else:
        narration = random.choice(LOCATIONS[state.location]["descriptions"])
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
    loc_name = LOCATIONS[state.location]["name"]
    text = (
        f"📊 *Stato del personaggio*\n\n"
        f"📍 Posizione: {loc_name}"
        + (f" › {get_current_building(state).get_room(state.current_room).name}" if state.current_building else "")
        + f"\n🔄 Turno: {state.turn}\n"
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

    # Controlla combo tra oggetti
    combo = check_item_combo(state, action)
    if combo:
        await send_scene(update, state, combo["result"])
        return

    # Azioni dentro un edificio
    if state.current_building:
        building = get_current_building(state)

        # Controlla combo oggetti
        combo = check_item_combo(state, action)
        if combo:
            await send_scene(update, state, combo["result"])
            return

        result = building.resolve_action(state.current_room, action)
        if result:
            state.turn += 1
            await send_scene(update, state, result)
            return
        # Prova indizi quest anche dentro gli edifici
        if await process_quest_clues(update, state, action):
            return
        await send_scene(update, state, random.choice([
            "Non succede nulla di particolare. Ma la sensazione di essere osservato si intensifica.",
            "Provi, ma questo posto non ti offre risposte facili.",
            "Il silenzio è la sola risposta che ricevi.",
        ]))
        return

    # Azioni sulla mappa esterna
    if await process_quest_clues(update, state, action):
        return

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

    # ── Entrata edificio ──
    if data == "building_enter":
        building = get_building_for_location(state.location)
        if building:
            state.current_building = building.BUILDING_ID
            state.current_room = building.ENTRY_ROOM
            arrival = building.describe_room(state, state.current_room)
            narration = f"{building.ENTRY_TEXT}\n\n{arrival}"
            await send_scene(update, state, narration, answer_callback=True)
        else:
            await query.answer("Non c'è nulla in cui entrare.", show_alert=True)

    # ── Uscita edificio ──
    elif data == "building_exit":
        building = get_current_building(state)
        exit_text = building.EXIT_TEXT if building else "Esci."
        state.current_building = None
        state.current_room = None
        loc_desc = random.choice(LOCATIONS[state.location]["descriptions"])
        await send_scene(update, state, f"{exit_text}\n\n{loc_desc}", answer_callback=True)

    # ── Movimento interno edificio ──
    elif data.startswith("room_move:"):
        direction = data.split(":", 1)[1]
        building = get_current_building(state)
        new_room_id = building.move(state.current_room, direction, state)
        if new_room_id:
            state.current_room = new_room_id
            state.turn += 1
            narration = building.describe_room(state, new_room_id)
            if await check_game_over(update, state, user_id):
                return
            await send_scene(update, state, narration, answer_callback=True)
        else:
            await query.answer("Non puoi andare in quella direzione.", show_alert=True)

    # ── Osserva interno ──
    elif data == "room_look":
        building = get_current_building(state)
        room = building.get_room(state.current_room)
        narration = random.choice(room.descriptions)
        await send_scene(update, state, narration, answer_callback=True)

    # ── Raccogli oggetto interno ──
    elif data.startswith("room_pick:"):
        item = data.split(":", 1)[1]
        building = get_current_building(state)
        description = building.pick_item(state, state.current_room, item)
        if description:
            await send_scene(update, state, f"Raccogli *{item}*.\n\n_{description}_", answer_callback=True)
        else:
            await query.answer("Non trovi quell'oggetto.", show_alert=True)

    # ── Movimento mappa esterna ──
    elif data.startswith("move:"):
        direction = data.split(":", 1)[1]
        old_loc = move_player(state, direction)
        if old_loc is not None:
            transition = describe_move(old_loc, state.location)
            arrival = describe_location(state)
            narration = f"{transition}\n\n{arrival}"
            if await process_quest_finales(update, state):
                return
            await send_scene(update, state, narration, answer_callback=True)
        else:
            await query.answer("Non puoi andare in quella direzione.", show_alert=True)

    # ── Raccogli oggetto esterno ──
    elif data.startswith("pick:"):
        item = data.split(":", 1)[1]
        description = pick_up_item(state, item)
        if description:
            await send_scene(update, state, f"Raccogli *{item}*.\n\n_{description}_", answer_callback=True)
        else:
            await query.answer("Non trovi quell'oggetto.", show_alert=True)

    # ── Usa oggetto ──
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
        narration = random.choice(LOCATIONS[state.location]["descriptions"])
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
        loc = LOCATIONS[state.location]
        await query.answer(
            f"❤️ HP: {state.hp}/100\n🧠 Sanità: {state.sanity}/100\n"
            f"📍 {loc['name']}\n🔄 Turno: {state.turn}",
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

    logger.info(f"Quest caricate: {[q.QUEST_NAME for q in ACTIVE_QUESTS]}")
    logger.info(f"Edifici caricati: {[b.BUILDING_NAME for b in ACTIVE_BUILDINGS.values()]}")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
