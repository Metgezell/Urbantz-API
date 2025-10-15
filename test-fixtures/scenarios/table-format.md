# Table Format Test Scenario

## Description
Tests AI extraction from PDF documents containing delivery information in table format.

## Expected Behavior
- Each data row (excluding header) should be extracted as a separate delivery
- Header row should be ignored
- All table columns should be mapped to appropriate delivery fields

## Test Documents
- `table-deliveries.pdf` - Multiple deliveries in table format
- `table-single.pdf` - Single delivery in table format

## Expected Output Format
```json
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
  }
]
```

## Success Criteria
- Correct number of deliveries extracted (one per data row)
- All required fields populated
- Time windows properly parsed
- Address information complete

