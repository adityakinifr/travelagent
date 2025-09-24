"""
Test script for the Destination Research Agent
"""

import os
from dotenv import load_dotenv
from destination_agent import DestinationResearchAgent

# Load environment variables
load_dotenv()

def test_destination_agent():
    """Test the destination research agent with various request types"""
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY environment variable")
        return
    
    # Check SerpAPI key status
    serpapi_key = os.getenv("SERPAPI_KEY")
    print(f"SerpAPI Key: {'✓ Configured' if serpapi_key else '✗ Not configured (will use LLM knowledge only)'}")
    print()
    
    # Initialize the destination agent
    agent = DestinationResearchAgent()
    
    # Test cases for different types of requests
    test_cases = [
        {
            "name": "Specific Destination",
            "request": "I want to visit Paris, France for 5 days. I'm interested in art, history, and French cuisine. My budget is around $2000."
        },
        {
            "name": "Abstract Destination",
            "request": "I'm looking for a sunny beach destination that's within 3 hours flight from SFO. I want to relax and enjoy water activities. Budget is around $1500."
        },
        {
            "name": "Multi-Location Comparison",
            "request": "I can't decide between Tokyo, Seoul, or Bangkok for a 7-day cultural trip. I'm interested in food, temples, and local experiences. Budget is $2500."
        },
        {
            "name": "Constrained Destination",
            "request": "I need a mountain destination within 2 hours drive from Denver. I want hiking and outdoor activities. Budget is flexible but prefer mid-range options."
        }
    ]
    
    print("🧭 Testing Destination Research Agent")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print("-" * 40)
        print(f"Request: {test_case['request']}")
        print("\n🔍 Researching...")
        
        try:
            # Research the destination
            result = agent.research_destination(test_case['request'])
            
            print(f"\n✅ Request Type: {result.request_type}")
            print(f"📊 Found {len(result.primary_destinations)} primary destinations")
            
            if result.primary_destinations:
                print("\n🏆 Primary Recommendations:")
                for j, dest in enumerate(result.primary_destinations[:3], 1):
                    print(f"{j}. {dest.name} - {dest.description[:100]}...")
            
            if result.alternative_destinations:
                print(f"\n🔄 {len(result.alternative_destinations)} alternative options available")
            
            if result.comparison_summary:
                print(f"\n📈 Comparison: {result.comparison_summary}")
            
            print(f"\n📝 Travel Recommendations:")
            print(result.travel_recommendations[:200] + "..." if len(result.travel_recommendations) > 200 else result.travel_recommendations)
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "="*60)

def test_request_analysis():
    """Test the request type analysis functionality"""
    agent = DestinationResearchAgent()
    
    test_requests = [
        "I want to go to Paris",
        "Looking for a beach destination near California",
        "Should I visit Tokyo or Seoul?",
        "Need a mountain getaway within 2 hours of Denver"
    ]
    
    print("\n🔍 Testing Request Type Analysis")
    print("=" * 40)
    
    for request in test_requests:
        request_type = agent.analyze_request_type(request)
        print(f"Request: {request}")
        print(f"Type: {request_type}")
        print("-" * 40)

def test_web_search():
    """Test web search functionality"""
    agent = DestinationResearchAgent()
    
    print("\n🌐 Testing Web Search Functionality")
    print("=" * 40)
    
    test_queries = [
        "Paris travel guide 2024",
        "best beach destinations near California",
        "Tokyo vs Seoul travel comparison"
    ]
    
    for query in test_queries:
        print(f"\nSearching: {query}")
        results = agent.search_web(query, num_results=2)
        
        if results:
            print(f"✅ Found {len(results)} results")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result[:100]}...")
        else:
            print("❌ No results found (SerpAPI may not be configured)")

if __name__ == "__main__":
    test_destination_agent()
    test_request_analysis()
    test_web_search()
