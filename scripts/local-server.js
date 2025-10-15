const express = require('express');
const path = require('path');
const cors = require('cors');
const multer = require('multer');
const dotenv = require('dotenv');
const fs = require('fs').promises;

// Load .env from project root
const envPath = path.join(__dirname, '..', '.env');
console.log('Loading .env from:', envPath);
dotenv.config({ path: envPath });
console.log('ANTHROPIC_API_KEY loaded:', process.env.ANTHROPIC_API_KEY ? 'YES (length: ' + process.env.ANTHROPIC_API_KEY.length + ')' : 'NO');

const app = express();
const PORT = 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Multer for file uploads
const upload = multer({ dest: 'uploads/' });

// Urbantz Export endpoint for bulk task creation
app.post('/api/urbantz-export', async (req, res) => {
  try {
    const deliveries = req.body;
    
    if (!Array.isArray(deliveries) || deliveries.length === 0) {
      return res.status(400).json({ 
        error: 'Expected array of deliveries' 
      });
    }
    
    console.log(`📦 Exporting ${deliveries.length} deliveries to Urbantz...`);
    
    const results = [];
    const errors = [];
    
    // Process each delivery
    for (const delivery of deliveries) {
      try {
        // Validation
        if (!delivery.customerRef || !delivery.deliveryAddress?.line1) {
          errors.push({
            delivery: delivery.customerRef || 'Unknown',
            error: 'customerRef and deliveryAddress.line1 are required'
          });
          continue;
        }
        
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 200));
        
        // Create Urbantz task
        const taskResult = await createUrbantzTask(delivery);
        
        results.push({
          success: true,
          customerRef: delivery.customerRef,
          taskId: taskResult.taskId,
          message: 'Task created successfully'
        });
        
      } catch (error) {
        errors.push({
          delivery: delivery.customerRef || 'Unknown',
          error: error.message
        });
      }
    }
    
    const response = {
      success: true,
      totalDeliveries: deliveries.length,
      successful: results.length,
      failed: errors.length,
      results: results,
      errors: errors,
      timestamp: new Date().toISOString()
    };
    
    console.log(`✅ Export completed: ${results.length} successful, ${errors.length} failed`);
    res.json(response);
    
  } catch (error) {
    console.error('Export error:', error);
    res.status(500).json({ 
      error: 'Export failed',
      details: error.message 
    });
  }
});

// Create individual Urbantz task
async function createUrbantzTask(delivery) {
  // This would be replaced with actual Urbantz API call
  const taskId = `URBANTZ-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  
  // Simulate task creation in Urbantz system
  const task = {
    taskId: taskId,
    customerRef: delivery.customerRef,
    deliveryAddress: delivery.deliveryAddress,
    serviceDate: delivery.serviceDate,
    timeWindowStart: delivery.timeWindowStart,
    timeWindowEnd: delivery.timeWindowEnd,
    items: delivery.items || [{ description: 'Pakket', quantity: 1, tempClass: 'ambient' }],
    notes: delivery.notes || '',
    status: 'pending',
    priority: delivery.priority || 'normal',
    createdAt: new Date().toISOString(),
    // Urbantz specific fields
    vehicleType: 'van',
    estimatedDuration: 30, // minutes
    specialInstructions: delivery.notes || '',
    contactPerson: {
      name: delivery.deliveryAddress.contactName,
      phone: delivery.deliveryAddress.contactPhone
    }
  };
  
  // Log the created task (in real implementation, this would be sent to Urbantz API)
  console.log(`✅ Created Urbantz task: ${taskId} for ${delivery.customerRef}`);
  
  return task;
}

// Smart AI analysis endpoint using Claude API
app.post('/api/smart-analyze', async (req, res) => {
  try {
    const { text, htmlContent, fileType } = req.body;
    
    console.log('\n' + '='.repeat(80));
    console.log('📥 SMART ANALYZE REQUEST RECEIVED');
    console.log('='.repeat(80));
    console.log('Text length:', text ? text.length : 0, 'chars');
    console.log('HTML content length:', htmlContent ? htmlContent.length : 0, 'chars');
    console.log('File type:', fileType);
    
    if (!text) {
      console.log('❌ No text provided');
      return res.status(400).json({ error: 'No text provided' });
    }
    
    console.log('\n📄 First 300 chars of text:');
    console.log(text.substring(0, 300));
    
    console.log('\n🔍 Analyzing text with Claude AI...');
    
    // If HTML content is provided and contains tables, parse it
    let processedText = text;
    if (htmlContent && htmlContent.includes('<table')) {
      console.log('🔍 HTML contains table, parsing...');
      const tableText = parseHTMLTables(htmlContent);
      if (tableText) {
        processedText = tableText + '\n\n' + text;
        console.log('✅ Parsed HTML tables successfully');
        console.log('📋 Parsed table text:');
        console.log(tableText);
      } else {
        console.log('⚠️ parseHTMLTables returned empty string');
      }
    } else {
      console.log('ℹ️ No HTML table found or no HTML content provided');
    }
    
    console.log('\n📤 Sending to Claude AI...');
    console.log('Processed text length:', processedText.length, 'chars');
    
    // Use Claude AI to intelligently extract delivery information
    const deliveries = await extractDeliveriesWithClaude(processedText);
    
    console.log('\n✅ Claude AI returned', deliveries.length, 'deliveries');
    console.log('Deliveries:', JSON.stringify(deliveries, null, 2));
    console.log('='.repeat(80) + '\n');
    
    res.json({
      success: true,
      confidence: deliveries.length > 0 ? 85 : 60,
      rawText: processedText,
      deliveries: deliveries,
      deliveryCount: deliveries.length,
      multipleDeliveries: deliveries.length > 1,
      aiPowered: true
    });
    
  } catch (error) {
    console.error('\n❌ SMART ANALYSIS ERROR:', error);
    console.error('Error stack:', error.stack);
    console.log('='.repeat(80) + '\n');
    res.status(500).json({ 
      error: 'Smart analysis failed',
      details: error.message 
    });
  }
});

// Helper function to parse HTML tables
function parseHTMLTables(html) {
  try {
    const tableRegex = /<table[^>]*>([\s\S]*?)<\/table>/gi;
    const tables = [];
    let match;
    
    while ((match = tableRegex.exec(html)) !== null) {
      const tableHTML = match[0];
      const rows = [];
      let headerRow = null;
      
      // Extract rows
      const rowRegex = /<tr[^>]*>([\s\S]*?)<\/tr>/gi;
      let rowMatch;
      let isFirstRow = true;
      
      while ((rowMatch = rowRegex.exec(tableHTML)) !== null) {
        const rowHTML = rowMatch[1];
        const cells = [];
        
        // Extract cells (th or td)
        const cellRegex = /<t[hd][^>]*>([\s\S]*?)<\/t[hd]>/gi;
        let cellMatch;
        
        while ((cellMatch = cellRegex.exec(rowHTML)) !== null) {
          const cellText = cellMatch[1].replace(/<[^>]*>/g, '').trim();
          cells.push(cellText);
        }
        
        if (cells.length > 0) {
          // First row with <th> tags is likely the header
          if (isFirstRow && rowHTML.includes('<th')) {
            headerRow = cells;
            rows.push('HEADER: ' + cells.join(' | '));
            isFirstRow = false;
          } else {
            // Mark data rows clearly
            rows.push('ROW: ' + cells.join(' | '));
            isFirstRow = false;
          }
        }
      }
      
      if (rows.length > 0) {
        tables.push('TABLE:\n' + rows.join('\n'));
      }
    }
    
    return tables.join('\n\n');
  } catch (error) {
    console.error('Error parsing HTML tables:', error);
    return '';
  }
}

// Document analysis endpoint with AI
app.post('/api/analyze-document-ai', upload.single('file'), async (req, res) => {
  try {
    const file = req.file;
    
    if (!file) {
      return res.status(400).json({ error: 'No file provided' });
    }
    
    console.log('📄 Analyzing document with AI:', file.originalname);
    
    let extractedText = '';
    
    // Handle PDF files
    if (file.mimetype === 'application/pdf') {
      try {
        // Try to use pdf-parse if available
        const pdfParse = require('pdf-parse');
        const dataBuffer = await fs.readFile(file.path);
        const data = await pdfParse(dataBuffer);
        extractedText = data.text;
        console.log('✅ Extracted text from PDF (' + extractedText.length + ' characters)');
        console.log('📄 First 200 chars:', extractedText.substring(0, 200) + '...');
        
        // Check if extracted text is meaningful
        if (extractedText.trim().length < 50) {
          console.log('⚠️ pdf-parse extracted very little text, trying Vision API...');
          throw new Error('Insufficient text extracted');
        }
        
      } catch (pdfError) {
        console.log('⚠️ pdf-parse error:', pdfError.message);
        console.log('📸 Falling back to Anthropic PDF vision...');
        
        // Fall back to Anthropic PDF vision
        const deliveries = await analyzePDFWithAnthropicVision(file.path, file.originalname);
        
        // Clean up uploaded file
        await fs.unlink(file.path);
        
        return res.json({
          success: true,
          confidence: 90,
          deliveries: deliveries,
          deliveryCount: deliveries.length,
          multipleDeliveries: deliveries.length > 1,
          fileName: file.originalname,
          method: 'anthropic-vision'
        });
      }
    } else {
      // For other file types, read as text
      extractedText = await fs.readFile(file.path, 'utf-8');
    }
    
    // Use Claude AI to extract deliveries
    const deliveries = await extractDeliveriesWithClaude(extractedText);
    
    // Clean up uploaded file
    await fs.unlink(file.path);
    
    res.json({
      success: true,
      confidence: 90,
      rawText: extractedText.substring(0, 500) + '...',
      deliveries: deliveries,
      deliveryCount: deliveries.length,
      multipleDeliveries: deliveries.length > 1,
      fileName: file.originalname,
      method: 'text-extraction'
    });
    
  } catch (error) {
    console.error('Document analysis error:', error);
    res.status(500).json({ 
      error: 'Document analysis failed',
      details: error.message 
    });
  }
});

// Legacy document analysis endpoint (kept for compatibility)
app.post('/api/analyze-document', upload.single('file'), async (req, res) => {
  try {
    const file = req.file;
    
    if (!file) {
      return res.status(400).json({ error: 'No file provided' });
    }
    
    console.log('📄 Analyzing document:', file.originalname);
    
    // Simulate OCR and AI analysis
    const mockText = `Levering informatie:
    
    Klant: CUST-12345
    Adres: Koningstraat 15, 1000 Brussel
    Contact: Jan Janssen (+32 2 123 4567)
    Datum: 2024-01-15
    Tijd: 09:00 - 12:00
    
    Items: 2x Pakketten, 1x Documenten`;
    
    const deliveries = await extractDeliveriesWithClaude(mockText);
    
    res.json({
      success: true,
      confidence: 90,
      rawText: mockText,
      deliveries: deliveries,
      deliveryCount: deliveries.length,
      multipleDeliveries: deliveries.length > 1,
      fileName: file.originalname
    });
    
  } catch (error) {
    console.error('Document analysis error:', error);
    res.status(500).json({ 
      error: 'Document analysis failed',
      details: error.message 
    });
  }
});

// Function to analyze PDF with Anthropic Vision API
async function analyzePDFWithAnthropicVision(filePath, fileName) {
  const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
  
  if (!ANTHROPIC_API_KEY) {
    throw new Error('ANTHROPIC_API_KEY niet gevonden in .env file');
  }
  
  try {
    // Convert PDF to PNG image (first page)
    console.log('🖼️ Converting PDF to PNG...');
    const { pdfToPng } = require('pdf-to-png-converter');
    
    const pngPages = await pdfToPng(filePath, {
      disableFontFace: false,
      useSystemFonts: true,  // Enable system fonts for better text rendering
      viewportScale: 3.0,    // Higher scale for better text clarity
      outputFolder: 'uploads',
      outputFileMask: 'page',
      pagesToProcess: [1],   // Only first page
      strict: false,         // Don't fail on font issues
      verbosityLevel: 0      // Reduce verbosity
    });
    
    if (!pngPages || pngPages.length === 0) {
      throw new Error('Could not convert PDF to PNG');
    }
    
    // Get the PNG buffer from first page
    const pngBuffer = pngPages[0].content;
    const base64PNG = pngBuffer.toString('base64');
    
    console.log('✅ PDF converted to PNG');
    console.log('📤 Sending PNG to Anthropic Vision API...');
    
    const prompt = `
Je bent een expert in het analyseren van leveringsdocumenten en PDF's, SPECIAAL TABELLEN.

Je krijgt nu een PDF document als afbeelding. Dit document bevat waarschijnlijk een TABEL met leveringen.

LET OP: Als je een TABEL ziet met kolommen zoals:
- REF / Referentie nummer
- Klant / Bedrijfsnaam  
- Adres / Locatie
- Tijd / Tijdslot / Uur
- Nummer / Telefoon / Contact

Dan is ELKE RIJ in de tabel = 1 LEVERING!

BELANGRIJK: 
- Negeer de HEADER rij (kolom namen)
- Elke DATA rij = 1 aparte levering
- Als er 10 rijen data zijn → 10 leveringen
- Als er 20 rijen data zijn → 20 leveringen

Voor elke levering (elke rij), extraheer:
- customerRef: Waarde uit REF kolom (bijv. ORD-ANT2801, ORD-BRU2802)
- deliveryAddress:
  - line1: Waarde uit Adres kolom (volledig adres)
  - contactName: Waarde uit Klant kolom (bedrijfsnaam)
  - contactPhone: Waarde uit Nummer kolom (telefoonnummer)
- serviceDate: Datum uit document titel of header (YYYY-MM-DD formaat, bijv. "28 oktober 2025" → "2025-10-28")
- timeWindowStart: Begin tijd uit Tijd kolom (bijv. "07:00" uit "07:00 - 09:00")
- timeWindowEnd: Eind tijd uit Tijd kolom (bijv. "09:00" uit "07:00 - 09:00")
- items: [{"description": "Standaard levering", "quantity": 1, "tempClass": "ambient"}]
- notes: Extra info indien aanwezig
- priority: "normal"

VOORBEELD:
Als je deze tabel ziet:
| REF | Klant | Adres | Tijd | Nummer |
| ORD-ANT2801 | Bistro Nova | Lange Koepoortstraat 23, 2000 Antwerpen | 07:00 – 09:00 | +32 470 81 32 40 |
| ORD-BRU2802 | Maison Blanche | Rue du Marché 12, 1000 Brussel | 08:15 – 10:30 | +32 491 27 84 66 |

Dan moet je 2 leveringen maken:
[
  {
    "customerRef": "ORD-ANT2801",
    "deliveryAddress": {
      "line1": "Lange Koepoortstraat 23, 2000 Antwerpen",
      "contactName": "Bistro Nova",
      "contactPhone": "+32 470 81 32 40"
    },
    "serviceDate": "2025-10-28",
    "timeWindowStart": "07:00",
    "timeWindowEnd": "09:00",
    "items": [{"description": "Standaard levering", "quantity": 1, "tempClass": "ambient"}],
    "notes": "",
    "priority": "normal"
  },
  {
    "customerRef": "ORD-BRU2802",
    "deliveryAddress": {
      "line1": "Rue du Marché 12, 1000 Brussel",
      "contactName": "Maison Blanche",
      "contactPhone": "+32 491 27 84 66"
    },
    "serviceDate": "2025-10-28",
    "timeWindowStart": "08:15",
    "timeWindowEnd": "10:30",
    "items": [{"description": "Standaard levering", "quantity": 1, "tempClass": "ambient"}],
    "notes": "",
    "priority": "normal"
  }
]

Analyseer nu het PDF document en geef een JSON array terug met ALLE leveringen.
BELANGRIJK: Gebruik de EXACTE tekst die je in het document ziet - vertaal NIETS!
- Als er "서울특별시 강남구" staat, gebruik dat
- Als er "주식회사 세진" staat, gebruik dat  
- Als er "Green Pantry" staat, gebruik dat
- Behoud de originele taal en tekens

Geef ALLEEN de JSON array terug, geen uitleg, geen markdown code fences.
`;

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': ANTHROPIC_API_KEY,
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-3-5-sonnet-20241022',  // Use the latest Sonnet model for better vision
        max_tokens: 8000,  // Increase token limit for better responses
        messages: [
          {
            role: 'user',
            content: [
              {
                type: 'image',
                source: {
                  type: 'base64',
                  media_type: 'image/png',
                  data: base64PNG
                }
              },
              {
                type: 'text',
                text: prompt
              }
            ]
          }
        ]
      })
    });
    
    if (!response.ok) {
      const errorBody = await response.text();
      throw new Error(`Anthropic API error: ${response.status} ${response.statusText} - ${errorBody}`);
    }
    
    const result = await response.json();
    
    console.log('🔍 Anthropic Vision API Response:', JSON.stringify(result, null, 2));
    
    if (result.content && result.content[0]) {
      let aiResponse = result.content[0].text;
      
      console.log('📝 Raw AI Response:', aiResponse);
      
      // Remove code fences if present
      aiResponse = aiResponse.replace(/```json\s*/g, '').replace(/```\s*/g, '').trim();
      
      console.log('🧹 Cleaned AI Response:', aiResponse);
      
      const deliveries = JSON.parse(aiResponse);
      console.log(`✅ Anthropic Vision extracted ${Array.isArray(deliveries) ? deliveries.length : 1} delivery(ies) from PDF`);
      console.log('📋 Extracted deliveries:', JSON.stringify(deliveries, null, 2));
      return Array.isArray(deliveries) ? deliveries : [deliveries];
    }
    
    throw new Error('Anthropic API gaf geen bruikbaar antwoord terug.');
    
  } catch (error) {
    console.error('Anthropic Vision API error:', error);
    throw error;
  }
}

// AI-powered delivery extraction using Claude API
async function extractDeliveriesWithClaude(text) {
  const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
  
  if (!ANTHROPIC_API_KEY) {
    throw new Error('ANTHROPIC_API_KEY niet gevonden in .env file. De AI scan functie vereist een geldige API key.');
  }
  
  try {
    const prompt = `
Je bent een expert in het analyseren van leveringsdocumenten, emails en VOORAL TABELLEN. 

=== STAP 1: ANALYSE VAN HET DOCUMENT ===
Analyseer eerst het document en bepaal:
1. Wat is het FORMAT? (TABEL, genummerde lijst, paragrafen, enkele levering, etc.)
2. Hoeveel LEVERINGEN zijn er? (tel zorgvuldig alle aparte leveringen)
3. Hoe is de DATA GESTRUCTUREERD? (kolommen, bullets, tekst)

⚠️ BELANGRIJK: Als je een TABEL ziet:
- Elke RIJ (behalve header) = 1 APARTE LEVERING!
- 10 rijen data = 10 leveringen
- 20 rijen data = 20 leveringen
- Negeer de header rij!

=== VOORBEELDEN VAN VERSCHILLENDE FORMATEN ===

VOORBEELD A - TABEL FORMAT (meerdere leveringen) ⭐ BELANGRIJK!
\`\`\`
| REF | Klant | Adres | Tijd | Nummer |
| ORD-ANT2801 | Bistro Nova | Lange Koepoortstraat 23, 2000 Antwerpen | 07:00 – 09:00 | +32 470 81 32 40 |
| ORD-BRU2802 | Maison Blanche | Rue du Marché 12, 1000 Brussel | 08:15 – 10:30 | +32 491 27 84 66 |
| ORD-GEN2803 | De Smaakfabriek | Hoogpoort 101, 9000 Gent | 09:00 – 11:15 | +32 472 69 10 58 |
\`\`\`
→ Format: TABEL
→ Aantal leveringen: 3 (één per data rij, header niet meetellen!)
→ Output: Array met 3 objecten

TABEL KOLOM MAPPING:
- REF kolom → customerRef
- Klant kolom → deliveryAddress.contactName
- Adres kolom → deliveryAddress.line1
- Tijd kolom → timeWindowStart en timeWindowEnd (split op " – " of " - ")
- Nummer kolom → deliveryAddress.contactPhone

VOORBEELD B - GENUMMERDE LIJST (meerdere leveringen):
\`\`\`
1. REF: ORD-001
   Klant: Bakkerij Jan
   Adres: Hoofdstraat 1, Brussel
   Tijd: 08:00 - 10:00

2. REF: ORD-002
   Klant: Café Marie
   Adres: Kerkstraat 5, Antwerpen
   Tijd: 09:00 - 11:00
\`\`\`
→ Format: GENUMMERDE LIJST
→ Aantal leveringen: 2 (één per nummer)
→ Output: Array met 2 objecten

VOORBEELD C - ENKELE LEVERING (één levering):
\`\`\`
Levering: BXL2501
Adres: Fleur du Jour, Vlaanderenstraat 16, 9000 Gent
Contact: +32 497 30 52 10
Tijd: 10:00 - 13:00
\`\`\`
→ Format: ENKELE LEVERING
→ Aantal leveringen: 1
→ Output: Array met 1 object

=== STAP 2: EXTRACTIE REGELS ===

Voor TABEL format: ⭐
- HEADER rij = kolom namen (bijv. REF, Klant, Adres, Tijd, Nummer) → NEGEER DEZE!
- Elke DATA RIJ daarna = 1 levering
- Map kolommen naar velden:
  * REF/Referentie kolom → customerRef
  * Klant/Naam kolom → deliveryAddress.contactName
  * Adres kolom → deliveryAddress.line1
  * Tijd/Tijdslot kolom → timeWindowStart + timeWindowEnd
  * Nummer/Telefoon kolom → deliveryAddress.contactPhone

Voor GENUMMERDE LIJST:
- Elk genummerd item = 1 levering
- Extraheer velden uit elk item

Voor ENKELE LEVERING:
- Alle info behoort tot 1 levering
- Extraheer alle beschikbare velden

Voor PARAGRAFEN/VRIJE TEKST:
- Zoek naar scheiding tussen leveringen (nummering, witruimte, "levering X", etc.)
- Elke aparte levering sectie = 1 levering

=== STAP 3: VELD EXTRACTIE ===
Voor elke levering:
- customerRef: Referentie nummer (ORD-XXX, REF:, etc.)
- deliveryAddress:
  - line1: Volledig adres (straat, nummer, postcode, stad)
  - contactName: Naam klant/bedrijf
  - contactPhone: Telefoonnummer
- serviceDate: Leverdatum in YYYY-MM-DD (haal uit document titel/header, bijv. "28 oktober 2025" → "2025-10-28")
- timeWindowStart: Start tijd (HH:MM format, bijv. "07:00" uit "07:00 - 09:00")
- timeWindowEnd: Eind tijd (HH:MM format, bijv. "09:00" uit "07:00 - 09:00")
- items: [{"description": "Standaard levering", "quantity": 1, "tempClass": "ambient"}]
- notes: Relevante extra info
- priority: "normal" (tenzij urgent/spoed vermeld)

⚠️ LET OP BIJ TIJD PARSING:
- "07:00 – 09:00" → start: "07:00", end: "09:00"
- "08:15 – 10:30" → start: "08:15", end: "10:30"
- Let op de streepjes: " – " of " - " of "-"

=== TEKST OM TE ANALYSEREN ===
${text}

=== OUTPUT FORMAT ===
Denk eerst na over:
1. Wat is het format? (Is het een TABEL? Zo ja, tel de rijen!)
2. Hoeveel leveringen zijn er? (Tel elke data rij als aparte levering)
3. Hoe extraheer ik de data? (Map tabel kolommen naar JSON velden)

Geef dan een JSON array terug met EXACT het aantal leveringen dat je hebt gevonden.
- Als het een tabel is met 10 DATA rijen (+ 1 header) → 10 leveringen
- Als het een lijst is met 5 items → 5 leveringen  
- Als het 1 enkele levering is → 1 levering

VOORBEELD OUTPUT voor een tabel met 3 leveringen:
[
  {
    "customerRef": "ORD-ANT2801",
    "deliveryAddress": {
      "line1": "Lange Koepoortstraat 23, 2000 Antwerpen",
      "contactName": "Bistro Nova",
      "contactPhone": "+32 470 81 32 40"
    },
    "serviceDate": "2025-10-28",
    "timeWindowStart": "07:00",
    "timeWindowEnd": "09:00",
    "items": [{"description": "Standaard levering", "quantity": 1, "tempClass": "ambient"}],
    "notes": "",
    "priority": "normal"
  },
  ... (2 more objects)
]

Geef ALLEEN de JSON array terug, geen uitleg, geen markdown code fences.
`;

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': ANTHROPIC_API_KEY,
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-3-haiku-20240307',
        max_tokens: 4096,
        messages: [
          {
            role: 'user',
            content: prompt
          }
        ]
      })
    });
    
    if (!response.ok) {
      const errorBody = await response.text();
      throw new Error(`Claude API error: ${response.status} ${response.statusText} - ${errorBody}`);
    }
    
    const result = await response.json();
    
    if (result.content && result.content[0]) {
      let aiResponse = result.content[0].text;
      
      try {
        // Remove code fences if present (```json ... ```)
        aiResponse = aiResponse.replace(/```json\s*/g, '').replace(/```\s*/g, '').trim();
        
        // Parse AI response as JSON
        const deliveries = JSON.parse(aiResponse);
        console.log(`✅ Claude AI extracted ${Array.isArray(deliveries) ? deliveries.length : 1} delivery(ies)`);
        return Array.isArray(deliveries) ? deliveries : [deliveries];
      } catch (parseError) {
        console.error('Failed to parse Claude response:', parseError);
        console.log('Claude response:', aiResponse);
        throw new Error('Claude API gaf een ongeldig antwoord. Kon leveringen niet parsen.');
      }
    }
    
    throw new Error('Claude API gaf geen bruikbaar antwoord terug.');
    
  } catch (error) {
    console.error('Claude API error:', error);
    throw error;
  }
}

// Fallback pattern matching function
async function extractDeliveriesWithPatterns(text) {
  const deliveries = [];
  
  // Smart section detection
  const sections = detectDeliverySections(text);
  
  sections.forEach((section, index) => {
    const delivery = {
      taskId: `TASK-${Date.now()}-${index + 1}`,
      customerRef: extractSmartCustomerRef(section),
      deliveryAddress: extractSmartAddress(section),
      serviceDate: extractSmartDate(section),
      timeWindowStart: extractSmartTimeStart(section),
      timeWindowEnd: extractSmartTimeEnd(section),
      items: extractSmartItems(section),
      notes: `Geëxtraheerd uit sectie ${index + 1}`,
      priority: determinePriority(section, index)
    };
    
    // Only add if meaningful data found
    if (delivery.customerRef || delivery.deliveryAddress.line1) {
      deliveries.push(delivery);
    }
  });
  
  return deliveries;
}

function detectDeliverySections(text) {
  // Look for clear section separators
  const sectionPatterns = [
    /(?:lever|delivery|adres|address|klant|customer|order|bestelling)[\s\S]*?(?=(?:lever|delivery|adres|address|klant|customer|order|bestelling)|$)/gi,
    /(?:lever|delivery)[\s\S]*?(?=(?:lever|delivery)|$)/gi
  ];
  
  const sections = [];
  
  for (const pattern of sectionPatterns) {
    const matches = text.match(pattern);
    if (matches) {
      sections.push(...matches);
    }
  }
  
  // If no clear sections, try to split by paragraphs
  if (sections.length === 0) {
    const paragraphs = text.split(/\n\s*\n/);
    sections.push(...paragraphs.filter(p => p.trim().length > 50));
  }
  
  return sections.length > 0 ? sections : [text];
}

function extractSmartCustomerRef(section) {
  const patterns = [
    /(?:klant|customer|ref|referentie|order|bestelling)[\s:]*([A-Z0-9-]+)/i,
    /([A-Z]{2,}\d{3,})/g,
    /(?:nr|nummer|number)[\s:]*([A-Z0-9-]+)/i
  ];
  
  for (const pattern of patterns) {
    const match = section.match(pattern);
    if (match && match[1]) return match[1].trim();
  }
  
  return `AUTO-${Math.floor(Math.random() * 1000)}`;
}

function extractSmartAddress(section) {
  const addressPatterns = [
    /(?:adres|address|leveradres|bezorgadres)[\s:]*([^\n\r]+(?:\n[^\n\r]+)*)/i,
    /([A-Za-z\s]+(?:straat|street|laan|avenue|plein|square|weg|road)\s+\d+[^\n\r]*)/i,
    /([A-Za-z\s]+\d+[A-Za-z]?\s*,\s*\d{4}\s+[A-Za-z\s]+)/i
  ];
  
  for (const pattern of addressPatterns) {
    const match = section.match(pattern);
    if (match && match[1]) {
      const address = match[1].trim();
      return {
        line1: address,
        contactName: extractContactName(section),
        contactPhone: extractPhone(section)
      };
    }
  }
  
  return {
    line1: "Adres niet gevonden",
    contactName: "Onbekend",
    contactPhone: "+32 000 000 000"
  };
}

function extractContactName(section) {
  const patterns = [
    /(?:contact|naam|name|contactpersoon)[\s:]*([A-Za-z\s]+)/i,
    /([A-Z][a-z]+\s+[A-Z][a-z]+)/g
  ];
  
  for (const pattern of patterns) {
    const match = section.match(pattern);
    if (match && match[1]) return match[1].trim();
  }
  
  return "Contact persoon";
}

function extractPhone(section) {
  const phonePatterns = [
    /(\+32\s?\d{2,3}\s?\d{2,3}\s?\d{2,3})/g,
    /(0\d{2,3}\s?\d{2,3}\s?\d{2,3})/g
  ];
  
  for (const pattern of phonePatterns) {
    const match = section.match(pattern);
    if (match && match[0]) return match[0];
  }
  
  return "+32 000 000 000";
}

function extractSmartDate(section) {
  const datePatterns = [
    /(?:datum|date|leverdatum|bezorgdatum)[\s:]*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})/i,
    /(\d{4}-\d{2}-\d{2})/,
    /(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})/
  ];
  
  for (const pattern of datePatterns) {
    const match = section.match(pattern);
    if (match && match[1]) {
      let date = match[1];
      // Convert to ISO format
      if (date.includes('/')) {
        const parts = date.split('/');
        if (parts[2].length === 2) {
          parts[2] = '20' + parts[2];
        }
        date = `${parts[2]}-${parts[1].padStart(2, '0')}-${parts[0].padStart(2, '0')}`;
      }
      return date;
    }
  }
  
  // Default to tomorrow
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  return tomorrow.toISOString().split('T')[0];
}

function extractSmartTimeStart(section) {
  const timePatterns = [
    /(?:tijd|time|tussen|van)[\s:]*(\d{1,2}:\d{2})/i,
    /(\d{1,2}:\d{2})\s*(?:tot|-)/i
  ];
  
  for (const pattern of timePatterns) {
    const match = section.match(pattern);
    if (match && match[1]) return match[1];
  }
  
  return "09:00";
}

function extractSmartTimeEnd(section) {
  const timePatterns = [
    /(?:tot|until|tot)[\s:]*(\d{1,2}:\d{2})/i,
    /(\d{1,2}:\d{2})\s*(?:einde|end)/i
  ];
  
  for (const pattern of timePatterns) {
    const match = section.match(pattern);
    if (match && match[1]) return match[1];
  }
  
  return "17:00";
}

function extractSmartItems(section) {
  const items = [];
  
  const itemPatterns = [
    /(?:items|pakketten|producten|artikelen)[\s:]*([^\n\r]+)/i,
    /(\d+\s*(?:x|stuks?|pakketten?|items?))/gi,
    /([A-Za-z\s]+\s*\d+)/g
  ];
  
  for (const pattern of itemPatterns) {
    const matches = section.match(pattern);
    if (matches) {
      matches.forEach(match => {
        items.push({
          description: match.trim(),
          quantity: 1,
          tempClass: "ambient"
        });
      });
    }
  }
  
  if (items.length === 0) {
    items.push({
      description: "Pakket uit document",
      quantity: 1,
      tempClass: "ambient"
    });
  }
  
  return items;
}

function determinePriority(section, index) {
  const highPriorityKeywords = ['urgent', 'spoed', 'priority', 'hoog', 'asap'];
  const lowPriorityKeywords = ['laag', 'low', 'niet urgent'];
  
  const text = section.toLowerCase();
  
  for (const keyword of highPriorityKeywords) {
    if (text.includes(keyword)) return 'high';
  }
  
  for (const keyword of lowPriorityKeywords) {
    if (text.includes(keyword)) return 'low';
  }
  
  return index === 0 ? 'high' : 'normal';
}

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`🚀 Local server running at http://localhost:${PORT}`);
  console.log(`📱 Open your browser and test the Urbantz API interface!`);
  console.log(`🔧 API endpoint: http://localhost:${PORT}/api/urbantz`);
});
