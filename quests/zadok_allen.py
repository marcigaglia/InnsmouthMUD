"""
zadok_allen.py — Quest: Il Segreto di Zadok Allen.

Il giocatore raccoglie 4 indizi sparsi per Innsmouth,
poi torna al molo per scoprire la verità.
"""

from quests.base import BaseQuest, QuestClue


class ZadokAllenQuest(BaseQuest):

    QUEST_ID = "zadok_allen"
    QUEST_NAME = "Il Segreto di Zadok Allen"
    FINALE_LOCATION = "innsmouth_dock"
    sanity_penalty = 20

    clues = [
        QuestClue(
            id="pagina_diario",
            location="fishermans_hut",
            triggers=["leggi appunti", "leggi", "appunti", "diario", "guarda appunti", "usa appunti"],
            found_text=(
                "Tra le pagine degli appunti del pescatore trovi una pagina scivolata via — "
                "diversa dalle altre, scritta in una calligrafia più vecchia e tremante.\n\n"
                "🔍 *INDIZIO TROVATO — La pagina nascosta:*\n"
                "_'Zadok Allen sa tutto. È vecchio come la città, ubriaco come il mare. "
                "Se vuoi sapere cosa si nasconde sotto Innsmouth, trovalo al molo al tramonto. "
                "Ma portati qualcosa da bere — parla solo con chi lo disseta.'_"
            ),
            journal_entry="Una pagina nascosta menziona Zadok Allen al molo.",
        ),
        QuestClue(
            id="simbolo_chiesa",
            location="old_church",
            triggers=["leggi simboli", "esamina simboli", "simboli", "portale", "rilievo", "esamina"],
            found_text=(
                "Tra i simboli sul portale, uno è diverso dagli altri — inciso più di recente. "
                "Non è un simbolo di Dagon. È un nome.\n\n"
                "🔍 *INDIZIO TROVATO — Il nome inciso:*\n"
                "_ZADOK — TRADITORE — VEDRÀ IL FONDO_\n\n"
                "Qualcuno voleva che Zadok Allen tacesse."
            ),
            journal_entry="Il nome di Zadok Allen è inciso sul portale come una condanna.",
        ),
        QuestClue(
            id="voce_paludi",
            location="marshes",
            triggers=["ascolta", "segui luci", "esamina acqua", "luci"],
            found_text=(
                "Nella nebbia delle paludi, una voce anziana e roca recita:\n\n"
                "🔍 *INDIZIO TROVATO — La voce nelle paludi:*\n"
                "_'Zadok vide la Trasformazione. Zadok vide Y'ha-nthlei. "
                "Torna al molo. Lui aspetta ancora.'_\n\n"
                "La voce svanisce. Non c'era nessuno."
            ),
            journal_entry="Una voce nelle paludi parla di Zadok e di Y'ha-nthlei.",
        ),
        QuestClue(
            id="giornale_articolo",
            location="main_street",
            triggers=["leggi giornale", "leggi", "giornale", "esamina giornale", "guarda giornale"],
            found_text=(
                "Nel retro del giornale, un articolo quasi illeggibile:\n\n"
                "🔍 *INDIZIO TROVATO — L'articolo cancellato:*\n"
                "_'Innsmouth Courier, 14 marzo 1928 — Zadok Allen, 96 anni, avvistato al molo "
                "in stato di agitazione. Le autorità invitano i residenti a non prestare ascolto "
                "alle sue affermazioni. Non è nel pieno delle sue facoltà.'_\n\n"
                "Le autorità mentivano."
            ),
            journal_entry="Un articolo del 1928 tentava di screditare Zadok Allen.",
        ),
    ]

    FINALE_TEXT = """
🌊 *IL SEGRETO DI ZADOK ALLEN*

Sei al molo. La nebbia è più densa del solito.

E poi lo vedi.

Un vecchio seduto sull'ultimo palo del molo — immobile come se aspettasse da decenni.
Centosei anni, forse di più. Occhi gialli e umidi che ti fissano senza sorpresa.

*"Sapevo che saresti venuto,"* dice. *"Lo sanno sempre, prima o poi."*

Ti racconta di Y'ha-nthlei — la città sommersa, a tre miglia dalla costa.
Di come gli abitanti di Innsmouth discendano da qualcosa che non ha nome umano.
Di come la Trasformazione sia inevitabile per chi ha il sangue di Innsmouth nelle vene.

*"Io sono l'ultimo che ricorda com'era prima,"* dice alla fine.
*"E tu sei l'unico che ha ascoltato."*

Si alza. Cammina verso il bordo del molo.

*"Il mare chiama anche me, ormai. È ora."*

Scompare nell'acqua nera senza fare rumore. Nessuna increspatura. Nessuna bolla.

Solo tu, il molo, e la certezza che quello che hai sentito è vero.
E che nessuno ti crederà mai.

━━━━━━━━━━━━━━━━━━━━━━━
🏆 *QUEST COMPLETATA — Il Segreto di Zadok Allen*
_Hai scoperto la verità su Innsmouth. \\-20 Sanità._
━━━━━━━━━━━━━━━━━━━━━━━
"""


# Istanza singleton usata dal sistema
quest = ZadokAllenQuest()
