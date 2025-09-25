"""
LangGraph Travel Agent for creating trip itineraries
"""

import os
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
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """Initialize the travel agent with OpenAI model"""
        self.llm = ChatOpenAI(model=model_name, temperature=0.7)
        self.destination_agent = DestinationResearchAgent(model_name)
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
        """Parse the user's trip request into structured data"""
        user_message = state["messages"][-1].content
        
        prompt = f"""
        Parse the following trip request and extract the key information:
        
        User Request: {user_message}
        
        Extract and structure the following information:
        - destination: Where they want to go
        - duration: How long the trip should be
        - budget: Their budget range
        - interests: What they're interested in (sightseeing, food, adventure, culture, etc.)
        - travel_style: Their preferred travel style (budget, luxury, backpacking, etc.)
        - accommodation_preference: Type of accommodation they prefer
        - travel_dates: When they want to travel (e.g., "June 2024", "summer", "next month", "March 15-20, 2024")
        
        If any information is missing, make reasonable assumptions based on the context.
        Return the information in a structured format.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        # Parse the response to create TripSpecification
        # For now, we'll use simple parsing - in a real implementation, you'd use more sophisticated parsing
        content = response.content.lower()
        user_content = user_message.lower()
        
        # Extract destination
        destination = "Paris, France"  # Default
        if "paris" in content:
            destination = "Paris, France"
        elif "tokyo" in content:
            destination = "Tokyo, Japan"
        elif "london" in content:
            destination = "London, UK"
        elif "new york" in content:
            destination = "New York, USA"
        
        # Extract duration
        duration = "5 days"  # Default
        if "3 days" in content or "3-day" in content:
            duration = "3 days"
        elif "7 days" in content or "week" in content:
            duration = "7 days"
        elif "10 days" in content:
            duration = "10 days"
        
        # Extract budget
        budget = None  # Default to None, will be validated later
        if "$1000" in content or "1000" in content:
            budget = "$1000"
        elif "$2000" in content or "2000" in content:
            budget = "$2000"
        elif "$3000" in content or "3000" in content:
            budget = "$3000"
        elif "$5000" in content or "5000" in content:
            budget = "$5000"
        elif "budget" in content and ("friendly" in content or "low" in content):
            budget = "budget-friendly"
        elif "luxury" in content:
            budget = "luxury"
        
        # Extract interests
        interests = ["sightseeing", "food", "culture"]  # Default
        if "adventure" in content:
            interests = ["adventure", "outdoor activities"]
        elif "beach" in content:
            interests = ["beach", "relaxation"]
        elif "history" in content:
            interests = ["history", "museums", "culture"]
        
        # Extract travel style
        travel_style = "comfortable"  # Default
        if "budget" in content:
            travel_style = "budget"
        elif "luxury" in content:
            travel_style = "luxury"
        elif "backpacking" in content:
            travel_style = "backpacking"
        
        # Extract accommodation preference
        accommodation_preference = "hotel"  # Default
        if "hostel" in content:
            accommodation_preference = "hostel"
        elif "airbnb" in content or "apartment" in content:
            accommodation_preference = "apartment"
        elif "resort" in content:
            accommodation_preference = "resort"
        
        # Extract travel dates
        travel_dates = None
        if "june" in content:
            travel_dates = "June 2024"
        elif "july" in content:
            travel_dates = "July 2024"
        elif "august" in content:
            travel_dates = "August 2024"
        elif "summer" in content:
            travel_dates = "summer 2024"
        elif "winter" in content:
            travel_dates = "winter 2024"
        elif "spring" in content:
            travel_dates = "spring 2024"
        elif "fall" in content or "autumn" in content:
            travel_dates = "fall 2024"
        elif "next month" in content:
            travel_dates = "next month"
        elif "march" in content:
            travel_dates = "March 2024"
        elif "april" in content:
            travel_dates = "April 2024"
        elif "may" in content:
            travel_dates = "May 2024"
        elif "september" in content:
            travel_dates = "September 2024"
        elif "october" in content:
            travel_dates = "October 2024"
        elif "november" in content:
            travel_dates = "November 2024"
        elif "december" in content:
            travel_dates = "December 2024"
        
        # Extract origin - look for specific origin indicators in user message
        origin = None
        if "flying from" in user_content or "departing from" in user_content or "leaving from" in user_content:
            # Extract origin from phrases like "flying from New York"
            if "sfo" in user_content or "san francisco" in user_content:
                origin = "SFO"
            elif "lax" in user_content or "los angeles" in user_content:
                origin = "LAX"
            elif "jfk" in user_content or "lga" in user_content or "new york" in user_content:
                origin = "NYC"
            elif "london" in user_content or "lhr" in user_content:
                origin = "London"
            elif "paris" in user_content or "cdg" in user_content:
                origin = "Paris"
            elif "tokyo" in user_content or "nrt" in user_content:
                origin = "Tokyo"
            elif "chicago" in user_content or "ord" in user_content:
                origin = "Chicago"
            elif "miami" in user_content or "mia" in user_content:
                origin = "Miami"
            elif "seattle" in user_content or "sea" in user_content:
                origin = "Seattle"
            elif "boston" in user_content or "bos" in user_content:
                origin = "Boston"
        elif "from" in user_content and ("sfo" in user_content or "san francisco" in user_content):
            origin = "SFO"
        elif "from" in user_content and ("lax" in user_content or "los angeles" in user_content):
            origin = "LAX"
        elif "from" in user_content and ("jfk" in user_content or "lga" in user_content or "new york" in user_content):
            origin = "NYC"
        elif "from" in user_content and ("london" in user_content or "lhr" in user_content):
            origin = "London"
        elif "from" in user_content and ("tokyo" in user_content or "nrt" in user_content):
            origin = "Tokyo"
        elif "from" in user_content and ("chicago" in user_content or "ord" in user_content):
            origin = "Chicago"
        elif "from" in user_content and ("miami" in user_content or "mia" in user_content):
            origin = "Miami"
        elif "from" in user_content and ("seattle" in user_content or "sea" in user_content):
            origin = "Seattle"
        elif "from" in user_content and ("boston" in user_content or "bos" in user_content):
            origin = "Boston"
        
        trip_spec = TripSpecification(
            destination=destination,
            duration=duration,
            budget=budget,
            interests=interests,
            travel_style=travel_style,
            accommodation_preference=accommodation_preference,
            travel_dates=travel_dates,
            origin=origin
        )
        
        state["trip_spec"] = trip_spec
        state["messages"].append(AIMessage(content=f"Parsed trip request: {trip_spec.destination} for {trip_spec.duration}"))
        
        return state
    
    def _research_destination(self, state: AgentState) -> AgentState:
        """Research the destination using the specialized destination agent"""
        trip_spec = state["trip_spec"]
        
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
        """
        
        # Use the destination research agent with feasibility checking
        destination_research = self.destination_agent.research_destination_with_feasibility(
            user_request=destination_request,
            check_feasibility=True,
            min_feasibility_score=0.6
        )
        
        # Check if dates, budget, or origin are required
        if (destination_research.date_required or 
            destination_research.budget_required or 
            destination_research.origin_required):
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
        
        # For demonstration, we'll use mock dates
        # In a real implementation, you'd parse dates from the trip specification
        departure_date = "2024-06-15"
        return_date = "2024-06-20"
        check_in = "2024-06-15"
        check_out = "2024-06-20"
        
        # Search flights
        flight_results = search_flights_real_api(
            origin="NYC",  # Default origin
            destination=trip_spec.destination,
            departure_date=departure_date,
            return_date=return_date,
            passengers=1
        )
        
        # Search hotels
        hotel_results = search_hotels_real_api(
            destination=trip_spec.destination,
            check_in=check_in,
            check_out=check_out,
            guests=1,
            rooms=1
        )
        
        state["flight_options"] = [{"results": flight_results}]
        state["hotel_options"] = [{"results": hotel_results}]
        
        state["messages"].append(AIMessage(content=f"Found travel options for {trip_spec.destination}"))
        
        return state
    
    def _create_itinerary(self, state: AgentState) -> AgentState:
        """Create a detailed day-by-day itinerary"""
        trip_spec = state["trip_spec"]
        
        # Get travel options
        flight_options = state.get("flight_options", [])
        hotel_options = state.get("hotel_options", [])
        
        # Build travel options summary
        travel_summary = ""
        if flight_options:
            travel_summary += f"\nFlight Options:\n{flight_options[0].get('results', 'No flights found')}\n"
        if hotel_options:
            travel_summary += f"\nHotel Options:\n{hotel_options[0].get('results', 'No hotels found')}\n"
        
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
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
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
