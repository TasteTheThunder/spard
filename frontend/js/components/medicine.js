/**
 * Medicine Component for SPARD
 * Stores and displays medicine lists extracted from Gemini OCR
 */
class MedicineComponent {
    constructor() {
        this.doctorAMedicines = [];
        this.doctorBMedicines = [];
    }

    storeMedicines(medicines, isDocA) {
        if (isDocA) {
            this.doctorAMedicines = medicines;
            window.storageService.setItem("doctorA", JSON.stringify(medicines));
        } else {
            this.doctorBMedicines = medicines;
            window.storageService.setItem("doctorB", JSON.stringify(medicines));
        }
    }

    displayExtractedMedicines(medicines, containerId, source) {
        const container = document.getElementById(containerId);

        if (!medicines || medicines.length === 0) {
            container.innerHTML = `<p>No medicines detected.</p>`;
        } else {
            container.innerHTML = `
                <h3>💊 Medicines (${medicines.length})</h3>
                <div class="medicine-list">
                    ${medicines.map(m => `<span class="medicine-tag">${m}</span>`).join("")}
                </div>
            `;
        }

        container.style.display = "block";
    }

    loadSavedMedicines() {
        const A = window.storageService.getItem("doctorA");
        const B = window.storageService.getItem("doctorB");

        if (A) {
            this.doctorAMedicines = JSON.parse(A);
            this.displayExtractedMedicines(this.doctorAMedicines, "medicinesA");
        }

        if (B) {
            this.doctorBMedicines = JSON.parse(B);
            this.displayExtractedMedicines(this.doctorBMedicines, "medicinesB");
        }
    }

    getMedicines() {
        return {
            doctorA: this.doctorAMedicines,
            doctorB: this.doctorBMedicines
        };
    }

    hasMedicines() {
        return this.doctorAMedicines.length > 0 && this.doctorBMedicines.length > 0;
    }

    clearMedicineData() {
        window.storageService.removeItem("doctorA");
        window.storageService.removeItem("doctorB");

        this.doctorAMedicines = [];
        this.doctorBMedicines = [];

        document.getElementById("medicinesA").innerHTML = "";
        document.getElementById("medicinesB").innerHTML = "";
        document.getElementById("medicinesA").style.display = "none";
        document.getElementById("medicinesB").style.display = "none";
    }
}

window.medicineComponent = new MedicineComponent();
