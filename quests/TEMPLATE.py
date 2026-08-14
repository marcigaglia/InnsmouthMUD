"""
TEMPLATE.py — Usa questo file come punto di partenza per creare una nuova quest.

ISTRUZIONI:
1. Copia questo file e rinominalo (es. la_cripta.py)
2. Modifica la classe con i tuoi dati
3. Salva nella cartella quests/
4. Il bot la caricherà automaticamente al prossimo avvio — nient'altro da fare!

STANZE DISPONIBILI:
  innsmouth_dock   — Molo di Innsmouth
  main_street      — Via Principale
  old_church       — Chiesa di Dagon
  fishermans_hut   — Capanna del Pescatore
  marshes          — Le Paludi
"""

from quests.base import BaseQuest, QuestClue


class MiaQuest(BaseQuest):

    # ── Dati principali ──────────────────────────────────────────
    QUEST_ID = "mia_quest"             # identificatore univoco, senza spazi
    QUEST_NAME = "Il Titolo della Quest"
    FINALE_LOCATION = "innsmouth_dock" # stanza dove si attiva il finale
    sanity_penalty = 10                # sanità persa al completamento (0 = nessuna)

    # ── Indizi ───────────────────────────────────────────────────
    # Aggiungi o rimuovi QuestClue secondo le tue necessità.
    # Ogni indizio ha:
    #   id           → nome interno univoco
    #   location     → stanza dove si trova
    #   triggers     → parole chiave che lo sbloccano (lista)
    #   found_text   → testo mostrato al giocatore quando lo trova
    #   journal_entry→ riga breve per il diario /quest

    clues = [
        QuestClue(
            id="primo_indizio",
            location="fishermans_hut",
            triggers=["ascolta", "esamina", "cerca"],
            found_text=(
                "Descrizione di cosa trova il giocatore.\n\n"
                "🔍 *INDIZIO TROVATO — Titolo indizio:*\n"
                "_Testo dell'indizio in corsivo._"
            ),
            journal_entry="Breve descrizione per il diario (una riga).",
        ),
        QuestClue(
            id="secondo_indizio",
            location="marshes",
            triggers=["ascolta", "segui luci"],
            found_text=(
                "Descrizione di cosa succede.\n\n"
                "🔍 *INDIZIO TROVATO — Titolo:*\n"
                "_Contenuto dell'indizio._"
            ),
            journal_entry="Breve descrizione.",
        ),
        # Aggiungi altri QuestClue qui...
    ]

    # ── Finale ───────────────────────────────────────────────────
    # Testo mostrato quando il giocatore arriva alla FINALE_LOCATION
    # con tutti gli indizi. Usa *grassetto* e _corsivo_ per Markdown.

    FINALE_TEXT = """
🌑 *TITOLO DEL FINALE*

Descrizione del finale della quest.
Cosa scopre il giocatore? Cosa succede?

Puoi usare più paragrafi, dialoghi, descrizioni atmosferiche.

━━━━━━━━━━━━━━━━━━━━━━━
🏆 *QUEST COMPLETATA — Il Titolo della Quest*
_Una riga riassuntiva del risultato._
━━━━━━━━━━━━━━━━━━━━━━━
"""


# Istanza singleton — NON rinominare "quest", il sistema la cerca con questo nome
quest = MiaQuest()
