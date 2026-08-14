"""
game.py — Motore narrativo classico MUD stile lovecraftiano.
Generato con MUD Map Editor.
"""

import random
from dataclasses import dataclass, field
from typing import Optional

# ─────────────────────────────────────────────
# Database location esterne
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
            "rete arrugginita": "Una rete da pesca arrugginita, con maglie troppo larghe per il pesce normale. Qualcosa ci è passato attraverso strappandola.",
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
        "first_visit": "Il molo di Innsmouth ti accoglie con indifferenza. L'autobus è già sparito dietro la collina.",
    },

    "main_street": {
        "name": "Via Principale di Innsmouth",
        "descriptions": [
            "Case abbandonate dai tetti sfondati fiancheggiano la strada. Le finestre sono sbarrate con assi, ma dietro qualcuna intravedi un bagliore verdastro. Nessun abitante in vista — eppure senti passi alle tue spalle.",
            "La strada è larga ma si sente claustrofobica. Le case si inclinano verso di te. Sui marciapiedi, impronte umide che portano verso i vicoli — e non tornano indietro.",
            "Un gatto ti fissa dall'angolo di un edificio. Ha tre occhi. Ti fissa per troppo tempo, poi scompare in un vicolo.",
        ],
        "exits": {"sud": "innsmouth_dock", "est": "old_church", "nord": "marshes", "ovest": "piazza"},
        "items": {
            "giornale ingiallito": "Un Innsmouth Courier del 1928. Il titolo: 'FESTIVAL DI DAGON — GRANDE SUCCESSO'. Le foto sono state strappate via.",
        },
        "actions": {
            "ascolta": [
                "Il canto arriva dalla chiesa a est. Parole incomprensibili, ma il ritmo ipnotico ti fa venire voglia di seguirle.",
                "Passi. Sempre passi. Ma non c'è nessuno. La tua testa inizia a pulsare.",
            ],
            "bussa porta": [
                "Bussi a una porta a caso. Silenzio. Poi, dall'interno, un respiro lento e umido. La porta non si apre.",
                "Nessuno risponde. Ma attraverso le assi vedi un occhio — grande, giallo, senza palpebre — che ti osserva.",
            ],
        },
        "first_visit": "La via principale di Innsmouth era probabilmente bella, una volta.",
    },

    "old_church": {
        "name": "Antica Chiesa di Dagon",
        "descriptions": [
            "Sul portale campeggia un rilievo di una creatura metà pesce metà uomo. L'interno è buio, ma un canto basso e gorgogliante filtra sotto la porta sigillata.",
            "La chiesa non assomiglia a nessun luogo di culto cristiano. I simboli sul muro sono angolari, ostili.",
            "Qualcuno ha lasciato offerte sul gradino: pesci morti, conchiglie, una bambola di stracci con fili d'alghe al posto dei capelli.",
        ],
        "exits": {"ovest": "main_street"},
        "items": {
            "simbolo di Dagon": "Una placca di metallo scuro con inciso il simbolo dell'Ordine di Dagon. Tenerla in mano ti fa sentire le dita intorpidite.",
            "candela nera": "Una candela consumata, di cera nera. Brucia ancora, anche se non c'è fiamma visibile.",
        },
        "actions": {
            "apri porta": [
                "La porta non si muove. È sigillata dall'interno. Ma senti qualcosa trascinarsi sul pavimento, avvicinarsi alla porta, e poi fermarsi. In attesa.",
                "Spingi con tutta la forza. La porta cede di un centimetro, poi viene richiusa con violenza dall'interno.",
            ],
            "leggi simboli": [
                "Non conosci questa scrittura. Eppure alcune parole sembrano comprensibili: 'risorgere', 'profondità', 'eterno'.",
                "I simboli sembrano cambiare mentre li guardi. Potresti giurare che prima non c'era quella figura inginocchiata.",
            ],
            "ascolta": [
                "Il canto è in una lingua pre-umana. Riconosci solo due parole: Ph'nglui. Wgah'nagl.",
                "Le note sono impossibili per una voce umana. Troppo basse, troppo continue. Chi canta non respira.",
            ],
        },
        "first_visit": "La chiesa di Dagon è il cuore malato di Innsmouth.",
        "sanity_penalty": 5,
    },

    "fishermans_hut": {
        "name": "Capanna del Pescatore",
        "descriptions": [
            "Una piccola capanna che odora di pesce marcio e salsedine. Sul tavolo trovi appunti scritti in una grafia tremante. L'ultimo rigo recita: 'vengono la notte di luna nuova'.",
            "La capanna è stata abbandonata in fretta: una sedia rovesciata, cibo ammuffito sul tavolo, una giacca ancora appesa all'uncino.",
            "Le pareti della capanna sono tappezzate di mappe nautiche. Alcune zone sono cerchiate in rosso con la scritta 'NON AVVICINARSI'.",
        ],
        "exits": {"ovest": "innsmouth_dock"},
        "items": {
            "appunti del pescatore": "Pagine di diario scritte in preda al terrore. Parlano di creature emerse dal mare, di riti notturni, e di qualcosa chiamato 'la Trasformazione'.",
            "arpione": "Un arpione arrugginito ma ancora affilato. Potrebbe essere utile.",
            "mappa di innsmouth": "Una mappa disegnata a mano su carta cerata, con le strade di Innsmouth segnate con inchiostro sbiadito. Usala per orientarti.",
        },
        "actions": {
            "leggi appunti": [
                "'La Trasformazione è irreversibile. Ho sentito Zadok Allen parlarne — dice che è una benedizione. Mentiva, lo vedevo dagli occhi.'",
                "'Giorno 14 — Li ho visti di nuovo stanotte. Non sono più solo Marsh e i suoi. Gli occhi... gli occhi sono cambiati.'",
            ],
            "esamina mappa": [
                "Il punto senza nome è segnato con le coordinate. Sotto, in inchiostro quasi invisibile: Y'ha-nthlei. La città sommersa.",
            ],
            "ascolta": [
                "Solo il vento e il mare. E qualcosa che gratta sotto il pavimento, lento e paziente.",
            ],
        },
        "first_visit": "La capanna sembra abbandonata da settimane, forse mesi. Ma le ceneri nel camino sono ancora tiepide.",
    },

    "marshes": {
        "name": "Le Paludi",
        "descriptions": [
            "La nebbia avvolge ogni cosa. Il terreno cede sotto i tuoi piedi con suoni viscidi. Sagome si muovono nella bruma — troppo alte per essere umane.",
            "Le paludi odorano di decomposizione e salsedine. Bolle di gas salgono dall'acqua stagnante. In lontananza, luci basse e bluastre si muovono lentamente.",
            "Qualcosa si muove nell'acqua accanto a te — grande, scivoloso. Vedi solo la scia prima che scompaia nella nebbia.",
        ],
        "exits": {"sud": "main_street"},
        "items": {
            "pietra con incisioni": "Una pietra piatta con incisioni antichissime. Le figure mostrano esseri marini che emergono dall'acqua e si mescolano con figure umane.",
        },
        "actions": {
            "segui luci": [
                "Ti addentri verso le luci. Si allontanano. Ti fermi. Si avvicinano. Decidi di non seguirle oltre.",
                "Le luci sembrano formare un cerchio. Al centro, qualcosa di scuro emerge dall'acqua e scompare.",
            ],
            "esamina acqua": [
                "L'acqua è nera e densa. Ci butti un sasso — non senti il tonfo. Solo silenzio.",
                "Qualcosa tocca la tua mano da sotto la superficie. Freddo, scivoloso, con troppe dita. Ti ritiri di scatto.",
            ],
            "ascolta": [
                "Un canto. Lo stesso della chiesa, ma qui viene da sotto terra — o da sotto l'acqua.",
                "Il silenzio è totale. Poi realizzi: nessun insetto. Nessuna rana. Niente. Le paludi sono morte.",
            ],
        },
        "first_visit": "Le paludi di Innsmouth sono il confine tra il mondo conosciuto e qualcosa d'altro.",
        "sanity_penalty": 8,
    },

    "piazza": {
        "name": "Piazza Centrale",
        "descriptions": [
            "Una piazza lastricata di ciottoli scivolosi. Al centro, una fontana prosciugata con una statua che raffigura qualcosa che non è né umano né marino. Solo qualcosa nel mezzo.",
            "La piazza è deserta. Le finestre degli edifici circostanti sono tutte sprangate. Eppure senti la sensazione precisa di essere al centro di molti sguardi.",
            "Il vento porta un odore di salsedine anche qui, lontano dal mare. Come se il mare stesse avanzando.",
        ],
        "exits": {"est": "main_street", "nord": "gilman_hotel", "ovest": "antica_villa"},
        "items": {

        },
        "actions": {
            "esamina statua": [
                "La statua è senza nome, senza targa. La figura centrale tiene le braccia aperte verso il cielo — o verso qualcosa che viene dal cielo.",
                "Da vicino vedi che la statua non è di pietra. È di qualcosa di più scuro, quasi organico. E leggermente umida.",
            ],
            "ascolta": [
                "Dal Gilman Hotel a nord proviene musica. Vecchia, stonata, come un carillon sommerso nell'acqua.",
            ],
        },
        "first_visit": "La piazza centrale di Innsmouth. Una volta doveva essere il cuore della città.",
    },

    "gilman_hotel": {
        "name": "Gilman Hotel",
        "descriptions": [
            "L'ingresso del Gilman Hotel odora di muffa e di qualcosa di più organico. Il bancone della reception è abbandonato, ma il registro degli ospiti è aperto.",
            "Le pareti del corridoio sono coperte di carta da parati che si stacca a strisce. Sotto, le pareti sembrano umide — come se l'edificio sudasse.",
            "Un lampadario ciondola dal soffitto senza che ci sia vento. Le lampadine sono spente, ma una luce verdastra filtra da qualche parte sopra.",
        ],
        "exits": {"sud": "piazza"},
        "items": {
            "registro degli ospiti": "Un registro con nomi e date. L'ultimo ospite registrato: 'R. Olmstead, 1927'. Sotto, in una grafia diversa: 'Non è mai partito'.",
        },
        "actions": {
            "leggi registro": [
                "Le pagine sono piene di nomi. Tutti con date di arrivo, nessuno con date di partenza. Tutti dal 1846 in poi.",
                "'Camera 17 — ospite permanente.' Non c'è nome. Solo una data di arrivo: 1893.",
            ],
            "ascolta": [
                "Dal piano di sopra provengono passi. Lenti, pesanti, con un ritmo leggermente sbagliato — una gamba trascina.",
                "Silenzio totale. Poi, da dietro il bancone, qualcosa si muove.",
            ],
            "esamina bancone": [
                "Sul bancone trovi una chiave con il numero 17. È calda, come se qualcuno la tenesse in mano fino a un momento fa.",
            ],
        },
        "first_visit": "Il Gilman Hotel è il posto dove i viaggiatori di passaggio dormivano. Nessuno di loro era di passaggio davvero.",
        "sanity_penalty": 3,
    },

    "antica_villa": {
        "name": "Villa Antica",
        "descriptions": [
            "Una villa signorile ridotta a scheletro. Le finestre sbarrate, il giardino inselvatichito. Qualcuno ci viveva, una volta. Forse ci vive ancora.",
        ],
        "exits": {"est": "piazza"},
        "items": {

        },
        "actions": {

        },
        "first_visit": "Una villa decadente",
    },
}

# ─────────────────────────────────────────────
# Testi di transizione
# ─────────────────────────────────────────────

MOVE_DESCRIPTIONS = {
    ("innsmouth_dock", "main_street"): "Ti sposti verso nord.",
    ("innsmouth_dock", "fishermans_hut"): "Ti sposti verso est.",
    ("main_street", "innsmouth_dock"): "Ti sposti verso sud.",
    ("main_street", "old_church"): "Ti sposti verso est.",
    ("main_street", "marshes"): "Ti sposti verso nord.",
    ("main_street", "piazza"): "Ti sposti verso ovest.",
    ("old_church", "main_street"): "Ti sposti verso ovest.",
    ("fishermans_hut", "innsmouth_dock"): "Ti sposti verso ovest.",
    ("marshes", "main_street"): "Ti sposti verso sud.",
    ("piazza", "main_street"): "Ti sposti verso est.",
    ("piazza", "gilman_hotel"): "Ti sposti verso nord.",
    ("piazza", "antica_villa"): "Ti sposti verso ovest.",
    ("gilman_hotel", "piazza"): "Ti sposti verso sud.",
    ("antica_villa", "piazza"): "Ti sposti verso est.",
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


# ─────────────────────────────────────────────
# Motore narrativo
# ─────────────────────────────────────────────

def describe_location(state: PlayerState) -> str:
    loc = state.current_location()
    loc_id = state.location
    if loc_id not in state.visited:
        state.visited.add(loc_id)
        penalty = loc.get("sanity_penalty", 0)
        if penalty:
            state.sanity = max(0, state.sanity - penalty)
        return loc.get("first_visit", random.choice(loc["descriptions"]))
    return random.choice(loc["descriptions"])


def describe_move(from_loc: str, to_loc: str) -> str:
    return MOVE_DESCRIPTIONS.get((from_loc, to_loc), "Ti sposti verso la destinazione.")


def resolve_action(state: PlayerState, action: str) -> dict:
    loc = state.current_location()
    action_lower = action.lower().strip()
    for keyword, responses in loc.get("actions", {}).items():
        if keyword in action_lower or any(w in action_lower for w in keyword.split()):
            return {"narration": random.choice(responses), "sanity_change": 0, "hp_change": 0}
    return {"narration": random.choice(GENERIC_RESPONSES), "sanity_change": 0, "hp_change": 0}


def move_player(state: PlayerState, direction: str) -> Optional[str]:
    loc = state.current_location()
    if direction in loc["exits"]:
        old_loc = state.location
        state.location = loc["exits"][direction]
        state.turn += 1
        return old_loc
    return None


def pick_up_item(state: PlayerState, item: str) -> Optional[str]:
    loc = state.current_location()
    for item_name in list(loc["items"].keys()):
        if item.lower() in item_name.lower():
            description = loc["items"].pop(item_name)
            state.inventory.append(item_name)
            state.turn += 1
            return description
    return None


# ─────────────────────────────────────────────
# Interazioni tra oggetti (combo)
# ─────────────────────────────────────────────

ITEM_COMBOS = [
    {
        "trigger": ["accendo", "candela"],
        "required_item": "fiammiferi",
        "target_item": "candela nera",
        "missing_msg": "Con cosa vuoi accendere la candela? Non hai nulla per farlo.",
        "success_msg": (
            "Strofini un fiammifero. La candela nera prende fuoco — ma la fiamma è verde, "
            "fredda, e non fa luce nel senso normale. Un brivido ti percorre la schiena. _-5 Sanità._"
        ),
        "sanity_change": -5,
        "consume_required": False,
    },
    {
        "trigger": ["accendo", "lanterna"],
        "required_item": "fiammiferi",
        "target_item": "lanterna spenta",
        "missing_msg": "Con cosa vuoi accendere la lanterna? Non hai nulla per farlo.",
        "success_msg": "Accendi la lanterna. Una luce calda illumina l'ambiente. _+5 HP._",
        "hp_change": 5,
        "consume_required": True,
    },
    {
        "trigger": ["uso", "chiave", "botola"],
        "required_item": "chiave della botola",
        "target_item": "chiave della botola",
        "missing_msg": "Non hai nessuna chiave.",
        "success_msg": (
            "Inserisci la chiave nella serratura della botola. Gira. Le catene cedono. "
            "La botola è aperta. *Si è aperta una via verso il basso.* _-10 Sanità._"
        ),
        "sanity_change": -10,
        "consume_required": False,
        "set_flag": "botola_aperta",
    },
]


def check_item_combo(state: PlayerState, action: str) -> Optional[dict]:
    action_lower = action.lower().strip()
    for combo in ITEM_COMBOS:
        if not all(t in action_lower for t in combo["trigger"]):
            continue
        has_target = (
            any(combo["target_item"].lower() in i.lower() for i in state.inventory)
            or combo["target_item"].lower() in [k.lower() for k in state.current_location()["items"].keys()]
        )
        if not has_target:
            continue
        has_required = any(combo["required_item"].lower() in i.lower() for i in state.inventory)
        if not has_required:
            return {"result": combo["missing_msg"], "missing": True}
        state.sanity = max(0, min(100, state.sanity + combo.get("sanity_change", 0)))
        state.hp = max(0, min(100, state.hp + combo.get("hp_change", 0)))
        if "set_flag" in combo:
            state.flags.add(combo["set_flag"])
        if combo.get("consume_required", False):
            for i, inv_item in enumerate(state.inventory):
                if combo["required_item"].lower() in inv_item.lower():
                    state.inventory.pop(i)
                    break
        return {"result": combo["success_msg"], "missing": False}
    return None


# ─────────────────────────────────────────────
# Mappa ASCII
# ─────────────────────────────────────────────

def render_map(state: PlayerState) -> str:
    current_name = LOCATIONS[state.location]["name"]
    visited_count = len(state.visited)
    total = len(LOCATIONS)

    def box(loc_id):
        if loc_id not in LOCATIONS:
            return "         "
        if loc_id == state.location:
            return "[ ◉ YOU ]"
        elif loc_id in state.visited:
            return "[  ░░░  ]"
        else:
            return "[  ???  ]"

    loc_lines = []
    for loc_id in LOCATIONS:
        b = box(loc_id)
        loc_lines.append(f"  {b}  {LOCATIONS[loc_id]['name']}")

    map_art = (
        "```\n"
        "  ╔══════════════════════╗\n"
        "  ║   MAPPA              ║\n"
        "  ╚══════════════════════╝\n"
        "\n"
    )
    for line in loc_lines:
        map_art += line + "\n"
    map_art += (
        "\n"
        f"◉ = Sei qui: {current_name}\n"
        f"░ = Visitato  ? = Inesplorato\n"
        f"Luoghi visitati: {visited_count}/{total}\n"
        "```"
    )
    return map_art


def use_item(state: PlayerState, item: str) -> Optional[str]:
    item_lower = item.lower()
    found = next((i for i in state.inventory if item_lower in i.lower()), None)
    if not found:
        return None
    if "mappa" in found.lower():
        return render_map(state)
    if "lanterna" in found.lower():
        return "Scuoti la lanterna — è vuota. Ma per un secondo vedi l'ombra di qualcosa che non c'è."
    if "arpione" in found.lower():
        state.hp = min(100, state.hp + 5)
        return "Stringi l'arpione. Ti ricorda che sei ancora vivo. _+5 HP._"
    if "simbolo" in found.lower():
        state.sanity = max(0, state.sanity - 5)
        return "Fissi il simbolo di Dagon. La tua mente vacilla. _-5 Sanità._"
    if "candela" in found.lower():
        return "Tieni la candela nera. Non brucia, eppure scalda."
    if "appunti" in found.lower():
        return "Rileggi gli appunti. Una riga: '_Se li incontri, non guardare gli occhi._'"
    if "pietra" in found.lower():
        state.sanity = max(0, state.sanity - 3)
        return "Le incisioni sulla pietra sembrano muoversi. _-3 Sanità._"
    if "rete" in found.lower():
        return "La rete è strappata dall'interno verso l'esterno."
    if "giornale" in found.lower():
        return "Il giornale parla del Festival di Dagon del 1927. Le foto sono state strappate via."
    if "registro" in found.lower():
        return "Centinaia di nomi, tutti con date di arrivo. Nessuna data di partenza."
    return f"Esamini {found}, ma non sai come usarlo qui."


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
