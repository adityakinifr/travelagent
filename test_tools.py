"""
Test script for the travel tools functionality
"""

import os
from travel_tools import TravelTools, FlightSearch, HotelSearch, CarRentalSearch
from travel_agent import TravelAgent

def test_travel_tools():
    """Test the individual travel tools"""
    print("="*60)
    print("TESTING TRAVEL TOOLS")
    print("="*60)
    
    tools = TravelTools()
    
    # Test flight search
    print("\n1. Testing Flight Search:")
    print("-" * 30)
    flight_search = FlightSearch(
        origin="New York",
        destination="Paris",
        departure_date="2024-06-15",
        return_date="2024-06-22",
        passengers=1
    )
    
    flights = tools.search_all_flights(flight_search)
    for i, flight in enumerate(flights, 1):
        print(f"{i}. {flight.airline} {flight.flight_number}")
        print(f"   {flight.departure_time} → {flight.arrival_time} | {flight.duration}")
        print(f"   Price: {flight.price} | Stops: {flight.stops}")
        print()
    
    # Test hotel search
    print("\n2. Testing Hotel Search:")
    print("-" * 30)
    hotel_search = HotelSearch(
        destination="Paris",
        check_in="2024-06-15",
        check_out="2024-06-22",
        guests=1,
        rooms=1
    )
    
    hotels = tools.search_all_hotels(hotel_search)
    for i, hotel in enumerate(hotels, 1):
        print(f"{i}. {hotel.name}")
        print(f"   Price: {hotel.price_per_night}/night (Total: {hotel.total_price})")
        print(f"   Rating: {hotel.rating} | Location: {hotel.location}")
        print(f"   Amenities: {', '.join(hotel.amenities)}")
        print()
    
    # Test car rental search
    print("\n3. Testing Car Rental Search:")
    print("-" * 30)
    car_search = CarRentalSearch(
        pickup_location="Paris",
        pickup_date="2024-06-15",
        return_date="2024-06-22"
    )
    
    cars = tools.search_all_car_rentals(car_search)
    for i, car in enumerate(cars, 1):
        print(f"{i}. {car.company} - {car.car_type}")
        print(f"   Price: {car.price_per_day}/day (Total: {car.total_price})")
        print(f"   Features: {', '.join(car.features)}")
        print()

def test_agent_with_tools():
    """Test the travel agent with integrated tools"""
    print("\n" + "="*60)
    print("TESTING TRAVEL AGENT WITH TOOLS")
    print("="*60)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY environment variable")
        print("You can copy env_example.txt to .env and add your key")
        return
    
    # Initialize the agent
    agent = TravelAgent()
    
    # Test trip request
    trip_request = """
    I want to plan a 5-day trip to Paris, France.
    My budget is around $2000.
    I'm interested in art, history, and French cuisine.
    I prefer comfortable travel and would like to stay in a nice hotel.
    I want to see the main attractions but also experience local culture.
    """
    
    print("Creating itinerary with travel options...")
    result = agent.create_itinerary(trip_request)
    
    print("\n" + "="*50)
    print("TRIP ITINERARY WITH TRAVEL OPTIONS")
    print("="*50)
    
    if result["itinerary"]:
        itinerary = result["itinerary"]
        print(f"Destination: {itinerary.destination}")
        print(f"Duration: {itinerary.duration}")
        print(f"Total Estimated Cost: {itinerary.total_estimated_cost}")
        
        # Display travel options
        if result["flight_options"]:
            print(f"\nFlight Options Found:")
            print(result["flight_options"][0].get("results", "No flights found"))
        
        if result["hotel_options"]:
            print(f"\nHotel Options Found:")
            print(result["hotel_options"][0].get("results", "No hotels found"))
        
        if result["car_rental_options"]:
            print(f"\nCar Rental Options Found:")
            print(result["car_rental_options"][0].get("results", "No car rentals found"))
        
        print("\nDaily Itinerary:")
        for day in itinerary.days:
            print(f"\n{day.date}:")
            print(f"  Activities: {', '.join(day.activities)}")
            print(f"  Meals: {', '.join(day.meals)}")
            print(f"  Accommodation: {day.accommodation}")
            print(f"  Estimated Cost: {day.estimated_cost}")

def test_individual_tool_functions():
    """Test the individual tool functions"""
    print("\n" + "="*60)
    print("TESTING INDIVIDUAL TOOL FUNCTIONS")
    print("="*60)
    
    from travel_tools import search_flights_tool, search_hotels_tool, search_car_rentals_tool
    
    # Test flight search tool
    print("\n1. Flight Search Tool:")
    print("-" * 30)
    flight_result = search_flights_tool(
        origin="New York",
        destination="London",
        departure_date="2024-07-01",
        return_date="2024-07-08",
        passengers=1
    )
    print(flight_result)
    
    # Test hotel search tool
    print("\n2. Hotel Search Tool:")
    print("-" * 30)
    hotel_result = search_hotels_tool(
        destination="London",
        check_in="2024-07-01",
        check_out="2024-07-08",
        guests=1,
        rooms=1
    )
    print(hotel_result)
    
    # Test car rental search tool
    print("\n3. Car Rental Search Tool:")
    print("-" * 30)
    car_result = search_car_rentals_tool(
        pickup_location="London",
        pickup_date="2024-07-01",
        return_date="2024-07-08"
    )
    print(car_result)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "tools":
            test_travel_tools()
        elif sys.argv[1] == "agent":
            test_agent_with_tools()
        elif sys.argv[1] == "functions":
            test_individual_tool_functions()
        else:
            print("Usage: python test_tools.py [tools|agent|functions]")
    else:
        # Run all tests
        test_travel_tools()
        test_individual_tool_functions()
        test_agent_with_tools()
