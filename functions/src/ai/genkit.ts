// Genkit integration - simplified for now
// Full Genkit integration can be added later when Genkit has stable Claude support

/**
 * Claude AI extraction prompt - reused from local-server.js
 */
function buildClaudePrompt(text: string): string {
  return `
Je bent een expert in het analyseren van leveringsdocumenten, emails en tabellen. 

=== STAP 1: ANALYSE VAN HET DOCUMENT ===
Analyseer eerst het document en bepaal:
1. Wat is het FORMAT? (tabel, genummerde lijst, paragrafen, enkele levering, etc.)
2. Hoeveel LEVERINGEN zijn er? (tel zorgvuldig alle aparte leveringen)
3. Hoe is de DATA GESTRUCTUREERD? (kolommen, bullets, tekst)

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

Geef dan een JSON array terug met EXACT het aantal leveringen dat je hebt gevonden.
- Als het een tabel is met 10 rijen → 10 leveringen
- Als het een lijst is met 5 items → 5 leveringen  
- Als het 1 enkele levering is → 1 levering

Geef ALLEEN de JSON array terug, geen uitleg.
`;
}

/**
 * Call Claude API directly (without Genkit for now, as Genkit doesn't have native Claude support yet)
 * @param text Input text to analyze
 * @param anthropicApiKey Anthropic API key
 * @returns Extracted deliveries array
 */
export async function extractWithClaude(
  text: string,
  anthropicApiKey: string
): Promise<any[]> {
  try {
    const prompt = buildClaudePrompt(text);

    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "x-api-key": anthropicApiKey,
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-3-5-sonnet-20241022",
        max_tokens: 8000,
        messages: [
          {
            role: "user",
            content: prompt,
          },
        ],
      }),
    });

    if (!response.ok) {
      throw new Error(
        `Claude API error: ${response.status} ${response.statusText}`
      );
    }

    const result: any = await response.json();

    if (result.content && result.content[0]) {
      const aiResponse = result.content[0].text;

      try {
        // Parse AI response as JSON
        const deliveries = JSON.parse(aiResponse);
        return Array.isArray(deliveries) ? deliveries : [deliveries];
      } catch (parseError) {
        console.error("Failed to parse Claude response:", parseError);
        console.log("Claude response:", aiResponse);
        throw new Error("Failed to parse Claude response as JSON");
      }
    }

    throw new Error("No content in Claude response");
  } catch (error) {
    console.error("Claude API error:", error);
    throw error;
  }
}

/**
 * Analyze document with logging wrapper
 * This can be upgraded to full Genkit integration when Genkit has stable Claude support
 */
export async function analyzeDocument(
  text: string,
  sourceType: string,
  anthropicApiKey: string
): Promise<{
  deliveries: any[];
  confidence: number;
  model: string;
}> {
  // Call Claude API
  const deliveries = await extractWithClaude(text, anthropicApiKey);

  return {
    deliveries,
    confidence: deliveries.length > 0 ? 85 : 60,
    model: "claude-3-5-sonnet-20241022",
  };
}

