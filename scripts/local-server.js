const express = require('express');
const path = require('path');
const cors = require('cors');
const multer = require('multer');
require('dotenv').config();

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
    
    if (!text) {
      return res.status(400).json({ error: 'No text provided' });
    }
    
    console.log('🔍 Analyzing text with Claude AI...');
    
    // If HTML content is provided and contains tables, parse it
    let processedText = text;
    if (htmlContent && htmlContent.includes('<table')) {
      const tableText = parseHTMLTables(htmlContent);
      if (tableText) {
        processedText = tableText + '\n\n' + text;
        console.log('📋 Parsed HTML tables');
      }
    }
    
    // Use Claude AI to intelligently extract delivery information
    const deliveries = await extractDeliveriesWithClaude(processedText);
    
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
    console.error('Smart analysis error:', error);
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

// Document analysis endpoint
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

// AI-powered delivery extraction using Claude API
async function extractDeliveriesWithClaude(text) {
  const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
  
  if (!ANTHROPIC_API_KEY) {
    console.warn('⚠️ ANTHROPIC_API_KEY not found, falling back to pattern matching');
    return extractDeliveriesWithPatterns(text);
  }
  
  try {
    const prompt = `
Je bent een expert in het analyseren van leveringsdocumenten, emails en tabellen. 

=== STAP 1: ANALYSE VAN HET DOCUMENT ===
Analyseer eerst het document en bepaal:
1. Wat is het FORMAT? (tabel, genummerde lijst, paragrafen, enkele levering, etc.)
2. Hoeveel LEVERINGEN zijn er? (tel zorgvuldig alle aparte leveringen)
3. Hoe is de DATA GESTRUCTUREERD? (kolommen, bullets, tekst)

=== VOORBEELDEN VAN VERSCHILLENDE FORMATEN ===

VOORBEELD A - TABEL FORMAT (meerdere leveringen):
\`\`\`
| Ref | Klant | Adres | Tijdslot | Contact |
| ORD-001 | Bakkerij Jan | Hoofdstraat 1, Brussel | 08:00–10:00 | +32 2 123 45 67 |
| ORD-002 | Café Marie | Kerkstraat 5, Antwerpen | 09:00–11:00 | +32 3 234 56 78 |
\`\`\`
→ Format: TABEL
→ Aantal leveringen: 2 (één per rij)
→ Output: Array met 2 objecten

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

Voor TABEL format:
- Elke DATA RIJ (niet de header) = 1 levering
- Map kolommen naar velden (Ref→customerRef, Klant→contactName, etc.)

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
- serviceDate: Leverdatum in YYYY-MM-DD (haal uit email tekst, gebruik voor alle leveringen)
- timeWindowStart: Start tijd (HH:MM)
- timeWindowEnd: Eind tijd (HH:MM)
- items: [{"description": "Standaard levering", "quantity": 1, "tempClass": "ambient"}]
- notes: Relevante extra info
- priority: "normal" (tenzij urgent/spoed vermeld)

=== TEKST OM TE ANALYSEREN ===
${text}

=== OUTPUT FORMAT ===
Denk eerst na over:
1. Wat is het format?
2. Hoeveel leveringen zijn er?
3. Hoe extraheer ik de data?

Geef dan een JSON array terug met EXACT het aantal leveringen dat je hebt gevonden.
- Als het een tabel is met 10 rijen → 10 leveringen
- Als het een lijst is met 5 items → 5 leveringen  
- Als het 1 enkele levering is → 1 levering

Geef ALLEEN de JSON array terug, geen uitleg.
`;

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': ANTHROPIC_API_KEY,
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 8000,
        messages: [
          {
            role: 'user',
            content: prompt
          }
        ]
      })
    });
    
    if (!response.ok) {
      throw new Error(`Claude API error: ${response.status} ${response.statusText}`);
    }
    
    const result = await response.json();
    
    if (result.content && result.content[0]) {
      const aiResponse = result.content[0].text;
      
      try {
        // Parse AI response as JSON
        const deliveries = JSON.parse(aiResponse);
        console.log(`✅ Claude AI extracted ${Array.isArray(deliveries) ? deliveries.length : 1} delivery(ies)`);
        return Array.isArray(deliveries) ? deliveries : [deliveries];
      } catch (parseError) {
        console.error('Failed to parse Claude response:', parseError);
        console.log('Claude response:', aiResponse);
        return extractDeliveriesWithPatterns(text);
      }
    }
    
    return extractDeliveriesWithPatterns(text);
    
  } catch (error) {
    console.error('Claude API error:', error);
    return extractDeliveriesWithPatterns(text);
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
    if (match) return match[1].trim();
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
    if (match) {
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
    if (match) return match[1].trim();
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
    if (match) return match[0];
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
    if (match) {
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
    if (match) return match[1];
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
    if (match) return match[1];
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
