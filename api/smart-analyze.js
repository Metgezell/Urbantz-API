// Smart document analysis using AI for context understanding
export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }
  
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  try {
    const { text, htmlContent, fileType } = req.body;
    
    if (!text) {
      return res.status(400).json({ error: 'No text provided' });
    }
    
    // If HTML content is provided and contains tables, parse it
    let processedText = text;
    if (htmlContent && htmlContent.includes('<table')) {
      processedText = parseHTMLTables(htmlContent) + '\n\n' + text;
    }
    
    // Use AI to intelligently extract delivery information
    const deliveries = await extractDeliveriesWithAI(processedText);
    
    res.status(200).json({
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
}

function parseHTMLTables(html) {
  // Enhanced HTML table parser for delivery data
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

async function extractDeliveriesWithAI(text) {
  const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
  
  if (!ANTHROPIC_API_KEY) {
    // Fallback to smart pattern matching
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

🚨 KRITIEKE VALIDATIE:
- Als de tekst GEEN leveringsdata bevat (zoals "test", "hello", random tekst), geef dan een lege array terug: []
- Als de tekst GEEN herkenbare leveringsinformatie heeft (adressen, referenties, tijden), geef dan een lege array terug: []
- Genereer NOOIT fictieve leveringen als er geen echte data is!
- Alleen extraheer data die daadwerkelijk in de tekst staat!

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

🚨 VALIDATIE VOOR OUTPUT:
- Als er GEEN leveringsdata gevonden wordt → geef een lege array terug: []
- Als er alleen test/random tekst staat → geef een lege array terug: []
- Alleen als er ECHTE leveringsdata is → extraheer de data

Geef dan een JSON array terug met EXACT het aantal leveringen dat je hebt gevonden.
- Als het een tabel is met 10 rijen → 10 leveringen
- Als het een lijst is met 5 items → 5 leveringen  
- Als het 1 enkele levering is → 1 levering
- Als er GEEN leveringsdata is → []

BELANGRIJK: Gebruik de EXACTE tekst uit het document - vertaal NIETS!
- Behoud originele talen (Nederlands, Engels, Duits, Frans, etc.)
- Gebruik exacte bedrijfsnamen zoals ze in het document staan
- Behoud originele adressen en telefoonnummers

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
    
    const result = await response.json();
    
    if (result.content && result.content[0]) {
      const aiResponse = result.content[0].text;
      
      try {
        // Parse AI response as JSON
        const deliveries = JSON.parse(aiResponse);
        return Array.isArray(deliveries) ? deliveries : [deliveries];
      } catch (parseError) {
        console.error('Failed to parse Claude response:', parseError);
        return extractDeliveriesWithPatterns(text);
      }
    }
    
    return extractDeliveriesWithPatterns(text);
    
  } catch (error) {
    console.error('Anthropic Claude API error:', error);
    return extractDeliveriesWithPatterns(text);
  }
}

function extractDeliveriesWithPatterns(text) {
  // 🚨 KRITIEKE VALIDATIE: Geen fictieve data voor ongeldige input
  if (!text || text.trim().length < 10) {
    return [];
  }
  
  // Check if text contains actual delivery-related keywords
  const deliveryKeywords = ['levering', 'delivery', 'adres', 'address', 'klant', 'customer', 'order', 'bestelling', 'tijd', 'time', 'contact', 'telefoon', 'phone'];
  const hasDeliveryKeywords = deliveryKeywords.some(keyword => 
    text.toLowerCase().includes(keyword.toLowerCase())
  );
  
  if (!hasDeliveryKeywords) {
    return [];
  }
  
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
  const sections = [];
  
  // First try to detect numbered deliveries (1. REF:, 2. REF:, etc.)
  const numberedDeliveryRegex = /(\d+\.\s+REF:\s+[A-Z0-9-]+[\s\S]*?(?=\d+\.\s+REF:|$))/g;
  const numberedMatches = text.match(numberedDeliveryRegex);
  
  if (numberedMatches && numberedMatches.length > 0) {
    sections.push(...numberedMatches);
    return sections;
  }
  
  // Look for clear section separators
  const sectionPatterns = [
    /(?:lever|delivery|adres|address|klant|customer|order|bestelling)[\s\S]*?(?=(?:lever|delivery|adres|address|klant|customer|order|bestelling)|$)/gi,
    /(?:lever|delivery)[\s\S]*?(?=(?:lever|delivery)|$)/gi
  ];
  
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
    /REF:\s*([A-Z0-9-]+)/i,  // Match "REF: TEST-REF-123" format
    /(?:klant|customer|ref|referentie|order|bestelling)[\s:]*([A-Z0-9-]+)/i,
    /([A-Z]{2,}\d{3,})/g,
    /(?:nr|nummer|number)[\s:]*([A-Z0-9-]+)/i
  ];
  
  for (const pattern of patterns) {
    const match = section.match(pattern);
    if (match) return match[1].trim();
  }
  
  // 🚨 Geen automatische referentie generatie meer!
  return null;
}

function extractSmartAddress(section) {
  // Look for address patterns with context
  const addressPatterns = [
    /Adres:\s*([^\n\r]+)/i,  // Match "Adres: Rue de Test 10, Brussel 1000" format
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
    /Klant:\s*([^\n\r]+)/i,  // Match "Klant: Maison Vert" format
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
    /Nummer:\s*(\+32\s?\d{2,3}\s?\d{2,3}\s?\d{2,3})/i,  // Match "Nummer: +32 470 11 22 33" format
    /(\+32\s?\d{2,3}\s?\d{2,3}\s?\d{2,3})/g,
    /(0\d{2,3}\s?\d{2,3}\s?\d{2,3})/g
  ];
  
  for (const pattern of phonePatterns) {
    const match = section.match(pattern);
    if (match) return match[1] || match[0];  // Use group 1 if available, otherwise match 0
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
  
  // Look for date in mail header (e.g., "11 oktober 2025")
  const dutchDateMatch = section.match(/(\d{1,2})\s+(januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december)\s+(\d{4})/i);
  if (dutchDateMatch) {
    const day = dutchDateMatch[1].padStart(2, '0');
    const year = dutchDateMatch[3];
    const monthMap = {
      'januari': '01', 'februari': '02', 'maart': '03', 'april': '04',
      'mei': '05', 'juni': '06', 'juli': '07', 'augustus': '08',
      'september': '09', 'oktober': '10', 'november': '11', 'december': '12'
    };
    const month = monthMap[dutchDateMatch[2].toLowerCase()] || '01';
    return `${year}-${month}-${day}`;
  }
  
  // Default to tomorrow
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  return tomorrow.toISOString().split('T')[0];
}

function extractSmartTimeStart(section) {
  const timePatterns = [
    /Tijd:\s*(\d{1,2}:\d{2})\s*(?:-|tot)/i,  // Match "Tijd: 09:00 - 12:00" format
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
    /Tijd:\s*\d{1,2}:\d{2}\s*(?:-|tot)\s*(\d{1,2}:\d{2})/i,  // Match "Tijd: 09:00 - 12:00" format
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
  
  // Look for item patterns
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
