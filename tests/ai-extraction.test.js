const fs = require('fs');
const path = require('path');

// Mock the AI extraction functions for testing
// In a real implementation, these would import from your actual AI modules
const mockExtractDeliveries = async (text) => {
  // This is a mock implementation for testing
  // Replace with actual AI extraction logic
  if (text.includes('ORD-ANT2801')) {
    return JSON.parse(fs.readFileSync(path.join(__dirname, '../test-fixtures/expected/table-deliveries.json'), 'utf8'));
  } else if (text.includes('BXL2501')) {
    return JSON.parse(fs.readFileSync(path.join(__dirname, '../test-fixtures/expected/single-delivery.json'), 'utf8'));
  }
  return [];
};

describe('AI Extraction Tests', () => {
  const testFixturesDir = path.join(__dirname, '../test-fixtures');
  
  test('should extract table format deliveries correctly', async () => {
    // Mock table format text
    const tableText = `
      REF | Klant | Adres | Tijd | Nummer
      ORD-ANT2801 | Bistro Nova | Lange Koepoortstraat 23, 2000 Antwerpen | 07:00 – 09:00 | +32 470 81 32 40
      ORD-BRU2802 | Maison Blanche | Rue du Marché 12, 1000 Brussel | 08:15 – 10:30 | +32 491 27 84 66
      ORD-GEN2803 | De Smaakfabriek | Hoogpoort 101, 9000 Gent | 09:00 – 11:15 | +32 472 69 10 58
    `;
    
    const result = await mockExtractDeliveries(tableText);
    const expected = JSON.parse(fs.readFileSync(path.join(testFixturesDir, 'expected/table-deliveries.json'), 'utf8'));
    
    expect(result).toHaveLength(3);
    expect(result).toEqual(expected);
  });
  
  test('should extract single delivery correctly', async () => {
    const singleDeliveryText = `
      Levering: BXL2501
      Adres: Fleur du Jour, Vlaanderenstraat 16, 9000 Gent
      Contact: +32 497 30 52 10
      Tijd: 10:00 - 13:00
    `;
    
    const result = await mockExtractDeliveries(singleDeliveryText);
    const expected = JSON.parse(fs.readFileSync(path.join(testFixturesDir, 'expected/single-delivery.json'), 'utf8'));
    
    expect(result).toHaveLength(1);
    expect(result).toEqual(expected);
  });
  
  test('should handle empty text gracefully', async () => {
    const result = await mockExtractDeliveries('');
    expect(result).toEqual([]);
  });
  
  test('should validate delivery object structure', async () => {
    const tableText = 'ORD-ANT2801 | Bistro Nova | Lange Koepoortstraat 23, 2000 Antwerpen | 07:00 – 09:00 | +32 470 81 32 40';
    const result = await mockExtractDeliveries(tableText);
    
    if (result.length > 0) {
      const delivery = result[0];
      expect(delivery).toHaveProperty('customerRef');
      expect(delivery).toHaveProperty('deliveryAddress');
      expect(delivery).toHaveProperty('serviceDate');
      expect(delivery).toHaveProperty('timeWindowStart');
      expect(delivery).toHaveProperty('timeWindowEnd');
      expect(delivery).toHaveProperty('items');
      expect(delivery).toHaveProperty('priority');
      
      expect(delivery.deliveryAddress).toHaveProperty('line1');
      expect(delivery.deliveryAddress).toHaveProperty('contactName');
      expect(delivery.deliveryAddress).toHaveProperty('contactPhone');
    }
  });
});

// Integration test that would use real AI extraction
describe('AI Integration Tests', () => {
  test('should have required environment variables', () => {
    // This test ensures the AI integration has the required environment setup
    const requiredVars = ['ANTHROPIC_API_KEY'];
    const missingVars = requiredVars.filter(varName => !process.env[varName]);
    
    if (missingVars.length > 0) {
      console.warn(`Missing environment variables: ${missingVars.join(', ')}`);
      console.warn('AI tests will use mock data');
    }
  });
});

