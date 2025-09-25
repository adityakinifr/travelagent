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

    async def execute_planning(self):
        """Execute the travel planning process"""
        try:
            # Step 1: Analyze request
            self.current_step = 1
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
            group_size = self.request_data.get('group_size', '')
            if group_size and group_size.isdigit():
                group_size = int(group_size)
            else:
                group_size = None
                
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
                'substeps': ['Initializing destination research agent']
            }

            # Show web search progress
            yield {
                'type': 'progress_update',
                'message': 'Performing web search for destination options...',
                'details': 'Searching travel websites and databases'
            }

            # Show airport lookup progress
            yield {
                'type': 'progress_update',
                'message': 'Looking up airport codes for destinations...',
                'details': 'Finding nearest airports for flight planning'
            }

            # Research destinations
            destination_research = self.travel_agent.destination_agent.research_destination_with_feasibility(destination_request)

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

            # Show flight search progress
            yield {
                'type': 'progress_update',
                'message': 'Searching for flight options...',
                'details': f'Checking flights from {trip_spec.origin} to {trip_spec.destination}'
            }

            # Search travel options
            travel_options = self.travel_agent._search_travel_options({
                'trip_spec': trip_spec,
                'destination_research': destination_research
            })

            # Show flight results
            num_flights = len(travel_options.get('flights', []))
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
            num_hotels = len(travel_options.get('hotels', []))
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
                'flights': [
                    {
                        'airline': flight.airline,
                        'price': flight.price,
                        'duration': flight.duration
                    }
                    for flight in travel_options.get('flights', [])
                ],
                'hotels': [
                    {
                        'name': hotel.name,
                        'price': hotel.price,
                        'rating': hotel.rating
                    }
                    for hotel in travel_options.get('hotels', [])
                ]
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
        
        # Create planning session
        session = PlanningSession(session_id, request_data)
        planning_sessions[session_id] = session

        def generate():
            try:
                # Create a new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Run the async generator
                async def run_planning():
                    async for update in session.execute_planning():
                        yield f"data: {json.dumps(update)}\n\n"
                
                # Collect all updates from the async generator
                async def collect_updates():
                    updates = []
                    async for update in run_planning():
                        updates.append(update)
                    return updates
                
                # Run the async function and yield results
                updates = loop.run_until_complete(collect_updates())
                for update in updates:
                    yield update
                    
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
