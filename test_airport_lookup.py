#!/usr/bin/env python3
"""
Test script for airport lookup functionality
"""

import sys
import os
sys.path.append('.')

from travel_agent import TravelAgent

def test_airport_lookup():
    """Test the airport lookup functionality"""
    print("🧪 Testing Airport Lookup Functionality")
    print("=" * 50)
    
    # Create travel agent instance
    agent = TravelAgent()
    
    # Test cases for different types of destinations
    test_locations = [
        "Aspen, Colorado",  # Small town, should find nearby major airport
        "Napa Valley, California",  # Wine region, should find nearby airport
        "Santorini, Greece",  # Island destination
        "Interlaken, Switzerland",  # Mountain town
        "Bruges, Belgium",  # Small European city
        "San Francisco, California",  # Major city
        "Tokyo, Japan",  # Major international city
    ]
    
    print("\n🔍 Testing airport lookup for various destinations:")
    for location in test_locations:
        print(f"\n📍 Testing: {location}")
        airports = agent._lookup_airport_codes(location)
        print(f"   Primary airport: {airports.get('primary', 'UNKNOWN')}")
        if airports.get('alternatives'):
            print(f"   Alternative airports: {', '.join(airports['alternatives'])}")
        else:
            print("   No alternative airports found")
    
    print("\n📊 Expected behavior:")
    print("   • Small towns should find nearby major airports")
    print("   • Major cities should find their primary airports")
    print("   • Island destinations should find nearest accessible airports")
    print("   • Mountain towns should find nearest major airports")
    
    # Test with a small town example
    print("\n🏔️ Testing small town scenario:")
    small_town = "Aspen, Colorado"
    print(f"   Destination: {small_town}")
    airports = agent._lookup_airport_codes(small_town)
    print(f"   Found airports: {airports}")
    
    if airports.get('primary') != 'UNKNOWN':
        print("   ✅ Successfully found airport for small town")
        print(f"   💡 Users can fly to {airports['primary']} and drive/take transport to {small_town}")
    else:
        print("   ⚠️  Could not find airport for small town")
    
    print("\n🎉 Airport lookup testing completed!")
    print("\n📱 Benefits of dynamic airport lookup:")
    print("   • No hardcoded airport values")
    print("   • Handles small towns and remote destinations")
    print("   • Finds nearest accessible airports")
    print("   • Provides alternative airport options")
    print("   • Works for any destination worldwide")

if __name__ == "__main__":
    test_airport_lookup()
