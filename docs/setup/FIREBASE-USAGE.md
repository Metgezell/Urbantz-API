# Firebase Functions Gebruikshandleiding

Deze handleiding laat zien hoe je de Firebase Cloud Functions gebruikt in je Urbantz Document Scanner.

## 🎯 Beschikbare Cloud Functions

### 1. analyzeFile - Document Analyse

Analyseert geüploade bestanden of tekst en extraheert leveringsinformatie.

**Input:**
```javascript
{
  fileType: "pdf" | "excel" | "email" | "text",
  text: string,              // Optioneel: directe tekst input
  fileBuffer: string,        // Optioneel: base64 encoded bestand
  fileName: string           // Optioneel: bestandsnaam
}
```

**Output:**
```javascript
{
  success: true,
  deliveries: [...],         // Array met geëxtraheerde leveringen
  deliveryIds: [...],        // Firestore document IDs
  deliveryCount: 5,
  confidence: 85,
  metadata: {...},
  extractedText: "..."       // Preview van geëxtraheerde tekst
}
```

**Voorbeeld gebruik:**

```javascript
// In browser met Firebase SDK
const functions = firebase.functions();
const analyzeFile = functions.httpsCallable('analyzeFile');

// Analyseer PDF
const pdfBuffer = await file.arrayBuffer();
const base64 = btoa(String.fromCharCode(...new Uint8Array(pdfBuffer)));

const result = await analyzeFile({
  fileType: 'pdf',
  fileBuffer: base64,
  fileName: 'leveringen.pdf'
});

console.log(`${result.data.deliveryCount} leveringen gevonden!`);
```

**Voorbeeld met tekst:**

```javascript
const result = await analyzeFile({
  fileType: 'text',
  text: `
    1. REF: ORD-001
       Klant: Bakkerij Jan
       Adres: Hoofdstraat 1, 1000 Brussel
       Tijd: 08:00 - 10:00
    
    2. REF: ORD-002
       Klant: Café Marie
       Adres: Kerkstraat 5, 2000 Antwerpen
       Tijd: 09:00 - 11:00
  `
});
```

---

### 2. saveCorrection - Training Data Opslaan

Slaat gebruikerscorrecties op voor AI training.

**Input:**
```javascript
{
  originalExtraction: {...},  // Originele AI output
  correctedData: {...},       // Door gebruiker gecorrigeerde data
  documentType: "email" | "pdf" | "excel"
}
```

**Output:**
```javascript
{
  success: true,
  sampleId: "abc123",
  message: "Correction saved successfully"
}
```

**Voorbeeld:**

```javascript
const saveCorrection = functions.httpsCallable('saveCorrection');

const result = await saveCorrection({
  originalExtraction: {
    customerRef: "ORD-01",    // AI dacht dit
    deliveryAddress: { line1: "Straat 1" }
  },
  correctedData: {
    customerRef: "ORD-001",   // Gebruiker corrigeerde naar dit
    deliveryAddress: { line1: "Hoofdstraat 1, 1000 Brussel" }
  },
  documentType: "email"
});
```

---

### 3. exportToUrbantz - Export naar Urbantz

Exporteert goedgekeurde leveringen naar Urbantz API.

**Input:**
```javascript
{
  deliveryIds: ["id1", "id2", "id3"]  // Firestore document IDs
}
```

**Output:**
```javascript
{
  success: true,
  totalDeliveries: 3,
  successful: 2,
  failed: 1,
  results: [
    {
      success: true,
      deliveryId: "id1",
      customerRef: "ORD-001",
      urbantzTaskId: "URBANTZ-123456",
      message: "Task created successfully"
    }
  ],
  errors: [
    {
      deliveryId: "id3",
      customerRef: "ORD-003",
      error: "Missing required fields"
    }
  ]
}
```

**Voorbeeld:**

```javascript
const exportToUrbantz = functions.httpsCallable('exportToUrbantz');

const result = await exportToUrbantz({
  deliveryIds: ["abc123", "def456", "ghi789"]
});

console.log(`${result.data.successful} van ${result.data.totalDeliveries} geëxporteerd`);
```

---

### 4. getDeliveries - Leveringen Ophalen

Haalt leveringen op uit Firestore gefilterd op status.

**Input:**
```javascript
{
  status: "draft" | "validated" | "exported",  // Optioneel
  limit: 50                                     // Optioneel, default 50
}
```

**Output:**
```javascript
{
  success: true,
  deliveries: [...],
  count: 25
}
```

**Voorbeeld:**

```javascript
const getDeliveries = functions.httpsCallable('getDeliveries');

// Haal alle draft leveringen op
const drafts = await getDeliveries({ status: 'draft' });

// Haal laatste 100 leveringen op (alle statussen)
const recent = await getDeliveries({ limit: 100 });
```

---

### 5. getTrainingSamples - Training Data Ophalen

Haalt opgeslagen training samples op voor analyse.

**Input:**
```javascript
{
  limit: 100  // Optioneel, default 100
}
```

**Output:**
```javascript
{
  success: true,
  samples: [...],
  count: 42
}
```

**Voorbeeld:**

```javascript
const getTrainingSamples = functions.httpsCallable('getTrainingSamples');

const result = await getTrainingSamples({ limit: 50 });
console.log(`${result.data.count} training samples beschikbaar`);
```

---

## 🔄 Complete Workflow Voorbeeld

Hier is een volledig voorbeeld van document upload tot Urbantz export:

```javascript
// Stap 1: Initialiseer Firebase
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id"
};
firebase.initializeApp(firebaseConfig);
const functions = firebase.functions();

// Stap 2: Analyseer document
async function analyzeDocument(file) {
  const analyzeFile = functions.httpsCallable('analyzeFile');
  
  const buffer = await file.arrayBuffer();
  const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)));
  
  const result = await analyzeFile({
    fileType: file.name.endsWith('.pdf') ? 'pdf' : 'excel',
    fileBuffer: base64,
    fileName: file.name
  });
  
  return result.data;
}

// Stap 3: Toon resultaten en laat gebruiker corrigeren
function showResults(analysisResult) {
  const deliveries = analysisResult.deliveries;
  
  // Render in UI...
  deliveries.forEach((delivery, index) => {
    console.log(`Levering ${index + 1}:`);
    console.log(`  Ref: ${delivery.customerRef}`);
    console.log(`  Adres: ${delivery.deliveryAddress.line1}`);
  });
}

// Stap 4: Sla correctie op (optioneel)
async function saveUserCorrection(original, corrected) {
  const saveCorrection = functions.httpsCallable('saveCorrection');
  
  await saveCorrection({
    originalExtraction: original,
    correctedData: corrected,
    documentType: 'pdf'
  });
  
  console.log('Correctie opgeslagen voor toekomstige AI verbetering');
}

// Stap 5: Export naar Urbantz
async function exportToUrbantz(deliveryIds) {
  const exportFunc = functions.httpsCallable('exportToUrbantz');
  
  const result = await exportFunc({ deliveryIds });
  
  console.log(`Exported ${result.data.successful}/${result.data.totalDeliveries}`);
  
  if (result.data.errors.length > 0) {
    console.error('Errors:', result.data.errors);
  }
  
  return result.data;
}

// Gebruik de workflow
async function processDocument(file) {
  // 1. Analyseer
  const analysis = await analyzeDocument(file);
  showResults(analysis);
  
  // 2. Wacht op gebruiker goedkeuring/correcties
  // (in echte app: UI interactie)
  
  // 3. Export goedgekeurde leveringen
  const exportResult = await exportToUrbantz(analysis.deliveryIds);
  
  return exportResult;
}
```

---

## 📊 Firestore Data Structuur

### deliveries collection

```javascript
{
  id: "auto-generated-id",
  customerRef: "ORD-001",
  deliveryAddress: {
    line1: "Hoofdstraat 1, 1000 Brussel",
    contactName: "Jan Janssen",
    contactPhone: "+32 2 123 4567"
  },
  serviceDate: "2024-01-15",
  timeWindowStart: "09:00",
  timeWindowEnd: "12:00",
  items: [
    {
      description: "2x Pakketten",
      quantity: 1,
      tempClass: "ambient"
    }
  ],
  notes: "Extra info",
  priority: "normal",
  status: "draft",           // "draft" | "validated" | "exported"
  sourceType: "pdf",         // "pdf" | "excel" | "email" | "text"
  createdAt: Timestamp,
  updatedAt: Timestamp
}
```

### trainingSamples collection

```javascript
{
  id: "auto-generated-id",
  originalExtraction: { /* AI output */ },
  correctedData: { /* User corrected */ },
  documentType: "pdf",
  userId: "user-id-or-anonymous",
  createdAt: Timestamp
}
```

### extractionLogs collection

```javascript
{
  id: "auto-generated-id",
  inputText: "Text that was analyzed (first 1000 chars)",
  extractedData: [ /* Array of deliveries */ ],
  confidence: 85,
  model: "claude-3-5-sonnet-20241022",
  timestamp: Timestamp
}
```

---

## 🔍 Firestore Queries Voorbeelden

```javascript
const db = firebase.firestore();

// Haal alle draft leveringen op
const drafts = await db.collection('deliveries')
  .where('status', '==', 'draft')
  .orderBy('createdAt', 'desc')
  .get();

// Haal leveringen van vandaag op
const today = new Date();
today.setHours(0, 0, 0, 0);

const todayDeliveries = await db.collection('deliveries')
  .where('createdAt', '>=', today)
  .get();

// Haal PDF leveringen op
const pdfDeliveries = await db.collection('deliveries')
  .where('sourceType', '==', 'pdf')
  .limit(10)
  .get();

// Haal training samples op
const samples = await db.collection('trainingSamples')
  .orderBy('createdAt', 'desc')
  .limit(50)
  .get();
```

---

## 🚨 Error Handling

```javascript
try {
  const analyzeFile = functions.httpsCallable('analyzeFile');
  const result = await analyzeFile({ text: 'test' });
  
} catch (error) {
  if (error.code === 'functions/invalid-argument') {
    console.error('Ongeldige input:', error.message);
  } else if (error.code === 'functions/failed-precondition') {
    console.error('API key niet geconfigureerd:', error.message);
  } else if (error.code === 'functions/internal') {
    console.error('Server error:', error.message);
  } else {
    console.error('Onbekende error:', error);
  }
}
```

---

## 🎨 UI Integratie Voorbeeld

```html
<!DOCTYPE html>
<html>
<head>
  <title>Urbantz Document Scanner</title>
  <script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js"></script>
  <script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-functions-compat.js"></script>
</head>
<body>
  <input type="file" id="fileInput" accept=".pdf,.xlsx,.xls">
  <button onclick="analyzeDocument()">Analyseer</button>
  <div id="results"></div>
  
  <script>
    // Firebase configuratie
    const firebaseConfig = {
      apiKey: "YOUR_API_KEY",
      projectId: "your-project-id"
    };
    firebase.initializeApp(firebaseConfig);
    
    async function analyzeDocument() {
      const file = document.getElementById('fileInput').files[0];
      if (!file) return;
      
      const functions = firebase.functions();
      const analyzeFile = functions.httpsCallable('analyzeFile');
      
      // Converteer naar base64
      const buffer = await file.arrayBuffer();
      const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)));
      
      // Call function
      const result = await analyzeFile({
        fileType: file.name.endsWith('.pdf') ? 'pdf' : 'excel',
        fileBuffer: base64,
        fileName: file.name
      });
      
      // Toon resultaten
      document.getElementById('results').innerHTML = `
        <h3>Gevonden: ${result.data.deliveryCount} leveringen</h3>
        <pre>${JSON.stringify(result.data.deliveries, null, 2)}</pre>
      `;
    }
  </script>
</body>
</html>
```

---

## 📝 Tips & Best Practices

1. **Batch Processing**: Voor grote bestanden, splits de analyse op in kleinere batches
2. **Error Recovery**: Sla failed exports op en probeer later opnieuw
3. **Caching**: Cache extraction logs om duplicate analyses te voorkomen
4. **Monitoring**: Gebruik Firebase Console om logs en errors te monitoren
5. **Rate Limiting**: Let op Anthropic API rate limits (gebruik delays bij bulk processing)

---

## 🔗 Volgende Stappen

1. Test de functions lokaal met Firebase Emulators
2. Deploy naar Firebase met `firebase deploy --only functions`
3. Configureer production environment variables
4. Implementeer authentication voor production
5. Set up monitoring en alerting

Voor meer details, zie `FIREBASE-SETUP.md`

