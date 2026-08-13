"""
game.py — Stato del giocatore e logica di gioco.
Ogni utente Telegram ha una propria sessione indipendente.
"""

from dataclasses import dataclass, field
from typing import Optional

LOCATIONS = {
    "innsmouth_dock": {
        "name": "Molo di Innsmouth",
        "description": (
            "Un molo marcio si stende sul mare nerastro. L'aria sa di alghe e qualcosa "
            "di più antico. Le barche di legno scricchiolano come se qualcosa le spingesse dall'interno."
        ),
        "exits": {"nord": "main_street", "est": "fishermans_hut"},
        "items": ["rete arrugginita", "lanterna spenta"],
    },
    "main_street": {
        "name": "Via Principale di Innsmouth",
        "description": (
            "Case abbandonate dai tetti sfondati fiancheggiano la strada. Le finestre sono "
            "sbarrate con assi, ma dietro qualcuna intravedi un bagliore verdastro. "
            "Nessun abitante in vista — eppure senti passi alle tue spalle."
        ),
        "exits": {"sud": "innsmouth_dock", "est": "old_church", "nord": "marshes"},
        "items": ["giornale ingiallito"],
    },
    "old_church": {
        "name": "Antica Chiesa di Dagon",
        "description": (
            "Una chiesa convertita a qualcosa di innominabile. Sul portale campeggia un rilievo "
            "di una creatura metà pesce metà uomo. L'interno è buio, ma un canto basso e gorgogliante "
            "filtra sotto la porta sigillata."
        ),
        "exits": {"ovest": "main_street"},
        "items": ["simbolo di Dagon", "candela nera"],
    },
    "fishermans_hut": {
        "name": "Capanna del Pescatore",
        "description": (
            "Una piccola capanna che odora di pesce marcio e salsedine. Sul tavolo trovi "
            "appunti scritti in una grafia tremante — chi li ha scritti era terrorizzato. "
            "L'ultimo rigo recita: 'vengono la notte di luna nuova'."
        ),
        "exits": {"ovest": "innsmouth_dock"},
        "items": ["appunti del pescatore", "arpione"],
    },
    "marshes": {
        "name": "Le Paludi",
        "description": (
            "La nebbia avvolge ogni cosa. Il terreno cede sotto i tuoi piedi con suoni viscidi. "
            "Sagome si muovono nella bruma — troppo alte per essere umane, troppo silenziose "
            "per essere animali. Qualcosa ti osserva."
        ),
        "exits": {"sud": "main_street"},
        "items": ["pietra con incisioni"],
    },
}


@dataclass
class PlayerState:
    location: str = "innsmouth_dock"
    hp: int = 100
    sanity: int = 100
    inventory: list = field(default_factory=list)
    history: list = field(default_factory=list)  # ultimi N eventi narrati
    turn: int = 0

    def current_location(self) -> dict:
        return LOCATIONS[self.location]

    def add_history(self, event: str, max_entries: int = 8):
        self.history.append(event)
        if len(self.history) > max_entries:
            self.history = self.history[-max_entries:]

    def to_context(self) -> str:
        loc = self.current_location()
        exits = ", ".join(loc["exits"].keys())
        items_here = ", ".join(loc["items"]) if loc["items"] else "nessuno"
        inventory = ", ".join(self.inventory) if self.inventory else "niente"
        history_text = "\n".join(self.history[-4:]) if self.history else "Inizio avventura."

        return (
            f"LUOGO ATTUALE: {loc['name']}\n"
            f"DESCRIZIONE: {loc['description']}\n"
            f"USCITE DISPONIBILI: {exits}\n"
            f"OGGETTI PRESENTI: {items_here}\n"
            f"INVENTARIO GIOCATORE: {inventory}\n"
            f"HP: {self.hp}/100 | SANITÀ: {self.sanity}/100\n"
            f"TURNO: {self.turn}\n"
            f"\nEVENTI RECENTI:\n{history_text}"
        )


# Dizionario globale: user_id → PlayerState
sessions: dict[int, PlayerState] = {}


def get_session(user_id: int) -> PlayerState:
    if user_id not in sessions:
        sessions[user_id] = PlayerState()
    return sessions[user_id]


def reset_session(user_id: int) -> PlayerState:
    sessions[user_id] = PlayerState()
    return sessions[user_id]


def move_player(state: PlayerState, direction: str) -> Optional[str]:
    """Sposta il giocatore. Ritorna il nuovo luogo o None se non valido."""
    loc = state.current_location()
    if direction in loc["exits"]:
        state.location = loc["exits"][direction]
        state.turn += 1
        return state.location
    return None


def pick_up_item(state: PlayerState, item: str) -> bool:
    """Raccoglie un oggetto dal luogo corrente."""
    loc = state.current_location()
    for i, it in enumerate(loc["items"]):
        if item.lower() in it.lower():
            state.inventory.append(it)
            loc["items"].pop(i)
            state.turn += 1
            return True
    return False
