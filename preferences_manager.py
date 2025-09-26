"""
Travel Preferences Manager for handling user travel preferences and customization
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

class TravelPreferences(BaseModel):
    """Structure for travel preferences"""
    traveler_profile: Dict[str, Any] = {}
    hotel_preferences: Dict[str, Any] = {}
    flight_preferences: Dict[str, Any] = {}
    travel_behavior: Dict[str, Any] = {}
    dining_preferences: Dict[str, Any] = {}
    activity_preferences: Dict[str, Any] = {}
    transportation_preferences: Dict[str, Any] = {}
    budget_preferences: Dict[str, Any] = {}
    special_requirements: Dict[str, Any] = {}
    loyalty_programs: Dict[str, Any] = {}
    travel_insurance: Dict[str, Any] = {}
    technology_preferences: Dict[str, Any] = {}
    packing_preferences: Dict[str, Any] = {}
    communication_preferences: Dict[str, Any] = {}
    health_wellness: Dict[str, Any] = {}
    safety_security: Dict[str, Any] = {}
    cultural_preferences: Dict[str, Any] = {}
    environmental_preferences: Dict[str, Any] = {}
    entertainment_preferences: Dict[str, Any] = {}
    photography_social: Dict[str, Any] = {}
    flexibility_preferences: Dict[str, Any] = {}
    group_dynamics: Dict[str, Any] = {}
    learning_development: Dict[str, Any] = {}
    comfort_preferences: Dict[str, Any] = {}
    logistics_preferences: Dict[str, Any] = {}

class PreferencesManager:
    """Manages travel preferences and applies them to recommendations"""
    
    def __init__(self, preferences_file: str = "travel_preferences.json"):
        self.preferences_file = preferences_file
        self.preferences = self.load_preferences()
    
    def load_preferences(self) -> TravelPreferences:
        """Load preferences from JSON file"""
        try:
            if os.path.exists(self.preferences_file):
                with open(self.preferences_file, 'r') as f:
                    prefs_data = json.load(f)
                return TravelPreferences(**prefs_data)
            else:
                print(f"⚠️ Preferences file {self.preferences_file} not found, using defaults")
                return self.get_default_preferences()
        except Exception as e:
            print(f"❌ Error loading preferences: {e}")
            return self.get_default_preferences()
    
    def get_default_preferences(self) -> TravelPreferences:
        """Get default preferences if file doesn't exist"""
        default_prefs = {
            "traveler_profile": {
                "name": "Default Traveler",
                "travel_style": "balanced",
                "budget_level": "moderate",
                "frequent_traveler": False
            },
            "hotel_preferences": {
                "preferred_chains": ["Marriott", "Hilton", "Hyatt"],
                "avoided_chains": [],
                "loyalty_programs": [],
                "hotel_types": {
                    "business": ["business_hotel", "airport_hotel"],
                    "leisure": ["resort", "boutique"],
                    "family": ["family_resort", "suite_hotel"]
                },
                "amenities_required": ["wifi"],
                "amenities_preferred": ["pool", "restaurant"]
            },
            "flight_preferences": {
                "preferred_airlines": ["United Airlines", "American Airlines", "Delta Air Lines"],
                "airline_alliances": ["Star Alliance", "Oneworld", "SkyTeam"],
                "avoided_airlines": [],
                "class_preferences": {
                    "domestic_short": "economy",
                    "domestic_long": "economy",
                    "international_short": "premium_economy",
                    "international_long": "business",
                    "red_eye_flights": "business"
                },
                "seat_preferences": {
                    "window": True,
                    "aisle": False,
                    "exit_row": True,
                    "bulkhead": False
                },
                "red_eye_preference": "avoid",
                "layover_preferences": {
                    "max_layover_time_hours": 3,
                    "prefer_direct": True,
                    "min_connection_time_minutes": 60
                }
            },
            "travel_behavior": {
                "advance_booking_days": {
                    "domestic": 14,
                    "international": 30
                },
                "flexibility": {
                    "dates": "moderate",
                    "airports": "high",
                    "hotels": "moderate"
                },
                "trip_length_preferences": {
                    "weekend": "2-3 days",
                    "short_break": "4-5 days",
                    "vacation": "7-10 days",
                    "extended": "14+ days"
                }
            },
            "dining_preferences": {
                "cuisine_preferences": ["local_cuisine", "international"],
                "dietary_restrictions": [],
                "dining_style": "moderate",
                "meal_times": {
                    "breakfast": "hotel",
                    "lunch": "local",
                    "dinner": "restaurant"
                }
            },
            "activity_preferences": {
                "outdoor_activities": ["hiking", "beach_activities", "sightseeing"],
                "indoor_activities": ["museums", "shopping", "cultural_sites"],
                "adventure_level": "moderate",
                "cultural_interest": "high"
            },
            "transportation_preferences": {
                "ground_transport": {
                    "prefer_rental_car": True,
                    "prefer_public_transport": False,
                    "prefer_rideshare": True
                },
                "car_rental_preferences": {
                    "preferred_companies": ["Hertz", "Enterprise", "Avis"],
                    "car_types": {
                        "business": "sedan",
                        "leisure": "suv",
                        "family": "minivan"
                    }
                }
            },
            "budget_preferences": {
                "accommodation_budget": {
                    "budget": "$50-100",
                    "moderate": "$100-200",
                    "luxury": "$200+"
                },
                "flight_budget": {
                    "domestic": "$200-500",
                    "international": "$500-1500"
                },
                "daily_spending": {
                    "budget": "$50-100",
                    "moderate": "$100-200",
                    "luxury": "$200+"
                }
            },
            "special_requirements": {
                "accessibility_needs": [],
                "pet_travel": False,
                "smoking_preference": "non_smoking",
                "language_preferences": ["English"]
            }
        }
        return TravelPreferences(**default_prefs)
    
    def get_hotel_recommendations(self, destination: str, trip_type: str = "leisure") -> Dict[str, Any]:
        """Get hotel recommendations based on preferences"""
        hotel_prefs = self.preferences.hotel_preferences
        
        # Determine hotel type based on trip type
        hotel_types = hotel_prefs.get("hotel_types", {}).get(trip_type, ["hotel"])
        
        return {
            "preferred_chains": hotel_prefs.get("preferred_chains", []),
            "avoided_chains": hotel_prefs.get("avoided_chains", []),
            "loyalty_programs": hotel_prefs.get("loyalty_programs", []),
            "hotel_types": hotel_types,
            "amenities_required": hotel_prefs.get("amenities_required", []),
            "amenities_preferred": hotel_prefs.get("amenities_preferred", [])
        }
    
    def get_flight_recommendations(self, origin: str, destination: str, trip_length: str = "domestic_short") -> Dict[str, Any]:
        """Get flight recommendations based on preferences"""
        flight_prefs = self.preferences.flight_preferences
        
        # Determine flight class based on trip length and type
        class_prefs = flight_prefs.get("class_preferences", {})
        flight_class = class_prefs.get(trip_length, "economy")
        
        return {
            "preferred_airlines": flight_prefs.get("preferred_airlines", []),
            "airline_alliances": flight_prefs.get("airline_alliances", []),
            "avoided_airlines": flight_prefs.get("avoided_airlines", []),
            "flight_class": flight_class,
            "seat_preferences": flight_prefs.get("seat_preferences", {}),
            "red_eye_preference": flight_prefs.get("red_eye_preference", "avoid"),
            "layover_preferences": flight_prefs.get("layover_preferences", {})
        }
    
    def get_budget_guidelines(self, trip_type: str = "moderate") -> Dict[str, str]:
        """Get budget guidelines based on preferences"""
        budget_prefs = self.preferences.budget_preferences
        
        return {
            "accommodation": budget_prefs.get("accommodation_budget", {}).get(trip_type, "$100-200"),
            "flight": budget_prefs.get("flight_budget", {}).get("domestic", "$200-500"),
            "daily_spending": budget_prefs.get("daily_spending", {}).get(trip_type, "$100-200")
        }
    
    def get_activity_recommendations(self, destination: str) -> Dict[str, Any]:
        """Get activity recommendations based on preferences"""
        activity_prefs = self.preferences.activity_preferences
        
        return {
            "outdoor_activities": activity_prefs.get("outdoor_activities", []),
            "indoor_activities": activity_prefs.get("indoor_activities", []),
            "adventure_level": activity_prefs.get("adventure_level", "moderate"),
            "cultural_interest": activity_prefs.get("cultural_interest", "high")
        }
    
    def get_transportation_recommendations(self, trip_type: str = "leisure") -> Dict[str, Any]:
        """Get transportation recommendations based on preferences"""
        transport_prefs = self._ensure_dict(self.preferences.transportation_preferences)
        ground_transport = self._ensure_dict(transport_prefs.get("ground_transport", {}))
        car_rental_prefs = self._ensure_dict(transport_prefs.get("car_rental_preferences", {}))

        car_types = car_rental_prefs.get("car_types", {})
        if not isinstance(car_types, dict):
            car_types = {}

        preferred_car_type = car_types.get(trip_type)
        if not isinstance(preferred_car_type, str):
            # Try a sensible fallback based on common trip types before defaulting
            fallback_keys = ["leisure", "business", "family"]
            for key in fallback_keys:
                value = car_types.get(key)
                if isinstance(value, str):
                    preferred_car_type = value
                    break
        if not isinstance(preferred_car_type, str):
            preferred_car_type = "sedan"

        return {
            "ground_transport": ground_transport,
            "car_rental": car_rental_prefs,
            "preferred_car_type": preferred_car_type
        }
    
    def determine_trip_type(self, destination: str, duration: str, traveler_type: str = "leisure") -> str:
        """Determine trip type based on destination, duration, and traveler type"""
        # Business vs leisure logic
        if traveler_type == "business":
            return "business"
        
        # Duration-based logic
        if "weekend" in duration.lower() or "2-3" in duration:
            return "weekend"
        elif "short" in duration.lower() or "4-5" in duration:
            return "short_break"
        elif "vacation" in duration.lower() or "7-10" in duration:
            return "vacation"
        elif "extended" in duration.lower() or "14+" in duration:
            return "extended"
        
        return "leisure"
    
    def determine_flight_class(self, origin: str, destination: str, trip_length: str, is_red_eye: bool = False) -> str:
        """Determine appropriate flight class based on preferences and trip details"""
        flight_prefs = self.preferences.flight_preferences
        class_prefs = flight_prefs.get("class_preferences", {})
        
        # Red-eye flights get special treatment
        if is_red_eye:
            return class_prefs.get("red_eye_flights", "business")
        
        # Determine trip type for class selection
        if self.is_domestic_flight(origin, destination):
            if self.is_short_flight(origin, destination):
                return class_prefs.get("domestic_short", "economy")
            else:
                return class_prefs.get("domestic_long", "economy")
        else:
            if self.is_short_international_flight(origin, destination):
                return class_prefs.get("international_short", "premium_economy")
            else:
                return class_prefs.get("international_long", "business")
    
    def is_domestic_flight(self, origin: str, destination: str) -> bool:
        """Determine if flight is domestic (simplified logic)"""
        # This is a simplified implementation - in reality, you'd use airport codes
        us_airports = ["SFO", "LAX", "JFK", "LGA", "ORD", "DFW", "ATL", "DEN", "SEA", "LAS"]
        return origin in us_airports and destination in us_airports
    
    def is_short_flight(self, origin: str, destination: str) -> bool:
        """Determine if domestic flight is short (under 3 hours)"""
        # Simplified logic - in reality, you'd use actual flight times
        short_routes = [
            ("SFO", "LAX"), ("SFO", "SEA"), ("SFO", "LAS"),
            ("NYC", "BOS"), ("NYC", "DC"), ("NYC", "CHI"),
            ("LAX", "LAS"), ("LAX", "SFO"), ("LAX", "SEA")
        ]
        return (origin, destination) in short_routes or (destination, origin) in short_routes
    
    def is_short_international_flight(self, origin: str, destination: str) -> bool:
        """Determine if international flight is short (under 6 hours)"""
        # Simplified logic for short international flights
        short_international = [
            ("NYC", "LON"), ("NYC", "PAR"), ("NYC", "TOR"),
            ("MIA", "MEX"), ("LAX", "VAN"), ("SEA", "VAN")
        ]
        return (origin, destination) in short_international or (destination, origin) in short_international
    
    def get_preferences_summary(self) -> str:
        """Get a summary of current preferences"""
        prefs = self.preferences
        
        summary = f"""
Travel Preferences Summary:
========================
Traveler: {prefs.traveler_profile.get('name', 'Unknown')}
Style: {prefs.traveler_profile.get('travel_style', 'Unknown')}
Budget Level: {prefs.traveler_profile.get('budget_level', 'Unknown')}

Hotel Preferences:
- Preferred Chains: {', '.join(prefs.hotel_preferences.get('preferred_chains', [])[:3])}
- Loyalty Programs: {', '.join(prefs.hotel_preferences.get('loyalty_programs', [])[:2])}

Flight Preferences:
- Preferred Airlines: {', '.join(prefs.flight_preferences.get('preferred_airlines', [])[:3])}
- Alliances: {', '.join(prefs.flight_preferences.get('airline_alliances', [])[:2])}
- Red-eye Preference: {prefs.flight_preferences.get('red_eye_preference', 'Unknown')}

Activities:
- Adventure Level: {prefs.activity_preferences.get('adventure_level', 'Unknown')}
- Cultural Interest: {prefs.activity_preferences.get('cultural_interest', 'Unknown')}
        """
        return summary.strip()
    
    def get_loyalty_benefits(self, provider: str, service_type: str) -> Dict[str, Any]:
        """Get loyalty program benefits for a specific provider"""
        loyalty_prefs = self.preferences.loyalty_programs
        
        if service_type == "airline":
            status = loyalty_prefs.get("airline_status", {}).get(provider.lower(), "none")
        elif service_type == "hotel":
            status = loyalty_prefs.get("hotel_status", {}).get(provider.lower(), "none")
        elif service_type == "car_rental":
            status = loyalty_prefs.get("car_rental_status", {}).get(provider.lower(), "none")
        else:
            status = "none"
        
        return {
            "status": status,
            "benefits": self._get_status_benefits(service_type, status),
            "credit_cards": loyalty_prefs.get("credit_cards", [])
        }
    
    def _get_status_benefits(self, service_type: str, status: str) -> List[str]:
        """Get benefits for a specific status level"""
        benefits_map = {
            "airline": {
                "silver": ["priority_checkin", "extra_baggage"],
                "gold": ["priority_checkin", "extra_baggage", "lounge_access"],
                "platinum": ["priority_checkin", "extra_baggage", "lounge_access", "upgrades"],
                "diamond": ["priority_checkin", "extra_baggage", "lounge_access", "upgrades", "concierge"]
            },
            "hotel": {
                "silver": ["late_checkout", "wifi"],
                "gold": ["late_checkout", "wifi", "room_upgrade"],
                "platinum": ["late_checkout", "wifi", "room_upgrade", "breakfast"],
                "diamond": ["late_checkout", "wifi", "room_upgrade", "breakfast", "suite_upgrade"]
            },
            "car_rental": {
                "gold": ["fast_track", "car_upgrade"],
                "executive": ["fast_track", "car_upgrade", "concierge"],
                "preferred": ["fast_track", "car_upgrade", "concierge", "free_upgrades"]
            }
        }
        
        return benefits_map.get(service_type, {}).get(status, [])
    
    def get_technology_recommendations(self) -> Dict[str, Any]:
        """Get technology and app recommendations"""
        tech_prefs = self.preferences.technology_preferences
        
        return {
            "recommended_apps": tech_prefs.get("mobile_apps", []),
            "digital_wallet": tech_prefs.get("digital_wallet", "Apple Pay"),
            "digital_preferences": {
                "boarding_pass": tech_prefs.get("prefer_digital_boarding", True),
                "checkin": tech_prefs.get("prefer_digital_checkin", True),
                "offline_maps": tech_prefs.get("backup_offline_maps", True)
            }
        }
    
    def get_health_wellness_recommendations(self) -> Dict[str, Any]:
        """Get health and wellness recommendations"""
        health_prefs = self.preferences.health_wellness
        
        return {
            "fitness_level": health_prefs.get("fitness_requirements", "moderate"),
            "wellness_activities": health_prefs.get("wellness_activities", []),
            "dietary_restrictions": health_prefs.get("dietary_restrictions", []),
            "medication_needs": health_prefs.get("medication_needs", []),
            "vaccination_status": health_prefs.get("vaccination_preferences", "up_to_date"),
            "hotel_gym_required": health_prefs.get("prefer_hotel_gym", True)
        }
    
    def get_safety_recommendations(self) -> Dict[str, Any]:
        """Get safety and security recommendations"""
        safety_prefs = self.preferences.safety_security
        
        return {
            "safety_level": safety_prefs.get("safety_consciousness", "high"),
            "safe_neighborhoods": safety_prefs.get("prefer_safe_neighborhoods", True),
            "travel_alerts": safety_prefs.get("travel_alerts", True),
            "emergency_preparedness": safety_prefs.get("emergency_preparedness", True),
            "insurance_required": safety_prefs.get("travel_insurance_required", True),
            "backup_plans": safety_prefs.get("backup_plans", True)
        }
    
    def get_cultural_recommendations(self) -> Dict[str, Any]:
        """Get cultural and local experience recommendations"""
        cultural_prefs = self.preferences.cultural_preferences
        
        return {
            "cultural_sensitivity": cultural_prefs.get("cultural_sensitivity", "high"),
            "authentic_experiences": cultural_prefs.get("prefer_authentic_experiences", True),
            "local_interaction": cultural_prefs.get("local_interaction_level", "moderate"),
            "language_learning": cultural_prefs.get("language_learning_interest", "basic_phrases"),
            "cultural_activities": cultural_prefs.get("cultural_activities", [])
        }
    
    def get_environmental_recommendations(self) -> Dict[str, Any]:
        """Get environmental and sustainability recommendations"""
        env_prefs = self.preferences.environmental_preferences
        
        return {
            "eco_conscious": env_prefs.get("eco_conscious", True),
            "eco_hotels": env_prefs.get("prefer_eco_hotels", False),
            "carbon_offset": env_prefs.get("carbon_offset_preference", "optional"),
            "sustainable_transport": env_prefs.get("sustainable_transport", "prefer"),
            "local_sourcing": env_prefs.get("local_sourcing", "prefer")
        }
    
    def get_entertainment_recommendations(self) -> Dict[str, Any]:
        """Get entertainment and activity recommendations"""
        entertainment_prefs = self.preferences.entertainment_preferences
        
        return {
            "nightlife": entertainment_prefs.get("nightlife_interest", "moderate"),
            "cultural_events": entertainment_prefs.get("cultural_events", "high"),
            "sports_events": entertainment_prefs.get("sports_events", "low"),
            "shopping": entertainment_prefs.get("shopping_interest", "moderate"),
            "entertainment_budget": entertainment_prefs.get("entertainment_budget", "moderate")
        }
    
    def get_photography_recommendations(self) -> Dict[str, Any]:
        """Get photography and social media recommendations"""
        photo_prefs = self.preferences.photography_social
        
        return {
            "photography_interest": photo_prefs.get("photography_interest", "high"),
            "social_sharing": photo_prefs.get("social_media_sharing", "moderate"),
            "instagrammable_spots": photo_prefs.get("prefer_instagrammable_spots", True),
            "documentation_level": photo_prefs.get("documentation_level", "moderate")
        }
    
    def get_flexibility_recommendations(self) -> Dict[str, Any]:
        """Get flexibility and contingency recommendations"""
        flex_prefs = self.preferences.flexibility_preferences
        
        return {
            "date_flexibility": flex_prefs.get("date_flexibility", "moderate"),
            "destination_flexibility": flex_prefs.get("destination_flexibility", "low"),
            "accommodation_flexibility": flex_prefs.get("accommodation_flexibility", "moderate"),
            "activity_flexibility": flex_prefs.get("activity_flexibility", "high"),
            "weather_contingency": flex_prefs.get("weather_contingency", True)
        }
    
    def get_group_dynamics_recommendations(self) -> Dict[str, Any]:
        """Get group dynamics and social recommendations"""
        group_prefs = self.preferences.group_dynamics
        
        return {
            "decision_making": group_prefs.get("group_decision_making", "consensus"),
            "group_activities": group_prefs.get("prefer_group_activities", True),
            "alone_time": group_prefs.get("alone_time_needs", "moderate"),
            "group_size": group_prefs.get("group_size_preference", "small"),
            "conflict_resolution": group_prefs.get("conflict_resolution", "discussion")
        }
    
    def get_learning_recommendations(self) -> Dict[str, Any]:
        """Get learning and development recommendations"""
        learning_prefs = self.preferences.learning_development
        
        return {
            "educational_interest": learning_prefs.get("educational_interest", "high"),
            "skill_development": learning_prefs.get("skill_development", "moderate"),
            "local_learning": learning_prefs.get("local_learning", True),
            "workshops": learning_prefs.get("workshop_interest", "moderate"),
            "cultural_immersion": learning_prefs.get("cultural_immersion", "moderate")
        }
    
    def get_comfort_recommendations(self) -> Dict[str, Any]:
        """Get comfort and lifestyle recommendations"""
        comfort_prefs = self.preferences.comfort_preferences
        
        return {
            "climate_comfort": comfort_prefs.get("climate_comfort", "moderate"),
            "noise_sensitivity": comfort_prefs.get("noise_sensitivity", "low"),
            "crowd_tolerance": comfort_prefs.get("crowd_tolerance", "moderate"),
            "pace_preference": comfort_prefs.get("pace_preference", "moderate"),
            "comfort_vs_adventure": comfort_prefs.get("comfort_vs_adventure", "balanced")
        }
    
    def get_logistics_recommendations(self) -> Dict[str, Any]:
        """Get logistics and planning recommendations"""
        logistics_prefs = self.preferences.logistics_preferences
        
        return {
            "planning_style": logistics_prefs.get("planning_style", "moderate"),
            "spontaneity": logistics_prefs.get("spontaneity_level", "moderate"),
            "backup_planning": logistics_prefs.get("backup_planning", True),
            "contingency_budget": logistics_prefs.get("contingency_budget", "10%"),
            "emergency_fund": logistics_prefs.get("emergency_fund", True)
        }
    
    def get_packing_recommendations(self) -> Dict[str, Any]:
        """Get packing and preparation recommendations"""
        packing_prefs = self.preferences.packing_preferences
        
        return {
            "packing_style": packing_prefs.get("packing_style", "light"),
            "carry_on_preference": packing_prefs.get("prefer_carry_on", True),
            "essential_items": packing_prefs.get("essential_items", []),
            "climate_preparation": packing_prefs.get("climate_preparation", "layered_clothing")
        }
    
    def get_communication_recommendations(self) -> Dict[str, Any]:
        """Get communication and connectivity recommendations"""
        comm_prefs = self.preferences.communication_preferences
        
        return {
            "roaming_preference": comm_prefs.get("international_roaming", "avoid"),
            "wifi_calling": comm_prefs.get("prefer_wifi_calling", True),
            "messaging_apps": comm_prefs.get("messaging_apps", []),
            "translation_needs": comm_prefs.get("translation_needs", "moderate"),
            "emergency_contacts": comm_prefs.get("emergency_contacts", True)
        }
    
    def get_travel_insurance_recommendations(self) -> Dict[str, Any]:
        """Get travel insurance recommendations"""
        insurance_prefs = self.preferences.travel_insurance
        
        return {
            "prefer_insurance": insurance_prefs.get("prefer_travel_insurance", True),
            "provider": insurance_prefs.get("insurance_provider", "Allianz"),
            "coverage_level": insurance_prefs.get("coverage_level", "comprehensive"),
            "pre_existing_conditions": insurance_prefs.get("pre_existing_conditions", False)
        }
    
    def get_comprehensive_recommendations(self, destination: str, trip_type: str = "leisure") -> Dict[str, Any]:
        """Get comprehensive recommendations combining all preference categories"""
        return {
            "hotel": self.get_hotel_recommendations(destination, trip_type),
            "flight": self.get_flight_recommendations("", destination, "domestic_short"),
            "budget": self.get_budget_guidelines(trip_type),
            "activities": self.get_activity_recommendations(destination),
            "transportation": self.get_transportation_recommendations(trip_type),
            "technology": self.get_technology_recommendations(),
            "health_wellness": self.get_health_wellness_recommendations(),
            "safety": self.get_safety_recommendations(),
            "cultural": self.get_cultural_recommendations(),
            "environmental": self.get_environmental_recommendations(),
            "entertainment": self.get_entertainment_recommendations(),
            "photography": self.get_photography_recommendations(),
            "flexibility": self.get_flexibility_recommendations(),
            "group_dynamics": self.get_group_dynamics_recommendations(),
            "learning": self.get_learning_recommendations(),
            "comfort": self.get_comfort_recommendations(),
            "logistics": self.get_logistics_recommendations(),
            "packing": self.get_packing_recommendations(),
            "communication": self.get_communication_recommendations(),
            "insurance": self.get_travel_insurance_recommendations()
        }
    @staticmethod
    def _ensure_dict(value: Any) -> Dict[str, Any]:
        """Return the value if it's a dict, otherwise provide a safe empty dict."""
        if isinstance(value, dict):
            return value
        if isinstance(value, BaseModel):
            # Pydantic models expose a dict representation – convert to avoid attribute errors
            return value.model_dump()
        return {}

