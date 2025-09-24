"""
Debug script for Amadeus API issues
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from amadeus import Client, ResponseError

# Load environment variables
load_dotenv()

def get_test_dates():
    """Get realistic test dates based on today"""
    today = datetime.now()
    
    # Use dates 30 days from now for realistic booking
    departure_date = (today + timedelta(days=30)).strftime('%Y-%m-%d')
    return_date = (today + timedelta(days=37)).strftime('%Y-%m-%d')  # 7-day trip
    check_in = departure_date
    check_out = return_date
    
    return {
        'departure_date': departure_date,
        'return_date': return_date,
        'check_in': check_in,
        'check_out': check_out,
        'today': today.strftime('%Y-%m-%d')
    }

def test_amadeus_connection():
    """Test basic Amadeus API connection"""
    amadeus_key = os.getenv("AMADEUS_API_KEY")
    amadeus_secret = os.getenv("AMADEUS_API_SECRET")
    
    if not amadeus_key or not amadeus_secret:
        print("❌ Amadeus API credentials not configured")
        print("Please set AMADEUS_API_KEY and AMADEUS_API_SECRET in your .env file")
        return False
    
    print(f"✅ API Key: {amadeus_key[:8]}...")
    print(f"✅ API Secret: {amadeus_secret[:8]}...")
    
    try:
        # Initialize client
        amadeus = Client(
            client_id=amadeus_key,
            client_secret=amadeus_secret,
            hostname='test'
        )
        print("✅ Amadeus client initialized successfully")
        
        # Test authentication
        print("\n🔍 Testing authentication...")
        response = amadeus.reference_data.locations.get(
            keyword='PAR',
            subType='CITY'
        )
        
        if response.data:
            print("✅ Authentication successful")
            print(f"✅ Found {len(response.data)} cities for 'PAR'")
            for city in response.data[:3]:
                print(f"   - {city.get('name', 'Unknown')} ({city.get('iataCode', 'N/A')})")
        else:
            print("❌ Authentication failed - no data returned")
            return False
            
    except ResponseError as error:
        print(f"❌ Amadeus API error: {error}")
        if hasattr(error, 'response') and error.response:
            print(f"❌ Error details: {error.response.body}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

def test_flight_search():
    """Test flight search with simple parameters"""
    amadeus_key = os.getenv("AMADEUS_API_KEY")
    amadeus_secret = os.getenv("AMADEUS_API_SECRET")
    
    if not amadeus_key or not amadeus_secret:
        print("❌ Amadeus API credentials not configured")
        return False
    
    try:
        amadeus = Client(
            client_id=amadeus_key,
            client_secret=amadeus_secret,
            hostname='test'
        )
        
        dates = get_test_dates()
        print("\n🔍 Testing flight search...")
        print(f"Searching: NYC → LAX on {dates['departure_date']}")
        
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode='NYC',
            destinationLocationCode='LAX',
            departureDate=dates['departure_date'],
            adults=1,
            max=3
        )
        
        if response.data:
            print(f"✅ Found {len(response.data)} flight offers")
            for i, offer in enumerate(response.data[:2], 1):
                price = offer.get('price', {}).get('total', 'N/A')
                currency = offer.get('price', {}).get('currency', 'USD')
                print(f"   {i}. Price: {currency} {price}")
        else:
            print("❌ No flight offers found")
            return False
            
    except ResponseError as error:
        print(f"❌ Flight search error: {error}")
        if hasattr(error, 'response') and error.response:
            print(f"❌ Error details: {error.response.body}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

def test_hotel_search():
    """Test hotel search"""
    amadeus_key = os.getenv("AMADEUS_API_KEY")
    amadeus_secret = os.getenv("AMADEUS_API_SECRET")
    
    if not amadeus_key or not amadeus_secret:
        print("❌ Amadeus API credentials not configured")
        return False
    
    try:
        amadeus = Client(
            client_id=amadeus_key,
            client_secret=amadeus_secret,
            hostname='test'
        )
        
        dates = get_test_dates()
        print("\n🔍 Testing hotel search...")
        print(f"Searching hotels in Paris for {dates['check_in']} to {dates['check_out']}")
        
        # First get city code
        city_response = amadeus.reference_data.locations.get(
            keyword='PAR',
            subType='CITY'
        )
        
        if not city_response.data:
            print("❌ Could not find Paris city code")
            return False
        
        city_code = city_response.data[0]['iataCode']
        print(f"✅ Found city code: {city_code}")
        
        # Get hotel list first to get hotel IDs
        hotel_list_response = amadeus.reference_data.locations.hotels.by_city.get(
            cityCode=city_code
        )
        
        if not hotel_list_response.data:
            print("❌ Could not find hotels for Paris")
            return False
        
        # Get hotel IDs (limit to 3 for testing)
        hotel_ids = [hotel['hotelId'] for hotel in hotel_list_response.data[:3]]
        print(f"✅ Found {len(hotel_ids)} hotels: {hotel_ids}")
        
        # Search hotels using hotel IDs
        response = amadeus.shopping.hotel_offers_search.get(
            hotelIds=','.join(hotel_ids),
            checkInDate=dates['check_in'],
            checkOutDate=dates['check_out'],
            adults=1,
            roomQuantity=1
        )
        
        if response.data:
            print(f"✅ Found {len(response.data)} hotel offers")
            for i, offer in enumerate(response.data[:2], 1):
                hotel_name = offer.get('hotel', {}).get('name', 'Unknown')
                price = offer.get('offers', [{}])[0].get('price', {}).get('total', 'N/A')
                currency = offer.get('offers', [{}])[0].get('price', {}).get('currency', 'USD')
                print(f"   {i}. {hotel_name} - {currency} {price}")
        else:
            print("❌ No hotel offers found")
            return False
            
    except ResponseError as error:
        print(f"❌ Hotel search error: {error}")
        if hasattr(error, 'response') and error.response:
            print(f"❌ Error details: {error.response.body}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True


def main():
    """Run all tests"""
    print("🚀 Amadeus API Debug Tool")
    print("=" * 50)
    
    # Show date information
    dates = get_test_dates()
    print(f"Today: {dates['today']}")
    print(f"Testing with departure: {dates['departure_date']} (30 days from today)")
    print(f"Testing with return: {dates['return_date']} (37 days from today)")
    print(f"Hotel check-in: {dates['check_in']}")
    print(f"Hotel check-out: {dates['check_out']}")
    print()
    
    # Check API key status
    amadeus_key = os.getenv("AMADEUS_API_KEY")
    amadeus_secret = os.getenv("AMADEUS_API_SECRET")
    serpapi_key = os.getenv("SERPAPI_KEY")
    flightsapi_key = os.getenv("FLIGHTSAPI_KEY")
    booking_api_key = os.getenv("BOOKING_API_KEY")
    booking_affiliate_id = os.getenv("BOOKING_AFFILIATE_ID")
    cartrawler_key = os.getenv("CARTRAWLER_API_KEY")
    rentalcars_key = os.getenv("RENTALCARS_API_KEY")
    
    print("API Key Status:")
    print(f"  Amadeus API Key: {'✓ Configured' if amadeus_key else '✗ Not configured'}")
    print(f"  Amadeus API Secret: {'✓ Configured' if amadeus_secret else '✗ Not configured'}")
    print(f"  SerpAPI Key: {'✓ Configured' if serpapi_key else '✗ Not configured'}")
    print(f"  FlightsAPI Key: {'✓ Configured' if flightsapi_key else '✗ Not configured'}")
    print(f"  Booking.com API Key: {'✓ Configured' if booking_api_key else '✗ Not configured'}")
    print(f"  Booking.com Affiliate ID: {'✓ Configured' if booking_affiliate_id else '✗ Not configured'}")
    print(f"  CarTrawler API Key: {'✓ Configured' if cartrawler_key else '✗ Not configured'}")
    print(f"  Rentalcars.com API Key: {'✓ Configured' if rentalcars_key else '✗ Not configured'}")
    print()
    
    # Test connection
    if not test_amadeus_connection():
        print("\n❌ Connection test failed. Please check your API credentials.")
        return
    
    # Test flight search
    if not test_flight_search():
        print("\n❌ Flight search test failed.")
    
    # Test hotel search
    if not test_hotel_search():
        print("\n❌ Hotel search test failed.")
    
    # Test car rental search
    if not test_car_rental_search():
        print("\n❌ Car rental search test failed.")
    
    print("\n✅ Debug tests completed!")

if __name__ == "__main__":
    main()
