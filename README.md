# Urbantz AI Document Scanner

Een intelligente document scanner die automatisch leveringsinformatie uit documenten en tekst kan extraheren en direct taken aanmaakt in Urbantz.

## 🚀 Features

- **AI-Powered Document Analysis**: Automatisch extraheren van leveringsinformatie uit documenten en tekst
- **Smart Pattern Recognition**: Herkent klant referenties, adressen, contactpersonen, tijdsvensters en items
- **Bulk Export naar Urbantz**: Direct exporteren van meerdere leveringen naar Urbantz systeem
- **File Upload Support**: Ondersteuning voor PDF, Excel en afbeeldingen
- **Real-time Validation**: Controleert data integriteit voordat export naar Urbantz
- **Modern Web Interface**: Gebruiksvriendelijke interface met drag & drop functionaliteit

## 📋 Wat wordt er geëxtraheerd?

De AI scanner herkent automatisch:

- **Klant Referentie**: CUST-12345, ORDER-456, etc.
- **Leveradres**: Volledige adresinformatie met postcode
- **Contact Persoon**: Naam en telefoonnummer
- **Leverdatum**: Datum in verschillende formaten
- **Tijdsvenster**: Start- en eindtijd voor levering
- **Items**: Pakketten, producten en hun specificaties
- **Prioriteit**: Urgent, normaal of laag op basis van tekst

## 🛠️ Installatie & Setup

### Vereisten
- Python 3.7+
- Moderne webbrowser

### Stap 1: Server Starten
```bash
python start-local-fixed.py
```

De server start op `http://localhost:3001`

### Stap 2: Interface Openen
Open je webbrowser en ga naar: `http://localhost:3001`

## 📖 Gebruik

### 1. Document Upload
- Sleep bestanden (PDF, Excel, afbeeldingen) naar de upload area
- Of klik om bestanden te selecteren

### 2. Tekst Analyse
- Plak email tekst of document content in het tekstveld
- Klik op "Scan met AI" knop
- De AI analyseert de tekst en extraheert leveringsinformatie

### 3. Data Controle
- Bekijk de geëxtraheerde leveringen in de grid
- Bewerk gegevens indien nodig via de edit knop
- Selecteer leveringen die geëxporteerd moeten worden

### 4. Export naar Urbantz
- Klik op "Exporteer Geselecteerde" of "Exporteer Alles"
- De leveringen worden automatisch als taken aangemaakt in Urbantz
- Ontvang bevestiging van succesvolle export

## 🔥 Firebase Integration (NEW!)

Dit project heeft nu **Firebase Cloud Functions** voor schaalbare, cloud-based document processing:

### ✨ Nieuwe Mogelijkheden

- **☁️ Cloud Functions**: 5 serverless functions voor document analyse, training en export
- **🗄️ Firestore Database**: Permanente opslag van leveringen, training data en logs
- **📦 Document Processing**: PDF (unpdf), Excel (SheetJS), Email (mailparser) extractors
- **🤖 AI Orchestration**: Genkit integration met Claude AI
- **🔒 Security**: Server-side API keys, authentication support

### 📚 Documentatie

- **[FIREBASE-SETUP.md](FIREBASE-SETUP.md)** - Volledige setup handleiding
- **[FIREBASE-USAGE.md](FIREBASE-USAGE.md)** - Gebruik voorbeelden en code snippets
- **[IMPLEMENTATION-SUMMARY.md](IMPLEMENTATION-SUMMARY.md)** - Implementatie overzicht

### 🚀 Quick Start Firebase

```bash
# 1. Installeer dependencies
npm install

# 2. Configureer Firebase
firebase login
# Update .firebaserc met je project ID

# 3. Deploy
firebase deploy --only functions

# 4. Test
firebase emulators:start
```

### 💻 Bestaande Setup Blijft Werken

De Firebase integratie is **toegevoegd naast** de bestaande Node.js/Python setup:

- ✅ `node local-server.js` werkt nog steeds
- ✅ `python start-local-fixed.py` werkt nog steeds  
- ✅ `index.html` en `ai-training.html` werken nog steeds

Je kunt kiezen welke backend je wilt gebruiken!

---

## 🔧 API Endpoints

### POST /api/smart-analyze
Analyseert tekst met AI en extraheert leveringsinformatie.

**Request:**
```json
{
  "text": "Levering voor klant CUST-12345 naar Koningstraat 15, 1000 Brussel...",
  "fileType": "text"
}
```

**Response:**
```json
{
  "success": true,
  "confidence": 85,
  "deliveries": [
    {
      "taskId": "TASK-1234567890-1",
      "customerRef": "CUST-12345",
      "deliveryAddress": {
        "line1": "Koningstraat 15, 1000 Brussel",
        "contactName": "Jan Janssen",
        "contactPhone": "+32 2 123 4567"
      },
      "serviceDate": "2024-01-15",
      "timeWindowStart": "09:00",
      "timeWindowEnd": "12:00",
      "items": [
        {
          "description": "2x Pakketten",
          "quantity": 1,
          "tempClass": "ambient"
        }
      ],
      "priority": "normal"
    }
  ],
  "deliveryCount": 1,
  "aiPowered": true
}
```

### POST /api/urbantz-export
Exporteert leveringen naar Urbantz systeem.

**Request:**
```json
[
  {
    "customerRef": "CUST-12345",
    "deliveryAddress": {
      "line1": "Koningstraat 15, 1000 Brussel",
      "contactName": "Jan Janssen",
      "contactPhone": "+32 2 123 4567"
    },
    "serviceDate": "2024-01-15",
    "timeWindowStart": "09:00",
    "timeWindowEnd": "12:00",
    "items": [...],
    "notes": "..."
  }
]
```

**Response:**
```json
{
  "success": true,
  "totalDeliveries": 1,
  "successful": 1,
  "failed": 0,
  "results": [
    {
      "success": true,
      "customerRef": "CUST-12345",
      "taskId": "URBANTZ-1234567890-1234",
      "message": "Task created successfully"
    }
  ],
  "errors": []
}
```

### GET /api/health
Health check endpoint.

**Response:**
```json
{
  "status": "OK",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## 🧪 Testing

Voer de test suite uit om alle functionaliteit te valideren:

```bash
python test-api.py
```

De test suite controleert:
- Health endpoint
- AI tekst analyse
- Urbantz export functionaliteit
- Data extractie kwaliteit

## 📁 Project Structuur

```
urbantz-koppeling/
├── index.html                 # Frontend interface
├── start-local-fixed.py      # Python server
├── test-api.py               # API test suite
├── api/                      # API endpoints
│   ├── smart-analyze.js      # AI analyse endpoint
│   ├── analyze-document.js   # Document analyse endpoint
│   └── urbantz.js           # Urbantz integratie
├── src/                      # TypeScript client
├── docs/                     # Documentatie
└── README.md                # Deze file
```

## 🔍 AI Extractie Logica

De AI gebruikt geavanceerde pattern matching om informatie te extraheren:

### Klant Referentie Patterns
- `CUST-12345`, `ORDER-456`
- `klant: ABC123`, `customer: XYZ789`
- Algemene referentie formaten

### Adres Patterns
- `Koningstraat 15, 1000 Brussel`
- `Grote Markt 8, 2000 Antwerpen`
- Nederlandse en Belgische adres formaten

### Contact Patterns
- `Contact: Jan Janssen`
- `Naam: Maria Verstraeten`
- Telefoonnummers: `+32 2 123 4567`

### Tijd Patterns
- `09:00 - 12:00`
- `tussen 10:00 en 14:00`
- `van 13:00 tot 17:00`

## 🚀 Productie Deployment

Voor productie gebruik:

1. **Configureer echte Urbantz API**:
   - Vervang mock API calls in `start-local-fixed.py`
   - Voeg authenticatie toe
   - Configureer productie endpoints

2. **Voeg echte AI services toe**:
   - Google Vision API voor OCR
   - Anthropic Claude voor geavanceerde tekst analyse

3. **Security & Performance**:
   - HTTPS certificaten
   - Rate limiting
   - Input validation
   - Error handling

## 📞 Support

Voor vragen of problemen:
- Controleer de console logs voor errors
- Test de API endpoints met de test suite
- Raadpleeg de documentatie in `/docs`

## 📄 License

MIT License - Zie LICENSE file voor details.

---

**✨ Klaar om documenten te scannen en automatisch Urbantz taken aan te maken!**
