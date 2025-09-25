"""
Test script for destination selection workflow
"""

import os
from dotenv import load_dotenv
from destination_agent import DestinationResearchAgent

# Load environment variables
load_dotenv()

def test_destination_selection_workflow():
    """Test the destination selection workflow"""
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY environment variable")
        return
    
    # Initialize the destination agent
    agent = DestinationResearchAgent()
    
    print("🎯 Testing Destination Selection Workflow")
    print("=" * 60)
    
    # Test cases that should trigger destination selection
    test_cases = [
        {
            "name": "Abstract Request - Multiple Options",
            "request": "I'm looking for a sunny beach destination within 3 hours flight from SFO. I want to relax and enjoy water activities. Budget is around $1500."
        },
        {
            "name": "Multi-Location Comparison",
            "request": "I can't decide between Tokyo, Seoul, or Bangkok for a 7-day cultural trip. I'm interested in food, temples, and local experiences. Budget is $2500."
        },
        {
            "name": "Constrained Request - Multiple Options",
            "request": "I need a mountain destination within 2 hours drive from Denver. I want hiking and outdoor activities. Budget is flexible but prefer mid-range options."
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
            print(f"🔄 User Choice Required: {'Yes' if result.user_choice_required else 'No'}")
            
            if result.primary_destinations:
                print("\n🏆 Destination Options:")
                for j, dest in enumerate(result.primary_destinations, 1):
                    print(f"\n{j}. {dest.name}")
                    print(f"   📍 {dest.country}, {dest.region}")
                    print(f"   📝 {dest.description}")
                    print(f"   ⭐ Why recommended: {dest.why_recommended}")
                    if dest.key_attractions:
                        print(f"   🏛️ Top attractions: {', '.join(dest.key_attractions[:3])}")
            
            if result.user_choice_required:
                print(f"\n🎯 **Destination Selection Required**")
                print(f"I found {len(result.primary_destinations)} destination options for you.")
                print("Please choose which one you'd like to proceed with:")
                
                for j, dest in enumerate(result.primary_destinations, 1):
                    print(f"\n{j}. {dest.name}")
                    print(f"   📍 {dest.country}, {dest.region}")
                    print(f"   📝 {dest.description}")
                    print(f"   ⭐ Why recommended: {dest.why_recommended}")
                
                print(f"\nPlease respond with the number (1-{len(result.primary_destinations)}) of your preferred destination.")
                
                # Simulate user selection (in real implementation, this would wait for user input)
                selected_destination = result.primary_destinations[0]
                print(f"\n✅ Selected destination: {selected_destination.name}")
                print(f"📍 Proceeding with {selected_destination.name} for itinerary planning...")
            else:
                print(f"\n✅ Single destination found: {result.primary_destinations[0].name}")
                print("Proceeding directly to itinerary planning...")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "="*60)

def test_single_destination_workflow():
    """Test workflow with single destination (no selection needed)"""
    
    agent = DestinationResearchAgent()
    
    print("\n🎯 Testing Single Destination Workflow")
    print("=" * 50)
    
    test_request = "I want to visit Paris, France for 5 days. I'm interested in art, history, and French cuisine. My budget is around $2000."
    
    print(f"Request: {test_request}")
    print("\n🔍 Researching destination...")
    
    try:
        result = agent.research_destination(test_request)
        
        print(f"\n✅ Request Type: {result.request_type}")
        print(f"📊 Found {len(result.primary_destinations)} primary destinations")
        print(f"🔄 User Choice Required: {'Yes' if result.user_choice_required else 'No'}")
        
        if not result.user_choice_required:
            destination = result.primary_destinations[0]
            print(f"\n✅ Single destination: {destination.name}")
            print(f"📍 {destination.country}, {destination.region}")
            print(f"📝 {destination.description}")
            print("\nProceeding directly to itinerary planning...")
        else:
            print("Unexpected: Multiple destinations found for specific request")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_destination_selection_workflow()
    test_single_destination_workflow()
