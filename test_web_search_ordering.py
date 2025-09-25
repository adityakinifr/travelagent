#!/usr/bin/env python3
"""
Test script for enhanced web search and ordering functionality
"""

import os
from dotenv import load_dotenv
from destination_agent import DestinationResearchAgent, DestinationRequest

# Load environment variables
load_dotenv()

def test_web_search_ordering():
    """Test the enhanced web search and ordering functionality"""
    print("🧪 Testing Enhanced Web Search and Ordering")
    print("=" * 60)
    
    # Initialize the destination research agent
    agent = DestinationResearchAgent()
    
    # Test case 1: Abstract destination with multiple criteria
    print("\n📋 Test Case 1: Abstract destination with multiple criteria")
    print("-" * 50)
    
    request = DestinationRequest(
        query="sunny beach destinations",
        origin_location="SFO",
        max_travel_time="5 hours",
        budget="$2000",
        interests=["beaches", "relaxation", "water activities"],
        travel_style="comfortable",
        traveler_type="family_with_kids",
        group_size=4,
        age_range="mixed_ages",
        mobility_requirements="any",
        seasonal_preferences="summer",
        travel_dates="June 2024"
    )
    
    print(f"Request: {request.query}")
    print(f"Origin: {request.origin_location}")
    print(f"Max travel time: {request.max_travel_time}")
    print(f"Budget: {request.budget}")
    print(f"Interests: {request.interests}")
    print(f"Traveler type: {request.traveler_type}")
    print(f"Seasonal: {request.seasonal_preferences}")
    
    try:
        # Test web search and ordering
        web_results = agent.search_and_order_destinations(request)
        
        print(f"\n🔍 Web Search Results:")
        print(f"   Found {len(web_results)} destinations")
        
        for i, result in enumerate(web_results[:5], 1):
            print(f"   {i}. {result['destination_name']} (Score: {result['score']:.2f})")
            print(f"      Criteria: {', '.join(result['criteria'])}")
            print(f"      Weight: {result['weight']}")
            print(f"      Score Breakdown: {result['score_breakdown']}")
            print()
        
        # Test full research
        print(f"\n🔍 Full Destination Research:")
        result = agent.research_abstract_destination(request)
        
        print(f"Request type: {result.request_type}")
        print(f"Primary destinations: {len(result.primary_destinations)}")
        print(f"Alternative destinations: {len(result.alternative_destinations)}")
        print(f"User choice required: {result.user_choice_required}")
        
        if result.primary_destinations:
            print(f"\nTop destinations found:")
            for i, dest in enumerate(result.primary_destinations, 1):
                print(f"   {i}. {dest.name}")
                print(f"      Country: {dest.country}")
                print(f"      Description: {dest.description[:100]}...")
                print()
        
        print("✅ SUCCESS: Web search and ordering functionality working!")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test case 2: Constrained destination search
    print("\n📋 Test Case 2: Constrained destination search")
    print("-" * 50)
    
    request2 = DestinationRequest(
        query="cultural destinations",
        origin_location="NYC",
        max_travel_time="3 hours",
        budget="$1500",
        interests=["museums", "history", "art"],
        travel_style="cultural",
        traveler_type="couple",
        group_size=2,
        age_range="middle_aged",
        mobility_requirements="any",
        seasonal_preferences="spring",
        travel_dates="April 2024"
    )
    
    print(f"Request: {request2.query}")
    print(f"Origin: {request2.origin_location}")
    print(f"Max travel time: {request2.max_travel_time}")
    print(f"Budget: {request2.budget}")
    print(f"Interests: {request2.interests}")
    print(f"Traveler type: {request2.traveler_type}")
    
    try:
        # Test constrained research
        result2 = agent.research_constrained_destination(request2)
        
        print(f"\n🔍 Constrained Destination Research:")
        print(f"Request type: {result2.request_type}")
        print(f"Primary destinations: {len(result2.primary_destinations)}")
        print(f"Alternative destinations: {len(result2.alternative_destinations)}")
        print(f"User choice required: {result2.user_choice_required}")
        
        if result2.primary_destinations:
            print(f"\nTop destinations found:")
            for i, dest in enumerate(result2.primary_destinations, 1):
                print(f"   {i}. {dest.name}")
                print(f"      Country: {dest.country}")
                print(f"      Description: {dest.description[:100]}...")
                print()
        
        print("✅ SUCCESS: Constrained destination research working!")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_search_query_generation():
    """Test the search query generation functionality"""
    print("\n🧪 Testing Search Query Generation")
    print("=" * 60)
    
    agent = DestinationResearchAgent()
    
    request = DestinationRequest(
        query="mountain destinations",
        origin_location="LAX",
        max_travel_time="4 hours",
        budget="$3000",
        interests=["hiking", "nature", "photography"],
        travel_style="adventure",
        traveler_type="solo",
        group_size=1,
        age_range="young_adults",
        mobility_requirements="active",
        seasonal_preferences="fall",
        travel_dates="October 2024"
    )
    
    try:
        queries = agent._generate_search_queries(request)
        
        print(f"Generated {len(queries)} search queries:")
        for i, query_info in enumerate(queries, 1):
            print(f"   {i}. Query: {query_info['query']}")
            print(f"      Criteria: {', '.join(query_info['criteria'])}")
            print(f"      Weight: {query_info['weight']}")
            print()
        
        print("✅ SUCCESS: Search query generation working!")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_result_scoring():
    """Test the result scoring functionality"""
    print("\n🧪 Testing Result Scoring")
    print("=" * 60)
    
    agent = DestinationResearchAgent()
    
    request = DestinationRequest(
        query="beach destinations",
        origin_location="MIA",
        max_travel_time="2 hours",
        budget="budget-friendly",
        interests=["beaches", "snorkeling"],
        travel_style="relaxing",
        traveler_type="family_with_kids",
        group_size=4,
        age_range="mixed_ages",
        mobility_requirements="any",
        seasonal_preferences="summer",
        travel_dates="July 2024"
    )
    
    # Mock web search result
    mock_result = """
    Title: Best Family Beach Destinations in the Caribbean
    Snippet: Discover the top family-friendly beach destinations in the Caribbean, perfect for kids and parents. These destinations offer safe beaches, family activities, and budget-friendly accommodations.
    Source: https://example.com/family-beach-destinations
    """
    
    try:
        scored_result = agent._score_result_by_criteria(mock_result, request, ["family", "beaches", "budget"], 1.2)
        
        if scored_result:
            print(f"Destination: {scored_result['destination_name']}")
            print(f"Score: {scored_result['score']:.2f}")
            print(f"Score Breakdown: {scored_result['score_breakdown']}")
            print(f"Criteria: {', '.join(scored_result['criteria'])}")
            print(f"Weight: {scored_result['weight']}")
            print("✅ SUCCESS: Result scoring working!")
        else:
            print("❌ FAILURE: No scored result returned")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Web Search and Ordering Tests")
    print("=" * 60)
    
    # Test search query generation
    test_search_query_generation()
    
    # Test result scoring
    test_result_scoring()
    
    # Test full web search and ordering
    test_web_search_ordering()
    
    print("\n🎉 Enhanced web search and ordering tests completed!")
