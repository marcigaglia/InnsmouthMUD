"""
base.py — Classe base per gli edifici esplorabili.

Un edificio è collegato a una location esterna (es. "old_church")
e contiene un insieme di stanze interne navigabili.
Il giocatore entra/esce tramite pulsante. La mappa esterna
mostra solo la location, non le stanze interne.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Room:
    """Una stanza all'interno di un edificio."""
    id: str                          # identificatore univoco nella stanza
    name: str                        # nome mostrato al giocatore
    descriptions: list[str]          # varianti random della descrizione
    exits: dict[str, str]            # {"nord": "room_id", ...}
    items: dict[str, str] = field(default_factory=dict)   # {nome: descrizione}
    actions: dict[str, list[str]] = field(default_factory=dict)  # {trigger: [risposte]}
    first_visit: Optional[str] = None   # testo speciale alla prima visita
    sanity_penalty: int = 0             # sanità persa alla prima visita


class BaseBuilding:
    """
    Classe base da cui ereditano tutti gli edifici.

    Ogni edificio deve definire:
      BUILDING_ID       : str — deve corrispondere all'id della location esterna
      BUILDING_NAME     : str — nome mostrato nel pulsante Entra
      ENTRY_ROOM        : str — id della stanza di ingresso
      ENTRY_TEXT        : str — testo mostrato entrando nell'edificio
      EXIT_TEXT         : str — testo mostrato uscendo
      rooms             : dict[str, Room] — tutte le stanze
    """

    BUILDING_ID = "building"
    BUILDING_NAME = "Edificio"
    ENTRY_ROOM = "entrance"
    ENTRY_TEXT = "Entri nell'edificio."
    EXIT_TEXT = "Esci all'aperto."
    rooms: dict[str, Room] = {}
    # Uscite sbloccate da flag: {room_id: {flag: {direzione: room_target}}}
    DYNAMIC_EXITS: dict = {}

    def get_room(self, room_id: str) -> Optional[Room]:
        return self.rooms.get(room_id)

    def describe_room(self, state, room_id: str) -> str:
        """Descrizione della stanza, con testo speciale alla prima visita."""
        import random
        room = self.get_room(room_id)
        if not room:
            return "Buio totale."

        visited_key = f"{self.BUILDING_ID}_visited_{room_id}"
        if not hasattr(state, "building_data"):
            state.building_data = {}

        if visited_key not in state.building_data:
            state.building_data[visited_key] = True
            # Applica penalità sanità
            if room.sanity_penalty:
                state.sanity = max(0, state.sanity - room.sanity_penalty)
            if room.first_visit:
                return room.first_visit

        return random.choice(room.descriptions)

    def resolve_action(self, room_id: str, action: str) -> Optional[str]:
        """Cerca l'azione nelle azioni specifiche della stanza."""
        import random
        room = self.get_room(room_id)
        if not room:
            return None
        action_lower = action.lower().strip()
        for keyword, responses in room.actions.items():
            if any(w in action_lower for w in keyword.split()):
                return random.choice(responses)
        return None

    def get_exits(self, room_id: str, state) -> dict:
        """
        Ritorna le uscite disponibili per la stanza, includendo
        quelle dinamiche sbloccate dai flag del giocatore.
        """
        room = self.get_room(room_id)
        if not room:
            return {}
        exits = dict(room.exits)

        # Uscite dinamiche: definite in DYNAMIC_EXITS come
        # {room_id: {flag_required: {direction: target_room}}}
        for flag, routes in self.DYNAMIC_EXITS.get(room_id, {}).items():
            if flag in state.flags:
                exits.update(routes)

        return exits

    def move(self, room_id: str, direction: str, state=None) -> Optional[str]:
        """Sposta il giocatore. Supporta uscite dinamiche se state è fornito."""
        if state:
            exits = self.get_exits(room_id, state)
        else:
            room = self.get_room(room_id)
            exits = room.exits if room else {}
        return exits.get(direction)

    def pick_item(self, state, room_id: str, item_name: str) -> Optional[str]:
        """Raccoglie un oggetto dalla stanza. Ritorna la descrizione o None."""
        room = self.get_room(room_id)
        if not room:
            return None
        for name in list(room.items.keys()):
            if item_name.lower() in name.lower():
                desc = room.items.pop(name)
                state.inventory.append(name)
                return desc
        return None
