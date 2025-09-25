#!/usr/bin/env python3
"""
Test script for luxury default budget functionality
"""

import requests
import json

def test_luxury_default_budget():
    """Test that luxury is used as default budget when none specified"""
    base_url = "http://localhost:8080"
    
    print("🧪 Testing Luxury Default Budget")
    print("=" * 50)
    
    # Test 1: No budget specified
    print("\n1. Testing with no budget specified...")
    try:
        response = requests.post(
            f"{base_url}/api/plan-trip",
            headers={"Content-Type": "application/json"},
            json={
                "destination_query": "beach destinations",
                "travel_dates": "summer",
                "origin": "SFO",
                "group_size": "2"
                # Note: no budget field
            },
            stream=True
        )
        
        if response.status_code == 200:
            print("   ✅ Trip planning request accepted")
            
            # Parse the streamed response
            progress_updates = []
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])  # Remove 'data: ' prefix
                            progress_updates.append(data)
                            
                            if data.get('type') == 'progress_update':
                                if 'luxury' in data.get('message', '').lower():
                                    print(f"   💰 Found luxury default message: {data['message']}")
                                    print(f"      Details: {data.get('details', '')}")
                                    break
                            
                            # Stop after getting several updates
                            if len(progress_updates) >= 5:
                                break
                                
                        except json.JSONDecodeError:
                            continue
            
            # Check if we found the luxury default message
            luxury_found = any('luxury' in str(update).lower() for update in progress_updates)
            if luxury_found:
                print("   ✅ Luxury default budget message found")
            else:
                print("   ⚠️  Luxury default budget message not found in updates")
                
        else:
            print(f"   ❌ Trip planning failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error testing luxury default: {e}")
    
    # Test 2: Empty budget specified
    print("\n2. Testing with empty budget...")
    try:
        response = requests.post(
            f"{base_url}/api/plan-trip",
            headers={"Content-Type": "application/json"},
            json={
                "destination_query": "city break",
                "travel_dates": "june",
                "budget": "",  # Empty budget
                "origin": "LAX",
                "group_size": "1"
            },
            stream=True
        )
        
        if response.status_code == 200:
            print("   ✅ Trip planning request accepted")
            
            # Parse the streamed response
            progress_updates = []
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])  # Remove 'data: ' prefix
                            progress_updates.append(data)
                            
                            if data.get('type') == 'progress_update':
                                if 'luxury' in data.get('message', '').lower():
                                    print(f"   💰 Found luxury default message: {data['message']}")
                                    break
                            
                            # Stop after getting several updates
                            if len(progress_updates) >= 5:
                                break
                                
                        except json.JSONDecodeError:
                            continue
            
            # Check if we found the luxury default message
            luxury_found = any('luxury' in str(update).lower() for update in progress_updates)
            if luxury_found:
                print("   ✅ Luxury default budget applied for empty budget")
            else:
                print("   ⚠️  Luxury default budget not applied for empty budget")
                
        else:
            print(f"   ❌ Trip planning failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error testing empty budget: {e}")
    
    # Test 3: Explicit budget specified (should not use default)
    print("\n3. Testing with explicit budget (should not use default)...")
    try:
        response = requests.post(
            f"{base_url}/api/plan-trip",
            headers={"Content-Type": "application/json"},
            json={
                "destination_query": "mountain destinations",
                "travel_dates": "winter",
                "budget": "$1500",  # Explicit budget
                "origin": "DEN",
                "group_size": "2"
            },
            stream=True
        )
        
        if response.status_code == 200:
            print("   ✅ Trip planning request accepted")
            
            # Parse the streamed response
            progress_updates = []
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])  # Remove 'data: ' prefix
                            progress_updates.append(data)
                            
                            if data.get('type') == 'progress_update':
                                if 'luxury' in data.get('message', '').lower():
                                    print(f"   ⚠️  Unexpected luxury default message: {data['message']}")
                                    break
                            
                            # Stop after getting several updates
                            if len(progress_updates) >= 5:
                                break
                                
                        except json.JSONDecodeError:
                            continue
            
            # Check if we found the luxury default message (should not)
            luxury_found = any('luxury' in str(update).lower() for update in progress_updates)
            if not luxury_found:
                print("   ✅ No luxury default applied when explicit budget provided")
            else:
                print("   ❌ Luxury default incorrectly applied when explicit budget provided")
                
        else:
            print(f"   ❌ Trip planning failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error testing explicit budget: {e}")
    
    print("\n🎉 Luxury default budget testing completed!")
    print("\n📱 Expected behavior:")
    print("   • No budget specified → Use luxury as default")
    print("   • Empty budget → Use luxury as default")
    print("   • Explicit budget → Use specified budget")
    print("   • Progress message should show when default is applied")

if __name__ == "__main__":
    test_luxury_default_budget()
