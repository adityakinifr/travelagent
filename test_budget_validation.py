#!/usr/bin/env python3
"""
Test script for budget validation functionality
"""

import os
from dotenv import load_dotenv
from travel_agent import TravelAgent
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

def test_budget_validation():
    """Test that the system stops and asks for budget when not provided"""
    print("🧪 Testing Budget Validation Functionality")
    print("=" * 60)
    
    # Initialize the travel agent
    agent = TravelAgent()
    
    # Test case 1: Request without budget
    print("\n📋 Test Case 1: Request without budget")
    print("-" * 40)
    
    request_without_budget = """
    I want to plan a trip to Paris, France for 5 days in June 2024.
    I'm interested in sightseeing, food, and culture.
    I prefer comfortable travel style and want to stay in a hotel.
    """
    
    print(f"Request: {request_without_budget.strip()}")
    
    try:
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=request_without_budget)],
            "trip_spec": None,
            "destination_research": None,
            "travel_options": None,
            "itinerary": None
        }
        
        # Run the agent
        result = agent.graph.invoke(initial_state)
        
        # Check if the workflow stopped due to missing budget
        final_messages = result.get("messages", [])
        if final_messages:
            last_message = final_messages[-1].content
            print(f"\n📝 Agent Response:")
            print(f"   {last_message}")
            
            # Check if the response indicates budget is required
            if "budget is required" in last_message.lower() or "specify your budget" in last_message.lower():
                print("✅ SUCCESS: System correctly stopped and asked for budget!")
            else:
                print("❌ FAILURE: System did not ask for budget")
        else:
            print("❌ FAILURE: No response from agent")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test case 2: Request with budget
    print("\n📋 Test Case 2: Request with budget")
    print("-" * 40)
    
    request_with_budget = """
    I want to plan a trip to Paris, France for 5 days in June 2024.
    My budget is $2000 and I'm interested in sightseeing, food, and culture.
    I prefer comfortable travel style and want to stay in a hotel.
    """
    
    print(f"Request: {request_with_budget.strip()}")
    
    try:
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=request_with_budget)],
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
            
            # Check if the response indicates budget is required
            if "budget is required" in last_message.lower() or "specify your budget" in last_message.lower():
                print("❌ FAILURE: System incorrectly asked for budget when it was provided")
            else:
                print("✅ SUCCESS: System proceeded with budget provided!")
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
    
    # Test case 1: Request without budget
    print("\n📋 Test Case 1: Direct destination research without budget")
    print("-" * 50)
    
    request_without_budget = "I want to visit Paris, France for 5 days in June 2024"
    
    try:
        result = destination_agent.research_destination(request_without_budget)
        
        print(f"Request type: {result.request_type}")
        print(f"Date required: {result.date_required}")
        print(f"Budget required: {result.budget_required}")
        print(f"Primary destinations: {len(result.primary_destinations)}")
        print(f"Travel recommendations: {result.travel_recommendations[:200]}...")
        
        if result.budget_required:
            print("✅ SUCCESS: Destination agent correctly identified missing budget!")
        else:
            print("❌ FAILURE: Destination agent did not identify missing budget")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test case 2: Request with budget
    print("\n📋 Test Case 2: Direct destination research with budget")
    print("-" * 50)
    
    request_with_budget = "I want to visit Paris, France for 5 days in June 2024 with a $2000 budget"
    
    try:
        result = destination_agent.research_destination(request_with_budget)
        
        print(f"Request type: {result.request_type}")
        print(f"Date required: {result.date_required}")
        print(f"Budget required: {result.budget_required}")
        print(f"Primary destinations: {len(result.primary_destinations)}")
        print(f"Travel recommendations: {result.travel_recommendations[:200]}...")
        
        if not result.budget_required:
            print("✅ SUCCESS: Destination agent correctly proceeded with budget provided!")
        else:
            print("❌ FAILURE: Destination agent incorrectly asked for budget when it was provided")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_both_missing():
    """Test when both dates and budget are missing"""
    print("\n🧪 Testing Both Dates and Budget Missing")
    print("=" * 60)
    
    from destination_agent import DestinationResearchAgent
    
    # Initialize the destination agent
    destination_agent = DestinationResearchAgent()
    
    # Test case: Request without dates or budget
    print("\n📋 Test Case: Direct destination research without dates or budget")
    print("-" * 60)
    
    request_without_both = "I want to visit Paris, France for 5 days"
    
    try:
        result = destination_agent.research_destination(request_without_both)
        
        print(f"Request type: {result.request_type}")
        print(f"Date required: {result.date_required}")
        print(f"Budget required: {result.budget_required}")
        print(f"Primary destinations: {len(result.primary_destinations)}")
        print(f"Travel recommendations: {result.travel_recommendations[:200]}...")
        
        if result.date_required:
            print("✅ SUCCESS: Destination agent correctly identified missing dates!")
        elif result.budget_required:
            print("✅ SUCCESS: Destination agent correctly identified missing budget!")
        else:
            print("❌ FAILURE: Destination agent did not identify missing requirements")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    print("🚀 Starting Budget Validation Tests")
    print("=" * 60)
    
    # Test destination agent directly first
    test_destination_agent_directly()
    
    # Test both missing
    test_both_missing()
    
    # Test full travel agent workflow
    test_budget_validation()
    
    print("\n🎉 Budget validation tests completed!")
