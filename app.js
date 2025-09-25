// Travel Agent Frontend Application
class TravelAgentApp {
    constructor() {
        this.currentStep = 0;
        this.isPlanning = false;
        this.preferences = {};
        this.currentRequest = null;
        this.init();
    }

    async init() {
        await this.loadPreferences();
        this.setupEventListeners();
        this.renderPreferencesEditor();
    }

    setupEventListeners() {
        // Travel request form submission
        document.getElementById('travel-request-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.startPlanning();
        });

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
                                <label for="dining">Dining</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="nightlife" ${this.preferences.activity_preferences?.indoor_activities?.includes('nightlife') ? 'checked' : ''}>
                                <label for="nightlife">Nightlife</label>
                            </div>
                        </div>
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
                preferred_chains: this.getCheckedValues(['marriott', 'hilton', 'hyatt', 'ihg']),
                room_preferences: this.getCheckedValues(['king-bed', 'ocean-view', 'high-floor'])
            },
            flight_preferences: {
                preferred_airlines: this.getCheckedValues(['united', 'american', 'delta', 'southwest']),
                class_preference: document.getElementById('class-preference').value,
                seat_preferences: this.getCheckedValues(['window-seat', 'aisle-seat', 'exit-row'])
            },
            budget_preferences: {
                budget_level: document.getElementById('budget-level').value,
                spending_style: document.getElementById('spending-style').value
            },
            activity_preferences: {
                outdoor_activities: this.getCheckedValues(['hiking', 'beach', 'sightseeing', 'water-sports']),
                indoor_activities: this.getCheckedValues(['museums', 'shopping', 'dining', 'nightlife'])
            },
            special_requirements: {
                mobility_requirements: document.getElementById('mobility-requirements').value,
                dietary_restrictions: this.getCheckedValues(['vegetarian', 'vegan', 'gluten-free', 'kosher'])
            }
        };

        return preferences;
    }

    getCheckedValues(ids) {
        return ids.filter(id => document.getElementById(id)?.checked).map(id => {
            const label = document.querySelector(`label[for="${id}"]`).textContent;
            return label.toLowerCase().replace(/\s+/g, '_');
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

    async startPlanning() {
        if (this.isPlanning) return;

        const formData = new FormData(document.getElementById('travel-request-form'));
        const request = {
            destination_query: document.getElementById('destination-query').value,
            travel_dates: document.getElementById('travel-dates').value,
            budget: document.getElementById('budget').value,
            origin: document.getElementById('origin').value,
            group_size: document.getElementById('group-size').value,
            traveler_type: document.getElementById('traveler-type').value
        };

        if (!request.destination_query.trim()) {
            this.showMessage('Please describe what kind of trip you\'re looking for.', 'warning');
            return;
        }

        this.isPlanning = true;
        this.currentRequest = request;
        this.currentStep = 0;

        // Show progress card
        document.getElementById('progress-card').classList.add('active');
        document.getElementById('results-section').classList.remove('active');
        document.getElementById('plan-trip-btn').disabled = true;

        try {
            await this.executePlanning(request);
        } catch (error) {
            console.error('Planning error:', error);
            this.showMessage('An error occurred during planning. Please try again.', 'error');
            this.cancelPlanning();
        }
    }

    async executePlanning(request) {
        const response = await fetch('/api/plan-trip', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(request)
        });

        if (!response.ok) {
            throw new Error('Failed to start planning');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        await this.handlePlanningUpdate(data);
                    } catch (e) {
                        console.error('Error parsing SSE data:', e);
                    }
                }
            }
        }
    }

    async handlePlanningUpdate(data) {
        switch (data.type) {
            case 'step':
                this.updateStep(data.step, data.message, data.details, data.substeps);
                break;
            case 'progress_update':
                this.updateProgressMessage(data.message, data.details);
                break;
            case 'user_input_required':
                await this.handleUserInputRequired(data);
                break;
            case 'destination_choice':
                await this.handleDestinationChoice(data);
                break;
            case 'results':
                this.showResults(data.results);
                break;
            case 'error':
                this.showMessage(data.message, 'error');
                this.cancelPlanning();
                break;
        }
    }

    updateStep(step, message, details = null, substeps = null) {
        this.currentStep = step;
        
        // Update step circles
        for (let i = 1; i <= 5; i++) {
            const circle = document.getElementById(`step-${i}`);
            if (i < step) {
                circle.classList.add('completed');
                circle.classList.remove('active');
            } else if (i === step) {
                circle.classList.add('active');
                circle.classList.remove('completed');
            } else {
                circle.classList.remove('active', 'completed');
            }
        }

        // Update progress content with detailed information
        const content = document.getElementById('progress-content');
        let progressHTML = `
            <div class="status-message status-info">
                <i class="fas fa-info-circle"></i>
                ${message}
            </div>
        `;

        if (details) {
            progressHTML += `
                <div class="progress-details">
                    <h4><i class="fas fa-search"></i> Processing Details</h4>
                    <p>${details}</p>
                </div>
            `;
        }

        if (substeps && substeps.length > 0) {
            progressHTML += `
                <div class="progress-substeps">
                    <h4><i class="fas fa-tasks"></i> Current Tasks</h4>
                    <ul class="substeps-list">
                        ${substeps.map(substep => `<li><i class="fas fa-clock"></i> ${substep}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        content.innerHTML = progressHTML;
    }

    updateProgressMessage(message, details = null) {
        // Update progress content with real-time message
        const content = document.getElementById('progress-content');
        let progressHTML = `
            <div class="status-message status-info">
                <i class="fas fa-spinner fa-spin"></i>
                ${message}
            </div>
        `;

        if (details) {
            progressHTML += `
                <div class="progress-details">
                    <h4><i class="fas fa-info-circle"></i> Current Activity</h4>
                    <p>${details}</p>
                </div>
            `;
        }

        content.innerHTML = progressHTML;
    }

    async handleUserInputRequired(data) {
        const content = document.getElementById('progress-content');
        content.innerHTML = `
            <div class="status-message status-warning">
                <i class="fas fa-exclamation-triangle"></i>
                ${data.message}
            </div>
            <div class="user-input-section">
                <h3>Please provide the missing information:</h3>
                <form id="user-input-form">
                    ${this.generateUserInputForm(data.required_fields)}
                    <button type="submit" class="btn">
                        <i class="fas fa-check"></i> Continue Planning
                    </button>
                </form>
            </div>
        `;

        // Setup form submission
        document.getElementById('user-input-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const inputData = Object.fromEntries(formData.entries());
            
            // Send user input back to server
            const response = await fetch('/api/user-input', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(inputData)
            });

            if (response.ok) {
                // Continue with planning
                this.updateStep(this.currentStep, 'Continuing with your input...');
            }
        });
    }

    generateUserInputForm(requiredFields) {
        let formHTML = '';
        
        for (const field of requiredFields) {
            switch (field) {
                case 'travel_dates':
                    formHTML += `
                        <div class="form-group">
                            <label for="input-travel-dates">Travel Dates *</label>
                            <input type="text" id="input-travel-dates" name="travel_dates" 
                                   placeholder="e.g., 'June 2024', 'summer', 'next month'" required>
                        </div>
                    `;
                    break;
                case 'budget':
                    formHTML += `
                        <div class="form-group">
                            <label for="input-budget">Budget *</label>
                            <input type="text" id="input-budget" name="budget" 
                                   placeholder="e.g., '$2000', 'budget-friendly', 'luxury'" required>
                        </div>
                    `;
                    break;
                case 'origin':
                    formHTML += `
                        <div class="form-group">
                            <label for="input-origin">Flying From *</label>
                            <input type="text" id="input-origin" name="origin" 
                                   placeholder="e.g., 'SFO', 'New York', 'London'" required>
                        </div>
                    `;
                    break;
            }
        }
        
        return formHTML;
    }

    async handleDestinationChoice(data) {
        const content = document.getElementById('progress-content');
        content.innerHTML = `
            <div class="status-message status-info">
                <i class="fas fa-map-marked-alt"></i>
                Found ${data.destinations.length} destination options for you!
            </div>
            <div class="user-input-section">
                <h3>Please choose your preferred destination:</h3>
                <form id="destination-choice-form">
                    ${data.destinations.map((dest, index) => `
                        <div class="destination-card">
                            <div class="destination-header">
                                <div>
                                    <div class="destination-name">${dest.name}</div>
                                    <div class="destination-location">${dest.country}</div>
                                </div>
                                <input type="radio" name="destination_choice" value="${index}" id="dest-${index}" required>
                            </div>
                            <div class="destination-description">${dest.description}</div>
                            <div class="destination-details">
                                <div class="detail-item">
                                    <i class="fas fa-clock"></i>
                                    <span>Best time: ${dest.best_time_to_visit}</span>
                                </div>
                                <div class="detail-item">
                                    <i class="fas fa-star"></i>
                                    <span>Family score: ${dest.family_friendly_score || 'N/A'}/10</span>
                                </div>
                                <div class="detail-item">
                                    <i class="fas fa-shield-alt"></i>
                                    <span>Safety: ${dest.safety_rating}</span>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                    <button type="submit" class="btn">
                        <i class="fas fa-check"></i> Select Destination
                    </button>
                </form>
            </div>
        `;

        // Setup form submission
        document.getElementById('destination-choice-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const choice = formData.get('destination_choice');
            
            // Send destination choice back to server
            const response = await fetch('/api/destination-choice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ choice: parseInt(choice) })
            });

            if (response.ok) {
                this.updateStep(this.currentStep + 1, 'Selected destination! Finding travel options...');
            }
        });
    }

    showResults(results) {
        const content = document.getElementById('results-content');
        content.innerHTML = `
            <div class="status-message status-success">
                <i class="fas fa-check-circle"></i>
                Your travel itinerary is ready!
            </div>
            ${this.renderItinerary(results)}
        `;

        document.getElementById('results-section').classList.add('active');
        document.getElementById('progress-card').classList.remove('active');
        this.cancelPlanning();
    }

    renderItinerary(itinerary) {
        if (!itinerary) return '<p>No itinerary available.</p>';

        let html = `
            <div class="destination-card">
                <div class="destination-header">
                    <div>
                        <div class="destination-name">${itinerary.destination || 'Selected Destination'}</div>
                        <div class="destination-location">${itinerary.duration || 'Trip Duration'}</div>
                    </div>
                </div>
                <div class="destination-description">${itinerary.summary || 'Your personalized travel itinerary'}</div>
            </div>
        `;

        if (itinerary.flights && itinerary.flights.length > 0) {
            html += `
                <div class="destination-card">
                    <h3><i class="fas fa-plane"></i> Flight Options</h3>
                    ${itinerary.flights.map(flight => `
                        <div class="detail-item">
                            <i class="fas fa-plane"></i>
                            <span>${flight.airline} - ${flight.price} (${flight.duration})</span>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        if (itinerary.hotels && itinerary.hotels.length > 0) {
            html += `
                <div class="destination-card">
                    <h3><i class="fas fa-bed"></i> Hotel Options</h3>
                    ${itinerary.hotels.map(hotel => `
                        <div class="detail-item">
                            <i class="fas fa-bed"></i>
                            <span>${hotel.name} - ${hotel.price} (${hotel.rating} stars)</span>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        return html;
    }

    showMessage(message, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `status-message status-${type}`;
        messageDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            ${message}
        `;

        // Insert at the top of the container
        const container = document.querySelector('.container');
        container.insertBefore(messageDiv, container.firstChild);

        // Remove after 5 seconds
        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }

    cancelPlanning() {
        this.isPlanning = false;
        this.currentStep = 0;
        document.getElementById('plan-trip-btn').disabled = false;
        document.getElementById('progress-card').classList.remove('active');
        
        // Reset step circles
        for (let i = 1; i <= 5; i++) {
            const circle = document.getElementById(`step-${i}`);
            circle.classList.remove('active', 'completed');
        }
    }
}

// Global functions for HTML onclick handlers
function savePreferences() {
    app.savePreferences();
}

function resetPreferences() {
    app.resetPreferences();
}

function cancelPlanning() {
    app.cancelPlanning();
}

// Initialize the app when the page loads
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new TravelAgentApp();
});
