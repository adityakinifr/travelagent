"""
Test script to demonstrate demographic and seasonal considerations in destination research
"""

import os
from dotenv import load_dotenv
from destination_agent import DestinationResearchAgent

# Load environment variables
load_dotenv()

def test_demographic_features():
    """Test destination research with different traveler demographics and seasonal preferences"""
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY environment variable")
        return
    
    # Initialize the destination agent
    agent = DestinationResearchAgent()
    
    print("👥 Testing Demographic and Seasonal Features")
    print("=" * 60)
    
    # Test cases with different traveler types and seasonal preferences
    test_cases = [
        {
            "name": "Family with Kids - Summer Beach Trip",
            "request": "We're a family with 2 young kids looking for a beach destination within 3 hours of SFO for our summer vacation. We want kid-friendly activities and safe beaches."
        },
        {
            "name": "Couple - Romantic Winter Getaway",
            "request": "My partner and I want a romantic winter destination within 4 hours of NYC. We're looking for cozy accommodations and intimate dining experiences."
        },
        {
            "name": "Solo Traveler - Spring Adventure",
            "request": "I'm a solo traveler in my 30s looking for an adventure destination within 5 hours of LAX for spring break. I want to meet other travelers and try new activities."
        },
        {
            "name": "Older Adults - Fall Cultural Trip",
            "request": "We're a retired couple in our 60s looking for a cultural destination within 2 hours of Chicago for fall. We prefer comfortable accommodations and easy walking."
        },
        {
            "name": "Group of Friends - Summer Party Destination",
            "request": "We're a group of 6 friends in our 20s looking for a fun summer destination within 3 hours of Miami. We want good nightlife and group activities."
        },
        {
            "name": "Business Traveler - Year-round Convenience",
            "request": "I need a business-friendly destination within 2 hours of Boston for work trips. I need good hotels, restaurants, and easy transportation."
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
            print(f"🎯 User Choice Required: {result.user_choice_required}")
            
            if result.primary_destinations:
                print("\n🏆 Destination Options:")
                for j, dest in enumerate(result.primary_destinations, 1):
                    print(f"\n{j}. {dest.name}")
                    print(f"   📍 {dest.country}, {dest.region}")
                    print(f"   📝 {dest.description}")
                    
                    # Show demographic-specific information
                    if dest.family_friendly_score:
                        print(f"   👨‍👩‍👧‍👦 Family-friendly score: {dest.family_friendly_score}/10")
                    
                    if dest.kid_friendly_activities:
                        print(f"   🧒 Kid-friendly activities: {', '.join(dest.kid_friendly_activities[:3])}")
                    
                    if dest.senior_friendly_features:
                        print(f"   👴 Senior-friendly features: {', '.join(dest.senior_friendly_features[:3])}")
                    
                    if dest.accessibility_features:
                        print(f"   ♿ Accessibility features: {', '.join(dest.accessibility_features[:3])}")
                    
                    if dest.romantic_appeal:
                        print(f"   💕 Romantic appeal: {dest.romantic_appeal}")
                    
                    if dest.nightlife_rating:
                        print(f"   🍸 Nightlife rating: {dest.nightlife_rating}")
                    
                    if dest.business_friendly:
                        print(f"   💼 Business-friendly: {dest.business_friendly}")
                    
                    if dest.crowd_levels:
                        print(f"   👥 Crowd levels: {dest.crowd_levels}")
                    
                    if dest.seasonal_highlights:
                        print(f"   🌟 Seasonal highlights: {dest.seasonal_highlights}")
                    
                    print(f"   🎯 Why recommended: {dest.why_recommended}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "="*60)

def test_seasonal_ranking():
    """Test how seasonal preferences affect destination ranking"""
    
    agent = DestinationResearchAgent()
    
    print("\n🌍 Testing Seasonal Ranking")
    print("=" * 50)
    
    # Same destination request but with different seasonal preferences
    base_request = "I want a beach destination within 3 hours of SFO"
    
    seasonal_tests = [
        ("Summer", f"{base_request} for summer vacation"),
        ("Winter", f"{base_request} for winter break"),
        ("Spring", f"{base_request} for spring break"),
        ("Fall", f"{base_request} for fall vacation")
    ]
    
    for season, request in seasonal_tests:
        print(f"\n🌤️ {season} Request: {request}")
        print("-" * 40)
        
        try:
            result = agent.research_destination(request)
            
            if result.primary_destinations:
                print(f"Top 3 destinations for {season}:")
                for i, dest in enumerate(result.primary_destinations[:3], 1):
                    print(f"  {i}. {dest.name} - {dest.best_time_to_visit}")
                    
                    # Show seasonal highlights if available
                    if dest.seasonal_highlights and season.lower() in dest.seasonal_highlights:
                        print(f"     {season} highlights: {dest.seasonal_highlights[season.lower()]}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_demographic_features()
    test_seasonal_ranking()
