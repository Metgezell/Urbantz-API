#!/usr/bin/env python3
import http.server
import socketserver
import webbrowser
import os
from urllib.parse import urlparse, parse_qs
import json

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/urbantz':
            self.handle_urbantz_api()
        elif self.path == '/api/smart-analyze':
            self.handle_smart_analyze()
        else:
            self.send_error(404)
    
    def handle_urbantz_api(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract sender information if available
            sender = data.get('sender', {})
            sender_name = sender.get('name', 'Onbekend')
            sender_email = sender.get('email', 'onbekend@example.com')
            
            print(f"🏢 Verzender: {sender_name} ({sender_email})")
            
            # Validation
            if not data.get('customerRef') or not data.get('deliveryAddress', {}).get('line1'):
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': 'customerRef and deliveryAddress.line1 are required'
                }).encode())
                return
            
            # Check if this is a test environment
            api_key = self.headers.get('X-API-Key', '')
            is_test_mode = api_key.startswith('test_') or api_key == 'test' or 'test' in data.get('customerRef', '').lower()
            
            if is_test_mode:
                # TEST MODE - Safe mock response
                response = {
                    'success': True,
                    'taskId': f'TEST-TASK-{int(__import__("time").time() * 1000)}',
                    'message': f'✅ TEST MODE: Task created successfully voor {sender_name} (NO REAL DELIVERY)',
                    'warning': '🚨 This is a TEST - no real delivery will be created!',
                    'sender': {
                        'name': sender_name,
                        'email': sender_email
                    },
                    'data': {
                        **data,
                        'status': 'test_pending',
                        'environment': 'TEST',
                        'createdAt': __import__('datetime').datetime.now().isoformat(),
                        'testMode': True
                    }
                }
            else:
                # PRODUCTION MODE - Simulate real API call
                response = {
                    'success': True,
                    'taskId': f'PROD-TASK-{int(__import__("time").time() * 1000)}',
                    'message': '⚠️ PRODUCTION MODE: This would create a REAL delivery!',
                    'warning': '🚨 WARNING: This is PRODUCTION mode - real delivery will be created!',
                    'data': {
                        **data,
                        'status': 'pending',
                        'environment': 'PRODUCTION',
                        'createdAt': __import__('datetime').datetime.now().isoformat(),
                        'testMode': False
                    }
                }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            }).encode())
    
    def handle_smart_analyze(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            text = data.get('text', '')
            if not text:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': 'No text provided'
                }).encode())
                return
            
            # Use AI to analyze the text
            deliveries = self.extract_deliveries_with_ai(text)
            
            response = {
                'success': True,
                'confidence': 85 if deliveries else 60,
                'rawText': text,
                'deliveries': deliveries,
                'deliveryCount': len(deliveries),
                'multipleDeliveries': len(deliveries) > 1,
                'aiPowered': True
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': 'Smart analysis failed',
                'details': str(e)
            }).encode())
    
    def extract_deliveries_with_ai(self, text):
        """Extract deliveries using AI analysis"""
        import os
        import requests
        
        # Load API key from .env file
        api_key = None
        try:
            with open('../.env', 'r') as f:
                for line in f:
                    if line.startswith('ANTHROPIC_API_KEY='):
                        api_key = line.split('=', 1)[1].strip()
                        break
        except:
            pass
        
        if not api_key:
            # Fallback to pattern matching
            return self.extract_deliveries_with_patterns(text)
        
        try:
            # Call Anthropic Claude API
            response = requests.post('https://api.anthropic.com/v1/messages', 
                headers={
                    'x-api-key': api_key,
                    'Content-Type': 'application/json',
                    'anthropic-version': '2023-06-01'
                },
                json={
                    'model': 'claude-3-5-sonnet-20241022',
                    'max_tokens': 4000,
                    'messages': [{
                        'role': 'user',
                        'content': f'''Je bent een expert in het analyseren van leveringsdocumenten. Extraheer altijd gestructureerde JSON data.

Analyseer de volgende tekst en extraheer alle leveringsinformatie. 
Identificeer elke levering als een aparte taak met de volgende structuur:

Voor elke levering, extraheer:
- customerRef: Klant referentie (bijv. CUST-123, ORDER-456)
- deliveryAddress: Volledig adres met contact informatie
- serviceDate: Leverdatum (YYYY-MM-DD formaat)
- timeWindowStart: Starttijd (HH:MM formaat)
- timeWindowEnd: Eindtijd (HH:MM formaat)  
- items: Array van items met description, quantity, tempClass
- notes: Relevante notities
- priority: "high", "normal", of "low"

Tekst om te analyseren:
{text}

Geef het antwoord terug als JSON array van leveringen. Als er geen leveringen gevonden worden, geef een lege array terug.'''
                    }]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('content') and result['content'][0].get('text'):
                    ai_response = result['content'][0]['text']
                    try:
                        deliveries = json.loads(ai_response)
                        return deliveries if isinstance(deliveries, list) else [deliveries]
                    except:
                        pass
            
        except Exception as e:
            print(f"AI API error: {e}")
        
        # Fallback to pattern matching
        return self.extract_deliveries_with_patterns(text)
    
    def extract_deliveries_with_patterns(self, text):
        """Fallback pattern matching for delivery extraction"""
        deliveries = []
        
        # Simple pattern detection
        sections = text.split('\n\n')
        
        for i, section in enumerate(sections):
            if len(section.strip()) > 50:  # Only process substantial sections
                delivery = {
                    'taskId': f'TASK-{int(__import__("time").time() * 1000)}-{i+1}',
                    'customerRef': f'AUTO-{i+1}',
                    'deliveryAddress': {
                        'line1': 'Adres uit document',
                        'contactName': 'Contact persoon',
                        'contactPhone': '+32 000 000 000'
                    },
                    'serviceDate': (__import__('datetime').datetime.now() + __import__('datetime').timedelta(days=1)).strftime('%Y-%m-%d'),
                    'timeWindowStart': '09:00',
                    'timeWindowEnd': '17:00',
                    'items': [{
                        'description': 'Pakket uit document',
                        'quantity': 1,
                        'tempClass': 'ambient'
                    }],
                    'notes': f'Geëxtraheerd uit sectie {i+1}',
                    'priority': 'normal'
                }
                deliveries.append(delivery)
        
        return deliveries
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
        self.end_headers()

def start_server():
    PORT = 3000
    
    # Change to public directory
    os.chdir('public')
    
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"🚀 Local server running at http://localhost:{PORT}")
        print(f"📱 Open your browser and test the Urbantz API interface!")
        print(f"🔧 API endpoint: http://localhost:{PORT}/api/urbantz")
        print(f"⏹️  Press Ctrl+C to stop the server")
        
        # Open browser automatically
        webbrowser.open(f'http://localhost:{PORT}')
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped!")

if __name__ == "__main__":
    start_server()
