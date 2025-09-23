"""
LangGraph Travel Agent for creating trip itineraries
"""

import os
from typing import Dict, List, TypedDict, Annotated
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from pydantic import BaseModel
from real_travel_apis import search_flights_real_api, search_hotels_real_api, search_car_rentals_real_api

# Load environment variables
load_dotenv()

class TripSpecification(BaseModel):
    """Structure for trip specifications"""
    destination: str
    duration: str
    budget: str
    interests: List[str]
    travel_style: str
    accommodation_preference: str

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
    itinerary: TripItinerary
    flight_options: List[Dict]
    hotel_options: List[Dict]
    car_rental_options: List[Dict]

class TravelAgent:
    """LangGraph Travel Agent for creating trip itineraries"""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """Initialize the travel agent with OpenAI model"""
        self.llm = ChatOpenAI(model=model_name, temperature=0.7)
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
        
        @tool
        def search_car_rentals(pickup_location: str, pickup_date: str, return_date: str,
                              pickup_time: str = "10:00", return_time: str = "10:00") -> str:
            """Search for car rentals from multiple providers using real APIs"""
            return search_car_rentals_real_api(pickup_location, pickup_date, return_date,
                                             pickup_time, return_time)
        
        return [search_flights, search_hotels, search_car_rentals]
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("parse_request", self._parse_request)
        workflow.add_node("research_destination", self._research_destination)
        workflow.add_node("search_travel_options", self._search_travel_options)
        workflow.add_node("create_itinerary", self._create_itinerary)
        workflow.add_node("refine_itinerary", self._refine_itinerary)
        
        # Add edges
        workflow.set_entry_point("parse_request")
        workflow.add_edge("parse_request", "research_destination")
        workflow.add_edge("research_destination", "search_travel_options")
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
        
        If any information is missing, make reasonable assumptions based on the context.
        Return the information in a structured format.
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        # Parse the response to create TripSpecification
        # For simplicity, we'll create a basic structure
        # In a real implementation, you'd use more sophisticated parsing
        trip_spec = TripSpecification(
            destination="Paris, France",  # Default example
            duration="5 days",
            budget="$2000",
            interests=["sightseeing", "food", "culture"],
            travel_style="comfortable",
            accommodation_preference="hotel"
        )
        
        state["trip_spec"] = trip_spec
        state["messages"].append(AIMessage(content=f"Parsed trip request: {trip_spec.destination} for {trip_spec.duration}"))
        
        return state
    
    def _research_destination(self, state: AgentState) -> AgentState:
        """Research the destination and gather relevant information"""
        trip_spec = state["trip_spec"]
        
        prompt = f"""
        Research the destination: {trip_spec.destination}
        
        Provide information about:
        1. Best time to visit
        2. Top attractions and landmarks
        3. Local cuisine and restaurants
        4. Transportation options
        5. Cultural highlights
        6. Budget considerations
        
        Focus on information relevant to a {trip_spec.duration} trip with interests in: {', '.join(trip_spec.interests)}
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        state["messages"].append(AIMessage(content=f"Research completed for {trip_spec.destination}"))
        
        return state
    
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
        
        # Search car rentals
        car_rental_results = search_car_rentals_real_api(
            pickup_location=trip_spec.destination,
            pickup_date=departure_date,
            return_date=return_date
        )
        
        state["flight_options"] = [{"results": flight_results}]
        state["hotel_options"] = [{"results": hotel_results}]
        state["car_rental_options"] = [{"results": car_rental_results}]
        
        state["messages"].append(AIMessage(content=f"Found travel options for {trip_spec.destination}"))
        
        return state
    
    def _create_itinerary(self, state: AgentState) -> AgentState:
        """Create a detailed day-by-day itinerary"""
        trip_spec = state["trip_spec"]
        
        # Get travel options
        flight_options = state.get("flight_options", [])
        hotel_options = state.get("hotel_options", [])
        car_rental_options = state.get("car_rental_options", [])
        
        # Build travel options summary
        travel_summary = ""
        if flight_options:
            travel_summary += f"\nFlight Options:\n{flight_options[0].get('results', 'No flights found')}\n"
        if hotel_options:
            travel_summary += f"\nHotel Options:\n{hotel_options[0].get('results', 'No hotels found')}\n"
        if car_rental_options:
            travel_summary += f"\nCar Rental Options:\n{car_rental_options[0].get('results', 'No car rentals found')}\n"
        
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
        7. Recommended flights, hotels, and car rentals from the options above
        
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
            "itinerary": None,
            "flight_options": [],
            "hotel_options": [],
            "car_rental_options": []
        }
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        return {
            "trip_specification": final_state["trip_spec"],
            "itinerary": final_state["itinerary"],
            "flight_options": final_state.get("flight_options", []),
            "hotel_options": final_state.get("hotel_options", []),
            "car_rental_options": final_state.get("car_rental_options", []),
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
