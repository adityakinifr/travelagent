"""
Mock data for testing and demonstration purposes
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import random

class MockDataProvider:
    """Provides mock data for all travel-related services"""
    
    def __init__(self):
        self.destinations = [
            {
                "name": "Maui",
                "country": "United States",
                "region": "Hawaii",
                "description": "Beautiful Hawaiian island with pristine beaches, volcanic landscapes, and world-class resorts.",
                "best_time_to_visit": "April to May, September to November",
                "family_friendly_score": 9,
                "safety_rating": "Very Safe",
                "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400",
                "estimated_cost": "$800",
                "travel_time_from_origin": "5h 30m",
                "key_attractions": ["Haleakala National Park", "Road to Hana", "Wailea Beach", "Lahaina Town"],
                "activities": ["Beach relaxation", "Snorkeling", "Hiking", "Whale watching", "Cultural tours"],
                "climate": "Tropical with warm temperatures year-round",
                "visa_requirements": "US citizens: No visa required",
                "language": "English, Hawaiian",
                "currency": "USD",
                "why_recommended": "Perfect blend of adventure and relaxation with stunning natural beauty",
                "seasonal_highlights": {
                    "summer": "Perfect beach weather, whale watching season",
                    "winter": "Mild temperatures, great for hiking",
                    "spring": "Wildflower blooms, fewer crowds",
                    "fall": "Harvest season, cultural festivals"
                }
            },
            {
                "name": "Santa Barbara",
                "country": "United States",
                "region": "California",
                "description": "Charming coastal city with Spanish architecture, wine country, and beautiful beaches.",
                "best_time_to_visit": "March to May, September to November",
                "family_friendly_score": 8,
                "safety_rating": "Very Safe",
                "image_url": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=400",
                "estimated_cost": "$600",
                "travel_time_from_origin": "1h 15m",
                "key_attractions": ["Stearns Wharf", "Santa Barbara Mission", "State Street", "Wine Country"],
                "activities": ["Wine tasting", "Beach activities", "Shopping", "Cultural tours", "Hiking"],
                "climate": "Mediterranean with mild, wet winters and warm, dry summers",
                "visa_requirements": "US citizens: No visa required",
                "language": "English, Spanish",
                "currency": "USD",
                "why_recommended": "Perfect blend of beach relaxation, wine country, and cultural attractions",
                "seasonal_highlights": {
                    "summer": "Warm ocean temperatures, outdoor festivals",
                    "winter": "Mild climate, wine tasting season",
                    "spring": "Wildflower super bloom, perfect hiking",
                    "fall": "Harvest festivals, ideal weather"
                }
            },
            {
                "name": "Monterey",
                "country": "United States",
                "region": "California",
                "description": "Historic coastal town famous for its aquarium, Cannery Row, and stunning Pacific views.",
                "best_time_to_visit": "April to October",
                "family_friendly_score": 9,
                "safety_rating": "Very Safe", 
                "image_url": "https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=400",
                "estimated_cost": "$500",
                "travel_time_from_origin": "2h 30m",
                "key_attractions": ["Monterey Bay Aquarium", "Cannery Row", "17-Mile Drive", "Fisherman's Wharf"],
                "activities": ["Aquarium visits", "Whale watching", "Golf", "Wine tasting", "Coastal hiking"],
                "climate": "Mediterranean with cool, foggy summers and mild winters",
                "visa_requirements": "US citizens: No visa required",
                "language": "English, Spanish",
                "currency": "USD",
                "why_recommended": "Perfect family destination with world-class aquarium and stunning coastal scenery",
                "seasonal_highlights": {
                    "summer": "Whale watching, outdoor concerts",
                    "winter": "Storm watching, cozy coastal vibes",
                    "spring": "Wildflower season, mild temperatures",
                    "fall": "Harvest time, fewer tourists"
                }
            },
            {
                "name": "San Diego",
                "country": "United States",
                "region": "California",
                "description": "Sunny Southern California city with perfect weather, world-class beaches, and family attractions.",
                "best_time_to_visit": "Year-round (best: March to May, September to November)",
                "family_friendly_score": 10,
                "safety_rating": "Very Safe",
                "image_url": "https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=400",
                "estimated_cost": "$700",
                "travel_time_from_origin": "1h 30m",
                "key_attractions": ["San Diego Zoo", "Balboa Park", "La Jolla Cove", "Gaslamp Quarter"],
                "activities": ["Zoo visits", "Beach activities", "Museums", "Hiking", "Water sports"],
                "climate": "Mediterranean with warm, dry summers and mild, wet winters",
                "visa_requirements": "US citizens: No visa required",
                "language": "English, Spanish",
                "currency": "USD",
                "why_recommended": "Perfect family destination with year-round perfect weather and world-class attractions",
                "seasonal_highlights": {
                    "summer": "Perfect beach weather, outdoor activities",
                    "winter": "Mild temperatures, whale watching",
                    "spring": "Wildflower blooms, ideal hiking",
                    "fall": "Harvest festivals, perfect weather"
                }
            },
            {
                "name": "Napa Valley",
                "country": "United States",
                "region": "California",
                "description": "World-renowned wine region with rolling vineyards, gourmet dining, and luxury resorts.",
                "best_time_to_visit": "August to October (harvest season)",
                "family_friendly_score": 6,
                "safety_rating": "Very Safe",
                "image_url": "https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?w=400",
                "estimated_cost": "$900",
                "travel_time_from_origin": "1h 45m",
                "key_attractions": ["Wine Country", "Castello di Amorosa", "Napa Valley Wine Train", "Oxbow Public Market"],
                "activities": ["Wine tasting", "Vineyard tours", "Gourmet dining", "Hot air ballooning", "Spa treatments"],
                "climate": "Mediterranean with warm, dry summers and cool, wet winters",
                "visa_requirements": "US citizens: No visa required",
                "language": "English, Spanish",
                "currency": "USD",
                "why_recommended": "Perfect for wine lovers and couples seeking luxury and romance",
                "seasonal_highlights": {
                    "summer": "Vineyard tours, outdoor dining",
                    "winter": "Cozy wine tastings, spa retreats",
                    "spring": "Bud break season, mild weather",
                    "fall": "Harvest season, wine festivals"
                }
            }
        ]
        
        self.flights = [
            {
                "airline": "United Airlines",
                "flight_number": "UA1234",
                "departure_time": "08:30",
                "arrival_time": "10:00",
                "duration": "1h 30m",
                "price": 250,
                "stops": 0,
                "departure_airport": "SFO",
                "arrival_airport": "SAN",
                "currency": "USD"
            },
            {
                "airline": "Alaska Airlines", 
                "flight_number": "AS5678",
                "departure_time": "14:15",
                "arrival_time": "15:45",
                "duration": "1h 30m",
                "price": 280,
                "stops": 0,
                "departure_airport": "SFO",
                "arrival_airport": "SAN",
                "currency": "USD"
            },
            {
                "airline": "Southwest Airlines",
                "flight_number": "WN9012",
                "departure_time": "11:20",
                "arrival_time": "12:50",
                "duration": "1h 30m", 
                "price": 220,
                "stops": 0,
                "departure_airport": "SFO",
                "arrival_airport": "SAN",
                "currency": "USD"
            }
        ]
        
        self.hotels = [
            {
                "name": "Hotel del Coronado",
                "price_per_night": "$350",
                "total_price": "$2,450",
                "rating": "4.5",
                "location": "San Diego, CA",
                "amenities": ["Beachfront", "Pool", "Spa", "Restaurant", "WiFi"],
                "availability": True,
                "currency": "USD"
            },
            {
                "name": "The Ritz-Carlton, Laguna Niguel",
                "price_per_night": "$450",
                "total_price": "$3,150", 
                "rating": "4.8",
                "location": "Dana Point, CA",
                "amenities": ["Ocean View", "Pool", "Spa", "Golf", "Restaurant", "WiFi"],
                "availability": True,
                "currency": "USD"
            },
            {
                "name": "Monterey Plaza Hotel & Spa",
                "price_per_night": "$280",
                "total_price": "$1,960",
                "rating": "4.3",
                "location": "Monterey, CA", 
                "amenities": ["Ocean View", "Spa", "Restaurant", "WiFi", "Parking"],
                "availability": True,
                "currency": "USD"
            }
        ]

    def get_mock_destinations(self, query: str = "", max_results: int = 5) -> List[Dict[str, Any]]:
        """Get mock destinations based on query"""
        # Filter destinations based on query keywords
        filtered_destinations = []
        query_lower = query.lower()
        
        for dest in self.destinations:
            if any(keyword in dest["name"].lower() or keyword in dest["description"].lower() 
                   for keyword in ["beach", "sunny", "coastal", "ocean"] if keyword in query_lower):
                filtered_destinations.append(dest)
            elif not query_lower or "beach" in query_lower or "sunny" in query_lower:
                # Default to beach destinations if no specific query
                if any(keyword in dest["description"].lower() 
                       for keyword in ["beach", "coastal", "ocean"]):
                    filtered_destinations.append(dest)
        
        # If no matches, return first few destinations
        if not filtered_destinations:
            filtered_destinations = self.destinations[:max_results]
        else:
            filtered_destinations = filtered_destinations[:max_results]
            
        return filtered_destinations

    def get_mock_flights(self, origin: str, destination: str, departure_date: str, return_date: str = None) -> List[Dict[str, Any]]:
        """Get mock flight data"""
        # Return a subset of flights with some randomization
        num_flights = random.randint(2, 4)
        selected_flights = random.sample(self.flights, min(num_flights, len(self.flights)))
        
        # Modify prices slightly for variety
        for flight in selected_flights:
            flight["price"] = flight["price"] + random.randint(-50, 100)
            
        return selected_flights

    def get_mock_hotels(self, destination: str, check_in: str, check_out: str) -> List[Dict[str, Any]]:
        """Get mock hotel data"""
        # Return a subset of hotels with some randomization
        num_hotels = random.randint(2, 3)
        selected_hotels = random.sample(self.hotels, min(num_hotels, len(self.hotels)))
        
        # Modify prices slightly for variety
        for hotel in selected_hotels:
            base_price = int(hotel["price_per_night"].replace("$", "").replace(",", ""))
            new_price = base_price + random.randint(-50, 100)
            hotel["price_per_night"] = f"${new_price}"
            hotel["total_price"] = f"${new_price * 7}"  # Assume 7 nights
            
        return selected_hotels

    def get_mock_extracted_parameters(self, user_request: str) -> Dict[str, Any]:
        """Get mock extracted parameters"""
        return {
            "query": "sunny beach destination",
            "origin_location": "SFO",
            "max_travel_time": "5 hours",
            "travel_dates": "next summer",
            "budget": "$20000",
            "interests": ["beaches", "outdoor activities"],
            "travel_style": "comfortable",
            "traveler_type": "leisure",
            "group_size": 2,
            "age_range": "adults",
            "mobility_requirements": "active",
            "seasonal_preferences": "summer"
        }

    def get_mock_feasibility_result(self, destination: str, origin: str) -> Dict[str, Any]:
        """Get mock feasibility result"""
        return {
            "is_feasible": True,
            "feasibility_score": random.uniform(0.7, 0.95),
            "issues": [],
            "alternatives": [],
            "estimated_total_cost": random.randint(800, 2000),
            "flight_available": True,
            "hotel_available": True,
            "within_budget": True,
            "details": {
                "flight": {
                    "available": True,
                    "cost": random.randint(200, 400),
                    "airline": "United Airlines",
                    "departure_time": "08:30",
                    "arrival_time": "10:00",
                    "flight_duration": "1h 30m",
                    "total_flights": 1
                },
                "hotel": {
                    "available": True,
                    "cost": random.randint(600, 1200),
                    "price_per_night": random.randint(100, 200),
                    "hotel_name": "Luxury Resort",
                    "rating": "4.5",
                    "nights": 7,
                    "total_hotels": 1
                }
            }
        }

# Global instance
mock_data = MockDataProvider()
