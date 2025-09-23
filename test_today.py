"""
Test script for travel APIs using today's date
"""

import os
from datetime import datetime, timedelta
from real_travel_apis import RealTravelAPIs, FlightSearch, HotelSearch, CarRentalSearch
from travel_agent import TravelAgent

def get_today_and_future_dates():
    """Get today's date and future dates for testing"""
    today = datetime.now()
    
    # For flights - use dates 30 days from now (realistic booking window)
    departure_date = (today + timedelta(days=30)).strftime('%Y-%m-%d')
    return_date = (today + timedelta(days=37)).strftime('%Y-%m-%d')  # 7-day trip
    
    # For hotels - use same dates as flights
    check_in = departure_date
    check_out = return_date
    
    return {
        'departure_date': departure_date,
        'return_date': return_date,
        'check_in': check_in,
        'check_out': check_out,
        'today': today.strftime('%Y-%m-%d')
    }

def test_travel_apis_today():
    """Test the travel APIs with today's date"""
    print("="*60)
    print("TESTING TRAVEL APIs WITH TODAY'S DATE")
    print("="*60)
    
    dates = get_today_and_future_dates()
    print(f"Today: {dates['today']}")
    print(f"Testing with departure: {dates['departure_date']}")
    print(f"Testing with return: {dates['return_date']}")
    print()
    
    # Check if API keys are configured
    amadeus_key = os.getenv("AMADEUS_API_KEY")
    amadeus_secret = os.getenv("AMADEUS_API_SECRET")
    serpapi_key = os.getenv("SERPAPI_KEY")
    flightsapi_key = os.getenv("FLIGHTSAPI_KEY")
    
    print(f"Amadeus API Key: {'✓ Configured' if amadeus_key else '✗ Not configured'}")
    print(f"Amadeus API Secret: {'✓ Configured' if amadeus_secret else '✗ Not configured'}")
    print(f"SerpAPI Key: {'✓ Configured' if serpapi_key else '✗ Not configured'}")
    print(f"FlightsAPI Key: {'✓ Configured' if flightsapi_key else '✗ Not configured'}")
    print()
    
    if not any([amadeus_key, serpapi_key, flightsapi_key]):
        print("⚠️  No API keys configured. Please set up at least one API key to test real data.")
        print("   Copy env_example.txt to .env and add your API keys.")
        return
    
    apis = RealTravelAPIs()
    
    # Test flight search with realistic dates
    print("\n1. Testing Real Flight Search (30 days from today):")
    print("-" * 50)
    flight_search = FlightSearch(
        origin="New York",
        destination="Paris",
        departure_date=dates['departure_date'],
        return_date=dates['return_date'],
        passengers=1
    )
    
    flights = apis.search_all_flights(flight_search)
    if flights:
        print(f"✅ Found {len(flights)} real flights:")
        for i, flight in enumerate(flights[:3], 1):  # Show first 3
            print(f"{i}. {flight.airline} {flight.flight_number}")
            print(f"   {flight.departure_time} → {flight.arrival_time}")
            print(f"   Price: {flight.price} | Duration: {flight.duration}")
            print(f"   Stops: {flight.stops}")
            print()
    else:
        print("❌ No flights found or API not configured")
    
    # Test hotel search with realistic dates
    print("\n2. Testing Real Hotel Search (30 days from today):")
    print("-" * 50)
    hotel_search = HotelSearch(
        destination="Paris",
        check_in=dates['check_in'],
        check_out=dates['check_out'],
        guests=1,
        rooms=1
    )
    
    hotels = apis.search_all_hotels(hotel_search)
    if hotels:
        print(f"✅ Found {len(hotels)} real hotels:")
        for i, hotel in enumerate(hotels[:3], 1):  # Show first 3
            print(f"{i}. {hotel.name}")
            print(f"   Price: {hotel.price_per_night}/night (Total: {hotel.total_price})")
            print(f"   Rating: {hotel.rating} | Location: {hotel.location}")
            print(f"   Amenities: {', '.join(hotel.amenities[:3])}")
            print()
    else:
        print("❌ No hotels found or API not configured")
    
    # Test car rental search with realistic dates
    print("\n3. Testing Real Car Rental Search (30 days from today):")
    print("-" * 50)
    car_search = CarRentalSearch(
        pickup_location="Paris",
        pickup_date=dates['departure_date'],
        return_date=dates['return_date']
    )
    
    cars = apis.search_all_car_rentals(car_search)
    if cars:
        print(f"✅ Found {len(cars)} real car rentals:")
        for i, car in enumerate(cars[:3], 1):  # Show first 3
            print(f"{i}. {car.company} - {car.car_type}")
            print(f"   Price: {car.price_per_day}/day (Total: {car.total_price})")
            print(f"   Features: {', '.join(car.features[:3])}")
            print()
    else:
        print("❌ No car rentals found or API not configured")

def test_agent_with_today():
    """Test the travel agent with today's date"""
    print("\n" + "="*60)
    print("TESTING TRAVEL AGENT WITH TODAY'S DATE")
    print("="*60)
    
    dates = get_today_and_future_dates()
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY environment variable")
        return
    
    # Check if at least one travel API is configured
    amadeus_key = os.getenv("AMADEUS_API_KEY")
    serpapi_key = os.getenv("SERPAPI_KEY")
    flightsapi_key = os.getenv("FLIGHTSAPI_KEY")
    
    if not any([amadeus_key, serpapi_key, flightsapi_key]):
        print("⚠️  No travel API keys configured. The agent will work but won't find real travel data.")
        print("   Please configure at least one travel API key for real data.")
    
    # Initialize the agent
    agent = TravelAgent()
    
    # Test trip request with realistic dates
    trip_request = f"""
    I want to plan a 7-day trip to Tokyo, Japan.
    I want to depart on {dates['departure_date']} and return on {dates['return_date']}.
    My budget is around $3000.
    I'm interested in technology, food, and Japanese culture.
    I prefer comfortable travel and would like to stay in a nice hotel.
    I want to see the main attractions and experience local culture.
    """
    
    print(f"Creating itinerary for trip departing {dates['departure_date']}...")
    result = agent.create_itinerary(trip_request)
    
    print("\n" + "="*50)
    print("TRIP ITINERARY WITH REAL TRAVEL DATA")
    print("="*50)
    
    if result["itinerary"]:
        itinerary = result["itinerary"]
        print(f"Destination: {itinerary.destination}")
        print(f"Duration: {itinerary.duration}")
        print(f"Total Estimated Cost: {itinerary.total_estimated_cost}")
        
        # Display travel options
        if result["flight_options"]:
            print(f"\nReal Flight Options:")
            print(result["flight_options"][0].get("results", "No flights found"))
        
        if result["hotel_options"]:
            print(f"\nReal Hotel Options:")
            print(result["hotel_options"][0].get("results", "No hotels found"))
        
        if result["car_rental_options"]:
            print(f"\nReal Car Rental Options:")
            print(result["car_rental_options"][0].get("results", "No car rentals found"))
        
        print("\nDaily Itinerary:")
        for day in itinerary.days:
            print(f"\n{day.date}:")
            print(f"  Activities: {', '.join(day.activities)}")
            print(f"  Meals: {', '.join(day.meals)}")
            print(f"  Accommodation: {day.accommodation}")
            print(f"  Estimated Cost: {day.estimated_cost}")

def test_individual_functions_today():
    """Test individual API functions with today's date"""
    print("\n" + "="*60)
    print("TESTING INDIVIDUAL API FUNCTIONS WITH TODAY'S DATE")
    print("="*60)
    
    dates = get_today_and_future_dates()
    
    from real_travel_apis import search_flights_real_api, search_hotels_real_api, search_car_rentals_real_api
    
    # Test flight search function
    print("\n1. Flight Search Function:")
    print("-" * 30)
    flight_result = search_flights_real_api(
        origin="New York",
        destination="London",
        departure_date=dates['departure_date'],
        return_date=dates['return_date'],
        passengers=1
    )
    print(flight_result)
    
    # Test hotel search function
    print("\n2. Hotel Search Function:")
    print("-" * 30)
    hotel_result = search_hotels_real_api(
        destination="London",
        check_in=dates['check_in'],
        check_out=dates['check_out'],
        guests=1,
        rooms=1
    )
    print(hotel_result)
    
    # Test car rental search function
    print("\n3. Car Rental Search Function:")
    print("-" * 30)
    car_result = search_car_rentals_real_api(
        pickup_location="London",
        pickup_date=dates['departure_date'],
        return_date=dates['return_date']
    )
    print(car_result)

def show_date_info():
    """Show information about the dates being used"""
    dates = get_today_and_future_dates()
    
    print("="*60)
    print("DATE INFORMATION FOR TESTING")
    print("="*60)
    print(f"Today: {dates['today']}")
    print(f"Departure Date (30 days from today): {dates['departure_date']}")
    print(f"Return Date (37 days from today): {dates['return_date']}")
    print(f"Check-in Date: {dates['check_in']}")
    print(f"Check-out Date: {dates['check_out']}")
    print()
    print("Note: Using dates 30+ days in the future for realistic booking scenarios.")
    print("Most travel APIs require advance booking for accurate pricing.")

def main():
    """Run all tests with today's date"""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "apis":
            test_travel_apis_today()
        elif sys.argv[1] == "agent":
            test_agent_with_today()
        elif sys.argv[1] == "functions":
            test_individual_functions_today()
        elif sys.argv[1] == "dates":
            show_date_info()
        else:
            print("Usage: python test_today.py [apis|agent|functions|dates]")
    else:
        # Run all tests
        show_date_info()
        test_travel_apis_today()
        test_individual_functions_today()
        test_agent_with_today()

if __name__ == "__main__":
    main()
