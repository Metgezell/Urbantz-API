# Anthropic Claude API Setup

## Probleem Opgelost ✅

De "Scan met AI" knop gebruikt nu de Anthropic Claude API voor intelligente document analyse!

## Wat is er veranderd?

Alle Python servers zijn geüpdatet om de Anthropic Claude API te gebruiken:
- `start-server-fast.py` (poort 8080)
- `start-server-with-reload.py` (poort 8080)
- `start-server.py` (poort 8000)

De servers proberen nu eerst de Anthropic Claude API te gebruiken, en vallen terug op pattern matching als de API key niet beschikbaar is.

## Setup Instructies

### Stap 0: Installeer Python dependencies

Installeer de benodigde Python packages:

```bash
pip install -r requirements.txt
```

Of installeer handmatig:

```bash
pip install python-dotenv
```

### Stap 1: Maak een `.env` bestand

Kopieer het `env.example` bestand naar `.env`:

```bash
copy env.example .env
```

Of maak handmatig een `.env` bestand in de root directory met de volgende inhoud:

```env
# Urbantz API Configuration
URBANTZ_BASE_URL=https://api.urbantz.com
URBANTZ_API_KEY=your_actual_api_key_here

# Anthropic Claude API Key - VERVANG MET JE ECHTE API KEY
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### Stap 2: Verkrijg een Anthropic API Key

1. Ga naar [Anthropic Console](https://console.anthropic.com/)
2. Maak een account aan of log in
3. Ga naar "API Keys"
4. Klik op "Create Key"
5. Kopieer de API key (begint met `sk-ant-api03-...`)

### Stap 3: Voeg je API Key toe aan `.env`

Open het `.env` bestand en vervang `your_anthropic_api_key_here` met je echte API key:

```env
ANTHROPIC_API_KEY=sk-ant-api03-jouw-echte-key-hier
```

### Stap 4: Herstart de server

Stop de server (Ctrl+C) en start opnieuw:

#### Met PowerShell script (aanbevolen):
```powershell
.\start-urbantz-dev.ps1
```

#### Met Python direct:
```bash
python start-server-fast.py
```

#### Met Batch file:
```bash
start-urbantz-fast.bat
```

### Stap 5: Test de setup

**Optie A: Gebruik het test script (aanbevolen)**

```bash
python test-anthropic-setup.py
```

Dit test script controleert:
- ✅ Of python-dotenv is geïnstalleerd
- ✅ Of de ANTHROPIC_API_KEY correct is ingesteld
- ✅ Of de API verbinding werkt
- ✅ Of delivery extractie werkt

**Optie B: Test via de browser**

1. Start de server
2. Open je browser op `http://localhost:8080`
3. Plak een test email of document tekst in het tekstveld
4. Klik op "Scan met AI"
5. Kijk in de server console - je zou moeten zien:
   ```
   🤖 Using Anthropic Claude API for AI analysis...
   ✅ Claude API extracted X delivery(ies)
   ```

## Troubleshooting

### De API wordt nog steeds niet gebruikt

**Check de console output:**

Als je dit ziet:
```
⚠️ ANTHROPIC_API_KEY not found, using pattern matching
```

Dan is de `.env` file niet correct geladen. Controleer:
1. Het `.env` bestand bestaat in de root directory
2. De API key is correct ingevuld (geen quotes, spaties, etc.)
3. De server is herstart na het aanmaken van `.env`

### API Error

Als je dit ziet:
```
⚠️ Claude API error: [error message]
   Falling back to pattern matching...
```

Dan is er een probleem met de API aanroep:
- **401 Unauthorized**: Je API key is ongeldig
- **429 Too Many Requests**: Je hebt je rate limit bereikt
- **500 Server Error**: Anthropic API heeft een probleem

### Windows PowerShell Environment Variables

PowerShell laadt automatisch `.env` bestanden via de `python-dotenv` package. Als dat niet werkt, installeer het:

```powershell
pip install python-dotenv
```

## Verificatie

Om te controleren of de `.env` variabelen correct zijn geladen, voer uit:

```python
import os
from dotenv import load_dotenv

load_dotenv()
print(f"API Key aanwezig: {bool(os.environ.get('ANTHROPIC_API_KEY'))}")
```

## Kosten

De Anthropic Claude API is een betaalde service:
- Claude 3.5 Sonnet: ~$3 per miljoen tokens input, ~$15 per miljoen tokens output
- Voor deze use case: ~$0.01-0.05 per document analyse

Zie [Anthropic Pricing](https://www.anthropic.com/pricing) voor actuele prijzen.

## Fallback Gedrag

Als de Anthropic API niet beschikbaar is:
- De server valt automatisch terug op intelligente pattern matching
- Je applicatie blijft werken (zij het met minder nauwkeurige extractie)
- Er wordt een waarschuwing getoond in de console

Dit zorgt ervoor dat je applicatie altijd blijft werken, zelfs zonder API key!

