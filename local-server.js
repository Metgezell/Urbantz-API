const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Simulate Urbantz API endpoint
app.post('/api/urbantz', async (req, res) => {
  try {
    const { customerRef, deliveryAddress, serviceDate, timeWindowStart, timeWindowEnd, items, notes } = req.body;
    
    // Validation
    if (!customerRef || !deliveryAddress?.line1) {
      return res.status(400).json({ 
        error: 'customerRef and deliveryAddress.line1 are required' 
      });
    }
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Mock response (replace with real API call)
    const mockResponse = {
      success: true,
      taskId: `TASK-${Date.now()}`,
      message: 'Task created successfully',
      data: {
        customerRef,
        deliveryAddress,
        serviceDate,
        timeWindowStart,
        timeWindowEnd,
        items: items || [],
        notes,
        status: 'pending',
        createdAt: new Date().toISOString()
      }
    };
    
    res.json(mockResponse);
    
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ 
      error: 'Internal server error',
      details: error.message 
    });
  }
});

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`🚀 Local server running at http://localhost:${PORT}`);
  console.log(`📱 Open your browser and test the Urbantz API interface!`);
  console.log(`🔧 API endpoint: http://localhost:${PORT}/api/urbantz`);
});
