#!/usr/bin/env python3
"""
Test script for the specific BD Bike email
"""

import requests
import json

# Your specific email content
test_email = """**Onderwerp:** Overzicht van 10 leveringen – BD Bike

Hey,

Hierbij een overzicht van **10 leveringen** die ingepland staan voor uitvoering.
**Klant:** BD Bike

1. **REF:** TEST-REF-123
   **Klant:** Maison Vert
   **Adres:** Rue de Test 10, 1000 Brussel
   **Datum:** 11/10/2025 — **Tijdvenster:** 09:00–12:00
   **Contact:** +32 470 11 22 33

2. **REF:** ORD-A2410
   **Klant:** Patisserie Romano
   **Adres:** Italiëlei 120, 2000 Antwerpen
   **Datum:** 11/10/2025 — **Tijdvenster:** 13:00–16:00
   **Contact:** +32 474 56 78 90

3. **REF:** ORD-G2411
   **Klant:** Café De Blauwe Vogel
   **Adres:** Sint-Pietersnieuwstraat 41, 9000 Gent
   **Datum:** 11/10/2025 — **Tijdvenster:** 10:00–12:00
   **Contact:** +32 498 20 45 11

4. **REF:** ORD-L2412
   **Klant:** Delifresh Leuven
   **Adres:** Bondgenotenlaan 85, 3000 Leuven
   **Datum:** 11/10/2025 — **Tijdvenster:** 14:00–17:00
   **Contact:** +32 495 88 77 66

5. **REF:** ORD-M2413
   **Klant:** Bistro Mechels Blad
   **Adres:** Bruul 48, 2800 Mechelen
   **Datum:** 11/10/2025 — **Tijdvenster:** 08:00–10:00
   **Contact:** +32 472 31 20 54

6. **REF:** ORD-B2414
   **Klant:** Choco Atelier Brugge
   **Adres:** Steenstraat 66, 8000 Brugge
   **Datum:** 11/10/2025 — **Tijdvenster:** 11:00–13:00
   **Contact:** +32 499 14 52 20

7. **REF:** ORD-H2415
   **Klant:** Brood & Tijd Hasselt
   **Adres:** Koning Albertstraat 22, 3500 Hasselt
   **Datum:** 11/10/2025 — **Tijdvenster:** 15:00–18:00
   **Contact:** +32 493 77 81 42

8. **REF:** ORD-K2416
   **Klant:** De Kortrijkse Kaaswinkel
   **Adres:** Doorniksestraat 12, 8500 Kortrijk
   **Datum:** 11/10/2025 — **Tijdvenster:** 09:30–11:30
   **Contact:** +32 476 33 58 90

9. **REF:** ORD-N2417
   **Klant:** Namur Gourmet
   **Adres:** Rue de Fer 23, 5000 Namen
   **Datum:** 11/10/2025 — **Tijdvenster:** 12:30–14:30
   **Contact:** +32 485 12 67 90

10. **REF:** ORD-LIE2418
    **Klant:** Le Pont Café
    **Adres:** Rue du Pont 5, 4000 Luik
    **Datum:** 11/10/2025 — **Tijdvenster:** 16:00–19:00
    **Contact:** +32 471 45 89 22

Laat gerust weten als er nog aanpassingen nodig zijn in adressen, tijdvensters of contactpersonen.
Dan werk ik het meteen bij in de planning.

Met vriendelijke groeten,
**Mats Domus**"""

def test_bd_bike_email():
    """Test the BD Bike email extraction"""
    print("🚚 Testing BD Bike email extraction...")
    print("=" * 60)
    
    url = "http://localhost:3001/api/smart-analyze"
    data = {
        "text": test_email,
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
            print(f"\n📋 Extracted deliveries ({len(result['deliveries'])}):")
            print("-" * 60)
            
            for i, delivery in enumerate(result['deliveries'], 1):
                print(f"\n{i}. 📦 {delivery.get('customerRef', 'N/A')}")
                print(f"   🏢 Klant: {delivery.get('deliveryAddress', {}).get('contactName', 'N/A')}")
                print(f"   📍 Adres: {delivery.get('deliveryAddress', {}).get('line1', 'N/A')}")
                print(f"   📞 Telefoon: {delivery.get('deliveryAddress', {}).get('contactPhone', 'N/A')}")
                print(f"   📅 Datum: {delivery.get('serviceDate', 'N/A')}")
                print(f"   ⏰ Tijd: {delivery.get('timeWindowStart', 'N/A')} - {delivery.get('timeWindowEnd', 'N/A')}")
                print(f"   📦 Items: {len(delivery.get('items', []))} items")
                print(f"   🎯 Prioriteit: {delivery.get('priority', 'N/A')}")
                
                # Check if extraction was successful
                success = (
                    delivery.get('customerRef') and 
                    delivery.get('deliveryAddress', {}).get('line1') != "Adres niet gevonden" and
                    delivery.get('deliveryAddress', {}).get('contactName') != "Onbekend" and
                    delivery.get('deliveryAddress', {}).get('contactPhone') != "+32 000 000 000"
                )
                
                status = "✅ GOED" if success else "❌ PROBLEEM"
                print(f"   Status: {status}")
        
        # Summary
        total_deliveries = len(result.get('deliveries', []))
        good_extractions = sum(1 for d in result.get('deliveries', []) 
                             if (d.get('customerRef') and 
                                 d.get('deliveryAddress', {}).get('line1') != "Adres niet gevonden" and
                                 d.get('deliveryAddress', {}).get('contactName') != "Onbekend" and
                                 d.get('deliveryAddress', {}).get('contactPhone') != "+32 000 000 000"))
        
        print(f"\n📊 SAMENVATTING:")
        print(f"   Totaal leveringen: {total_deliveries}")
        print(f"   Goede extracties: {good_extractions}")
        print(f"   Problematische extracties: {total_deliveries - good_extractions}")
        print(f"   Succespercentage: {(good_extractions/total_deliveries*100):.1f}%" if total_deliveries > 0 else "N/A")
        
        return result.get('deliveries', [])
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

if __name__ == "__main__":
    print("🚀 BD Bike Email Test Suite")
    print("=" * 60)
    
    deliveries = test_bd_bike_email()
    
    if deliveries:
        print(f"\n✨ Test completed! Found {len(deliveries)} deliveries.")
        print("\n💡 Tip: Als er nog problemen zijn, kunnen we de regex patterns verder verfijnen.")
    else:
        print("\n⚠️ No deliveries found. Check server status.")
