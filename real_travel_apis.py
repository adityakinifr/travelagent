"""
Real API implementations for travel data lookup
"""

import os
import requests
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from dotenv import load_dotenv
from amadeus import Client, ResponseError
from serpapi import GoogleSearch

# Load environment variables
load_dotenv()

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
    currency: str = "USD"

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
    currency: str = "USD"

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
    currency: str = "USD"

class RealTravelAPIs:
    """Real API implementations for travel data"""
    
    def __init__(self):
        self.amadeus_client = None
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.flightsapi_key = os.getenv("FLIGHTSAPI_KEY")
        
        # Initialize Amadeus client if credentials are available
        amadeus_key = os.getenv("AMADEUS_API_KEY")
        amadeus_secret = os.getenv("AMADEUS_API_SECRET")
        
        if amadeus_key and amadeus_secret:
            self.amadeus_client = Client(
                client_id=amadeus_key,
                client_secret=amadeus_secret,
                hostname='https://test.api.amadeus.com'  # Use specific test API URL
            )
    
    def search_flights_amadeus(self, search: FlightSearch) -> List[FlightResult]:
        """Search flights using Amadeus API"""
        if not self.amadeus_client:
            print("Amadeus API credentials not configured")
            return []
        
        try:
            # Search for flights
            response = self.amadeus_client.shopping.flight_offers_search.get(
                originLocationCode=search.origin,
                destinationLocationCode=search.destination,
                departureDate=search.departure_date,
                adults=search.passengers,
                max=10
            )
            
            flights = []
            for offer in response.data:
                if offer['itineraries']:
                    itinerary = offer['itineraries'][0]
                    segments = itinerary['segments']
                    
                    if segments:
                        first_segment = segments[0]
                        last_segment = segments[-1]
                        
                        # Extract flight information
                        airline = first_segment['carrierCode']
                        flight_number = f"{airline}{first_segment['number']}"
                        departure_time = first_segment['departure']['at'][:16].replace('T', ' ')
                        arrival_time = last_segment['arrival']['at'][:16].replace('T', ' ')
                        
                        # Calculate duration
                        dep_time = datetime.fromisoformat(first_segment['departure']['at'].replace('Z', '+00:00'))
                        arr_time = datetime.fromisoformat(last_segment['arrival']['at'].replace('Z', '+00:00'))
                        duration = str(arr_time - dep_time).split('.')[0]
                        
                        # Get price
                        price = offer['price']['total']
                        currency = offer['price']['currency']
                        
                        # Count stops
                        stops = len(segments) - 1
                        
                        flights.append(FlightResult(
                            airline=airline,
                            flight_number=flight_number,
                            departure_time=departure_time,
                            arrival_time=arrival_time,
                            duration=duration,
                            price=f"{currency} {price}",
                            stops=stops,
                            departure_airport=first_segment['departure']['iataCode'],
                            arrival_airport=last_segment['arrival']['iataCode'],
                            currency=currency
                        ))
            
            return flights
            
        except ResponseError as error:
            print(f"Amadeus API error: {error}")
            return []
        except Exception as e:
            print(f"Error searching flights with Amadeus: {e}")
            return []
    
    def search_flights_serpapi(self, search: FlightSearch) -> List[FlightResult]:
        """Search flights using SerpAPI (Google Flights)"""
        if not self.serpapi_key:
            print("SerpAPI key not configured")
            return []
        
        try:
            params = {
                "engine": "google_flights",
                "departure_id": search.origin,
                "arrival_id": search.destination,
                "outbound_date": search.departure_date,
                "return_date": search.return_date,
                "adults": search.passengers,
                "currency": "USD",
                "api_key": self.serpapi_key
            }
            
            search_engine = GoogleSearch(params)
            results = search_engine.get_dict()
            
            flights = []
            if 'flights' in results:
                for flight_data in results['flights'][:5]:  # Limit to 5 results
                    flights.append(FlightResult(
                        airline=flight_data.get('airline', 'Unknown'),
                        flight_number=flight_data.get('flight_number', 'N/A'),
                        departure_time=flight_data.get('departure_time', 'N/A'),
                        arrival_time=flight_data.get('arrival_time', 'N/A'),
                        duration=flight_data.get('duration', 'N/A'),
                        price=flight_data.get('price', 'N/A'),
                        stops=flight_data.get('stops', 0),
                        departure_airport=search.origin,
                        arrival_airport=search.destination,
                        currency="USD"
                    ))
            
            return flights
            
        except Exception as e:
            print(f"Error searching flights with SerpAPI: {e}")
            return []
    
    def search_flights_flightsapi(self, search: FlightSearch) -> List[FlightResult]:
        """Search flights using FlightsAPI.io"""
        if not self.flightsapi_key:
            print("FlightsAPI key not configured")
            return []
        
        try:
            url = "https://api.flightsapi.io/api/flights"
            headers = {
                "Authorization": f"Bearer {self.flightsapi_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "from": search.origin,
                "to": search.destination,
                "departure_date": search.departure_date,
                "return_date": search.return_date,
                "adults": search.passengers,
                "currency": "USD"
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            flights_data = response.json()
            flights = []
            
            if 'data' in flights_data:
                for flight_data in flights_data['data'][:5]:  # Limit to 5 results
                    flights.append(FlightResult(
                        airline=flight_data.get('airline', 'Unknown'),
                        flight_number=flight_data.get('flight_number', 'N/A'),
                        departure_time=flight_data.get('departure_time', 'N/A'),
                        arrival_time=flight_data.get('arrival_time', 'N/A'),
                        duration=flight_data.get('duration', 'N/A'),
                        price=flight_data.get('price', 'N/A'),
                        stops=flight_data.get('stops', 0),
                        departure_airport=search.origin,
                        arrival_airport=search.destination,
                        currency="USD"
                    ))
            
            return flights
            
        except Exception as e:
            print(f"Error searching flights with FlightsAPI: {e}")
            return []
    
    def search_hotels_amadeus(self, search: HotelSearch) -> List[HotelResult]:
        """Search hotels using Amadeus API"""
        if not self.amadeus_client:
            print("Amadeus API credentials not configured")
            return []
        
        try:
            # First, get the city code for the destination
            city_response = self.amadeus_client.reference_data.locations.get(
                keyword=search.destination,
                subType='CITY'
            )
            
            if not city_response.data:
                print(f"No city found for destination: {search.destination}")
                return []
            
            city_code = city_response.data[0]['iataCode']
            
            # Search for hotels
            response = self.amadeus_client.shopping.hotel_offers.get(
                cityCode=city_code,
                checkInDate=search.check_in,
                checkOutDate=search.check_out,
                adults=search.guests,
                roomQuantity=search.rooms,
                max=10
            )
            
            hotels = []
            for offer in response.data:
                hotel_data = offer['hotel']
                price_data = offer['offers'][0]['price']
                
                # Extract amenities
                amenities = []
                if 'amenities' in hotel_data:
                    amenities = [amenity['description'] for amenity in hotel_data['amenities']]
                
                hotels.append(HotelResult(
                    name=hotel_data['name'],
                    price_per_night=f"{price_data['currency']} {price_data['base']}",
                    total_price=f"{price_data['currency']} {price_data['total']}",
                    rating=str(hotel_data.get('rating', 'N/A')),
                    location=hotel_data.get('address', {}).get('cityName', search.destination),
                    amenities=amenities,
                    availability=True,
                    currency=price_data['currency']
                ))
            
            return hotels
            
        except ResponseError as error:
            print(f"Amadeus API error: {error}")
            return []
        except Exception as e:
            print(f"Error searching hotels with Amadeus: {e}")
            return []
    
    def search_car_rentals_amadeus(self, search: CarRentalSearch) -> List[CarRentalResult]:
        """Search car rentals using Amadeus API"""
        if not self.amadeus_client:
            print("Amadeus API credentials not configured")
            return []
        
        try:
            # Search for car rentals
            response = self.amadeus_client.shopping.car_rental_offers.get(
                pickUpLocationCode=search.pickup_location,
                dropOffLocationCode=search.pickup_location,  # Same location for round trip
                pickUpDateTime=search.pickup_date,
                dropOffDateTime=search.return_date,
                currency='USD'
            )
            
            cars = []
            for offer in response.data:
                car_data = offer['car']
                price_data = offer['price']
                
                # Extract features
                features = []
                if 'features' in car_data:
                    features = [feature['description'] for feature in car_data['features']]
                
                cars.append(CarRentalResult(
                    company=offer.get('provider', {}).get('name', 'Unknown'),
                    car_type=car_data.get('model', 'Unknown'),
                    price_per_day=f"{price_data['currency']} {price_data['base']}",
                    total_price=f"{price_data['currency']} {price_data['total']}",
                    pickup_location=search.pickup_location,
                    features=features,
                    availability=True,
                    currency=price_data['currency']
                ))
            
            return cars
            
        except ResponseError as error:
            print(f"Amadeus API error: {error}")
            return []
        except Exception as e:
            print(f"Error searching car rentals with Amadeus: {e}")
            return []
    
    def search_all_flights(self, search: FlightSearch) -> List[FlightResult]:
        """Search multiple flight providers and combine results"""
        all_flights = []
        
        # Try Amadeus first
        amadeus_flights = self.search_flights_amadeus(search)
        all_flights.extend(amadeus_flights)
        
        # Try SerpAPI if Amadeus didn't return results
        if not all_flights:
            serpapi_flights = self.search_flights_serpapi(search)
            all_flights.extend(serpapi_flights)
        
        # Try FlightsAPI as fallback
        if not all_flights:
            flightsapi_flights = self.search_flights_flightsapi(search)
            all_flights.extend(flightsapi_flights)
        
        # Sort by price (convert to float for sorting)
        def extract_price(flight):
            try:
                price_str = flight.price.replace('USD', '').replace('$', '').strip()
                return float(price_str)
            except:
                return float('inf')
        
        all_flights.sort(key=extract_price)
        
        return all_flights[:10]  # Return top 10 results
    
    def search_all_hotels(self, search: HotelSearch) -> List[HotelResult]:
        """Search multiple hotel providers and combine results"""
        all_hotels = []
        
        # Use Amadeus for hotels
        amadeus_hotels = self.search_hotels_amadeus(search)
        all_hotels.extend(amadeus_hotels)
        
        # Sort by price
        def extract_price(hotel):
            try:
                price_str = hotel.price_per_night.replace('USD', '').replace('$', '').strip()
                return float(price_str)
            except:
                return float('inf')
        
        all_hotels.sort(key=extract_price)
        
        return all_hotels[:10]  # Return top 10 results
    
    def search_all_car_rentals(self, search: CarRentalSearch) -> List[CarRentalResult]:
        """Search multiple car rental providers and combine results"""
        all_cars = []
        
        # Use Amadeus for car rentals
        amadeus_cars = self.search_car_rentals_amadeus(search)
        all_cars.extend(amadeus_cars)
        
        # Sort by price
        def extract_price(car):
            try:
                price_str = car.price_per_day.replace('USD', '').replace('$', '').strip()
                return float(price_str)
            except:
                return float('inf')
        
        all_cars.sort(key=extract_price)
        
        return all_cars[:10]  # Return top 10 results

# Tool functions for LangChain integration
def search_flights_real_api(origin: str, destination: str, departure_date: str, 
                           return_date: str = None, passengers: int = 1, 
                           class_type: str = "economy") -> str:
    """
    Tool for searching flights using real APIs
    """
    apis = RealTravelAPIs()
    search = FlightSearch(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        return_date=return_date,
        passengers=passengers,
        class_type=class_type
    )
    
    flights = apis.search_all_flights(search)
    
    if not flights:
        return "No flights found for the given criteria. Please check your search parameters or try again later."
    
    result = f"Found {len(flights)} flights from {origin} to {destination}:\n\n"
    for i, flight in enumerate(flights, 1):
        result += f"{i}. {flight.airline} {flight.flight_number}\n"
        result += f"   Departure: {flight.departure_time} | Arrival: {flight.arrival_time}\n"
        result += f"   Duration: {flight.duration} | Price: {flight.price}\n"
        result += f"   Stops: {flight.stops} | Route: {flight.departure_airport} → {flight.arrival_airport}\n\n"
    
    return result

def search_hotels_real_api(destination: str, check_in: str, check_out: str, 
                          guests: int = 1, rooms: int = 1) -> str:
    """
    Tool for searching hotels using real APIs
    """
    apis = RealTravelAPIs()
    search = HotelSearch(
        destination=destination,
        check_in=check_in,
        check_out=check_out,
        guests=guests,
        rooms=rooms
    )
    
    hotels = apis.search_all_hotels(search)
    
    if not hotels:
        return "No hotels found for the given criteria. Please check your search parameters or try again later."
    
    result = f"Found {len(hotels)} hotels in {destination}:\n\n"
    for i, hotel in enumerate(hotels, 1):
        result += f"{i}. {hotel.name}\n"
        result += f"   Price: {hotel.price_per_night}/night (Total: {hotel.total_price})\n"
        result += f"   Rating: {hotel.rating} | Location: {hotel.location}\n"
        result += f"   Amenities: {', '.join(hotel.amenities[:3])}{'...' if len(hotel.amenities) > 3 else ''}\n\n"
    
    return result

def search_car_rentals_real_api(pickup_location: str, pickup_date: str, return_date: str,
                               pickup_time: str = "10:00", return_time: str = "10:00") -> str:
    """
    Tool for searching car rentals using real APIs
    """
    apis = RealTravelAPIs()
    search = CarRentalSearch(
        pickup_location=pickup_location,
        pickup_date=pickup_date,
        return_date=return_date,
        pickup_time=pickup_time,
        return_time=return_time
    )
    
    cars = apis.search_all_car_rentals(search)
    
    if not cars:
        return "No car rentals found for the given criteria. Please check your search parameters or try again later."
    
    result = f"Found {len(cars)} car rental options in {pickup_location}:\n\n"
    for i, car in enumerate(cars, 1):
        result += f"{i}. {car.company} - {car.car_type}\n"
        result += f"   Price: {car.price_per_day}/day (Total: {car.total_price})\n"
        result += f"   Features: {', '.join(car.features[:3])}{'...' if len(car.features) > 3 else ''}\n\n"
    
    return result
