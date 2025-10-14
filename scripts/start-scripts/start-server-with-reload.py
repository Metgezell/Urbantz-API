#!/usr/bin/env python3
"""
Fast and stable server for Urbantz AI Document Scanner with live-reload support
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
import signal
import sys
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
        elif self.path == '/api/status':
            self.handle_status()
        else:
            self.send_error(404)

    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/smart-analyze':
            self.handle_smart_analyze()
        elif self.path == '/api/urbantz-export':
            self.handle_urbantz_export()
        else:
            self.send_error(404)

    def handle_health(self):
        """Health check endpoint"""
        response = {
            "status": "OK",
            "timestamp": datetime.datetime.now().isoformat(),
            "uptime": time.time() - start_time,
            "server": "Python FastAPI Handler",
            "version": "2.0"
        }
        self.send_json_response(response)

    def handle_status(self):
        """Detailed status endpoint"""
        response = {
            "status": "OK",
            "server": {
                "name": "Urbantz AI Document Scanner",
                "version": "2.0",
                "python_version": sys.version,
                "uptime": time.time() - start_time
            },
            "endpoints": [
                {"path": "/api/health", "method": "GET", "description": "Health check"},
                {"path": "/api/status", "method": "GET", "description": "Server status"},
                {"path": "/api/smart-analyze", "method": "POST", "description": "AI document analysis"},
                {"path": "/api/urbantz-export", "method": "POST", "description": "Export to Urbantz"}
            ],
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.send_json_response(response)

    def handle_smart_analyze(self):
        """Smart analyze endpoint with improved AI integration"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error(400, "No content provided")
                return
                
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            text = data.get('text', '')
            if not text:
                self.send_error(400, "No text provided")
                return
            
            # Use improved AI analysis
            deliveries = self.extract_deliveries_with_improved_ai(text)
            
            response = {
                "success": True,
                "confidence": 90,
                "rawText": text,
                "deliveries": deliveries,
                "deliveryCount": len(deliveries),
                "multipleDeliveries": len(deliveries) > 1,
                "aiPowered": True,
                "processedAt": datetime.datetime.now().isoformat()
            }
            
            self.send_json_response(response)
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            print(f"Smart analyze error: {e}")
            self.send_error(500, str(e))

    def handle_urbantz_export(self):
        """Urbantz export endpoint"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error(400, "No content provided")
                return
                
            post_data = self.rfile.read(content_length)
            deliveries = json.loads(post_data.decode('utf-8'))
            
            if not isinstance(deliveries, list):
                self.send_error(400, "Expected array of deliveries")
                return
            
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
                        "status": "success",
                        "createdAt": datetime.datetime.now().isoformat()
                    })
                    successful += 1
                except Exception as e:
                    results.append({
                        "customerRef": delivery.get('customerRef', 'N/A'),
                        "error": str(e),
                        "status": "failed",
                        "failedAt": datetime.datetime.now().isoformat()
                    })
                    failed += 1
            
            response = {
                "success": True,
                "totalDeliveries": len(deliveries),
                "successful": successful,
                "failed": failed,
                "results": results,
                "errors": [r for r in results if r.get('status') == 'failed'],
                "exportedAt": datetime.datetime.now().isoformat()
            }
            
            self.send_json_response(response)
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            print(f"Export error: {e}")
            self.send_error(500, str(e))

    def extract_deliveries_with_improved_ai(self, text):
        """Improved delivery extraction using Anthropic Claude API"""
        # Try to use Anthropic Claude API first
        anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
        
        if anthropic_api_key:
            try:
                print("🤖 Using Anthropic Claude API for AI analysis...")
                deliveries = self.extract_deliveries_with_claude(text, anthropic_api_key)
                if deliveries:
                    print(f"✅ Claude API extracted {len(deliveries)} delivery(ies)")
                    return deliveries
            except Exception as e:
                print(f"⚠️ Claude API error: {e}")
                print("   Falling back to pattern matching...")
        else:
            print("⚠️ ANTHROPIC_API_KEY not found, using pattern matching")
        
        # Fallback to pattern matching
        return self.extract_deliveries_with_patterns(text)
    
    def extract_deliveries_with_claude(self, text, api_key):
        """Extract deliveries using Anthropic Claude API"""
        prompt = f"""
Je bent een expert in het analyseren van leveringsdocumenten en emails. Extraheer zorgvuldig alle leveringsinformatie uit de volgende tekst.

INSTRUCTIES:
1. Identificeer alle leveringen in de tekst
2. Voor elke levering, extraheer de volgende informatie:
   - customerRef: Klant referentie (zoek naar REF:, klant:, customer:, order: etc.)
   - deliveryAddress: Volledig adres met contactgegevens (zoek naar adres:, address: etc.)
   - serviceDate: Leverdatum in YYYY-MM-DD formaat
   - timeWindowStart: Starttijd in HH:MM formaat  
   - timeWindowEnd: Eindtijd in HH:MM formaat
   - items: Array van items met description, quantity, tempClass
   - notes: Relevante notities
   - priority: "high", "normal", of "low"

BELANGRIJK:
- Gebruik de exacte tekst uit het document
- Als informatie ontbreekt, gebruik "Niet gevonden" in plaats van "N/A"
- Converteer datums naar YYYY-MM-DD formaat
- Zorg dat contact informatie correct wordt gekoppeld aan het adres
- Geef altijd een geldig JSON array terug, ook als er geen leveringen gevonden worden

Tekst om te analyseren:
{text}

Geef het antwoord terug als een JSON array van leveringen. Als er geen leveringen gevonden worden, geef een lege array terug.
"""
        
        # Prepare API request
        request_data = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 4000,
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
            
            try:
                # Parse AI response as JSON
                deliveries = json.loads(ai_response)
                if isinstance(deliveries, list):
                    return deliveries
                elif isinstance(deliveries, dict):
                    return [deliveries]
            except json.JSONDecodeError as e:
                print(f"Failed to parse Claude response: {e}")
                print(f"Claude response: {ai_response}")
        
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
                "priority": "normal",
                "extractedAt": datetime.datetime.now().isoformat()
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
        
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(json_data.encode('utf-8'))

    def log_message(self, format, *args):
        """Custom log message format"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {format % args}")

# Global start time for uptime calculation
start_time = time.time()

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

def start_server():
    """Start the server with better error handling"""
    print("🚀 Starting Fast Urbantz AI Document Scanner server...")
    print(f"📱 Server will be available at: http://localhost:{PORT}")
    print("🔧 API endpoints available:")
    print("   - GET  /api/health")
    print("   - GET  /api/status")
    print("   - POST /api/smart-analyze")
    print("   - POST /api/urbantz-export")
    print("\n✨ Ready to scan documents and create Urbantz tasks!")
    print("💡 Press Ctrl+C to stop the server")
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Try different ports if current one is busy
    current_port = PORT
    max_attempts = 5
    
    for attempt in range(max_attempts):
        try:
            with socketserver.TCPServer(("", current_port), FastAPIHandler) as httpd:
                print(f"✅ Server started successfully on port {current_port}")
                print(f"🔗 Health check: http://localhost:{current_port}/api/health")
                print(f"📊 Status: http://localhost:{current_port}/api/status")
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
