#!/usr/bin/env python3
"""
Test script for Urbantz AI Document Scanner API
"""

import requests
import json

# Test data
test_text = """Levering informatie:

Klant: CUST-12345
Adres: Koningstraat 15, 1000 Brussel
Contact: Jan Janssen (+32 2 123 4567)
Datum: 2024-01-15
Tijd: 09:00 - 12:00

Items: 2x Pakketten, 1x Documenten"""

def test_smart_analyze():
    """Test the smart analyze endpoint"""
    print("🔍 Testing smart analyze endpoint...")
    
    url = "http://localhost:8080/api/smart-analyze"
    data = {
        "text": test_text,
        "fileType": "text"
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        print(f"✅ Status: {response.status_code}")
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
                print(f"     Items: {len(delivery.get('items', []))} items")
                print()
        
        return result.get('deliveries', [])
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_urbantz_export(deliveries):
    """Test the Urbantz export endpoint"""
    if not deliveries:
        print("⚠️ No deliveries to export")
        return
    
    print("📦 Testing Urbantz export endpoint...")
    
    url = "http://localhost:8080/api/urbantz-export"
    
    try:
        response = requests.post(url, json=deliveries)
        result = response.json()
        
        print(f"✅ Status: {response.status_code}")
        print(f"📊 Total deliveries: {result.get('totalDeliveries', 0)}")
        print(f"✅ Successful: {result.get('successful', 0)}")
        print(f"❌ Failed: {result.get('failed', 0)}")
        
        if result.get('results'):
            print("\n🎯 Successful exports:")
            for export_result in result['results']:
                print(f"  - {export_result.get('customerRef', 'N/A')} -> {export_result.get('taskId', 'N/A')}")
        
        if result.get('errors'):
            print("\n⚠️ Export errors:")
            for error in result['errors']:
                print(f"  - {error.get('delivery', 'N/A')}: {error.get('error', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health():
    """Test the health endpoint"""
    print("🏥 Testing health endpoint...")
    
    try:
        response = requests.get("http://localhost:8080/api/health")
        result = response.json()
        
        print(f"✅ Status: {response.status_code}")
        print(f"🕐 Timestamp: {result.get('timestamp', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Urbantz AI Document Scanner - API Test Suite")
    print("=" * 50)
    
    # Test health endpoint
    test_health()
    print()
    
    # Test smart analyze
    deliveries = test_smart_analyze()
    print()
    
    # Test export
    test_urbantz_export(deliveries)
    
    print("\n✨ All tests completed!")
