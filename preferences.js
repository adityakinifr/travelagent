// Travel Preferences Management
class PreferencesManager {
    constructor() {
        this.preferences = {};
        this.init();
    }

    async init() {
        await this.loadPreferences();
        this.renderPreferencesEditor();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Auto-save preferences on change
        document.getElementById('preferences-editor').addEventListener('change', () => {
            this.autoSavePreferences();
        });
    }

    async loadPreferences() {
        try {
            const response = await fetch('/api/preferences');
            if (response.ok) {
                this.preferences = await response.json();
            } else {
                // Load default preferences
                this.preferences = this.getDefaultPreferences();
            }
        } catch (error) {
            console.error('Error loading preferences:', error);
            this.preferences = this.getDefaultPreferences();
        }
    }

    getDefaultPreferences() {
        return {
            traveler_profile: {
                home_airport: "SFO",
                preferred_airlines: ["United", "American", "Delta"],
                frequent_flyer_programs: ["United MileagePlus", "American AAdvantage"],
                travel_style: "comfortable",
                group_size: 2,
                age_range: "middle_aged"
            },
            hotel_preferences: {
                preferred_chains: ["Marriott", "Hilton", "Hyatt"],
                loyalty_programs: ["Marriott Bonvoy", "Hilton Honors"],
                room_preferences: ["king_bed", "ocean_view", "high_floor"],
                amenities: ["wifi", "gym", "pool", "spa"]
            },
            flight_preferences: {
                preferred_airlines: ["United", "American", "Delta"],
                class_preference: "economy",
                seat_preferences: ["window", "aisle", "exit_row"],
                red_eye_preference: false,
                layover_preference: "minimal"
            },
            budget_preferences: {
                budget_level: "moderate",
                currency: "USD",
                spending_style: "balanced"
            },
            activity_preferences: {
                outdoor_activities: ["hiking", "beach", "sightseeing"],
                indoor_activities: ["museums", "shopping", "dining"],
                adventure_level: "moderate"
            },
            special_requirements: {
                dietary_restrictions: [],
                accessibility_needs: [],
                mobility_requirements: "any"
            }
        };
    }

    renderPreferencesEditor() {
        const editor = document.getElementById('preferences-editor');
        editor.innerHTML = `
            <div class="preferences-grid">
                <div class="preference-section">
                    <h3><i class="fas fa-user"></i> Traveler Profile</h3>
                    <div class="form-group">
                        <label for="home-airport">Home Airport</label>
                        <input type="text" id="home-airport" value="${this.preferences.traveler_profile?.home_airport || 'SFO'}" placeholder="e.g., SFO, LAX, JFK">
                    </div>
                    <div class="form-group">
                        <label for="travel-style">Travel Style</label>
                        <select id="travel-style">
                            <option value="budget" ${this.preferences.traveler_profile?.travel_style === 'budget' ? 'selected' : ''}>Budget</option>
                            <option value="comfortable" ${this.preferences.traveler_profile?.travel_style === 'comfortable' ? 'selected' : ''}>Comfortable</option>
                            <option value="luxury" ${this.preferences.traveler_profile?.travel_style === 'luxury' ? 'selected' : ''}>Luxury</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="age-range">Age Range</label>
                        <select id="age-range">
                            <option value="young_adults" ${this.preferences.traveler_profile?.age_range === 'young_adults' ? 'selected' : ''}>Young Adults (18-30)</option>
                            <option value="middle_aged" ${this.preferences.traveler_profile?.age_range === 'middle_aged' ? 'selected' : ''}>Middle Aged (31-50)</option>
                            <option value="seniors" ${this.preferences.traveler_profile?.age_range === 'seniors' ? 'selected' : ''}>Seniors (50+)</option>
                            <option value="mixed_ages" ${this.preferences.traveler_profile?.age_range === 'mixed_ages' ? 'selected' : ''}>Mixed Ages</option>
                        </select>
                    </div>
                </div>

                <div class="preference-section">
                    <h3><i class="fas fa-bed"></i> Hotel Preferences</h3>
                    <div class="form-group">
                        <label>Preferred Hotel Chains</label>
                        <div class="checkbox-group">
                            <div class="checkbox-item">
                                <input type="checkbox" id="marriott" ${this.preferences.hotel_preferences?.preferred_chains?.includes('Marriott') ? 'checked' : ''}>
                                <label for="marriott">Marriott</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="hilton" ${this.preferences.hotel_preferences?.preferred_chains?.includes('Hilton') ? 'checked' : ''}>
                                <label for="hilton">Hilton</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="hyatt" ${this.preferences.hotel_preferences?.preferred_chains?.includes('Hyatt') ? 'checked' : ''}>
                                <label for="hyatt">Hyatt</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="ihg" ${this.preferences.hotel_preferences?.preferred_chains?.includes('IHG') ? 'checked' : ''}>
                                <label for="ihg">IHG</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="accor" ${this.preferences.hotel_preferences?.preferred_chains?.includes('Accor') ? 'checked' : ''}>
                                <label for="accor">Accor</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="wyndham" ${this.preferences.hotel_preferences?.preferred_chains?.includes('Wyndham') ? 'checked' : ''}>
                                <label for="wyndham">Wyndham</label>
                            </div>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Room Preferences</label>
                        <div class="checkbox-group">
                            <div class="checkbox-item">
                                <input type="checkbox" id="king-bed" ${this.preferences.hotel_preferences?.room_preferences?.includes('king_bed') ? 'checked' : ''}>
                                <label for="king-bed">King Bed</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="ocean-view" ${this.preferences.hotel_preferences?.room_preferences?.includes('ocean_view') ? 'checked' : ''}>
                                <label for="ocean-view">Ocean View</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="high-floor" ${this.preferences.hotel_preferences?.room_preferences?.includes('high_floor') ? 'checked' : ''}>
                                <label for="high-floor">High Floor</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="suite" ${this.preferences.hotel_preferences?.room_preferences?.includes('suite') ? 'checked' : ''}>
                                <label for="suite">Suite</label>
                            </div>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Preferred Amenities</label>
                        <div class="checkbox-group">
                            <div class="checkbox-item">
                                <input type="checkbox" id="wifi" ${this.preferences.hotel_preferences?.amenities?.includes('wifi') ? 'checked' : ''}>
                                <label for="wifi">Free WiFi</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="gym" ${this.preferences.hotel_preferences?.amenities?.includes('gym') ? 'checked' : ''}>
                                <label for="gym">Fitness Center</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="pool" ${this.preferences.hotel_preferences?.amenities?.includes('pool') ? 'checked' : ''}>
                                <label for="pool">Swimming Pool</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="spa" ${this.preferences.hotel_preferences?.amenities?.includes('spa') ? 'checked' : ''}>
                                <label for="spa">Spa Services</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="restaurant" ${this.preferences.hotel_preferences?.amenities?.includes('restaurant') ? 'checked' : ''}>
                                <label for="restaurant">Restaurant</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="parking" ${this.preferences.hotel_preferences?.amenities?.includes('parking') ? 'checked' : ''}>
                                <label for="parking">Parking</label>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="preference-section">
                    <h3><i class="fas fa-plane"></i> Flight Preferences</h3>
                    <div class="form-group">
                        <label>Preferred Airlines</label>
                        <div class="checkbox-group">
                            <div class="checkbox-item">
                                <input type="checkbox" id="united" ${this.preferences.flight_preferences?.preferred_airlines?.includes('United') ? 'checked' : ''}>
                                <label for="united">United</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="american" ${this.preferences.flight_preferences?.preferred_airlines?.includes('American') ? 'checked' : ''}>
                                <label for="american">American</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="delta" ${this.preferences.flight_preferences?.preferred_airlines?.includes('Delta') ? 'checked' : ''}>
                                <label for="delta">Delta</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="southwest" ${this.preferences.flight_preferences?.preferred_airlines?.includes('Southwest') ? 'checked' : ''}>
                                <label for="southwest">Southwest</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="jetblue" ${this.preferences.flight_preferences?.preferred_airlines?.includes('JetBlue') ? 'checked' : ''}>
                                <label for="jetblue">JetBlue</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="alaska" ${this.preferences.flight_preferences?.preferred_airlines?.includes('Alaska') ? 'checked' : ''}>
                                <label for="alaska">Alaska Airlines</label>
                            </div>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="class-preference">Class Preference</label>
                        <select id="class-preference">
                            <option value="economy" ${this.preferences.flight_preferences?.class_preference === 'economy' ? 'selected' : ''}>Economy</option>
                            <option value="premium_economy" ${this.preferences.flight_preferences?.class_preference === 'premium_economy' ? 'selected' : ''}>Premium Economy</option>
                            <option value="business" ${this.preferences.flight_preferences?.class_preference === 'business' ? 'selected' : ''}>Business</option>
                            <option value="first" ${this.preferences.flight_preferences?.class_preference === 'first' ? 'selected' : ''}>First</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Seat Preferences</label>
                        <div class="checkbox-group">
                            <div class="checkbox-item">
                                <input type="checkbox" id="window-seat" ${this.preferences.flight_preferences?.seat_preferences?.includes('window') ? 'checked' : ''}>
                                <label for="window-seat">Window</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="aisle-seat" ${this.preferences.flight_preferences?.seat_preferences?.includes('aisle') ? 'checked' : ''}>
                                <label for="aisle-seat">Aisle</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="exit-row" ${this.preferences.flight_preferences?.seat_preferences?.includes('exit_row') ? 'checked' : ''}>
                                <label for="exit-row">Exit Row</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="bulkhead" ${this.preferences.flight_preferences?.seat_preferences?.includes('bulkhead') ? 'checked' : ''}>
                                <label for="bulkhead">Bulkhead</label>
                            </div>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Flight Preferences</label>
                        <div class="checkbox-group">
                            <div class="checkbox-item">
                                <input type="checkbox" id="red-eye" ${this.preferences.flight_preferences?.red_eye_preference ? 'checked' : ''}>
                                <label for="red-eye">Red-eye flights OK</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="direct-flights" ${this.preferences.flight_preferences?.direct_flights_only ? 'checked' : ''}>
                                <label for="direct-flights">Direct flights only</label>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="preference-section">
                    <h3><i class="fas fa-dollar-sign"></i> Budget Preferences</h3>
                    <div class="form-group">
                        <label for="budget-level">Budget Level</label>
                        <select id="budget-level">
                            <option value="budget" ${this.preferences.budget_preferences?.budget_level === 'budget' ? 'selected' : ''}>Budget</option>
                            <option value="moderate" ${this.preferences.budget_preferences?.budget_level === 'moderate' ? 'selected' : ''}>Moderate</option>
                            <option value="luxury" ${this.preferences.budget_preferences?.budget_level === 'luxury' ? 'selected' : ''}>Luxury</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="spending-style">Spending Style</label>
                        <select id="spending-style">
                            <option value="frugal" ${this.preferences.budget_preferences?.spending_style === 'frugal' ? 'selected' : ''}>Frugal</option>
                            <option value="balanced" ${this.preferences.budget_preferences?.spending_style === 'balanced' ? 'selected' : ''}>Balanced</option>
                            <option value="splurge" ${this.preferences.budget_preferences?.spending_style === 'splurge' ? 'selected' : ''}>Splurge</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="currency">Preferred Currency</label>
                        <select id="currency">
                            <option value="USD" ${this.preferences.budget_preferences?.currency === 'USD' ? 'selected' : ''}>USD ($)</option>
                            <option value="EUR" ${this.preferences.budget_preferences?.currency === 'EUR' ? 'selected' : ''}>EUR (€)</option>
                            <option value="GBP" ${this.preferences.budget_preferences?.currency === 'GBP' ? 'selected' : ''}>GBP (£)</option>
                            <option value="CAD" ${this.preferences.budget_preferences?.currency === 'CAD' ? 'selected' : ''}>CAD (C$)</option>
                        </select>
                    </div>
                </div>

                <div class="preference-section">
                    <h3><i class="fas fa-hiking"></i> Activity Preferences</h3>
                    <div class="form-group">
                        <label>Outdoor Activities</label>
                        <div class="checkbox-group">
                            <div class="checkbox-item">
                                <input type="checkbox" id="hiking" ${this.preferences.activity_preferences?.outdoor_activities?.includes('hiking') ? 'checked' : ''}>
                                <label for="hiking">Hiking</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="beach" ${this.preferences.activity_preferences?.outdoor_activities?.includes('beach') ? 'checked' : ''}>
                                <label for="beach">Beach</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="sightseeing" ${this.preferences.activity_preferences?.outdoor_activities?.includes('sightseeing') ? 'checked' : ''}>
                                <label for="sightseeing">Sightseeing</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="water-sports" ${this.preferences.activity_preferences?.outdoor_activities?.includes('water_sports') ? 'checked' : ''}>
                                <label for="water-sports">Water Sports</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="adventure" ${this.preferences.activity_preferences?.outdoor_activities?.includes('adventure') ? 'checked' : ''}>
                                <label for="adventure">Adventure Sports</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="nature" ${this.preferences.activity_preferences?.outdoor_activities?.includes('nature') ? 'checked' : ''}>
                                <label for="nature">Nature Tours</label>
                            </div>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Indoor Activities</label>
                        <div class="checkbox-group">
                            <div class="checkbox-item">
                                <input type="checkbox" id="museums" ${this.preferences.activity_preferences?.indoor_activities?.includes('museums') ? 'checked' : ''}>
                                <label for="museums">Museums</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="shopping" ${this.preferences.activity_preferences?.indoor_activities?.includes('shopping') ? 'checked' : ''}>
                                <label for="shopping">Shopping</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="dining" ${this.preferences.activity_preferences?.indoor_activities?.includes('dining') ? 'checked' : ''}>
                                <label for="dining">Fine Dining</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="nightlife" ${this.preferences.activity_preferences?.indoor_activities?.includes('nightlife') ? 'checked' : ''}>
                                <label for="nightlife">Nightlife</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="cultural" ${this.preferences.activity_preferences?.indoor_activities?.includes('cultural') ? 'checked' : ''}>
                                <label for="cultural">Cultural Events</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="spa-activities" ${this.preferences.activity_preferences?.indoor_activities?.includes('spa') ? 'checked' : ''}>
                                <label for="spa-activities">Spa & Wellness</label>
                            </div>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="adventure-level">Adventure Level</label>
                        <select id="adventure-level">
                            <option value="low" ${this.preferences.activity_preferences?.adventure_level === 'low' ? 'selected' : ''}>Low - Relaxing</option>
                            <option value="moderate" ${this.preferences.activity_preferences?.adventure_level === 'moderate' ? 'selected' : ''}>Moderate - Balanced</option>
                            <option value="high" ${this.preferences.activity_preferences?.adventure_level === 'high' ? 'selected' : ''}>High - Thrilling</option>
                        </select>
                    </div>
                </div>

                <div class="preference-section">
                    <h3><i class="fas fa-wheelchair"></i> Special Requirements</h3>
                    <div class="form-group">
                        <label for="mobility-requirements">Mobility Requirements</label>
                        <select id="mobility-requirements">
                            <option value="any" ${this.preferences.special_requirements?.mobility_requirements === 'any' ? 'selected' : ''}>Any</option>
                            <option value="wheelchair_accessible" ${this.preferences.special_requirements?.mobility_requirements === 'wheelchair_accessible' ? 'selected' : ''}>Wheelchair Accessible</option>
                            <option value="limited_mobility" ${this.preferences.special_requirements?.mobility_requirements === 'limited_mobility' ? 'selected' : ''}>Limited Mobility</option>
                            <option value="active" ${this.preferences.special_requirements?.mobility_requirements === 'active' ? 'selected' : ''}>Active</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Dietary Restrictions</label>
                        <div class="checkbox-group">
                            <div class="checkbox-item">
                                <input type="checkbox" id="vegetarian" ${this.preferences.special_requirements?.dietary_restrictions?.includes('vegetarian') ? 'checked' : ''}>
                                <label for="vegetarian">Vegetarian</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="vegan" ${this.preferences.special_requirements?.dietary_restrictions?.includes('vegan') ? 'checked' : ''}>
                                <label for="vegan">Vegan</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="gluten-free" ${this.preferences.special_requirements?.dietary_restrictions?.includes('gluten_free') ? 'checked' : ''}>
                                <label for="gluten-free">Gluten-Free</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="kosher" ${this.preferences.special_requirements?.dietary_restrictions?.includes('kosher') ? 'checked' : ''}>
                                <label for="kosher">Kosher</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="halal" ${this.preferences.special_requirements?.dietary_restrictions?.includes('halal') ? 'checked' : ''}>
                                <label for="halal">Halal</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="dairy-free" ${this.preferences.special_requirements?.dietary_restrictions?.includes('dairy_free') ? 'checked' : ''}>
                                <label for="dairy-free">Dairy-Free</label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    collectPreferences() {
        const preferences = {
            traveler_profile: {
                home_airport: document.getElementById('home-airport').value,
                travel_style: document.getElementById('travel-style').value,
                age_range: document.getElementById('age-range').value
            },
            hotel_preferences: {
                preferred_chains: this.getCheckedValues(['marriott', 'hilton', 'hyatt', 'ihg', 'accor', 'wyndham']),
                room_preferences: this.getCheckedValues(['king-bed', 'ocean-view', 'high-floor', 'suite']),
                amenities: this.getCheckedValues(['wifi', 'gym', 'pool', 'spa', 'restaurant', 'parking'])
            },
            flight_preferences: {
                preferred_airlines: this.getCheckedValues(['united', 'american', 'delta', 'southwest', 'jetblue', 'alaska']),
                class_preference: document.getElementById('class-preference').value,
                seat_preferences: this.getCheckedValues(['window-seat', 'aisle-seat', 'exit-row', 'bulkhead']),
                red_eye_preference: document.getElementById('red-eye').checked,
                direct_flights_only: document.getElementById('direct-flights').checked
            },
            budget_preferences: {
                budget_level: document.getElementById('budget-level').value,
                spending_style: document.getElementById('spending-style').value,
                currency: document.getElementById('currency').value
            },
            activity_preferences: {
                outdoor_activities: this.getCheckedValues(['hiking', 'beach', 'sightseeing', 'water-sports', 'adventure', 'nature']),
                indoor_activities: this.getCheckedValues(['museums', 'shopping', 'dining', 'nightlife', 'cultural', 'spa-activities']),
                adventure_level: document.getElementById('adventure-level').value
            },
            special_requirements: {
                mobility_requirements: document.getElementById('mobility-requirements').value,
                dietary_restrictions: this.getCheckedValues(['vegetarian', 'vegan', 'gluten-free', 'kosher', 'halal', 'dairy-free'])
            }
        };

        return preferences;
    }

    getCheckedValues(ids) {
        return ids.filter(id => document.getElementById(id)?.checked).map(id => {
            const label = document.querySelector(`label[for="${id}"]`).textContent;
            return label.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
        });
    }

    async savePreferences() {
        const preferences = this.collectPreferences();
        
        try {
            const response = await fetch('/api/preferences', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(preferences)
            });

            if (response.ok) {
                this.showMessage('Preferences saved successfully!', 'success');
                this.preferences = preferences;
            } else {
                throw new Error('Failed to save preferences');
            }
        } catch (error) {
            console.error('Error saving preferences:', error);
            this.showMessage('Error saving preferences. Please try again.', 'error');
        }
    }

    async autoSavePreferences() {
        // Debounce auto-save
        clearTimeout(this.autoSaveTimeout);
        this.autoSaveTimeout = setTimeout(() => {
            this.savePreferences();
        }, 1000);
    }

    async resetPreferences() {
        if (confirm('Are you sure you want to reset all preferences to defaults?')) {
            this.preferences = this.getDefaultPreferences();
            this.renderPreferencesEditor();
            await this.savePreferences();
            this.showMessage('Preferences reset to defaults!', 'success');
        }
    }

    showMessage(message, type) {
        const messageDiv = document.getElementById('status-message');
        messageDiv.innerHTML = `
            <div class="status-message status-${type}">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
                ${message}
            </div>
        `;

        // Remove after 5 seconds
        setTimeout(() => {
            messageDiv.innerHTML = '';
        }, 5000);
    }
}

// Global functions for HTML onclick handlers
function savePreferences() {
    preferencesManager.savePreferences();
}

function resetPreferences() {
    preferencesManager.resetPreferences();
}

// Initialize the preferences manager when the page loads
let preferencesManager;
document.addEventListener('DOMContentLoaded', () => {
    preferencesManager = new PreferencesManager();
});
