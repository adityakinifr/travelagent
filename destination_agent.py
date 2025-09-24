"""
Destination Research Agent for handling specific and abstract destination requests
"""

import os
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
        prompt = f"""
        Research the destination: {request.query}
        
        Provide comprehensive information about this destination including:
        - Best time to visit
        - Key attractions and activities
        - Climate and weather
        - Visa requirements
        - Language and currency
        - Safety considerations
        - Estimated costs
        - Why it's recommended for travel
        
        If origin_location is provided ({request.origin_location}), include travel time and options.
        If budget is specified ({request.budget}), tailor recommendations accordingly.
        If interests are mentioned ({request.interests}), focus on relevant attractions.
        
        Format as a detailed destination profile.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        # Parse the response into structured data
        destination = self._parse_destination_response(response.content, request.query)
        
        return DestinationResearchResult(
            request_type="specific",
            primary_destinations=[destination],
            alternative_destinations=[],
            travel_recommendations=response.content
        )
    
    def research_abstract_destination(self, request: DestinationRequest) -> DestinationResearchResult:
        """Research destinations based on abstract criteria"""
        prompt = f"""
        Find destinations that match these criteria:
        
        Query: {request.query}
        Origin: {request.origin_location or 'Not specified'}
        Max travel time: {request.max_travel_time or 'Not specified'}
        Budget: {request.budget or 'Not specified'}
        Interests: {request.interests or 'Not specified'}
        Travel style: {request.travel_style or 'Not specified'}
        
        Provide 3-5 destination recommendations that match the criteria.
        For each destination, include:
        - Name and location
        - Why it matches the criteria
        - Best time to visit
        - Key attractions
        - Travel time from origin (if specified)
        - Estimated costs
        - Climate and activities
        
        Rank them by how well they match the criteria.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        # Parse multiple destinations from response
        destinations = self._parse_multiple_destinations(response.content)
        
        return DestinationResearchResult(
            request_type="abstract",
            primary_destinations=destinations[:3],  # Top 3
            alternative_destinations=destinations[3:],  # Rest as alternatives
            travel_recommendations=response.content
        )
    
    def research_multi_location(self, request: DestinationRequest) -> DestinationResearchResult:
        """Research multiple destinations or provide comparisons"""
        prompt = f"""
        Analyze this multi-location travel request: {request.query}
        
        If multiple specific destinations are mentioned, provide detailed comparison.
        If the user wants to choose between options, provide pros/cons for each.
        
        For each destination, include:
        - Overview and highlights
        - Best time to visit
        - Key attractions and activities
        - Travel logistics (if origin specified)
        - Costs and budget considerations
        - Unique selling points
        
        Provide a comparison summary highlighting differences and recommendations.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        destinations = self._parse_multiple_destinations(response.content)
        
        return DestinationResearchResult(
            request_type="multi_location",
            primary_destinations=destinations,
            alternative_destinations=[],
            travel_recommendations=response.content,
            comparison_summary=self._extract_comparison_summary(response.content)
        )
    
    def research_constrained_destination(self, request: DestinationRequest) -> DestinationResearchResult:
        """Research destinations with specific constraints"""
        prompt = f"""
        Find destinations that meet these specific constraints:
        
        Origin: {request.origin_location}
        Max travel time: {request.max_travel_time}
        Budget: {request.budget or 'Flexible'}
        Interests: {request.interests or 'General travel'}
        Travel style: {request.travel_style or 'Not specified'}
        
        Focus on destinations that are:
        1. Within the specified travel time from origin
        2. Match the budget constraints
        3. Align with interests and travel style
        
        Provide 3-5 options ranked by how well they meet the constraints.
        Include travel time, costs, and why each destination fits the criteria.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        destinations = self._parse_multiple_destinations(response.content)
        
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
    
    def _parse_destination_response(self, response: str, destination_name: str) -> DestinationOption:
        """Parse LLM response into structured destination data"""
        # This is a simplified parser - in production, you'd want more robust parsing
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
    
    def _parse_multiple_destinations(self, response: str) -> List[DestinationOption]:
        """Parse multiple destinations from LLM response"""
        # Simplified parsing - in production, use more sophisticated parsing
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
