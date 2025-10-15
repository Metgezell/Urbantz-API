// Test setup file
// This file runs before all tests

// Mock console methods to reduce noise during testing
const originalConsoleLog = console.log;
const originalConsoleWarn = console.warn;
const originalConsoleError = console.error;

beforeAll(() => {
  // Suppress console output during tests unless explicitly needed
  console.log = jest.fn();
  console.warn = jest.fn();
  console.error = jest.fn();
});

afterAll(() => {
  // Restore console methods
  console.log = originalConsoleLog;
  console.warn = originalConsoleWarn;
  console.error = originalConsoleError;
});

// Set test timeout for AI operations
jest.setTimeout(30000); // 30 seconds for AI API calls
