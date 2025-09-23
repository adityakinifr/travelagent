"""
Travel tools for looking up flights, hotels, and car rentals
"""

import requests
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from pydantic import BaseModel
import time
import re

class FlightSearch(BaseModel):
    """Flight search parameters"""
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    passengers: int = 1
    class_type: str = "economy"

class FlightResult(BaseModel):
    """Flight search result"""
    airline: str
    flight_number: str
    departure_time: str
    arrival_time: str
    duration: str
    price: str
    stops: int
    departure_airport: str
    arrival_airport: str

class HotelSearch(BaseModel):
    """Hotel search parameters"""
    destination: str
    check_in: str
    check_out: str
    guests: int = 1
    rooms: int = 1

class HotelResult(BaseModel):
    """Hotel search result"""
    name: str
    price_per_night: str
    total_price: str
    rating: str
    location: str
    amenities: List[str]
    availability: bool

class CarRentalSearch(BaseModel):
    """Car rental search parameters"""
    pickup_location: str
    pickup_date: str
    return_date: str
    pickup_time: str = "10:00"
    return_time: str = "10:00"

class CarRentalResult(BaseModel):
    """Car rental search result"""
    company: str
    car_type: str
    price_per_day: str
    total_price: str
    pickup_location: str
    features: List[str]
    availability: bool

class TravelTools:
    """Collection of tools for travel data lookup"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search_flights_google(self, search: FlightSearch) -> List[FlightResult]:
        """
        Search for flights using Google Flights
        Note: This is a simplified implementation. In production, you'd use official APIs.
        """
        try:
            # For demonstration, we'll return mock data
            # In a real implementation, you'd scrape Google Flights or use their API
            mock_flights = [
                FlightResult(
                    airline="American Airlines",
                    flight_number="AA1234",
                    departure_time="08:30",
                    arrival_time="11:45",
                    duration="3h 15m",
                    price="$299",
                    stops=0,
                    departure_airport=search.origin,
                    arrival_airport=search.destination
                ),
                FlightResult(
                    airline="Delta",
                    flight_number="DL5678",
                    departure_time="14:20",
                    arrival_time="17:35",
                    duration="3h 15m",
                    price="$325",
                    stops=0,
                    departure_airport=search.origin,
                    arrival_airport=search.destination
                ),
                FlightResult(
                    airline="United",
                    flight_number="UA9012",
                    departure_time="19:45",
                    arrival_time="23:00",
                    duration="3h 15m",
                    price="$275",
                    stops=0,
                    departure_airport=search.origin,
                    arrival_airport=search.destination
                )
            ]
            return mock_flights
        except Exception as e:
            print(f"Error searching flights: {e}")
            return []
    
    def search_flights_skyscanner(self, search: FlightSearch) -> List[FlightResult]:
        """
        Search for flights using Skyscanner (mock implementation)
        """
        try:
            # Mock Skyscanner results
            mock_flights = [
                FlightResult(
                    airline="Lufthansa",
                    flight_number="LH456",
                    departure_time="09:15",
                    arrival_time="12:30",
                    duration="3h 15m",
                    price="$280",
                    stops=0,
                    departure_airport=search.origin,
                    arrival_airport=search.destination
                ),
                FlightResult(
                    airline="Air France",
                    flight_number="AF789",
                    departure_time="16:30",
                    arrival_time="19:45",
                    duration="3h 15m",
                    price="$310",
                    stops=0,
                    departure_airport=search.origin,
                    arrival_airport=search.destination
                )
            ]
            return mock_flights
        except Exception as e:
            print(f"Error searching flights on Skyscanner: {e}")
            return []
    
    def search_hotels_booking(self, search: HotelSearch) -> List[HotelResult]:
        """
        Search for hotels using Booking.com (mock implementation)
        """
        try:
            # Mock Booking.com results
            mock_hotels = [
                HotelResult(
                    name="Grand Hotel Central",
                    price_per_night="$150",
                    total_price="$750",
                    rating="4.5",
                    location="City Center",
                    amenities=["WiFi", "Pool", "Gym", "Restaurant"],
                    availability=True
                ),
                HotelResult(
                    name="Boutique Hotel Paris",
                    price_per_night="$120",
                    total_price="$600",
                    rating="4.2",
                    location="Near Eiffel Tower",
                    amenities=["WiFi", "Breakfast", "Concierge"],
                    availability=True
                ),
                HotelResult(
                    name="Budget Inn Express",
                    price_per_night="$80",
                    total_price="$400",
                    rating="3.8",
                    location="Airport Area",
                    amenities=["WiFi", "Parking", "Shuttle"],
                    availability=True
                )
            ]
            return mock_hotels
        except Exception as e:
            print(f"Error searching hotels: {e}")
            return []
    
    def search_hotels_expedia(self, search: HotelSearch) -> List[HotelResult]:
        """
        Search for hotels using Expedia (mock implementation)
        """
        try:
            # Mock Expedia results
            mock_hotels = [
                HotelResult(
                    name="Luxury Resort & Spa",
                    price_per_night="$200",
                    total_price="$1000",
                    rating="4.7",
                    location="Beachfront",
                    amenities=["WiFi", "Pool", "Spa", "Restaurant", "Beach Access"],
                    availability=True
                ),
                HotelResult(
                    name="Business Hotel Plaza",
                    price_per_night="$110",
                    total_price="$550",
                    rating="4.0",
                    location="Business District",
                    amenities=["WiFi", "Gym", "Business Center", "Restaurant"],
                    availability=True
                )
            ]
            return mock_hotels
        except Exception as e:
            print(f"Error searching hotels on Expedia: {e}")
            return []
    
    def search_car_rentals_hertz(self, search: CarRentalSearch) -> List[CarRentalResult]:
        """
        Search for car rentals using Hertz (mock implementation)
        """
        try:
            # Mock Hertz results
            mock_cars = [
                CarRentalResult(
                    company="Hertz",
                    car_type="Economy Car",
                    price_per_day="$45",
                    total_price="$225",
                    pickup_location=search.pickup_location,
                    features=["Automatic", "AC", "4 doors"],
                    availability=True
                ),
                CarRentalResult(
                    company="Hertz",
                    car_type="Mid-size SUV",
                    price_per_day="$75",
                    total_price="$375",
                    pickup_location=search.pickup_location,
                    features=["Automatic", "AC", "GPS", "Bluetooth"],
                    availability=True
                )
            ]
            return mock_cars
        except Exception as e:
            print(f"Error searching car rentals: {e}")
            return []
    
    def search_car_rentals_avis(self, search: CarRentalSearch) -> List[CarRentalResult]:
        """
        Search for car rentals using Avis (mock implementation)
        """
        try:
            # Mock Avis results
            mock_cars = [
                CarRentalResult(
                    company="Avis",
                    car_type="Compact Car",
                    price_per_day="$40",
                    total_price="$200",
                    pickup_location=search.pickup_location,
                    features=["Manual", "AC", "4 doors"],
                    availability=True
                ),
                CarRentalResult(
                    company="Avis",
                    car_type="Luxury Sedan",
                    price_per_day="$120",
                    total_price="$600",
                    pickup_location=search.pickup_location,
                    features=["Automatic", "AC", "GPS", "Leather Seats", "Premium Sound"],
                    availability=True
                )
            ]
            return mock_cars
        except Exception as e:
            print(f"Error searching car rentals on Avis: {e}")
            return []
    
    def search_all_flights(self, search: FlightSearch) -> List[FlightResult]:
        """Search multiple flight providers and combine results"""
        all_flights = []
        
        # Search Google Flights
        google_flights = self.search_flights_google(search)
        all_flights.extend(google_flights)
        
        # Search Skyscanner
        skyscanner_flights = self.search_flights_skyscanner(search)
        all_flights.extend(skyscanner_flights)
        
        # Sort by price
        all_flights.sort(key=lambda x: float(re.sub(r'[^\d.]', '', x.price)))
        
        return all_flights
    
    def search_all_hotels(self, search: HotelSearch) -> List[HotelResult]:
        """Search multiple hotel providers and combine results"""
        all_hotels = []
        
        # Search Booking.com
        booking_hotels = self.search_hotels_booking(search)
        all_hotels.extend(booking_hotels)
        
        # Search Expedia
        expedia_hotels = self.search_hotels_expedia(search)
        all_hotels.extend(expedia_hotels)
        
        # Sort by price
        all_hotels.sort(key=lambda x: float(re.sub(r'[^\d.]', '', x.price_per_night)))
        
        return all_hotels
    
    def search_all_car_rentals(self, search: CarRentalSearch) -> List[CarRentalResult]:
        """Search multiple car rental providers and combine results"""
        all_cars = []
        
        # Search Hertz
        hertz_cars = self.search_car_rentals_hertz(search)
        all_cars.extend(hertz_cars)
        
        # Search Avis
        avis_cars = self.search_car_rentals_avis(search)
        all_cars.extend(avis_cars)
        
        # Sort by price
        all_cars.sort(key=lambda x: float(re.sub(r'[^\d.]', '', x.price_per_day)))
        
        return all_cars

# Tool functions for LangChain integration
def search_flights_tool(origin: str, destination: str, departure_date: str, 
                       return_date: str = None, passengers: int = 1, 
                       class_type: str = "economy") -> str:
    """
    Tool for searching flights
    """
    tools = TravelTools()
    search = FlightSearch(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        return_date=return_date,
        passengers=passengers,
        class_type=class_type
    )
    
    flights = tools.search_all_flights(search)
    
    if not flights:
        return "No flights found for the given criteria."
    
    result = f"Found {len(flights)} flights from {origin} to {destination}:\n\n"
    for i, flight in enumerate(flights, 1):
        result += f"{i}. {flight.airline} {flight.flight_number}\n"
        result += f"   Departure: {flight.departure_time} | Arrival: {flight.arrival_time}\n"
        result += f"   Duration: {flight.duration} | Price: {flight.price}\n"
        result += f"   Stops: {flight.stops}\n\n"
    
    return result

def search_hotels_tool(destination: str, check_in: str, check_out: str, 
                      guests: int = 1, rooms: int = 1) -> str:
    """
    Tool for searching hotels
    """
    tools = TravelTools()
    search = HotelSearch(
        destination=destination,
        check_in=check_in,
        check_out=check_out,
        guests=guests,
        rooms=rooms
    )
    
    hotels = tools.search_all_hotels(search)
    
    if not hotels:
        return "No hotels found for the given criteria."
    
    result = f"Found {len(hotels)} hotels in {destination}:\n\n"
    for i, hotel in enumerate(hotels, 1):
        result += f"{i}. {hotel.name}\n"
        result += f"   Price: {hotel.price_per_night}/night (Total: {hotel.total_price})\n"
        result += f"   Rating: {hotel.rating} | Location: {hotel.location}\n"
        result += f"   Amenities: {', '.join(hotel.amenities)}\n\n"
    
    return result

def search_car_rentals_tool(pickup_location: str, pickup_date: str, return_date: str,
                           pickup_time: str = "10:00", return_time: str = "10:00") -> str:
    """
    Tool for searching car rentals
    """
    tools = TravelTools()
    search = CarRentalSearch(
        pickup_location=pickup_location,
        pickup_date=pickup_date,
        return_date=return_date,
        pickup_time=pickup_time,
        return_time=return_time
    )
    
    cars = tools.search_all_car_rentals(search)
    
    if not cars:
        return "No car rentals found for the given criteria."
    
    result = f"Found {len(cars)} car rental options in {pickup_location}:\n\n"
    for i, car in enumerate(cars, 1):
        result += f"{i}. {car.company} - {car.car_type}\n"
        result += f"   Price: {car.price_per_day}/day (Total: {car.total_price})\n"
        result += f"   Features: {', '.join(car.features)}\n\n"
    
    return result
