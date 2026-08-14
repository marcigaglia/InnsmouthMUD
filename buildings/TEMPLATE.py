"""
TEMPLATE.py — Usa questo file per creare un nuovo edificio esplorabile.

ISTRUZIONI:
1. Copia questo file e rinominalo (es. gilman_house.py)
2. Modifica BUILDING_ID con l'id della location esterna a cui vuoi collegarlo
3. Aggiungi le stanze nel dizionario rooms
4. Salva nella cartella buildings/
5. Il bot lo caricherà automaticamente — nient'altro da fare!

LOCATION ESTERNE DISPONIBILI (game.py):
  innsmouth_dock   — Molo di Innsmouth
  main_street      — Via Principale
  old_church       — Chiesa di Dagon  (già usata da old_church.py)
  fishermans_hut   — Capanna del Pescatore
  marshes          — Le Paludi

DIREZIONI disponibili nei exits:
  nord, sud, est, ovest, su, giu

LAYOUT CONSIGLIATO (disegnalo su carta prima):
  Decidi quante stanze vuoi e come sono collegate.
  Una stanza di ingresso (ENTRY_ROOM) e le altre accessibili da lì.
"""

from buildings.base import BaseBuilding, Room


class MioEdificio(BaseBuilding):

    # ── Dati principali ──────────────────────────────────────────
    BUILDING_ID = "fishermans_hut"   # deve corrispondere a un id in LOCATIONS (game.py)
    BUILDING_NAME = "Nome Edificio"  # appare nel pulsante 🚪 Entra
    ENTRY_ROOM = "ingresso"          # id della stanza di ingresso
    ENTRY_TEXT = "Descrizione di cosa vede il giocatore entrando."
    EXIT_TEXT = "Descrizione di cosa sente/vede uscendo."

    rooms = {

        "ingresso": Room(
            id="ingresso",
            name="Nome della Stanza",
            first_visit="Testo speciale mostrato solo alla prima visita (opzionale).",
            descriptions=[
                "Prima variante della descrizione (mostrata random).",
                "Seconda variante.",
                "Terza variante.",
            ],
            exits={
                "nord": "seconda_stanza",   # collega ad altre stanze
                # "est": "terza_stanza",
            },
            items={
                "nome oggetto": "Descrizione dell'oggetto quando viene raccolto.",
            },
            actions={
                "ascolta": ["Cosa sente il giocatore.", "Variante alternativa."],
                "esamina porta": ["Cosa trova esaminando la porta."],
            },
            sanity_penalty=0,   # sanità persa alla prima visita (0 = nessuna)
        ),

        "seconda_stanza": Room(
            id="seconda_stanza",
            name="Nome Seconda Stanza",
            descriptions=[
                "Descrizione della stanza.",
            ],
            exits={
                "sud": "ingresso",   # torna all'ingresso
            },
            items={},
            actions={},
            sanity_penalty=0,
        ),

        # Aggiungi altre stanze qui...
    }


# Istanza singleton — NON rinominare "building"
building = MioEdificio()
