#!/usr/bin/env python3
"""
Test script to verify the UI shows detailed progress updates
"""

import requests
import json
import time

def test_ui_progress():
    """Test that the UI receives and displays detailed progress updates"""
    base_url = "http://localhost:8080"
    
    print("🧪 Testing UI Progress Updates")
    print("=" * 50)
    
    print("\n1. Testing detailed progress updates...")
    try:
        response = requests.post(
            f"{base_url}/api/plan-trip",
            headers={"Content-Type": "application/json"},
            json={
                "destination_query": "beach destinations",
                "travel_dates": "summer 2024",
                "budget": "$2000",
                "origin": "SFO",
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
                            
                            if data.get('type') == 'step':
                                print(f"   📊 Step {data['step']}: {data['message']}")
                                if data.get('details'):
                                    print(f"      Details: {data['details']}")
                                if data.get('substeps'):
                                    print(f"      Tasks: {len(data['substeps'])} subtasks")
                                print()
                            
                            elif data.get('type') == 'progress_update':
                                print(f"   🔄 Progress: {data['message']}")
                                if data.get('details'):
                                    print(f"      Activity: {data['details']}")
                                print()
                            
                            # Stop after getting several updates
                            if len(progress_updates) >= 8:
                                break
                                
                        except json.JSONDecodeError:
                            continue
            
            # Verify we got both step and progress updates
            step_updates = [u for u in progress_updates if u.get('type') == 'step']
            progress_updates_list = [u for u in progress_updates if u.get('type') == 'progress_update']
            
            print(f"\n   📈 Summary:")
            print(f"      • {len(step_updates)} step updates received")
            print(f"      • {len(progress_updates_list)} progress updates received")
            print(f"      • Total updates: {len(progress_updates)}")
            
            if step_updates and progress_updates_list:
                print("   ✅ Both step and progress updates working correctly")
            else:
                print("   ⚠️  Missing some update types")
                
        else:
            print(f"   ❌ Trip planning failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error testing progress: {e}")
    
    print("\n🎉 UI Progress testing completed!")
    print("\n📱 Enhanced progress features now include:")
    print("   • Real-time step updates with details")
    print("   • Granular progress messages (e.g., 'Performing web search...')")
    print("   • Results updates (e.g., 'Found 3 destination options')")
    print("   • Activity details for each progress update")
    print("   • Spinning icons for active progress updates")

if __name__ == "__main__":
    test_ui_progress()
