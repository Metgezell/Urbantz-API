# 🚀 Firebase Quickstart

## In 5 Minuten aan de Slag

### Stap 1: Firebase Project Setup (eenmalig)

```bash
# Login bij Firebase
firebase login

# Update .firebaserc met je project ID
# Vervang "your-project-id" met je echte Firebase project ID
```

### Stap 2: Credentials Configureren

1. Ga naar [Firebase Console](https://console.firebase.google.com)
2. Selecteer je project
3. Project Settings → Service Accounts → Generate new private key
4. Kopieer de waarden naar `.env`:

```env
ANTHROPIC_API_KEY=sk-ant-xxxxx                    # Heb je al!
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
```

### Stap 3: Deploy Functions

```bash
# Bouw TypeScript code
cd functions
npm run build
cd ..

# Deploy naar Firebase
firebase deploy --only functions
```

Klaar! Je hebt nu 5 Cloud Functions live:
- ✅ `analyzeFile` - Document analyse
- ✅ `saveCorrection` - Training data opslaan
- ✅ `exportToUrbantz` - Export naar Urbantz
- ✅ `getDeliveries` - Leveringen ophalen
- ✅ `getTrainingSamples` - Training data ophalen

### Stap 4: Test een Function

```javascript
// Test in browser console of in je HTML
const functions = firebase.functions();
const analyzeFile = functions.httpsCallable('analyzeFile');

const result = await analyzeFile({
  fileType: 'text',
  text: 'REF: ORD-001\nKlant: Test BV\nAdres: Teststraat 1, 1000 Brussel'
});

console.log(result.data.deliveries);
```

---

## 🧪 Lokaal Testen (zonder deploy)

```bash
# Start Firebase Emulators
firebase emulators:start

# Functions draaien nu lokaal op:
# http://localhost:5001/your-project/us-central1/analyzeFile
```

---

## 📊 Cloud Functions URLs

Na deployment zijn je functions beschikbaar op:

```
https://us-central1-YOUR_PROJECT_ID.cloudfunctions.net/analyzeFile
https://us-central1-YOUR_PROJECT_ID.cloudfunctions.net/saveCorrection
https://us-central1-YOUR_PROJECT_ID.cloudfunctions.net/exportToUrbantz
https://us-central1-YOUR_PROJECT_ID.cloudfunctions.net/getDeliveries
https://us-central1-YOUR_PROJECT_ID.cloudfunctions.net/getTrainingSamples
```

---

## 🗄️ Firestore Database

Na eerste gebruik worden automatisch 3 collections aangemaakt:

1. **deliveries** - Alle geëxtraheerde leveringen
2. **trainingSamples** - Gebruikerscorrecties voor AI training
3. **extractionLogs** - Logs van alle AI extracties

Bekijk in Firebase Console → Firestore Database

---

## 🎯 Workflow

```
1. Upload document → analyzeFile()
   ↓
2. AI extraheert data → Opgeslagen in Firestore
   ↓
3. Gebruiker controleert/corrigeert → saveCorrection()
   ↓
4. Goedkeuren → exportToUrbantz()
   ↓
5. Taken aangemaakt in Urbantz ✅
```

---

## 🆘 Problemen?

**Build errors?**
```bash
cd functions
npm install
npm run build
```

**Deploy errors?**
```bash
firebase login
firebase use your-project-id
firebase deploy --only functions
```

**Function errors?**
```bash
# Bekijk logs
firebase functions:log

# Of in Firebase Console → Functions → Logs
```

---

## 📚 Meer Info

- **Setup Details**: Zie `FIREBASE-SETUP.md`
- **Code Voorbeelden**: Zie `FIREBASE-USAGE.md`
- **Implementatie**: Zie `IMPLEMENTATION-SUMMARY.md`

---

## ✨ Pro Tips

1. **Test lokaal eerst** met `firebase emulators:start`
2. **Check logs** met `firebase functions:log`
3. **Monitor costs** in Firebase Console → Usage
4. **Backup data** regelmatig met Firestore export
5. **Use .env** files voor development

---

Klaar om te beginnen? Run:

```bash
firebase deploy --only functions
```

🚀 **Let's go!**

