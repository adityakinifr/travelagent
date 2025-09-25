"""
Debug script to test the Hydra, Greece bug specifically
"""

import os
from dotenv import load_dotenv
from destination_agent import DestinationResearchAgent

# Load environment variables
load_dotenv()

def debug_hydra_bug():
    """Debug the specific Hydra, Greece bug"""
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY environment variable")
        return
    
    # Initialize the destination agent
    agent = DestinationResearchAgent()
    
    print("🐛 Debugging Hydra, Greece Bug")
    print("=" * 50)
    
    # Test the exact request that's causing the issue
    test_request = "I'm looking for a sunny beach destination that's within 3 hours from SFO"
    
    print(f"Test Request: {test_request}")
    print("\n" + "="*50)
    
    try:
        # Research the destination
        result = agent.research_destination(test_request)
        
        print(f"\n📊 Results:")
        print(f"   Request Type: {result.request_type}")
        print(f"   Primary Destinations: {len(result.primary_destinations)}")
        print(f"   User Choice Required: {result.user_choice_required}")
        
        if result.primary_destinations:
            print(f"\n🏆 Destination Options:")
            for i, dest in enumerate(result.primary_destinations, 1):
                print(f"\n{i}. {dest.name}")
                print(f"   📍 {dest.country}, {dest.region}")
                print(f"   📝 {dest.description}")
                
                # Check specifically for Hydra, Greece
                if 'HYDRA' in dest.name.upper() or 'GREECE' in dest.name.upper():
                    print(f"   ❌ BUG CONFIRMED: {dest.name} is NOT within 3 hours of SFO!")
                    print(f"   🛠️ This should have been filtered out by validation")
                else:
                    print(f"   ✅ Valid: {dest.name} is within reasonable distance of SFO")
        else:
            print("\n⚠️ No destinations found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_hydra_bug()
