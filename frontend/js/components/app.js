/**
 * Main App Component for SPARD
 * Coordinates all components and handles application lifecycle
 */
class AppComponent {
  constructor() {
    this.isInitialized = false;
  }

  init() {
    if (this.isInitialized) {
      console.log("App already initialized");
      return;
    }

    console.log("DEBUG: Initializing SPARD Application");

    // Initialize event listeners
    this.initializeEventListeners();

    // Check and load saved data
    window.storageService.checkAndLoadSavedData();

    // Update initial UI state
    this.updateCheckButtonState();

    this.isInitialized = true;
    console.log("DEBUG: SPARD Application initialization complete");
  }

  initializeEventListeners() {
    console.log("DEBUG: Setting up main event listeners");

    // File upload listeners
    const prescriptionA = document.getElementById("prescriptionA");
    const prescriptionB = document.getElementById("prescriptionB");

    if (prescriptionA) {
      prescriptionA.addEventListener("change", (e) =>
        window.ocrComponent.handleFileUpload(e)
      );
    }

    if (prescriptionB) {
      prescriptionB.addEventListener("change", (e) =>
        window.ocrComponent.handleFileUpload(e)
      );
    }

    // Drag and drop listeners
    window.ocrComponent.setupDragAndDrop("uploadBoxA", "prescriptionA");
    window.ocrComponent.setupDragAndDrop("uploadBoxB", "prescriptionB");

    // Set up allergy component event listeners
    window.allergyComponent.setupEventListeners();

    // Button listeners
    const checkConflictsBtn = document.getElementById("checkConflicts");
    const clearAllBtn = document.getElementById("clearAll");

    if (checkConflictsBtn) {
      checkConflictsBtn.addEventListener("click", () =>
        window.conflictComponent.checkConflicts()
      );
    }

    if (clearAllBtn) {
      clearAllBtn.addEventListener("click", () => this.clearAll());
    }

    console.log("DEBUG: Event listeners setup completed");
  }

  updateCheckButtonState() {
    const checkButton = document.getElementById("checkConflicts");
    if (!checkButton) return;

    const hasMedicines = window.medicineComponent.hasMedicines();
    const ocrState = window.ocrComponent.getProcessingState();
    const notProcessing = !ocrState.isProcessingA && !ocrState.isProcessingB;

    checkButton.disabled = !(hasMedicines && notProcessing);

    console.log("DEBUG: Check button state updated -", {
      hasMedicines,
      notProcessing,
      disabled: checkButton.disabled,
    });
  }

  clearAll() {
    if (
      confirm(
        "Are you sure you want to clear all data? This will remove uploaded images and extracted medicines."
      )
    ) {
      // Clear all data
      window.storageService.clearAllData();

      // Reset OCR processing states
      window.ocrComponent.isProcessingA = false;
      window.ocrComponent.isProcessingB = false;

      // Clear file inputs
      const prescriptionA = document.getElementById("prescriptionA");
      const prescriptionB = document.getElementById("prescriptionB");

      if (prescriptionA) prescriptionA.value = "";
      if (prescriptionB) prescriptionB.value = "";

      // Clear previews
      const previewA = document.getElementById("previewA");
      const previewB = document.getElementById("previewB");

      if (previewA) previewA.innerHTML = "";
      if (previewB) previewB.innerHTML = "";

      // Hide progress bars
      const progressA = document.getElementById("progressA");
      const progressB = document.getElementById("progressB");

      if (progressA) progressA.style.display = "none";
      if (progressB) progressB.style.display = "none";

      // Reset upload boxes
      const uploadBoxA = document.getElementById("uploadBoxA");
      const uploadBoxB = document.getElementById("uploadBoxB");

      if (uploadBoxA) uploadBoxA.classList.remove("dragover");
      if (uploadBoxB) uploadBoxB.classList.remove("dragover");

      // Update button state
      this.updateCheckButtonState();

      console.log("DEBUG: All data cleared successfully");
    }
  }

  // Export functionality
  exportData() {
    try {
      const exportData = window.storageService.exportAllData();

      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `spard-data-${new Date().toISOString().split("T")[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      alert("Data exported successfully!");
      console.log("DEBUG: Data exported successfully");
    } catch (error) {
      console.error("Error exporting data:", error);
      alert("Error exporting data. Please try again.");
    }
  }

  // Import functionality
  importData(file) {
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const importedData = JSON.parse(e.target.result);

        const success = window.storageService.importData(importedData);

        if (success) {
          // Update button state after import
          this.updateCheckButtonState();
          alert("Data imported successfully!");
          console.log("DEBUG: Data imported successfully");
        } else {
          throw new Error("Import validation failed");
        }
      } catch (error) {
        console.error("Error importing data:", error);
        alert(
          "Error importing data. Please check the file format and try again."
        );
      }
    };

    reader.readAsText(file);
  }

  // Utility function for testing
  loadTestData() {
    const success = window.medicineComponent.testWithSampleData();
    if (success) {
      this.updateCheckButtonState();
      console.log("DEBUG: Test data loaded successfully");
    }
  }

  // Get current application state
  getAppState() {
    const medicines = window.medicineComponent.getMedicines();
    const allergies = window.allergyComponent.getAllergies();
    const ocrState = window.ocrComponent.getProcessingState();
    const user = window.storageService.getCurrentUser();

    return {
      initialized: this.isInitialized,
      user: user,
      medicines: medicines,
      allergies: allergies,
      processing: ocrState,
      hasMedicines: window.medicineComponent.hasMedicines(),
      hasAllergies: window.allergyComponent.hasAllergies(),
    };
  }

  // Handle application errors
  handleError(error, context = "") {
    console.error(`App Error${context ? " in " + context : ""}:`, error);

    const errorMessage = error.message || "An unexpected error occurred";
    alert(
      `Error: ${errorMessage}\n\nPlease try again or contact support if the problem persists.`
    );
  }

  // Cleanup function for page unload
  cleanup() {
    console.log("DEBUG: Cleaning up application");
    // Could add cleanup logic here if needed
  }
}

// Initialize app when DOM is ready
document.addEventListener("DOMContentLoaded", function () {
  // Create global app instance
  window.appComponent = new AppComponent();

  // Initialize the application
  window.appComponent.init();

  // Set up cleanup on page unload
  window.addEventListener("beforeunload", () => {
    window.appComponent.cleanup();
  });
});

// Make test function available globally for debugging
window.testWithSampleData = () => {
  if (window.appComponent) {
    window.appComponent.loadTestData();
  }
};
