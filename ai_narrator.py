"""
ai_narrator.py — Interfaccia con l'API Anthropic.
Claude interpreta il ruolo di narratore lovecraftiano.
"""

import anthropic

client = anthropic.Anthropic()  # legge ANTHROPIC_API_KEY dall'ambiente

SYSTEM_PROMPT = """Sei il narratore di un gioco MUD in stile horror lovecraftiano ambientato a Innsmouth.
Il tuo compito è rispondere alle azioni del giocatore con descrizioni vivide, atmosferiche e inquietanti.

REGOLE NARRATIVE:
- Scrivi in italiano, in seconda persona ("Tu vedi...", "Senti...")
- Mantieni un tono oscuro, opprimente, pieno di presagi
- Le descrizioni devono essere evocative ma concise (2-4 frasi)
- Inserisci dettagli sensoriali: odori, suoni, sensazioni fisiche
- Quando il giocatore si avvicina a qualcosa di innominabile, riduci la sanità (indicalo nel JSON)
- Non svelare troppo — il mistero è la tensione principale
- Concludi sempre con qualcosa che spinge il giocatore ad agire

FORMATO RISPOSTA — rispondi SOLO con JSON valido:
{
  "narration": "testo narrativo per il giocatore",
  "sanity_change": 0,
  "hp_change": 0,
  "note": "eventuale nota interna opzionale"
}

sanity_change e hp_change sono interi negativi (danno) o positivi (recupero).
Il danno alla sanità deve essere usato con parsimonia (max -10 per azione).
"""


def narrate(action: str, context: str) -> dict:
    """
    Chiama Claude per narrare l'azione del giocatore.
    Ritorna un dizionario con narration, sanity_change, hp_change.
    """
    user_message = f"""STATO DEL GIOCO:
{context}

AZIONE DEL GIOCATORE: {action}

Descrivi cosa succede in risposta a questa azione."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = message.content[0].text.strip()

    # Pulizia del JSON (rimuove eventuali backtick)
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    import json
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback se Claude non rispetta il formato
        result = {
            "narration": raw,
            "sanity_change": 0,
            "hp_change": 0,
        }

    return result


def narrate_arrival(location_name: str, context: str) -> str:
    """Narra l'arrivo in un nuovo luogo."""
    return narrate(f"Il giocatore arriva a: {location_name}", context).get(
        "narration", f"Sei arrivato a {location_name}."
    )
