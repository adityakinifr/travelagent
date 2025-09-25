#!/usr/bin/env python3
"""
Test script for the detailed progress tracking
"""

import requests
import json

def test_detailed_progress():
    """Test the detailed progress tracking functionality"""
    base_url = "http://localhost:8080"
    
    print("🧪 Testing Detailed Progress Tracking")
    print("=" * 50)
    
    # Test trip planning with detailed progress
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
                                    for i, substep in enumerate(data['substeps'][:3], 1):  # Show first 3
                                        print(f"         {i}. {substep}")
                                    if len(data['substeps']) > 3:
                                        print(f"         ... and {len(data['substeps']) - 3} more")
                                print()
                            
                            # Stop after getting a few updates
                            if len(progress_updates) >= 3:
                                break
                                
                        except json.JSONDecodeError:
                            continue
            
            # Verify we got detailed progress updates
            step_updates = [u for u in progress_updates if u.get('type') == 'step']
            if step_updates:
                print(f"   ✅ Received {len(step_updates)} detailed progress updates")
                
                # Check if updates have details and substeps
                detailed_updates = [u for u in step_updates if u.get('details') and u.get('substeps')]
                if detailed_updates:
                    print(f"   ✅ {len(detailed_updates)} updates include detailed information")
                else:
                    print("   ⚠️  No updates with detailed information found")
            else:
                print("   ❌ No step updates received")
                
        else:
            print(f"   ❌ Trip planning failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error testing progress: {e}")
    
    print("\n🎉 Detailed progress testing completed!")
    print("\n📱 Enhanced progress features:")
    print("   • Detailed processing information for each step")
    print("   • List of current tasks being performed")
    print("   • Real-time updates on what the system is processing")
    print("   • Visual progress indicators with substeps")

if __name__ == "__main__":
    test_detailed_progress()
