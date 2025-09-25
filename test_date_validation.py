#!/usr/bin/env python3
"""
Test script for date validation functionality
"""

import os
from dotenv import load_dotenv
from travel_agent import TravelAgent
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

def test_date_validation():
    """Test that the system stops and asks for dates when not provided"""
    print("🧪 Testing Date Validation Functionality")
    print("=" * 60)
    
    # Initialize the travel agent
    agent = TravelAgent()
    
    # Test case 1: Request without dates
    print("\n📋 Test Case 1: Request without travel dates")
    print("-" * 40)
    
    request_without_dates = """
    I want to plan a trip to Paris, France for 5 days.
    My budget is $2000 and I'm interested in sightseeing, food, and culture.
    I prefer comfortable travel style and want to stay in a hotel.
    """
    
    print(f"Request: {request_without_dates.strip()}")
    
    try:
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=request_without_dates)],
            "trip_spec": None,
            "destination_research": None,
            "travel_options": None,
            "itinerary": None
        }
        
        # Run the agent
        result = agent.graph.invoke(initial_state)
        
        # Check if the workflow stopped due to missing dates
        final_messages = result.get("messages", [])
        if final_messages:
            last_message = final_messages[-1].content
            print(f"\n📝 Agent Response:")
            print(f"   {last_message}")
            
            # Check if the response indicates dates are required
            if "travel dates are required" in last_message.lower() or "specify your travel dates" in last_message.lower():
                print("✅ SUCCESS: System correctly stopped and asked for travel dates!")
            else:
                print("❌ FAILURE: System did not ask for travel dates")
        else:
            print("❌ FAILURE: No response from agent")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test case 2: Request with dates
    print("\n📋 Test Case 2: Request with travel dates")
    print("-" * 40)
    
    request_with_dates = """
    I want to plan a trip to Paris, France for 5 days in June 2024.
    My budget is $2000 and I'm interested in sightseeing, food, and culture.
    I prefer comfortable travel style and want to stay in a hotel.
    """
    
    print(f"Request: {request_with_dates.strip()}")
    
    try:
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=request_with_dates)],
            "trip_spec": None,
            "destination_research": None,
            "travel_options": None,
            "itinerary": None
        }
        
        # Run the agent
        result = agent.graph.invoke(initial_state)
        
        # Check if the workflow continued
        final_messages = result.get("messages", [])
        if final_messages:
            last_message = final_messages[-1].content
            print(f"\n📝 Agent Response:")
            print(f"   {last_message}")
            
            # Check if the response indicates dates are required
            if "travel dates are required" in last_message.lower() or "specify your travel dates" in last_message.lower():
                print("❌ FAILURE: System incorrectly asked for dates when they were provided")
            else:
                print("✅ SUCCESS: System proceeded with dates provided!")
        else:
            print("❌ FAILURE: No response from agent")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_destination_agent_directly():
    """Test the destination agent directly"""
    print("\n🧪 Testing Destination Agent Directly")
    print("=" * 60)
    
    from destination_agent import DestinationResearchAgent
    
    # Initialize the destination agent
    destination_agent = DestinationResearchAgent()
    
    # Test case 1: Request without dates
    print("\n📋 Test Case 1: Direct destination research without dates")
    print("-" * 50)
    
    request_without_dates = "I want to visit Paris, France for 5 days with a $2000 budget"
    
    try:
        result = destination_agent.research_destination(request_without_dates)
        
        print(f"Request type: {result.request_type}")
        print(f"Date required: {result.date_required}")
        print(f"Primary destinations: {len(result.primary_destinations)}")
        print(f"Travel recommendations: {result.travel_recommendations[:200]}...")
        
        if result.date_required:
            print("✅ SUCCESS: Destination agent correctly identified missing dates!")
        else:
            print("❌ FAILURE: Destination agent did not identify missing dates")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test case 2: Request with dates
    print("\n📋 Test Case 2: Direct destination research with dates")
    print("-" * 50)
    
    request_with_dates = "I want to visit Paris, France for 5 days in June 2024 with a $2000 budget"
    
    try:
        result = destination_agent.research_destination(request_with_dates)
        
        print(f"Request type: {result.request_type}")
        print(f"Date required: {result.date_required}")
        print(f"Primary destinations: {len(result.primary_destinations)}")
        print(f"Travel recommendations: {result.travel_recommendations[:200]}...")
        
        if not result.date_required:
            print("✅ SUCCESS: Destination agent correctly proceeded with dates provided!")
        else:
            print("❌ FAILURE: Destination agent incorrectly asked for dates when they were provided")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    print("🚀 Starting Date Validation Tests")
    print("=" * 60)
    
    # Test destination agent directly first
    test_destination_agent_directly()
    
    # Test full travel agent workflow
    test_date_validation()
    
    print("\n🎉 Date validation tests completed!")
