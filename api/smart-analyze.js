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
    const { text, fileType } = req.body;
    
    if (!text) {
      return res.status(400).json({ error: 'No text provided' });
    }
    
    // Use AI to intelligently extract delivery information
    const deliveries = await extractDeliveriesWithAI(text);
    
    res.status(200).json({
      success: true,
      confidence: deliveries.length > 0 ? 85 : 60,
      rawText: text,
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

async function extractDeliveriesWithAI(text) {
  const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
  
  if (!ANTHROPIC_API_KEY) {
    // Fallback to smart pattern matching
    return extractDeliveriesWithPatterns(text);
  }
  
  try {
    const prompt = `
Analyseer de volgende tekst en extraheer alle leveringsinformatie. 
Identificeer elke levering als een aparte taak met de volgende structuur:

Voor elke levering, extraheer:
- customerRef: Klant referentie (bijv. CUST-123, ORDER-456)
- deliveryAddress: Volledig adres met contact informatie
- serviceDate: Leverdatum (YYYY-MM-DD formaat)
- timeWindowStart: Starttijd (HH:MM formaat)
- timeWindowEnd: Eindtijd (HH:MM formaat)  
- items: Array van items met description, quantity, tempClass
- notes: Relevante notities
- priority: "high", "normal", of "low"

Tekst om te analyseren:
${text}

Geef het antwoord terug als JSON array van leveringen. Als er geen leveringen gevonden worden, geef een lege array terug.
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
        max_tokens: 4000,
        messages: [
          {
            role: 'user',
            content: `Je bent een expert in het analyseren van leveringsdocumenten. Extraheer altijd gestructureerde JSON data.\n\n${prompt}`
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
  // Look for address patterns with context
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
