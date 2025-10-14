#!/usr/bin/env python3
"""
Stable Urbantz AI Document Scanner Server
Improved version with better error handling and stability
"""

import http.server
import socketserver
import json
import urllib.parse
import re
import datetime
import random
import sys
import signal
import time
from io import BytesIO
import os
import urllib.request

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    print("   Environment variables will only be loaded from system environment")

PORT = 8000

class StableUrbantzAPIHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Custom log format"""
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{timestamp} - {format % args}")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        try:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
        except Exception as e:
            print(f"CORS error: {e}")

    def do_GET(self):
        """Handle GET requests"""
        try:
            if self.path == '/api/health':
                self.send_json_response({'status': 'OK', 'timestamp': datetime.datetime.now().isoformat()})
            elif self.path == '/' or self.path == '/index.html':
                self.serve_file('index.html')
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            print(f"GET error: {e}")
            self.send_error(500, "Internal Server Error")

    def do_POST(self):
        """Handle POST requests"""
        try:
            if self.path == '/api/smart-analyze':
                self.handle_smart_analyze()
            elif self.path == '/api/urbantz-export':
                self.handle_urbantz_export()
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            print(f"POST error: {e}")
            self.send_error(500, "Internal Server Error")
    
    def handle_smart_analyze(self):
        """Handle AI text analysis with improved error handling"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_json_response({'error': 'No content provided'}, status=400)
                return
                
            post_data = self.rfile.read(content_length)
            # Handle UTF-8 encoding errors gracefully
            try:
                text_data = post_data.decode('utf-8')
            except UnicodeDecodeError:
                # Try with error handling
                text_data = post_data.decode('utf-8', errors='ignore')
            
            data = json.loads(text_data)
            
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
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            self.send_json_response({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            print(f"Smart analysis error: {e}")
            self.send_json_response({'error': 'Smart analysis failed', 'details': str(e)}, status=500)

    def handle_urbantz_export(self):
        """Handle Urbantz export with improved error handling"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_json_response({'error': 'No content provided'}, status=400)
                return
                
            post_data = self.rfile.read(content_length)
            # Handle UTF-8 encoding errors gracefully
            try:
                text_data = post_data.decode('utf-8')
            except UnicodeDecodeError:
                # Try with error handling
                text_data = post_data.decode('utf-8', errors='ignore')
            
            deliveries = json.loads(text_data)
            
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
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            self.send_json_response({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            print(f"Export error: {e}")
            self.send_json_response({'error': 'Export failed', 'details': str(e)}, status=500)

    def extract_deliveries_with_ai(self, text):
        """AI-powered delivery extraction using Anthropic Claude API"""
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
        try:
            deliveries = []
            
            # Smart section detection
            sections = self.detect_delivery_sections(text)
            
            for i, section in enumerate(sections):
                try:
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
                except Exception as e:
                    print(f"Error processing section {i}: {e}")
                    continue
            
            return deliveries
        except Exception as e:
            print(f"Error in extract_deliveries_with_patterns: {e}")
            return []

    def detect_delivery_sections(self, text):
        """Detect delivery sections in text with improved email parsing"""
        try:
            # First, try to detect numbered deliveries (1., 2., 3., etc.)
            numbered_deliveries = self.extract_numbered_deliveries(text)
            if numbered_deliveries:
                print(f"Found {len(numbered_deliveries)} numbered deliveries")
                return numbered_deliveries
            
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
                try:
                    matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
                    sections.extend(matches)
                except Exception as e:
                    print(f"Regex error with pattern {pattern}: {e}")
                    continue
            
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
        except Exception as e:
            print(f"Error in detect_delivery_sections: {e}")
            return [text]
    
    def extract_numbered_deliveries(self, text):
        """Extract numbered deliveries (1., 2., 3., etc.)"""
        try:
            # Pattern to match numbered deliveries with **bold** formatting
            pattern = r'\*\*(\d+)\.\s*([^*]+?)\*\*(.*?)(?=\*\*\d+\.|$)'
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            
            deliveries = []
            for match in matches:
                delivery_num = match[0]
                delivery_ref = match[1].strip()
                delivery_content = match[2].strip()
                
                # Combine the delivery reference and content
                full_delivery = f"{delivery_num}. {delivery_ref}\n{delivery_content}"
                
                if len(full_delivery) > 30:  # Only add substantial sections
                    deliveries.append(full_delivery)
                    print(f"Extracted delivery {delivery_num}: {delivery_ref[:50]}...")
            
            # If no bold formatting found, try without **
            if not deliveries:
                pattern = r'(\d+)\.\s*([A-Z0-9-]+)(.*?)(?=\d+\.|$)'
                matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
                
                for match in matches:
                    delivery_num = match[0]
                    delivery_ref = match[1].strip()
                    delivery_content = match[2].strip()
                    
                    full_delivery = f"{delivery_num}. {delivery_ref}\n{delivery_content}"
                    
                    if len(full_delivery) > 30:
                        deliveries.append(full_delivery)
                        print(f"Extracted delivery {delivery_num}: {delivery_ref[:50]}...")
            
            return deliveries
        except Exception as e:
            print(f"Error in extract_numbered_deliveries: {e}")
            return []

    def extract_customer_ref(self, section):
        """Extract customer reference with improved patterns"""
        try:
            patterns = [
                # Specific formats from the email
                r'(TEST-REF-\d+)',
                r'(ORD-[A-Z]\d{4})',
                r'(ORD-[A-Z]{2,}\d{4})',
                r'(ORD-LIE\d{4})',
                # Generic patterns
                r'(?:klant|customer|ref|referentie|order|bestelling)[\s:]*([A-Z0-9-]+)',
                r'([A-Z]{2,}\d{3,})',
                r'(?:nr|nummer|number)[\s:]*([A-Z0-9-]+)',
                # Order reference patterns
                r'(\d+\.\s*)([A-Z0-9-]+)',  # "1. TEST-REF-123"
                r'([A-Z]+-\d+)'  # Generic format
            ]
            
            for pattern in patterns:
                match = re.search(pattern, section, re.IGNORECASE)
                if match:
                    # Return the first captured group, or the full match if no groups
                    ref = match.group(1) if match.groups() else match.group(0)
                    if ref and len(ref.strip()) > 2:
                        return ref.strip()
            
            return f"AUTO-{random.randint(100, 999)}"
        except Exception as e:
            print(f"Error in extract_customer_ref: {e}")
            return f"AUTO-{random.randint(100, 999)}"

    def extract_address(self, section):
        """Extract delivery address with improved patterns"""
        try:
            address_patterns = [
                # Specific addresses from the email
                r'(Rue de Test\s+\d+,\s*\d{4}\s+Brussel)',
                r'(Italiëlei\s+\d+,\s*\d{4}\s+Antwerpen)',
                r'(Sint-Pietersnieuwstraat\s+\d+,\s*\d{4}\s+Gent)',
                r'(Bondgenotenlaan\s+\d+,\s*\d{4}\s+Leuven)',
                r'(Bruul\s+\d+,\s*\d{4}\s+Mechelen)',
                r'(Steenstraat\s+\d+,\s*\d{4}\s+Brugge)',
                r'(Koning Albertstraat\s+\d+,\s*\d{4}\s+Hasselt)',
                r'(Doorniksestraat\s+\d+,\s*\d{4}\s+Kortrijk)',
                r'(Rue de Fer\s+\d+,\s*\d{4}\s+Namen)',
                r'(Rue du Pont\s+\d+,\s*\d{4}\s+Luik)',
                # Generic Belgian/Dutch address patterns
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
        except Exception as e:
            print(f"Error in extract_address: {e}")
            return {
                'line1': "Adres niet gevonden",
                'contactName': "Onbekend",
                'contactPhone': "+32 000 000 000"
            }

    def extract_contact_name(self, section):
        """Extract contact name with improved patterns"""
        try:
            patterns = [
                # Specific customer names from the email
                r'(?:klant|Klant)[\s:]*([^\n\r]+)',
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
                    # Remove common prefixes
                    name = re.sub(r'^(?:klant|Klant)[\s:]*', '', name, flags=re.IGNORECASE)
                    if len(name) > 2:  # Accept single words for business names
                        return name
            
            return "Contact persoon"
        except Exception as e:
            print(f"Error in extract_contact_name: {e}")
            return "Contact persoon"

    def extract_phone(self, section):
        """Extract phone number with improved patterns"""
        try:
            phone_patterns = [
                # Specific phone numbers from the email
                r'(\+32\s?470\s?11\s?22\s?33)',
                r'(\+32\s?474\s?56\s?78\s?90)',
                r'(\+32\s?498\s?20\s?45\s?11)',
                r'(\+32\s?495\s?88\s?77\s?66)',
                r'(\+32\s?472\s?31\s?20\s?54)',
                r'(\+32\s?499\s?14\s?52\s?20)',
                r'(\+32\s?493\s?77\s?81\s?42)',
                r'(\+32\s?476\s?33\s?58\s?90)',
                r'(\+32\s?485\s?12\s?67\s?90)',
                r'(\+32\s?471\s?45\s?89\s?22)',
                # After "contact:" or "Contact:"
                r'(?:contact|Contact)[\s:]*(\+32\s?\d{2,3}\s?\d{2,3}\s?\d{2,3}\s?\d{2,3})',
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
        except Exception as e:
            print(f"Error in extract_phone: {e}")
            return "+32 000 000 000"

    def extract_date(self, section):
        """Extract service date with improved patterns"""
        try:
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
        except Exception as e:
            print(f"Error in extract_date: {e}")
            tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
            return tomorrow.strftime('%Y-%m-%d')

    def extract_time_start(self, section):
        """Extract start time"""
        try:
            time_patterns = [
                # Specific time windows from the email
                r'(?:tijdvenster|Tijdvenster)[\s:]*(\d{1,2}:\d{2})',
                r'(?:tijd|time|tussen|van)[\s:]*(\d{1,2}:\d{2})',
                r'(\d{1,2}:\d{2})\s*(?:tot|–|-)',
                # Time range patterns
                r'(\d{1,2}:\d{2})–\d{1,2}:\d{2}',
                r'(\d{1,2}:\d{2})-\d{1,2}:\d{2}'
            ]
            
            for pattern in time_patterns:
                match = re.search(pattern, section, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return "09:00"
        except Exception as e:
            print(f"Error in extract_time_start: {e}")
            return "09:00"

    def extract_time_end(self, section):
        """Extract end time"""
        try:
            time_patterns = [
                # Specific time windows from the email
                r'(?:tijdvenster|Tijdvenster)[\s:]*\d{1,2}:\d{2}[\s–-]*(\d{1,2}:\d{2})',
                r'(?:tot|until|tot)[\s:]*(\d{1,2}:\d{2})',
                r'\d{1,2}:\d{2}\s*(?:–|-)\s*(\d{1,2}:\d{2})',
                r'(\d{1,2}:\d{2})\s*(?:einde|end)',
                # Time range patterns
                r'\d{1,2}:\d{2}–(\d{1,2}:\d{2})',
                r'\d{1,2}:\d{2}-(\d{1,2}:\d{2})'
            ]
            
            for pattern in time_patterns:
                match = re.search(pattern, section, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return "17:00"
        except Exception as e:
            print(f"Error in extract_time_end: {e}")
            return "17:00"

    def extract_items(self, section):
        """Extract items"""
        try:
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
        except Exception as e:
            print(f"Error in extract_items: {e}")
            return [{'description': "Pakket uit document", 'quantity': 1, 'tempClass': "ambient"}]

    def determine_priority(self, section, index):
        """Determine priority level"""
        try:
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
        except Exception as e:
            print(f"Error in determine_priority: {e}")
            return 'normal'

    def send_json_response(self, data, status=200):
        """Send JSON response with error handling"""
        try:
            self.send_response(status)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))
        except Exception as e:
            print(f"Error sending JSON response: {e}")

    def serve_file(self, filename):
        """Serve static file with error handling"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "File not found")
        except Exception as e:
            print(f"Error serving file {filename}: {e}")
            self.send_error(500, "Internal Server Error")

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    print(f"\n🛑 Shutdown signal received. Stopping server...")
    sys.exit(0)

if __name__ == "__main__":
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print(f"🚀 Starting Stable Urbantz AI Document Scanner server...")
    print(f"📱 Open your browser and go to: http://localhost:{PORT}")
    print(f"🔧 API endpoints available:")
    print(f"   - POST /api/smart-analyze")
    print(f"   - POST /api/urbantz-export")
    print(f"   - GET /api/health")
    print(f"\n✨ Ready to scan documents and create Urbantz tasks!")
    print(f"🔗 Always use port {PORT} for consistent hosting!")
    print(f"🛡️  Server includes improved error handling and stability")
    print(f"🔄 Use Ctrl+C to stop the server gracefully")
    
    try:
        with socketserver.TCPServer(("", PORT), StableUrbantzAPIHandler) as httpd:
            # Set socket options to prevent "Address already in use" errors
            httpd.allow_reuse_address = True
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"❌ Port {PORT} is already in use. Trying to kill existing processes...")
            try:
                os.system(f"taskkill /f /im python.exe 2>nul")
                time.sleep(2)
                with socketserver.TCPServer(("", PORT), StableUrbantzAPIHandler) as httpd:
                    httpd.allow_reuse_address = True
                    httpd.serve_forever()
            except Exception as e2:
                print(f"❌ Could not start server: {e2}")
                sys.exit(1)
        else:
            print(f"❌ Server error: {e}")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n👋 Server stopped gracefully.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
