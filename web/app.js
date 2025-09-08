/**
 * MoMo Data Analysis Dashboard - Main Application
 * Handles the main application logic and initialization
 */

class MoMoDashboard {
    constructor() {
        // Initialize components
        this.chartHandler = new ChartHandler();
        this.currentView = 'overview';
        
        // Initialize event listeners
        this.initEventListeners();
    }
    
    /**
     * Initialize event listeners for navigation and UI interactions
     */
    initEventListeners() {
        // Navigation
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', () => {
                const targetView = item.getAttribute('data-view');
                this.switchView(targetView);
            });
        });
        
        // Initialize view-specific event listeners
        this.initOverviewListeners();
        this.initTransactionListeners();
        this.initAnalyticsListeners();
    }
    
    /**
     * Initialize event listeners for the Overview view
     */
    initOverviewListeners() {
        // Add any overview-specific event listeners here
    }
    
    /**
     * Initialize event listeners for the Transactions view
     */
    initTransactionListeners() {
        // Add any transaction-specific event listeners here
    }
    
    /**
     * Initialize event listeners for the Analytics view
     */
    initAnalyticsListeners() {
        // Add any analytics-specific event listeners here
    }
    
    /**
     * Switch between different views (overview, transactions, analytics)
     */
    switchView(viewName) {
        if (viewName === this.currentView) return;
        
        // Update active nav item
        document.querySelectorAll('.nav-item').forEach(item => {
            if (item.getAttribute('data-view') === viewName) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
        
        // Show selected view, hide others
        document.querySelectorAll('.view').forEach(view => {
            if (view.id === viewName) {
                view.classList.add('active');
            } else {
                view.classList.remove('active');
            }
        });
        
        this.currentView = viewName;
    }
    
    /**
     * Initialize the dashboard
     */
    async init() {
        try {
            // Show loading state
            document.getElementById('loading').style.display = 'flex';
            
            // Initialize chart handler
            await this.chartHandler.init();
            
            // Hide loading state
            document.getElementById('loading').style.display = 'none';
            
            // Set default view
            this.switchView('overview');
        } catch (error) {
            console.error('Error initializing dashboard:', error);
            this.showError('Failed to initialize dashboard. Please try again later.');
            document.getElementById('loading').style.display = 'none';
        }
    }
    
    /**
     * Show error message to user
     */
    showError(message) {
        const errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        errorElement.textContent = message;
        
        document.body.appendChild(errorElement);
        
        // Remove after 5 seconds
        setTimeout(() => {
            errorElement.classList.add('fade-out');
            setTimeout(() => {
                document.body.removeChild(errorElement);
            }, 500);
        }, 5000);
    }
}

// Initialize the dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new MoMoDashboard();
    dashboard.init();
});