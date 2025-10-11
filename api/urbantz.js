// Vercel serverless function for Urbantz API
export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-API-Key');
  
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }
  
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  try {
    const { URBANTZ_API_KEY, URBANTZ_BASE_URL } = process.env;
    
    if (!URBANTZ_API_KEY) {
      return res.status(400).json({ 
        error: 'URBANTZ_API_KEY environment variable not set' 
      });
    }
    
    const baseUrl = URBANTZ_BASE_URL || 'https://api.urbantz.com';
    const apiKey = req.headers['x-api-key'] || URBANTZ_API_KEY;
    
    // Validate payload
    const { customerRef, deliveryAddress, serviceDate, timeWindowStart, timeWindowEnd, items, notes } = req.body;
    
    if (!customerRef || !deliveryAddress?.line1) {
      return res.status(400).json({ 
        error: 'customerRef and deliveryAddress.line1 are required' 
      });
    }
    
    // Validate date format
    if (serviceDate && !/^\d{4}-\d{2}-\d{2}$/.test(serviceDate)) {
      return res.status(400).json({ 
        error: 'serviceDate must be in YYYY-MM-DD format' 
      });
    }
    
    // Validate time format
    if (timeWindowStart && !/^\d{2}:\d{2}$/.test(timeWindowStart)) {
      return res.status(400).json({ 
        error: 'timeWindowStart must be in HH:MM format' 
      });
    }
    
    if (timeWindowEnd && !/^\d{2}:\d{2}$/.test(timeWindowEnd)) {
      return res.status(400).json({ 
        error: 'timeWindowEnd must be in HH:MM format' 
      });
    }
    
    // Call Urbantz API
    const urbantzResponse = await fetch(`${baseUrl}/v2/announce`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
      },
      body: JSON.stringify({
        customerRef,
        pickupAddress: null,
        deliveryAddress,
        serviceDate,
        timeWindowStart,
        timeWindowEnd,
        items: items || [],
        notes
      }),
    });
    
    if (!urbantzResponse.ok) {
      const errorText = await urbantzResponse.text();
      return res.status(urbantzResponse.status).json({
        error: `Urbantz API error: ${urbantzResponse.status}`,
        details: errorText
      });
    }
    
    const result = await urbantzResponse.json();
    res.status(200).json(result);
    
  } catch (error) {
    console.error('Urbantz API error:', error);
    res.status(500).json({ 
      error: 'Internal server error',
      details: error.message 
    });
  }
}
