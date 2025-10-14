#!/usr/bin/env python3
"""
Test script to verify Anthropic API setup
"""

import os
import sys

def test_dotenv():
    """Test if python-dotenv is installed and working"""
    print("=" * 60)
    print("1. Testing python-dotenv installation...")
    print("=" * 60)
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv is installed")
        
        # Try to load .env file
        result = load_dotenv()
        if result:
            print("✅ .env file found and loaded")
        else:
            print("⚠️  .env file not found (will use system environment)")
        
        return True
    except ImportError:
        print("❌ python-dotenv is NOT installed")
        print("   Install with: pip install python-dotenv")
        return False

def test_api_key():
    """Test if ANTHROPIC_API_KEY is set"""
    print("\n" + "=" * 60)
    print("2. Testing ANTHROPIC_API_KEY...")
    print("=" * 60)
    
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("❌ ANTHROPIC_API_KEY is NOT set")
        print("   Add it to your .env file:")
        print("   ANTHROPIC_API_KEY=sk-ant-api03-your-key-here")
        return False
    
    if api_key == "your_anthropic_api_key_here":
        print("⚠️  ANTHROPIC_API_KEY is set to the default placeholder")
        print("   Replace it with your real API key from:")
        print("   https://console.anthropic.com/")
        return False
    
    # Check if it looks like a valid key
    if not api_key.startswith('sk-ant-'):
        print("⚠️  ANTHROPIC_API_KEY doesn't look like a valid Anthropic key")
        print("   Anthropic keys usually start with 'sk-ant-'")
        print(f"   Your key starts with: {api_key[:10]}...")
        return False
    
    print(f"✅ ANTHROPIC_API_KEY is set")
    print(f"   Key starts with: {api_key[:15]}...")
    return True

def test_api_connection():
    """Test if we can connect to Anthropic API"""
    print("\n" + "=" * 60)
    print("3. Testing Anthropic API connection...")
    print("=" * 60)
    
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    
    if not api_key or api_key == "your_anthropic_api_key_here":
        print("⏭️  Skipping API test (no valid API key)")
        return False
    
    try:
        import urllib.request
        import json
        
        print("🔄 Making test request to Anthropic API...")
        
        # Simple test request
        request_data = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 100,
            "messages": [
                {
                    "role": "user",
                    "content": "Say 'API connection successful' in Dutch"
                }
            ]
        }
        
        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=json.dumps(request_data).encode('utf-8'),
            headers={
                'x-api-key': api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
        )
        
        response = urllib.request.urlopen(req, timeout=10)
        result = json.loads(response.read().decode('utf-8'))
        
        if result.get('content') and len(result['content']) > 0:
            ai_response = result['content'][0]['text']
            print(f"✅ API connection successful!")
            print(f"   Claude response: {ai_response}")
            return True
        else:
            print("⚠️  API returned unexpected response")
            print(f"   Response: {result}")
            return False
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"❌ API request failed with HTTP {e.code}")
        
        if e.code == 401:
            print("   Error: Invalid API key")
            print("   Check your ANTHROPIC_API_KEY in .env file")
        elif e.code == 429:
            print("   Error: Rate limit exceeded")
            print("   Wait a moment and try again")
        elif e.code == 500:
            print("   Error: Anthropic API server error")
            print("   Try again later")
        else:
            print(f"   Error details: {error_body}")
        
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_delivery_extraction():
    """Test delivery extraction with Claude"""
    print("\n" + "=" * 60)
    print("4. Testing delivery extraction...")
    print("=" * 60)
    
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    
    if not api_key or api_key == "your_anthropic_api_key_here":
        print("⏭️  Skipping extraction test (no valid API key)")
        return False
    
    try:
        import urllib.request
        import json
        
        # Test with a sample delivery text
        test_text = """
REF: TEST-001
Klant: Test Bedrijf BV
Adres: Teststraat 123, 1000 Brussel
Nummer: +32 470 11 22 33
Datum: 15/10/2025
Tijd: 09:00 - 12:00
Items: 2x Pakket
        """
        
        prompt = f"""
Je bent een expert in het analyseren van leveringsdocumenten. Extraheer zorgvuldig alle leveringsinformatie uit de volgende tekst.

INSTRUCTIES:
1. Identificeer alle leveringen in de tekst
2. Voor elke levering, extraheer: customerRef, deliveryAddress, serviceDate, timeWindowStart, timeWindowEnd, items, notes, priority

Tekst om te analyseren:
{test_text}

Geef het antwoord terug als een JSON array van leveringen.
"""
        
        request_data = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 2000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        print("🔄 Extracting delivery information...")
        
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
                deliveries = json.loads(ai_response)
                print(f"✅ Successfully extracted {len(deliveries) if isinstance(deliveries, list) else 1} delivery(ies)")
                print(f"\n   Example delivery:")
                print(f"   {json.dumps(deliveries[0] if isinstance(deliveries, list) else deliveries, indent=2)}")
                return True
            except json.JSONDecodeError:
                print("⚠️  Claude returned a response but it's not valid JSON")
                print(f"   Response: {ai_response[:200]}...")
                return False
        else:
            print("⚠️  API returned unexpected response")
            return False
            
    except Exception as e:
        print(f"❌ Extraction test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n🧪 ANTHROPIC API SETUP TEST\n")
    
    results = []
    
    # Test 1: python-dotenv
    results.append(("python-dotenv", test_dotenv()))
    
    # Test 2: API key
    results.append(("API Key", test_api_key()))
    
    # Test 3: API connection
    results.append(("API Connection", test_api_connection()))
    
    # Test 4: Delivery extraction
    results.append(("Delivery Extraction", test_delivery_extraction()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}  {name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print("\n" + "=" * 60)
    print(f"Results: {passed_count}/{total_count} tests passed")
    print("=" * 60)
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! Your Anthropic API setup is working correctly.")
        print("   You can now use the 'Scan met AI' feature!")
    else:
        print("\n⚠️  Some tests failed. Please follow the instructions above to fix the issues.")
        print("   See ANTHROPIC-SETUP.md for detailed setup instructions.")
    
    return passed_count == total_count

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

