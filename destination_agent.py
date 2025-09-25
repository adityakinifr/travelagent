"""
Destination Research Agent for handling specific and abstract destination requests
"""

import os
import requests
from typing import Dict, List, Optional, Union
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel
from datetime import datetime, timedelta
from preferences_manager import PreferencesManager
from feasibility_checker import FeasibilityChecker

# Load environment variables
load_dotenv()

class DestinationRequest(BaseModel):
    """Structure for destination research requests"""
    query: str
    origin_location: Optional[str] = None
    max_travel_time: Optional[str] = None
    travel_dates: Optional[str] = None
    budget: Optional[str] = None
    interests: List[str] = []
    travel_style: Optional[str] = None
    traveler_type: Optional[str] = None  # "family_with_kids", "couple", "solo", "older_adults", "group_friends", "business"
    group_size: Optional[int] = None
    age_range: Optional[str] = None  # "young_adults", "middle_aged", "seniors", "mixed_ages"
    mobility_requirements: Optional[str] = None  # "wheelchair_accessible", "limited_mobility", "active", "any"
    seasonal_preferences: Optional[str] = None  # "summer", "winter", "spring", "fall", "any"

class DestinationOption(BaseModel):
    """Structure for destination options"""
    name: str
    country: str
    region: str
    description: str
    best_time_to_visit: str
    travel_time_from_origin: Optional[str] = None
    estimated_cost: Optional[str] = None
    key_attractions: List[str] = []
    activities: List[str] = []
    climate: str
    visa_requirements: str
    language: str
    currency: str
    safety_rating: str
    why_recommended: str
    family_friendly_score: Optional[int] = None  # 1-10 scale
    kid_friendly_activities: List[str] = []
    senior_friendly_features: List[str] = []
    accessibility_features: List[str] = []
    seasonal_highlights: Dict[str, str] = {}  # season -> highlights
    crowd_levels: Optional[str] = None  # "low", "moderate", "high", "peak"
    nightlife_rating: Optional[str] = None  # "none", "limited", "moderate", "vibrant"
    romantic_appeal: Optional[str] = None  # "low", "moderate", "high"
    business_friendly: Optional[bool] = None

class DestinationResearchResult(BaseModel):
    """Structure for destination research results"""
    request_type: str  # "specific", "abstract", "multi_location"
    primary_destinations: List[DestinationOption]
    alternative_destinations: List[DestinationOption]
    travel_recommendations: str
    comparison_summary: Optional[str] = None
    user_choice_required: bool = False
    choice_prompt: Optional[str] = None

class DestinationResearchAgent:
    """Specialized agent for destination research and recommendation"""
    
    def __init__(self, model_name: str = "gpt-4o-mini", preferences_file: str = "travel_preferences.json"):
        """Initialize the destination research agent"""
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.preferences_manager = PreferencesManager(preferences_file)
        self.feasibility_checker = FeasibilityChecker(preferences_file)
    
    def search_web(self, query: str, num_results: int = 5) -> List[str]:
        """Search the web for current information about destinations"""
        if not self.serpapi_key:
            print("SerpAPI key not configured - using LLM knowledge only")
            return []
        
        try:
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "num": num_results,
                "engine": "google"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if "organic_results" in data:
                for result in data["organic_results"][:num_results]:
                    title = result.get("title", "")
                    snippet = result.get("snippet", "")
                    link = result.get("link", "")
                    results.append(f"Title: {title}\nSnippet: {snippet}\nSource: {link}")
            
            return results
            
        except Exception as e:
            print(f"Web search error: {e}")
            return []
    
    def get_current_travel_info(self, destination: str) -> str:
        """Get current travel information for a destination"""
        web_queries = [
            f"{destination} travel guide 2024",
            f"{destination} best time to visit current",
            f"{destination} travel requirements visa 2024",
            f"{destination} safety travel advisory current"
        ]
        
        web_results = []
        for query in web_queries:
            results = self.search_web(query, num_results=2)
            web_results.extend(results)
        
        return "\n\n".join(web_results) if web_results else ""
    
    def _validate_destination_constraints(self, destinations: List[DestinationOption], request: DestinationRequest) -> List[DestinationOption]:
        """Validate that destinations meet the specified constraints"""
        print(f"🔍 Validating {len(destinations)} destinations against constraints...")
        print(f"   Origin: {request.origin_location}")
        print(f"   Max travel time: {request.max_travel_time}")
        
        if not request.max_travel_time or not request.origin_location:
            print("   ⚠️ No constraints specified, returning all destinations")
            return destinations
        
        # Parse travel time constraint (e.g., "3 hours" -> 3)
        try:
            time_parts = request.max_travel_time.lower().split()
            max_hours = None
            for part in time_parts:
                if part.isdigit():
                    max_hours = int(part)
                    break
            if not max_hours:
                print("   ⚠️ Could not parse travel time, returning all destinations")
                return destinations
            print(f"   📏 Parsed max travel time: {max_hours} hours")
        except:
            print("   ⚠️ Error parsing travel time, returning all destinations")
            return destinations
        
        # Common travel time mappings for major origins
        origin = request.origin_location.upper()
        valid_destinations = []
        
        # More comprehensive invalid destination lists
        invalid_destinations_sfo = [
            'GREECE', 'HYDRA', 'EUROPE', 'FRANCE', 'ITALY', 'SPAIN', 'GERMANY', 'PORTUGAL',
            'ASIA', 'JAPAN', 'CHINA', 'KOREA', 'THAILAND', 'SINGAPORE', 'VIETNAM', 'INDIA',
            'AUSTRALIA', 'NEW ZEALAND', 'AFRICA', 'SOUTH AMERICA', 'BRAZIL', 'ARGENTINA',
            'RUSSIA', 'TURKEY', 'ISRAEL', 'EGYPT', 'MOROCCO', 'SOUTH AFRICA'
        ]
        
        invalid_destinations_nyc = [
            'EUROPE', 'FRANCE', 'ITALY', 'SPAIN', 'GERMANY', 'GREECE', 'PORTUGAL', 'NETHERLANDS',
            'ASIA', 'JAPAN', 'CHINA', 'KOREA', 'THAILAND', 'SINGAPORE', 'VIETNAM', 'INDIA',
            'AUSTRALIA', 'NEW ZEALAND', 'AFRICA', 'SOUTH AMERICA', 'BRAZIL', 'ARGENTINA',
            'RUSSIA', 'TURKEY', 'ISRAEL', 'EGYPT', 'MOROCCO', 'SOUTH AFRICA'
        ]
        
        for dest in destinations:
            dest_name = dest.name.upper()
            dest_country = dest.country.upper() if dest.country else ""
            dest_region = dest.region.upper() if dest.region else ""
            
            print(f"   🔍 Checking: {dest.name} ({dest.country}, {dest.region})")
            
            is_valid = True
            
            # Check for obviously invalid destinations based on origin
            if origin in ['SFO', 'SAN FRANCISCO', 'CALIFORNIA']:
                # Check name, country, and region
                all_dest_text = f"{dest_name} {dest_country} {dest_region}"
                
                if any(invalid in all_dest_text for invalid in invalid_destinations_sfo):
                    is_valid = False
                    print(f"   ❌ Filtered out {dest.name} - not within {request.max_travel_time} of {request.origin_location}")
                    print(f"      Matched invalid term in: {all_dest_text}")
            
            elif origin in ['NYC', 'NEW YORK', 'JFK', 'LGA']:
                # Check name, country, and region
                all_dest_text = f"{dest_name} {dest_country} {dest_region}"
                
                if any(invalid in all_dest_text for invalid in invalid_destinations_nyc):
                    is_valid = False
                    print(f"   ❌ Filtered out {dest.name} - not within {request.max_travel_time} of {request.origin_location}")
                    print(f"      Matched invalid term in: {all_dest_text}")
            
            if is_valid:
                valid_destinations.append(dest)
                print(f"   ✅ Valid: {dest.name}")
        
        print(f"   📊 Validation complete: {len(valid_destinations)}/{len(destinations)} destinations passed")
        return valid_destinations
    
    
    def analyze_request_type(self, user_request: str) -> str:
        """Analyze the type of destination request"""
        prompt = f"""
        Analyze this travel request and determine the type of destination inquiry:
        
        Request: "{user_request}"
        
        Classify as one of these types:
        1. "specific" - User mentions a specific destination (e.g., "Paris", "Tokyo", "New York")
        2. "abstract" - User describes desired characteristics (e.g., "sunny beach", "mountain destination", "cultural city")
        3. "multi_location" - User mentions multiple destinations or wants to compare options
        4. "constrained" - User has specific constraints (time, distance, budget) but flexible on destination
        
        Respond with just the type: specific, abstract, multi_location, or constrained
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip().lower()
    
    def extract_destination_parameters(self, user_request: str) -> DestinationRequest:
        """Extract structured parameters from the user request"""
        prompt = f"""
        Extract destination research parameters from this travel request:
        
        Request: "{user_request}"
        
        Extract and return a JSON object with these fields:
        {{
            "query": "The main destination query or description",
            "origin_location": "Starting location if mentioned (e.g., 'SFO', 'New York', 'London')",
            "max_travel_time": "Maximum travel time if specified (e.g., '3 hours', '5 hours')",
            "travel_dates": "Travel dates if mentioned (e.g., 'June 2024', 'summer', 'next month')",
            "budget": "Budget constraints if mentioned (e.g., '$2000', 'budget-friendly', 'luxury')",
            "interests": ["List of interests mentioned (e.g., 'beaches', 'history', 'food')"],
            "travel_style": "Travel style if mentioned (e.g., 'relaxing', 'adventure', 'cultural')",
            "traveler_type": "Type of travelers if mentioned (e.g., 'family_with_kids', 'couple', 'solo', 'older_adults', 'group_friends', 'business')",
            "group_size": "Number of people traveling if mentioned (e.g., 2, 4, 6)",
            "age_range": "Age range if mentioned (e.g., 'young_adults', 'middle_aged', 'seniors', 'mixed_ages')",
            "mobility_requirements": "Mobility needs if mentioned (e.g., 'wheelchair_accessible', 'limited_mobility', 'active', 'any')",
            "seasonal_preferences": "Season preference if mentioned (e.g., 'summer', 'winter', 'spring', 'fall', 'any')"
        }}
        
        If a field is not mentioned, use null. Be specific and accurate.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        try:
            import json
            # Clean up the response to extract JSON
            content = response.content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            params = json.loads(content)
            print(f"✅ Successfully parsed parameters: {params}")
            return DestinationRequest(**params)
        except Exception as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"   Raw response: {response.content}")
            
            # Enhanced fallback parsing with regex
            import re
            
            # Extract origin location
            origin_location = None
            origin_patterns = [
                r'from\s+([A-Z]{3})',  # "from SFO"
                r'from\s+([A-Za-z\s]+)',  # "from San Francisco"
                r'([A-Z]{3})\s+to',  # "SFO to"
                r'([A-Za-z\s]+)\s+to'  # "San Francisco to"
            ]
            
            for pattern in origin_patterns:
                match = re.search(pattern, user_request, re.IGNORECASE)
                if match:
                    origin_location = match.group(1).strip()
                    break
            
            # Extract travel time
            max_travel_time = None
            time_patterns = [
                r'within\s+(\d+\s+hours?)',  # "within 3 hours"
                r'(\d+\s+hours?)\s+from',  # "3 hours from"
                r'(\d+\s+hours?)\s+flight',  # "3 hours flight"
                r'(\d+\s+hours?)\s+drive'  # "3 hours drive"
            ]
            
            for pattern in time_patterns:
                match = re.search(pattern, user_request, re.IGNORECASE)
                if match:
                    max_travel_time = match.group(1).strip()
                    break
            
            print(f"   Fallback parsing - Origin: {origin_location}, Travel time: {max_travel_time}")
            
            # Extract traveler type and demographics
            traveler_type = None
            group_size = None
            age_range = None
            mobility_requirements = None
            seasonal_preferences = None
            
            # Traveler type patterns
            traveler_patterns = [
                (r'\b(family|families|kids|children|with kids)\b', 'family_with_kids'),
                (r'\b(couple|couples|romantic|honeymoon)\b', 'couple'),
                (r'\b(solo|alone|single traveler)\b', 'solo'),
                (r'\b(seniors|older|elderly|retired)\b', 'older_adults'),
                (r'\b(friends|group|bachelor|bachelorette)\b', 'group_friends'),
                (r'\b(business|work|conference|meeting)\b', 'business')
            ]
            
            for pattern, traveler_type_val in traveler_patterns:
                if re.search(pattern, user_request, re.IGNORECASE):
                    traveler_type = traveler_type_val
                    break
            
            # Group size patterns
            group_size_match = re.search(r'\b(\d+)\s*(people|travelers|guests|adults)\b', user_request, re.IGNORECASE)
            if group_size_match:
                group_size = int(group_size_match.group(1))
            
            # Age range patterns
            age_patterns = [
                (r'\b(young|millennials|20s|30s)\b', 'young_adults'),
                (r'\b(middle.?aged|40s|50s)\b', 'middle_aged'),
                (r'\b(seniors|older|elderly|60s|70s|80s)\b', 'seniors')
            ]
            
            for pattern, age_range_val in age_patterns:
                if re.search(pattern, user_request, re.IGNORECASE):
                    age_range = age_range_val
                    break
            
            # Mobility requirements patterns
            mobility_patterns = [
                (r'\b(wheelchair|accessible|disability)\b', 'wheelchair_accessible'),
                (r'\b(limited mobility|walking difficulties)\b', 'limited_mobility'),
                (r'\b(active|hiking|adventure|sports)\b', 'active')
            ]
            
            for pattern, mobility_val in mobility_patterns:
                if re.search(pattern, user_request, re.IGNORECASE):
                    mobility_requirements = mobility_val
                    break
            
            # Seasonal preferences patterns
            seasonal_patterns = [
                (r'\b(summer|june|july|august)\b', 'summer'),
                (r'\b(winter|december|january|february)\b', 'winter'),
                (r'\b(spring|march|april|may)\b', 'spring'),
                (r'\b(fall|autumn|september|october|november)\b', 'fall')
            ]
            
            for pattern, seasonal_val in seasonal_patterns:
                if re.search(pattern, user_request, re.IGNORECASE):
                    seasonal_preferences = seasonal_val
                    break
            
            print(f"   Enhanced fallback parsing:")
            print(f"      Traveler type: {traveler_type}")
            print(f"      Group size: {group_size}")
            print(f"      Age range: {age_range}")
            print(f"      Mobility: {mobility_requirements}")
            print(f"      Seasonal: {seasonal_preferences}")
            
            return DestinationRequest(
                query=user_request,
                origin_location=origin_location,
                max_travel_time=max_travel_time,
                travel_dates=None,
                budget=None,
                interests=[],
                travel_style=None,
                traveler_type=traveler_type,
                group_size=group_size,
                age_range=age_range,
                mobility_requirements=mobility_requirements,
                seasonal_preferences=seasonal_preferences
            )
    
    def research_specific_destination(self, request: DestinationRequest) -> DestinationResearchResult:
        """Research a specific destination mentioned by the user"""
        
        # Get current web information
        current_info = self.get_current_travel_info(request.query)
        
        prompt = f"""
        Research the destination: {request.query}
        
        Use your knowledge and the current information provided below to give comprehensive details about this destination.
        
        Current Web Information:
        {current_info if current_info else "No current web information available - rely on your knowledge"}
        
        Provide detailed information about:
        - Best time to visit (consider current year 2024)
        - Key attractions and activities
        - Climate and weather patterns
        - Visa requirements and entry procedures
        - Language and currency
        - Safety considerations and travel advisories
        - Estimated costs for different budget levels
        - Local transportation options
        - Cultural highlights and experiences
        - Why it's recommended for travel
        
        If origin_location is provided ({request.origin_location}), include travel time and transportation options.
        If budget is specified ({request.budget}), tailor recommendations accordingly.
        If interests are mentioned ({request.interests}), focus on relevant attractions and activities.
        
        Provide a comprehensive, up-to-date destination profile based on your knowledge and current information.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        # Create structured destination data from LLM response
        destination = self._create_destination_from_llm_response(response.content, request.query)
        
        # For specific destinations, usually no choice needed unless multiple locations found
        all_destinations = [destination]
        
        return DestinationResearchResult(
            request_type="specific",
            primary_destinations=[destination],
            alternative_destinations=[],
            travel_recommendations=response.content,
            user_choice_required=len(all_destinations) > 1
        )
    
    def research_abstract_destination(self, request: DestinationRequest) -> DestinationResearchResult:
        """Research destinations based on abstract criteria"""
        
        # Search for current information about destinations matching criteria
        search_query = f"{request.query} destinations {request.origin_location or ''} {request.max_travel_time or ''}"
        current_info = self.search_web(search_query, num_results=3)
        
        prompt = f"""
        Find destinations that match these criteria:
        
        Query: {request.query}
        Origin: {request.origin_location or 'Not specified'}
        Max travel time: {request.max_travel_time or 'Not specified'}
        Budget: {request.budget or 'Not specified'}
        Interests: {request.interests or 'Not specified'}
        Travel style: {request.travel_style or 'Not specified'}
        Traveler type: {request.traveler_type or 'Not specified'}
        Group size: {request.group_size or 'Not specified'}
        Age range: {request.age_range or 'Not specified'}
        Mobility requirements: {request.mobility_requirements or 'Not specified'}
        Seasonal preferences: {request.seasonal_preferences or 'Not specified'}
        Travel dates: {request.travel_dates or 'Not specified'}
        
        Current Web Information:
        {chr(10).join(current_info) if current_info else "No current web information available - rely on your knowledge"}
        
        IMPORTANT CONSTRAINTS:
        - If a maximum travel time is specified ({request.max_travel_time}), ONLY recommend destinations that are actually within that travel time from the origin ({request.origin_location})
        - For example, if origin is SFO and max travel time is 3 hours, destinations like Greece, Europe, or Asia are NOT acceptable
        - Only recommend destinations that are realistically reachable within the specified time constraint
        - If no destinations meet the time constraint, say so clearly
        
        TRAVELER-SPECIFIC CONSIDERATIONS:
        - Consider the traveler type ({request.traveler_type}) when ranking destinations
        - For families with kids: prioritize family-friendly activities, safety, and kid-appropriate attractions
        - For couples: consider romantic appeal, adult-oriented activities, and intimate settings
        - For solo travelers: focus on safety, social opportunities, and solo-friendly activities
        - For older adults: consider accessibility, comfort, and less physically demanding activities
        - For groups of friends: look for social activities, nightlife, and group-friendly accommodations
        - For business travelers: prioritize convenience, business facilities, and professional amenities
        
        PREFERENCES-BASED CONSIDERATIONS:
        - Hotel preferences: Consider preferred hotel chains and loyalty programs
        - Flight preferences: Consider airline alliances, class preferences, and red-eye preferences
        - Budget preferences: Align recommendations with budget level and spending patterns
        - Activity preferences: Match outdoor/indoor activities and adventure level
        - Cultural preferences: Consider cultural sensitivity and authentic experiences
        - Safety preferences: Prioritize safety-conscious recommendations
        - Technology preferences: Consider digital-friendly destinations and connectivity
        - Environmental preferences: Factor in eco-conscious and sustainable options
        
        SEASONAL CONSIDERATIONS:
        - Consider the time of year ({request.seasonal_preferences or request.travel_dates}) when ranking destinations
        - Factor in weather conditions, crowd levels, and seasonal activities
        - Adjust recommendations based on peak/off-peak seasons
        - Consider seasonal pricing and availability
        
        Use your knowledge and current information to provide 3-5 destination recommendations that match ALL criteria.
        For each destination, include:
        - Name and location
        - Why it matches the criteria (especially for the specific traveler type)
        - Best time to visit (consider current year 2024 and seasonal factors)
        - Key attractions and activities (tailored to traveler type)
        - EXACT travel time from origin (if specified) - be accurate
        - Estimated costs for different budget levels
        - Climate and weather (consider seasonal variations)
        - Safety considerations (especially important for families and solo travelers)
        - Family-friendliness score (1-10) if applicable
        - Accessibility features if mobility requirements are specified
        - Seasonal highlights and crowd levels
        - Unique selling points for the specific traveler type
        
        Rank them by how well they match the criteria, considering both the basic requirements AND the traveler demographics and seasonal factors.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        # Create structured destinations from LLM response
        destinations = self._create_multiple_destinations_from_llm(response.content)
        
        # Validate destinations against constraints
        validated_destinations = self._validate_destination_constraints(destinations, request)
        
        # For abstract requests, always require user choice if multiple options
        all_destinations = validated_destinations
        
        return DestinationResearchResult(
            request_type="abstract",
            primary_destinations=validated_destinations[:3],  # Top 3
            alternative_destinations=validated_destinations[3:],  # Rest as alternatives
            travel_recommendations=response.content,
            user_choice_required=len(all_destinations) > 1
        )
    
    def research_multi_location(self, request: DestinationRequest) -> DestinationResearchResult:
        """Research multiple destinations or provide comparisons"""
        
        # Get current information for comparison
        current_info = self.get_current_travel_info(request.query)
        
        prompt = f"""
        Analyze this multi-location travel request: {request.query}
        
        Current Web Information:
        {current_info if current_info else "No current web information available - rely on your knowledge"}
        
        If multiple specific destinations are mentioned, provide detailed comparison using current information.
        If the user wants to choose between options, provide pros/cons for each.
        
        For each destination, include:
        - Overview and highlights
        - Best time to visit (consider current year 2024)
        - Key attractions and activities
        - Travel logistics (if origin specified)
        - Costs and budget considerations
        - Safety and current travel conditions
        - Unique selling points
        - Current travel requirements and advisories
        
        Provide a comprehensive comparison summary highlighting differences, current conditions, and recommendations.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        destinations = self._create_multiple_destinations_from_llm(response.content)
        
        # For multi-location requests, always require user choice
        all_destinations = destinations
        
        return DestinationResearchResult(
            request_type="multi_location",
            primary_destinations=destinations,
            alternative_destinations=[],
            travel_recommendations=response.content,
            comparison_summary=self._extract_comparison_summary(response.content),
            user_choice_required=len(all_destinations) > 1
        )
    
    def research_constrained_destination(self, request: DestinationRequest) -> DestinationResearchResult:
        """Research destinations with specific constraints"""
        
        # Search for destinations meeting specific constraints
        search_query = f"destinations within {request.max_travel_time} of {request.origin_location} {request.interests}"
        current_info = self.search_web(search_query, num_results=3)
        
        prompt = f"""
        Find destinations that meet these specific constraints:
        
        Origin: {request.origin_location}
        Max travel time: {request.max_travel_time}
        Budget: {request.budget or 'Flexible'}
        Interests: {request.interests or 'General travel'}
        Travel style: {request.travel_style or 'Not specified'}
        
        Current Web Information:
        {chr(10).join(current_info) if current_info else "No current web information available - rely on your knowledge"}
        
        Focus on destinations that are:
        1. Within the specified travel time from origin
        2. Match the budget constraints
        3. Align with interests and travel style
        4. Currently accessible and safe to visit
        
        Use your knowledge and current information to provide 3-5 options ranked by how well they meet the constraints.
        Include:
        - Exact travel time from origin
        - Current costs and budget considerations
        - Why each destination fits the criteria
        - Current travel conditions and requirements
        - Best time to visit considering constraints
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        destinations = self._create_multiple_destinations_from_llm(response.content)
        
        # Validate destinations against constraints
        validated_destinations = self._validate_destination_constraints(destinations, request)
        
        # For constrained requests, require user choice if multiple options
        all_destinations = validated_destinations
        
        return DestinationResearchResult(
            request_type="constrained",
            primary_destinations=validated_destinations[:3],
            alternative_destinations=validated_destinations[3:],
            travel_recommendations=response.content,
            user_choice_required=len(all_destinations) > 1
        )
    
    def research_destination(self, user_request: str) -> DestinationResearchResult:
        """Main method to research destinations based on user request"""
        print(f"🔍 Starting destination research for: {user_request}")
        
        # Analyze request type
        request_type = self.analyze_request_type(user_request)
        print(f"   📋 Request type: {request_type}")
        
        # Extract parameters
        request_params = self.extract_destination_parameters(user_request)
        print(f"   📊 Extracted parameters:")
        print(f"      Query: {request_params.query}")
        print(f"      Origin: {request_params.origin_location}")
        print(f"      Max travel time: {request_params.max_travel_time}")
        print(f"      Budget: {request_params.budget}")
        print(f"      Interests: {request_params.interests}")
        print(f"      Traveler type: {request_params.traveler_type}")
        print(f"      Group size: {request_params.group_size}")
        print(f"      Age range: {request_params.age_range}")
        print(f"      Mobility: {request_params.mobility_requirements}")
        print(f"      Seasonal: {request_params.seasonal_preferences}")
        print(f"      Travel dates: {request_params.travel_dates}")
        
        # Route to appropriate research method
        if request_type == "specific":
            return self.research_specific_destination(request_params)
        elif request_type == "abstract":
            return self.research_abstract_destination(request_params)
        elif request_type == "multi_location":
            return self.research_multi_location(request_params)
        elif request_type == "constrained":
            return self.research_constrained_destination(request_params)
        else:
            # Default to abstract research
            return self.research_abstract_destination(request_params)
    
    def _create_destination_from_llm_response(self, response: str, destination_name: str) -> DestinationOption:
        """Create structured destination data from LLM response"""
        
        # Use LLM to extract structured information
        extraction_prompt = f"""
        Extract structured information from this destination research response:
        
        Destination: {destination_name}
        Response: {response}
        
        Extract and return a JSON object with these fields:
        {{
            "name": "{destination_name}",
            "country": "Country name",
            "region": "Region/state/province",
            "description": "Brief description (max 200 chars)",
            "best_time_to_visit": "Best time to visit",
            "key_attractions": ["List of top 3-5 attractions"],
            "activities": ["List of top 3-5 activities"],
            "climate": "Climate description",
            "visa_requirements": "Visa requirements",
            "language": "Primary language",
            "currency": "Local currency",
            "safety_rating": "Safety rating/considerations",
            "why_recommended": "Why this destination is recommended"
        }}
        
        Base the information on the response content. If information is not available, use reasonable defaults.
        """
        
        try:
            extraction_response = self.llm.invoke([HumanMessage(content=extraction_prompt)])
            import json
            data = json.loads(extraction_response.content)
            return DestinationOption(**data)
        except:
            # Fallback to basic parsing
            return DestinationOption(
                name=destination_name,
                country="Unknown",
                region="Unknown",
                description=response[:200] + "..." if len(response) > 200 else response,
                best_time_to_visit="Year-round",
                key_attractions=["Various attractions"],
                activities=["Various activities"],
                climate="Varies",
                visa_requirements="Check with embassy",
                language="Local language",
                currency="Local currency",
                safety_rating="Good",
                why_recommended="See description"
            )
    
    def _create_multiple_destinations_from_llm(self, response: str) -> List[DestinationOption]:
        """Create multiple destinations from LLM response using structured extraction"""
        
        # Use LLM to extract multiple destinations
        extraction_prompt = f"""
        Extract multiple destinations from this research response:
        
        Response: {response}
        
        Return a JSON array of destination objects. Each object should have these fields:
        {{
            "name": "Destination name",
            "country": "Country name",
            "region": "Region/state/province",
            "description": "Brief description (max 150 chars)",
            "best_time_to_visit": "Best time to visit",
            "key_attractions": ["List of top 3 attractions"],
            "activities": ["List of top 3 activities"],
            "climate": "Climate description",
            "visa_requirements": "Visa requirements",
            "language": "Primary language",
            "currency": "Local currency",
            "safety_rating": "Safety rating/considerations",
            "why_recommended": "Why this destination is recommended",
            "family_friendly_score": "Family-friendliness score (1-10, null if not applicable)",
            "kid_friendly_activities": ["List of kid-friendly activities"],
            "senior_friendly_features": ["List of senior-friendly features"],
            "accessibility_features": ["List of accessibility features"],
            "seasonal_highlights": {{"summer": "Summer highlights", "winter": "Winter highlights", "spring": "Spring highlights", "fall": "Fall highlights"}},
            "crowd_levels": "Crowd levels (low/moderate/high/peak)",
            "nightlife_rating": "Nightlife rating (none/limited/moderate/vibrant)",
            "romantic_appeal": "Romantic appeal (low/moderate/high)",
            "business_friendly": "Business-friendly (true/false/null)"
        }}
        
        Extract all destinations mentioned in the response. If information is not available for a field, use reasonable defaults.
        Return as a JSON array.
        """
        
        try:
            extraction_response = self.llm.invoke([HumanMessage(content=extraction_prompt)])
            import json
            
            # Clean up the response to extract JSON
            content = extraction_response.content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            destinations_data = json.loads(content)
            destinations = [DestinationOption(**dest) for dest in destinations_data]
            print(f"✅ Successfully extracted {len(destinations)} destinations from LLM response")
            return destinations[:5]  # Limit to 5 destinations
        except Exception as e:
            print(f"❌ Destination extraction failed: {e}")
            print(f"   Raw extraction response: {extraction_response.content if 'extraction_response' in locals() else 'No response'}")
            
            # Enhanced fallback parsing using regex to find destination names
            import re
            destinations = []
            
            # Look for patterns like "1. **Destination Name**" or "### 1. **Destination Name**"
            destination_patterns = [
                r'\d+\.\s*\*\*([^*]+)\*\*',  # "1. **Monterey, CA**"
                r'###\s*\d+\.\s*\*\*([^*]+)\*\*',  # "### 1. **Monterey, CA**"
                r'\*\*([^*]+)\*\*',  # "**Monterey, CA**"
                r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2})',  # "Monterey, CA"
            ]
            
            for pattern in destination_patterns:
                matches = re.findall(pattern, response, re.MULTILINE)
                for match in matches:
                    dest_name = match.strip()
                    if dest_name and len(dest_name) > 2 and dest_name not in [d.name for d in destinations]:
                        destinations.append(DestinationOption(
                            name=dest_name,
                            country="Unknown",
                            region="Unknown",
                            description="See full response",
                            best_time_to_visit="Year-round",
                            key_attractions=[],
                            activities=[],
                            climate="Varies",
                            visa_requirements="Check with embassy",
                            language="Local language",
                            currency="Local currency",
                            safety_rating="Good",
                            why_recommended="See full response"
                        ))
            
            print(f"   Fallback parsing found {len(destinations)} destinations: {[d.name for d in destinations]}")
            return destinations[:5]  # Limit to 5 destinations
    
    def _extract_comparison_summary(self, response: str) -> str:
        """Extract comparison summary from response"""
        # Look for comparison keywords and extract relevant section
        if "comparison" in response.lower() or "compare" in response.lower():
            return "See detailed comparison in travel recommendations"
        return "Multiple destinations analyzed - see individual recommendations"
    
    def research_destination_with_feasibility(
        self, 
        user_request: str, 
        check_feasibility: bool = True,
        min_feasibility_score: float = 0.6
    ) -> DestinationResearchResult:
        """Research destinations with feasibility checking and backtracking"""
        
        print(f"🔍 Starting destination research with feasibility checking: {user_request}")
        
        # First, do the normal destination research
        initial_result = self.research_destination(user_request)
        
        if not check_feasibility:
            return initial_result
        
        # Extract parameters for feasibility checking
        request_params = self.extract_destination_parameters(user_request)
        
        # Check feasibility for all primary destinations
        if initial_result.primary_destinations:
            print(f"\n🔍 Checking feasibility for {len(initial_result.primary_destinations)} destinations...")
            
            destination_names = [dest.name for dest in initial_result.primary_destinations]
            
            feasibility_results = self.feasibility_checker.check_multiple_destinations(
                destinations=destination_names,
                origin=request_params.origin_location or "Unknown",
                travel_dates=request_params.travel_dates or "summer",
                budget=request_params.budget,
                traveler_type=request_params.traveler_type or "leisure"
            )
            
            # Filter for feasible destinations
            feasible_destinations = []
            infeasible_destinations = []
            
            for dest_name, feasibility_result in feasibility_results:
                if feasibility_result.is_feasible and feasibility_result.feasibility_score >= min_feasibility_score:
                    # Find the original destination object
                    original_dest = next((d for d in initial_result.primary_destinations if d.name == dest_name), None)
                    if original_dest:
                        # Add feasibility information to the destination
                        original_dest.estimated_cost = f"${feasibility_result.estimated_total_cost:.0f}"
                        original_dest.travel_time_from_origin = feasibility_result.details.get("flight", {}).get("flight_duration", "Unknown")
                        feasible_destinations.append(original_dest)
                else:
                    infeasible_destinations.append((dest_name, feasibility_result))
            
            # If we have feasible destinations, use them
            if feasible_destinations:
                print(f"✅ Found {len(feasible_destinations)} feasible destinations")
                
                # Update the result with feasible destinations
                initial_result.primary_destinations = feasible_destinations
                initial_result.alternative_destinations = initial_result.alternative_destinations + [
                    dest for dest in initial_result.primary_destinations 
                    if dest not in feasible_destinations
                ]
                
                # Add feasibility information to the recommendations
                feasibility_summary = self._create_feasibility_summary(feasible_destinations, infeasible_destinations)
                initial_result.travel_recommendations += f"\n\n{feasibility_summary}"
                
            else:
                print(f"❌ No feasible destinations found, generating alternatives...")
                
                # Generate alternative destinations
                alternative_result = self._generate_alternative_destinations(
                    user_request, request_params, infeasible_destinations
                )
                
                if alternative_result:
                    return alternative_result
                else:
                    # If no alternatives work, return the original result with feasibility warnings
                    feasibility_warnings = self._create_feasibility_warnings(infeasible_destinations)
                    initial_result.travel_recommendations += f"\n\n{feasibility_warnings}"
        
        return initial_result
    
    def _create_feasibility_summary(
        self, 
        feasible_destinations: List[DestinationOption], 
        infeasible_destinations: List[Tuple[str, Any]]
    ) -> str:
        """Create a summary of feasibility results"""
        
        summary = "## Feasibility Analysis\n\n"
        
        if feasible_destinations:
            summary += "### ✅ Feasible Destinations:\n"
            for dest in feasible_destinations:
                summary += f"- **{dest.name}**: Estimated cost {dest.estimated_cost}, Travel time {dest.travel_time_from_origin}\n"
        
        if infeasible_destinations:
            summary += "\n### ⚠️ Destinations with Issues:\n"
            for dest_name, feasibility_result in infeasible_destinations:
                summary += f"- **{dest_name}**: {', '.join(feasibility_result.issues)}\n"
        
        return summary
    
    def _create_feasibility_warnings(self, infeasible_destinations: List[Tuple[str, Any]]) -> str:
        """Create warnings for infeasible destinations"""
        
        warnings = "## ⚠️ Feasibility Warnings\n\n"
        warnings += "The following destinations have feasibility issues:\n\n"
        
        for dest_name, feasibility_result in infeasible_destinations:
            warnings += f"### {dest_name}\n"
            warnings += f"- **Feasibility Score**: {feasibility_result.feasibility_score:.1f}/1.0\n"
            warnings += f"- **Issues**: {', '.join(feasibility_result.issues)}\n"
            
            if feasibility_result.alternatives:
                warnings += f"- **Suggested Alternatives**: {', '.join(feasibility_result.alternatives)}\n"
            
            warnings += "\n"
        
        return warnings
    
    def _generate_alternative_destinations(
        self, 
        user_request: str, 
        request_params: DestinationRequest,
        infeasible_destinations: List[Tuple[str, Any]]
    ) -> Optional[DestinationResearchResult]:
        """Generate alternative destinations when primary options are not feasible"""
        
        print("🔄 Generating alternative destinations...")
        
        # Collect all alternatives from infeasible destinations
        all_alternatives = []
        for _, feasibility_result in infeasible_destinations:
            all_alternatives.extend(feasibility_result.alternatives)
        
        # Remove duplicates and limit to top 5
        unique_alternatives = list(dict.fromkeys(all_alternatives))[:5]
        
        if not unique_alternatives:
            return None
        
        # Create a new request for alternatives
        alternative_request = f"Find alternative destinations similar to: {request_params.query}"
        if request_params.origin_location:
            alternative_request += f" within reasonable distance from {request_params.origin_location}"
        if request_params.max_travel_time:
            alternative_request += f" within {request_params.max_travel_time}"
        if request_params.budget:
            alternative_request += f" with budget around {request_params.budget}"
        
        # Research alternatives
        alternative_result = self.research_destination(alternative_request)
        
        if alternative_result.primary_destinations:
            # Add a note about why these are alternatives
            alternative_result.travel_recommendations = (
                "## Alternative Destinations\n\n"
                "The originally suggested destinations had feasibility issues. "
                "Here are alternative options that should work better:\n\n" +
                alternative_result.travel_recommendations
            )
            
            return alternative_result
        
        return None
