"""
Example usage of the Travel Agent
"""

import os
from travel_agent import TravelAgent

def run_examples():
    """Run example trip requests"""
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY environment variable")
        print("You can copy env_example.txt to .env and add your key")
        return
    
    # Initialize the agent
    agent = TravelAgent()
    
    # Example 1: European city trip
    print("="*60)
    print("EXAMPLE 1: European City Trip")
    print("="*60)
    
    trip_request_1 = """
    I want to plan a 4-day trip to Rome, Italy.
    My budget is around $1500.
    I'm interested in ancient history, art, and Italian food.
    I prefer mid-range accommodation and want to experience local culture.
    """
    
    result_1 = agent.create_itinerary(trip_request_1)
    print_itinerary(result_1)
    
    # Example 2: Adventure trip
    print("\n" + "="*60)
    print("EXAMPLE 2: Adventure Trip")
    print("="*60)
    

def print_itinerary(result):
    """Print the itinerary in a formatted way"""
    if not result["itinerary"]:
        print("No itinerary generated")
        return
    
    itinerary = result["itinerary"]
    print(f"\nDestination: {itinerary.destination}")
    print(f"Duration: {itinerary.duration}")
    print(f"Total Estimated Cost: {itinerary.total_estimated_cost}")
    print("\nDaily Itinerary:")
    
    for day in itinerary.days:
        print(f"\n{day.date}:")
        print(f"  Activities: {', '.join(day.activities)}")
        print(f"  Meals: {', '.join(day.meals)}")
        print(f"  Accommodation: {day.accommodation}")
        print(f"  Estimated Cost: {day.estimated_cost}")

def interactive_mode():
    """Run the agent in interactive mode"""
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY environment variable")
        print("You can copy env_example.txt to .env and add your key")
        return
    
    agent = TravelAgent()
    
    print("Welcome to the Travel Agent!")
    print("Describe your dream trip and I'll create an itinerary for you.")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("Describe your trip: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        print("\nCreating your itinerary...")
        result = agent.create_itinerary(user_input)
        print_itinerary(result)
        print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_mode()
    else:
        run_examples()
