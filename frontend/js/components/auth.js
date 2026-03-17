/**
 * Authentication Component for SPARD
 * Handles login/signup functionality
 */
class AuthComponent {
    constructor() {
        this.isLoading = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkExistingAuth();
    }

    setupEventListeners() {
        // Form submissions
        const loginForm = document.getElementById('loginForm');
        const signupForm = document.getElementById('signupForm');
        
        if (loginForm) {
            loginForm.addEventListener('submit', this.handleLogin.bind(this));
        }
        
        if (signupForm) {
            signupForm.addEventListener('submit', this.handleSignup.bind(this));
        }

        // Form switching
        const showSignupLink = document.getElementById('showSignup');
        const showLoginLink = document.getElementById('showLogin');
        
        if (showSignupLink) {
            showSignupLink.addEventListener('click', this.showSignupForm.bind(this));
        }
        
        if (showLoginLink) {
            showLoginLink.addEventListener('click', this.showLoginForm.bind(this));
        }
    }

    async checkExistingAuth() {
        const savedUser = localStorage.getItem('currentUser');
        
        // If we're on login page and have valid user, redirect to main app
        if (window.location.pathname.includes('login.html')) {
            if (savedUser) {
                try {
                    const userData = JSON.parse(savedUser);
                    if (userData.session_id) {
                        const response = await window.apiService.verifySession(userData.session_id);
                        if (response.success) {
                            this.redirectToMainApp();
                            return;
                        }
                    }
                } catch (error) {
                    console.error('Auth check failed:', error);
                }
                localStorage.removeItem('currentUser');
            }
            return;
        }
        
        // If we're on main app and no user, redirect to login
        if (!savedUser) {
            window.location.href = 'login.html';
            return;
        }
        
        try {
            const userData = JSON.parse(savedUser);
            if (!userData.session_id) {
                localStorage.clear();
                window.location.href = 'login.html';
                return;
            }
            
            // Verify session with backend
            const response = await window.apiService.verifySession(userData.session_id);
            if (!response.success) {
                localStorage.removeItem('currentUser');
                window.location.href = 'login.html';
                return;
            }
            
            // Setup main app if authenticated
            this.setupMainApp(userData);
            
        } catch (error) {
            console.error('Auth check failed:', error);
            localStorage.removeItem('currentUser');
            window.location.href = 'login.html';
        }
    }
    
    setupMainApp(userData) {
        // Update user display
        const userName = document.getElementById('userName');
        if (userName) {
            userName.textContent = `Welcome, ${userData.name}!`;
        }
        
        // Setup logout button
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', async (e) => {
                e.preventDefault();
                await this.logout();
            });
        }
        
        console.log('Main app setup completed');
    }

    async handleLogin(e) {
        e.preventDefault();
        if (this.isLoading) return;

        const email = document.getElementById('loginEmail').value.trim();
        const password = document.getElementById('loginPassword').value;

        if (!email || !password) {
            this.showMessage('Please fill in all fields', 'error');
            return;
        }

        this.setLoading(true);

        try {
            const result = await window.apiService.login(email, password);
            console.log('Login result:', result);
            
            if (result.success) {
                // Merge session_id into user object for consistent storage
                const userWithSession = {
                    ...result.user,
                    session_id: result.session_id
                };
                console.log('Storing user data:', userWithSession);
                localStorage.setItem('currentUser', JSON.stringify(userWithSession));
                this.showMessage('Login successful! Redirecting...', 'success');
                setTimeout(() => this.redirectToMainApp(), 1000);
            } else {
                console.log('Login failed:', result);
                this.showMessage(result.message || result.error || 'Login failed', 'error');
            }
        } catch (error) {
            this.showMessage('Network error. Please try again.', 'error');
            console.error('Login error:', error);
        } finally {
            this.setLoading(false);
        }
    }

    async handleSignup(e) {
        e.preventDefault();
        if (this.isLoading) return;

        const name = document.getElementById('signupName').value.trim();
        const email = document.getElementById('signupEmail').value.trim();
        const password = document.getElementById('signupPassword').value;

        if (!name || !email || !password) {
            this.showMessage('Please fill in all fields', 'error');
            return;
        }

        if (password.length < 6) {
            this.showMessage('Password must be at least 6 characters', 'error');
            return;
        }

        this.setLoading(true);

        try {
            const result = await window.apiService.signup(name, email, password);
            
            if (result.success) {
                this.showMessage('Account created successfully! Please sign in.', 'success');
                setTimeout(() => this.showLoginForm({preventDefault: () => {}}), 2000);
            } else {
                this.showMessage(result.message || result.error || 'Registration failed', 'error');
            }
        } catch (error) {
            this.showMessage('Network error. Please try again.', 'error');
            console.error('Signup error:', error);
        } finally {
            this.setLoading(false);
        }
    }

    showLoginForm(e) {
        e.preventDefault();
        document.getElementById('signupForm').classList.add('hidden');
        document.getElementById('loginForm').classList.remove('hidden');
        this.clearMessage();
    }

    showSignupForm(e) {
        e.preventDefault();
        document.getElementById('loginForm').classList.add('hidden');
        document.getElementById('signupForm').classList.remove('hidden');
        this.clearMessage();
    }

    setLoading(loading) {
        this.isLoading = loading;
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            if (loading) {
                overlay.classList.remove('hidden');
            } else {
                overlay.classList.add('hidden');
            }
        }
    }

    showMessage(text, type) {
        const container = document.getElementById('messageContainer');
        if (container) {
            container.innerHTML = `<div class="message ${type}">${text}</div>`;
            container.classList.add('show');
        }
    }

    clearMessage() {
        const container = document.getElementById('messageContainer');
        if (container) {
            container.classList.remove('show');
            container.innerHTML = '';
        }
    }

    redirectToMainApp() {
        window.location.href = 'index.html';
    }

    async logout() {
        console.log('Logout initiated');
        try {
            const currentUser = localStorage.getItem('currentUser');
            if (currentUser) {
                const userData = JSON.parse(currentUser);
                if (userData.session_id && window.apiService) {
                    console.log('Calling backend logout...');
                    await window.apiService.logout(userData.session_id);
                    console.log('Backend logout successful');
                }
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            // Always clear localStorage and redirect
            console.log('Clearing storage and redirecting to login');
            localStorage.clear();
            window.location.href = 'login.html';
        }
    }
}

// Initialize auth component when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.authComponent = new AuthComponent();
    });
} else {
    window.authComponent = new AuthComponent();
}