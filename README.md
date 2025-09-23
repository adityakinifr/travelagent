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

### Workflow Diagram

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Parse Request │───▶│ Research         │───▶│ Search Travel       │
│                 │    │ Destination      │    │ Options             │
│ • Extract trip  │    │                  │    │                     │
│   details       │    │ • Best time to   │    │ • Amadeus API       │
│ • Structure     │    │   visit          │    │ • SerpAPI           │
│   data          │    │ • Attractions    │    │ • FlightsAPI.io     │
│ • Validate      │    │ • Local cuisine  │    │ • Real-time data    │
└─────────────────┘    │ • Transportation │    │ • Price comparison  │
                       │ • Culture        │    └─────────────────────┘
                       └──────────────────┘              │
                                                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Refine        │◀───│ Create           │◀───│ Travel Options      │
│   Itinerary     │    │ Itinerary        │    │ Results             │
│                 │    │                  │    │                     │
│ • Review flow   │    │ • Day-by-day     │    │ • Flight options    │
│ • Check timing  │    │   activities     │    │ • Hotel options     │
│ • Add tips      │    │ • Meal plans     │    │ • Car rental        │
│ • Final polish  │    │ • Transportation │    │   options           │
│                 │    │ • Cost estimates │    │ • Integrated into   │
└─────────────────┘    │ • Travel options │    │   recommendations   │
                       └──────────────────┘    └─────────────────────┘
```

### Data Flow

```
User Input → Parse → Research → Search APIs → Create → Refine → Final Itinerary
    │           │        │         │          │        │
    ▼           ▼        ▼         ▼          ▼        ▼
Natural    Structured  Destination  Real      Detailed  Polished
Language   Trip Data   Information  Travel    Itinerary Itinerary
Request               & Context     Options   with Data
```

## Travel Tools

The agent includes integrated tools for searching real travel options:

### Flight Search APIs
- **Amadeus API**: Comprehensive flight search with real-time data
- **SerpAPI (Google Flights)**: Access to Google Flights data
- **FlightsAPI.io**: Alternative flight search provider
- **Features**: Real-time prices, schedules, airline details, stop information

### Hotel Search APIs
- **Amadeus API**: Real-time hotel availability and pricing
- **Features**: Live rates, availability, amenities, ratings, location details

### Car Rental Search APIs
- **Amadeus API**: Real-time car rental options
- **Features**: Live availability, pricing, vehicle types, pickup locations

### API Configuration
The system supports multiple API providers with automatic fallback:
1. **Primary**: Amadeus API (recommended - covers all travel types)
   - **Uses TEST environment by default** (not production)
   - Safe for development and testing
2. **Fallback**: SerpAPI for flights if Amadeus unavailable
3. **Fallback**: FlightsAPI.io for additional flight options

### API Integration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Travel Agent Core                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Flights   │  │   Hotels    │  │ Car Rentals │            │
│  │   Search    │  │   Search    │  │   Search    │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
           │                │                │
           ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Layer                                    │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │   Amadeus   │    │   SerpAPI   │    │ FlightsAPI  │        │
│  │     API     │    │ (Google     │    │     .io     │        │
│  │             │    │  Flights)   │    │             │        │
│  │ • Flights   │    │             │    │             │        │
│  │ • Hotels    │    │ • Flights   │    │ • Flights   │        │
│  │ • Cars      │    │ • Real-time │    │ • Global    │        │
│  │ • Test env  │    │ • Google    │    │ • 500+      │        │
│  │             │    │   data      │    │   airlines  │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│           │                │                │                  │
│           ▼                ▼                ▼                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Automatic Fallback System                  │  │
│  │  • Try Amadeus first (comprehensive)                   │  │
│  │  • Fallback to SerpAPI if needed                       │  │
│  │  │  • Fallback to FlightsAPI.io if needed              │  │
│  │  • Sort results by price                               │  │
│  │  • Return top 10 options                               │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your API keys:

```bash
# Copy the example environment file
cp env_example.txt .env

# Edit .env and add your API keys
OPENAI_API_KEY=your_openai_api_key_here

# Travel APIs (at least one required for real data)
# Note: Amadeus uses TEST environment by default (not production)
AMADEUS_API_KEY=your_amadeus_test_api_key_here
AMADEUS_API_SECRET=your_amadeus_test_api_secret_here
SERPAPI_KEY=your_serpapi_key_here
FLIGHTSAPI_KEY=your_flightsapi_key_here
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
# Test real APIs
python test_real_apis.py

# Test individual components
python test_real_apis.py apis      # Test real APIs only
python test_real_apis.py agent     # Test agent with real APIs
python test_real_apis.py functions # Test individual API functions
python test_real_apis.py setup     # Show API setup instructions

# Test mock data (legacy)
python test_tools.py
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
- `amadeus`: Official Amadeus API client
- `google-search-results`: SerpAPI client for Google Flights

## Limitations

- Requires OpenAI API key and internet connection
- Requires at least one travel API key for real data
- Itinerary quality depends on the AI model's knowledge
- API rate limits may apply (especially for free tiers)
- Basic parsing of natural language input
- Some APIs may have geographic restrictions

## Future Enhancements

- Integration with additional travel APIs (Skyscanner API, Booking.com API, etc.)
- More sophisticated natural language parsing
- Support for multi-city trips
- Integration with booking systems
- Weather and seasonal considerations
- User preference learning
- Real-time price monitoring and alerts
- Integration with travel insurance providers
- Support for group bookings
- Mobile app development
- Caching for improved performance
- Advanced filtering and sorting options

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.
