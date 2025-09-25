#!/usr/bin/env python3
"""
Test script for smart date parsing functionality
"""

import sys
import os
sys.path.append('.')

from destination_agent import DestinationResearchAgent
from datetime import datetime

def test_smart_date_parsing():
    """Test the smart date parsing functionality"""
    print("🧪 Testing Smart Date Parsing")
    print("=" * 50)
    
    # Create destination agent instance
    agent = DestinationResearchAgent()
    
    # Get current date info
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    
    print(f"📅 Current date: {current_date.strftime('%B %d, %Y')}")
    print(f"📅 Current month: {current_month}")
    print(f"📅 Current year: {current_year}")
    print()
    
    # Test cases
    test_cases = [
        "summer",
        "winter", 
        "spring",
        "fall",
        "june",
        "december",
        "march",
        "next month",
        "next year",
        "this year",
        "summer 2024",  # Already has year
        "june 2025",    # Already has year
    ]
    
    print("🔍 Testing date parsing:")
    for test_input in test_cases:
        parsed = agent._parse_smart_dates(test_input)
        print(f"   '{test_input}' → '{parsed}'")
    
    print("\n📊 Expected behavior:")
    print("   • If current month is in a season, that season should use next year")
    print("   • If current month is not in a season, that season should use current year if upcoming, next year if passed")
    print("   • Months should use current year if upcoming, next year if passed")
    print("   • 'next month' should calculate the actual next month")
    print("   • Dates with years should remain unchanged")
    
    # Test with actual trip planning
    print("\n🚀 Testing with actual trip planning...")
    try:
        from destination_agent import DestinationRequest
        
        # Test summer request
        request = DestinationRequest(
            query="beach destinations",
            travel_dates="summer",
            budget="$2000",
            origin_location="SFO"
        )
        
        # This should parse the dates
        error = agent._validate_travel_dates(request)
        if error:
            print(f"   ❌ Date validation failed: {error}")
        else:
            print(f"   ✅ Summer dates parsed as: '{request.travel_dates}'")
        
        # Test June request
        request2 = DestinationRequest(
            query="city break",
            travel_dates="june",
            budget="$1500",
            origin_location="LAX"
        )
        
        error2 = agent._validate_travel_dates(request2)
        if error2:
            print(f"   ❌ Date validation failed: {error2}")
        else:
            print(f"   ✅ June dates parsed as: '{request2.travel_dates}'")
            
    except Exception as e:
        print(f"   ❌ Error testing with trip planning: {e}")
    
    print("\n🎉 Smart date parsing test completed!")

if __name__ == "__main__":
    test_smart_date_parsing()
