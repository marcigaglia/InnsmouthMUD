"""
base.py — Classe base per tutte le quest.

Per creare una nuova quest, copia il file TEMPLATE.py,
rinominalo e segui le istruzioni al suo interno.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class QuestClue:
    """Un singolo indizio della quest."""
    id: str
    location: str
    triggers: list[str]
    found_text: str
    journal_entry: str


class BaseQuest:
    """
    Classe base da cui ereditano tutte le quest.

    Ogni quest deve definire:
      QUEST_ID        : str, identificatore univoco
      QUEST_NAME      : str, nome mostrato al giocatore
      FINALE_TEXT     : str, testo del finale
      FINALE_LOCATION : str, stanza dove si attiva il finale
      clues           : list[QuestClue]
      sanity_penalty  : int, penalità sanità al completamento
    """

    QUEST_ID = "base"
    QUEST_NAME = "Quest senza nome"
    FINALE_TEXT = ""
    FINALE_LOCATION = "innsmouth_dock"
    sanity_penalty = 0
    clues: list[QuestClue] = []

    def _found_key(self):
        return f"{self.QUEST_ID}_found"

    def _completed_key(self):
        return f"{self.QUEST_ID}_completed"

    def check_clue(self, state, action: str) -> Optional[str]:
        """
        Controlla se l'azione sblocca un indizio nella stanza corrente.
        Ritorna il testo dell'indizio o None.
        """
        found_key = self._found_key()
        if found_key not in state.quest_data:
            state.quest_data[found_key] = set()

        action_lower = action.lower().strip()

        for clue in self.clues:
            if clue.id in state.quest_data[found_key]:
                continue
            if clue.location != state.location:
                continue
            if any(t in action_lower for t in clue.triggers):
                state.quest_data[found_key].add(clue.id)
                return clue.found_text

        return None

    def is_complete(self, state) -> bool:
        """Tutti gli indizi trovati."""
        found = state.quest_data.get(self._found_key(), set())
        return len(found) >= len(self.clues)

    def is_finale_triggered(self, state) -> bool:
        """Finale attivabile: indizi completi + stanza giusta + non ancora completata."""
        already_done = state.quest_data.get(self._completed_key(), False)
        return (
            self.is_complete(state)
            and state.location == self.FINALE_LOCATION
            and not already_done
        )

    def complete(self, state) -> str:
        """Segna la quest come completata e applica effetti."""
        state.quest_data[self._completed_key()] = True
        state.sanity = max(0, state.sanity - self.sanity_penalty)
        return self.FINALE_TEXT

    def status(self, state) -> str:
        """Testo riassuntivo per /quest."""
        if state.quest_data.get(self._completed_key(), False):
            return f"✅ *{self.QUEST_NAME}* — Completata"

        found = state.quest_data.get(self._found_key(), set())
        total = len(self.clues)
        n = len(found)

        lines = [f"📜 *{self.QUEST_NAME}* — {n}/{total} indizi\n"]
        for clue in self.clues:
            if clue.id in found:
                lines.append(f"  ✓ {clue.journal_entry}")
            else:
                lines.append(f"  ○ ???")

        if n == total:
            lines.append(f"\n_Torna a: {LOCATIONS_NAMES.get(self.FINALE_LOCATION, self.FINALE_LOCATION)}_")

        return "\n".join(lines)


# Nomi leggibili delle stanze
LOCATIONS_NAMES = {
    "innsmouth_dock": "Molo di Innsmouth",
    "main_street": "Via Principale",
    "old_church": "Chiesa di Dagon",
    "fishermans_hut": "Capanna del Pescatore",
    "marshes": "Le Paludi",
}
