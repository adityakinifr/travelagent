# Travel Agent - Itinerary Creator

A simple LangGraph agent that takes user trip specifications and creates detailed travel itineraries using OpenAI's GPT models.

## Features

- **Structured Trip Planning**: Parses natural language trip requests into structured data
- **Multi-step Workflow**: Uses LangGraph to create a sophisticated planning pipeline
- **Destination Research**: Researches destinations and provides relevant information
- **Detailed Itineraries**: Creates day-by-day itineraries with activities, meals, and costs
- **Budget-Aware**: Considers budget constraints in itinerary planning
- **Flexible Input**: Accepts natural language trip descriptions
- **Real Travel Data**: Integrates with flight, hotel, and car rental search tools
- **Multi-Provider Search**: Searches multiple travel providers for best options

## Architecture

The agent uses a LangGraph workflow with the following nodes:

1. **Parse Request**: Extracts structured information from natural language input
2. **Research Destination**: Gathers relevant information about the destination
3. **Search Travel Options**: Searches for flights, hotels, and car rentals
4. **Create Itinerary**: Generates a detailed day-by-day itinerary with travel options
5. **Refine Itinerary**: Reviews and improves the itinerary

## Travel Tools

The agent includes integrated tools for searching travel options:

### Flight Search
- **Google Flights**: Searches multiple airlines and routes
- **Skyscanner**: Alternative flight search provider
- **Features**: Price comparison, stop information, duration, airline details

### Hotel Search
- **Booking.com**: Comprehensive hotel search
- **Expedia**: Alternative hotel provider
- **Features**: Price per night, ratings, amenities, location details

### Car Rental Search
- **Hertz**: Premium car rental options
- **Avis**: Alternative car rental provider
- **Features**: Car types, pricing, features, pickup locations

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:

```bash
# Copy the example environment file
cp env_example.txt .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

### Basic Usage

```python
from travel_agent import TravelAgent

# Initialize the agent
agent = TravelAgent()

# Create an itinerary
trip_request = """
I want to plan a 5-day trip to Paris, France.
My budget is around $2000.
I'm interested in art, history, and French cuisine.
I prefer comfortable travel and would like to stay in a nice hotel.
"""

result = agent.create_itinerary(trip_request)
print(result["itinerary"])
```

### Running Examples

```bash
# Run predefined examples
python example_usage.py

# Run in interactive mode
python example_usage.py interactive
```

### Testing Travel Tools

```bash
# Test all travel tools
python test_tools.py

# Test individual components
python test_tools.py tools      # Test travel tools only
python test_tools.py agent      # Test agent with tools
python test_tools.py functions  # Test individual tool functions
```

### Running the Main Script

```bash
python travel_agent.py
```

## Example Trip Requests

The agent can handle various types of trip requests:

### City Break
```
I want to plan a 4-day trip to Rome, Italy.
My budget is around $1500.
I'm interested in ancient history, art, and Italian food.
I prefer mid-range accommodation.
```

### Adventure Trip
```
I want to plan a 7-day adventure trip to Costa Rica.
My budget is around $3000.
I'm interested in hiking, wildlife, beaches, and adventure activities.
I prefer eco-lodges and want to experience nature.
```

### Budget Backpacking
```
I want to plan a 10-day backpacking trip to Thailand.
My budget is around $800.
I'm interested in temples, street food, and meeting other travelers.
I prefer hostels and budget accommodations.
```

## Data Models

### TripSpecification
- `destination`: Where to travel
- `duration`: Trip length
- `budget`: Budget range
- `interests`: List of interests (sightseeing, food, adventure, etc.)
- `travel_style`: Travel style preference
- `accommodation_preference`: Type of accommodation

### ItineraryDay
- `day`: Day number
- `date`: Date or day label
- `activities`: List of activities
- `meals`: Meal recommendations
- `accommodation`: Accommodation details
- `estimated_cost`: Daily cost estimate

### TripItinerary
- `destination`: Trip destination
- `duration`: Trip duration
- `total_estimated_cost`: Total cost estimate
- `days`: List of ItineraryDay objects

## Customization

### Using Different Models

```python
# Use GPT-4 instead of GPT-4o-mini
agent = TravelAgent(model_name="gpt-4")
```

### Extending the Workflow

You can extend the LangGraph workflow by adding new nodes:

```python
def custom_node(state: AgentState) -> AgentState:
    # Your custom logic here
    return state

# Add to workflow
workflow.add_node("custom_node", custom_node)
workflow.add_edge("create_itinerary", "custom_node")
workflow.add_edge("custom_node", "refine_itinerary")
```

## Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for API calls

## Dependencies

- `langgraph`: For building the agent workflow
- `langchain`: Core LangChain functionality
- `langchain-openai`: OpenAI integration
- `langchain-core`: Core LangChain components
- `python-dotenv`: Environment variable management
- `pydantic`: Data validation and settings
- `requests`: HTTP requests for API calls
- `beautifulsoup4`: Web scraping functionality
- `selenium`: Browser automation for dynamic content
- `webdriver-manager`: Automatic driver management

## Limitations

- Requires OpenAI API key and internet connection
- Itinerary quality depends on the AI model's knowledge
- Travel tools currently use mock data (can be extended with real APIs)
- Basic parsing of natural language input
- Chrome browser required for Selenium-based scraping

## Future Enhancements

- Integration with real-time travel APIs (Amadeus, Skyscanner API, etc.)
- More sophisticated natural language parsing
- Support for multi-city trips
- Integration with booking systems
- Weather and seasonal considerations
- User preference learning
- Real-time price monitoring
- Integration with travel insurance providers
- Support for group bookings
- Mobile app development

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.
