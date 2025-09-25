"""
Test script to verify travel time constraint validation
"""

import os
from dotenv import load_dotenv
from destination_agent import DestinationResearchAgent

# Load environment variables
load_dotenv()

def test_travel_time_validation():
    """Test that destinations are properly validated against travel time constraints"""
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY environment variable")
        return
    
    # Initialize the destination agent
    agent = DestinationResearchAgent()
    
    print("🛡️ Testing Travel Time Constraint Validation")
    print("=" * 60)
    
    # Test cases that should NOT include distant destinations
    test_cases = [
        {
            "name": "SFO to Beach Destination (3 hours)",
            "request": "I'm looking for a sunny beach destination that's within 3 hours flight from SFO. I want to relax and enjoy water activities. Budget is around $1500."
        },
        {
            "name": "NYC to Mountain Destination (2 hours)",
            "request": "I need a mountain destination within 2 hours drive from NYC. I want hiking and outdoor activities. Budget is flexible."
        },
        {
            "name": "LAX to Cultural Destination (4 hours)",
            "request": "Looking for a cultural destination within 4 hours flight from LAX. Interested in history and local experiences. Budget is $2000."
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print("-" * 50)
        print(f"Request: {test_case['request']}")
        print("\n🔍 Researching destinations...")
        
        try:
            # Research the destination
            result = agent.research_destination(test_case['request'])
            
            print(f"\n✅ Request Type: {result.request_type}")
            print(f"📊 Found {len(result.primary_destinations)} primary destinations")
            
            if result.primary_destinations:
                print("\n🏆 Destination Options:")
                for j, dest in enumerate(result.primary_destinations, 1):
                    print(f"\n{j}. {dest.name}")
                    print(f"   📍 {dest.country}, {dest.region}")
                    print(f"   📝 {dest.description}")
                    
                    # Check if this destination makes sense for the constraint
                    dest_name = dest.name.upper()
                    if 'SFO' in test_case['request'].upper() and '3 HOURS' in test_case['request'].upper():
                        # Should not include distant destinations
                        invalid_destinations = [
                            'GREECE', 'HYDRA', 'EUROPE', 'FRANCE', 'ITALY', 'SPAIN', 'GERMANY',
                            'ASIA', 'JAPAN', 'CHINA', 'KOREA', 'THAILAND', 'SINGAPORE',
                            'AUSTRALIA', 'NEW ZEALAND', 'AFRICA', 'SOUTH AMERICA'
                        ]
                        
                        if any(invalid in dest_name for invalid in invalid_destinations):
                            print(f"   ❌ ERROR: {dest.name} is NOT within 3 hours of SFO!")
                        else:
                            print(f"   ✅ Valid: {dest.name} is within reasonable distance of SFO")
                    
                    elif 'NYC' in test_case['request'].upper() and '2 HOURS' in test_case['request'].upper():
                        # Should not include distant destinations
                        invalid_destinations = [
                            'EUROPE', 'FRANCE', 'ITALY', 'SPAIN', 'GERMANY', 'GREECE',
                            'ASIA', 'JAPAN', 'CHINA', 'KOREA', 'THAILAND', 'SINGAPORE',
                            'AUSTRALIA', 'NEW ZEALAND', 'AFRICA', 'SOUTH AMERICA'
                        ]
                        
                        if any(invalid in dest_name for invalid in invalid_destinations):
                            print(f"   ❌ ERROR: {dest.name} is NOT within 2 hours of NYC!")
                        else:
                            print(f"   ✅ Valid: {dest.name} is within reasonable distance of NYC")
            
            # Check if any invalid destinations were filtered out
            if len(result.primary_destinations) == 0:
                print("\n⚠️ No destinations found - this might indicate the constraints are too restrictive")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "="*60)

def test_specific_bug_case():
    """Test the specific bug case mentioned - SFO to beach destination"""
    
    agent = DestinationResearchAgent()
    
    print("\n🐛 Testing Specific Bug Case")
    print("=" * 50)
    
    bug_request = "I'm looking for a sunny beach destination that's within 3 hours from SFO"
    
    print(f"Request: {bug_request}")
    print("\n🔍 Researching destinations...")
    
    try:
        result = agent.research_destination(bug_request)
        
        print(f"\n✅ Request Type: {result.request_type}")
        print(f"📊 Found {len(result.primary_destinations)} primary destinations")
        
        if result.primary_destinations:
            print("\n🏆 Destination Options:")
            for j, dest in enumerate(result.primary_destinations, 1):
                print(f"\n{j}. {dest.name}")
                print(f"   📍 {dest.country}, {dest.region}")
                
                # Specifically check for Hydra, Greece
                if 'HYDRA' in dest.name.upper() or 'GREECE' in dest.name.upper():
                    print(f"   ❌ BUG CONFIRMED: {dest.name} is NOT within 3 hours of SFO!")
                    print(f"   🛠️ This should have been filtered out by validation")
                else:
                    print(f"   ✅ Valid: {dest.name} is within reasonable distance of SFO")
        
        # Check if validation worked
        greece_destinations = [d for d in result.primary_destinations if 'GREECE' in d.name.upper() or 'HYDRA' in d.name.upper()]
        if greece_destinations:
            print(f"\n❌ VALIDATION FAILED: Found {len(greece_destinations)} invalid destinations")
            for dest in greece_destinations:
                print(f"   - {dest.name}")
        else:
            print(f"\n✅ VALIDATION SUCCESS: No invalid destinations found")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_travel_time_validation()
    test_specific_bug_case()
