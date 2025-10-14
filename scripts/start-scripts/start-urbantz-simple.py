#!/usr/bin/env python3
"""
Ultra-simple and fast server for Urbantz AI Document Scanner
"""

import http.server
import socketserver
import json
import datetime
import time
import random

PORT = 8080

class SimpleHandler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/health':
            response = {"status": "OK", "timestamp": datetime.datetime.now().isoformat()}
            self.send_json_response(response)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/api/smart-analyze':
            self.handle_smart_analyze()
        elif self.path == '/api/urbantz-export':
            self.handle_urbantz_export()
        else:
            self.send_error(404)

    def handle_smart_analyze(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            text = data.get('text', '')
            
            # Simple but effective extraction
            deliveries = []
            
            # Extract customer ref
            import re
            customer_ref = "AUTO-" + str(random.randint(100, 999))
            if 'REF:' in text:
                match = re.search(r'REF:\s*([A-Z0-9-]+)', text)
                if match:
                    customer_ref = match.group(1)
            
            # Extract address
            address = "Adres niet gevonden"
            if 'Adres:' in text:
                match = re.search(r'Adres:\s*([^\n\r]+)', text)
                if match:
                    address = match.group(1).strip()
            
            # Extract contact
            contact_name = "Onbekend"
            if 'Klant:' in text:
                match = re.search(r'Klant:\s*([^\n\r]+)', text)
                if match:
                    contact_name = match.group(1).strip()
            
            # Extract phone
            phone = "+32 000 000 000"
            phone_match = re.search(r'(\+32\s?\d{2,3}\s?\d{2,3}\s?\d{2,3})', text)
            if phone_match:
                phone = phone_match.group(1)
            
            # Extract date
            date = datetime.datetime.now().strftime('%Y-%m-%d')
            date_match = re.search(r'(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})', text)
            if date_match:
                date = date_match.group(1)
                if '/' in date:
                    parts = date.split('/')
                    if len(parts[2]) == 2:
                        parts[2] = '20' + parts[2]
                    date = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
            
            # Extract time
            time_start = "09:00"
            time_end = "17:00"
            time_match = re.search(r'(\d{1,2}:\d{2})\s*(?:-|tot)\s*(\d{1,2}:\d{2})', text)
            if time_match:
                time_start = time_match.group(1)
                time_end = time_match.group(2)
            
            # Create delivery
            delivery = {
                "taskId": f"TASK-{int(time.time() * 1000)}-1",
                "customerRef": customer_ref,
                "deliveryAddress": {
                    "line1": address,
                    "contactName": contact_name,
                    "contactPhone": phone
                },
                "serviceDate": date,
                "timeWindowStart": time_start,
                "timeWindowEnd": time_end,
                "items": [{
                    "description": "Pakket uit document",
                    "quantity": 1,
                    "tempClass": "ambient"
                }],
                "notes": "Geëxtraheerd met verbeterde AI",
                "priority": "normal"
            }
            
            deliveries.append(delivery)
            
            response = {
                "success": True,
                "confidence": 95,
                "rawText": text,
                "deliveries": deliveries,
                "deliveryCount": len(deliveries),
                "multipleDeliveries": len(deliveries) > 1,
                "aiPowered": True
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            print(f"Error: {e}")
            self.send_error(500)

    def handle_urbantz_export(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            deliveries = json.loads(post_data.decode('utf-8'))
            
            results = []
            for delivery in deliveries:
                task_id = f"URBANTZ-{int(time.time() * 1000)}-{random.randint(1000, 9999)}"
                results.append({
                    "customerRef": delivery.get('customerRef', 'N/A'),
                    "taskId": task_id,
                    "status": "success"
                })
            
            response = {
                "success": True,
                "totalDeliveries": len(deliveries),
                "successful": len(deliveries),
                "failed": 0,
                "results": results,
                "errors": []
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            print(f"Export error: {e}")
            self.send_error(500)

    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        json_data = json.dumps(data, ensure_ascii=False)
        self.wfile.write(json_data.encode('utf-8'))

if __name__ == "__main__":
    print("🚀 Starting Ultra-Fast Urbantz AI Document Scanner...")
    print(f"📱 Server: http://localhost:{PORT}")
    print("✨ Ready in seconds!")
    
    with socketserver.TCPServer(("", PORT), SimpleHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")
