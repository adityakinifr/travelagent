# AI Travel Agent - Web Interface

A beautiful, interactive web interface for the AI Travel Agent that allows users to edit their preferences and plan trips with real-time progress tracking.

## Features

### 🎨 **Modern Web Interface**
- Responsive design that works on desktop and mobile
- Beautiful gradient backgrounds and smooth animations
- Intuitive user experience with clear visual feedback

### ⚙️ **Comprehensive Preferences Editor**
- **Traveler Profile**: Home airport, travel style, age range
- **Hotel Preferences**: Preferred chains, room preferences, loyalty programs
- **Flight Preferences**: Preferred airlines, class preference, seat preferences
- **Budget Preferences**: Budget level, spending style
- **Activity Preferences**: Outdoor/indoor activities, adventure level
- **Special Requirements**: Mobility needs, dietary restrictions

### 🚀 **Real-Time Trip Planning**
- **Step-by-step Progress**: Visual progress tracking with 5 clear steps
- **Interactive Forms**: Dynamic forms for missing information
- **Destination Selection**: Visual destination cards with detailed information
- **Live Updates**: Server-sent events for real-time progress updates

### 📊 **Visual Results Display**
- **Destination Cards**: Beautiful cards showing destination details
- **Flight Options**: Clear display of flight information and pricing
- **Hotel Options**: Hotel details with ratings and pricing
- **Itinerary Summary**: Comprehensive trip overview

## Quick Start

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Set Up Environment**
Create a `.env` file with your API keys:
```bash
cp env_example.txt .env
# Edit .env with your API keys
```

### 3. **Start the Server**
```bash
python start_server.py
```

### 4. **Open in Browser**
Navigate to `http://localhost:8080` in your web browser.

## Usage

### **Setting Up Preferences**
1. **Open the Preferences Editor** on the left side of the interface
2. **Configure your travel preferences**:
   - Set your home airport (e.g., "SFO", "LAX")
   - Choose preferred hotel chains and airlines
   - Set your budget level and travel style
   - Select your activity preferences
   - Add any special requirements
3. **Save your preferences** - they'll be automatically saved to `travel_preferences.json`

### **Planning a Trip**
1. **Fill out the trip request form** on the right side:
   - Describe what kind of trip you're looking for
   - Specify travel dates, budget, and origin
   - Select your group size and traveler type
2. **Click "Plan My Trip"** to start the planning process
3. **Watch the progress** as the system:
   - Analyzes your request
   - Researches destinations with web search
   - Checks feasibility and constraints
   - Finds travel options
   - Creates your personalized itinerary

### **Interactive Features**
- **Missing Information**: If dates, budget, or origin are missing, the system will ask for them
- **Destination Choice**: If multiple destinations are found, you can choose your preferred one
- **Real-time Updates**: See progress updates in real-time as the system works
- **Visual Feedback**: Clear status messages and progress indicators

## Technical Architecture

### **Frontend (HTML/CSS/JavaScript)**
- **Responsive Design**: CSS Grid and Flexbox for modern layouts
- **Interactive Components**: Dynamic forms and real-time updates
- **Server-Sent Events**: Real-time communication with the backend
- **Progressive Enhancement**: Works without JavaScript for basic functionality

### **Backend (Flask)**
- **RESTful API**: Clean API endpoints for all functionality
- **Server-Sent Events**: Real-time progress streaming
- **Session Management**: Handles multiple planning sessions
- **Error Handling**: Comprehensive error handling and user feedback

### **Integration**
- **Travel Agent**: Integrates with the existing LangGraph-based travel agent
- **Destination Research**: Uses the enhanced web search and ordering system
- **Preferences Management**: Loads and saves user preferences
- **Feasibility Checking**: Validates destinations against constraints

## File Structure

```
travelagent/
├── index.html              # Main web interface
├── app.js                  # Frontend JavaScript
├── app.py                  # Flask backend server
├── start_server.py         # Startup script
├── travel_preferences.json # User preferences storage
├── travel_agent.py         # Main travel agent
├── destination_agent.py    # Destination research agent
├── preferences_manager.py  # Preferences management
└── requirements.txt        # Python dependencies
```

## API Endpoints

### **Preferences**
- `GET /api/preferences` - Get user preferences
- `POST /api/preferences` - Save user preferences

### **Trip Planning**
- `POST /api/plan-trip` - Start trip planning (Server-Sent Events)
- `POST /api/user-input` - Handle missing information input
- `POST /api/destination-choice` - Handle destination selection

### **Health**
- `GET /api/health` - Health check endpoint

## Customization

### **Styling**
- Modify `index.html` CSS for visual customization
- Colors, fonts, and layouts can be easily adjusted
- Responsive breakpoints can be modified for different screen sizes

### **Preferences**
- Add new preference categories in `app.js`
- Update the preferences manager to handle new fields
- Modify the backend to process additional preferences

### **Planning Flow**
- Customize the planning steps in `app.py`
- Add new user input types
- Modify the progress tracking system

## Troubleshooting

### **Common Issues**

1. **Server won't start**
   - Check that all dependencies are installed
   - Verify environment variables are set correctly
   - Ensure port 5000 is available

2. **Preferences not saving**
   - Check file permissions for `travel_preferences.json`
   - Verify the preferences format is valid JSON

3. **Planning process stops**
   - Check API keys are valid and have sufficient credits
   - Verify network connectivity for external APIs
   - Check server logs for error messages

### **Debug Mode**
The server runs in debug mode by default, which provides:
- Detailed error messages
- Automatic reloading on code changes
- Enhanced logging

## Future Enhancements

- **User Authentication**: Login system for multiple users
- **Trip History**: Save and retrieve previous trips
- **Sharing**: Share itineraries with others
- **Mobile App**: Native mobile application
- **Advanced Filters**: More detailed filtering options
- **Real-time Pricing**: Live price updates
- **Booking Integration**: Direct booking capabilities

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the server logs for error messages
3. Verify all dependencies and environment variables
4. Test with simple requests first

The web interface provides a complete, user-friendly way to interact with the AI Travel Agent, making travel planning accessible and enjoyable for all users! 🌟
