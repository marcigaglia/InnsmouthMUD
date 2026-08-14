# 🌊 Innsmouth MUD Bot

Un gioco MUD horror lovecraftiano su Telegram, narrato da Claude AI.

## Deploy su Railway

### 1. Prerequisiti
- Account [GitHub](https://github.com)
- Account [Railway](https://railway.app) (gratuito)
- Token bot Telegram da [@BotFather](https://t.me/BotFather)
- API key Anthropic da [console.anthropic.com](https://console.anthropic.com)

### 2. Carica su GitHub
```bash
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/TUO_USERNAME/mud-bot.git
git push -u origin main
```

### 3. Deploy su Railway
1. Vai su [railway.app](https://railway.app) → **New Project**
2. Scegli **Deploy from GitHub repo**
3. Seleziona il repository `mud-bot`
4. Railway rileva automaticamente il `Procfile`

### 4. Variabili d'ambiente
Nel pannello Railway → **Variables**, aggiungi:

| Variabile | Valore |
|---|---|
| `TELEGRAM_TOKEN` | Il token di BotFather |
| `ANTHROPIC_API_KEY` | La tua chiave Anthropic |

### 5. Avvia
Railway avvierà automaticamente `python bot.py`. Il bot è online!

## Comandi del bot
| Comando | Descrizione |
|---|---|
| `/start` | Inizia l'avventura |
| `/look` | Osserva l'ambiente |
| `/inventory` | Controlla lo zaino |
| `/status` | HP e Sanità |
| `/help` | Aiuto |

Puoi anche scrivere liberamente qualsiasi azione in italiano.
