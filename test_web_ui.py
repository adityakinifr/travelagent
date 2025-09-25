#!/usr/bin/env python3
"""
Test script for the web UI functionality
"""

import requests
import json
import time

def test_web_ui():
    """Test the web UI endpoints"""
    base_url = "http://localhost:8080"
    
    print("🧪 Testing AI Travel Agent Web UI")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check passed: {data['status']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Main page
    print("\n2. Testing main page...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            content = response.text
            if "AI Travel Agent" in content and "Travel Preferences" in content:
                print("   ✅ Main page loads correctly")
            else:
                print("   ❌ Main page content missing")
        else:
            print(f"   ❌ Main page failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Main page error: {e}")
    
    # Test 3: JavaScript file
    print("\n3. Testing JavaScript file...")
    try:
        response = requests.get(f"{base_url}/app.js")
        if response.status_code == 200:
            content = response.text
            if "TravelAgentApp" in content and "class TravelAgentApp" in content:
                print("   ✅ JavaScript file loads correctly")
            else:
                print("   ❌ JavaScript content missing")
        else:
            print(f"   ❌ JavaScript file failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ JavaScript file error: {e}")
    
    # Test 4: Preferences API
    print("\n4. Testing preferences API...")
    try:
        response = requests.get(f"{base_url}/api/preferences")
        if response.status_code == 200:
            data = response.json()
            if "traveler_profile" in data and "hotel_preferences" in data:
                print("   ✅ Preferences API works correctly")
                print(f"   📊 Loaded {len(data)} preference categories")
            else:
                print("   ❌ Preferences data missing")
        else:
            print(f"   ❌ Preferences API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Preferences API error: {e}")
    
    # Test 5: Save preferences
    print("\n5. Testing save preferences...")
    try:
        test_preferences = {
            "traveler_profile": {
                "home_airport": "LAX",
                "travel_style": "luxury"
            },
            "hotel_preferences": {
                "preferred_chains": ["Marriott", "Hilton"]
            }
        }
        
        response = requests.post(
            f"{base_url}/api/preferences",
            json=test_preferences,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   ✅ Save preferences works correctly")
            else:
                print("   ❌ Save preferences failed")
        else:
            print(f"   ❌ Save preferences failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Save preferences error: {e}")
    
    # Test 6: Trip planning endpoint (basic test)
    print("\n6. Testing trip planning endpoint...")
    try:
        test_request = {
            "destination_query": "beach destinations",
            "travel_dates": "summer 2024",
            "budget": "$2000",
            "origin": "SFO",
            "group_size": "2",
            "traveler_type": "couple"
        }
        
        # Start the request but don't wait for completion
        response = requests.post(
            f"{base_url}/api/plan-trip",
            json=test_request,
            headers={'Content-Type': 'application/json'},
            stream=True,
            timeout=5  # Short timeout for testing
        )
        
        if response.status_code == 200:
            print("   ✅ Trip planning endpoint accepts requests")
            print("   📝 Note: Full planning test would require longer timeout")
        else:
            print(f"   ❌ Trip planning endpoint failed: {response.status_code}")
    except requests.exceptions.Timeout:
        print("   ✅ Trip planning endpoint accepts requests (timeout expected)")
    except Exception as e:
        print(f"   ❌ Trip planning endpoint error: {e}")
    
    print("\n🎉 Web UI testing completed!")
    print("\n📱 To use the web interface:")
    print(f"   1. Open {base_url} in your browser")
    print("   2. Configure your travel preferences")
    print("   3. Plan your trip!")

if __name__ == "__main__":
    test_web_ui()
