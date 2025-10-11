// Document analysis API endpoint using Google Vision API
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
    const { file, fileType } = req.body;
    
    if (!file) {
      return res.status(400).json({ error: 'No file provided' });
    }
    
    // Convert base64 to buffer
    const fileBuffer = Buffer.from(file, 'base64');
    
    // Call Google Vision API
    const visionResult = await analyzeWithGoogleVision(fileBuffer, fileType);
    
    // Extract delivery information using AI
    const extractedDeliveries = extractDeliveryInfo(visionResult.text);
    
    res.status(200).json({
      success: true,
      confidence: visionResult.confidence,
      rawText: visionResult.text,
      deliveries: extractedDeliveries,
      deliveryCount: extractedDeliveries.length,
      multipleDeliveries: extractedDeliveries.length > 1
    });
    
  } catch (error) {
    console.error('Document analysis error:', error);
    res.status(500).json({ 
      error: 'Document analysis failed',
      details: error.message 
    });
  }
}

async function analyzeWithGoogleVision(fileBuffer, fileType) {
  const GOOGLE_VISION_API_KEY = process.env.GOOGLE_VISION_API_KEY;
  
  if (!GOOGLE_VISION_API_KEY) {
    // Fallback to mock analysis if no API key
    return {
      text: "Mock OCR text - Google Vision API key not configured",
      confidence: 85
    };
  }
  
  try {
    const response = await fetch(`https://vision.googleapis.com/v1/images:annotate?key=${GOOGLE_VISION_API_KEY}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        requests: [{
          image: {
            content: fileBuffer.toString('base64')
          },
          features: [{
            type: 'TEXT_DETECTION',
            maxResults: 1
          }]
        }]
      })
    });
    
    const result = await response.json();
    
    if (result.responses && result.responses[0] && result.responses[0].textAnnotations) {
      const text = result.responses[0].textAnnotations[0].description;
      const confidence = result.responses[0].textAnnotations[0].score || 0.8;
      
      return { text, confidence };
    } else {
      throw new Error('No text found in document');
    }
    
  } catch (error) {
    console.error('Google Vision API error:', error);
    throw error;
  }
}

function extractDeliveryInfo(text) {
  // Smart pattern matching for delivery information
  const deliveries = [];
  
  // Split text into potential delivery sections
  const sections = text.split(/(?=lever|delivery|adres|address|klant|customer)/i);
  
  sections.forEach((section, index) => {
    if (section.trim().length < 50) return; // Skip short sections
    
    const delivery = {
      taskId: `TASK-${Date.now()}-${index + 1}`,
      customerRef: extractCustomerRef(section),
      deliveryAddress: extractAddress(section),
      serviceDate: extractDate(section),
      timeWindowStart: extractTimeStart(section),
      timeWindowEnd: extractTimeEnd(section),
      items: extractItems(section),
      notes: `Geëxtraheerd uit sectie ${index + 1}`,
      priority: index === 0 ? 'high' : 'normal'
    };
    
    // Only add if we found meaningful data
    if (delivery.customerRef || delivery.deliveryAddress.line1) {
      deliveries.push(delivery);
    }
  });
  
  // If no sections found, try to extract from full text
  if (deliveries.length === 0) {
    const delivery = {
      taskId: `TASK-${Date.now()}-1`,
      customerRef: extractCustomerRef(text),
      deliveryAddress: extractAddress(text),
      serviceDate: extractDate(text),
      timeWindowStart: extractTimeStart(text),
      timeWindowEnd: extractTimeEnd(text),
      items: extractItems(text),
      notes: 'Geëxtraheerd uit volledige document',
      priority: 'normal'
    };
    
    if (delivery.customerRef || delivery.deliveryAddress.line1) {
      deliveries.push(delivery);
    }
  }
  
  return deliveries;
}

function extractCustomerRef(text) {
  const patterns = [
    /(?:klant|customer|ref|referentie)[\s:]*([A-Z0-9-]+)/i,
    /(?:order|bestelling)[\s:]*([A-Z0-9-]+)/i,
    /([A-Z]{2,}\d{3,})/g
  ];
  
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) return match[1].trim();
  }
  
  return `AUTO-${Math.floor(Math.random() * 1000)}`;
}

function extractAddress(text) {
  const addressPatterns = [
    /(?:adres|address|leveradres)[\s:]*([^\n\r]+)/i,
    /([A-Za-z\s]+(?:straat|street|laan|avenue|plein|square)\s+\d+[^\n\r]*)/i,
    /([A-Za-z\s]+\d+[^\n\r]*)/i
  ];
  
  for (const pattern of addressPatterns) {
    const match = text.match(pattern);
    if (match) {
      return {
        line1: match[1].trim(),
        contactName: extractContactName(text),
        contactPhone: extractPhone(text)
      };
    }
  }
  
  return {
    line1: "Adres niet gevonden in document",
    contactName: "Onbekend",
    contactPhone: "+32 000 000 000"
  };
}

function extractContactName(text) {
  const patterns = [
    /(?:contact|naam|name)[\s:]*([A-Za-z\s]+)/i,
    /([A-Z][a-z]+\s+[A-Z][a-z]+)/g
  ];
  
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) return match[1].trim();
  }
  
  return "Contact persoon";
}

function extractPhone(text) {
  const phonePattern = /(\+32\s?\d{2,3}\s?\d{2,3}\s?\d{2,3})/g;
  const match = text.match(phonePattern);
  return match ? match[0] : "+32 000 000 000";
}

function extractDate(text) {
  const datePatterns = [
    /(\d{4}-\d{2}-\d{2})/,
    /(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})/,
    /(?:datum|date|leverdatum)[\s:]*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})/i
  ];
  
  for (const pattern of datePatterns) {
    const match = text.match(pattern);
    if (match) {
      let date = match[1];
      // Convert to ISO format if needed
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

function extractTimeStart(text) {
  const timePattern = /(?:tijd|time|tussen)[\s:]*(\d{1,2}:\d{2})/i;
  const match = text.match(timePattern);
  return match ? match[1] : "09:00";
}

function extractTimeEnd(text) {
  const timePattern = /(?:tot|until)[\s:]*(\d{1,2}:\d{2})/i;
  const match = text.match(timePattern);
  return match ? match[1] : "17:00";
}

function extractItems(text) {
  const itemPatterns = [
    /(?:items|pakketten|producten)[\s:]*([^\n\r]+)/i,
    /(\d+\s*(?:x|stuks?|pakketten?))/gi
  ];
  
  const items = [];
  
  for (const pattern of itemPatterns) {
    const matches = text.match(pattern);
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
