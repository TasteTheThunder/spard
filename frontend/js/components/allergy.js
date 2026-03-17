/**
 * Allergy Management Component for SPARD
 * Handles user allergy input, storage, and display
 */
class AllergyComponent {
    constructor() {
        this.userAllergies = [];
    }

    addAllergy() {
        console.log('DEBUG: addAllergy function called');
        
        const allergyInput = document.getElementById('allergyInput');
        const allergyName = allergyInput.value.trim();
        
        console.log('DEBUG: Allergy input value:', allergyName);
        
        if (!allergyName) {
            console.log('DEBUG: No allergy name entered');
            alert('Please enter an allergy name');
            return;
        }
        
        // Check if allergy already exists
        if (this.userAllergies.some(allergy => allergy.toLowerCase() === allergyName.toLowerCase())) {
            console.log('DEBUG: Allergy already exists');
            alert('This allergy is already in your list');
            allergyInput.value = '';
            return;
        }
        
        // Add allergy to list
        this.userAllergies.push(allergyName);
        console.log('DEBUG: Added allergy. Current list:', this.userAllergies);
        
        // Save to localStorage
        window.storageService.setItem('userAllergies', JSON.stringify(this.userAllergies));
        console.log('DEBUG: Saved to localStorage');
        
        // Update display
        this.displayAllergies();
        console.log('DEBUG: Updated display');
        
        // Clear input
        allergyInput.value = '';
        
        // Update check button state
        window.appComponent.updateCheckButtonState();
        console.log('DEBUG: addAllergy function completed');
    }

    removeAllergy(allergyToRemove) {
        this.userAllergies = this.userAllergies.filter(allergy => allergy !== allergyToRemove);
        
        // Save to localStorage
        window.storageService.setItem('userAllergies', JSON.stringify(this.userAllergies));
        
        // Update display
        this.displayAllergies();
        
        // Update check button state
        window.appComponent.updateCheckButtonState();
    }

    displayAllergies() {
        console.log('DEBUG: displayAllergies called with:', this.userAllergies);
        
        const allergiesDisplay = document.getElementById('allergiesDisplay');
        
        if (!allergiesDisplay) {
            console.error('DEBUG: allergiesDisplay element not found!');
            return;
        }
        
        if (this.userAllergies.length === 0) {
            console.log('DEBUG: No allergies to display');
            allergiesDisplay.classList.remove('show');
            return;
        }
        
        allergiesDisplay.classList.add('show');
        
        const allergiesHtml = `
            <h4>📋 Your Allergies:</h4>
            <div class="allergies-list">
                ${this.userAllergies.map(allergy => `
                    <div class="allergy-tag">
                        ${allergy}
                        <button class="remove-allergy" onclick="window.allergyComponent.removeAllergy('${allergy}')" title="Remove allergy">
                            ×
                        </button>
                    </div>
                `).join('')}
            </div>
        `;
        
        allergiesDisplay.innerHTML = allergiesHtml;
        console.log('DEBUG: Allergies display updated with HTML:', allergiesHtml);
    }

    loadSavedAllergies() {
        console.log('DEBUG: loadSavedAllergies called');
        
        const savedAllergies = window.storageService.getItem('userAllergies');
        console.log('DEBUG: Raw saved allergies from localStorage:', savedAllergies);
        
        if (savedAllergies) {
            try {
                this.userAllergies = JSON.parse(savedAllergies);
                console.log('DEBUG: Parsed user allergies:', this.userAllergies);
                this.displayAllergies();
            } catch (e) {
                console.error('Error loading saved allergies:', e);
                this.userAllergies = [];
            }
        } else {
            console.log('DEBUG: No saved allergies found in localStorage');
            this.userAllergies = [];
        }
        
        console.log('DEBUG: Final userAllergies array after loading:', this.userAllergies);
    }

    clearAllergies() {
        this.userAllergies = [];
        
        // Clear from localStorage
        window.storageService.removeItem('userAllergies');
        
        // Clear UI displays
        const allergiesDisplay = document.getElementById('allergiesDisplay');
        
        if (allergiesDisplay) {
            allergiesDisplay.innerHTML = '';
            allergiesDisplay.classList.remove('show');
        }
        
        // Clear allergy input
        const allergyInput = document.getElementById('allergyInput');
        if (allergyInput) {
            allergyInput.value = '';
        }
        
        console.log('DEBUG: All allergies cleared');
    }

    getAllergies() {
        return [...this.userAllergies]; // Return a copy to prevent external modification
    }

    hasAllergies() {
        return this.userAllergies.length > 0;
    }

    setupEventListeners() {
        // Allergy input listeners
        const addAllergyBtn = document.getElementById('addAllergyBtn');
        const allergyInput = document.getElementById('allergyInput');
        
        if (addAllergyBtn) {
            console.log('DEBUG: Setting up add allergy button listener');
            addAllergyBtn.addEventListener('click', () => this.addAllergy());
        } else {
            console.error('DEBUG: addAllergyBtn element not found!');
        }
        
        if (allergyInput) {
            console.log('DEBUG: Setting up allergy input keypress listener');
            allergyInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.addAllergy();
                }
            });
        } else {
            console.error('DEBUG: allergyInput element not found!');
        }
    }
}

// Export as global
window.allergyComponent = new AllergyComponent();