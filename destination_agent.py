"""
Destination Research Agent for handling specific and abstract destination requests
"""

import os
import requests
from typing import Dict, List, Optional, Union, Tuple, Any, Callable
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel
from datetime import datetime, timedelta
import re
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
    seasonal_highlights: Dict[str, Optional[str]] = {}  # season -> highlights
    crowd_levels: Optional[str] = None  # "low", "moderate", "high", "peak"
    nightlife_rating: Optional[str] = None  # "none", "limited", "moderate", "vibrant"
    romantic_appeal: Optional[str] = None  # "low", "moderate", "high"
    image_url: Optional[str] = None  # Main destination image
    image_urls: List[str] = []  # Additional images
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
    date_required: bool = False
    budget_required: bool = False
    origin_required: bool = False

class DestinationResearchAgent:
    """Specialized agent for destination research and recommendation"""
    
    def __init__(self, model_name: str = "gpt-4o-mini", preferences_file: str = "travel_preferences.json", mock_mode: bool = False):
        """Initialize the destination research agent"""
        self.mock_mode = mock_mode
        
        if not mock_mode:
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=0.3,
                api_key=os.getenv("OPENAI_API_KEY")
            )
        else:
            self.llm = None
            from mock_data import mock_data
            self.mock_data = mock_data
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.preferences_manager = PreferencesManager(preferences_file)
        self.feasibility_checker = FeasibilityChecker(preferences_file, mock_mode=mock_mode)
    
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
    
    def search_and_order_destinations(self, request: DestinationRequest) -> List[Dict[str, any]]:
        """Perform comprehensive web search and order results by criteria"""
        print(f"🔍 Performing comprehensive web search for destination research...")
        
        # Define search queries based on request type and criteria
        search_queries = self._generate_search_queries(request)
        
        all_results = []
        
        # Perform multiple targeted searches
        for query_info in search_queries:
            query = query_info["query"]
            criteria = query_info["criteria"]
            weight = query_info["weight"]
            
            print(f"   🔎 Searching: {query}")
            web_results = self.search_web(query, num_results=3)
            
            # Process and score each result
            for result in web_results:
                scored_result = self._score_result_by_criteria(result, request, criteria, weight)
                if scored_result:
                    all_results.append(scored_result)
        
        # Remove duplicates and order by score
        unique_results = self._deduplicate_results(all_results)
        ordered_results = sorted(unique_results, key=lambda x: x["score"], reverse=True)
        
        print(f"   📊 Found {len(ordered_results)} unique destinations from web search")
        return ordered_results[:10]  # Return top 10 results
    
    def _generate_search_queries(self, request: DestinationRequest) -> List[Dict[str, any]]:
        """Generate targeted search queries based on request criteria"""
        queries = []
        
        # Base query for general destination search
        base_query = f"{request.query} travel destinations"
        if request.origin_location:
            base_query += f" from {request.origin_location}"
        if request.max_travel_time:
            base_query += f" within {request.max_travel_time}"
        
        queries.append({
            "query": base_query,
            "criteria": ["general", "accessibility"],
            "weight": 1.0
        })
        
        # Budget-specific queries
        if request.budget:
            budget_query = f"{request.query} {request.budget} budget travel"
            if request.origin_location:
                budget_query += f" from {request.origin_location}"
            queries.append({
                "query": budget_query,
                "criteria": ["budget", "cost"],
                "weight": 1.2
            })
        
        # Interest-specific queries
        if request.interests:
            for interest in request.interests:
                interest_query = f"{request.query} {interest} destinations"
                if request.origin_location:
                    interest_query += f" from {request.origin_location}"
                queries.append({
                    "query": interest_query,
                    "criteria": ["interests", interest],
                    "weight": 1.1
                })
        
        # Traveler type specific queries
        if request.traveler_type:
            traveler_query = f"{request.query} {request.traveler_type} travel destinations"
            if request.origin_location:
                traveler_query += f" from {request.origin_location}"
            queries.append({
                "query": traveler_query,
                "criteria": ["traveler_type", request.traveler_type],
                "weight": 1.3
            })
        
        # Seasonal queries
        if request.seasonal_preferences or request.travel_dates:
            season = request.seasonal_preferences or request.travel_dates
            seasonal_query = f"{request.query} {season} travel destinations"
            if request.origin_location:
                seasonal_query += f" from {request.origin_location}"
            queries.append({
                "query": seasonal_query,
                "criteria": ["seasonal", "timing"],
                "weight": 1.1
            })
        
        # Time constraint queries
        if request.max_travel_time and request.origin_location:
            time_query = f"destinations within {request.max_travel_time} of {request.origin_location}"
            queries.append({
                "query": time_query,
                "criteria": ["travel_time", "distance"],
                "weight": 1.4
            })
        
        return queries
    
    def _score_result_by_criteria(self, result: str, request: DestinationRequest, criteria: List[str], weight: float) -> Optional[Dict[str, any]]:
        """Score a web search result based on how well it matches the criteria"""
        try:
            # Extract destination name from result
            destination_name = self._extract_destination_name(result)
            if not destination_name:
                return None
            
            score = 0.0
            score_breakdown = {}
            
            # Score based on criteria
            for criterion in criteria:
                criterion_score = self._calculate_criterion_score(result, request, criterion)
                score_breakdown[criterion] = criterion_score
                score += criterion_score
            
            # Apply weight
            score *= weight
            
            return {
                "destination_name": destination_name,
                "result": result,
                "score": score,
                "score_breakdown": score_breakdown,
                "criteria": criteria,
                "weight": weight
            }
            
        except Exception as e:
            print(f"Error scoring result: {e}")
            return None
    
    def _extract_destination_name(self, result: str) -> Optional[str]:
        """Extract destination name from web search result"""
        # Use LLM to extract destination name
        prompt = f"""
        Extract the main destination name from this web search result:
        
        {result}
        
        Return only the destination name (e.g., "Paris", "Tokyo", "Barcelona"). 
        If no clear destination is mentioned, return "None".
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            destination = response.content.strip()
            return destination if destination != "None" else None
        except:
            return None
    
    def _calculate_criterion_score(self, result: str, request: DestinationRequest, criterion: str) -> float:
        """Calculate score for a specific criterion"""
        result_lower = result.lower()
        
        if criterion == "general":
            return 0.5  # Base score for general relevance
        
        elif criterion == "budget":
            if request.budget:
                budget_lower = request.budget.lower()
                if "budget" in budget_lower and ("budget" in result_lower or "cheap" in result_lower or "affordable" in result_lower):
                    return 1.0
                elif "luxury" in budget_lower and ("luxury" in result_lower or "expensive" in result_lower or "premium" in result_lower):
                    return 1.0
                elif "$" in request.budget and ("$" in result or "cost" in result_lower or "price" in result_lower):
                    return 0.8
            return 0.3
        
        elif criterion == "interests":
            if request.interests:
                for interest in request.interests:
                    if interest.lower() in result_lower:
                        return 1.0
            return 0.3
        
        elif criterion == "traveler_type":
            if request.traveler_type:
                traveler_lower = request.traveler_type.lower()
                if traveler_lower in result_lower:
                    return 1.0
                elif "family" in traveler_lower and ("family" in result_lower or "kids" in result_lower or "children" in result_lower):
                    return 0.9
                elif "solo" in traveler_lower and ("solo" in result_lower or "single" in result_lower or "backpacker" in result_lower):
                    return 0.9
            return 0.3
        
        elif criterion == "seasonal":
            if request.seasonal_preferences or request.travel_dates:
                season = (request.seasonal_preferences or request.travel_dates).lower()
                if season in result_lower:
                    return 1.0
                elif "summer" in season and ("summer" in result_lower or "warm" in result_lower):
                    return 0.8
                elif "winter" in season and ("winter" in result_lower or "snow" in result_lower or "cold" in result_lower):
                    return 0.8
            return 0.3
        
        elif criterion == "travel_time":
            if request.max_travel_time and request.origin_location:
                if "hour" in result_lower or "flight" in result_lower or "distance" in result_lower:
                    return 0.8
            return 0.3
        
        elif criterion == "accessibility":
            if request.mobility_requirements:
                if "accessible" in result_lower or "wheelchair" in result_lower or "mobility" in result_lower:
                    return 1.0
            return 0.5
        
        return 0.3  # Default score
    
    def _deduplicate_results(self, results: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """Remove duplicate destinations and combine scores"""
        destination_map = {}
        
        for result in results:
            dest_name = result["destination_name"]
            if dest_name in destination_map:
                # Combine scores for duplicate destinations
                existing = destination_map[dest_name]
                existing["score"] = max(existing["score"], result["score"])
                existing["score_breakdown"].update(result["score_breakdown"])
            else:
                destination_map[dest_name] = result
        
        return list(destination_map.values())
    
    def _search_destination_images(self, destination_name: str, country: str = None) -> Dict[str, str]:
        """Search for destination images using web search"""
        try:
            # Create search query for destination images
            search_query = f"{destination_name} {country or ''} travel destination photos".strip()
            print(f"   📸 Searching for images: {search_query}")
            
            # Use SerpAPI for image search
            serpapi_key = os.getenv('SERPAPI_API_KEY')
            if not serpapi_key:
                print("   ⚠️  SERPAPI_API_KEY not found, using LLM fallback for images")
                return self._llm_image_lookup(destination_name, country)
            
            params = {
                'q': search_query,
                'api_key': serpapi_key,
                'tbm': 'isch',  # Image search
                'num': 5
            }
            
            response = requests.get('https://serpapi.com/search', params=params)
            if response.status_code == 200:
                data = response.json()
                images = data.get('images_results', [])
                
                if images:
                    # Get the first few high-quality images
                    image_urls = []
                    for img in images[:3]:  # Get top 3 images
                        if img.get('original'):
                            image_urls.append(img['original'])
                        elif img.get('link'):
                            image_urls.append(img['link'])
                    
                    if image_urls:
                        return {
                            "primary": image_urls[0],
                            "additional": image_urls[1:] if len(image_urls) > 1 else []
                        }
            
            print(f"   ⚠️  No images found for {destination_name}")
            return self._llm_image_lookup(destination_name, country)
            
        except Exception as e:
            print(f"   ❌ Error searching for images: {e}")
            return self._llm_image_lookup(destination_name, country)
    
    def _llm_image_lookup(self, destination_name: str, country: str = None) -> Dict[str, str]:
        """Use LLM to suggest image search terms when web search is not available"""
        try:
            prompt = f"""
            Suggest image search terms for this destination: {destination_name}, {country or ''}
            
            Return a JSON object with search terms that would help find good travel photos:
            {{
                "search_terms": ["term1", "term2", "term3"],
                "description": "Brief description of what images to look for"
            }}
            
            Focus on:
            - Famous landmarks or attractions
            - Beautiful scenery or landscapes
            - Cultural highlights
            - Popular tourist spots
            
            Return only the JSON, no additional text.
            """
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Parse the JSON response
            import json
            import re
            
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                print(f"   🧠 LLM suggested image search terms: {result.get('search_terms', [])}")
                return {
                    "primary": None,  # No actual image URL
                    "additional": [],
                    "search_terms": result.get('search_terms', []),
                    "description": result.get('description', '')
                }
            else:
                return {"primary": None, "additional": []}
                
        except Exception as e:
            print(f"   ❌ Error in LLM image lookup: {e}")
            return {"primary": None, "additional": []}

    def _create_web_search_context(self, web_search_results: List[Dict[str, any]]) -> str:
        """Create a formatted context from web search results"""
        if not web_search_results:
            return "No web search results available."
        
        context = "Web search results ordered by relevance score:\n\n"
        
        for i, result in enumerate(web_search_results[:10], 1):  # Show top 10
            context += f"{i}. {result['destination_name']} (Score: {result['score']:.2f})\n"
            context += f"   Criteria: {', '.join(result['criteria'])}\n"
            context += f"   Weight: {result['weight']}\n"
            context += f"   Score Breakdown: {result['score_breakdown']}\n"
            context += f"   Result: {result['result'][:200]}...\n\n"
        
        return context
    
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
    
    def extract_destination_parameters(self, user_request: str, progress_callback=None) -> DestinationRequest:
        """Extract structured parameters from the user request"""
        
        def format_parameters_for_ui(params_dict):
            """Return only meaningful parameters for UI display"""
            filtered = {}
            for key, value in params_dict.items():
                if value is None:
                    continue
                if isinstance(value, str) and not value.strip():
                    continue
                if isinstance(value, (list, tuple, set, dict)) and not value:
                    continue
                filtered[key] = value
            return filtered

        if self.mock_mode:
            print(f"🎭 MOCK MODE: Using mock extracted parameters")
            params = self.mock_data.get_mock_extracted_parameters(user_request)
            
            # Send extracted parameters to UI if callback provided
            if progress_callback:
                print(f"   📤 Sending mock extracted parameters to UI via progress callback")
                ui_parameters = format_parameters_for_ui(params)
                progress_callback({
                    'type': 'progress_update',
                    'message': '✅ Successfully extracted travel parameters (MOCK MODE)',
                    'details': f"Query: {params.get('query', 'N/A')} | Origin: {params.get('origin_location', 'N/A')} | Budget: {params.get('budget', 'N/A')} | Dates: {params.get('travel_dates', 'N/A')} | Group Size: {params.get('group_size', 'N/A')} | Traveler Type: {params.get('traveler_type', 'N/A')}",
                    'parameters': ui_parameters
                })
                print(f"   ✅ Mock progress callback sent successfully")
            
            return DestinationRequest(**params)
        
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
            
            # Send extracted parameters to UI if callback provided
            if progress_callback:
                print(f"   📤 Sending extracted parameters to UI via progress callback")
                ui_parameters = format_parameters_for_ui(params)
                progress_callback({
                    'type': 'progress_update',
                    'message': '✅ Successfully extracted travel parameters',
                    'details': f"Query: {params.get('query', 'N/A')} | Origin: {params.get('origin_location', 'N/A')} | Budget: {params.get('budget', 'N/A')} | Dates: {params.get('travel_dates', 'N/A')} | Group Size: {params.get('group_size', 'N/A')} | Traveler Type: {params.get('traveler_type', 'N/A')}",
                    'parameters': ui_parameters
                })
                print(f"   ✅ Progress callback sent successfully")
            else:
                print(f"   ⚠️ No progress callback provided")
            
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
            
            # Send extracted parameters to UI if callback provided (fallback parsing)
            if progress_callback:
                print(f"   📤 Sending extracted parameters to UI via progress callback (fallback)")
                fallback_params = {
                    'query': user_request,
                    'origin_location': origin_location,
                    'max_travel_time': max_travel_time,
                    'travel_dates': None,
                    'budget': None,
                    'interests': [],
                    'travel_style': None,
                    'traveler_type': traveler_type,
                    'group_size': group_size,
                    'age_range': age_range,
                    'mobility_requirements': mobility_requirements,
                    'seasonal_preferences': seasonal_preferences
                }
                ui_parameters = format_parameters_for_ui(fallback_params)
                progress_callback({
                    'type': 'progress_update',
                    'message': '✅ Successfully extracted travel parameters (fallback parsing)',
                    'details': f"Query: {user_request[:50]}... | Origin: {origin_location or 'N/A'} | Budget: N/A | Dates: N/A | Group Size: {group_size or 'N/A'} | Traveler Type: {traveler_type or 'N/A'}",
                    'parameters': ui_parameters
                })
                print(f"   ✅ Progress callback sent successfully (fallback)")
            else:
                print(f"   ⚠️ No progress callback provided (fallback)")
            
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
        
        # Perform comprehensive web search and ordering
        web_search_results = self.search_and_order_destinations(request)
        
        # Get current travel information for top results
        top_destinations = [result["destination_name"] for result in web_search_results[:5]]
        current_info = []
        for dest in top_destinations:
            dest_info = self.get_current_travel_info(dest)
            current_info.extend(dest_info)
        
        # Create web search context
        web_context = self._create_web_search_context(web_search_results)
        
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
        
        WEB SEARCH RESULTS (ordered by relevance to criteria):
        {web_context}
        
        Current Travel Information:
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
        
        EVALUATION INSTRUCTIONS:
        1. Review the web search results above, which are already ordered by relevance to your criteria
        2. Evaluate each destination in the order presented, considering how well it matches the specific criteria
        3. Focus on destinations that appear early in the ordered list as they scored highest for relevance
        4. Use both the web search information and your knowledge to provide comprehensive recommendations
        
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
        
        # Perform comprehensive web search and ordering
        web_search_results = self.search_and_order_destinations(request)
        
        # Get current travel information for top results
        top_destinations = [result["destination_name"] for result in web_search_results[:5]]
        current_info = []
        for dest in top_destinations:
            dest_info = self.get_current_travel_info(dest)
            current_info.extend(dest_info)
        
        # Create web search context
        web_context = self._create_web_search_context(web_search_results)
        
        prompt = f"""
        Find destinations that meet these specific constraints:
        
        Origin: {request.origin_location}
        Max travel time: {request.max_travel_time}
        Budget: {request.budget or 'Flexible'}
        Interests: {request.interests or 'General travel'}
        Travel style: {request.travel_style or 'Not specified'}
        
        WEB SEARCH RESULTS (ordered by relevance to constraints):
        {web_context}
        
        Current Travel Information:
        {chr(10).join(current_info) if current_info else "No current web information available - rely on your knowledge"}
        
        EVALUATION INSTRUCTIONS:
        1. Review the web search results above, which are already ordered by relevance to your constraints
        2. Evaluate each destination in the order presented, focusing on constraint compliance
        3. Prioritize destinations that appear early in the ordered list as they scored highest for constraint relevance
        4. Use both the web search information and your knowledge to provide comprehensive recommendations
        
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
    
    def _parse_smart_dates(self, date_input: str) -> str:
        """Parse date input intelligently based on current date"""
        if not date_input or date_input.strip() == "":
            return date_input
        
        date_input = date_input.strip().lower()
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        # If already has a year, return as is
        if re.search(r'\b(20\d{2})\b', date_input):
            return date_input
        
        # Handle seasons
        season_mappings = {
            'spring': {'months': [3, 4, 5], 'name': 'Spring'},
            'summer': {'months': [6, 7, 8], 'name': 'Summer'},
            'fall': {'months': [9, 10, 11], 'name': 'Fall'},
            'autumn': {'months': [9, 10, 11], 'name': 'Fall'},
            'winter': {'months': [12, 1, 2], 'name': 'Winter'}
        }
        
        for season, info in season_mappings.items():
            if season in date_input:
                # Check if we're currently in this season
                if current_month in info['months']:
                    # We're in the season, use next year
                    return f"{info['name']} {current_year + 1}"
                else:
                    # We're not in the season, check if it's coming up this year
                    next_season_month = min([m for m in info['months'] if m > current_month], default=min(info['months']))
                    if next_season_month > current_month:
                        # Season is coming up this year
                        return f"{info['name']} {current_year}"
                    else:
                        # Season already passed this year, use next year
                        return f"{info['name']} {current_year + 1}"
        
        # Handle months
        month_mappings = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9, 'sept': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12
        }
        
        for month_name, month_num in month_mappings.items():
            if month_name in date_input:
                if month_num > current_month:
                    # Month is coming up this year
                    return f"{month_name.title()} {current_year}"
                else:
                    # Month already passed this year, use next year
                    return f"{month_name.title()} {current_year + 1}"
        
        # Handle relative terms
        if 'next month' in date_input:
            next_month = current_date.replace(day=1) + timedelta(days=32)
            next_month = next_month.replace(day=1)
            return next_month.strftime("%B %Y")
        
        if 'next year' in date_input:
            return f"{current_year + 1}"
        
        if 'this year' in date_input:
            return f"{current_year}"
        
        # If no specific pattern matched, return original
        return date_input

    def _validate_travel_dates(self, request_params: DestinationRequest) -> Optional[str]:
        """Check if travel dates are specified and return error message if not"""
        if not request_params.travel_dates or request_params.travel_dates.strip() == "":
            return "Travel dates are required to proceed with destination research and feasibility checking. Please specify your travel dates (e.g., 'June 2024', 'summer', 'next month', 'March 15-20, 2024')."
        
        # Parse the dates intelligently
        parsed_dates = self._parse_smart_dates(request_params.travel_dates)
        request_params.travel_dates = parsed_dates
        
        return None
    
    def _validate_budget(self, request_params: DestinationRequest) -> Optional[str]:
        """Check if budget is specified and set default to luxury if not"""
        if (not request_params.budget or 
            request_params.budget.strip() == "" or 
            request_params.budget.lower() == "none" or
            request_params.budget.lower() == "not specified"):
            # Set default budget to luxury
            request_params.budget = "luxury"
            print(f"   💰 No budget specified, using default: luxury")
        return None
    
    def _validate_origin(self, request_params: DestinationRequest) -> Optional[str]:
        """Check if origin location is specified and return error message if not"""
        # Check if origin is provided in the request
        if (request_params.origin_location and 
            request_params.origin_location.strip() != "" and 
            request_params.origin_location.lower() not in ["none", "not specified", "unknown"]):
            return None
        
        # Check if origin is available in user preferences
        try:
            preferences = self.preferences_manager.get_comprehensive_recommendations()
            if preferences and preferences.get("home_airport") and preferences["home_airport"].strip() != "":
                return None
        except:
            pass
        
        # If no origin found, return error message
        return "Origin location is required to proceed with destination research and feasibility checking. Please specify your departure location (e.g., 'SFO', 'New York', 'London', 'LAX')."
    
    def _mock_research_destination(self, user_request: str, progress_callback=None) -> DestinationResearchResult:
        """Mock destination research for testing"""
        print(f"🎭 MOCK MODE: Performing mock destination research")
        
        # Get mock destinations
        mock_destinations = self.mock_data.get_mock_destinations(user_request, max_results=3)
        
        # Convert to DestinationOption objects
        primary_destinations = []
        for dest_data in mock_destinations:
            dest_option = DestinationOption(
                name=dest_data["name"],
                country=dest_data["country"],
                region=dest_data["region"],
                description=dest_data["description"],
                best_time_to_visit=dest_data["best_time_to_visit"],
                travel_time_from_origin=dest_data["travel_time_from_origin"],
                estimated_cost=dest_data["estimated_cost"],
                key_attractions=dest_data["key_attractions"],
                activities=dest_data["activities"],
                climate=dest_data["climate"],
                visa_requirements=dest_data["visa_requirements"],
                language=dest_data["language"],
                currency=dest_data["currency"],
                safety_rating=dest_data["safety_rating"],
                why_recommended=dest_data["why_recommended"],
                family_friendly_score=dest_data["family_friendly_score"],
                seasonal_highlights=dest_data["seasonal_highlights"],
                image_url=dest_data["image_url"]
            )
            primary_destinations.append(dest_option)
        
        # Send progress updates
        if progress_callback:
            progress_callback({
                'type': 'progress_update',
                'message': '🎭 Mock destination research completed',
                'details': f'Found {len(primary_destinations)} mock destinations'
            })
        
        return DestinationResearchResult(
            request_type="mock",
            primary_destinations=primary_destinations,
            alternative_destinations=[],
            travel_recommendations=f"Mock research found {len(primary_destinations)} destinations for your request.",
            date_required=False,
            budget_required=False,
            origin_required=False
        )
    
    def research_destination(
        self,
        user_request: str,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> DestinationResearchResult:
        """Main method to research destinations based on user request"""
        print(f"🔍 Starting destination research for: {user_request}")
        
        if self.mock_mode:
            print(f"🎭 MOCK MODE: Using mock destination research")
            return self._mock_research_destination(user_request, progress_callback)
        
        # Analyze request type
        request_type = self.analyze_request_type(user_request)
        print(f"   📋 Request type: {request_type}")
        
        # Extract parameters
        request_params = self.extract_destination_parameters(user_request, progress_callback)
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

        if progress_callback:
            def _format_value(value: Any) -> Optional[str]:
                if value is None:
                    return None
                if isinstance(value, list):
                    return ", ".join(str(item) for item in value) if value else None
                if isinstance(value, str) and value.strip() == "":
                    return None
                return str(value)

            parameter_summary = {
                "Query": _format_value(request_params.query),
                "Origin": _format_value(request_params.origin_location),
                "Max travel time": _format_value(request_params.max_travel_time),
                "Budget": _format_value(request_params.budget),
                "Interests": _format_value(request_params.interests),
                "Traveler type": _format_value(request_params.traveler_type),
                "Group size": _format_value(request_params.group_size),
                "Age range": _format_value(request_params.age_range),
                "Mobility": _format_value(request_params.mobility_requirements),
                "Seasonal": _format_value(request_params.seasonal_preferences),
                "Travel dates": _format_value(request_params.travel_dates)
            }

            filtered_summary = {
                key: value
                for key, value in parameter_summary.items()
                if value not in (None, "")
            }

            if filtered_summary:
                progress_callback({
                    'type': 'progress_update',
                    'message': '✅ Extracted destination parameters',
                    'details': 'Identified key details from your request to guide research.',
                    'parameters': filtered_summary
                })
        
        # Validate travel dates
        date_error = self._validate_travel_dates(request_params)
        if date_error:
            print(f"   ❌ {date_error}")
            return DestinationResearchResult(
                request_type=request_type,
                primary_destinations=[],
                alternative_destinations=[],
                travel_recommendations=date_error,
                user_choice_required=False,
                date_required=True,
                budget_required=False,
                origin_required=False
            )
        
        # Validate budget
        budget_error = self._validate_budget(request_params)
        if budget_error:
            print(f"   ❌ {budget_error}")
            return DestinationResearchResult(
                request_type=request_type,
                primary_destinations=[],
                alternative_destinations=[],
                travel_recommendations=budget_error,
                user_choice_required=False,
                date_required=False,
                budget_required=True,
                origin_required=False
            )
        
        # Validate origin
        origin_error = self._validate_origin(request_params)
        if origin_error:
            print(f"   ❌ {origin_error}")
            return DestinationResearchResult(
                request_type=request_type,
                primary_destinations=[],
                alternative_destinations=[],
                travel_recommendations=origin_error,
                user_choice_required=False,
                date_required=False,
                budget_required=False,
                origin_required=True
            )
        
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
        min_feasibility_score: float = 0.6,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> DestinationResearchResult:
        """Research destinations with feasibility checking and backtracking"""
        
        print(f"🔍 Starting destination research with feasibility checking: {user_request}")
        print(f"   📋 Request details: {user_request}")
        
        # First, do the normal destination research
        print(f"   🚀 Initializing destination research...")
        initial_result = self.research_destination(
            user_request,
            progress_callback=progress_callback
        )
        print(f"   ✅ Initial research completed - found {len(initial_result.primary_destinations) if initial_result.primary_destinations else 0} destinations")
        
        if not check_feasibility:
            return initial_result
        
        # Extract parameters for feasibility checking
        request_params = self.extract_destination_parameters(user_request, progress_callback)
        
        # Check feasibility for all primary destinations
        if initial_result.primary_destinations:
            print(f"\n🔍 Checking feasibility for {len(initial_result.primary_destinations)} destinations...")
            destination_names = [dest.name for dest in initial_result.primary_destinations]
            print(f"   📍 Destinations to check: {', '.join(destination_names)}")
            print(f"   ✈️  Origin: {request_params.origin_location or 'Unknown'}")
            print(f"   📅 Travel dates: {request_params.travel_dates or 'summer'}")
            print(f"   💰 Budget: {request_params.budget or 'Not specified'}")
            print(f"   👥 Traveler type: {request_params.traveler_type or 'leisure'}")
            
            print(f"   🔄 Starting feasibility analysis...")
            feasibility_results = self.feasibility_checker.check_multiple_destinations(
                destinations=destination_names,
                origin=request_params.origin_location or "Unknown",
                travel_dates=request_params.travel_dates or "summer",
                budget=request_params.budget,
                traveler_type=request_params.traveler_type or "leisure"
            )
            print(f"   ✅ Feasibility analysis completed for {len(feasibility_results)} destinations")
            
            # Filter for feasible destinations
            print(f"   🔍 Filtering destinations by feasibility (min score: {min_feasibility_score})...")
            feasible_destinations = []
            infeasible_destinations = []
            
            for dest_name, feasibility_result in feasibility_results:
                print(f"   📊 {dest_name}: Score {feasibility_result.feasibility_score:.2f}, Feasible: {feasibility_result.is_feasible}")
                if feasibility_result.is_feasible and feasibility_result.feasibility_score >= min_feasibility_score:
                    # Find the original destination object
                    original_dest = next((d for d in initial_result.primary_destinations if d.name == dest_name), None)
                    if original_dest:
                        # Add feasibility information to the destination
                        original_dest.estimated_cost = f"${feasibility_result.estimated_total_cost:.0f}"
                        if isinstance(feasibility_result.details, dict):
                            flight_details = feasibility_result.details.get("flight", {})
                            if isinstance(flight_details, dict):
                                original_dest.travel_time_from_origin = flight_details.get("flight_duration", "Unknown")
                            else:
                                original_dest.travel_time_from_origin = "Unknown"
                        else:
                            original_dest.travel_time_from_origin = "Unknown"
                        feasible_destinations.append(original_dest)
                        print(f"   ✅ {dest_name} added to feasible destinations")
                else:
                    infeasible_destinations.append((dest_name, feasibility_result))
                    print(f"   ❌ {dest_name} marked as infeasible")
            
            print(f"   📈 Results: {len(feasible_destinations)} feasible, {len(infeasible_destinations)} infeasible")
            
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
