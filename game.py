"""
game.py — Motore narrativo MUD.
Generato con MUD Map Editor.
"""

import random
from dataclasses import dataclass, field
from typing import Optional

# ─────────────────────────────────────────────
# Location esterne
# ─────────────────────────────────────────────

LOCATIONS = {

    "innsmouth_dock": {
        "name": "Molo di Innsmouth",
        "descriptions": [
            "Un molo marcio si stende sul mare nerastro. L'aria sa di alghe e qualcosa di più antico. Le barche di legno scricchiolano come se qualcosa le spingesse dall'interno.",
            "Il legno del molo cede leggermente sotto i tuoi piedi. Qualcosa di viscido brilla tra le assi. In lontananza, oltre la nebbia, una sagoma scura emerge e scompare tra i flutti. Non è una barca.",
            "Il sale brucia gli occhi. Il molo odora di pesce marcio e di qualcosa di metallico, quasi come sangue. Una rete abbandonata si muove da sola.",
        ],
        "exits": {"nord": "main_street", "est": "fishermans_hut"},
        "items": {
            "rete arrugginita": "Una rete da pesca arrugginita, con maglie troppo larghe per il pesce normale.",
            "lanterna spenta": "Una lanterna a olio, vuota. Sul vetro ci sono impronte di dita — troppo lunghe per essere umane.",
        },
        "actions": {
            "esamina mare": [
                "Ti avvicini al bordo. L'acqua è nera e opaca. Per un momento ti sembra di vedere occhi che ti guardano dal basso.",
                "Il mare è stranamente immobile. Solo silenzio e l'odore di qualcosa di molto vecchio.",
            ],
            "ascolta": [
                "Sotto lo scricchiolio del legno, senti un ritmo sordo provenire dall'acqua. Come un tamburo, o come un cuore.",
                "Voci? No. Solo il vento. Eppure le parole sembrano formarsi da sole nella tua testa: 'Vieni. Vieni.'",
            ],
        },
        "first_visit": "Il molo di Innsmouth ti accoglie con indifferenza. L'autobus è già sparito. Un cartello sbiadito recita: INNSMOUTH — POP. 1243. Qualcuno ha cancellato il numero con la vernice rossa.",
    },

    "main_street": {
        "name": "Via Principale",
        "descriptions": [
            "Case abbandonate dai tetti sfondati fiancheggiano la strada. Le finestre sono sbarrate con assi, ma dietro qualcuna intravedi un bagliore verdastro.",
            "La strada è larga ma si sente claustrofobica. Sui marciapiedi, impronte umide che portano verso i vicoli — e non tornano indietro.",
            "Un gatto ti fissa dall'angolo di un edificio. Ha tre occhi.",
        ],
        "exits": {"sud": "innsmouth_dock", "est": "old_church", "nord": "marshes", "ovest": "piazza"},
        "items": {
            "giornale ingiallito": "Un Innsmouth Courier del 1928. 'FESTIVAL DI DAGON — GRANDE SUCCESSO'. Le foto sono state strappate via.",
        },
        "actions": {
            "ascolta": [
                "Il canto arriva dalla chiesa a est. Parole incomprensibili, ma il ritmo ipnotico ti fa venire voglia di seguirle.",
                "Passi. Sempre passi. Ma non c'è nessuno.",
            ],
        },
        "first_visit": "La via principale di Innsmouth era probabilmente bella, una volta. Ora è un monumento al decadimento.",
    },

    "old_church": {
        "name": "Chiesa di Dagon",
        "descriptions": [
            "Sul portale campeggia un rilievo di una creatura metà pesce metà uomo. Un canto basso e gorgogliante filtra sotto la porta sigillata.",
            "La chiesa non assomiglia a nessun luogo di culto cristiano. I simboli sul muro sono angolari, ostili.",
            "Qualcuno ha lasciato offerte sul gradino: pesci morti, conchiglie, una bambola di stracci con fili d'alghe al posto dei capelli.",
        ],
        "exits": {"ovest": "main_street"},
        "items": {
            "simbolo di Dagon": "Una placca di metallo scuro con inciso il simbolo dell'Ordine di Dagon.",
            "candela nera": "Una candela consumata, di cera nera. Brucia ancora, anche se non c'è fiamma visibile.",
        },
        "actions": {
            "ascolta": [
                "Il canto è in una lingua pre-umana.",
                "Le note sono impossibili per una voce umana. Troppo basse, troppo continue. Chi canta non respira.",
            ],
        },
        "first_visit": "La chiesa di Dagon è il cuore malato di Innsmouth. La porta è sigillata, ma qualcosa là dentro sa che sei arrivato.",
        "sanity_penalty": 5,
    },

    "fishermans_hut": {
        "name": "Capanna del Pescatore",
        "descriptions": [
            "Una piccola capanna che odora di pesce marcio e salsedine. L'ultimo rigo degli appunti recita: 'vengono la notte di luna nuova'.",
            "La capanna è stata abbandonata in fretta: una sedia rovesciata, cibo ammuffito sul tavolo.",
            "Le pareti sono tappezzate di mappe nautiche. Alcune zone cerchiate in rosso: 'NON AVVICINARSI'.",
        ],
        "exits": {"ovest": "innsmouth_dock"},
        "items": {
            "appunti del pescatore": "Pagine di diario scritte in preda al terrore. Parlano di 'la Trasformazione'.",
            "arpione": "Un arpione arrugginito ma ancora affilato.",
            "mappa di innsmouth": "Una mappa disegnata a mano su carta cerata. Usala per orientarti.",
        },
        "actions": {
            "leggi appunti": [
                "'La Trasformazione è irreversibile. Ho sentito Zadok Allen parlarne — dice che è una benedizione. Mentiva.'",
            ],
        },
        "first_visit": "La capanna sembra abbandonata da settimane, forse mesi. Ma le ceneri nel camino sono ancora tiepide.",
    },

    "marshes": {
        "name": "Le Paludi",
        "descriptions": [
            "La nebbia avvolge ogni cosa. Il terreno cede sotto i tuoi piedi con suoni viscidi. Sagome si muovono nella bruma.",
            "Le paludi odorano di decomposizione e salsedine. Luci basse e bluastre si muovono in lontananza.",
            "Qualcosa si muove nell'acqua accanto a te — grande, scivoloso. Vedi solo la scia.",
        ],
        "exits": {"sud": "main_street"},
        "items": {
            "pietra con incisioni": "Una pietra piatta con incisioni antichissime. Figure di esseri marini che si mescolano con figure umane.",
        },
        "actions": {
            "ascolta": [
                "Un canto. Lo stesso della chiesa, ma qui viene da sotto terra.",
                "Il silenzio è totale. Nessun insetto. Nessuna rana. Le paludi sono morte.",
            ],
            "segui luci": [
                "Ti addentri verso le luci. Si allontanano. Ti fermi. Si avvicinano. Decidi di non seguirle oltre.",
            ],
        },
        "first_visit": "Le paludi di Innsmouth sono il confine tra il mondo conosciuto e qualcosa d'altro.",
        "sanity_penalty": 8,
    },

    "piazza": {
        "name": "Piazza",
        "descriptions": [

        ],
        "exits": {"est": "main_street", "nord": "gilman_hotel"},
        "items": {
            # nessun oggetto
        },
        "actions": {
            # nessuna azione
        },
    },

    "gilman_hotel": {
        "name": "Gilman Hotel",
        "descriptions": [

        ],
        "exits": {"sud": "piazza"},
        "items": {
            # nessun oggetto
        },
        "actions": {
            # nessuna azione
        },
    },
}

# ─────────────────────────────────────────────
# Testi di transizione
# ─────────────────────────────────────────────

MOVE_DESCRIPTIONS = {
    ("innsmouth_dock", "main_street"): "Ti sposti verso nord.",
    ("main_street", "innsmouth_dock"): "Ti sposti verso sud.",
    ("innsmouth_dock", "fishermans_hut"): "Ti sposti verso est.",
    ("fishermans_hut", "innsmouth_dock"): "Ti sposti verso ovest.",
    ("main_street", "old_church"): "Ti sposti verso est.",
    ("old_church", "main_street"): "Ti sposti verso ovest.",
    ("main_street", "marshes"): "Ti sposti verso nord.",
    ("marshes", "main_street"): "Ti sposti verso sud.",
    ("piazza", "main_street"): "Ti sposti verso est.",
    ("main_street", "piazza"): "Ti sposti verso ovest.",
    ("piazza", "gilman_hotel"): "Ti sposti verso nord.",
    ("gilman_hotel", "piazza"): "Ti sposti verso sud.",
}

# ─────────────────────────────────────────────
# Risposte generiche
# ─────────────────────────────────────────────

GENERIC_RESPONSES = [
    "Non succede nulla di particolare. Ma la sensazione di essere osservato si intensifica.",
    "Provi, ma Innsmouth non ti offre risposte facili.",
    "Il silenzio è la sola risposta che ricevi.",
    "Qualcosa ti ferma — un istinto primordiale che ti dice di non farlo.",
    "L'azione non porta a nulla di visibile. Almeno, non ancora.",
]

# ─────────────────────────────────────────────
# Stato giocatore
# ─────────────────────────────────────────────

@dataclass
class PlayerState:
    location: str = "innsmouth_dock"
    hp: int = 100
    sanity: int = 100
    inventory: list = field(default_factory=list)
    visited: set = field(default_factory=set)
    turn: int = 0
    quest_data: dict = field(default_factory=dict)
    flags: set = field(default_factory=set)
    current_building: Optional[str] = None
    current_room: Optional[str] = None
    building_data: dict = field(default_factory=dict)

    def current_location(self) -> dict:
        return LOCATIONS[self.location]

    def to_context(self) -> str:
        loc = self.current_location()
        return f"Luogo: {loc['name']} | HP: {self.hp} | Sanità: {self.sanity}"
