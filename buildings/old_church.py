"""
old_church.py — La Chiesa di Dagon, 5 stanze esplorabili.

Collegate alla location esterna "old_church".
Layout interno:

         [Campanile]
              |
  [Sagrestia]-[Navata]-[Altare]
              |
          [Cripta]
"""

from buildings.base import BaseBuilding, Room


class OldChurchBuilding(BaseBuilding):

    BUILDING_ID = "old_church"
    BUILDING_NAME = "Chiesa di Dagon"
    ENTRY_ROOM = "navata"
    ENTRY_TEXT = (
        "Spingi la porta con forza. Cede con un gemito profondo, come se l'edificio "
        "stesso stesse esalando l'ultimo respiro. Sei dentro."
    )
    EXIT_TEXT = (
        "Torni all'aria aperta. Il canto nella tua testa si affievolisce, "
        "ma non scompare del tutto. Non scomparirà più."
    )

    rooms = {

        "navata": Room(
            id="navata",
            name="Navata della Chiesa",
            first_visit=(
                "La navata si estende davanti a te nel buio. Panche di legno nero "
                "fiancheggiano il corridoio centrale, alcune spezzate come se qualcuno "
                "— o qualcosa — le avesse usate come armi. Sul soffitto, affreschi "
                "che non raffigurano santi: figure acquatiche in processione verso il mare. "
                "L'aria sa di salsedine, incenso e qualcosa che non riesci a identificare."
            ),
            descriptions=[
                "La navata è silenziosa. Le panche proiettano ombre lunghe. "
                "Dal fondo della chiesa, oltre l'altare, proviene un bagliore verdastro.",
                "Il pavimento è coperto di sabbia umida e squame secche. "
                "Qualcuno ha recentemente camminato qui — le impronte portano verso la cripta.",
                "Le finestre sono tappate con tela cerata. Filtra solo una luce grigia, "
                "sufficiente a vedere le incisioni sui muri: nomi, centinaia di nomi.",
            ],
            exits={"nord": "altare", "est": "sagrestia", "su": "campanile", "giu": "cripta"},
            items={
                "libro delle cerimonie": (
                    "Un libro rilegato in pelle scura, le pagine gonfie di umidità. "
                    "Contiene rituali in una lingua pre-umana, con illustrazioni che "
                    "sarebbe meglio non aver visto."
                ),
            },
            actions={
                "esamina panche": [
                    "Le panche portano incisioni: nomi di famiglie di Innsmouth — Marsh, Gilman, Waite. "
                    "Alcune sono cancellate con violenza.",
                    "Sotto una panca trovi un bottone di madreperla. Stranamente caldo al tatto.",
                ],
                "guarda soffitto": [
                    "Gli affreschi mostrano la Trasformazione in sequenza: uomini che entrano nel mare "
                    "e ne emergono come qualcos'altro. L'ultimo pannello è stato deliberatamente cancellato.",
                ],
                "ascolta": [
                    "Il canto che sentivi fuori è più chiaro qui. Proviene da sotto i tuoi piedi.",
                    "Silenzio. Poi un respiro — lento, umido, non tuo.",
                ],
            },
            sanity_penalty=5,
        ),

        "altare": Room(
            id="altare",
            name="Altare di Dagon",
            first_visit=(
                "L'altare è una lastra di pietra nera larga tre metri. Non ha croci, "
                "non ha simboli cristiani. Al centro è inciso il sigillo di Dagon — "
                "lo stesso che hai visto sul portale, ma qui è grande quanto un uomo. "
                "Attorno alla lastra, candele nere bruciano da sole. "
                "Nessuno le ha accese. Nessuno le spegnerà."
            ),
            descriptions=[
                "Le candele bruciano immobili, senza fiamma visibile. La luce che emettono "
                "è di un verde malsano che fa sembrare tutto sottomarino.",
                "Sulla lastra ci sono macchie scure. Non vuoi sapere cosa sono.",
                "Il sigillo di Dagon sembra pulsare leggermente. O forse è solo "
                "il battito del tuo cuore che proietta ombre tremanti.",
            ],
            exits={"sud": "navata"},
            items={
                "frammento del sigillo": (
                    "Un pezzo di pietra scheggiato dall'altare. Freddo come il fondo del mare, "
                    "anche dopo minuti in mano. Sul retro, coordinate in numeri romani."
                ),
            },
            actions={
                "tocca altare": [
                    "Appoggi una mano sulla pietra. Una visione fulminea: profondità oceaniche, "
                    "luci bioluminescenti, una città sommersa. Ti ritiri di scatto. -5 Sanità.",
                    "La pietra è liscia e fredda. Senti una vibrazione — come una frequenza "
                    "troppo bassa per le orecchie umane, percepita solo nel petto.",
                ],
                "esamina candele": [
                    "Le candele non hanno stoppino visibile. La cera nera scende ma non si consuma. "
                    "Bruciavano già prima che Innsmouth esistesse.",
                ],
                "ascolta": [
                    "Il canto è fortissimo qui. Proviene dall'altare stesso — dalla pietra.",
                    "Parole. Finalmente riconosci parole: Ph'nglui mglw'nafh Cthulhu R'lyeh wgah'nagl fhtagn.",
                ],
            },
            sanity_penalty=8,
        ),

        "sagrestia": Room(
            id="sagrestia",
            name="Sagrestia",
            first_visit=(
                "Una stanza piccola e disordinata, usata per preparare i riti. "
                "Armadi aperti mostrano vesti cerimoniali — non bianche, ma di un verde "
                "scuro che ricorda le alghe. Su un tavolo, strumenti rituali che non "
                "corrispondono a nessuna religione conosciuta."
            ),
            descriptions=[
                "Gli armadi sono pieni di vesti in varie misure — alcune enormi, "
                "costruite per corpi dalla forma sbagliata.",
                "Sul tavolo, un registro aperto. Le ultime voci risalgono a tre giorni fa.",
                "Odore di incenso rancido e di mare chiuso. Una finestra sigillata "
                "dà sul vicolo — dall'altra parte, un occhio ti fissa. Poi sparisce.",
            ],
            exits={"ovest": "navata"},
            items={
                "registro dei riti": (
                    "Un registro con date e nomi. L'ultimo rito: 'Luna Nuova — "
                    "Offerta alla Profondità — Partecipanti: 47'. "
                    "Quarantasette persone. In questa città fantasma."
                ),
            },
            actions={
                "esamina vesti": [
                    "Le vesti hanno cuciture strane — aperture nei posti sbagliati, "
                    "come se chi le indossa avesse arti in posizioni non umane.",
                    "Dentro una veste trovi un nome cucito: OBED MARSH. "
                    "Obed Marsh è morto nel 1878.",
                ],
                "leggi registro": [
                    "I nomi si ripetono per decenni. Gli stessi cognomi — Marsh, Gilman, Waite — "
                    "dal 1846 a oggi. Le stesse persone? No. Le stesse famiglie.",
                    "Trovi una voce diversa: 'Visitatore esterno — non iniziato — sorvegliare.' "
                    "La data è di oggi.",
                ],
                "ascolta": [
                    "Silenzio qui, quasi. Solo il registro che si muove da solo, "
                    "girandosi alla pagina sbagliata.",
                ],
            },
        ),

        "campanile": Room(
            id="campanile",
            name="Campanile",
            first_visit=(
                "Scala a chiocciola, gradini scivolosi. In cima, una campana enorme "
                "di bronzo verde. Non ha batacchio — ma suona comunque, "
                "a frequenze che senti nelle ossa più che nelle orecchie. "
                "Da quassù vedi tutta Innsmouth. E il mare. E qualcosa nel mare."
            ),
            descriptions=[
                "La campana vibra in continuazione con un suono subsonico. "
                "I piccioni che di solito abitano i campanili qui non ci sono. Non ci sono mai stati.",
                "Dal campanile vedi le paludi a nord, il molo a sud. E, oltre la linea dell'orizzonte, "
                "qualcosa che emerge e scompare — troppo grande per essere una balena.",
                "Il vento porta voci da giù. La gente di Innsmouth si muove di notte, non di giorno. "
                "Da quassù, al tramonto, le strade si riempiono.",
            ],
            exits={"giu": "navata"},
            items={
                "cannocchiale arrugginito": (
                    "Un vecchio cannocchiale da marina. Attraverso la lente incrinata "
                    "riesci a vedere più lontano — e vorresti non averlo fatto."
                ),
            },
            actions={
                "guarda mare": [
                    "Con o senza cannocchiale, vedi la stessa cosa: a tre miglia dalla costa, "
                    "l'acqua ha un colore diverso. Più scura. Come se qualcosa di enorme "
                    "stesse sotto la superficie, bloccando la luce.",
                    "Il mare si muove in modo strano in un punto preciso. Cerchi concentrici, "
                    "come se qualcosa stesse per emergere. Poi smette.",
                ],
                "tocca campana": [
                    "Appoggi una mano sulla campana. La vibrazione ti attraversa completamente. "
                    "Per un secondo vedi il fondale oceanico con chiarezza cristallina. "
                    "Poi torni a te, con le mani che tremano.",
                ],
                "ascolta": [
                    "La campana non smette mai. Ti chiedi come facciano gli abitanti "
                    "a dormire con questo rumore. Poi realizzi: forse non dormono.",
                ],
            },
            sanity_penalty=3,
        ),

        "cripta": Room(
            id="cripta",
            name="Cripta Sotterranea",
            first_visit=(
                "Scendi una scala ripida nel buio. La cripta odora di mare aperto "
                "e di qualcosa di vivo — nonostante tutto. Nicchie nelle pareti "
                "contengono non bare, ma vasche riempite d'acqua di mare. "
                "Alcune vasche si muovono. Dall'interno."
            ),
            descriptions=[
                "Le vasche gorgogliano. Non guardi cosa c'è dentro. Hai preso la decisione giusta.",
                "Sul pavimento, un canale scavato nella pietra porta acqua di mare "
                "dall'esterno. La corrente va verso il centro della stanza, "
                "verso una botola sigillata con catene.",
                "Luci bioluminescenti verdi filtrano da sotto la botola. "
                "Il canto è più forte qui di qualunque altro posto nella chiesa.",
            ],
            exits={"su": "navata"},
            items={
                "chiave della botola": (
                    "Una chiave di bronzo verde, coperta di incrostazioni marine. "
                    "Apre qualcosa. Non sei sicuro di voler sapere cosa."
                ),
            },
            actions={
                "apri botola": [
                    "Provi ad aprire la botola. Le catene tengono. Ma dall'altra parte, "
                    "qualcosa sente il tuo tentativo — e risponde con tre colpi lenti, dal basso.",
                    "La botola è sigillata dall'esterno e dall'interno. "
                    "Chi l'ha chiusa non voleva che niente uscisse. O entrasse.",
                ],
                "esamina vasche": [
                    "Ti avvicini a una vasca. L'acqua è torbida. Qualcosa si muove — "
                    "una forma pallida, lunga, che si gira lentamente verso di te. "
                    "Ti allontani prima di vedere il viso.",
                ],
                "ascolta": [
                    "Il canto viene da sotto la botola. Parole reali, in una lingua reale, "
                    "cantate da voci che un tempo erano umane.",
                    "Silenzio improvviso. Tutte le vasche smettono di muoversi contemporaneamente. "
                    "Ti stanno ascoltando.",
                ],
            },
            sanity_penalty=10,
        ),
    }


# Istanza singleton
building = OldChurchBuilding()
