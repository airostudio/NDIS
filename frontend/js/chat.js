/**
 * Cheryl Chat Interface
 * Handles chat interactions with Cheryl AI
 */

class CherylChat {
    constructor() {
        this.messagesContainer = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendButton');
        this.suggestedPrompts = document.getElementById('suggestedPrompts');
        this.clearChatButton = document.getElementById('clearChat');

        this.isTyping = false;
        this.messageHistory = [];

        this.init();
    }

    init() {
        // Auto-resize textarea
        this.chatInput.addEventListener('input', () => {
            this.autoResizeTextarea();
            this.updateSendButton();
        });

        // Send on Enter (Shift+Enter for new line)
        this.chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Send button click
        this.sendButton.addEventListener('click', () => {
            this.sendMessage();
        });

        // Suggested prompts
        document.querySelectorAll('.suggested-prompt').forEach(button => {
            button.addEventListener('click', () => {
                const prompt = button.dataset.prompt;
                this.chatInput.value = prompt;
                this.updateSendButton();
                this.sendMessage();
            });
        });

        // Clear chat
        if (this.clearChatButton) {
            this.clearChatButton.addEventListener('click', () => {
                this.clearChat();
            });
        }

        // Load chat history from session storage
        this.loadChatHistory();
    }

    autoResizeTextarea() {
        this.chatInput.style.height = 'auto';
        this.chatInput.style.height = Math.min(this.chatInput.scrollHeight, 120) + 'px';
    }

    updateSendButton() {
        const hasContent = this.chatInput.value.trim().length > 0;
        this.sendButton.disabled = !hasContent || this.isTyping;
    }

    async sendMessage() {
        const message = this.chatInput.value.trim();

        if (!message || this.isTyping) return;

        // Hide suggested prompts
        if (this.suggestedPrompts) {
            this.suggestedPrompts.style.display = 'none';
        }

        // Add user message
        this.addMessage(message, 'user');

        // Clear input
        this.chatInput.value = '';
        this.autoResizeTextarea();
        this.updateSendButton();

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send to API
            const response = await CherylAPI.chat(message);

            // Remove typing indicator
            this.hideTypingIndicator();

            // Add assistant response
            this.addMessage(response.message, 'assistant', response);

            // Save to history
            this.saveChatHistory();
        } catch (error) {
            console.error('Chat error:', error);
            this.hideTypingIndicator();

            this.addMessage(
                "I'm sorry, I'm having trouble connecting right now. Please try again in a moment.",
                'assistant',
                { status: 'error' }
            );

            CherylToast.error('Failed to send message. Please try again.');
        }
    }

    addMessage(text, sender, metadata = {}) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;

        const avatar = sender === 'user' ? 'U' : 'V';
        const time = CherylUtils.formatTime(new Date());

        // Parse markdown-like formatting
        const formattedText = CherylUtils.parseMarkdown(text);

        messageDiv.innerHTML = `
            <div class="chat-message-avatar">${avatar}</div>
            <div class="chat-message-content">
                <div class="chat-message-bubble">
                    ${formattedText}
                </div>
                <div class="chat-message-time">${time}</div>
            </div>
        `;

        this.messagesContainer.appendChild(messageDiv);

        // Scroll to bottom
        this.scrollToBottom();

        // Add to history
        this.messageHistory.push({
            text,
            sender,
            metadata,
            timestamp: new Date().toISOString()
        });
    }

    showTypingIndicator() {
        this.isTyping = true;
        this.updateSendButton();

        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message assistant';
        typingDiv.id = 'typingIndicator';

        typingDiv.innerHTML = `
            <div class="chat-message-avatar">V</div>
            <div class="chat-message-content">
                <div class="chat-typing-indicator">
                    <div class="chat-typing-dot"></div>
                    <div class="chat-typing-dot"></div>
                    <div class="chat-typing-dot"></div>
                </div>
            </div>
        `;

        this.messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.isTyping = false;
        this.updateSendButton();

        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    scrollToBottom() {
        this.messagesContainer.scrollTo({
            top: this.messagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    }

    clearChat() {
        CherylModal.show(
            'Clear Conversation',
            '<p>Are you sure you want to clear the conversation? This action cannot be undone.</p>',
            [
                {
                    id: 'cancel',
                    label: 'Cancel',
                    className: 'btn btn-ghost'
                },
                {
                    id: 'confirm',
                    label: 'Clear Chat',
                    className: 'btn btn-error',
                    handler: () => {
                        // Remove all messages except welcome
                        const messages = this.messagesContainer.querySelectorAll('.chat-message');
                        messages.forEach((msg, index) => {
                            if (index > 0) { // Keep first welcome message
                                msg.remove();
                            }
                        });

                        // Clear history
                        this.messageHistory = [];
                        sessionStorage.removeItem('cheryl_chat_history');

                        // Show suggested prompts
                        if (this.suggestedPrompts) {
                            this.suggestedPrompts.style.display = 'block';
                        }

                        CherylToast.success('Conversation cleared');
                    }
                }
            ]
        );
    }

    saveChatHistory() {
        try {
            sessionStorage.setItem('cheryl_chat_history', JSON.stringify(this.messageHistory));
        } catch (error) {
            console.error('Failed to save chat history:', error);
        }
    }

    loadChatHistory() {
        try {
            const saved = sessionStorage.getItem('cheryl_chat_history');
            if (saved) {
                this.messageHistory = JSON.parse(saved);

                // Restore messages (skip welcome message)
                this.messageHistory.forEach(msg => {
                    if (msg.sender !== 'system') {
                        this.addMessageFromHistory(msg);
                    }
                });

                // Hide suggested prompts if there are messages
                if (this.messageHistory.length > 0 && this.suggestedPrompts) {
                    this.suggestedPrompts.style.display = 'none';
                }
            }
        } catch (error) {
            console.error('Failed to load chat history:', error);
        }
    }

    addMessageFromHistory(msg) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${msg.sender}`;

        const avatar = msg.sender === 'user' ? 'U' : 'V';
        const time = CherylUtils.formatTime(new Date(msg.timestamp));
        const formattedText = CherylUtils.parseMarkdown(msg.text);

        messageDiv.innerHTML = `
            <div class="chat-message-avatar">${avatar}</div>
            <div class="chat-message-content">
                <div class="chat-message-bubble">
                    ${formattedText}
                </div>
                <div class="chat-message-time">${time}</div>
            </div>
        `;

        this.messagesContainer.appendChild(messageDiv);
    }
}

// Initialize chat when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.cherylChat = new CherylChat();
});
