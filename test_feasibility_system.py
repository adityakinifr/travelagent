"""
Test script for the feasibility checking and backtracking system
"""

import os
from dotenv import load_dotenv
from destination_agent import DestinationResearchAgent
from feasibility_checker import FeasibilityChecker

# Load environment variables
load_dotenv()

def test_feasibility_checker():
    """Test the feasibility checker directly"""
    
    print("🔍 Testing Feasibility Checker")
    print("=" * 50)
    
    # Initialize the feasibility checker
    checker = FeasibilityChecker()
    
    # Test cases with different scenarios
    test_cases = [
        {
            "name": "Budget Constraint Test",
            "destination": "Monterey, CA",
            "origin": "SFO",
            "travel_dates": "summer",
            "budget": "$500",  # Low budget
            "traveler_type": "leisure"
        },
        {
            "name": "Flight Availability Test",
            "destination": "Paris, France",
            "origin": "SFO",
            "travel_dates": "summer",
            "budget": "$2000",
            "traveler_type": "leisure"
        },
        {
            "name": "Business Traveler Test",
            "destination": "New York, NY",
            "origin": "SFO",
            "travel_dates": "summer",
            "budget": "$1500",
            "traveler_type": "business"
        },
        {
            "name": "Family Traveler Test",
            "destination": "San Diego, CA",
            "origin": "SFO",
            "travel_dates": "summer",
            "budget": "$1000",
            "traveler_type": "family_with_kids"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            result = checker.check_destination_feasibility(
                destination=test_case["destination"],
                origin=test_case["origin"],
                travel_dates=test_case["travel_dates"],
                budget=test_case["budget"],
                traveler_type=test_case["traveler_type"]
            )
            
            print(f"✅ Feasible: {result.is_feasible}")
            print(f"📊 Feasibility Score: {result.feasibility_score:.2f}/1.0")
            print(f"💰 Estimated Cost: ${result.estimated_total_cost:.0f}")
            print(f"✈️ Flight Available: {result.flight_available}")
            print(f"🏨 Hotel Available: {result.hotel_available}")
            print(f"💵 Within Budget: {result.within_budget}")
            
            if result.issues:
                print(f"⚠️ Issues: {', '.join(result.issues)}")
            
            if result.alternatives:
                print(f"🔄 Alternatives: {', '.join(result.alternatives)}")
            
            # Show detailed breakdown
            if result.details:
                print(f"\n📋 Detailed Breakdown:")
                if "flight" in result.details:
                    flight_info = result.details["flight"]
                    print(f"   ✈️ Flight: {flight_info.get('airline', 'Unknown')} - ${flight_info.get('cost', 0)}")
                
                if "hotel" in result.details:
                    hotel_info = result.details["hotel"]
                    print(f"   🏨 Hotel: {hotel_info.get('hotel_name', 'Unknown')} - ${hotel_info.get('cost', 0)}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

def test_multiple_destinations():
    """Test feasibility checking for multiple destinations"""
    
    print("\n\n🔍 Testing Multiple Destinations Feasibility")
    print("=" * 50)
    
    checker = FeasibilityChecker()
    
    destinations = [
        "Monterey, CA",
        "Carmel, CA", 
        "Santa Barbara, CA",
        "San Diego, CA",
        "Las Vegas, NV"
    ]
    
    origin = "SFO"
    travel_dates = "summer"
    budget = "$1200"
    traveler_type = "leisure"
    
    print(f"Checking {len(destinations)} destinations from {origin}")
    print(f"Budget: {budget}, Traveler Type: {traveler_type}")
    
    try:
        results = checker.check_multiple_destinations(
            destinations=destinations,
            origin=origin,
            travel_dates=travel_dates,
            budget=budget,
            traveler_type=traveler_type
        )
        
        print(f"\n📊 Feasibility Results (ranked by score):")
        for i, (destination, result) in enumerate(results, 1):
            print(f"\n{i}. {destination}")
            print(f"   Score: {result.feasibility_score:.2f}/1.0")
            print(f"   Feasible: {result.is_feasible}")
            print(f"   Cost: ${result.estimated_total_cost:.0f}")
            
            if result.issues:
                print(f"   Issues: {', '.join(result.issues[:2])}")  # Show first 2 issues
        
        # Get only feasible destinations
        feasible_results = checker.get_feasible_destinations(
            destinations=destinations,
            origin=origin,
            travel_dates=travel_dates,
            budget=budget,
            traveler_type=traveler_type,
            min_feasibility_score=0.6
        )
        
        print(f"\n✅ Feasible Destinations ({len(feasible_results)}):")
        for destination, result in feasible_results:
            print(f"   - {destination}: ${result.estimated_total_cost:.0f}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_budget_adjustments():
    """Test budget adjustment suggestions"""
    
    print("\n\n💰 Testing Budget Adjustment Suggestions")
    print("=" * 50)
    
    checker = FeasibilityChecker()
    
    test_cases = [
        {
            "destination": "Monterey, CA",
            "origin": "SFO",
            "travel_dates": "summer",
            "current_budget": "$300",  # Very low budget
            "traveler_type": "leisure"
        },
        {
            "destination": "New York, NY",
            "origin": "SFO",
            "travel_dates": "summer",
            "current_budget": "$800",  # Low budget for cross-country
            "traveler_type": "business"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['destination']}")
        print("-" * 40)
        
        try:
            suggestions = checker.suggest_budget_adjustments(
                destination=test_case["destination"],
                origin=test_case["origin"],
                travel_dates=test_case["travel_dates"],
                current_budget=test_case["current_budget"],
                traveler_type=test_case["traveler_type"]
            )
            
            if suggestions["adjustment_needed"]:
                print(f"💰 Current Budget: ${suggestions['current_budget']:.0f}")
                print(f"💸 Estimated Cost: ${suggestions['estimated_cost']:.0f}")
                print(f"📈 Increase Needed: ${suggestions['increase_needed']:.0f} ({suggestions['increase_percentage']:.1f}%)")
                print(f"💡 Suggested Budget: {suggestions['suggested_budget']}")
                
                if suggestions["alternatives"]:
                    print(f"🔄 Alternatives: {', '.join(suggestions['alternatives'])}")
            else:
                print(f"✅ {suggestions['message']}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_destination_agent_with_feasibility():
    """Test the destination agent with feasibility checking"""
    
    print("\n\n🎯 Testing Destination Agent with Feasibility")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY environment variable")
        return
    
    # Initialize the destination agent
    agent = DestinationResearchAgent()
    
    test_cases = [
        {
            "name": "Low Budget Beach Trip",
            "request": "I want a beach destination within 3 hours of SFO for summer vacation. My budget is only $400 for the whole trip."
        },
        {
            "name": "Business Trip with Constraints",
            "request": "I need a business destination within 2 hours of NYC for a work trip. Budget is $800 and I need good hotels and direct flights."
        },
        {
            "name": "Family Trip with High Requirements",
            "request": "We're a family with 2 kids looking for a fun destination within 4 hours of LAX. We need family-friendly hotels and activities. Budget is $1500."
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print("-" * 50)
        print(f"Request: {test_case['request']}")
        print("\n🔍 Researching with feasibility checking...")
        
        try:
            # Use the new feasibility-enabled method
            result = agent.research_destination_with_feasibility(
                user_request=test_case["request"],
                check_feasibility=True,
                min_feasibility_score=0.6
            )
            
            print(f"\n✅ Request Type: {result.request_type}")
            print(f"📊 Found {len(result.primary_destinations)} primary destinations")
            print(f"🎯 User Choice Required: {result.user_choice_required}")
            
            if result.primary_destinations:
                print(f"\n🏆 Feasible Destination Recommendations:")
                for j, dest in enumerate(result.primary_destinations, 1):
                    print(f"\n{j}. {dest.name}")
                    print(f"   📍 {dest.country}, {dest.region}")
                    print(f"   📝 {dest.description}")
                    
                    if dest.estimated_cost:
                        print(f"   💰 Estimated Cost: {dest.estimated_cost}")
                    
                    if dest.travel_time_from_origin:
                        print(f"   ⏱️ Travel Time: {dest.travel_time_from_origin}")
                    
                    if dest.family_friendly_score:
                        print(f"   👨‍👩‍👧‍👦 Family-friendly: {dest.family_friendly_score}/10")
                    
                    print(f"   🎯 Why recommended: {dest.why_recommended}")
            
            # Show feasibility analysis if present
            if "Feasibility Analysis" in result.travel_recommendations:
                print(f"\n📊 Feasibility Analysis included in recommendations")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_feasibility_checker()
    test_multiple_destinations()
    test_budget_adjustments()
    test_destination_agent_with_feasibility()
