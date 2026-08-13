"""
game.py — Motore narrativo classico MUD stile lovecraftiano.
Nessuna AI: testi scritti a mano, varianti random per atmosfera.
"""

import random
from dataclasses import dataclass, field
from typing import Optional

# ─────────────────────────────────────────────
# Database stanze
# ─────────────────────────────────────────────

LOCATIONS = {
    "innsmouth_dock": {
        "name": "Molo di Innsmouth",
        "descriptions": [
            "Un molo marcio si stende sul mare nerastro. L'aria sa di alghe e qualcosa di più antico. "
            "Le barche di legno scricchiolano come se qualcosa le spingesse dall'interno. "
            "Le onde non si infrangono — si ritirano, come se il mare stesse inspirando.",

            "Il legno del molo cede leggermente sotto i tuoi piedi. Qualcosa di viscido brilla tra le assi. "
            "In lontananza, oltre la nebbia, una sagoma scura emerge e scompare tra i flutti. "
            "Non è una barca.",

            "Il sale brucia gli occhi. Il molo odora di pesce marcio e di qualcosa di metallico, "
            "quasi come sangue. Una rete abbandonata si muove da sola, stirata da qualcosa sotto la superficie.",
        ],
        "exits": {"nord": "main_street", "est": "fishermans_hut"},
        "items": {
            "rete arrugginita": "Una rete da pesca arrugginita, con maglie troppo larghe per il pesce normale. Qualcosa ci è passato attraverso strappandola.",
            "lanterna spenta": "Una lanterna a olio, vuota. Sul vetro ci sono impronte di dita — troppo lunghe per essere umane.",
        },
        "actions": {
            "esamina mare": [
                "Ti avvicini al bordo. L'acqua è nera e opaca. Per un momento ti sembra di vedere occhi — molti occhi — che ti guardano dal basso. Poi scompaiono.",
                "Il mare è stranamente immobile. Nessuna creatura marina visibile. Nessun gabbiano. Solo silenzio e l'odore di qualcosa di molto vecchio.",
            ],
            "ascolta": [
                "Sotto lo scricchiolio del legno, senti un ritmo sordo provenire dall'acqua. Come un tamburo, o come un cuore.",
                "Voci? No. Solo il vento. Eppure le parole sembrano formarsi da sole nella tua testa: 'Vieni. Vieni. Vieni.'",
            ],
        },
        "first_visit": (
            "Il molo di Innsmouth ti accoglie con indifferenza. L'autobus è già sparito dietro la collina. "
            "Non c'è nessuno in vista — solo il rumore del mare e il cigolìo del legno. "
            "Un cartello sbiadito recita: INNSMOUTH — POP. 1243. Qualcuno ha cancellato il numero con la vernice rossa."
        ),
    },

    "main_street": {
        "name": "Via Principale di Innsmouth",
        "descriptions": [
            "Case abbandonate dai tetti sfondati fiancheggiano la strada. Le finestre sono sbarrate con assi, "
            "ma dietro qualcuna intravedi un bagliore verdastro. Nessun abitante in vista — "
            "eppure senti passi alle tue spalle. Ogni volta che ti giri, niente.",

            "La strada è larga ma si sente claustrofobica. Le case si inclinano verso di te. "
            "Sui marciapiedi, impronte umide che portano verso i vicoli — e non tornano indietro. "
            "L'odore del mare è ovunque, anche qui nel centro.",

            "Un gatto ti fissa dall'angolo di un edificio. Ha tre occhi. Ti fissa per troppo tempo, "
            "poi scompare in un vicolo. Da qualche finestra chiusa proviene un canto gutturale, "
            "ritmico, come una preghiera in una lingua che non dovrebbe esistere.",
        ],
        "exits": {"sud": "innsmouth_dock", "est": "old_church", "nord": "marshes"},
        "items": {
            "giornale ingiallito": "Un Innsmouth Courier del 1928. Il titolo: 'FESTIVAL DI DAGON — GRANDE SUCCESSO'. Le foto sono state strappate via.",
        },
        "actions": {
            "bussa porta": [
                "Bussi a una porta a caso. Silenzio. Poi, dall'interno, un respiro lento e umido. La porta non si apre.",
                "Nessuno risponde. Ma attraverso le assi vedi un occhio — grande, giallo, senza palpebre — che ti osserva.",
            ],
            "esamina impronte": [
                "Le impronte sono umane, ma i piedi sembrano troppo larghi, le dita troppo lunghe. Alcune terminano a metà strada, come se chi le ha lasciate fosse semplicemente sparito.",
            ],
            "ascolta": [
                "Il canto arriva dalla chiesa a est. Parole incomprensibili, ma il ritmo ipnotico ti fa venire voglia di seguirle.",
                "Passi. Sempre passi. Ma non c'è nessuno. La tua testa inizia a pulsare.",
            ],
        },
        "first_visit": (
            "La via principale di Innsmouth era probabilmente bella, una volta. "
            "Ora è un monumento al decadimento. Negozi sbarrati, insegne illeggibili, "
            "e quella sensazione costante di essere osservato da mille angoli contemporaneamente."
        ),
    },

    "old_church": {
        "name": "Antica Chiesa di Dagon",
        "descriptions": [
            "Sul portale campeggia un rilievo di una creatura metà pesce metà uomo. "
            "L'interno è buio, ma un canto basso e gorgogliante filtra sotto la porta sigillata. "
            "Il pavimento intorno alla chiesa è coperto di squame secche.",

            "La chiesa non assomiglia a nessun luogo di culto cristiano. I simboli sul muro "
            "sono angolari, ostili, come se fossero stati incisi da qualcuno che odiava la pietra. "
            "L'aria qui è più fredda di qualche grado. Senza motivo apparente.",

            "Qualcuno ha lasciato offerte sul gradino: pesci morti, conchiglie, una bambola di stracci "
            "con fili d'alghe al posto dei capelli. Il canto dall'interno si intensifica mentre ti avvicini, "
            "come se qualcosa sapesse che sei qui.",
        ],
        "exits": {"ovest": "main_street"},
        "items": {
            "simbolo di Dagon": "Una placca di metallo scuro con inciso il simbolo dell'Ordine di Dagon. Tenerla in mano ti fa sentire le dita intorpidite.",
            "candela nera": "Una candela consumata, di cera nera. Brucia ancora, anche se non c'è fiamma visibile.",
        },
        "actions": {
            "apri porta": [
                "La porta non si muove. È sigillata dall'interno. Ma senti qualcosa trascinarsi sul pavimento, avvicinarsi alla porta, e poi fermarsi. In attesa.",
                "Spingi con tutta la forza. La porta cede di un centimetro, poi viene richiusa con violenza dall'interno. Un odore nauseante di alghe e formalina ti investe.",
            ],
            "leggi simboli": [
                "Non conosci questa scrittura. Eppure alcune parole sembrano comprensibili: 'risorgere', 'profondità', 'eterno'. La tua testa pulsa.",
                "I simboli sembrano cambiare mentre li guardi. Potresti giurare che prima non c'era quella figura inginocchiata.",
            ],
            "ascolta": [
                "Il canto è in una lingua pre-umana. Riconosci solo due parole, da qualche lettura universitaria dimenticata: Ph'nglui. Wgah'nagl.",
                "Le note sono impossibili per una voce umana. Troppo basse, troppo continue. Chi canta non respira.",
            ],
        },
        "first_visit": (
            "La chiesa di Dagon è il cuore malato di Innsmouth. "
            "Qui si tengono i riti dell'Ordine — lo sai dal giornale che hai trovato. "
            "La porta è sigillata, ma qualcosa là dentro sa che sei arrivato."
        ),
        "sanity_penalty": 5,
    },

    "fishermans_hut": {
        "name": "Capanna del Pescatore",
        "descriptions": [
            "Una piccola capanna che odora di pesce marcio e salsedine. Sul tavolo trovi "
            "appunti scritti in una grafia tremante. L'ultimo rigo recita: 'vengono la notte di luna nuova'.",

            "La capanna è stata abbandonata in fretta: una sedia rovesciata, cibo ammuffito sul tavolo, "
            "una giacca ancora appesa all'uncino. In un angolo, graffiata nella parete, una figura con pinne al posto delle braccia.",

            "Le pareti della capanna sono tappezzate di mappe nautiche. Alcune zone sono cerchiate in rosso "
            "con la scritta 'NON AVVICINARSI'. Al centro di tutti i cerchi: un punto senza nome, "
            "a tre miglia dalla costa.",
        ],
        "exits": {"ovest": "innsmouth_dock"},
        "items": {
            "appunti del pescatore": "Pagine di diario scritte in preda al terrore. Parlano di creature emerse dal mare, di riti notturni, e di qualcosa chiamato 'la Trasformazione'.",
            "arpione": "Un arpione arrugginito ma ancora affilato. Potrebbe essere utile.",
        },
        "actions": {
            "leggi appunti": [
                "'Giorno 14 — Li ho visti di nuovo stanotte. Non sono più solo Marsh e i suoi. Anche il sindaco. Anche il parroco. Gli occhi... gli occhi sono cambiati.' La scrittura qui diventa illeggibile.",
                "'La Trasformazione è irreversibile. Ho sentito Zadok Allen parlarne — dice che tutti prima o poi ci passano. Dice che è una benedizione. Mentiva, lo vedevo dagli occhi.'",
            ],
            "esamina mappa": [
                "Il punto senza nome è segnato con le coordinate. Sotto, in inchiostro quasi invisibile: Y'ha-nthlei. La città sommersa.",
                "Qualcuno ha aggiunto una nota a matita: 'La marea sale ogni anno. Tra vent'anni, Innsmouth sarà sott'acqua. E loro lo vogliono.'",
            ],
            "ascolta": [
                "Solo il vento e il mare. E qualcosa che gratta sotto il pavimento, lento e paziente.",
            ],
        },
        "first_visit": (
            "La capanna sembra abbandonata da settimane, forse mesi. "
            "Ma il fuoco nel camino era acceso di recente — le ceneri sono ancora tiepide."
        ),
    },

    "marshes": {
        "name": "Le Paludi",
        "descriptions": [
            "La nebbia avvolge ogni cosa. Il terreno cede sotto i tuoi piedi con suoni viscidi. "
            "Sagome si muovono nella bruma — troppo alte per essere umane, troppo silenziose per essere animali.",

            "Le paludi odorano di decomposizione e salsedine. Bulles di gas salgono dall'acqua stagnante. "
            "In lontananza, luci basse e bluastre si muovono lentamente. Fuochi fatui? O lampade?",

            "Qualcosa si muove nell'acqua accanto a te — grande, scivoloso. "
            "Vedi solo la scia prima che scompaia nella nebbia. "
            "I tuoi piedi sono bagnati. Non ricordi di aver messo un piede in falso.",
        ],
        "exits": {"sud": "main_street"},
        "items": {
            "pietra con incisioni": "Una pietra piatta con incisioni antichissime. Le figure mostrano esseri marini che emergono dall'acqua e si mescolano con figure umane.",
        },
        "actions": {
            "segui luci": [
                "Ti addentri verso le luci. Si allontanano. Ti fermi. Si avvicinano. Decidi di non seguirle oltre.",
                "Le luci sembrano formare un cerchio. Al centro del cerchio, qualcosa di scuro emerge dall'acqua e scompare prima che tu possa vederlo bene.",
            ],
            "esamina acqua": [
                "L'acqua è nera e densa. Ci butti un sasso — non senti il tonfo. Solo silenzio.",
                "Qualcosa tocca la tua mano da sotto la superficie. Freddo, scivoloso, con tropte dita. Ti ritiri di scatto.",
            ],
            "ascolta": [
                "Un canto. Lo stesso della chiesa, ma qui viene da sotto terra — o da sotto l'acqua.",
                "Il silenzio è totale. Poi realizzi: nessun insetto. Nessuna rana. Niente. Le paludi sono morte.",
            ],
        },
        "first_visit": (
            "Le paludi di Innsmouth sono il confine tra il mondo conosciuto e qualcosa d'altro. "
            "Nessun cartello vieta l'accesso — nessuno sente il bisogno di farlo."
        ),
        "sanity_penalty": 8,
    },
}

# ─────────────────────────────────────────────
# Risposte azioni generiche
# ─────────────────────────────────────────────

GENERIC_RESPONSES = [
    "Non succede nulla di particolare. Ma la sensazione di essere osservato si intensifica.",
    "Provi, ma Innsmouth non ti offre risposte facili.",
    "Il silenzio è la sola risposta che ricevi.",
    "Qualcosa ti ferma — un istinto primordiale che ti dice di non farlo.",
    "L'azione non porta a nulla di visibile. Almeno, non ancora.",
]

MOVE_DESCRIPTIONS = {
    ("innsmouth_dock", "main_street"): "Ti allontani dal molo. L'odore del mare ti segue.",
    ("innsmouth_dock", "fishermans_hut"): "Percorri la riva fino alla capanna. Il legno del pontile cigola sotto i tuoi passi.",
    ("main_street", "innsmouth_dock"): "Torni verso il molo. L'acqua nera ti aspetta.",
    ("main_street", "old_church"): "Ti avvicini alla chiesa. Il canto si fa più forte ad ogni passo.",
    ("main_street", "marshes"): "Entri nelle paludi. La nebbia ti avvolge immediatamente.",
    ("old_church", "main_street"): "Ti allontani dalla chiesa. Il canto si affievolisce, ma non scompare dalla tua testa.",
    ("fishermans_hut", "innsmouth_dock"): "Torni al molo. Le tue scarpe lasciano impronte umide.",
    ("marshes", "main_street"): "Torni in città. L'aria delle paludi sembra seguirti.",
}


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

    def current_location(self) -> dict:
        return LOCATIONS[self.location]

    def to_context(self) -> str:
        """Compatibilità con eventuali usi futuri."""
        loc = self.current_location()
        return f"Luogo: {loc['name']} | HP: {self.hp} | Sanità: {self.sanity}"


# ─────────────────────────────────────────────
# Motore narrativo
# ─────────────────────────────────────────────

def describe_location(state: PlayerState) -> str:
    """Restituisce la descrizione della stanza corrente."""
    loc = state.current_location()
    loc_id = state.location

    if loc_id not in state.visited:
        state.visited.add(loc_id)
        return loc.get("first_visit", random.choice(loc["descriptions"]))

    return random.choice(loc["descriptions"])


def describe_move(from_loc: str, to_loc: str) -> str:
    """Testo di transizione tra due stanze."""
    key = (from_loc, to_loc)
    return MOVE_DESCRIPTIONS.get(key, "Ti sposti verso la destinazione.")


def resolve_action(state: PlayerState, action: str) -> dict:
    """
    Risolve un'azione in testo libero.
    Cerca corrispondenze nelle azioni della stanza, poi risposta generica.
    Ritorna dict con narration, sanity_change, hp_change.
    """
    loc = state.current_location()
    action_lower = action.lower().strip()

    # Cerca nelle azioni specifiche della stanza
    for keyword, responses in loc.get("actions", {}).items():
        if keyword in action_lower or any(w in action_lower for w in keyword.split()):
            return {
                "narration": random.choice(responses),
                "sanity_change": 0,
                "hp_change": 0,
            }

    # Azione generica
    return {
        "narration": random.choice(GENERIC_RESPONSES),
        "sanity_change": 0,
        "hp_change": 0,
    }


def move_player(state: PlayerState, direction: str) -> Optional[str]:
    """Sposta il giocatore. Ritorna il nuovo luogo o None."""
    loc = state.current_location()
    if direction in loc["exits"]:
        old_loc = state.location
        state.location = loc["exits"][direction]
        state.turn += 1

        # Penalità sanità per luoghi particolari
        penalty = LOCATIONS[state.location].get("sanity_penalty", 0)
        if penalty and state.location not in state.visited:
            state.sanity = max(0, state.sanity - penalty)

        return old_loc  # ritorna da dove veniva per il testo di transizione
    return None


def pick_up_item(state: PlayerState, item: str) -> Optional[str]:
    """Raccoglie un oggetto. Ritorna la descrizione o None."""
    loc = state.current_location()
    for item_name in list(loc["items"].keys()):
        if item.lower() in item_name.lower():
            description = loc["items"].pop(item_name)
            state.inventory.append(item_name)
            state.turn += 1
            return description
    return None


# ─────────────────────────────────────────────
# Sessioni
# ─────────────────────────────────────────────

sessions: dict[int, PlayerState] = {}


def get_session(user_id: int) -> PlayerState:
    if user_id not in sessions:
        sessions[user_id] = PlayerState()
    return sessions[user_id]


def reset_session(user_id: int) -> PlayerState:
    sessions[user_id] = PlayerState()
    return sessions[user_id]
