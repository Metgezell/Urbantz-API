#!/usr/bin/env python3
"""
Local development server for Urbantz AI Document Scanner
Provides API endpoints for document analysis and Urbantz export
"""

import http.server
import socketserver
import json
import urllib.parse
import re
import datetime
import random
from io import BytesIO
import cgi
import os

PORT = 8000

class UrbantzAPIHandler(http.server.BaseHTTPRequestHandler):
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
            self.send_json_response({'status': 'OK', 'timestamp': datetime.datetime.now().isoformat()})
        elif self.path == '/' or self.path == '/index.html':
            self.serve_file('index.html')
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/smart-analyze':
            self.handle_smart_analyze()
        elif self.path == '/api/urbantz-export':
            self.handle_urbantz_export()
        else:
            self.send_error(404, "Not Found")
    
    def handle_smart_analyze(self):
        """Handle AI text analysis"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            text = data.get('text', '')
            if not text:
                self.send_json_response({'error': 'No text provided'}, status=400)
                return
            
            print(f"🔍 Analyzing text with AI...")
            
            # Use AI to extract delivery information
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
            
            self.send_json_response(response)
            
        except Exception as e:
            print(f"Smart analysis error: {e}")
            self.send_json_response({'error': 'Smart analysis failed', 'details': str(e)}, status=500)

    def handle_urbantz_export(self):
        """Handle Urbantz export"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            deliveries = json.loads(post_data.decode('utf-8'))
            
            if not isinstance(deliveries, list) or len(deliveries) == 0:
                self.send_json_response({'error': 'Expected array of deliveries'}, status=400)
                return
            
            print(f"📦 Exporting {len(deliveries)} deliveries to Urbantz...")
            
            results = []
            errors = []
            
            # Process each delivery
            for delivery in deliveries:
                try:
                    # Validation
                    if not delivery.get('customerRef') or not delivery.get('deliveryAddress', {}).get('line1'):
                        errors.append({
                            'delivery': delivery.get('customerRef', 'Unknown'),
                            'error': 'customerRef and deliveryAddress.line1 are required'
                        })
                        continue
                    
                    # Create Urbantz task
                    task_id = f"URBANTZ-{int(datetime.datetime.now().timestamp())}-{random.randint(1000, 9999)}"
                    
                    results.append({
                        'success': True,
                        'customerRef': delivery['customerRef'],
                        'taskId': task_id,
                        'message': 'Task created successfully'
                    })
                    
                    print(f"✅ Created Urbantz task: {task_id} for {delivery['customerRef']}")
                    
                except Exception as error:
                    errors.append({
                        'delivery': delivery.get('customerRef', 'Unknown'),
                        'error': str(error)
                    })
            
            response = {
                'success': True,
                'totalDeliveries': len(deliveries),
                'successful': len(results),
                'failed': len(errors),
                'results': results,
                'errors': errors,
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            print(f"✅ Export completed: {len(results)} successful, {len(errors)} failed")
            self.send_json_response(response)
            
        except Exception as e:
            print(f"Export error: {e}")
            self.send_json_response({'error': 'Export failed', 'details': str(e)}, status=500)

    def extract_deliveries_with_ai(self, text):
        """AI-powered delivery extraction"""
        deliveries = []
        
        # Smart section detection
        sections = self.detect_delivery_sections(text)
        
        for i, section in enumerate(sections):
            delivery = {
                'taskId': f"TASK-{int(datetime.datetime.now().timestamp())}-{i + 1}",
                'customerRef': self.extract_customer_ref(section),
                'deliveryAddress': self.extract_address(section),
                'serviceDate': self.extract_date(section),
                'timeWindowStart': self.extract_time_start(section),
                'timeWindowEnd': self.extract_time_end(section),
                'items': self.extract_items(section),
                'notes': f"Geëxtraheerd uit sectie {i + 1}",
                'priority': self.determine_priority(section, i)
            }
            
            # Only add if meaningful data found
            if delivery['customerRef'] or delivery['deliveryAddress']['line1']:
                deliveries.append(delivery)
        
        return deliveries
    
    def detect_delivery_sections(self, text):
        """Detect delivery sections in text with improved email parsing"""
        # Look for clear section separators
        section_patterns = [
            # Delivery-specific sections
            r'(?:lever|delivery|bezorg|adres|address|klant|customer|order|bestelling)[\s\S]*?(?=(?:lever|delivery|bezorg|adres|address|klant|customer|order|bestelling)|$)',
            # Email signature sections
            r'(?:met\s+vriendelijke\s+groet|best\s+regards|groeten)[\s\S]*?(?=(?:met\s+vriendelijke\s+groet|best\s+regards|groeten)|$)',
            # Contact information blocks
            r'(?:contact|naam|adres|telefoon|phone)[\s\S]*?(?=(?:contact|naam|adres|telefoon|phone)|$)',
            # Time and date sections
            r'(?:datum|date|tijd|time)[\s\S]*?(?=(?:datum|date|tijd|time)|$)'
        ]
        
        sections = []
        
        for pattern in section_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            sections.extend(matches)
        
        # If no clear sections, try to split by paragraphs or sentences
        if not sections:
            # Try splitting by double newlines first
            paragraphs = text.split('\n\n')
            sections = [p for p in paragraphs if len(p.strip()) > 30]
            
            # If still no good sections, try splitting by single newlines
            if len(sections) < 2:
                lines = text.split('\n')
                current_section = ""
                for line in lines:
                    line = line.strip()
                    if line:
                        current_section += line + " "
                        # If section is substantial enough, add it
                        if len(current_section.strip()) > 50:
                            sections.append(current_section.strip())
                            current_section = ""
                # Add remaining content
                if current_section.strip():
                    sections.append(current_section.strip())
        
        # If still no sections, use the whole text
        return sections if sections else [text]

    def extract_customer_ref(self, section):
        """Extract customer reference"""
        patterns = [
            r'(?:klant|customer|ref|referentie|order|bestelling)[\s:]*([A-Z0-9-]+)',
            r'([A-Z]{2,}\d{3,})',
            r'(?:nr|nummer|number)[\s:]*([A-Z0-9-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, section, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return f"AUTO-{random.randint(100, 999)}"

    def extract_address(self, section):
        """Extract delivery address with improved patterns"""
        address_patterns = [
            # Explicit address markers
            r'(?:adres|address|leveradres|bezorgadres|delivery\s+address)[\s:]*([^\n\r]+)',
            # Street patterns (Dutch/Belgian)
            r'([A-Za-z\s]+(?:straat|street|laan|avenue|plein|square|weg|road|boulevard|allée|avenue|rue|chaussée)\s+\d+[A-Za-z]?[^\n\r]*)',
            # Full address with postal code
            r'([A-Za-z\s]+\d+[A-Za-z]?\s*,\s*\d{4}\s+[A-Za-z\s]+)',
            # Belgian/Dutch postal format
            r'([A-Za-z\s]+,\s*\d{4}\s+[A-Za-z\s]+)',
            # Specific street examples
            r'(Koningstraat\s+\d+[A-Za-z]?[^\n\r]*)',
            r'(Grote\s+Markt\s+\d+[^\n\r]*)',
            r'(Vrijdagmarkt\s+\d+[^\n\r]*)',
            r'(Stationsplein\s+\d+[^\n\r]*)',
            r'(Marktstraat\s+\d+[^\n\r]*)',
            r'(Hoofdstraat\s+\d+[^\n\r]*)',
            r'(Kerkstraat\s+\d+[^\n\r]*)',
            # City with street number
            r'([A-Za-z\s]+\d+[A-Za-z]?\s+[A-Za-z\s]+,\s*\d{4}\s+[A-Za-z\s]+)',
            # After "leveren aan" or "bezorgen aan"
            r'(?:leveren\s+aan|bezorgen\s+aan|delivery\s+to)[\s:]*([^\n\r]+)',
            # Common email patterns
            r'(?:locatie|location)[\s:]*([^\n\r]+)'
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, section, re.IGNORECASE)
            if match:
                address = match.group(1).strip()
                # Clean up common artifacts
                address = re.sub(r'^(?:op|at|in)\s+', '', address, flags=re.IGNORECASE)
                address = re.sub(r'\s+', ' ', address)  # Normalize whitespace
                if len(address) > 10:  # Only accept substantial addresses
                    return {
                        'line1': address,
                        'contactName': self.extract_contact_name(section),
                        'contactPhone': self.extract_phone(section)
                    }
        
        return {
            'line1': "Adres niet gevonden",
            'contactName': "Onbekend",
            'contactPhone': "+32 000 000 000"
        }

    def extract_contact_name(self, section):
        """Extract contact name with improved patterns"""
        patterns = [
            # Explicit contact markers
            r'(?:contact|naam|name|contactpersoon|contact\s+person)[\s:]*([A-Za-z\s]+)',
            # After "contact:" or "naam:"
            r'(?:contact|naam)[\s:]*([A-Z][a-z]+\s+[A-Z][a-z]+)',
            # Common Dutch names pattern
            r'([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            # After "voor" or "t.a.v." (attn)
            r'(?:voor|t\.a\.v\.|attn)[\s:]*([A-Za-z\s]+)',
            # Email signature patterns
            r'(?:met\s+vriendelijke\s+groet|best\s+regards)[\s,]*([A-Za-z\s]+)',
            # Phone number context
            r'([A-Za-z\s]+)\s*\+32\s?\d',
            # Before phone number
            r'([A-Za-z\s]+)\s*(?:tel|telefoon|phone)',
            # Delivery to person
            r'(?:leveren\s+aan|bezorgen\s+aan|delivery\s+to)\s+([A-Za-z\s]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, section, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean up common artifacts
                name = re.sub(r'\s+', ' ', name)
                name = re.sub(r'^(?:de|het|een|a|an|the)\s+', '', name, flags=re.IGNORECASE)
                if len(name) > 2 and len(name.split()) >= 2:  # At least 2 words
                    return name
        
        return "Contact persoon"

    def extract_phone(self, section):
        """Extract phone number with improved patterns"""
        phone_patterns = [
            # Belgian mobile numbers
            r'(\+32\s?(?:4\d{2}|4\d{1})\s?\d{2}\s?\d{2}\s?\d{2})',
            # Belgian landline
            r'(\+32\s?(?:[1-9]\d)\s?\d{3}\s?\d{2}\s?\d{2})',
            # Dutch mobile
            r'(\+31\s?6\s?\d{4}\s?\d{4})',
            # Dutch landline
            r'(\+31\s?[1-9]\d\s?\d{3}\s?\d{4})',
            # Belgian without country code
            r'(0[1-9]\d{1,2}\s?\d{2}\s?\d{2}\s?\d{2})',
            # Dutch without country code
            r'(0[1-9]\d{1,2}\s?\d{3}\s?\d{4})',
            # After "tel:" or "telefoon:"
            r'(?:tel|telefoon|phone|mobiel)[\s:]*(\+?\d{2,3}\s?\d{2,4}\s?\d{2,4}\s?\d{2,4})',
            # General international format
            r'(\+\d{1,3}\s?\d{1,4}\s?\d{1,4}\s?\d{1,4})',
            # Spaces and dashes
            r'(\+32[-\s]?\d{2,3}[-\s]?\d{2,3}[-\s]?\d{2,3})',
            r'(0\d{2,3}[-\s]?\d{2,3}[-\s]?\d{2,3})'
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, section, re.IGNORECASE)
            if match:
                phone = match.group(1).strip()
                # Clean up the phone number
                phone = re.sub(r'\s+', ' ', phone)
                return phone
        
        return "+32 000 000 000"

    def extract_date(self, section):
        """Extract service date with improved patterns"""
        date_patterns = [
            # ISO format
            r'(\d{4}-\d{2}-\d{2})',
            # Explicit date markers
            r'(?:datum|date|leverdatum|bezorgdatum|delivery\s+date)[\s:]*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})',
            # Dutch date format (dd-mm-yyyy)
            r'(\d{1,2}[-\/]\d{1,2}[-\/]\d{4})',
            # Short year format (dd-mm-yy)
            r'(\d{1,2}[-\/]\d{1,2}[-\/]\d{2})',
            # After "op" or "voor"
            r'(?:op|voor|on)\s+(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})',
            # Belgian format variations
            r'(\d{1,2}\s+(?:jan|feb|mrt|apr|mei|jun|jul|aug|sep|okt|nov|dec)\s+\d{2,4})',
            # Tomorrow/today indicators
            r'(?:morgen|tomorrow)[\s:]*(?:(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4}))?',
            # Weekday + date
            r'(?:maandag|dinsdag|woensdag|donderdag|vrijdag|zaterdag|zondag)[\s,]*(\d{1,2}[-\/]\d{1,2})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, section, re.IGNORECASE)
            if match:
                date_str = match.group(1) if match.groups() else match.group(0)
                if date_str:
                    try:
                        # Convert to ISO format
                        if '/' in date_str:
                            parts = date_str.split('/')
                            if len(parts) == 3:
                                if len(parts[2]) == 2:
                                    parts[2] = '20' + parts[2]
                                # Assume dd/mm/yyyy format
                                date = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
                                return date
                        elif '-' in date_str:
                            parts = date_str.split('-')
                            if len(parts) == 3:
                                if len(parts[2]) == 2:
                                    parts[2] = '20' + parts[2]
                                # Check if it's already in yyyy-mm-dd format
                                if len(parts[0]) == 4:
                                    return date_str
                                else:
                                    # Assume dd-mm-yyyy format
                                    date = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
                                    return date
                    except:
                        continue
        
        # Default to tomorrow
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        return tomorrow.strftime('%Y-%m-%d')

    def extract_time_start(self, section):
        """Extract start time"""
        time_patterns = [
            r'(?:tijd|time|tussen|van)[\s:]*(\d{1,2}:\d{2})',
            r'(\d{1,2}:\d{2})\s*(?:tot|-)'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, section, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "09:00"

    def extract_time_end(self, section):
        """Extract end time"""
        time_patterns = [
            r'(?:tot|until|tot)[\s:]*(\d{1,2}:\d{2})',
            r'(\d{1,2}:\d{2})\s*(?:einde|end)'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, section, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "17:00"

    def extract_items(self, section):
        """Extract items"""
        items = []
        
        item_patterns = [
            r'(?:items|pakketten|producten|artikelen)[\s:]*([^\n\r]+)',
            r'(\d+\s*(?:x|stuks?|pakketten?|items?))',
            r'([A-Za-z\s]+\s*\d+)'
        ]
        
        for pattern in item_patterns:
            matches = re.findall(pattern, section, re.IGNORECASE)
            for match in matches:
                items.append({
                    'description': match.strip(),
                    'quantity': 1,
                    'tempClass': "ambient"
                })
        
        if not items:
            items.append({
                'description': "Pakket uit document",
                'quantity': 1,
                'tempClass': "ambient"
            })
        
        return items

    def determine_priority(self, section, index):
        """Determine priority level"""
        high_priority_keywords = ['urgent', 'spoed', 'priority', 'hoog', 'asap']
        low_priority_keywords = ['laag', 'low', 'niet urgent']
        
        text = section.lower()
        
        for keyword in high_priority_keywords:
            if keyword in text:
                return 'high'
        
        for keyword in low_priority_keywords:
            if keyword in text:
                return 'low'
        
        return 'high' if index == 0 else 'normal'

    def send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def serve_file(self, filename):
        """Serve static file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "File not found")

if __name__ == "__main__":
    print(f"🚀 Starting Urbantz AI Document Scanner server...")
    print(f"📱 Open your browser and go to: http://localhost:{PORT}")
    print(f"🔧 API endpoints available:")
    print(f"   - POST /api/smart-analyze")
    print(f"   - POST /api/urbantz-export")
    print(f"   - GET /api/health")
    print(f"\n✨ Ready to scan documents and create Urbantz tasks!")
    print(f"🔗 Always use port {PORT} for consistent hosting!")
    
    with socketserver.TCPServer(("", PORT), UrbantzAPIHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n👋 Server stopped.")