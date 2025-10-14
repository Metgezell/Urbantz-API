# 🚀 Quick Start - PDF Upload met AI

## Snel Aan De Slag in 3 Stappen:

### 1️⃣ Maak .env Bestand
```bash
# Kopieer env.example naar .env
copy env.example .env

# Of op Linux/Mac:
cp env.example .env
```

Open `.env` en vul je Anthropic API key in:
```
ANTHROPIC_API_KEY=sk-ant-api03-jouw-key-hier
```

### 2️⃣ Start de Server
```bash
npm run server
```

Je zou dit moeten zien:
```
🚀 Local server running at http://localhost:3001
📱 Open your browser and test the Urbantz API interface!
```

### 3️⃣ Test het!
1. Open browser: `http://localhost:3001/index.html`
2. Sleep een PDF naar het upload vak
3. Je ziet nu: **📄 jouw-bestand.pdf (125.5 KB)**
4. Klik op **"Scan met AI"** 🤖
5. Klaar! Leveringen worden automatisch geëxtraheerd ✅

## 📝 Test Voorbeelden

### Test met Tekst (Zonder PDF)
Kopieer deze tekst en plak in het tekstvak:

```
REF: TEST-001
Klant: Bakkerij Jan
Adres: Hoofdstraat 12, 1000 Brussel
Contact: Jan Peeters
Nummer: +32 2 123 4567
Tijd: 09:00 - 12:00
Datum: 16/10/2025
```

Klik "Scan met AI" → Levering wordt gemaakt!

### Test met Multiple PDF's
1. Upload meerdere PDF's tegelijk
2. Ze worden allemaal getoond
3. Klik één keer op "Scan met AI"
4. Alle PDF's worden verwerkt!

## ✨ Nieuwe Features

### Visuele Feedback
Voor: Geen feedback ❌
Nu: Mooie kaartjes met bestanden ✅

### PDF Support
Voor: Alleen tekst ❌
Nu: PDF + Tekst + Beide! ✅

### Bestand Verwijderen
Klik op [×] om een bestand te verwijderen voor je scant

## 🎯 Wat Gebeurt Er?

1. **Upload PDF** → Bestand wordt lokaal opgeslagen
2. **Klik Scan** → PDF wordt naar server gestuurd
3. **Server leest PDF** → Tekst wordt geëxtraheerd met pdf-parse
4. **AI Analyse** → Anthropic Claude analyseert de tekst
5. **Extractie** → Leveringen worden automatisch gevonden
6. **Weergave** → Je ziet de leveringen in kaartjes
7. **Export** → Klik "Exporteer naar Urbantz" om te verzenden

## 🔥 Tips & Tricks

### Combineer Inputs
Je kunt **tegelijk**:
- Een PDF uploaden
- Tekst plakken in het vak
- Op "Scan met AI" klikken
→ Beide worden verwerkt en gecombineerd!

### Multiple Files
Upload zo veel PDF's als je wilt:
- Alle bestanden worden getoond
- Alle bestanden worden verwerkt
- Alle leveringen worden gecombineerd

### Fout Gemaakt?
Klik op [×] naast een bestand om het te verwijderen

## 🐛 Problemen?

### "ANTHROPIC_API_KEY niet gevonden"
→ Maak `.env` bestand met je API key

### PDF wordt niet getoond
→ Accepteert alleen: .pdf, .xlsx, .xls, .png, .jpg

### Server start niet
→ Port 3001 in gebruik? Stop andere Node apps:
```bash
# Windows
taskkill /F /IM node.exe

# Linux/Mac  
killall node
```

### Geen leveringen gevonden
→ Check of de PDF tekst bevat (niet alleen afbeeldingen)
→ De AI kan ook gescande PDF's lezen met Vision API

## 📞 Test Flow Voorbeeld

```
1. Sleep "leveringen.pdf" naar upload vak
   ✅ Zie: 📄 leveringen.pdf (234 KB) [×]

2. Klik "Scan met AI" 🤖
   ⏳ Loading...
   
3. Server output:
   📄 Analyzing document with AI: leveringen.pdf
   ✅ Extracted text from PDF: Levering informatie...
   ✅ Claude AI extracted 5 delivery(ies)
   
4. Browser toont:
   ✅ 5 nieuwe leveringen verschijnen
   ✅ Elk met adres, contact, tijd, etc.
   
5. Selecteer welke je wilt exporteren
   
6. Klik "Exporteer naar Urbantz"
   ✅ Done!
```

## 🎨 UI Voorbeelden

### Upload Area (Leeg)
```
┌──────────────────────────────────┐
│         [  +  ]                  │
│  Sleep bestanden hier            │
│  of klik om te uploaden          │
│  PDF, Excel, Afbeeldingen        │
└──────────────────────────────────┘
```

### Upload Area (Met PDF)
```
┌──────────────────────────────────┐
│         [  +  ]                  │
│  Sleep bestanden hier            │
│  of klik om te uploaden          │
│  PDF, Excel, Afbeeldingen        │
│                                  │
│  ┌────────────────────────────┐ │
│  │ 📄  leveringen.pdf    [×] │ │
│  │     234.5 KB              │ │
│  └────────────────────────────┘ │
│                                  │
│  ┌────────────────────────────┐ │
│  │ 📄  bestellingen.pdf  [×] │ │
│  │     156.2 KB              │ │
│  └────────────────────────────┘ │
└──────────────────────────────────┘
```

## 🎉 Success!

Als je dit ziet, werkt alles:
```
✅ Extracted text from PDF
✅ Claude AI extracted X delivery(ies)
```

Geniet van de nieuwe functionaliteit! 🚀

---

**Vragen?** Check `TEST-PDF-UPLOAD.md` voor details!

