"""
Test script for the real travel APIs
"""

import os
from real_travel_apis import RealTravelAPIs, FlightSearch, HotelSearch, CarRentalSearch
from travel_agent import TravelAgent

def test_real_apis():
    """Test the real travel APIs"""
    print("="*60)
    print("TESTING REAL TRAVEL APIs")
    print("="*60)
    
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
    
    # Test flight search
    print("\n1. Testing Real Flight Search:")
    print("-" * 40)
    flight_search = FlightSearch(
        origin="NYC",
        destination="LAX",
        departure_date="2024-07-15",
        return_date="2024-07-22",
        passengers=1
    )
    
    flights = apis.search_all_flights(flight_search)
    if flights:
        print(f"Found {len(flights)} real flights:")
        for i, flight in enumerate(flights[:3], 1):  # Show first 3
            print(f"{i}. {flight.airline} {flight.flight_number}")
            print(f"   {flight.departure_time} → {flight.arrival_time}")
            print(f"   Price: {flight.price} | Duration: {flight.duration}")
            print(f"   Stops: {flight.stops}")
            print()
    else:
        print("No flights found or API not configured")
    
    # Test hotel search
    print("\n2. Testing Real Hotel Search:")
    print("-" * 40)
    hotel_search = HotelSearch(
        destination="New York",
        check_in="2024-07-15",
        check_out="2024-07-22",
        guests=1,
        rooms=1
    )
    
    hotels = apis.search_all_hotels(hotel_search)
    if hotels:
        print(f"Found {len(hotels)} real hotels:")
        for i, hotel in enumerate(hotels[:3], 1):  # Show first 3
            print(f"{i}. {hotel.name}")
            print(f"   Price: {hotel.price_per_night}/night (Total: {hotel.total_price})")
            print(f"   Rating: {hotel.rating} | Location: {hotel.location}")
            print(f"   Amenities: {', '.join(hotel.amenities[:3])}")
            print()
    else:
        print("No hotels found or API not configured")
    
    # Test car rental search
    print("\n3. Testing Real Car Rental Search:")
    print("-" * 40)
    car_search = CarRentalSearch(
        pickup_location="LAX",
        pickup_date="2024-07-15",
        return_date="2024-07-22"
    )
    
    cars = apis.search_all_car_rentals(car_search)
    if cars:
        print(f"Found {len(cars)} real car rentals:")
        for i, car in enumerate(cars[:3], 1):  # Show first 3
            print(f"{i}. {car.company} - {car.car_type}")
            print(f"   Price: {car.price_per_day}/day (Total: {car.total_price})")
            print(f"   Features: {', '.join(car.features[:3])}")
            print()
    else:
        print("No car rentals found or API not configured")

def test_agent_with_real_apis():
    """Test the travel agent with real APIs"""
    print("\n" + "="*60)
    print("TESTING TRAVEL AGENT WITH REAL APIs")
    print("="*60)
    
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
    
    # Test trip request
    trip_request = """
    I want to plan a 5-day trip to San Francisco, California.
    My budget is around $2500.
    I'm interested in technology, food, and sightseeing.
    I prefer comfortable travel and would like to stay in a nice hotel.
    I want to see the main attractions and experience the local culture.
    """
    
    print("Creating itinerary with real travel data...")
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

def test_individual_api_functions():
    """Test individual API functions"""
    print("\n" + "="*60)
    print("TESTING INDIVIDUAL API FUNCTIONS")
    print("="*60)
    
    from real_travel_apis import search_flights_real_api, search_hotels_real_api, search_car_rentals_real_api
    
    # Test flight search function
    print("\n1. Flight Search Function:")
    print("-" * 30)
    flight_result = search_flights_real_api(
        origin="JFK",
        destination="SFO",
        departure_date="2024-08-01",
        return_date="2024-08-08",
        passengers=1
    )
    print(flight_result)
    
    # Test hotel search function
    print("\n2. Hotel Search Function:")
    print("-" * 30)
    hotel_result = search_hotels_real_api(
        destination="San Francisco",
        check_in="2024-08-01",
        check_out="2024-08-08",
        guests=1,
        rooms=1
    )
    print(hotel_result)
    
    # Test car rental search function
    print("\n3. Car Rental Search Function:")
    print("-" * 30)
    car_result = search_car_rentals_real_api(
        pickup_location="SFO",
        pickup_date="2024-08-01",
        return_date="2024-08-08"
    )
    print(car_result)

def show_api_setup_instructions():
    """Show instructions for setting up API keys"""
    print("\n" + "="*60)
    print("API SETUP INSTRUCTIONS")
    print("="*60)
    
    print("\n1. Amadeus API (Recommended - Free tier available):")
    print("   - Go to: https://developers.amadeus.com/")
    print("   - Sign up for a free account")
    print("   - Create a new app to get API key and secret")
    print("   - Add to .env: AMADEUS_API_KEY=your_key")
    print("   - Add to .env: AMADEUS_API_SECRET=your_secret")
    
    print("\n2. SerpAPI (Google Flights):")
    print("   - Go to: https://serpapi.com/")
    print("   - Sign up for a free account (100 searches/month)")
    print("   - Get your API key from dashboard")
    print("   - Add to .env: SERPAPI_KEY=your_key")
    
    print("\n3. FlightsAPI.io:")
    print("   - Go to: https://flightsapi.io/")
    print("   - Sign up for an account")
    print("   - Get your API key")
    print("   - Add to .env: FLIGHTSAPI_KEY=your_key")
    
    print("\n4. OpenAI API (Required for the agent):")
    print("   - Go to: https://platform.openai.com/")
    print("   - Create an account and get API key")
    print("   - Add to .env: OPENAI_API_KEY=your_key")
    
    print("\nNote: You need at least one travel API key for real data.")
    print("Amadeus is recommended as it provides flights, hotels, and car rentals.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "apis":
            test_real_apis()
        elif sys.argv[1] == "agent":
            test_agent_with_real_apis()
        elif sys.argv[1] == "functions":
            test_individual_api_functions()
        elif sys.argv[1] == "setup":
            show_api_setup_instructions()
        else:
            print("Usage: python test_real_apis.py [apis|agent|functions|setup]")
    else:
        # Run all tests
        show_api_setup_instructions()
        test_real_apis()
        test_individual_api_functions()
        test_agent_with_real_apis()
