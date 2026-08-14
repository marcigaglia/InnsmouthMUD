# ─────────────────────────────────────────────
# Generato con MUD Map Editor
# Incolla questo blocco in game.py
# sostituendo LOCATIONS e MOVE_DESCRIPTIONS
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
        "first_visit": "La capanna sembra abbandonata da settimane, forse mesi.",
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
            # nessun oggetto
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
        "first_visit": "Il Gilman Hotel è il posto dove i viaggiatori di passaggio dormivano.",
        "sanity_penalty": 3,
    },

    "antica_villa": {
        "name": "Villa Antica",
        "descriptions": [

        ],
        "exits": {"est": "piazza"},
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
    ("gilman_hotel", "piazza"): "Ti sposti verso sud.",
    ("antica_villa", "piazza"): "Ti sposti verso est.",
    ("piazza", "antica_villa"): "Ti sposti verso ovest.",
}
