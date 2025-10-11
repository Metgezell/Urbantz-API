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
        else:
            self.send_error(404)
    
    def handle_urbantz_api(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
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
                    'message': '✅ TEST MODE: Task created successfully (NO REAL DELIVERY)',
                    'warning': '🚨 This is a TEST - no real delivery will be created!',
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
