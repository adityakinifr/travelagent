"""
Feasibility Checker for validating travel recommendations against real constraints
"""

import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pydantic import BaseModel
from preferences_manager import PreferencesManager
from real_travel_apis import RealTravelAPIs

# Load environment variables
load_dotenv()

class FeasibilityResult(BaseModel):
    """Result of feasibility checking"""
    is_feasible: bool
    feasibility_score: float  # 0.0 to 1.0
    issues: List[str]
    alternatives: List[str]
    estimated_total_cost: Optional[float] = None
    flight_available: bool = False
    hotel_available: bool = False
    within_budget: bool = False
    details: Dict[str, Any] = {}

class FeasibilityChecker:
    """Checks feasibility of travel recommendations"""
    
    def __init__(self, preferences_file: str = "travel_preferences.json"):
        self.preferences_manager = PreferencesManager(preferences_file)
        self.travel_apis = RealTravelAPIs()
        
    def check_destination_feasibility(
        self, 
        destination: str, 
        origin: str, 
        travel_dates: str,
        budget: Optional[str] = None,
        traveler_type: str = "leisure"
    ) -> FeasibilityResult:
        """Check if a destination is feasible for travel"""
        
        print(f"🔍 Checking feasibility for {destination} from {origin}")
        print(f"   📅 Travel dates: {travel_dates}")
        print(f"   💰 Budget: {budget or 'Not specified'}")
        print(f"   👥 Traveler type: {traveler_type}")
        
        issues = []
        alternatives = []
        feasibility_score = 1.0
        estimated_total_cost = 0.0
        flight_available = False
        hotel_available = False
        within_budget = True
        details = {}
        
        # Parse travel dates
        print(f"   📅 Parsing travel dates...")
        departure_date, return_date = self._parse_travel_dates(travel_dates)
        print(f"   📅 Parsed dates: {departure_date} to {return_date}")
        
        # Check flight availability and cost
        print(f"   ✈️  Checking flight availability...")
        flight_result = self._check_flight_feasibility(origin, destination, departure_date, return_date)
        if flight_result:
            flight_available = flight_result.get("available", False)
            flight_cost = flight_result.get("cost", 0)
            estimated_total_cost += flight_cost
            details["flight"] = flight_result
            
            if not flight_available:
                issues.append(f"No flights available from {origin} to {destination}")
                feasibility_score -= 0.4
            elif flight_cost > self._get_flight_budget_limit(budget, traveler_type):
                issues.append(f"Flight cost (${flight_cost}) exceeds budget")
                within_budget = False
                feasibility_score -= 0.3
        
        # Check hotel availability and cost
        print(f"   🏨 Checking hotel availability...")
        hotel_result = self._check_hotel_feasibility(destination, departure_date, return_date, traveler_type)
        if hotel_result:
            hotel_available = hotel_result.get("available", False)
            hotel_cost = hotel_result.get("cost", 0)
            estimated_total_cost += hotel_cost
            details["hotel"] = hotel_result
            
            if not hotel_available:
                issues.append(f"No suitable hotels available in {destination}")
                feasibility_score -= 0.3
            elif hotel_cost > self._get_hotel_budget_limit(budget, traveler_type):
                issues.append(f"Hotel cost (${hotel_cost}) exceeds budget")
                within_budget = False
                feasibility_score -= 0.2
        
        # Check total budget feasibility
        if budget and estimated_total_cost > self._parse_budget(budget):
            issues.append(f"Total estimated cost (${estimated_total_cost:.0f}) exceeds budget (${budget})")
            within_budget = False
            feasibility_score -= 0.2
        
        # Generate alternatives if not feasible
        if feasibility_score < 0.6:
            alternatives = self._generate_alternatives(origin, destination, travel_dates, budget, traveler_type)
        
        # Ensure feasibility score is between 0 and 1
        feasibility_score = max(0.0, min(1.0, feasibility_score))
        
        is_feasible = feasibility_score >= 0.6 and flight_available and hotel_available and within_budget
        
        # Log final results
        print(f"   📊 Final feasibility assessment:")
        print(f"      Score: {feasibility_score:.2f}")
        print(f"      Feasible: {is_feasible}")
        print(f"      Flight available: {flight_available}")
        print(f"      Hotel available: {hotel_available}")
        print(f"      Within budget: {within_budget}")
        print(f"      Estimated cost: ${estimated_total_cost:.0f}")
        if issues:
            print(f"      Issues: {', '.join(issues[:2])}")
        
        return FeasibilityResult(
            is_feasible=is_feasible,
            feasibility_score=feasibility_score,
            issues=issues,
            alternatives=alternatives,
            estimated_total_cost=estimated_total_cost,
            flight_available=flight_available,
            hotel_available=hotel_available,
            within_budget=within_budget,
            details=details
        )
    
    def _check_flight_feasibility(
        self, 
        origin: str, 
        destination: str, 
        departure_date: str, 
        return_date: str
    ) -> Optional[Dict[str, Any]]:
        """Check flight availability and cost"""
        try:
            print(f"   ✈️ Checking flights from {origin} to {destination}")
            
            # Use the real travel APIs to check flights
            flight_results = self.travel_apis.search_flights_real_api(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                return_date=return_date,
                adults=1
            )
            
            if flight_results and len(flight_results) > 0:
                # Get the cheapest flight
                cheapest_flight = min(flight_results, key=lambda x: x.price)
                
                return {
                    "available": True,
                    "cost": cheapest_flight.price,
                    "airline": cheapest_flight.airline,
                    "departure_time": cheapest_flight.departure_time,
                    "arrival_time": cheapest_flight.arrival_time,
                    "flight_duration": cheapest_flight.duration,
                    "total_flights": len(flight_results)
                }
            else:
                return {
                    "available": False,
                    "cost": 0,
                    "reason": "No flights found"
                }
                
        except Exception as e:
            print(f"   ❌ Error checking flights: {e}")
            return {
                "available": False,
                "cost": 0,
                "error": str(e)
            }
    
    def _check_hotel_feasibility(
        self, 
        destination: str, 
        departure_date: str, 
        return_date: str,
        traveler_type: str
    ) -> Optional[Dict[str, Any]]:
        """Check hotel availability and cost"""
        try:
            print(f"   🏨 Checking hotels in {destination}")
            
            # Use the real travel APIs to check hotels
            hotel_results = self.travel_apis.search_hotels_real_api(
                destination=destination,
                check_in=departure_date,
                check_out=return_date,
                adults=1
            )
            
            if hotel_results and len(hotel_results) > 0:
                # Get the cheapest suitable hotel
                cheapest_hotel = min(hotel_results, key=lambda x: x.price_per_night)
                
                # Calculate total hotel cost
                nights = self._calculate_nights(departure_date, return_date)
                total_hotel_cost = cheapest_hotel.price_per_night * nights
                
                return {
                    "available": True,
                    "cost": total_hotel_cost,
                    "price_per_night": cheapest_hotel.price_per_night,
                    "hotel_name": cheapest_hotel.name,
                    "rating": cheapest_hotel.rating,
                    "nights": nights,
                    "total_hotels": len(hotel_results)
                }
            else:
                return {
                    "available": False,
                    "cost": 0,
                    "reason": "No hotels found"
                }
                
        except Exception as e:
            print(f"   ❌ Error checking hotels: {e}")
            return {
                "available": False,
                "cost": 0,
                "error": str(e)
            }
    
    def _parse_travel_dates(self, travel_dates: str) -> Tuple[str, str]:
        """Parse travel dates into departure and return dates using smart date logic"""
        # Default to 7 days from now for departure, 10 days from now for return
        base_date = datetime.now() + timedelta(days=7)
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # Handle seasons with smart year logic
        if "summer" in travel_dates.lower():
            # Check if we're currently in summer (June-August)
            if current_month in [6, 7, 8]:
                # We're in summer, use next year
                year = current_year + 1
            else:
                # Check if summer is coming up this year
                if current_month < 6:
                    year = current_year  # Summer is coming up
                else:
                    year = current_year + 1  # Summer already passed
            departure_date = f"{year}-06-15"
            return_date = f"{year}-06-22"
            
        elif "winter" in travel_dates.lower():
            # Check if we're currently in winter (Dec, Jan, Feb)
            if current_month in [12, 1, 2]:
                # We're in winter, use next year
                year = current_year + 1
            else:
                # Check if winter is coming up this year
                if current_month < 12:
                    year = current_year  # Winter is coming up
                else:
                    year = current_year + 1  # Winter already passed
            departure_date = f"{year}-12-15"
            return_date = f"{year}-12-22"
            
        elif "spring" in travel_dates.lower():
            # Check if we're currently in spring (March-May)
            if current_month in [3, 4, 5]:
                # We're in spring, use next year
                year = current_year + 1
            else:
                # Check if spring is coming up this year
                if current_month < 3:
                    year = current_year  # Spring is coming up
                else:
                    year = current_year + 1  # Spring already passed
            departure_date = f"{year}-04-15"
            return_date = f"{year}-04-22"
            
        elif "fall" in travel_dates.lower() or "autumn" in travel_dates.lower():
            # Check if we're currently in fall (September-November)
            if current_month in [9, 10, 11]:
                # We're in fall, use next year
                year = current_year + 1
            else:
                # Check if fall is coming up this year
                if current_month < 9:
                    year = current_year  # Fall is coming up
                else:
                    year = current_year + 1  # Fall already passed
            departure_date = f"{year}-10-15"
            return_date = f"{year}-10-22"
            
        # Handle specific months
        elif "june" in travel_dates.lower():
            year = current_year + 1 if current_month >= 6 else current_year
            departure_date = f"{year}-06-15"
            return_date = f"{year}-06-22"
        elif "july" in travel_dates.lower():
            year = current_year + 1 if current_month >= 7 else current_year
            departure_date = f"{year}-07-15"
            return_date = f"{year}-07-22"
        elif "august" in travel_dates.lower():
            year = current_year + 1 if current_month >= 8 else current_year
            departure_date = f"{year}-08-15"
            return_date = f"{year}-08-22"
        elif "december" in travel_dates.lower():
            year = current_year + 1 if current_month >= 12 else current_year
            departure_date = f"{year}-12-15"
            return_date = f"{year}-12-22"
        elif "march" in travel_dates.lower():
            year = current_year + 1 if current_month >= 3 else current_year
            departure_date = f"{year}-03-15"
            return_date = f"{year}-03-22"
        elif "april" in travel_dates.lower():
            year = current_year + 1 if current_month >= 4 else current_year
            departure_date = f"{year}-04-15"
            return_date = f"{year}-04-22"
        elif "may" in travel_dates.lower():
            year = current_year + 1 if current_month >= 5 else current_year
            departure_date = f"{year}-05-15"
            return_date = f"{year}-05-22"
        elif "september" in travel_dates.lower():
            year = current_year + 1 if current_month >= 9 else current_year
            departure_date = f"{year}-09-15"
            return_date = f"{year}-09-22"
        elif "october" in travel_dates.lower():
            year = current_year + 1 if current_month >= 10 else current_year
            departure_date = f"{year}-10-15"
            return_date = f"{year}-10-22"
        elif "november" in travel_dates.lower():
            year = current_year + 1 if current_month >= 11 else current_year
            departure_date = f"{year}-11-15"
            return_date = f"{year}-11-22"
        elif "january" in travel_dates.lower():
            year = current_year + 1 if current_month >= 1 else current_year
            departure_date = f"{year}-01-15"
            return_date = f"{year}-01-22"
        elif "february" in travel_dates.lower():
            year = current_year + 1 if current_month >= 2 else current_year
            departure_date = f"{year}-02-15"
            return_date = f"{year}-02-22"
        else:
            # Default to 7 days from now
            departure_date = base_date.strftime("%Y-%m-%d")
            return_date = (base_date + timedelta(days=7)).strftime("%Y-%m-%d")
        
        return departure_date, return_date
    
    def _calculate_nights(self, departure_date: str, return_date: str) -> int:
        """Calculate number of nights between dates"""
        try:
            dep_date = datetime.strptime(departure_date, "%Y-%m-%d")
            ret_date = datetime.strptime(return_date, "%Y-%m-%d")
            return (ret_date - dep_date).days
        except:
            return 7  # Default to 7 nights
    
    def _get_flight_budget_limit(self, budget: Optional[str], traveler_type: str) -> float:
        """Get flight budget limit based on total budget and traveler type"""
        if not budget:
            return float('inf')
        
        total_budget = self._parse_budget(budget)
        
        # Allocate 40-60% of budget to flights depending on traveler type
        if traveler_type == "business":
            return total_budget * 0.6  # Business travelers can spend more on flights
        elif traveler_type == "family_with_kids":
            return total_budget * 0.4  # Families need more budget for hotels and activities
        else:
            return total_budget * 0.5  # Balanced allocation
    
    def _get_hotel_budget_limit(self, budget: Optional[str], traveler_type: str) -> float:
        """Get hotel budget limit based on total budget and traveler type"""
        if not budget:
            return float('inf')
        
        total_budget = self._parse_budget(budget)
        
        # Allocate 30-50% of budget to hotels depending on traveler type
        if traveler_type == "business":
            return total_budget * 0.4  # Business travelers need good hotels
        elif traveler_type == "family_with_kids":
            return total_budget * 0.5  # Families need more space and amenities
        else:
            return total_budget * 0.35  # Balanced allocation
    
    def _parse_budget(self, budget: str) -> float:
        """Parse budget string into float value"""
        try:
            if not budget:
                return 1000.0  # Default budget
            
            # Remove currency symbols and commas
            budget_clean = budget.replace("$", "").replace(",", "").replace(" ", "")
            
            # Handle ranges like "100-200" by taking the lower bound
            if "-" in budget_clean:
                budget_clean = budget_clean.split("-")[0]
            
            # Handle "k" for thousands
            if budget_clean.lower().endswith("k"):
                return float(budget_clean[:-1]) * 1000
            
            return float(budget_clean)
        except Exception as e:
            print(f"Error parsing budget '{budget}': {e}")
            return 1000.0  # Default budget
    
    def _generate_alternatives(
        self, 
        origin: str, 
        destination: str, 
        travel_dates: str,
        budget: Optional[str],
        traveler_type: str
    ) -> List[str]:
        """Generate alternative destinations when primary option is not feasible"""
        
        print(f"   🔄 Generating alternatives for {destination}")
        
        # Get nearby or similar destinations
        alternatives = []
        
        # Common alternative destinations based on origin
        if origin.upper() in ["SFO", "SAN FRANCISCO"]:
            alternatives = [
                "Monterey, CA", "Carmel, CA", "Napa Valley, CA", 
                "Lake Tahoe, CA", "Santa Barbara, CA", "San Diego, CA"
            ]
        elif origin.upper() in ["NYC", "NEW YORK", "JFK", "LGA"]:
            alternatives = [
                "Boston, MA", "Washington DC", "Philadelphia, PA",
                "Montreal, Canada", "Toronto, Canada", "Miami, FL"
            ]
        elif origin.upper() in ["LAX", "LOS ANGELES"]:
            alternatives = [
                "San Diego, CA", "Las Vegas, NV", "San Francisco, CA",
                "Phoenix, AZ", "Seattle, WA", "Portland, OR"
            ]
        else:
            # Generic alternatives
            alternatives = [
                "Nearby city", "Alternative destination", "Backup option"
            ]
        
        # Remove the original destination if it's in the list
        alternatives = [alt for alt in alternatives if alt.lower() != destination.lower()]
        
        return alternatives[:3]  # Return top 3 alternatives
    
    def check_multiple_destinations(
        self, 
        destinations: List[str], 
        origin: str, 
        travel_dates: str,
        budget: Optional[str] = None,
        traveler_type: str = "leisure"
    ) -> List[Tuple[str, FeasibilityResult]]:
        """Check feasibility for multiple destinations and return ranked results"""
        
        print(f"🔍 Checking feasibility for {len(destinations)} destinations")
        print(f"   📍 Destinations: {', '.join(destinations)}")
        print(f"   ✈️  Origin: {origin}")
        print(f"   📅 Dates: {travel_dates}")
        print(f"   💰 Budget: {budget or 'Not specified'}")
        print(f"   👥 Traveler type: {traveler_type}")
        
        results = []
        
        for i, destination in enumerate(destinations, 1):
            print(f"\n   🔍 [{i}/{len(destinations)}] Checking feasibility for {destination}...")
            result = self.check_destination_feasibility(
                destination=destination,
                origin=origin,
                travel_dates=travel_dates,
                budget=budget,
                traveler_type=traveler_type
            )
            print(f"   📊 {destination}: Score {result.feasibility_score:.2f}, Feasible: {result.is_feasible}")
            if result.issues:
                print(f"   ⚠️  Issues: {', '.join(result.issues[:2])}")  # Show first 2 issues
            results.append((destination, result))
        
        # Sort by feasibility score (highest first)
        results.sort(key=lambda x: x[1].feasibility_score, reverse=True)
        
        return results
    
    def get_feasible_destinations(
        self, 
        destinations: List[str], 
        origin: str, 
        travel_dates: str,
        budget: Optional[str] = None,
        traveler_type: str = "leisure",
        min_feasibility_score: float = 0.6
    ) -> List[Tuple[str, FeasibilityResult]]:
        """Get only feasible destinations that meet minimum criteria"""
        
        all_results = self.check_multiple_destinations(
            destinations, origin, travel_dates, budget, traveler_type
        )
        
        # Filter for feasible destinations
        feasible_results = [
            (dest, result) for dest, result in all_results 
            if result.is_feasible and result.feasibility_score >= min_feasibility_score
        ]
        
        return feasible_results
    
    def suggest_budget_adjustments(
        self, 
        destination: str, 
        origin: str, 
        travel_dates: str,
        current_budget: str,
        traveler_type: str = "leisure"
    ) -> Dict[str, Any]:
        """Suggest budget adjustments to make a destination feasible"""
        
        result = self.check_destination_feasibility(
            destination, origin, travel_dates, current_budget, traveler_type
        )
        
        if result.is_feasible:
            return {
                "adjustment_needed": False,
                "message": "Destination is already feasible within current budget"
            }
        
        current_budget_amount = self._parse_budget(current_budget)
        estimated_cost = result.estimated_total_cost
        
        if estimated_cost > current_budget_amount:
            increase_needed = estimated_cost - current_budget_amount
            increase_percentage = (increase_needed / current_budget_amount) * 100
            
            return {
                "adjustment_needed": True,
                "current_budget": current_budget_amount,
                "estimated_cost": estimated_cost,
                "increase_needed": increase_needed,
                "increase_percentage": increase_percentage,
                "suggested_budget": f"${estimated_cost * 1.1:.0f}",  # Add 10% buffer
                "alternatives": result.alternatives
            }
        
        return {
            "adjustment_needed": False,
            "message": "Budget is sufficient, but other constraints prevent feasibility"
        }
