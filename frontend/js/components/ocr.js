/**
 * OCR Component for SPARD
 * Now uses Gemini OCR which directly returns MEDICINES, not text
 */
class OCRComponent {
  constructor() {
    this.isProcessingA = false;
    this.isProcessingB = false;
  }

  // ---------------------------
  // FILE UPLOAD HANDLER
  // ---------------------------
  async handleFileUpload(event) {
    const file = event.target.files[0];
    const isDocA = event.target.id === "prescriptionA";
    if (!file) return;

    if (!file.type.match("image.*")) {
      alert("Please upload a valid image (PNG, JPG, JPEG).");
      return;
    }

    this.showPreview(file, isDocA ? "previewA" : "previewB");
    await this.performOCR(file, isDocA);
  }

  // ---------------------------
  // PREVIEW IMAGE
  // ---------------------------
  showPreview(file, containerId) {
    const reader = new FileReader();
    const container = document.getElementById(containerId);

    reader.onload = (e) => {
      container.innerHTML = `<img src="${e.target.result}" />`;
    };

    reader.readAsDataURL(file);
  }

  // ---------------------------
  // GEMINI OCR PROCESSING
  // ---------------------------
  async performOCR(file, isDocA) {
    const progressId = isDocA ? "progressA" : "progressB";
    const progress = document.getElementById(progressId);

    progress.style.display = "block";
    progress.innerHTML = `<div class="progress-bar" style="width:20%"></div>`;

    try {
      const response = await window.apiService.processOCR(file);

      progress.innerHTML = `<div class="progress-bar" style="width:100%"></div>`;

      if (!response.success) {
        throw new Error("OCR failed");
      }

      const medicines = response.medicines;

      window.medicineComponent.storeMedicines(medicines, isDocA);

      window.medicineComponent.displayExtractedMedicines(
        medicines,
        isDocA ? "medicinesA" : "medicinesB",
        "gemini"
      );

      window.appComponent.updateCheckButtonState();
    } catch (error) {
      progress.innerHTML = `<p style="color:red">OCR failed. Try again.</p>`;
    }

    setTimeout(() => (progress.style.display = "none"), 1500);
  }

  // ---------------------------
  // DRAG & DROP SUPPORT
  // ---------------------------
  setupDragAndDrop(boxId, inputId) {
    const box = document.getElementById(boxId);
    const input = document.getElementById(inputId);

    if (!box || !input) return;

    // highlight when dragging
    box.addEventListener("dragover", (e) => {
      e.preventDefault();
      box.classList.add("dragover");
    });

    box.addEventListener("dragleave", (e) => {
      e.preventDefault();
      box.classList.remove("dragover");
    });

    // handle drop event
    box.addEventListener("drop", (e) => {
      e.preventDefault();
      box.classList.remove("dragover");

      const file = e.dataTransfer.files[0];
      if (!file) return;

      input.files = e.dataTransfer.files; // assign dropped file
      this.handleFileUpload({ target: input }); // process as normal upload
    });
  }

  getProcessingState() {
    return {
      isProcessingA: this.isProcessingA,
      isProcessingB: this.isProcessingB,
    };
  }
}

window.ocrComponent = new OCRComponent();
