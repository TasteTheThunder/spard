/**
 * Conflict Analysis Component for SPARD
 * Uses ONLY Gemini-based multi-prescription conflict API
 */
class ConflictComponent {
  async checkConflicts() {
    const meds = window.medicineComponent.getMedicines();
    const allergies = window.allergyComponent.getAllergies();

    if (!window.medicineComponent.hasMedicines()) {
      alert("Upload both prescriptions first.");
      return;
    }

    document.getElementById("loadingSection").style.display = "flex";

    try {
      const payload = {
        doctor_a_medicines: meds.doctorA,
        doctor_b_medicines: meds.doctorB,
        user_allergies: allergies,
      };

      const response = await window.apiService.checkMultiPrescriptionConflicts(
        payload
      );

      this.displayResults(response.analysis);
    } catch (error) {
      console.error(error);
      alert("Server error during conflict analysis.");
    }

    document.getElementById("loadingSection").style.display = "none";
  }

  displayResults(analysis) {
    const container = document.getElementById("resultsContent");
    const section = document.getElementById("resultsSection");

    let html = `
        <h2>AI Conflict Analysis</h2>
        <p><strong>Risk Level:</strong> ${analysis.risk_level}</p>
        <p>${analysis.analysis_summary}</p>
    `;

    // -----------------------------
    // 🟦 DRUG INTERACTIONS
    // -----------------------------
    if (analysis.drug_interactions && analysis.drug_interactions.length > 0) {
      html += `<h3>⚠ Drug Interactions</h3>`;

      html += analysis.drug_interactions
        .map((interaction) => {
          const medicines = interaction.medicines || [];

          const reason = interaction.reason || "Reason not provided";

          return `
                <div class="conflict-item">
                    <div class="conflict-pair">${medicines.join(" + ")}</div>
                    <div class="conflict-reason">${reason}</div>
                </div>
            `;
        })
        .join("");
    }

    // -----------------------------
    // 🟧 ALLERGY CONFLICTS
    // -----------------------------
    if (analysis.allergy_conflicts && analysis.allergy_conflicts.length > 0) {
      html += `<h3>⚠ Allergy Conflicts</h3>`;

      html += analysis.allergy_conflicts
        .map((conflict) => {
          const medicine = conflict.medicine || "Unknown medicine";
          const allergy = conflict.allergy || "Unknown allergy";
          const reason = conflict.reason || "Potential allergic reaction";

          return `
                <div class="conflict-item urgent">
                    <div class="conflict-pair">${medicine} vs ${allergy}</div>
                    <div class="conflict-reason">${reason}</div>
                </div>
            `;
        })
        .join("");
    }

    container.innerHTML = html;
    section.style.display = "block";
    section.scrollIntoView({ behavior: "smooth" });
  }

  hideResults() {
    const resultsSection = document.getElementById("resultsSection");
    const resultsContent = document.getElementById("resultsContent");

    if (resultsContent) {
      resultsContent.innerHTML = "";
    }
    if (resultsSection) {
      resultsSection.style.display = "none";
    }

    console.log("DEBUG: Results hidden");
  }
}

window.conflictComponent = new ConflictComponent();
