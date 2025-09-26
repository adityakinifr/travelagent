#!/usr/bin/env python3
"""
Flask backend for the AI Travel Agent UI
"""

import os
import json
import asyncio
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from dotenv import load_dotenv
import threading
import time

# Import our travel agent components
from travel_agent import TravelAgent
from destination_agent import DestinationResearchAgent, DestinationRequest
from preferences_manager import PreferencesManager

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Global variables for managing planning sessions
planning_sessions = {}

class PlanningSession:
    def __init__(self, session_id, request_data):
        self.session_id = session_id
        self.request_data = request_data
        self.travel_agent = TravelAgent()
        self.current_step = 0
        self.is_complete = False
        self.results = None
        self.error = None
        self.user_input_required = None
        self.destination_choice_required = None

    def _extract_flight_data(self, flight_options):
        """Extract flight data from the complex flight_options structure"""
        flights = []
        for option in flight_options:
            if isinstance(option, dict) and 'results' in option:
                # For now, return a simplified representation since results is a string
                flights.append({
                    'airline': 'Multiple options available',
                    'price': 'See details',
                    'duration': 'Various',
                    'details': option['results']
                })
            else:
                # Handle unexpected format
                flights.append({
                    'airline': 'Unknown',
                    'price': 'Unknown',
                    'duration': 'Unknown',
                    'details': str(option)
                })
        return flights

    def _extract_hotel_data(self, hotel_options):
        """Extract hotel data from the complex hotel_options structure"""
        hotels = []
        for option in hotel_options:
            if isinstance(option, dict) and 'results' in option:
                # For now, return a simplified representation since results is a string
                hotels.append({
                    'name': 'Multiple hotels available',
                    'price': 'See details',
                    'rating': 'Various',
                    'details': option['results']
                })
            else:
                # Handle unexpected format
                hotels.append({
                    'name': 'Unknown',
                    'price': 'Unknown',
                    'rating': 'Unknown',
                    'details': str(option)
                })
        return hotels

    async def execute_planning(self):
        """Execute the travel planning process"""
        try:
            print(f"\n🚀 WEB UI: Starting travel planning session {self.session_id}")
            print(f"   📝 Request data: {self.request_data}")
            print(f"   🔧 Initializing travel agent...")
            
            # Step 1: Analyze request
            self.current_step = 1
            print(f"   📊 Step 1: Analyzing travel request...")
            yield {
                'type': 'step',
                'step': 1,
                'message': 'Analyzing your travel request...',
                'details': f"Processing: {self.request_data.get('destination_query', 'No query provided')}",
                'substeps': [
                    'Parsing destination query',
                    'Extracting travel parameters',
                    'Validating required fields',
                    'Preparing destination research request'
                ]
            }

            # Create destination request
            print(f"\n🚀 WEB UI: Processing user request...")
            print(f"   📝 Raw request data: {self.request_data}")
            
            group_size = self.request_data.get('group_size', '')
            if group_size and group_size.isdigit():
                group_size = int(group_size)
            else:
                group_size = None
                
            print(f"   🔧 Parsing request parameters...")
            print(f"      Query: {self.request_data.get('destination_query', '')}")
            print(f"      Origin: {self.request_data.get('origin', '')}")
            print(f"      Dates: {self.request_data.get('travel_dates', '')}")
            print(f"      Budget: {self.request_data.get('budget', '')}")
            print(f"      Traveler type: {self.request_data.get('traveler_type', '')}")
            print(f"      Group size: {group_size}")
                
            destination_request = DestinationRequest(
                query=self.request_data.get('destination_query', ''),
                origin_location=self.request_data.get('origin', ''),
                max_travel_time=None,  # Will be extracted from query if present
                travel_dates=self.request_data.get('travel_dates', ''),
                budget=self.request_data.get('budget', ''),
                interests=[],  # Will be extracted from query
                travel_style=None,
                traveler_type=self.request_data.get('traveler_type', ''),
                group_size=group_size,
                age_range=None,
                mobility_requirements=None,
                seasonal_preferences=None
            )
            
            print(f"   ✅ Destination request created: {destination_request}")

            # Check if budget needs default
            if not self.request_data.get('budget', '').strip():
                yield {
                    'type': 'progress_update',
                    'message': 'No budget specified, using luxury as default',
                    'details': 'Setting budget to luxury for premium travel options'
                }

            # Step 2: Research destinations
            self.current_step = 2
            yield {
                'type': 'step',
                'step': 2,
                'message': 'Starting destination research...',
                'details': f"Analyzing request: {destination_request.query}",
                'substeps': [
                    'Initializing destination research agent',
                    'Setting up web search parameters',
                    'Preparing image search algorithms',
                    'Configuring feasibility checking'
                ]
            }

            # Show detailed research progress
            yield {
                'type': 'progress_update',
                'message': '🔍 Starting comprehensive destination research...',
                'details': 'Initializing search algorithms and preference matching'
            }

            yield {
                'type': 'progress_update',
                'message': '🧠 Parsing request with intelligent LLM...',
                'details': 'Extracting structured information from your request'
            }

            yield {
                'type': 'progress_update',
                'message': '✈️ Looking up airport codes...',
                'details': 'Finding nearest airports for destination and origin'
            }

            yield {
                'type': 'progress_update',
                'message': '🌐 Performing web search for destination options...',
                'details': 'Searching travel websites, blogs, and destination databases'
            }

            yield {
                'type': 'progress_update',
                'message': '📸 Searching for destination images...',
                'details': 'Finding beautiful photos to showcase each destination'
            }

            yield {
                'type': 'progress_update',
                'message': '🧠 Analyzing destinations with AI...',
                'details': 'Using LLM to evaluate and rank destinations'
            }

            yield {
                'type': 'progress_update',
                'message': '🔍 Checking feasibility of destinations...',
                'details': 'Validating flights, hotels, and budget constraints'
            }

            yield {
                'type': 'progress_update',
                'message': '📊 Scoring and ranking destinations...',
                'details': 'Applying feasibility scores and user preferences'
            }

            # Research destinations
            print(f"\n🚀 WEB UI: Starting destination research...")
            print(f"   📋 Request: {destination_request}")
            print(f"   🔍 Calling destination research agent...")
            
            # Convert DestinationRequest object to string for the research method
            destination_request_str = f"""
            Destination: {destination_request.query}
            Origin: {destination_request.origin_location or 'Not specified'}
            Travel Dates: {destination_request.travel_dates or 'Not specified'}
            Budget: {destination_request.budget or 'Not specified'}
            Interests: {destination_request.interests or []}
            Travel Style: {destination_request.travel_style or 'Not specified'}
            Traveler Type: {destination_request.traveler_type or 'Not specified'}
            Group Size: {destination_request.group_size or 'Not specified'}
            Max Travel Time: {destination_request.max_travel_time or 'Not specified'}
            """
            
            destination_progress_updates = []

            def handle_destination_progress(update):
                destination_progress_updates.append(update)

            destination_research = self.travel_agent.destination_agent.research_destination_with_feasibility(
                destination_request_str,
                progress_callback=handle_destination_progress
            )

            print(f"   ✅ Destination research completed!")
            print(f"   📊 Results: {len(destination_research.primary_destinations) if destination_research.primary_destinations else 0} primary, {len(destination_research.alternative_destinations) if destination_research.alternative_destinations else 0} alternative destinations")

            for update in destination_progress_updates:
                yield update

            # Show results found
            num_destinations = len(destination_research.primary_destinations) if destination_research.primary_destinations else 0
            yield {
                'type': 'progress_update',
                'message': f'Found {num_destinations} destination options',
                'details': f'Evaluating destinations based on your criteria'
            }

            if destination_research.primary_destinations:
                destination_names = [dest.name for dest in destination_research.primary_destinations[:3]]
                yield {
                    'type': 'progress_update',
                    'message': f'Top destinations: {", ".join(destination_names)}',
                    'details': 'Checking feasibility and pricing for each option'
                }

            # Check if user input is required
            if destination_research.date_required:
                self.user_input_required = {
                    'message': 'Travel dates are required to proceed with destination research and feasibility checking.',
                    'required_fields': ['travel_dates']
                }
                yield {
                    'type': 'user_input_required',
                    **self.user_input_required
                }
                return

            if destination_research.budget_required:
                self.user_input_required = {
                    'message': 'Budget is required to proceed with destination research and feasibility checking.',
                    'required_fields': ['budget']
                }
                yield {
                    'type': 'user_input_required',
                    **self.user_input_required
                }
                return

            if destination_research.origin_required:
                self.user_input_required = {
                    'message': 'Origin location is required to proceed with destination research and feasibility checking.',
                    'required_fields': ['origin']
                }
                yield {
                    'type': 'user_input_required',
                    **self.user_input_required
                }
                return

            # Check if destination choice is required
            if destination_research.user_choice_required and len(destination_research.primary_destinations) > 1:
                self.destination_choice_required = {
                    'destinations': [
                        {
                            'name': dest.name,
                            'country': dest.country,
                            'description': dest.description,
                            'best_time_to_visit': dest.best_time_to_visit,
                            'family_friendly_score': dest.family_friendly_score,
                            'safety_rating': dest.safety_rating
                        }
                        for dest in destination_research.primary_destinations
                    ]
                }
                yield {
                    'type': 'destination_choice',
                    **self.destination_choice_required
                }
                return

            # Step 3: Check feasibility
            self.current_step = 3
            selected_destination = destination_research.primary_destinations[0].name if destination_research.primary_destinations else self.request_data.get('destination_query', '')
            yield {
                'type': 'step',
                'step': 3,
                'message': 'Checking feasibility and finding travel options...',
                'details': f"Validating travel feasibility for: {selected_destination}",
                'substeps': [
                    'Checking flight availability and pricing',
                    'Validating budget constraints',
                    'Assessing accommodation options',
                    'Evaluating travel time and logistics'
                ]
            }

            # Step 4: Search travel options
            self.current_step = 4
            yield {
                'type': 'step',
                'step': 4,
                'message': 'Searching for flights and hotels...',
                'details': f"Finding best travel options for: {selected_destination}",
                'substeps': [
                    'Searching flight options with Amadeus API',
                    'Finding hotel accommodations',
                    'Comparing prices and availability',
                    'Applying user preferences and filters'
                ]
            }

            # Create trip specification
            from travel_agent import TripSpecification
            trip_spec = TripSpecification(
                destination=destination_research.primary_destinations[0].name if destination_research.primary_destinations else self.request_data.get('destination_query', ''),
                duration="7 days",  # Default duration
                budget=self.request_data.get('budget', ''),
                interests=[],
                travel_style="comfortable",
                accommodation_preference="hotel",
                travel_dates=self.request_data.get('travel_dates', ''),
                origin=self.request_data.get('origin', '')
            )

            # Show detailed travel options search progress
            yield {
                'type': 'progress_update',
                'message': '🔍 Starting travel options search...',
                'details': f'Preparing to search flights and hotels for {trip_spec.destination}'
            }

            yield {
                'type': 'progress_update',
                'message': '✈️ Searching for flight options...',
                'details': f'Checking flights from {trip_spec.origin} to {trip_spec.destination}'
            }

            yield {
                'type': 'progress_update',
                'message': '🏨 Searching for hotel options...',
                'details': f'Finding accommodations in {trip_spec.destination}'
            }

            yield {
                'type': 'progress_update',
                'message': '💰 Analyzing pricing and availability...',
                'details': 'Comparing costs and checking budget constraints'
            }

            # Search travel options
            print(f"\n🚀 WEB UI: Starting travel options search...")
            print(f"   🎯 Destination: {trip_spec.destination}")
            print(f"   ✈️ Origin: {trip_spec.origin}")
            print(f"   📅 Dates: {trip_spec.travel_dates}")
            print(f"   💰 Budget: {trip_spec.budget}")
            
            travel_options = self.travel_agent._search_travel_options({
                'trip_spec': trip_spec,
                'destination_research': destination_research
            })
            
            print(f"   ✅ Travel options search completed!")
            print(f"   📊 Results: {travel_options}")

            # Show flight results
            num_flights = len(travel_options.get('flight_options', []))
            yield {
                'type': 'progress_update',
                'message': f'Found {num_flights} flight options',
                'details': 'Comparing prices and schedules'
            }

            # Show hotel search progress
            yield {
                'type': 'progress_update',
                'message': 'Searching for hotel accommodations...',
                'details': f'Finding hotels in {trip_spec.destination}'
            }

            # Show hotel results
            num_hotels = len(travel_options.get('hotel_options', []))
            yield {
                'type': 'progress_update',
                'message': f'Found {num_hotels} hotel options',
                'details': 'Evaluating amenities and pricing'
            }

            # Step 5: Create itinerary
            self.current_step = 5
            yield {
                'type': 'step',
                'step': 5,
                'message': 'Creating your personalized itinerary...',
                'details': f"Generating detailed itinerary for: {selected_destination}",
                'substeps': [
                    'Analyzing travel options and preferences',
                    'Creating day-by-day activity schedule',
                    'Optimizing timing and logistics',
                    'Adding personalized recommendations',
                    'Finalizing itinerary details'
                ]
            }

            # Show itinerary creation progress
            yield {
                'type': 'progress_update',
                'message': 'Analyzing your preferences and travel options...',
                'details': 'Personalizing recommendations based on your profile'
            }

            # Create itinerary
            print(f"\n🚀 WEB UI: Creating personalized itinerary...")
            print(f"   🎯 Destination: {selected_destination}")
            print(f"   📅 Duration: {trip_spec.duration}")
            print(f"   💰 Budget: {trip_spec.budget}")
            print(f"   🎨 Interests: {trip_spec.interests}")
            
            itinerary = self.travel_agent._create_itinerary({
                'trip_spec': trip_spec,
                'travel_options': travel_options,
                'destination_research': destination_research
            })

            # Show itinerary completion
            yield {
                'type': 'progress_update',
                'message': 'Itinerary created successfully!',
                'details': 'Finalizing your personalized travel plan'
            }

            # Store results
            self.results = {
                'destination': trip_spec.destination,
                'duration': trip_spec.duration,
                'summary': itinerary.summary,
                'flights': self._extract_flight_data(travel_options.get('flight_options', [])),
                'hotels': self._extract_hotel_data(travel_options.get('hotel_options', []))
            }

            self.is_complete = True
            yield {
                'type': 'results',
                'results': self.results
            }

        except Exception as e:
            self.error = str(e)
            yield {
                'type': 'error',
                'message': f'An error occurred: {str(e)}'
            }

@app.route('/api/preferences', methods=['GET'])
def get_preferences():
    """Get user preferences"""
    try:
        # Load preferences from file if it exists
        if os.path.exists('travel_preferences.json'):
            with open('travel_preferences.json', 'r') as f:
                preferences = json.load(f)
        else:
            # Return default preferences
            preferences = {
                "traveler_profile": {
                    "home_airport": "SFO",
                    "preferred_airlines": ["United", "American", "Delta"],
                    "frequent_flyer_programs": ["United MileagePlus", "American AAdvantage"],
                    "travel_style": "comfortable",
                    "group_size": 2,
                    "age_range": "middle_aged"
                },
                "hotel_preferences": {
                    "preferred_chains": ["Marriott", "Hilton", "Hyatt"],
                    "loyalty_programs": ["Marriott Bonvoy", "Hilton Honors"],
                    "room_preferences": ["king_bed", "ocean_view", "high_floor"],
                    "amenities": ["wifi", "gym", "pool", "spa"]
                },
                "flight_preferences": {
                    "preferred_airlines": ["United", "American", "Delta"],
                    "class_preference": "economy",
                    "seat_preferences": ["window", "aisle", "exit_row"],
                    "red_eye_preference": False,
                    "layover_preference": "minimal"
                },
                "budget_preferences": {
                    "budget_level": "moderate",
                    "currency": "USD",
                    "spending_style": "balanced"
                },
                "activity_preferences": {
                    "outdoor_activities": ["hiking", "beach", "sightseeing"],
                    "indoor_activities": ["museums", "shopping", "dining"],
                    "adventure_level": "moderate"
                },
                "special_requirements": {
                    "dietary_restrictions": [],
                    "accessibility_needs": [],
                    "mobility_requirements": "any"
                }
            }
        return jsonify(preferences)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/preferences', methods=['POST'])
def save_preferences():
    """Save user preferences"""
    try:
        preferences = request.json
        # Save preferences to file
        with open('travel_preferences.json', 'w') as f:
            json.dump(preferences, f, indent=2)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/plan-trip', methods=['POST'])
def plan_trip():
    """Start travel planning process"""
    try:
        request_data = request.json
        session_id = f"session_{int(time.time())}"
        
        print(f"\n🌐 API: Received travel planning request")
        print(f"   📝 Request data: {request_data}")
        print(f"   🆔 Session ID: {session_id}")
        print(f"   🔧 Creating planning session...")
        
        # Create planning session
        session = PlanningSession(session_id, request_data)
        planning_sessions[session_id] = session
        
        print(f"   ✅ Planning session created and stored")

        def generate():
            try:
                print(f"   🚀 Starting SSE stream generation...")
                # Create a new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                print(f"   🔄 Event loop created, starting planning execution...")
                
                # Run the async generator
                async def run_planning():
                    print(f"   📡 Starting async planning execution...")
                    async for update in session.execute_planning():
                        print(f"   📤 Yielding update: {update.get('type', 'unknown')}")
                        yield update
                
                # Collect all updates from the async generator
                async def collect_updates():
                    print(f"   📥 Collecting all updates...")
                    updates = []
                    async for update in run_planning():
                        updates.append(update)
                        print(f"   📥 Collected update: {update.get('type', 'unknown')}")
                    print(f"   ✅ Collected {len(updates)} total updates")
                    return updates
                
                # Run the async function and yield results
                print(f"   🔄 Running async planning execution...")
                updates = loop.run_until_complete(collect_updates())
                print(f"   ✅ Planning execution completed, yielding {len(updates)} updates")
                for update in updates:
                    yield f"data: {json.dumps(update)}\n\n"
                    
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            finally:
                if 'loop' in locals():
                    loop.close()

        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Cache-Control'
            }
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user-input', methods=['POST'])
def handle_user_input():
    """Handle user input for missing information"""
    try:
        input_data = request.json
        # Update the request data with user input
        # This would typically update the planning session
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/destination-choice', methods=['POST'])
def handle_destination_choice():
    """Handle user destination choice"""
    try:
        choice_data = request.json
        # Update the planning session with the chosen destination
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    """Serve the main HTML page"""
    try:
        with open('index.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "HTML file not found. Please ensure index.html exists in the current directory.", 404

@app.route('/preferences.html')
def preferences():
    """Serve the preferences HTML page"""
    try:
        with open('preferences.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Preferences page not found. Please ensure preferences.html exists in the current directory.", 404

@app.route('/app.js')
def app_js():
    """Serve the JavaScript file"""
    try:
        with open('app.js', 'r') as f:
            return f.read(), 200, {'Content-Type': 'application/javascript'}
    except FileNotFoundError:
        return "JavaScript file not found. Please ensure app.js exists in the current directory.", 404

@app.route('/preferences.js')
def preferences_js():
    """Serve the preferences JavaScript file"""
    try:
        with open('preferences.js', 'r') as f:
            return f.read(), 200, {'Content-Type': 'application/javascript'}
    except FileNotFoundError:
        return "Preferences JavaScript file not found. Please ensure preferences.js exists in the current directory.", 404

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'version': '1.0.0'})

if __name__ == '__main__':
    # Check if required environment variables are set
    required_vars = ['OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file")
        exit(1)
    
    print("🚀 Starting AI Travel Agent Server...")
    print("📱 Open http://localhost:8080 in your browser")
    
    app.run(debug=True, host='0.0.0.0', port=8080)
