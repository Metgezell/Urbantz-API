# 🚀 Urbantz AI Document Scanner - Server Setup

## ✅ Probleem Opgelost!

Het oneindig laden probleem is opgelost met een **stabiele server** die betere error handling heeft.

## 🎯 Eenvoudige Hosting - 3 Manieren

### Methode 1: PowerShell Script (Aanbevolen)
```powershell
.\start-urbantz.ps1
```

### Methode 2: Batch Script
```cmd
start-urbantz.bat
```

### Methode 3: Direct Python
```bash
python start-server.py
```

## 🌐 Toegang
- **URL:** http://localhost:8000
- **Poort:** 8000 (altijd consistent)
- **Status:** http://localhost:8000/api/health

## 🔧 Verbeteringen

### ✅ **Stabiliteit**
- Betere error handling
- Graceful shutdown met Ctrl+C
- Automatische port conflict resolutie
- Geen oneindig laden meer

### ✅ **AI Extractie**
- Verbeterde adres herkenning
- Betere contact naam extractie
- Nauwkeurigere telefoon nummers
- Intelligente datum/tijd parsing
- Email-specifieke patronen

### ✅ **Gebruiksvriendelijkheid**
- Eenvoudige startup scripts
- Duidelijke status berichten
- Automatische herstart bij problemen

## 🧪 Test Voorbeelden

### Voorbeeld 1: Nederlandse Email
```
Beste team,

We hebben een levering voor morgen nodig:

Klant: CUST-12345
Adres: Koningstraat 15, 1000 Brussel
Contact: Jan Janssen
Telefoon: +32 2 123 4567
Datum: 15/10/2024
Tijd: 09:00 - 12:00

Met vriendelijke groet,
Delivery Team
```

### Voorbeeld 2: Belgische Levering
```
Delivery informatie:

Order: ORD-789
Leveren aan: Maria Verstraeten
Grote Markt 8, 2000 Antwerpen
Tel: 03 234 5678
Voor 16/10/2024 tussen 13:00 en 16:00
```

## 🛠️ Troubleshooting

### Server start niet?
1. Controleer of Python geïnstalleerd is: `python --version`
2. Probeer de PowerShell script: `.\start-urbantz.ps1`
3. Controleer poort 8000: `netstat -an | findstr :8000`

### Port al in gebruik?
De server probeert automatisch andere Python processen te stoppen.

### AI extractie werkt niet goed?
- Gebruik duidelijke labels: "Adres:", "Contact:", "Telefoon:"
- Vermijd complexe formatting
- Test met de voorbeelden hierboven

## 📁 Bestanden Overzicht

- `start-server.py` - Stabiele server met error handling
- `start-urbantz.ps1` - PowerShell startup script
- `start-urbantz.bat` - Windows batch script
- `index.html` - Frontend interface
- `start-local.py` - Oude server (niet meer gebruiken)

## 🎉 Klaar!

Je kunt nu altijd gemakkelijk hosten zonder problemen. Gebruik gewoon:
```powershell
.\start-urbantz.ps1
```

En ga naar http://localhost:8000 🚀
