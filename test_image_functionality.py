#!/usr/bin/env python3
"""
Test script to verify image functionality in destination research
"""

import sys
import os
sys.path.append('.')

from destination_agent import DestinationResearchAgent, DestinationRequest

def test_image_search():
    """Test the image search functionality"""
    print("🧪 Testing Image Search Functionality")
    print("=" * 50)
    
    agent = DestinationResearchAgent()
    
    # Test image search for a popular destination
    print("\n📸 Testing image search for Paris, France...")
    image_data = agent._search_destination_images("Paris", "France")
    print(f"   Image data: {image_data}")
    
    if image_data.get('primary'):
        print(f"   ✅ Found primary image: {image_data['primary']}")
    else:
        print(f"   ⚠️  No primary image found")
        if image_data.get('search_terms'):
            print(f"   🔍 LLM suggested search terms: {image_data['search_terms']}")
    
    # Test with a smaller destination
    print("\n📸 Testing image search for Santorini, Greece...")
    image_data2 = agent._search_destination_images("Santorini", "Greece")
    print(f"   Image data: {image_data2}")
    
    if image_data2.get('primary'):
        print(f"   ✅ Found primary image: {image_data2['primary']}")
    else:
        print(f"   ⚠️  No primary image found")
        if image_data2.get('search_terms'):
            print(f"   🔍 LLM suggested search terms: {image_data2['search_terms']}")

def test_destination_with_images():
    """Test destination research with image integration"""
    print("\n\n🧪 Testing Destination Research with Images")
    print("=" * 50)
    
    agent = DestinationResearchAgent()
    
    # Create a test request
    request = DestinationRequest(
        query="beach destinations in Europe",
        travel_dates="summer",
        budget="moderate",
        origin_location="LHR"
    )
    
    print(f"\n🔍 Researching destinations for: {request.query}")
    print(f"   Travel dates: {request.travel_dates}")
    print(f"   Budget: {request.budget}")
    print(f"   Origin: {request.origin_location}")
    
    try:
        # This will test the full research flow including image search
        result = agent.research_abstract_destination(request)
        
        print(f"\n✅ Research completed!")
        all_destinations = result.primary_destinations + result.alternative_destinations
        print(f"   Found {len(all_destinations)} destinations")
        
        for i, dest in enumerate(all_destinations[:3]):  # Show first 3
            print(f"\n   Destination {i+1}: {dest.name}, {dest.country}")
            print(f"      Description: {dest.description[:100]}...")
            if dest.image_url:
                print(f"      🖼️  Image: {dest.image_url}")
            else:
                print(f"      ⚠️  No image available")
            if dest.image_urls:
                print(f"      🖼️  Additional images: {len(dest.image_urls)}")
                
    except Exception as e:
        print(f"   ❌ Error during research: {e}")

if __name__ == "__main__":
    test_image_search()
    test_destination_with_images()
    print("\n🎉 Image functionality test completed!")
