/**
 * Velma Core JavaScript
 * Core utilities and shared functionality
 */

// API Configuration
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : '/api';

// Utility Functions
const VelmaUtils = {
    /**
     * Format date/time
     */
    formatTime(date) {
        const now = new Date();
        const diff = now - date;
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (seconds < 60) return 'Just now';
        if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        if (days < 7) return `${days} day${days > 1 ? 's' : ''} ago`;

        return date.toLocaleDateString('en-AU', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },

    /**
     * Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Generate unique ID
     */
    generateId() {
        return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    },

    /**
     * Escape HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * Parse markdown-like formatting
     */
    parseMarkdown(text) {
        // Simple markdown parsing
        return text
            // Bold
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Italic
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Code
            .replace(/`(.*?)`/g, '<code>$1</code>')
            // Line breaks
            .replace(/\n/g, '<br>');
    }
};

// Toast Notification System
const VelmaToast = {
    container: null,

    init() {
        this.container = document.getElementById('toastContainer');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toastContainer';
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        }
    },

    show(message, type = 'info', duration = 5000) {
        if (!this.container) this.init();

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const icons = {
            success: '<svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
            error: '<svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
            warning: '<svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>',
            info: '<svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>'
        };

        toast.innerHTML = `
            <div class="toast-icon">${icons[type]}</div>
            <div class="toast-content">
                <div class="toast-message">${VelmaUtils.escapeHtml(message)}</div>
            </div>
            <button class="toast-close" aria-label="Close">&times;</button>
        `;

        this.container.appendChild(toast);

        // Close button
        toast.querySelector('.toast-close').addEventListener('click', () => {
            this.hide(toast);
        });

        // Show toast
        setTimeout(() => toast.classList.add('show'), 10);

        // Auto-hide
        if (duration > 0) {
            setTimeout(() => this.hide(toast), duration);
        }

        return toast;
    },

    hide(toast) {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    },

    success(message, duration) {
        return this.show(message, 'success', duration);
    },

    error(message, duration) {
        return this.show(message, 'error', duration);
    },

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    },

    info(message, duration) {
        return this.show(message, 'info', duration);
    }
};

// API Client
const VelmaAPI = {
    /**
     * Make API request
     */
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'API request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    /**
     * Send chat message
     */
    async chat(message, context = {}) {
        return this.request('/api/chat', {
            method: 'POST',
            body: JSON.stringify({
                message,
                context,
                user_id: this.getUserId()
            })
        });
    },

    /**
     * Get health status
     */
    async health() {
        return this.request('/health');
    },

    /**
     * Get configuration
     */
    async getConfig() {
        return this.request('/api/config');
    },

    /**
     * Get user ID from session storage
     */
    getUserId() {
        let userId = sessionStorage.getItem('velma_user_id');
        if (!userId) {
            userId = VelmaUtils.generateId();
            sessionStorage.setItem('velma_user_id', userId);
        }
        return userId;
    }
};

// Modal System
const VelmaModal = {
    show(title, content, actions = []) {
        // Remove existing modal
        this.hide();

        // Create backdrop
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop';
        backdrop.id = 'modalBackdrop';

        // Create modal
        const modal = document.createElement('div');
        modal.className = 'modal';

        // Build actions HTML
        const actionsHTML = actions.length > 0
            ? `<div class="modal-footer">
                ${actions.map(action => `
                    <button class="btn ${action.className || 'btn-primary'}" data-action="${action.id}">
                        ${action.label}
                    </button>
                `).join('')}
            </div>`
            : '';

        modal.innerHTML = `
            <div class="modal-header">
                <h3 class="modal-title">${VelmaUtils.escapeHtml(title)}</h3>
                <button class="modal-close" aria-label="Close">&times;</button>
            </div>
            <div class="modal-body">
                ${content}
            </div>
            ${actionsHTML}
        `;

        backdrop.appendChild(modal);
        document.body.appendChild(backdrop);

        // Show modal
        setTimeout(() => backdrop.classList.add('show'), 10);

        // Close handlers
        const closeModal = () => this.hide();
        backdrop.addEventListener('click', (e) => {
            if (e.target === backdrop) closeModal();
        });
        modal.querySelector('.modal-close').addEventListener('click', closeModal);

        // Action handlers
        actions.forEach(action => {
            const btn = modal.querySelector(`[data-action="${action.id}"]`);
            if (btn && action.handler) {
                btn.addEventListener('click', () => {
                    action.handler();
                    if (action.closeOnClick !== false) closeModal();
                });
            }
        });

        return backdrop;
    },

    hide() {
        const backdrop = document.getElementById('modalBackdrop');
        if (backdrop) {
            backdrop.classList.remove('show');
            setTimeout(() => backdrop.remove(), 300);
        }
    }
};

// Menu Toggle (Mobile)
document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('show');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                    sidebar.classList.remove('show');
                }
            }
        });
    }

    // Initialize toast system
    VelmaToast.init();

    // Check API health
    VelmaAPI.health()
        .then(data => {
            console.log('Velma API Status:', data);
            const statusBadge = document.getElementById('statusBadge');
            if (statusBadge) {
                statusBadge.textContent = 'Online';
                statusBadge.className = 'badge badge-success';
            }
        })
        .catch(error => {
            console.error('Velma API offline:', error);
            const statusBadge = document.getElementById('statusBadge');
            if (statusBadge) {
                statusBadge.textContent = 'Offline';
                statusBadge.className = 'badge badge-error';
            }
            VelmaToast.warning('Unable to connect to Velma API. Some features may be limited.', 10000);
        });
});

// Export for use in other scripts
window.VelmaUtils = VelmaUtils;
window.VelmaToast = VelmaToast;
window.VelmaAPI = VelmaAPI;
window.VelmaModal = VelmaModal;
