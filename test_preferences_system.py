"""
Test script to demonstrate the comprehensive preferences system
"""

import os
from dotenv import load_dotenv
from destination_agent import DestinationResearchAgent
from preferences_manager import PreferencesManager

# Load environment variables
load_dotenv()

def test_preferences_system():
    """Test the comprehensive preferences system"""
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY environment variable")
        return
    
    print("🎯 Testing Comprehensive Preferences System")
    print("=" * 60)
    
    # Initialize the preferences manager
    prefs_manager = PreferencesManager()
    
    # Show current preferences summary
    print("\n📋 Current Preferences Summary:")
    print(prefs_manager.get_preferences_summary())
    
    # Test different preference categories
    print("\n🏨 Hotel Preferences:")
    hotel_recs = prefs_manager.get_hotel_recommendations("Monterey", "leisure")
    print(f"   Preferred chains: {', '.join(hotel_recs['preferred_chains'][:3])}")
    print(f"   Loyalty programs: {', '.join(hotel_recs['loyalty_programs'][:2])}")
    print(f"   Required amenities: {', '.join(hotel_recs['amenities_required'])}")
    
    print("\n✈️ Flight Preferences:")
    flight_recs = prefs_manager.get_flight_recommendations("SFO", "LAX", "domestic_short")
    print(f"   Preferred airlines: {', '.join(flight_recs['preferred_airlines'][:3])}")
    print(f"   Flight class: {flight_recs['flight_class']}")
    print(f"   Red-eye preference: {flight_recs['red_eye_preference']}")
    
    print("\n💳 Loyalty Benefits:")
    united_benefits = prefs_manager.get_loyalty_benefits("united", "airline")
    print(f"   United status: {united_benefits['status']}")
    print(f"   Benefits: {', '.join(united_benefits['benefits'])}")
    
    marriott_benefits = prefs_manager.get_loyalty_benefits("marriott", "hotel")
    print(f"   Marriott status: {marriott_benefits['status']}")
    print(f"   Benefits: {', '.join(marriott_benefits['benefits'])}")
    
    print("\n📱 Technology Recommendations:")
    tech_recs = prefs_manager.get_technology_recommendations()
    print(f"   Recommended apps: {', '.join(tech_recs['recommended_apps'][:3])}")
    print(f"   Digital wallet: {tech_recs['digital_wallet']}")
    print(f"   Digital boarding: {tech_recs['digital_preferences']['boarding_pass']}")
    
    print("\n🏥 Health & Wellness:")
    health_recs = prefs_manager.get_health_wellness_recommendations()
    print(f"   Fitness level: {health_recs['fitness_level']}")
    print(f"   Wellness activities: {', '.join(health_recs['wellness_activities'])}")
    print(f"   Hotel gym required: {health_recs['hotel_gym_required']}")
    
    print("\n🛡️ Safety & Security:")
    safety_recs = prefs_manager.get_safety_recommendations()
    print(f"   Safety level: {safety_recs['safety_level']}")
    print(f"   Safe neighborhoods: {safety_recs['safe_neighborhoods']}")
    print(f"   Travel alerts: {safety_recs['travel_alerts']}")
    
    print("\n🌍 Cultural Preferences:")
    cultural_recs = prefs_manager.get_cultural_recommendations()
    print(f"   Cultural sensitivity: {cultural_recs['cultural_sensitivity']}")
    print(f"   Authentic experiences: {cultural_recs['authentic_experiences']}")
    print(f"   Cultural activities: {', '.join(cultural_recs['cultural_activities'][:3])}")
    
    print("\n🌱 Environmental Preferences:")
    env_recs = prefs_manager.get_environmental_recommendations()
    print(f"   Eco-conscious: {env_recs['eco_conscious']}")
    print(f"   Sustainable transport: {env_recs['sustainable_transport']}")
    print(f"   Carbon offset: {env_recs['carbon_offset']}")
    
    print("\n📸 Photography & Social:")
    photo_recs = prefs_manager.get_photography_recommendations()
    print(f"   Photography interest: {photo_recs['photography_interest']}")
    print(f"   Instagrammable spots: {photo_recs['instagrammable_spots']}")
    print(f"   Social sharing: {photo_recs['social_sharing']}")
    
    print("\n🎒 Packing Preferences:")
    packing_recs = prefs_manager.get_packing_recommendations()
    print(f"   Packing style: {packing_recs['packing_style']}")
    print(f"   Carry-on preference: {packing_recs['carry_on_preference']}")
    print(f"   Essential items: {', '.join(packing_recs['essential_items'][:3])}")
    
    print("\n💬 Communication Preferences:")
    comm_recs = prefs_manager.get_communication_recommendations()
    print(f"   Roaming preference: {comm_recs['roaming_preference']}")
    print(f"   WiFi calling: {comm_recs['wifi_calling']}")
    print(f"   Messaging apps: {', '.join(comm_recs['messaging_apps'])}")
    
    print("\n🏥 Travel Insurance:")
    insurance_recs = prefs_manager.get_travel_insurance_recommendations()
    print(f"   Prefer insurance: {insurance_recs['prefer_insurance']}")
    print(f"   Provider: {insurance_recs['provider']}")
    print(f"   Coverage level: {insurance_recs['coverage_level']}")

def test_destination_research_with_preferences():
    """Test destination research with preferences integration"""
    
    print("\n\n🔍 Testing Destination Research with Preferences")
    print("=" * 60)
    
    # Initialize the destination agent with preferences
    agent = DestinationResearchAgent()
    
    # Test cases that should leverage different preferences
    test_cases = [
        {
            "name": "Business Traveler with Loyalty Status",
            "request": "I need a business destination within 2 hours of NYC. I have United Gold status and Marriott Gold status. I prefer direct flights and business class for long flights."
        },
        {
            "name": "Eco-Conscious Family",
            "request": "We're an eco-conscious family with 2 kids looking for a sustainable beach destination within 3 hours of SFO. We prefer eco-hotels and sustainable transportation."
        },
        {
            "name": "Photography Enthusiast Solo Traveler",
            "request": "I'm a solo photographer looking for Instagram-worthy destinations within 4 hours of LAX. I want great photo opportunities and good WiFi for social media sharing."
        },
        {
            "name": "Health & Wellness Focused Couple",
            "request": "We're a couple interested in wellness and fitness looking for a destination within 3 hours of Miami. We need hotels with gyms and spa facilities."
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print("-" * 50)
        print(f"Request: {test_case['request']}")
        print("\n🔍 Researching with preferences...")
        
        try:
            # Research the destination
            result = agent.research_destination(test_case['request'])
            
            print(f"\n✅ Request Type: {result.request_type}")
            print(f"📊 Found {len(result.primary_destinations)} primary destinations")
            
            if result.primary_destinations:
                print("\n🏆 Top Destination Recommendations:")
                for j, dest in enumerate(result.primary_destinations[:2], 1):
                    print(f"\n{j}. {dest.name}")
                    print(f"   📍 {dest.country}, {dest.region}")
                    print(f"   📝 {dest.description}")
                    
                    # Show preference-relevant information
                    if dest.family_friendly_score:
                        print(f"   👨‍👩‍👧‍👦 Family-friendly: {dest.family_friendly_score}/10")
                    if dest.business_friendly:
                        print(f"   💼 Business-friendly: {dest.business_friendly}")
                    if dest.romantic_appeal:
                        print(f"   💕 Romantic appeal: {dest.romantic_appeal}")
                    if dest.nightlife_rating:
                        print(f"   🍸 Nightlife: {dest.nightlife_rating}")
                    if dest.crowd_levels:
                        print(f"   👥 Crowd levels: {dest.crowd_levels}")
                    
                    print(f"   🎯 Why recommended: {dest.why_recommended}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

def test_comprehensive_recommendations():
    """Test comprehensive recommendations combining all preferences"""
    
    print("\n\n🎯 Testing Comprehensive Recommendations")
    print("=" * 60)
    
    prefs_manager = PreferencesManager()
    
    # Get comprehensive recommendations for a destination
    destination = "Monterey, CA"
    trip_type = "leisure"
    
    print(f"\n📍 Getting comprehensive recommendations for {destination} ({trip_type})")
    
    comprehensive_recs = prefs_manager.get_comprehensive_recommendations(destination, trip_type)
    
    print(f"\n🏨 Hotel Recommendations:")
    print(f"   Preferred chains: {', '.join(comprehensive_recs['hotel']['preferred_chains'][:3])}")
    print(f"   Hotel types: {', '.join(comprehensive_recs['hotel']['hotel_types'])}")
    
    print(f"\n✈️ Flight Recommendations:")
    print(f"   Preferred airlines: {', '.join(comprehensive_recs['flight']['preferred_airlines'][:3])}")
    print(f"   Flight class: {comprehensive_recs['flight']['flight_class']}")
    
    print(f"\n💰 Budget Guidelines:")
    print(f"   Accommodation: {comprehensive_recs['budget']['accommodation']}")
    print(f"   Daily spending: {comprehensive_recs['budget']['daily_spending']}")
    
    print(f"\n🎯 Activity Recommendations:")
    print(f"   Outdoor activities: {', '.join(comprehensive_recs['activities']['outdoor_activities'][:3])}")
    print(f"   Adventure level: {comprehensive_recs['activities']['adventure_level']}")
    
    print(f"\n📱 Technology Recommendations:")
    print(f"   Recommended apps: {', '.join(comprehensive_recs['technology']['recommended_apps'][:3])}")
    print(f"   Digital wallet: {comprehensive_recs['technology']['digital_wallet']}")
    
    print(f"\n🛡️ Safety Recommendations:")
    print(f"   Safety level: {comprehensive_recs['safety']['safety_level']}")
    print(f"   Safe neighborhoods: {comprehensive_recs['safety']['safe_neighborhoods']}")
    
    print(f"\n🌍 Cultural Recommendations:")
    print(f"   Cultural sensitivity: {comprehensive_recs['cultural']['cultural_sensitivity']}")
    print(f"   Authentic experiences: {comprehensive_recs['cultural']['authentic_experiences']}")
    
    print(f"\n🌱 Environmental Recommendations:")
    print(f"   Eco-conscious: {comprehensive_recs['environmental']['eco_conscious']}")
    print(f"   Sustainable transport: {comprehensive_recs['environmental']['sustainable_transport']}")
    
    print(f"\n📸 Photography Recommendations:")
    print(f"   Photography interest: {comprehensive_recs['photography']['photography_interest']}")
    print(f"   Instagrammable spots: {comprehensive_recs['photography']['instagrammable_spots']}")
    
    print(f"\n🎒 Packing Recommendations:")
    print(f"   Packing style: {comprehensive_recs['packing']['packing_style']}")
    print(f"   Carry-on preference: {comprehensive_recs['packing']['carry_on_preference']}")
    
    print(f"\n💬 Communication Recommendations:")
    print(f"   Roaming preference: {comprehensive_recs['communication']['roaming_preference']}")
    print(f"   WiFi calling: {comprehensive_recs['communication']['wifi_calling']}")
    
    print(f"\n🏥 Insurance Recommendations:")
    print(f"   Prefer insurance: {comprehensive_recs['insurance']['prefer_insurance']}")
    print(f"   Provider: {comprehensive_recs['insurance']['provider']}")

if __name__ == "__main__":
    test_preferences_system()
    test_destination_research_with_preferences()
    test_comprehensive_recommendations()
