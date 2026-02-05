/**
 * Velma Core JavaScript
 * Core utilities and shared functionality
 */

// API Configuration (from config.js)
const API_BASE_URL = window.VELMA_CONFIG?.API_BASE_URL || '/api';
const DEMO_MODE = window.VELMA_CONFIG?.DEMO_MODE || false;

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
     * Get API key from localStorage
     */
    getApiKey() {
        return localStorage.getItem('velma_anthropic_api_key');
    },

    /**
     * Get selected AI model from localStorage
     */
    getAiModel() {
        return localStorage.getItem('velma_ai_model') || 'claude-sonnet-4-5-20250929';
    },

    /**
     * Build conversation history for API
     */
    getConversationHistory() {
        try {
            const history = sessionStorage.getItem('velma_chat_history');
            if (!history) return [];

            const messages = JSON.parse(history);
            // Convert to Anthropic format: [{role: "user", content: "..."}, {role: "assistant", content: "..."}]
            return messages
                .filter(msg => msg.sender === 'user' || msg.sender === 'assistant')
                .map(msg => ({
                    role: msg.sender === 'user' ? 'user' : 'assistant',
                    content: msg.text
                }))
                .slice(-10); // Keep last 10 messages for context
        } catch (error) {
            console.error('Failed to get conversation history:', error);
            return [];
        }
    },

    /**
     * Call Anthropic API directly
     */
    async callAnthropicAPI(message) {
        const apiKey = this.getApiKey();
        const model = this.getAiModel();

        if (!apiKey) {
            throw new Error('No API key configured. Please set your Anthropic API key in Settings.');
        }

        // Get conversation history
        const history = this.getConversationHistory();

        // Build messages array (history + new message)
        const messages = [...history, { role: 'user', content: message }];

        // System prompt for Velma
        const systemPrompt = `You are Velma, an AI assistant specialized in NDIS (National Disability Insurance Scheme) compliance, payroll, and operations in Australia.

You help with:
- SCHADS Award rates and calculations
- NDIS worker compliance requirements
- Payroll calculations with penalty rates and allowances
- Employee onboarding and HR processes
- Leave entitlements and calculations
- Credential tracking and compliance alerts

Be professional, accurate, and helpful. Provide specific information about Australian NDIS regulations, SCHADS Award conditions, and best practices for disability service providers.`;

        try {
            const response = await fetch('https://api.anthropic.com/v1/messages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-api-key': apiKey,
                    'anthropic-version': '2023-06-01'
                },
                body: JSON.stringify({
                    model: model,
                    max_tokens: 2048,
                    system: systemPrompt,
                    messages: messages
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error?.message || `API request failed with status ${response.status}`);
            }

            const data = await response.json();

            // Extract response text
            const responseText = data.content
                .filter(block => block.type === 'text')
                .map(block => block.text)
                .join('\n\n');

            return {
                status: 'success',
                message: responseText,
                action: 'respond',
                model: model,
                usage: data.usage
            };
        } catch (error) {
            console.error('Anthropic API Error:', error);

            // Check if it's an authentication error
            if (error.message.includes('401') || error.message.includes('authentication')) {
                throw new Error('Invalid API key. Please check your Anthropic API key in Settings.');
            }

            throw error;
        }
    },

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
        // Check if we have an API key - if so, use real Anthropic API
        const apiKey = this.getApiKey();

        if (apiKey) {
            try {
                console.log('Using Anthropic API with configured key');
                return await this.callAnthropicAPI(message);
            } catch (error) {
                console.error('Anthropic API call failed, falling back to demo mode:', error);
                VelmaToast.warning('API call failed: ' + error.message, 8000);
                // Fall back to demo mode
                return this.getDemoResponse(message);
            }
        }

        // Demo mode - return simulated responses
        if (DEMO_MODE || !API_BASE_URL) {
            console.log('Using demo mode (no API key configured)');
            return this.getDemoResponse(message);
        }

        // Try backend API if configured
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
     * Get demo response (when backend is not available)
     */
    async getDemoResponse(message) {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 700));

        const messageLower = message.toLowerCase();

        // SCHADS rates
        if (messageLower.includes('schads') || messageLower.includes('award') || messageLower.includes('rate')) {
            return {
                status: 'success',
                message: `**SCHADS Award 2010 - 2026 Rates**\n\n**Level 2 - Support Worker (Most Common):**\n- Level 2.1: $28.45/hour - Certificate II or 6 months experience\n- Level 2.2: $29.15/hour - Certificate III\n- Level 2.3: $29.85/hour - Certificate III + additional skills\n\n**Penalty Rates:**\n- Saturday: 1.5x (50% extra)\n- Sunday: 1.75x (75% extra)\n- Public Holiday: 2.5x (150% extra)\n- Night (8pm-7am): 1.25x\n- Afternoon (3pm-8pm): 1.15x\n\n**Note:** This is demo mode. Connect to the Velma API for real calculations.`,
                action: 'respond'
            };
        }

        // Compliance
        if (messageLower.includes('compliance') || messageLower.includes('documents') || messageLower.includes('screening')) {
            return {
                status: 'success',
                message: `**NDIS Worker Compliance Requirements**\n\nAll NDIS workers must maintain:\n\n1. **NDIS Worker Screening Check** (Yellow Card) - Valid 5 years\n2. **Working with Children Check** (WWCC) - Valid 5 years\n3. **First Aid Certificate** - Valid 3 years\n4. **CPR Certificate** - Valid 12 months\n5. **Police Check** - Valid 3 years\n6. **NDIS Worker Orientation Module** - One-time completion\n\nVelma automatically tracks expiry dates and sends reminders at 30, 60, and 90 days before expiration.\n\n**Note:** This is demo mode. Connect to the Velma API for actual compliance tracking.`,
                action: 'respond'
            };
        }

        // Calculate pay
        if (messageLower.includes('calculate') || messageLower.includes('pay')) {
            return {
                status: 'success',
                message: `**Pay Calculation Example**\n\nFor a Level 2.1 worker ($28.45/hour) working Saturday 9am-5pm (8 hours):\n\n- Base rate: $28.45/hour\n- Saturday penalty: 1.5x\n- Hourly rate: $28.45 × 1.5 = $42.68/hour\n- Total pay: $42.68 × 8 hours = **$341.44**\n\nThis includes:\n- Ordinary time earnings: $227.60\n- Saturday penalty: $113.84\n- Superannuation (11.5%): $26.17\n\n**Note:** This is demo mode. Connect to the Velma API for detailed calculations with all penalties and allowances.`,
                action: 'respond'
            };
        }

        // Onboarding
        if (messageLower.includes('onboard') || messageLower.includes('new employee')) {
            return {
                status: 'success',
                message: `**NDIS Employee Onboarding Checklist**\n\n**Pre-Employment:**\n- ✓ Job offer accepted\n- ✓ NDIS Worker Screening verified\n- ✓ WWCC verified\n- ✓ Police Check completed\n- ✓ First Aid & CPR certificates verified\n- ✓ Employment contract signed\n- ✓ TFN Declaration completed\n- ✓ Superannuation choice form\n\n**First Week:**\n- NDIS Worker Orientation Module\n- NDIS Code of Conduct training\n- Company policies review\n- IT systems access\n- Initial training\n\n**Note:** This is demo mode. Connect to the Velma API for automated onboarding management.`,
                action: 'respond'
            };
        }

        // Leave loading
        if (messageLower.includes('leave loading') || messageLower.includes('annual leave')) {
            return {
                status: 'success',
                message: `**Annual Leave Loading (SCHADS Award)**\n\nThe SCHADS Award provides **17.5% leave loading** on annual leave.\n\n**Example Calculation:**\nFor an employee on $30/hour:\n- 4 weeks annual leave = 152 hours\n- Normal pay: $30 × 152 = $4,560\n- Leave loading (17.5%): $4,560 × 0.175 = $798\n- **Total entitlement: $5,358**\n\nLeave loading compensates workers for not earning penalty rates while on leave.\n\n**Note:** This is demo mode. Connect to the Velma API for personalized calculations.`,
                action: 'respond'
            };
        }

        // Expiring credentials
        if (messageLower.includes('expir') || messageLower.includes('credential')) {
            return {
                status: 'success',
                message: `**Credential Expiry Monitoring**\n\nVelma automatically monitors and alerts for:\n\n**30 Days Before Expiry:**\n- NDIS Worker Screening Checks\n- Working with Children Checks\n\n**60 Days Before Expiry:**\n- First Aid Certificates\n- CPR Certificates\n\n**90 Days Before Expiry:**\n- Police Checks\n\nWorkers cannot work shifts if credentials have expired.\n\n**Note:** This is demo mode. Connect to the Velma API for real-time credential tracking.`,
                action: 'respond'
            };
        }

        // Default response
        return {
            status: 'success',
            message: `Hello! I'm Velma, your NDIS AI assistant.\n\n**Demo Mode Active** - This is a preview of Velma running without a backend API.\n\nI can help you with:\n- SCHADS Award rates and calculations\n- NDIS compliance requirements\n- Payroll calculations\n- Employee onboarding\n- Leave entitlements\n- Credential tracking\n\n**To access full features:**\n1. Deploy the Velma backend API\n2. Update \`frontend/config.js\` with your API URL\n3. Set \`DEMO_MODE = false\`\n\nTry asking: "What are the SCHADS rates?" or "Calculate pay for a Saturday shift"`,
            action: 'respond'
        };
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
