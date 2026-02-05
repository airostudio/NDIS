/**
 * Velma Frontend Configuration
 * Configure API endpoint based on environment
 */

window.VELMA_CONFIG = {
    // API Configuration
    // For local development: 'http://localhost:8000'
    // For production: Set your backend API URL
    // Leave empty to use demo mode (no backend required)
    API_BASE_URL: '',

    // Demo mode (no backend required)
    // Set to true to enable demo mode with simulated responses
    DEMO_MODE: true,

    // Company Information
    COMPANY_NAME: 'Your NDIS Company',

    // Feature Flags
    FEATURES: {
        CHAT: true,
        DASHBOARD: true,
        HR: true,
        PAYROLL: true,
        CALENDAR: true,
        TASKS: true
    }
};

// Auto-detect environment
(function() {
    const hostname = window.location.hostname;

    // Local development
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        window.VELMA_CONFIG.API_BASE_URL = 'http://localhost:8000';
        window.VELMA_CONFIG.DEMO_MODE = false;
    }
    // Vercel deployment (static only - enable demo mode)
    else if (hostname.includes('vercel.app')) {
        window.VELMA_CONFIG.DEMO_MODE = true;
        console.info('Velma: Running in demo mode (Vercel deployment)');
        console.info('To connect to your backend API, set VELMA_CONFIG.API_BASE_URL in config.js');
    }
    // Custom domain (configure API_BASE_URL above)
    else {
        if (!window.VELMA_CONFIG.API_BASE_URL && !window.VELMA_CONFIG.DEMO_MODE) {
            console.warn('Velma: No API_BASE_URL configured. Enable DEMO_MODE or set API_BASE_URL');
            window.VELMA_CONFIG.DEMO_MODE = true;
        }
    }
})();
