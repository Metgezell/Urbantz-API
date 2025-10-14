#!/usr/bin/env python3
"""
Fast and stable server for Urbantz AI Document Scanner
"""

import http.server
import socketserver
import json
import urllib.parse
import re
import datetime
import random
from io import BytesIO
import os
import threading
import time
import urllib.request

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    print("   Environment variables will only be loaded from system environment")

# Use a different port to avoid conflicts
PORT = 8080

class FastAPIHandler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/api/health':
            self.handle_health()
        else:
            self.send_error(404)

    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/smart-analyze':
            self.handle_smart_analyze()
        elif self.path == '/api/urbantz-export':
            self.handle_urbantz_export()
        elif self.path == '/api/analyze-document':
            self.handle_analyze_document()
        else:
            self.send_error(404)

    def handle_health(self):
        """Health check endpoint"""
        response = {
            "status": "OK",
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.send_json_response(response)

    def handle_smart_analyze(self):
        """Smart analyze endpoint with improved AI integration"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            text = data.get('text', '')
            html_content = data.get('htmlContent', '')
            
            if not text:
                self.send_error(400, "No text provided")
                return
            
            # DEBUG: Print wat we ontvangen
            print("\n" + "="*50)
            print("📥 RECEIVED DATA:")
            print("="*50)
            print(f"Text length: {len(text)} chars")
            print(f"HTML content length: {len(html_content)} chars")
            print(f"\nFirst 500 chars of text:\n{text[:500]}")
            if html_content:
                print(f"\nFirst 500 chars of HTML:\n{html_content[:500]}")
            print("="*50 + "\n")
            
            # Use AI analysis with enhanced prompting
            deliveries = self.extract_deliveries_with_improved_ai(text, html_content)
            
            response = {
                "success": True,
                "confidence": 90,
                "rawText": text,
                "deliveries": deliveries,
                "deliveryCount": len(deliveries),
                "multipleDeliveries": len(deliveries) > 1,
                "aiPowered": True,
                "method": "ai_extraction"
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            print(f"Smart analyze error: {e}")
            self.send_error(500, str(e))

    def handle_urbantz_export(self):
        """Urbantz export endpoint"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            deliveries = json.loads(post_data.decode('utf-8'))
            
            results = []
            successful = 0
            failed = 0
            
            for delivery in deliveries:
                try:
                    # Create mock Urbantz task ID
                    task_id = f"URBANTZ-{int(time.time() * 1000)}-{random.randint(1000, 9999)}"
                    results.append({
                        "customerRef": delivery.get('customerRef', 'N/A'),
                        "taskId": task_id,
                        "status": "success"
                    })
                    successful += 1
                except Exception as e:
                    results.append({
                        "customerRef": delivery.get('customerRef', 'N/A'),
                        "error": str(e),
                        "status": "failed"
                    })
                    failed += 1
            
            response = {
                "success": True,
                "totalDeliveries": len(deliveries),
                "successful": successful,
                "failed": failed,
                "results": results,
                "errors": [r for r in results if r.get('status') == 'failed']
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            print(f"Export error: {e}")
            self.send_error(500, str(e))

    def handle_analyze_document(self):
        """Handle document analysis endpoint"""
        try:
            # For now, simulate document analysis with mock data
            mock_text = """
            Levering informatie:
            
            REF: DOC-12345
            Klant: Test Bedrijf
            Adres: Teststraat 123, 1000 Brussel
            Nummer: +32 2 123 4567
            Datum: 15/10/2025
            Tijd: 10:00 - 14:00
            
            Items: 3x Pakketten, 1x Documenten
            """
            
            deliveries = self.extract_deliveries_with_improved_ai(mock_text)
            
            response = {
                "success": True,
                "confidence": 85,
                "rawText": mock_text,
                "deliveries": deliveries,
                "deliveryCount": len(deliveries),
                "multipleDeliveries": len(deliveries) > 1,
                "fileName": "uploaded_document.pdf"
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            print(f"Document analysis error: {e}")
            self.send_error(500, str(e))

    def extract_deliveries_with_improved_ai(self, text, html_content=''):
        """Improved delivery extraction using Anthropic Claude API with few-shot learning"""
        # Try to use Anthropic Claude API first
        anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
        
        if anthropic_api_key:
            try:
                print("🤖 Using Anthropic Claude API for AI analysis...")
                
                # DEBUG: Log the prompt being sent
                print("\n📤 SENDING TO AI:")
                print(f"Text to analyze (first 300 chars): {text[:300]}...")
                
                deliveries = self.extract_deliveries_with_claude(text, api_key=anthropic_api_key)
                
                # DEBUG: Log what we got back
                print(f"\n📨 AI RESPONSE:")
                print(f"Number of deliveries: {len(deliveries) if deliveries else 0}")
                if deliveries:
                    print(f"First delivery: {json.dumps(deliveries[0], indent=2)}")
                
                if deliveries:
                    print(f"✅ Claude API extracted {len(deliveries)} delivery(ies)")
                    return deliveries
            except Exception as e:
                print(f"⚠️ Claude API error: {e}")
                import traceback
                traceback.print_exc()
                print("   Falling back to pattern matching...")
        else:
            print("⚠️ ANTHROPIC_API_KEY not found, using pattern matching")
        
        # Fallback to pattern matching
        return self.extract_deliveries_with_patterns(text)
    
    def extract_deliveries_with_claude(self, text, api_key):
        """Extract deliveries using Anthropic Claude API with chain-of-thought reasoning"""
        prompt = f"""
Je bent een expert in het analyseren van leveringsdocumenten, emails en tabellen. 

=== STAP 1: ANALYSE VAN HET DOCUMENT ===
Analyseer eerst het document en bepaal:
1. Wat is het FORMAT? (tabel, genummerde lijst, paragrafen, enkele levering, etc.)
2. Hoeveel LEVERINGEN zijn er? (tel zorgvuldig alle aparte leveringen)
3. Hoe is de DATA GESTRUCTUREERD? (kolommen, bullets, tekst)

=== VOORBEELDEN VAN VERSCHILLENDE FORMATEN ===

VOORBEELD A - TABEL FORMAT (meerdere leveringen):
```
| Ref | Klant | Adres | Tijdslot | Contact |
| ORD-001 | Bakkerij Jan | Hoofdstraat 1, Brussel | 08:00–10:00 | +32 2 123 45 67 |
| ORD-002 | Café Marie | Kerkstraat 5, Antwerpen | 09:00–11:00 | +32 3 234 56 78 |
```
→ Format: TABEL
→ Aantal leveringen: 2 (één per rij)
→ Output: Array met 2 objecten

VOORBEELD B - GENUMMERDE LIJST (meerdere leveringen):
```
1. REF: ORD-001
   Klant: Bakkerij Jan
   Adres: Hoofdstraat 1, Brussel
   Tijd: 08:00 - 10:00

2. REF: ORD-002
   Klant: Café Marie
   Adres: Kerkstraat 5, Antwerpen
   Tijd: 09:00 - 11:00
```
→ Format: GENUMMERDE LIJST
→ Aantal leveringen: 2 (één per nummer)
→ Output: Array met 2 objecten

VOORBEELD C - ENKELE LEVERING (één levering):
```
Levering: BXL2501
Adres: Fleur du Jour, Vlaanderenstraat 16, 9000 Gent
Contact: +32 497 30 52 10
Tijd: 10:00 - 13:00
```
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
- items: [{{description: "Standaard levering", quantity: 1, tempClass: "ambient"}}]
- notes: Relevante extra info
- priority: "normal" (tenzij urgent/spoed vermeld)

=== TEKST OM TE ANALYSEREN ===
{text}

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
"""
        
        # Prepare API request
        request_data = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 8000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        # Make API request
        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=json.dumps(request_data).encode('utf-8'),
            headers={
                'x-api-key': api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
        )
        
        response = urllib.request.urlopen(req, timeout=30)
        result = json.loads(response.read().decode('utf-8'))
        
        if result.get('content') and len(result['content']) > 0:
            ai_response = result['content'][0]['text']
            
            print(f"\n🤖 RAW AI RESPONSE:")
            print(f"{ai_response[:1000]}...")  # First 1000 chars
            
            try:
                # Try to extract JSON from the response (might have markdown code blocks)
                json_match = re.search(r'```json\s*([\s\S]*?)\s*```', ai_response)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Try to find any JSON array in the response
                    json_match = re.search(r'\[[\s\S]*\]', ai_response)
                    if json_match:
                        json_str = json_match.group(0)
                    else:
                        json_str = ai_response
                
                # Parse AI response as JSON
                deliveries = json.loads(json_str)
                if isinstance(deliveries, list):
                    return deliveries
                elif isinstance(deliveries, dict):
                    return [deliveries]
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse Claude response: {e}")
                print(f"Claude full response: {ai_response}")
        
        return None
    
    def extract_deliveries_with_patterns(self, text):
        """Fallback: Extract deliveries using pattern matching"""
        deliveries = []
        
        # Improved pattern matching
        sections = self.detect_delivery_sections(text)
        
        for i, section in enumerate(sections):
            delivery = {
                "taskId": f"TASK-{int(time.time() * 1000)}-{i + 1}",
                "customerRef": self.extract_customer_ref(section),
                "deliveryAddress": self.extract_address(section),
                "serviceDate": self.extract_date(section),
                "timeWindowStart": self.extract_time_start(section),
                "timeWindowEnd": self.extract_time_end(section),
                "items": self.extract_items(section),
                "notes": f"Geëxtraheerd uit sectie {i + 1}",
                "priority": "normal"
            }
            
            # Only add if we found meaningful data
            if delivery["customerRef"] != "AUTO-NOTFOUND" or delivery["deliveryAddress"]["line1"] != "Adres niet gevonden":
                deliveries.append(delivery)
        
        return deliveries

    def detect_delivery_sections(self, text):
        """Detect delivery sections in text"""
        # Look for clear section separators
        sections = []
        
        # Try to split by REF: patterns
        ref_sections = re.split(r'(?=REF:\s*[A-Z0-9-]+)', text, flags=re.IGNORECASE)
        if len(ref_sections) > 1:
            sections.extend([s for s in ref_sections if s.strip()])
        
        # If no REF sections, try other patterns
        if not sections:
            section_patterns = [
                r'(?=Klant:\s*)',
                r'(?=Adres:\s*)',
                r'(?=lever|delivery)'
            ]
            
            for pattern in section_patterns:
                parts = re.split(pattern, text, flags=re.IGNORECASE)
                if len(parts) > 1:
                    sections.extend([p for p in parts if p.strip() and len(p.strip()) > 50])
                    break
        
        # Fallback to full text
        if not sections:
            sections = [text]
        
        return sections

    def extract_customer_ref(self, text):
        """Extract customer reference with improved patterns"""
        patterns = [
            r'REF:\s*([A-Z0-9-]+)',
            r'Klant:\s*([A-Z0-9-]+)',
            r'Customer:\s*([A-Z0-9-]+)',
            r'Order:\s*([A-Z0-9-]+)',
            r'([A-Z]{2,}\d{3,})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "AUTO-NOTFOUND"

    def extract_address(self, text):
        """Extract address with improved patterns"""
        patterns = [
            r'Adres:\s*([^\n\r]+)',
            r'Address:\s*([^\n\r]+)',
            r'([A-Za-z\s]+(?:straat|street|laan|avenue|plein|square|weg|road)\s+\d+[^\n\r]*)',
            r'([A-Za-z\s]+\d+[A-Za-z]?\s*,\s*\d{4}\s+[A-Za-z\s]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                address = match.group(1).strip()
                return {
                    "line1": address,
                    "contactName": self.extract_contact_name(text),
                    "contactPhone": self.extract_phone(text)
                }
        
        return {
            "line1": "Adres niet gevonden",
            "contactName": "Onbekend",
            "contactPhone": "+32 000 000 000"
        }

    def extract_contact_name(self, text):
        """Extract contact name"""
        patterns = [
            r'Klant:\s*([^\n\r]+)',
            r'Contact:\s*([^\n\r]+)',
            r'Naam:\s*([^\n\r]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Contact persoon"

    def extract_phone(self, text):
        """Extract phone number"""
        patterns = [
            r'Nummer:\s*(\+32\s?\d{2,3}\s?\d{2,3}\s?\d{2,3})',
            r'(\+32\s?\d{2,3}\s?\d{2,3}\s?\d{2,3})',
            r'(0\d{2,3}\s?\d{2,3}\s?\d{2,3})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return "+32 000 000 000"

    def extract_date(self, text):
        """Extract date with improved patterns"""
        patterns = [
            r'Datum:\s*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})',
            r'Date:\s*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                # Convert to ISO format
                if '/' in date_str:
                    parts = date_str.split('/')
                    if len(parts[2]) == 2:
                        parts[2] = '20' + parts[2]
                    return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
                elif '-' in date_str:
                    return date_str
        
        # Default to tomorrow
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        return tomorrow.strftime('%Y-%m-%d')

    def extract_time_start(self, text):
        """Extract start time"""
        patterns = [
            r'Tijd:\s*(\d{1,2}:\d{2})\s*(?:-|tot)',
            r'Time:\s*(\d{1,2}:\d{2})\s*(?:-|tot)',
            r'(\d{1,2}:\d{2})\s*(?:tot|-)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "09:00"

    def extract_time_end(self, text):
        """Extract end time"""
        patterns = [
            r'Tijd:\s*\d{1,2}:\d{2}\s*(?:-|tot)\s*(\d{1,2}:\d{2})',
            r'Time:\s*\d{1,2}:\d{2}\s*(?:-|tot)\s*(\d{1,2}:\d{2})',
            r'(\d{1,2}:\d{2})\s*(?:einde|end)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "17:00"

    def extract_items(self, text):
        """Extract items"""
        items = []
        
        # Look for item patterns
        patterns = [
            r'Items:\s*([^\n\r]+)',
            r'Pakketten:\s*([^\n\r]+)',
            r'(\d+\s*(?:x|stuks?|pakketten?))'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                items.append({
                    "description": match.strip(),
                    "quantity": 1,
                    "tempClass": "ambient"
                })
        
        if not items:
            items.append({
                "description": "Pakket uit document",
                "quantity": 1,
                "tempClass": "ambient"
            })
        
        return items

    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        json_data = json.dumps(data, ensure_ascii=False)
        self.wfile.write(json_data.encode('utf-8'))

def start_server():
    """Start the server with better error handling"""
    print("🚀 Starting Fast Urbantz AI Document Scanner server...")
    print(f"📱 Server will be available at: http://localhost:{PORT}")
    print("🔧 API endpoints available:")
    print("   - POST /api/smart-analyze")
    print("   - POST /api/urbantz-export")
    print("   - GET /api/health")
    print("\n✨ Ready to scan documents and create Urbantz tasks!")
    
    # Try different ports if current one is busy
    current_port = PORT
    max_attempts = 5
    
    for attempt in range(max_attempts):
        try:
            with socketserver.TCPServer(("", current_port), FastAPIHandler) as httpd:
                print(f"✅ Server started successfully on port {current_port}")
                httpd.serve_forever()
        except OSError as e:
            if "address already in use" in str(e) or "already been used" in str(e):
                current_port += 1
                print(f"⚠️ Port {current_port - 1} is busy, trying port {current_port}...")
                continue
            else:
                print(f"❌ Server error: {e}")
                break
        except KeyboardInterrupt:
            print("\n👋 Server stopped by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            break
    
    if attempt == max_attempts - 1:
        print(f"❌ Could not start server after {max_attempts} attempts")

if __name__ == "__main__":
    start_server()
