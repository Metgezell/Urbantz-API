# Urbantz API Reference

## Authenticatie

- **Methode**: API key via header
- **Header**: `x-api-key: YOUR_API_KEY`
- **Content-Type**: `application/json`

## Kernendpoint

### POST /v2/announce

Maakt een nieuwe taak aan (pickup of delivery).

**Minimale velden:**
- `customerRef` - Klant referentie (verplicht)
- `deliveryAddress.line1` - Adres regel 1 (verplicht)
- `serviceDate` - Service datum in YYYY-MM-DD formaat (verplicht)

**Optionele velden:**
- `pickupAddress` - Pickup adres (voor pickup taken)
- `timeWindowStart/End` - Tijdvenster in HH:MM formaat
- `items[]` - Items array met beschrijving, hoeveelheid, etc.
- `notes` - Extra notities
- `contactName/Phone/Email` - Contact informatie

## Response

**Succes (200):**
```json
{
  "taskId": "string",
  "customerRef": "string"
}
```

**Fouten:**
- **400**: Bad Request - Ongeldige payload
- **401**: Unauthorized - Ongeldige API key  
- **409**: Conflict - Task bestaat al

## Validatie

- `serviceDate`: Moet YYYY-MM-DD formaat zijn
- `timeWindowStart/End`: Moet HH:MM formaat zijn
- `customerRef`: Verplicht veld
- `deliveryAddress.line1`: Verplicht veld
