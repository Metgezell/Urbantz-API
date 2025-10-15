# Test Fixtures for AI Integration

This directory contains test documents and expected outputs for the AI integration.

## Structure

```
test-fixtures/
├── documents/           # Sample PDFs, HTML, and text files
├── expected/           # Expected JSON outputs for each test case
└── scenarios/          # Different test scenarios (table, single delivery, etc.)
```

## Test Cases

### Table Format (Multiple Deliveries)
- **Document**: `table-deliveries.pdf`
- **Expected**: `expected/table-deliveries.json`
- **Description**: PDF with table containing multiple delivery rows

### Single Delivery
- **Document**: `single-delivery.pdf`
- **Expected**: `expected/single-delivery.json`
- **Description**: PDF with single delivery information

### Numbered List Format
- **Document**: `numbered-list.txt`
- **Expected**: `expected/numbered-list.json`
- **Description**: Text with numbered delivery list

## Adding New Test Cases

1. Add the test document to `documents/`
2. Run the AI extraction on the document
3. Save the expected output to `expected/`
4. Update this README with the new test case

## Running Tests

```bash
npm test
```

This will run all test fixtures against the current AI extraction logic.

