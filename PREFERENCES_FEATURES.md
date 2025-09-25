# Travel Preferences System

## Overview
The travel preferences system provides comprehensive customization for travel recommendations, taking into account personal preferences, loyalty programs, and travel behavior patterns.

## Core Preference Categories

### 🏨 Hotel Preferences
- **Preferred Chains**: Marriott, Hilton, Hyatt, IHG, Accor
- **Avoided Chains**: Motel 6, Super 8
- **Loyalty Programs**: Marriott Bonvoy, Hilton Honors, World of Hyatt
- **Hotel Types**: Business, leisure, family-specific recommendations
- **Amenities**: Required (WiFi, fitness center) and preferred (pool, spa, business center)

### ✈️ Flight Preferences
- **Preferred Airlines**: United, American, Delta, Southwest
- **Airline Alliances**: Star Alliance, Oneworld, SkyTeam
- **Class Preferences**: 
  - Domestic short: Economy
  - Domestic long: Economy
  - International short: Premium Economy
  - International long: Business
  - Red-eye flights: Business
- **Seat Preferences**: Window, aisle, exit row, bulkhead
- **Red-eye Preference**: Avoid, prefer, or neutral
- **Layover Preferences**: Max 3 hours, prefer direct flights

### 💳 Loyalty Programs
- **Airline Status**: United Silver, American Gold, Delta Platinum, Southwest A-List
- **Hotel Status**: Marriott Gold, Hilton Diamond, Hyatt Explorist, IHG Platinum
- **Car Rental Status**: Hertz Gold, Enterprise Executive, Avis Preferred
- **Credit Cards**: Chase Sapphire Reserve, Amex Platinum, Capital One Venture

### 🏥 Travel Insurance
- **Preference**: Comprehensive coverage preferred
- **Provider**: Allianz
- **Coverage Level**: Comprehensive
- **Pre-existing Conditions**: Covered/not covered

### 📱 Technology Preferences
- **Mobile Apps**: Google Maps, Uber, Airbnb, TripAdvisor, Google Translate
- **Digital Wallet**: Apple Pay
- **Digital Preferences**: Digital boarding passes, digital check-in, offline maps

### 🎒 Packing Preferences
- **Packing Style**: Light, moderate, or heavy
- **Carry-on Preference**: Yes/No
- **Essential Items**: Phone charger, travel documents, medications, comfortable shoes
- **Climate Preparation**: Layered clothing approach

### 💬 Communication Preferences
- **International Roaming**: Avoid, prefer WiFi calling
- **Messaging Apps**: WhatsApp, iMessage
- **Translation Needs**: Moderate
- **Emergency Contacts**: Enabled

### 🏥 Health & Wellness
- **Fitness Requirements**: Moderate
- **Hotel Gym**: Preferred
- **Wellness Activities**: Spa, yoga, hiking
- **Dietary Restrictions**: Customizable
- **Medication Needs**: Trackable
- **Vaccination Status**: Up to date

### 🛡️ Safety & Security
- **Safety Consciousness**: High
- **Safe Neighborhoods**: Preferred
- **Travel Alerts**: Enabled
- **Emergency Preparedness**: Required
- **Travel Insurance**: Required
- **Backup Plans**: Recommended

### 🌍 Cultural Preferences
- **Cultural Sensitivity**: High
- **Authentic Experiences**: Preferred
- **Local Interaction Level**: Moderate
- **Language Learning**: Basic phrases
- **Cultural Activities**: Museums, local festivals, historical sites

### 🌱 Environmental Preferences
- **Eco-Conscious**: Yes
- **Eco-Hotels**: Optional
- **Carbon Offset**: Optional
- **Sustainable Transport**: Preferred
- **Local Sourcing**: Preferred

### 🎭 Entertainment Preferences
- **Nightlife Interest**: Moderate
- **Cultural Events**: High
- **Sports Events**: Low
- **Shopping Interest**: Moderate
- **Entertainment Budget**: Moderate

### 📸 Photography & Social
- **Photography Interest**: High
- **Social Media Sharing**: Moderate
- **Instagrammable Spots**: Preferred
- **Documentation Level**: Moderate

### 🔄 Flexibility Preferences
- **Date Flexibility**: Moderate
- **Destination Flexibility**: Low
- **Accommodation Flexibility**: Moderate
- **Activity Flexibility**: High
- **Weather Contingency**: Yes

### 👥 Group Dynamics
- **Decision Making**: Consensus
- **Group Activities**: Preferred
- **Alone Time Needs**: Moderate
- **Group Size Preference**: Small
- **Conflict Resolution**: Discussion

### 📚 Learning & Development
- **Educational Interest**: High
- **Skill Development**: Moderate
- **Local Learning**: Yes
- **Workshop Interest**: Moderate
- **Cultural Immersion**: Moderate

### 😌 Comfort Preferences
- **Climate Comfort**: Moderate
- **Noise Sensitivity**: Low
- **Crowd Tolerance**: Moderate
- **Pace Preference**: Moderate
- **Comfort vs Adventure**: Balanced

### 📋 Logistics Preferences
- **Planning Style**: Moderate
- **Spontaneity Level**: Moderate
- **Backup Planning**: Yes
- **Contingency Budget**: 10%
- **Emergency Fund**: Yes

## Usage Examples

### Business Traveler
```json
{
  "traveler_type": "business",
  "loyalty_programs": {
    "airline_status": {"united": "gold"},
    "hotel_status": {"marriott": "platinum"}
  },
  "flight_preferences": {
    "class_preferences": {
      "domestic_long": "business",
      "international_long": "business"
    }
  }
}
```

### Family with Kids
```json
{
  "traveler_type": "family_with_kids",
  "hotel_preferences": {
    "hotel_types": {"family": ["family_resort", "suite_hotel"]},
    "amenities_required": ["wifi", "pool", "restaurant"]
  },
  "safety_security": {
    "safety_consciousness": "high",
    "prefer_safe_neighborhoods": true
  }
}
```

### Eco-Conscious Solo Traveler
```json
{
  "traveler_type": "solo",
  "environmental_preferences": {
    "eco_conscious": true,
    "prefer_eco_hotels": true,
    "sustainable_transport": "prefer"
  },
  "cultural_preferences": {
    "prefer_authentic_experiences": true,
    "local_interaction_level": "high"
  }
}
```

## Integration with Destination Research

The preferences system is fully integrated with the destination research agent, providing:

1. **Personalized Recommendations**: Destinations ranked based on traveler preferences
2. **Loyalty Program Benefits**: Recommendations that maximize loyalty program benefits
3. **Budget Alignment**: Recommendations that match budget preferences
4. **Activity Matching**: Activities that align with interests and capabilities
5. **Safety Considerations**: Destinations that match safety preferences
6. **Cultural Fit**: Destinations that match cultural sensitivity and interests

## Benefits

- **Personalization**: Highly tailored recommendations
- **Loyalty Optimization**: Maximize benefits from loyalty programs
- **Budget Efficiency**: Align recommendations with budget preferences
- **Safety First**: Prioritize safety-conscious recommendations
- **Cultural Fit**: Match destinations to cultural preferences
- **Comprehensive Coverage**: All aspects of travel considered
- **Flexibility**: Easy to modify and update preferences
- **Integration**: Seamlessly integrated with existing travel planning

## File Structure

- `travel_preferences.json`: Main preferences configuration file
- `preferences_manager.py`: Preferences management and application logic
- `destination_agent.py`: Enhanced with preferences integration
- `test_preferences_system.py`: Comprehensive testing suite

## Future Enhancements

- Machine learning-based preference learning
- Dynamic preference updates based on travel history
- Integration with external loyalty program APIs
- Real-time preference synchronization across devices
- Advanced budget optimization algorithms
