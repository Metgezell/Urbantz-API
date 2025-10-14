# Firebase Setup Guide

Deze handleiding helpt je om Firebase te configureren voor je Urbantz Document Scanner project.

## 📋 Vereisten

- Node.js 18+ geïnstalleerd
- Firebase project aangemaakt in [Firebase Console](https://console.firebase.google.com)
- Firebase CLI geïnstalleerd (gedaan via npm install -g firebase-tools)

## 🔧 Stap 1: Firebase Project Configureren

### 1.1 Maak een Firebase Project

1. Ga naar [Firebase Console](https://console.firebase.google.com)
2. Klik op "Add project" of selecteer een bestaand project
3. Volg de stappen om je project aan te maken

### 1.2 Activeer Firestore Database

1. In Firebase Console, ga naar **Build** → **Firestore Database**
2. Klik op **Create database**
3. Kies **Start in test mode** (we zullen later de regels aanpassen)
4. Selecteer een locatie (bijv. `europe-west1` voor Europa)

### 1.3 Activeer Firebase Storage

1. In Firebase Console, ga naar **Build** → **Storage**
2. Klik op **Get started**
3. Accepteer de standaard regels
4. Storage wordt automatisch aangemaakt

### 1.4 Genereer Service Account Key

1. In Firebase Console, ga naar **Project Settings** (tandwiel icoon)
2. Ga naar het tabblad **Service accounts**
3. Klik op **Generate new private key**
4. Download het JSON bestand (bewaar dit veilig!)

## 🔑 Stap 2: Environment Variables Configureren

### 2.1 Kopieer env.example naar .env

```bash
cp env.example .env
```

### 2.2 Vul Firebase Credentials in .env

Open het gedownloade service account JSON bestand en kopieer de waarden:

```env
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour private key here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project-id.iam.gserviceaccount.com
```

**Let op:** De private key moet tussen aanhalingstekens en met `\n` voor newlines.

### 2.3 Vul Anthropic API Key in

```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

### 2.4 Vul Urbantz API Key in (optioneel voor nu)

```env
URBANTZ_API_KEY=your-urbantz-api-key
```

## 🔗 Stap 3: Firebase Project Koppelen

### 3.1 Update .firebaserc

Open `.firebaserc` en vervang `your-project-id` met je echte Firebase project ID:

```json
{
  "projects": {
    "default": "your-actual-project-id"
  }
}
```

### 3.2 Login bij Firebase

```bash
firebase login
```

Dit opent een browser window waar je moet inloggen met je Google account.

### 3.3 Verifieer Project Koppeling

```bash
firebase projects:list
```

Je zou je project in de lijst moeten zien.

## 📦 Stap 4: Functions Environment Variables Instellen

Firebase Functions hebben hun eigen environment variables nodig:

```bash
cd functions
firebase functions:config:set anthropic.api_key="sk-ant-xxxxx"
firebase functions:config:set urbantz.api_key="your-urbantz-key"
firebase functions:config:set urbantz.base_url="https://api.urbantz.com"
```

Of gebruik een `.env` bestand in de functions directory (aanbevolen voor development):

```bash
cd functions
cp ../.env .env
```

## 🏗️ Stap 5: Build en Deploy

### 5.1 Build Functions

```bash
cd functions
npm run build
```

### 5.2 Deploy naar Firebase

```bash
cd ..
firebase deploy --only functions
```

Dit deployt alle Cloud Functions naar Firebase.

### 5.3 Deploy Firestore Rules

```bash
firebase deploy --only firestore:rules
```

### 5.4 Deploy Storage Rules

```bash
firebase deploy --only storage
```

### 5.5 Deploy Alles Tegelijk

```bash
firebase deploy
```

## 🧪 Stap 6: Testen

### 6.1 Test Cloud Functions Lokaal (Emulators)

```bash
firebase emulators:start
```

Dit start lokale emulators voor Functions, Firestore, en Storage.

### 6.2 Test een Cloud Function

Je kunt de deployed functions testen via de Firebase Console of met curl:

```bash
# Get the function URL from Firebase Console
curl -X POST https://YOUR-REGION-YOUR-PROJECT.cloudfunctions.net/analyzeFile \
  -H "Content-Type: application/json" \
  -d '{"text": "Test levering naar Brussel"}'
```

## 📊 Stap 7: Firestore Database Structuur

Na deployment worden automatisch de volgende collections aangemaakt bij eerste gebruik:

### Collections:

1. **deliveries** - Geëxtraheerde leveringen
   - Status: draft, validated, exported
   - Bevat alle levering informatie

2. **trainingSamples** - Gebruikerscorrecties voor AI training
   - Originele extractie vs gecorrigeerde data
   - Gebruikt voor model verbetering

3. **extractionLogs** - Logs van alle AI extracties
   - Input tekst, output, confidence
   - Voor debugging en analyse

## 🔒 Stap 8: Security Rules (Productie)

Voor productie moet je de Firestore rules aanpassen in `firestore.rules`:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Deliveries - alleen voor authenticated users
    match /deliveries/{deliveryId} {
      allow read, write: if request.auth != null;
    }
    
    // Training samples - alleen voor authenticated users
    match /trainingSamples/{sampleId} {
      allow read, write: if request.auth != null;
    }
    
    // Extraction logs - alleen admins
    match /extractionLogs/{logId} {
      allow read: if request.auth != null;
      allow write: if request.auth.token.admin == true;
    }
  }
}
```

Deploy de nieuwe rules:

```bash
firebase deploy --only firestore:rules
```

## 🔍 Stap 9: Monitoring & Logs

### View Function Logs

```bash
firebase functions:log
```

Of in Firebase Console → Functions → Logs

### View Firestore Data

Ga naar Firebase Console → Firestore Database om je data te bekijken en te bewerken.

## 📱 Stap 10: Frontend Integratie (Optioneel)

Als je Firebase SDK wilt gebruiken in je frontend:

### 10.1 Voeg Firebase SDK toe aan HTML

```html
<script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-functions-compat.js"></script>

<script>
  // Firebase configuratie (gebruik PUBLIC keys, geen private key!)
  const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "your-project.firebaseapp.com",
    projectId: "your-project-id",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "123456789",
    appId: "1:123456789:web:abcdef"
  };
  
  firebase.initializeApp(firebaseConfig);
  const functions = firebase.functions();
  
  // Call Cloud Function
  const analyzeFile = functions.httpsCallable('analyzeFile');
  analyzeFile({ text: 'Test data' })
    .then(result => console.log(result.data));
</script>
```

### 10.2 Of gebruik moderne SDK

```bash
npm install firebase
```

```javascript
import { initializeApp } from 'firebase/app';
import { getFunctions, httpsCallable } from 'firebase/functions';

const app = initializeApp(firebaseConfig);
const functions = getFunctions(app);

const analyzeFile = httpsCallable(functions, 'analyzeFile');
const result = await analyzeFile({ text: 'Test data' });
```

## ✅ Checklist

- [ ] Firebase project aangemaakt
- [ ] Firestore Database geactiveerd
- [ ] Firebase Storage geactiveerd
- [ ] Service account key gegenereerd
- [ ] `.env` bestand geconfigureerd
- [ ] `.firebaserc` project ID ingesteld
- [ ] `firebase login` uitgevoerd
- [ ] Functions environment variables ingesteld
- [ ] `npm install` in functions/ directory
- [ ] Functions gebuild met `npm run build`
- [ ] Functions deployed met `firebase deploy`
- [ ] Firestore rules deployed
- [ ] Functions getest (lokaal of remote)

## 🚨 Troubleshooting

### Error: "Default Firebase app not initialized"

→ Check of `admin.initializeApp()` wordt aangeroepen in `firebase.ts`

### Error: "ANTHROPIC_API_KEY not configured"

→ Zet de API key in Firebase Functions config:
```bash
firebase functions:config:set anthropic.api_key="your-key"
```

### Error: "Permission denied" bij Firestore

→ Check je `firestore.rules` en zorg dat de regels correct zijn

### Functions deployen duurt lang

→ Dit is normaal, eerste deployment kan 5-10 minuten duren

### Build errors in TypeScript

→ Run `npm run build` in de functions directory en fix TypeScript errors

## 📚 Meer Informatie

- [Firebase Documentation](https://firebase.google.com/docs)
- [Cloud Functions Documentation](https://firebase.google.com/docs/functions)
- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Genkit Documentation](https://firebase.google.com/docs/genkit)

## 🎉 Klaar!

Je Firebase backend is nu geconfigureerd! Je kunt nu:

1. ✅ Documenten uploaden en analyseren via Cloud Functions
2. ✅ Data opslaan in Firestore
3. ✅ Correcties opslaan voor AI training
4. ✅ Deliveries exporteren naar Urbantz
5. ✅ Alle data beveiligd opslaan in de cloud

Veel success met je Urbantz Document Scanner! 🚀

