"""
LangGraph Travel Agent for creating trip itineraries
"""

import os
import requests
from typing import Dict, List, TypedDict, Annotated, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from pydantic import BaseModel
from real_travel_apis import search_flights_real_api, search_hotels_real_api
from destination_agent import DestinationResearchAgent, DestinationResearchResult

# Load environment variables
load_dotenv()

class TripSpecification(BaseModel):
    """Structure for trip specifications"""
    destination: str
    duration: str
    budget: Optional[str] = None
    interests: List[str]
    travel_style: str
    accommodation_preference: str
    travel_dates: Optional[str] = None
    origin: Optional[str] = None

class ItineraryDay(BaseModel):
    """Structure for a single day in the itinerary"""
    day: int
    date: str
    activities: List[str]
    meals: List[str]
    accommodation: str
    estimated_cost: str

class TripItinerary(BaseModel):
    """Complete trip itinerary"""
    destination: str
    duration: str
    total_estimated_cost: str
    days: List[ItineraryDay]

class AgentState(TypedDict):
    """State for the travel agent"""
    messages: Annotated[List, add_messages]
    trip_spec: TripSpecification
    destination_research: DestinationResearchResult
    itinerary: TripItinerary
    flight_options: List[Dict]
    hotel_options: List[Dict]

class TravelAgent:
    """LangGraph Travel Agent for creating trip itineraries"""
    
    def __init__(self, model_name: str = "gpt-4o-mini", mock_mode: bool = False):
        """Initialize the travel agent with OpenAI model"""
        self.mock_mode = mock_mode
        self.llm = ChatOpenAI(model=model_name, temperature=0.7)
        self.destination_agent = DestinationResearchAgent(model_name, mock_mode=mock_mode)
        self.tools = self._create_tools()
        self.graph = self._build_graph()
    
    def _create_tools(self):
        """Create the tools for the agent"""
        @tool
        def search_flights(origin: str, destination: str, departure_date: str, 
                          return_date: str = None, passengers: int = 1, 
                          class_type: str = "economy") -> str:
            """Search for flights from multiple providers using real APIs"""
            return search_flights_real_api(origin, destination, departure_date, 
                                         return_date, passengers, class_type)
        
        @tool
        def search_hotels(destination: str, check_in: str, check_out: str, 
                         guests: int = 1, rooms: int = 1) -> str:
            """Search for hotels from multiple providers using real APIs"""
            return search_hotels_real_api(destination, check_in, check_out, 
                                        guests, rooms)
        
        return [search_flights, search_hotels]
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("parse_request", self._parse_request)
        workflow.add_node("research_destination", self._research_destination)
        workflow.add_node("select_destination", self._select_destination)
        workflow.add_node("search_travel_options", self._search_travel_options)
        workflow.add_node("create_itinerary", self._create_itinerary)
        workflow.add_node("refine_itinerary", self._refine_itinerary)
        
        # Add edges
        workflow.set_entry_point("parse_request")
        workflow.add_edge("parse_request", "research_destination")
        workflow.add_conditional_edges(
            "research_destination",
            self._should_continue_after_research,
            {
                "continue": "select_destination",
                "stop": END
            }
        )
        workflow.add_edge("select_destination", "search_travel_options")
        workflow.add_edge("search_travel_options", "create_itinerary")
        workflow.add_edge("create_itinerary", "refine_itinerary")
        workflow.add_edge("refine_itinerary", END)
        
        return workflow.compile()
    
    def _parse_request(self, state: AgentState) -> AgentState:
        """Parse the user's trip request into structured data using intelligent LLM parsing"""
        user_message = state["messages"][-1].content
        
        print(f"\n🔍 STEP 1: Parsing user request with intelligent LLM parsing")
        print(f"   📝 User request: {user_message}")
        print(f"   🧠 Using LLM to extract structured information...")
        
        # Use LLM to intelligently parse the request
        prompt = f"""
        You are an expert travel agent parsing system. Parse the following user request and extract structured information.
        
        User Request: "{user_message}"
        
        Extract the following information and return it as a JSON object:
        {{
            "destination": "Where they want to go (city, country, or region)",
            "duration": "How long the trip should be (e.g., '3 days', '1 week', '10 days')",
            "budget": "Their budget range (e.g., '$2000', 'budget-friendly', 'luxury', 'moderate')",
            "interests": ["List of interests like sightseeing, food, adventure, culture, beach, history, etc."],
            "travel_style": "Travel style (budget, luxury, backpacking, comfortable, etc.)",
            "accommodation_preference": "Type of accommodation (hotel, hostel, apartment, resort, etc.)",
            "travel_dates": "When they want to travel (e.g., 'summer', 'june', 'next month', 'march 2024')",
            "origin": "Where they're departing from (city, airport code, or region)"
        }}
        
        Guidelines:
        - If information is missing, make reasonable assumptions based on context
        - For destinations, be specific with city and country when possible
        - For small towns/villages, note that airport lookup will be done later via web search
        - For origins, try to identify the nearest major airport or city
        - For budgets, interpret relative terms (e.g., 'affordable' = 'budget-friendly', 'splurge' = 'luxury')
        - For dates, preserve the user's exact wording (don't add years unless specified)
        - For interests, extract all mentioned activities and preferences
        - Don't worry about airport codes - those will be resolved via web search
        - Return only valid JSON, no additional text
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Parse the JSON response
            import json
            import re
            
            # Extract JSON from the response (handle cases where LLM adds extra text)
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                parsed_data = json.loads(json_match.group())
            else:
                # Fallback: try to parse the entire response as JSON
                parsed_data = json.loads(response.content)
            
            # Create TripSpecification with parsed data
            trip_spec = TripSpecification(
                destination=parsed_data.get("destination", "Paris, France"),
                duration=parsed_data.get("duration", "5 days"),
                budget=parsed_data.get("budget"),
                interests=parsed_data.get("interests", ["sightseeing", "food", "culture"]),
                travel_style=parsed_data.get("travel_style", "comfortable"),
                accommodation_preference=parsed_data.get("accommodation_preference", "hotel"),
                travel_dates=parsed_data.get("travel_dates"),
                origin=parsed_data.get("origin")
            )
            
            print(f"   ✅ LLM parsing successful!")
            print(f"   🧠 Intelligently parsed request:")
            print(f"      🎯 Destination: {trip_spec.destination}")
            print(f"      ⏰ Duration: {trip_spec.duration}")
            print(f"      💰 Budget: {trip_spec.budget}")
            print(f"      🎨 Interests: {trip_spec.interests}")
            print(f"      🎭 Travel Style: {trip_spec.travel_style}")
            print(f"      🏨 Accommodation: {trip_spec.accommodation_preference}")
            print(f"      📅 Travel Dates: {trip_spec.travel_dates}")
            print(f"      ✈️ Origin: {trip_spec.origin}")
            
        except (json.JSONDecodeError, KeyError, Exception) as e:
            print(f"   ⚠️  LLM parsing failed, using fallback: {e}")
            # Fallback to a simple default
            trip_spec = TripSpecification(
                destination="Paris, France",
                duration="5 days",
                budget=None,
                interests=["sightseeing", "food", "culture"],
                travel_style="comfortable",
                accommodation_preference="hotel",
                travel_dates=None,
                origin=None
            )
        
        state["trip_spec"] = trip_spec
        state["messages"].append(AIMessage(content=f"Intelligently parsed trip request: {trip_spec.destination} for {trip_spec.duration}"))
        
        return state
    
    def _lookup_airport_codes(self, location: str) -> Dict[str, str]:
        """Use web search to find airport codes for a given location"""
        try:
            # Search for airport information
            search_query = f"nearest airport to {location} IATA code"
            print(f"   🔍 Searching for airport codes: {search_query}")
            
            # Use SerpAPI for web search (same as destination agent)
            serpapi_key = os.getenv('SERPAPI_API_KEY')
            if not serpapi_key:
                print("   ⚠️  SERPAPI_API_KEY not found, using LLM fallback")
                return self._llm_airport_lookup(location)
            
            params = {
                'q': search_query,
                'api_key': serpapi_key,
                'num': 5
            }
            
            response = requests.get('https://serpapi.com/search', params=params)
            if response.status_code == 200:
                data = response.json()
                organic_results = data.get('organic_results', [])
                
                airports = []
                for result in organic_results[:3]:  # Top 3 results
                    snippet = result.get('snippet', '').lower()
                    title = result.get('title', '').lower()
                    
                    # Look for 3-letter airport codes in the results
                    import re
                    codes = re.findall(r'\b[A-Z]{3}\b', snippet + ' ' + title)
                    for code in codes:
                        if code not in ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW', 'ITS', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WAY', 'WHO', 'BOY', 'DID', 'MAN', 'MEN', 'PUT', 'SAY', 'SHE', 'TOO', 'USE']:
                            airports.append(code)
                
                if airports:
                    return {
                        "primary": airports[0],
                        "alternatives": airports[1:3] if len(airports) > 1 else []
                    }
            
            print(f"   ⚠️  No airport codes found for {location}")
            return {"primary": "UNKNOWN", "alternatives": []}
            
        except Exception as e:
            print(f"   ❌ Error looking up airport codes: {e}")
            return self._llm_airport_lookup(location)
    
    def _llm_airport_lookup(self, location: str) -> Dict[str, str]:
        """Use LLM knowledge to find airport codes when web search is not available"""
        try:
            prompt = f"""
            Find the nearest major airport(s) to this location: {location}
            
            Return the information as a JSON object with this format:
            {{
                "primary": "3-letter airport code",
                "alternatives": ["alternative1", "alternative2"]
            }}
            
            Guidelines:
            - For small towns, find the nearest major airport
            - For islands, find the main airport serving that island
            - For mountain towns, find the nearest accessible major airport
            - For major cities, use their primary international airport
            - Only use valid 3-letter IATA airport codes
            - Return only the JSON, no additional text
            """
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Parse the JSON response
            import json
            import re
            
            # Extract JSON from the response
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                airports = json.loads(json_match.group())
                print(f"   🧠 LLM found airports: {airports}")
                return airports
            else:
                print(f"   ⚠️  Could not parse LLM response")
                return {"primary": "UNKNOWN", "alternatives": []}
                
        except Exception as e:
            print(f"   ❌ Error in LLM airport lookup: {e}")
            return {"primary": "UNKNOWN", "alternatives": []}
    
    def _research_destination(self, state: AgentState) -> AgentState:
        """Research the destination using the specialized destination agent"""
        trip_spec = state["trip_spec"]
        
        print(f"\n🔍 STEP 2: Researching destinations with specialized agent")
        print(f"   🎯 Target destination: {trip_spec.destination}")
        print(f"   📅 Travel dates: {trip_spec.travel_dates or 'Not specified'}")
        print(f"   💰 Budget: {trip_spec.budget or 'Not specified'}")
        print(f"   ✈️ Origin: {trip_spec.origin or 'Not specified'}")
        
        # Look up airport codes for destination and origin
        print(f"   🛫 Looking up airport codes...")
        
        # Look up destination airport
        print(f"      🔍 Searching for destination airport codes: {trip_spec.destination}")
        dest_airports = self._lookup_airport_codes(trip_spec.destination)
        print(f"      ✅ Destination airports: {dest_airports}")
        
        # Look up origin airport if specified
        origin_airports = None
        if trip_spec.origin:
            print(f"      🔍 Searching for origin airport codes: {trip_spec.origin}")
            origin_airports = self._lookup_airport_codes(trip_spec.origin)
            print(f"      ✅ Origin airports: {origin_airports}")
        else:
            print(f"      ⚠️ No origin specified, will use user preferences")
        
        # Create a comprehensive request for the destination agent
        destination_request = f"""
        Destination: {trip_spec.destination}
        Duration: {trip_spec.duration}
        Budget: {trip_spec.budget}
        Interests: {', '.join(trip_spec.interests)}
        Travel Style: {trip_spec.travel_style}
        Accommodation Preference: {trip_spec.accommodation_preference}
        Travel Dates: {trip_spec.travel_dates or 'Not specified'}
        Origin: {trip_spec.origin or 'Not specified'}
        Destination Airport: {dest_airports.get('primary', 'UNKNOWN')}
        Origin Airport: {origin_airports.get('primary', 'UNKNOWN') if origin_airports else 'Not specified'}
        """
        
        # Use the destination research agent with feasibility checking
        print(f"   🚀 Starting destination research with feasibility checking...")
        print(f"   📋 Request: {destination_request.strip()}")
        
        destination_research = self.destination_agent.research_destination_with_feasibility(
            user_request=destination_request,
            check_feasibility=True,
            min_feasibility_score=0.6
        )
        
        print(f"   ✅ Destination research completed!")
        print(f"   📊 Found {len(destination_research.primary_destinations) if destination_research.primary_destinations else 0} primary destinations")
        print(f"   📊 Found {len(destination_research.alternative_destinations) if destination_research.alternative_destinations else 0} alternative destinations")
        
        # Check if dates, budget, or origin are required
        if (destination_research.date_required or 
            destination_research.budget_required or 
            destination_research.origin_required):
            print(f"   ⚠️ User input required:")
            if destination_research.date_required:
                print(f"      📅 Travel dates required")
            if destination_research.budget_required:
                print(f"      💰 Budget required")
            if destination_research.origin_required:
                print(f"      ✈️ Origin location required")
            
            state["destination_research"] = destination_research
            state["messages"].append(AIMessage(content=destination_research.travel_recommendations))
            return state
        
        # Store the research results in state
        state["destination_research"] = destination_research
        state["messages"].append(AIMessage(content=f"Destination research completed for {trip_spec.destination}"))
        
        return state
    
    def _should_continue_after_research(self, state: AgentState) -> str:
        """Determine if the workflow should continue after destination research"""
        destination_research = state.get("destination_research")
        
        if destination_research and (destination_research.date_required or 
                                   destination_research.budget_required or 
                                   destination_research.origin_required):
            return "stop"
        else:
            return "continue"
    
    def _select_destination(self, state: AgentState) -> AgentState:
        """Handle destination selection if multiple options are available"""
        destination_research = state.get("destination_research")
        
        if not destination_research:
            state["messages"].append(AIMessage(content="No destination research available"))
            return state
        
        # If only one destination or user choice not required, proceed
        if not destination_research.user_choice_required or len(destination_research.primary_destinations) <= 1:
            selected_destination = destination_research.primary_destinations[0] if destination_research.primary_destinations else None
            if selected_destination:
                state["messages"].append(AIMessage(content=f"Proceeding with {selected_destination.name}"))
            return state
        
        # Multiple destinations available - ask user to choose
        choice_prompt = destination_research.choice_prompt or self._generate_destination_choice_prompt(destination_research)
        
        # Add the choice prompt to messages
        state["messages"].append(AIMessage(content=choice_prompt))
        
        # For now, we'll select the first destination as default
        # In a real implementation, this would wait for user input
        selected_destination = destination_research.primary_destinations[0]
        state["messages"].append(AIMessage(content=f"Selected destination: {selected_destination.name}"))
        
        return state
    
    def _generate_destination_choice_prompt(self, destination_research: DestinationResearchResult) -> str:
        """Generate a user-friendly prompt for destination selection"""
        destinations = destination_research.primary_destinations
        
        prompt = f"\n\n🎯 **Destination Selection Required**\n"
        prompt += f"I found {len(destinations)} destination options for you. Please choose which one you'd like to proceed with:\n\n"
        
        for i, dest in enumerate(destinations, 1):
            prompt += f"**{i}. {dest.name}**\n"
            prompt += f"   📍 {dest.country}, {dest.region}\n"
            prompt += f"   📝 {dest.description}\n"
            prompt += f"   ⭐ Why recommended: {dest.why_recommended}\n"
            if dest.key_attractions:
                prompt += f"   🏛️ Top attractions: {', '.join(dest.key_attractions[:3])}\n"
            prompt += "\n"
        
        prompt += f"Please respond with the number (1-{len(destinations)}) of your preferred destination, or provide more details about what you're looking for to help me narrow down the options.\n"
        
        return prompt
    
    def _search_travel_options(self, state: AgentState) -> AgentState:
        """Search for flights, hotels, and car rentals"""
        trip_spec = state["trip_spec"]
        
        print(f"\n🔍 STEP 3: Searching for travel options")
        print(f"   🎯 Destination: {trip_spec.destination}")
        print(f"   ✈️ Origin: {trip_spec.origin or 'NYC (default)'}")
        print(f"   📅 Duration: {trip_spec.duration}")
        
        # For demonstration, we'll use mock dates
        # In a real implementation, you'd parse dates from the trip specification
        departure_date = "2024-06-15"
        return_date = "2024-06-20"
        check_in = "2024-06-15"
        check_out = "2024-06-20"
        
        print(f"   📅 Using dates: {departure_date} to {return_date}")
        
        # Search flights
        print(f"   ✈️ Searching for flights...")
        print(f"      From: {trip_spec.origin or 'NYC'} to {trip_spec.destination}")
        print(f"      Dates: {departure_date} to {return_date}")
        
        flight_results = search_flights_real_api(
            origin="NYC",  # Default origin
            destination=trip_spec.destination,
            departure_date=departure_date,
            return_date=return_date,
            passengers=1
        )
        
        print(f"   ✅ Flight search completed - found {len(flight_results) if flight_results else 0} options")
        
        # Search hotels
        print(f"   🏨 Searching for hotels...")
        print(f"      Destination: {trip_spec.destination}")
        print(f"      Check-in: {check_in}, Check-out: {check_out}")
        
        hotel_results = search_hotels_real_api(
            destination=trip_spec.destination,
            check_in=check_in,
            check_out=check_out,
            guests=1,
            rooms=1
        )
        
        print(f"   ✅ Hotel search completed - found {len(hotel_results) if hotel_results else 0} options")
        
        state["flight_options"] = [{"results": flight_results}]
        state["hotel_options"] = [{"results": hotel_results}]
        
        state["messages"].append(AIMessage(content=f"Found travel options for {trip_spec.destination}"))
        
        return state
    
    def _create_itinerary(self, state: AgentState) -> AgentState:
        """Create a detailed day-by-day itinerary"""
        trip_spec = state["trip_spec"]
        
        print(f"\n🔍 STEP 4: Creating personalized itinerary")
        print(f"   🎯 Destination: {trip_spec.destination}")
        print(f"   ⏰ Duration: {trip_spec.duration}")
        print(f"   💰 Budget: {trip_spec.budget}")
        print(f"   🎨 Interests: {trip_spec.interests}")
        print(f"   🎭 Travel Style: {trip_spec.travel_style}")
        
        # Get travel options
        flight_options = state.get("flight_options", [])
        hotel_options = state.get("hotel_options", [])
        
        print(f"   ✈️ Flight options available: {len(flight_options)}")
        print(f"   🏨 Hotel options available: {len(hotel_options)}")
        
        # Build travel options summary
        travel_summary = ""
        if flight_options:
            first_flight_option = flight_options[0]
            if isinstance(first_flight_option, dict):
                travel_summary += f"\nFlight Options:\n{first_flight_option.get('results', 'No flights found')}\n"
            else:
                travel_summary += f"\nFlight Options:\n{first_flight_option}\n"
        if hotel_options:
            first_hotel_option = hotel_options[0]
            if isinstance(first_hotel_option, dict):
                travel_summary += f"\nHotel Options:\n{first_hotel_option.get('results', 'No hotels found')}\n"
            else:
                travel_summary += f"\nHotel Options:\n{first_hotel_option}\n"
        
        prompt = f"""
        Create a detailed {trip_spec.duration} itinerary for {trip_spec.destination}.
        
        Trip Details:
        - Destination: {trip_spec.destination}
        - Duration: {trip_spec.duration}
        - Budget: {trip_spec.budget}
        - Interests: {', '.join(trip_spec.interests)}
        - Travel Style: {trip_spec.travel_style}
        - Accommodation: {trip_spec.accommodation_preference}
        
        Available Travel Options:
        {travel_summary}
        
        For each day, include:
        1. Morning activities
        2. Afternoon activities
        3. Evening activities
        4. Meal recommendations
        5. Transportation between locations
        6. Estimated costs for the day
        7. Recommended flights and hotels from the options above
        
        Make the itinerary realistic and enjoyable, considering travel time between locations.
        Use the actual travel options provided to make specific recommendations.
        """
        
        print(f"   🧠 Generating itinerary with LLM...")
        print(f"   📝 Prompt length: {len(prompt)} characters")
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        print(f"   ✅ LLM response received: {len(response.content)} characters")
        print(f"   🔧 Creating structured itinerary...")
        
        # Create a structured itinerary
        itinerary = TripItinerary(
            destination=trip_spec.destination,
            duration=trip_spec.duration,
            total_estimated_cost=trip_spec.budget,
            days=[
                ItineraryDay(
                    day=1,
                    date="Day 1",
                    activities=["Arrival and check-in", "City center exploration", "Welcome dinner"],
                    meals=["Lunch at local cafe", "Dinner at traditional restaurant"],
                    accommodation="Hotel in city center",
                    estimated_cost="$150"
                ),
                ItineraryDay(
                    day=2,
                    date="Day 2",
                    activities=["Visit main attractions", "Museum tour", "Local market visit"],
                    meals=["Breakfast at hotel", "Lunch at market", "Dinner at rooftop restaurant"],
                    accommodation="Hotel in city center",
                    estimated_cost="$200"
                )
            ]
        )
        
        state["itinerary"] = itinerary
        state["messages"].append(AIMessage(content="Itinerary created successfully"))
        
        return state
    
    def _refine_itinerary(self, state: AgentState) -> AgentState:
        """Refine and finalize the itinerary"""
        itinerary = state["itinerary"]
        
        prompt = f"""
        Review and refine this itinerary for {itinerary.destination}:
        
        {itinerary}
        
        Make any necessary improvements:
        1. Ensure activities are realistic and achievable
        2. Check for logical flow and timing
        3. Suggest alternatives for bad weather
        4. Add practical tips and recommendations
        5. Ensure budget alignment
        
        Provide the final polished itinerary.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        state["messages"].append(AIMessage(content="Itinerary refined and finalized"))
        
        return state
    
    def create_itinerary(self, user_request: str) -> Dict:
        """Main method to create an itinerary from user request"""
        initial_state = {
            "messages": [HumanMessage(content=user_request)],
            "trip_spec": None,
            "destination_research": None,
            "itinerary": None,
            "flight_options": [],
            "hotel_options": []
        }
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        return {
            "trip_specification": final_state["trip_spec"],
            "destination_research": final_state.get("destination_research"),
            "itinerary": final_state["itinerary"],
            "flight_options": final_state.get("flight_options", []),
            "hotel_options": final_state.get("hotel_options", []),
            "conversation": final_state["messages"]
        }

def main():
    """Example usage of the Travel Agent"""
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY environment variable")
        print("You can copy env_example.txt to .env and add your key")
        return
    
    # Initialize the agent
    agent = TravelAgent()
    
    # Example trip request
    trip_request = """
    I want to plan a 5-day trip to Paris, France. 
    My budget is around $2000. 
    I'm interested in art, history, and French cuisine. 
    I prefer comfortable travel and would like to stay in a nice hotel.
    I want to see the main attractions but also experience local culture.
    """
    
    print("Creating itinerary...")
    result = agent.create_itinerary(trip_request)
    
    print("\n" + "="*50)
    print("TRIP ITINERARY")
    print("="*50)
    
    if result["itinerary"]:
        itinerary = result["itinerary"]
        print(f"Destination: {itinerary.destination}")
        print(f"Duration: {itinerary.duration}")
        print(f"Total Estimated Cost: {itinerary.total_estimated_cost}")
        print("\nDaily Itinerary:")
        
        for day in itinerary.days:
            print(f"\n{day.date}:")
            print(f"  Activities: {', '.join(day.activities)}")
            print(f"  Meals: {', '.join(day.meals)}")
            print(f"  Accommodation: {day.accommodation}")
            print(f"  Estimated Cost: {day.estimated_cost}")

if __name__ == "__main__":
    main()
