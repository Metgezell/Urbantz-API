# Urbantz API Integration

Deze directory bevat lokale Urbantz API documentatie en integratie voor betere code-suggesties.

## Lokale Documentatie

- **`index.html`** - Hoofdpagina van de Urbantz API documentatie
- **`openapi.yaml`** - OpenAPI specificatie (placeholder - download de echte versie via browser)
- **`reference.md`** - Korte referentie voor developers

## Setup

### 1. Environment Variables

Kopieer `.env.example` naar `.env` en vul je API key in:

```bash
cp .env.example .env
```

Vul in `.env` je echte Urbantz API key in:
```
URBANTZ_API_KEY=your_actual_api_key_here
```

### 2. Dependencies Installeren

```bash
npm install ts-node dotenv
```

### 3. Dry-Run Testen

```bash
npm run urbantz:dry-run
```

## TypeScript Client

De `announceTask()` functie in `src/clients/urbantz.ts` biedt:

- **Authenticatie**: API key via `x-api-key` header
- **Validatie**: Datum (YYYY-MM-DD) en tijd (HH:MM) formaten
- **Foutafhandeling**: Duidelijke error messages voor 400/401/409 responses
- **Type Safety**: Volledig getypeerde payload en response

### Belangrijke Headers

- `Content-Type: application/json`
- `x-api-key: YOUR_API_KEY`

### Minimale Payload Velden

- `customerRef` (verplicht)
- `deliveryAddress.line1` (verplicht)
- `serviceDate` (YYYY-MM-DD format)
- `timeWindowStart/End` (HH:MM format, optioneel)
- `items[]` (optioneel)
- `notes` (optioneel)

## OpenAPI Specificatie

**Belangrijk**: De huidige `openapi.yaml` is een placeholder. Voor de complete specificatie:

1. Ga naar [https://docs.urbantz.com/](https://docs.urbantz.com/)
2. Zoek naar "Download OpenAPI specification"
3. Download de YAML/JSON file
4. Vervang `docs/urbantz/openapi.yaml` met de echte versie

## Response Codes

- **200**: Task succesvol aangemaakt
- **400**: Bad Request - ongeldige payload
- **401**: Unauthorized - ongeldige API key
- **409**: Conflict - task bestaat al
