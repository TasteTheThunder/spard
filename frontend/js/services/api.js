/**
 * API Service for SPARD Frontend
 * Handles all HTTP requests to the backend
 */
class ApiService {
    constructor() {
        this.baseUrl = 'http://localhost:5000';
        this.checkBackendConnection();
    }

    // -------------------------------------------------------
    // Backend connection health check
    // -------------------------------------------------------
    async checkBackendConnection() {
    try {
        const response = await fetch(this.baseUrl + "/");
        if (!response.ok) {
            console.warn('Backend connection issue:', response.status);
        }
    } catch (error) {
        console.error('Backend not accessible:', error);
    }
}


    // -------------------------------------------------------
    // Core request handler
    // -------------------------------------------------------
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;

        const defaultOptions = {
            headers: {}
        };

        // Add user session token
        const user = this.getCurrentUser();
        if (user && user.session_id && !endpoint.includes("/auth")) {
            defaultOptions.headers["X-Session-Token"] = user.session_id;
        }

        const requestOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...(options.headers || {})
            }
        };

        const response = await fetch(url, requestOptions);

        let data;
        const contentType = response.headers.get("content-type") || "";

        if (contentType.includes("application/json")) {
            data = await response.json();
        } else {
            data = { success: false, error: "Non-JSON response", status: response.status };
        }

        if (!response.ok) {
            throw new Error(data.error || `HTTP ${response.status}`);
        }

        return data;
    }

    // -------------------------------------------------------
    // HTTP Methods
    // -------------------------------------------------------
    async get(endpoint, options = {}) {
        return this.request(endpoint, { method: "GET", ...options });
    }

    async post(endpoint, data = null, options = {}) {
        let reqOptions = { method: "POST", headers: {} };

        if (data instanceof FormData) {
            delete reqOptions.headers["Content-Type"]; // Let browser set it
            reqOptions.body = data;
        } else if (data) {
            reqOptions.headers["Content-Type"] = "application/json";
            reqOptions.body = JSON.stringify(data);
        }

        return this.request(endpoint, reqOptions);
    }

    // -------------------------------------------------------
    // User Session
    // -------------------------------------------------------
    getCurrentUser() {
        const userData = localStorage.getItem("currentUser");
        return userData ? JSON.parse(userData) : null;
    }

    // Auth endpoints
    async login(email, password) {
        return this.post("/auth/login", { email, password });
    }

    async signup(name, email, password) {
        return this.post("/auth/signup", { name, email, password });
    }

    async logout(sessionId) {
        return this.post("/auth/logout", { session_id: sessionId });
    }

    async verifySession(sessionId) {
        return this.post("/auth/verify", { session_id: sessionId });
    }

    // -------------------------------------------------------
    // OCR (now returns MEDICINES, not TEXT)
    // -------------------------------------------------------
    async processOCR(imageFile) {
        const formData = new FormData();
        formData.append("image", imageFile);
        return this.post("/api/ocr", formData);
    }

    // -------------------------------------------------------
    // Multi-prescription conflict analysis (MAIN ENDPOINT)
    // -------------------------------------------------------
    async checkMultiPrescriptionConflicts(data) {
        return this.post("/api/check-multi-prescription-conflicts", data);
    }
}

// Create global instance
window.apiService = new ApiService();
