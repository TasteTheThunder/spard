/**
 * Storage Service for SPARD
 * Handles localStorage operations and data persistence
 */
class StorageService {
    constructor() {
        this.prefix = 'spard_';
    }

    setItem(key, value) {
        try {
            localStorage.setItem(this.prefix + key, value);
            console.log(`StorageService: Set ${key} =`, value);
            return true;
        } catch (error) {
            console.error(`StorageService: Error setting ${key}:`, error);
            return false;
        }
    }

    getItem(key) {
        try {
            const value = localStorage.getItem(this.prefix + key);
            console.log(`StorageService: Get ${key} =`, value);
            return value;
        } catch (error) {
            console.error(`StorageService: Error getting ${key}:`, error);
            return null;
        }
    }

    removeItem(key) {
        try {
            localStorage.removeItem(this.prefix + key);
            console.log(`StorageService: Removed ${key}`);
            return true;
        } catch (error) {
            console.error(`StorageService: Error removing ${key}:`, error);
            return false;
        }
    }

    clear() {
        try {
            // Get all keys that start with our prefix
            const keysToRemove = [];
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key && key.startsWith(this.prefix)) {
                    keysToRemove.push(key);
                }
            }
            
            // Remove all our keys
            keysToRemove.forEach(key => localStorage.removeItem(key));
            console.log('StorageService: Cleared all SPARD data');
            return true;
        } catch (error) {
            console.error('StorageService: Error clearing data:', error);
            return false;
        }
    }

    // Session management
    getCurrentUser() {
        const userData = this.getItem('currentUser');
        return userData ? JSON.parse(userData) : null;
    }

    setCurrentUser(userData) {
        return this.setItem('currentUser', JSON.stringify(userData));
    }

    clearCurrentUser() {
        return this.removeItem('currentUser');
    }

    getLastSessionId() {
        return this.getItem('lastSessionId');
    }

    setLastSessionId(sessionId) {
        return this.setItem('lastSessionId', sessionId);
    }

    // Data management utilities
    checkAndLoadSavedData() {
        console.log('DEBUG: checkAndLoadSavedData called');
        
        // Check if this is a fresh login by comparing session info
        const currentUser = this.getCurrentUser();
        const lastSessionId = this.getLastSessionId();
        
        console.log('DEBUG: Current user:', currentUser);
        console.log('DEBUG: Last session ID:', lastSessionId);
        
        if (currentUser && currentUser.session_id) {
            if (lastSessionId !== currentUser.session_id) {
                console.log('DEBUG: Fresh login detected - clearing old data');
                // Fresh login - clear old medicine data but NOT allergies
                window.medicineComponent.clearMedicineData();
                this.setLastSessionId(currentUser.session_id);
            } else {
                console.log('DEBUG: Same session - loading saved data');
                // Same session - load saved medicines
                window.medicineComponent.loadSavedMedicines();
            }
            // Always load allergies regardless of session
            window.allergyComponent.loadSavedAllergies();
        } else {
            console.log('DEBUG: No user logged in - clearing everything');
            // No user logged in - clear everything
            this.clearAllData();
            this.removeItem('lastSessionId');
        }
    }

    clearAllData() {
        console.log('DEBUG: clearAllData called');
        
        // Clear medicine data
        window.medicineComponent.clearMedicineData();
        
        // Clear allergy data
        window.allergyComponent.clearAllergies();
        
        // Hide any displayed results
        window.conflictComponent.hideResults();
        
        console.log('DEBUG: All data cleared');
    }

    clearMedicineDataOnly() {
        console.log('DEBUG: clearMedicineDataOnly called');
        
        // Clear only medicine data, preserve allergies
        window.medicineComponent.clearMedicineData();
        
        console.log('DEBUG: Medicine data cleared, allergies preserved');
    }

    hasValidSession() {
        const currentUser = this.getCurrentUser();
        return currentUser && currentUser.session_id;
    }

    // Export/Import functionality
    exportAllData() {
        const currentUser = this.getCurrentUser();
        const medicines = window.medicineComponent.getMedicines();
        const allergies = window.allergyComponent.getAllergies();
        
        const exportData = {
            version: '1.0',
            timestamp: new Date().toISOString(),
            user: currentUser ? currentUser.name : 'Anonymous',
            medicines: medicines,
            allergies: allergies
        };
        
        return exportData;
    }

    importData(importedData) {
        try {
            if (!importedData || typeof importedData !== 'object') {
                throw new Error('Invalid data format');
            }
            
            // Import allergies if present
            if (importedData.allergies && Array.isArray(importedData.allergies)) {
                this.setItem('userAllergies', JSON.stringify(importedData.allergies));
                window.allergyComponent.userAllergies = [...importedData.allergies];
                window.allergyComponent.displayAllergies();
            }
            
            // Import medicines if present
            if (importedData.medicines && typeof importedData.medicines === 'object') {
                if (importedData.medicines.doctorA && Array.isArray(importedData.medicines.doctorA)) {
                    this.setItem('doctorA', JSON.stringify(importedData.medicines.doctorA));
                    window.medicineComponent.doctorAMedicines = [...importedData.medicines.doctorA];
                    window.medicineComponent.displayExtractedMedicines(importedData.medicines.doctorA, 'medicinesA');
                }
                
                if (importedData.medicines.doctorB && Array.isArray(importedData.medicines.doctorB)) {
                    this.setItem('doctorB', JSON.stringify(importedData.medicines.doctorB));
                    window.medicineComponent.doctorBMedicines = [...importedData.medicines.doctorB];
                    window.medicineComponent.displayExtractedMedicines(importedData.medicines.doctorB, 'medicinesB');
                }
            }
            
            // Update UI state
            if (window.appComponent && window.appComponent.updateCheckButtonState) {
                window.appComponent.updateCheckButtonState();
            }
            
            console.log('StorageService: Data imported successfully');
            return true;
            
        } catch (error) {
            console.error('StorageService: Error importing data:', error);
            return false;
        }
    }
}

// Export as global
window.storageService = new StorageService();