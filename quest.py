from typing import Optional

"""
quest.py — Sistema quest: Il Segreto di Zadok Allen.

Il giocatore deve raccogliere 4 indizi sparsi per Innsmouth,
poi tornare al molo per scoprire la verità.
"""

# ─────────────────────────────────────────────
# Definizione indizi
# ─────────────────────────────────────────────

CLUES = {
    "pagina_diario": {
        "location": "fishermans_hut",
        "trigger_action": ["leggi appunti", "leggi", "appunti", "diario"],
        "found_text": (
            "Tra le pagine degli appunti del pescatore trovi una pagina scivolata via — "
            "diversa dalle altre, scritta in una calligrafia più vecchia e tremante.\n\n"
            "🔍 *INDIZIO TROVATO — La pagina nascosta:*\n"
            "_'Zadok Allen sa tutto. È vecchio come la città, ubriaco come il mare. "
            "Se vuoi sapere cosa si nasconde sotto Innsmouth, trovalo al molo al tramonto. "
            "Ma portati qualcosa da bere — parla solo con chi lo disseta.'_"
        ),
        "journal_entry": "Una pagina nascosta negli appunti del pescatore menziona Zadok Allen.",
    },
    "simbolo_chiesa": {
        "location": "old_church",
        "trigger_action": ["leggi simboli", "esamina simboli", "simboli", "portale", "rilievo", "esamina"],
        "found_text": (
            "Tra i simboli sul portale, uno è diverso dagli altri — inciso più di recente, "
            "con una mano meno sicura. Non è un simbolo di Dagon. È un nome.\n\n"
            "🔍 *INDIZIO TROVATO — Il nome inciso:*\n"
            "_ZADOK — TRADITORE — VEDRÀ IL FONDO_\n\n"
            "Qualcuno voleva che Zadok Allen tacesse. Non ci è riuscito."
        ),
        "journal_entry": "Il nome di Zadok Allen è inciso sul portale della chiesa, come una condanna.",
    },
    "voce_paludi": {
        "location": "marshes",
        "trigger_action": ["ascolta", "segui luci", "esamina acqua", "luci"],
        "found_text": (
            "Nella nebbia delle paludi, una voce — anziana, roca, quasi sommersa dall'acqua — "
            "recita qualcosa come una filastrocca:\n\n"
            "🔍 *INDIZIO TROVATO — La voce nelle paludi:*\n"
            "_'Zadok vide la Trasformazione. Zadok vide Y'ha-nthlei. "
            "Zadok bevve per dimenticare, ma il mare non dimentica mai. "
            "Torna al molo. Lui aspetta ancora.'_\n\n"
            "La voce svanisce. Non c'era nessuno."
        ),
        "journal_entry": "Una voce nelle paludi parla di Zadok Allen e di qualcosa chiamato Y'ha-nthlei.",
    },
    "giornale_articolo": {
        "location": "main_street",
        "trigger_action": ["leggi giornale", "leggi", "giornale", "esamina giornale"],
        "found_text": (
            "Nel retro del giornale, nascosto tra le inserzioni funebri, trovi un articolo "
            "quasi illeggibile per via dell'umidità:\n\n"
            "🔍 *INDIZIO TROVATO — L'articolo cancellato:*\n"
            "_'INNSMOUTH COURIER, 14 marzo 1928 — "
            "Il cittadino Zadok Allen, 96 anni, è stato avvistato ieri sera al molo "
            "in stato di agitazione. Le autorità invitano i residenti a non prestare "
            "ascolto alle sue... affermazioni. Zadok Allen non è nel pieno delle sue facoltà.'_\n\n"
            "Le autorità mentivano. Lo sai già."
        ),
        "journal_entry": "Un articolo del 1928 tentava di screditare Zadok Allen come pazzo.",
    },
}

# Finale della quest — si attiva al molo con tutti gli indizi
QUEST_FINALE = """
🌊 *IL SEGRETO DI ZADOK ALLEN*

Sei al molo. La nebbia è più densa del solito.

E poi lo vedi.

Un vecchio seduto sull'ultimo palo del molo — immobile come se aspettasse da decenni. 
Centosei anni, forse di più. Occhi gialli e umidi che ti fissano senza sorpresa.

*"Sapevo che saresti venuto,"* dice. *"Lo sanno sempre, prima o poi."*

Parla per un'ora. O forse per un giorno. Il tempo non funziona bene, vicino al mare di Innsmouth.

Ti racconta di Y'ha-nthlei — la città sommersa, a tre miglia dalla costa. 
Di come gli abitanti di Innsmouth discendano da qualcosa che non ha nome umano. 
Di come la Trasformazione sia inevitabile per chi ha il sangue di Innsmouth nelle vene.

Ti racconta dell'Ordine di Dagon. Dei riti notturni. Di cosa emerge quando la luna è nuova.

*"Io sono l'ultimo che ricorda com'era prima,"* dice alla fine. 
*"E tu sei l'unico che ha ascoltato."*

Si alza. Cammina verso il bordo del molo.

*"Il mare chiama anche me, ormai. È ora."*

Scompare nell'acqua nera senza fare rumore. Nessuna increspatura. Nessuna bolla.

Solo tu, il molo, e la certezza assoluta che quello che hai sentito è vero.
E che nessuno ti crederà mai.

━━━━━━━━━━━━━━━━━━━━━━━
🏆 *QUEST COMPLETATA*
_Il Segreto di Zadok Allen_

Hai scoperto la verità su Innsmouth.
La verità ti costerà *-20 Sanità*.
Ma alcune cose non possono essere dimenticate.
━━━━━━━━━━━━━━━━━━━━━━━
"""


# ─────────────────────────────────────────────
# Logica quest
# ─────────────────────────────────────────────

def check_clue(state, action: str) -> Optional[str]:
    """
    Controlla se l'azione attuale sblocca un indizio nella stanza corrente.
    Ritorna il testo dell'indizio se trovato, None altrimenti.
    Aggiorna state.clues_found.
    """
    action_lower = action.lower().strip()

    for clue_id, clue in CLUES.items():
        # Già trovato
        if clue_id in state.clues_found:
            continue
        # Stanza sbagliata
        if clue["location"] != state.location:
            continue
        # Controlla trigger
        for trigger in clue["trigger_action"]:
            if trigger in action_lower:
                state.clues_found.add(clue_id)
                return clue["found_text"]

    return None


def check_quest_finale(state) -> bool:
    """
    Ritorna True se il giocatore è al molo con tutti gli indizi
    e la quest non è ancora completata.
    """
    return (
        state.location == "innsmouth_dock"
        and len(state.clues_found) >= len(CLUES)
        and not state.quest_completed
    )


def quest_status(state) -> str:
    """Testo riassuntivo dello stato della quest."""
    found = len(state.clues_found)
    total = len(CLUES)

    if state.quest_completed:
        return "✅ *Quest completata:* Il Segreto di Zadok Allen"

    if found == 0:
        return f"📜 *Quest attiva:* Scopri il segreto di Zadok Allen\n_Indizi: 0/{total} — Esplora e interagisci con l'ambiente._"

    entries = []
    for clue_id, clue in CLUES.items():
        if clue_id in state.clues_found:
            entries.append(f"  ✓ {clue['journal_entry']}")
        else:
            entries.append(f"  ○ ???")

    clue_list = "\n".join(entries)
    hint = "\n_Torna al molo quando hai tutti gli indizi._" if found == total else ""
    return f"📜 *Il Segreto di Zadok Allen* — {found}/{total} indizi\n{clue_list}{hint}"
