#!/usr/bin/env python3
"""
Test script for the navigation and preferences page
"""

import requests

def test_navigation():
    """Test the navigation between pages"""
    base_url = "http://localhost:8080"
    
    print("🧪 Testing Navigation and Preferences Page")
    print("=" * 50)
    
    # Test 1: Main page
    print("\n1. Testing main page...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            content = response.text
            if "Plan Trip" in content and "Preferences" in content and "navigation" in content:
                print("   ✅ Main page loads with navigation")
            else:
                print("   ❌ Main page missing navigation elements")
        else:
            print(f"   ❌ Main page failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Main page error: {e}")
    
    # Test 2: Preferences page
    print("\n2. Testing preferences page...")
    try:
        response = requests.get(f"{base_url}/preferences.html")
        if response.status_code == 200:
            content = response.text
            if "Travel Preferences" in content and "preferences-editor" in content and "preferences.js" in content:
                print("   ✅ Preferences page loads correctly")
            else:
                print("   ❌ Preferences page content missing")
        else:
            print(f"   ❌ Preferences page failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Preferences page error: {e}")
    
    # Test 3: Preferences JavaScript
    print("\n3. Testing preferences JavaScript...")
    try:
        response = requests.get(f"{base_url}/preferences.js")
        if response.status_code == 200:
            content = response.text
            if "PreferencesManager" in content and "savePreferences" in content:
                print("   ✅ Preferences JavaScript loads correctly")
            else:
                print("   ❌ Preferences JavaScript content missing")
        else:
            print(f"   ❌ Preferences JavaScript failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Preferences JavaScript error: {e}")
    
    # Test 4: Navigation links
    print("\n4. Testing navigation structure...")
    try:
        # Test main page navigation
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            content = response.text
            if 'href="/"' in content and 'href="/preferences.html"' in content:
                print("   ✅ Navigation links present on main page")
            else:
                print("   ❌ Navigation links missing on main page")
        
        # Test preferences page navigation
        response = requests.get(f"{base_url}/preferences.html")
        if response.status_code == 200:
            content = response.text
            if 'href="/"' in content and 'href="/preferences.html"' in content:
                print("   ✅ Navigation links present on preferences page")
            else:
                print("   ❌ Navigation links missing on preferences page")
                
    except Exception as e:
        print(f"   ❌ Navigation test error: {e}")
    
    print("\n🎉 Navigation testing completed!")
    print("\n📱 To use the updated interface:")
    print(f"   1. Main page: {base_url}")
    print(f"   2. Preferences page: {base_url}/preferences.html")
    print("   3. Use the navigation dropdown to switch between pages")

if __name__ == "__main__":
    test_navigation()
