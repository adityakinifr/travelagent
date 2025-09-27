// Travel Agent Frontend Application
class TravelAgentApp {
    constructor() {
        this.currentStep = 0;
        this.isPlanning = false;
        this.preferences = {};
        this.currentRequest = null;
        this.sseBuffer = '';
        this.totalSteps = 5;
        this.activeStep = 1;
        this.maxStepReached = 1;
        this.stepEntries = this.initializeStepEntries();
        this.stepUnread = this.initializeStepUnread();
        this.progressStepElements = [];
        this.init();
    }

    async init() {
        await this.loadPreferences();
        this.setupEventListeners();
        this.renderPreferencesEditor();
        this.setupProgressNavigation();
        this.resetProgressState();
    }

    initializeStepEntries() {
        const entries = {};
        for (let i = 1; i <= this.totalSteps; i++) {
            entries[i] = [];
        }
        return entries;
    }

    initializeStepUnread() {
        const unread = {};
        for (let i = 1; i <= this.totalSteps; i++) {
            unread[i] = 0;
        }
        return unread;
    }

    resetProgressState() {
        this.stepEntries = this.initializeStepEntries();
        this.stepUnread = this.initializeStepUnread();
        this.currentStep = 0;
        this.activeStep = 1;
        this.maxStepReached = this.isPlanning ? 1 : 0;
        this.renderActiveStep();
        this.updateStepIndicators();
    }

    setupEventListeners() {
        // Travel request form submission
        const travelForm = document.getElementById('travel-request-form');
        if (travelForm) {
            travelForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.startPlanning();
            });
        } else {
            console.warn('⚠️ travel-request-form element not found; planning cannot be started from this page.');
        }

        // Auto-save preferences on change
        const preferencesEditor = document.getElementById('preferences-editor');
        if (preferencesEditor) {
            preferencesEditor.addEventListener('change', () => {
                this.autoSavePreferences();
            });
        } else {
            console.warn('⚠️ preferences-editor element not found; auto-save disabled for this page.');
        }
    }

    setupProgressNavigation() {
        this.progressStepElements = Array.from(document.querySelectorAll('.progress-step'));
        this.progressStepElements.forEach((stepElement, index) => {
            const stepNumber = parseInt(stepElement.dataset.step, 10) || index + 1;
            stepElement.dataset.step = stepNumber;
            stepElement.setAttribute('role', 'tab');
            if (!stepElement.hasAttribute('tabindex')) {
                stepElement.setAttribute('tabindex', stepNumber === 1 ? '0' : '-1');
            }

            stepElement.addEventListener('click', () => {
                this.showStep(stepNumber);
            });

            stepElement.addEventListener('keydown', (event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    this.showStep(stepNumber);
                }
            });
        });
        this.updateStepIndicators();
    }

    addStepEntry(step, entry, options = {}) {
        const { replace = false, activate = false } = options;
        const targetStep = Math.min(Math.max(step, 1), this.totalSteps);

        if (!this.stepEntries[targetStep] || replace) {
            this.stepEntries[targetStep] = [];
        }

        this.stepEntries[targetStep].push(entry);

        if (activate) {
            this.activeStep = targetStep;
            this.stepUnread[targetStep] = 0;
        }

        if (!activate && this.activeStep !== targetStep) {
            this.stepUnread[targetStep] = (this.stepUnread[targetStep] || 0) + 1;
        }

        if (this.activeStep === targetStep || activate) {
            this.renderActiveStep();
        }

        this.updateStepIndicators();
    }

    renderActiveStep() {
        const content = document.getElementById('progress-content');
        if (!content) return;

        const entries = this.stepEntries[this.activeStep] || [];
        this.stepUnread[this.activeStep] = 0;

        if (entries.length === 0) {
            content.innerHTML = this.wrapProgressEntry(
                this.createStatusMessage('fas fa-clock', 'info', 'Waiting for updates for this stage...')
            );
            return;
        }

        content.innerHTML = entries.map((entry) => entry.html).join('');

        // Initialize any interactive elements within the active step content
        this.attachInteractiveHandlers(this.activeStep);
        this.updateStepIndicators();
    }

    showStep(step, options = {}) {
        const { force = false } = options;
        if (!force && step > this.maxStepReached) {
            return;
        }

        this.activeStep = Math.min(Math.max(step, 1), this.totalSteps);
        this.stepUnread[this.activeStep] = 0;
        this.renderActiveStep();
        this.updateStepIndicators();
    }

    updateStepIndicators(currentStep = this.currentStep) {
        if (!Array.isArray(this.progressStepElements) || this.progressStepElements.length === 0) {
            this.progressStepElements = Array.from(document.querySelectorAll('.progress-step'));
        }

        this.progressStepElements.forEach((stepElement) => {
            const stepNumber = parseInt(stepElement.dataset.step, 10) || 1;
            const circle = stepElement.querySelector('.step-circle');
            const isActive = stepNumber === this.activeStep;
            const isAccessible = stepNumber <= this.maxStepReached || isActive;
            const labelElement = stepElement.querySelector('.step-label');
            const baseLabel = labelElement ? labelElement.textContent : `Step ${stepNumber}`;

            if (circle) {
                circle.classList.remove('active', 'completed');
                if (currentStep && stepNumber < currentStep) {
                    circle.classList.add('completed');
                } else if (currentStep && stepNumber === currentStep) {
                    circle.classList.add('active');
                }
            }

            if (stepNumber <= this.maxStepReached) {
                stepElement.classList.add('available');
            } else {
                stepElement.classList.remove('available');
            }

            if (isActive) {
                stepElement.classList.add('viewing');
            } else {
                stepElement.classList.remove('viewing');
            }

            if ((this.stepUnread[stepNumber] || 0) > 0 && !isActive) {
                stepElement.classList.add('has-updates');
                stepElement.setAttribute('data-unread', this.stepUnread[stepNumber]);
                stepElement.setAttribute('aria-label', `${baseLabel} (${this.stepUnread[stepNumber]} new updates)`);
            } else {
                stepElement.classList.remove('has-updates');
                stepElement.removeAttribute('data-unread');
                stepElement.setAttribute('aria-label', baseLabel);
            }

            stepElement.setAttribute('aria-selected', isActive ? 'true' : 'false');
            stepElement.setAttribute('aria-disabled', isAccessible ? 'false' : 'true');
            stepElement.setAttribute('tabindex', isAccessible ? '0' : '-1');
        });
    }

    attachInteractiveHandlers(step) {
        const entries = this.stepEntries[step] || [];
        entries.forEach((entry) => {
            if (typeof entry.setup === 'function') {
                entry.setup();
            }
        });
    }

    escapeHTML(value) {
        return String(value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    createStatusMessage(iconClass, statusType, message) {
        const safeMessage = message ? String(message) : '';
        return `
            <div class="status-message status-${statusType}">
                <i class="${iconClass}"></i>
                ${this.escapeHTML(safeMessage)}
            </div>
        `;
    }

    createDetailsSection(title, details) {
        if (!details) return '';
        return `
            <div class="progress-details">
                <h4><i class="fas fa-info-circle"></i> ${this.escapeHTML(title)}</h4>
                <p>${this.escapeHTML(details)}</p>
            </div>
        `;
    }

    createSubstepsSection(substeps) {
        if (!Array.isArray(substeps) || substeps.length === 0) return '';
        const items = substeps.map((step) => `<li><i class="fas fa-clock"></i> ${this.escapeHTML(step)}</li>`).join('');
        return `
            <div class="progress-substeps">
                <h4><i class="fas fa-tasks"></i> Current Tasks</h4>
                <ul class="substeps-list">${items}</ul>
            </div>
        `;
    }

    createParametersSection(parameters) {
        if (!parameters || Object.keys(parameters).length === 0) return '';

        const parameterItems = Object.entries(parameters).map(([key, value]) => {
            let displayValue = value;
            if (Array.isArray(value)) {
                displayValue = value.join(', ');
            } else if (value && typeof value === 'object') {
                displayValue = JSON.stringify(value);
            }
            return `
                <li>
                    <span class="param-key">${this.escapeHTML(key)}:</span>
                    <span class="param-value">${this.escapeHTML(displayValue)}</span>
                </li>
            `;
        }).join('');

        return `
            <div class="progress-details">
                <h4><i class="fas fa-list-ul"></i> Extracted Parameters</h4>
                <ul class="parameters-list">${parameterItems}</ul>
            </div>
        `;
    }

    wrapProgressEntry(content) {
        return `<div class="progress-entry">${content}</div>`;
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

        const request = {
            destination_query: document.getElementById('destination-query').value,
            travel_dates: document.getElementById('travel-dates').value,
            budget: document.getElementById('budget').value,
            origin: document.getElementById('origin').value,
            group_size: document.getElementById('group-size').value,
            traveler_type: document.getElementById('traveler-type').value,
            mock_mode: document.getElementById('mock-mode').checked
        };

        if (!request.destination_query.trim()) {
            this.showMessage('Please describe what kind of trip you\'re looking for.', 'warning');
            return;
        }

        this.isPlanning = true;
        this.currentRequest = request;
        this.resetProgressState();

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
        this.sseBuffer = '';
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

            const chunk = decoder.decode(value, { stream: true });
            this.sseBuffer += chunk;

            const events = this.sseBuffer.split('\n\n');
            this.sseBuffer = events.pop();

            for (const event of events) {
                const lines = event.split('\n');
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

        if (this.sseBuffer.trim()) {
            const remainingLines = this.sseBuffer.split('\n');
            for (const line of remainingLines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        await this.handlePlanningUpdate(data);
                    } catch (e) {
                        console.error('Error parsing remaining SSE data:', e);
                    }
                }
            }
        }
    }

    async handlePlanningUpdate(data) {
        try {
            console.log('📥 Received update:', data);
            
            // Validate data structure
            if (!data || typeof data !== 'object') {
                console.error('❌ Invalid data received:', data);
                return;
            }
            
            if (!data.type) {
                console.error('❌ Missing type in data:', data);
                return;
            }
            
            console.log('📥 Processing update type:', data.type, 'message:', data.message);
            switch (data.type) {
                case 'step':
                    this.updateStep(data.step, data.message, data.details, data.substeps);
                    break;
                case 'progress_update':
                    console.log('📤 Updating progress message:', data.message);
                    this.updateProgressMessage(data.message, data.details, data.parameters);
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
            default:
                console.warn('⚠️ Unknown update type:', data.type, data);
                // Try to show the message if it exists
                if (data.message) {
                    this.updateProgressMessage(data.message, data.details);
                }
                break;
            }
        } catch (error) {
            console.error('❌ Error handling planning update:', error);
            console.error('❌ Error stack:', error.stack);
            console.error('❌ Data that caused error:', data);
            console.error('❌ Data type:', typeof data);
            console.error('❌ Data keys:', data ? Object.keys(data) : 'null');
            this.showMessage(`Error processing update: ${error.message}`, 'error');
        }
    }

    updateStep(step, message, details = null, substeps = null) {
        this.currentStep = step;
        this.maxStepReached = Math.max(this.maxStepReached, step);
        this.activeStep = step;

        const statusMessage = this.createStatusMessage('fas fa-info-circle', 'info', message);
        const detailsSection = details ? this.createDetailsSection('Processing Details', details) : '';
        const substepsSection = this.createSubstepsSection(substeps);
        const entryHtml = this.wrapProgressEntry(`${statusMessage}${detailsSection}${substepsSection}`);

        this.addStepEntry(step, { html: entryHtml }, { replace: true, activate: true });
        this.updateStepIndicators(step);
    }

    updateProgressMessage(message, details = null, parameters = null) {
        const safeMessage = message ? String(message) : 'Processing...';
        const targetStep = this.currentStep || this.activeStep || 1;
        this.maxStepReached = Math.max(this.maxStepReached, targetStep);

        let iconClass = 'fas fa-info-circle';
        let statusType = 'info';
        const lowered = safeMessage.toLowerCase();
        if (safeMessage.includes('✅') || lowered.includes('success')) {
            iconClass = 'fas fa-check-circle';
            statusType = 'success';
        } else if (safeMessage.includes('⚠️') || lowered.includes('warning')) {
            iconClass = 'fas fa-exclamation-triangle';
            statusType = 'warning';
        } else if (safeMessage.includes('❌') || lowered.includes('error')) {
            iconClass = 'fas fa-exclamation-circle';
            statusType = 'error';
        }

        const statusMessage = this.createStatusMessage(iconClass, statusType, safeMessage);
        const detailsSection = this.createDetailsSection('Current Activity', details);
        const parametersSection = this.createParametersSection(parameters);
        const entryHtml = this.wrapProgressEntry(`${statusMessage}${detailsSection}${parametersSection}`);

        const shouldActivate = targetStep === this.activeStep;
        this.addStepEntry(targetStep, { html: entryHtml }, { activate: shouldActivate });
    }

    async handleUserInputRequired(data) {
        const step = this.currentStep || this.activeStep || 1;
        const formHtml = `
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

        const entryHtml = this.wrapProgressEntry(
            `${this.createStatusMessage('fas fa-exclamation-triangle', 'warning', data.message)}${formHtml}`
        );

        this.addStepEntry(step, {
            html: entryHtml,
            setup: () => {
                const form = document.getElementById('user-input-form');
                if (form && !form.dataset.bound) {
                    form.dataset.bound = 'true';
                    form.addEventListener('submit', async (e) => {
                        e.preventDefault();
                        const formData = new FormData(e.target);
                        const inputData = Object.fromEntries(formData.entries());

                        const response = await fetch('/api/user-input', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(inputData)
                        });

                        if (response.ok) {
                            const currentEntries = this.stepEntries[step] || [];
                            this.stepEntries[step] = currentEntries.filter((entry) => !entry.html.includes('user-input-form'));
                            const confirmationHtml = this.wrapProgressEntry(
                                this.createStatusMessage('fas fa-check-circle', 'success', 'Thanks! Continuing with your input...')
                            );
                            this.addStepEntry(step, { html: confirmationHtml }, { activate: true });
                        }
                    });
                }
            }
        }, { activate: true });
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
        const step = this.currentStep || this.activeStep || 1;
        const destinationsHtml = data.destinations.map((dest, index) => `
            <div class="destination-card">
                <div class="destination-image">
                    ${dest.image_url ?
                        `<img src="${dest.image_url}" alt="${dest.name}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                         <div style="display: none;"><i class="fas fa-map-marker-alt"></i> ${dest.name}</div>` :
                        `<div><i class="fas fa-map-marker-alt"></i> ${dest.name}</div>`
                    }
                </div>
                <div class="destination-content">
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
            </div>
        `).join('');

        const entryHtml = this.wrapProgressEntry(`
            ${this.createStatusMessage('fas fa-map-marked-alt', 'info', `Found ${data.destinations.length} destination options for you!`)}
            <div class="user-input-section">
                <h3>Please choose your preferred destination:</h3>
                <form id="destination-choice-form">
                    ${destinationsHtml}
                    <button type="submit" class="btn">
                        <i class="fas fa-check"></i> Select Destination
                    </button>
                </form>
            </div>
        `);

        this.addStepEntry(step, {
            html: entryHtml,
            setup: () => {
                const form = document.getElementById('destination-choice-form');
                if (form && !form.dataset.bound) {
                    form.dataset.bound = 'true';
                    form.addEventListener('submit', async (e) => {
                        e.preventDefault();
                        const formData = new FormData(e.target);
                        const choice = formData.get('destination_choice');

                        const response = await fetch('/api/destination-choice', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ choice: parseInt(choice, 10) })
                        });

                        if (response.ok) {
                            const currentEntries = this.stepEntries[step] || [];
                            this.stepEntries[step] = currentEntries.filter((entry) => !entry.html.includes('destination-choice-form'));
                            const confirmationHtml = this.wrapProgressEntry(
                                this.createStatusMessage('fas fa-check-circle', 'success', 'Destination selected! Finding the best options for you...')
                            );
                            this.addStepEntry(step, { html: confirmationHtml }, { activate: true });
                            this.updateStep(this.currentStep + 1, 'Selected destination! Finding travel options...');
                        }
                    });
                }
            }
        }, { activate: true });
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
        try {
            // Ensure message is a string
            const safeMessage = message ? String(message) : 'An error occurred';
            const safeType = type || 'error';
            
            const messageDiv = document.createElement('div');
            messageDiv.className = `status-message status-${safeType}`;
            messageDiv.innerHTML = `
                <i class="fas fa-${safeType === 'success' ? 'check-circle' : safeType === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                ${safeMessage}
            `;

            // Insert at the top of the container
            const container = document.querySelector('.container');
            if (container) {
                container.insertBefore(messageDiv, container.firstChild);

                // Remove after 5 seconds
                setTimeout(() => {
                    if (messageDiv.parentNode) {
                        messageDiv.remove();
                    }
                }, 5000);
            } else {
                console.error('❌ Container not found for showMessage');
            }
        } catch (error) {
            console.error('❌ Error in showMessage:', error);
            console.error('❌ Message:', message, 'Type:', type);
        }
    }

    cancelPlanning() {
        this.isPlanning = false;
        document.getElementById('plan-trip-btn').disabled = false;
        document.getElementById('progress-card').classList.remove('active');
        this.resetProgressState();
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
