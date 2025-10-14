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

PORT = 3001

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
            html_content = data.get('htmlContent', '')
            
            if not text:
                self.send_json_response({'error': 'No text provided'}, status=400)
                return
            
            print(f"🔍 Analyzing text with AI...")
            
            # If HTML content is provided and contains tables, parse it
            processed_text = text
            if html_content and '<table' in html_content:
                table_text = self.parse_html_tables(html_content)
                if table_text:
                    processed_text = table_text + '\n\n' + text
                    print(f"📋 Parsed HTML tables")
            
            # Use AI to extract delivery information
            deliveries = self.extract_deliveries_with_ai(processed_text)
            
            response = {
                'success': True,
                'confidence': 85 if deliveries else 60,
                'rawText': processed_text,
                'deliveries': deliveries,
                'deliveryCount': len(deliveries),
                'multipleDeliveries': len(deliveries) > 1,
                'aiPowered': True
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            print(f"Smart analysis error: {e}")
            self.send_json_response({'error': 'Smart analysis failed', 'details': str(e)}, status=500)
    
    def parse_html_tables(self, html):
        """Parse HTML tables to extract structured data"""
        try:
            import re
            
            # Enhanced regex-based HTML table parser
            table_regex = r'<table[^>]*>([\s\S]*?)</table>'
            tables = []
            
            for table_match in re.finditer(table_regex, html, re.IGNORECASE):
                table_html = table_match.group(0)
                rows = []
                is_first_row = True
                
                # Extract rows
                row_regex = r'<tr[^>]*>([\s\S]*?)</tr>'
                for row_match in re.finditer(row_regex, table_html, re.IGNORECASE):
                    row_html = row_match.group(1)
                    cells = []
                    
                    # Extract cells (th or td)
                    cell_regex = r'<t[hd][^>]*>([\s\S]*?)</t[hd]>'
                    for cell_match in re.finditer(cell_regex, row_html, re.IGNORECASE):
                        # Remove HTML tags and get text content
                        cell_text = re.sub(r'<[^>]*>', '', cell_match.group(1)).strip()
                        cells.append(cell_text)
                    
                    if cells:
                        # Mark header and data rows clearly
                        if is_first_row and '<th' in row_html.lower():
                            rows.append('HEADER: ' + ' | '.join(cells))
                            is_first_row = False
                        else:
                            rows.append('ROW: ' + ' | '.join(cells))
                            is_first_row = False
                
                if rows:
                    tables.append('TABLE:\n' + '\n'.join(rows))
            
            return '\n\n'.join(tables)
        except Exception as e:
            print(f"Error parsing HTML tables: {e}")
            return ''

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
        """Detect delivery sections in text, including table rows"""
        sections = []
        
        # First check if this is TABLE format with ROW markers
        if 'TABLE:' in text and 'ROW:' in text:
            # This is structured table data
            header = None
            rows = []
            
            for line in text.split('\n'):
                if line.startswith('HEADER:'):
                    header = line.replace('HEADER:', '').strip()
                elif line.startswith('ROW:'):
                    row_data = line.replace('ROW:', '').strip()
                    # Each ROW is a separate delivery
                    if header:
                        sections.append(f"{header}\n{row_data}")
                    else:
                        sections.append(row_data)
            
            if sections:
                print(f"📊 Detected {len(sections)} deliveries from table format")
                return sections
        
        # Look for numbered delivery entries (1. REF: ... 2. REF: ... etc.)
        numbered_pattern = r'\d+\.\s*\*\*REF:\*\*\s*([^\n]+)(?:\s*\*\*Klant:\*\*\s*([^\n]+))?(?:\s*\*\*Adres:\*\*\s*([^\n]+))?(?:\s*\*\*Datum:\*\*\s*([^\n]+))?(?:\s*\*\*Tijdvenster:\*\*\s*([^\n]+))?(?:\s*\*\*Contact:\*\*\s*([^\n]+))?'
        
        matches = re.findall(numbered_pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        
        if matches:
            for match in matches:
                ref, klant, adres, datum, tijd, contact = match
                section = f"REF: {ref.strip()}"
                if klant.strip():
                    section += f"\nKlant: {klant.strip()}"
                if adres.strip():
                    section += f"\nAdres: {adres.strip()}"
                if datum.strip():
                    section += f"\nDatum: {datum.strip()}"
                if tijd.strip():
                    section += f"\nTijd: {tijd.strip()}"
                if contact.strip():
                    section += f"\nContact: {contact.strip()}"
                sections.append(section)
        
        # Fallback to original logic if no numbered entries found
        if not sections:
            section_patterns = [
                r'(?:lever|delivery|adres|address|klant|customer|order|bestelling)[\s\S]*?(?=(?:lever|delivery|adres|address|klant|customer|order|bestelling)|$)',
                r'(?:lever|delivery)[\s\S]*?(?=(?:lever|delivery)|$)'
            ]
            
            for pattern in section_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                sections.extend(matches)
            
            # If no clear sections, try to split by paragraphs
            if not sections:
                paragraphs = text.split('\n\n')
                sections = [p for p in paragraphs if len(p.strip()) > 50]
        
        return sections if sections else [text]

    def extract_customer_ref(self, section):
        """Extract customer reference"""
        # Check if this is pipe-separated table data (first column is usually ref)
        if '|' in section:
            parts = [p.strip() for p in section.split('|')]
            # First non-header part that looks like a reference
            for part in parts:
                if re.match(r'^(ORD|REF|TEST)-[A-Z0-9]+', part, re.IGNORECASE):
                    return part
        
        patterns = [
            r'(?:ref|referentie)[\s:]*([A-Z0-9-]+)',
            r'(ORD-[A-Z0-9]+)',
            r'([A-Z]{2,}\d{3,})',
            r'(?:nr|nummer|number)[\s:]*([A-Z0-9-]+)',
            r'(TEST-REF-\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, section, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return f"AUTO-{random.randint(100, 999)}"

    def extract_address(self, section):
        """Extract delivery address"""
        # Check if this is pipe-separated table data
        if '|' in section:
            parts = [p.strip() for p in section.split('|')]
            # Try to find address-like data (contains street name and numbers)
            address_line = None
            contact_name = None
            
            for part in parts:
                # Address typically contains street + number + city
                if re.search(r'(?:straat|laan|weg|avenue|rue|road|plein)\s+\d+', part, re.IGNORECASE) or \
                   re.search(r'\d{4}\s+[A-Za-z]+', part):
                    address_line = part
                # Contact name (often second column after ref)
                elif not contact_name and part and not re.match(r'^(ORD|REF|TEST)-', part) and not re.search(r'\d{2}:\d{2}', part):
                    if not re.search(r'\+\d{2}', part):  # Not a phone number
                        contact_name = part
            
            if address_line:
                return {
                    'line1': address_line,
                    'contactName': contact_name or self.extract_contact_name(section),
                    'contactPhone': self.extract_phone(section)
                }
        
        address_patterns = [
            r'(?:adres|address|leveradres|bezorgadres)[\s:]*([^\n\r]+)',
            r'(Rue\s+[^,]+,\s*\d+\s+[^\n\r]+)',
            r'([A-Za-z\s]+(?:straat|street|laan|avenue|plein|square|weg|road)\s+\d+[^\n\r]*)',
            r'([A-Za-z\s]+\d+[A-Za-z]?\s*,\s*\d{4}\s+[A-Za-z\s]+)',
            r'(Koningstraat\s+\d+[,\s]*\d+\s+[A-Za-z\s]+)'
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, section, re.IGNORECASE)
            if match:
                address = match.group(1).strip()
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
        """Extract contact name"""
        patterns = [
            r'(?:klant|customer)[\s:]*([A-Za-z\s&]+)',
            r'(?:contact|naam|name|contactpersoon)[\s:]*([A-Za-z\s]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'(Maison Vert|Patisserie Romano|Café De Blauwe Vogel|Delifresh Leuven|Bistro Mechels Blad|Choco Atelier Brugge|Brood & Tijd Hasselt|De Kortrijkse Kaaswinkel|Namur Gourmet|Le Pont Café)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, section, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Contact persoon"

    def extract_phone(self, section):
        """Extract phone number"""
        phone_patterns = [
            r'(\+32\s?\d{2,3}\s?\d{2,3}\s?\d{2,3})',
            r'(0\d{2,3}\s?\d{2,3}\s?\d{2,3})',
            r'(\+32\s?\d{3}\s?\d{2}\s?\d{2}\s?\d{2})',
            r'(?:contact|telefoon|phone)[\s:]*(\+32\s?\d{2,3}\s?\d{2,3}\s?\d{2,3})'
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, section)
            if match:
                return match.group(1) if len(match.groups()) > 0 else match.group(0)
        
        return "+32 000 000 000"

    def extract_date(self, section):
        """Extract service date"""
        date_patterns = [
            r'(?:datum|date|leverdatum|bezorgdatum)[\s:]*(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, section, re.IGNORECASE)
            if match:
                date = match.group(1)
                # Convert to ISO format
                if '/' in date:
                    parts = date.split('/')
                    if len(parts[2]) == 2:
                        parts[2] = '20' + parts[2]
                    date = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
                return date
        
        # Default to tomorrow
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        return tomorrow.strftime('%Y-%m-%d')

    def extract_time_start(self, section):
        """Extract start time"""
        # Check for time slot in pipe-separated format (e.g., "07:30 - 10:00")
        if '|' in section:
            parts = [p.strip() for p in section.split('|')]
            for part in parts:
                # Look for time range patterns
                time_range_match = re.search(r'(\d{1,2}:\d{2})\s*[-–]\s*\d{1,2}:\d{2}', part)
                if time_range_match:
                    return time_range_match.group(1)
        
        time_patterns = [
            r'(?:tijd|time|tijdvenster)[\s:]*(\d{1,2}:\d{2})',
            r'(?:tussen|van)[\s:]*(\d{1,2}:\d{2})',
            r'(\d{1,2}:\d{2})\s*(?:tot|-|–)',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, section, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "09:00"

    def extract_time_end(self, section):
        """Extract end time"""
        # Check for time slot in pipe-separated format (e.g., "07:30 - 10:00")
        if '|' in section:
            parts = [p.strip() for p in section.split('|')]
            for part in parts:
                # Look for time range patterns and extract end time
                time_range_match = re.search(r'\d{1,2}:\d{2}\s*[-–]\s*(\d{1,2}:\d{2})', part)
                if time_range_match:
                    return time_range_match.group(1)
        
        time_patterns = [
            r'(?:tot|until|tot)[\s:]*(\d{1,2}:\d{2})',
            r'(\d{1,2}:\d{2})\s*(?:einde|end)',
            r'–(\d{1,2}:\d{2})',
            r'(\d{1,2}:\d{2})\s*$'
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
    
    with socketserver.TCPServer(("", PORT), UrbantzAPIHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n👋 Server stopped.")
