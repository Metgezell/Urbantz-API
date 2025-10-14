#!/usr/bin/env python3
"""
Test script voor Claude API integratie in Urbantz koppeling
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_claude_api():
    """Test de Claude API integratie"""
    
    # Test data - voorbeeld email tekst
    test_text = """
    Beste team,
    
    Hierbij de leveringsinformatie voor morgen:
    
    REF: TEST-REF-123
    Klant: Maison Vert
    Adres: Rue de Test 10, Brussel 1000
    Nummer: +32 470 11 22 33
    Datum: 11 oktober 2025
    Tijd: 09:00 - 12:00
    
    Items: 2x Planten, 1x Potgrond
    
    Met vriendelijke groeten,
    Mats Domus
    """
    
    # API endpoint
    url = "http://localhost:3001/api/smart-analyze"
    
    payload = {
        "text": test_text,
        "fileType": "text"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("🧪 Testing Claude API integration...")
        print(f"📝 Test text: {test_text[:100]}...")
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ API call successful!")
            print(f"📊 Confidence: {result.get('confidence', 'N/A')}")
            print(f"📦 Deliveries found: {result.get('deliveryCount', 0)}")
            print(f"🤖 AI Powered: {result.get('aiPowered', False)}")
            
            if result.get('deliveries'):
                print("\n📋 Extracted deliveries:")
                for i, delivery in enumerate(result['deliveries'], 1):
                    print(f"  {i}. Customer Ref: {delivery.get('customerRef', 'N/A')}")
                    print(f"     Address: {delivery.get('deliveryAddress', {}).get('line1', 'N/A')}")
                    print(f"     Contact: {delivery.get('deliveryAddress', {}).get('contactName', 'N/A')}")
                    print(f"     Phone: {delivery.get('deliveryAddress', {}).get('contactPhone', 'N/A')}")
                    print(f"     Date: {delivery.get('serviceDate', 'N/A')}")
                    print(f"     Time: {delivery.get('timeWindowStart', 'N/A')} - {delivery.get('timeWindowEnd', 'N/A')}")
                    print()
            else:
                print("❌ No deliveries extracted")
                
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on port 3001")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_environment():
    """Check if environment variables are set"""
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    print("🔧 Environment check:")
    if anthropic_key and anthropic_key != 'your_anthropic_api_key_here':
        print("✅ ANTHROPIC_API_KEY is set")
        return True
    else:
        print("❌ ANTHROPIC_API_KEY is not set or still has placeholder value")
        print("   Please set your Claude API key in the .env file")
        return False

if __name__ == "__main__":
    print("🚀 Urbantz Claude API Test")
    print("=" * 50)
    
    if check_environment():
        test_claude_api()
    else:
        print("\n📝 To use Claude AI:")
        print("1. Get an API key from https://console.anthropic.com/")
        print("2. Create a .env file in the project root")
        print("3. Add: ANTHROPIC_API_KEY=your_actual_api_key_here")
        print("4. Restart the server")
        print("\n🔄 The system will fall back to pattern matching if no API key is set")