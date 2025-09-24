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

class DestinationResearchResult(BaseModel):
    """Structure for destination research results"""
    request_type: str  # "specific", "abstract", "multi_location"
    primary_destinations: List[DestinationOption]
    alternative_destinations: List[DestinationOption]
    travel_recommendations: str
    comparison_summary: Optional[str] = None

class DestinationResearchAgent:
    """Specialized agent for destination research and recommendation"""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """Initialize the destination research agent"""
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.serpapi_key = os.getenv("SERPAPI_KEY")
    
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
            "travel_style": "Travel style if mentioned (e.g., 'relaxing', 'adventure', 'cultural')"
        }}
        
        If a field is not mentioned, use null. Be specific and accurate.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        try:
            import json
            params = json.loads(response.content)
            return DestinationRequest(**params)
        except:
            # Fallback parsing
            return DestinationRequest(
                query=user_request,
                interests=[],
                travel_style=None
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
        
        return DestinationResearchResult(
            request_type="specific",
            primary_destinations=[destination],
            alternative_destinations=[],
            travel_recommendations=response.content
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
        
        Current Web Information:
        {chr(10).join(current_info) if current_info else "No current web information available - rely on your knowledge"}
        
        Use your knowledge and current information to provide 3-5 destination recommendations that match the criteria.
        For each destination, include:
        - Name and location
        - Why it matches the criteria
        - Best time to visit (consider current year 2024)
        - Key attractions and activities
        - Travel time from origin (if specified)
        - Estimated costs for different budget levels
        - Climate and weather
        - Safety considerations
        - Unique selling points
        
        Rank them by how well they match the criteria and provide detailed reasoning for each recommendation.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        # Create structured destinations from LLM response
        destinations = self._create_multiple_destinations_from_llm(response.content)
        
        return DestinationResearchResult(
            request_type="abstract",
            primary_destinations=destinations[:3],  # Top 3
            alternative_destinations=destinations[3:],  # Rest as alternatives
            travel_recommendations=response.content
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
        
        return DestinationResearchResult(
            request_type="multi_location",
            primary_destinations=destinations,
            alternative_destinations=[],
            travel_recommendations=response.content,
            comparison_summary=self._extract_comparison_summary(response.content)
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
        
        return DestinationResearchResult(
            request_type="constrained",
            primary_destinations=destinations[:3],
            alternative_destinations=destinations[3:],
            travel_recommendations=response.content
        )
    
    def research_destination(self, user_request: str) -> DestinationResearchResult:
        """Main method to research destinations based on user request"""
        # Analyze request type
        request_type = self.analyze_request_type(user_request)
        
        # Extract parameters
        request_params = self.extract_destination_parameters(user_request)
        
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
            "why_recommended": "Why this destination is recommended"
        }}
        
        Extract all destinations mentioned in the response. If information is not available for a field, use reasonable defaults.
        Return as a JSON array.
        """
        
        try:
            extraction_response = self.llm.invoke([HumanMessage(content=extraction_prompt)])
            import json
            destinations_data = json.loads(extraction_response.content)
            destinations = [DestinationOption(**dest) for dest in destinations_data]
            return destinations[:5]  # Limit to 5 destinations
        except:
            # Fallback to basic parsing
            destinations = []
            lines = response.split('\n')
            current_dest = None
            
            for line in lines:
                if line.strip() and not line.startswith(' '):
                    if current_dest:
                        destinations.append(current_dest)
                    current_dest = DestinationOption(
                        name=line.strip(),
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
                    )
            
            if current_dest:
                destinations.append(current_dest)
            
            return destinations[:5]  # Limit to 5 destinations
    
    def _extract_comparison_summary(self, response: str) -> str:
        """Extract comparison summary from response"""
        # Look for comparison keywords and extract relevant section
        if "comparison" in response.lower() or "compare" in response.lower():
            return "See detailed comparison in travel recommendations"
        return "Multiple destinations analyzed - see individual recommendations"
