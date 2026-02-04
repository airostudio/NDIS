"""
Velma FastAPI Application
REST API for interacting with Velma
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

from ..core import Velma
from ..utils import Config, get_logger

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Velma API",
    description="NDIS Virtual AI Executive Suite API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Velma instance
config = Config()
velma = None


@app.on_event("startup")
async def startup_event():
    """Initialize Velma on startup"""
    global velma
    velma = Velma(config)
    logger.info("Velma API started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global velma
    if velma:
        await velma.shutdown()
    logger.info("Velma API stopped")


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    status: str
    message: str
    action: str
    metadata: Optional[Dict[str, Any]] = None


# API Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with simple web interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Velma - NDIS AI Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #2c3e50; }
            .chat-container { border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin: 20px 0; }
            #messages { height: 400px; overflow-y: auto; border: 1px solid #eee; padding: 15px; margin-bottom: 15px; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user { background: #e3f2fd; text-align: right; }
            .assistant { background: #f5f5f5; }
            input { width: 80%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
            button { padding: 10px 20px; background: #2196F3; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #1976D2; }
        </style>
    </head>
    <body>
        <h1>🤖 Velma - NDIS Virtual AI Executive Suite</h1>
        <p>Your intelligent assistant for executive tasks, reception, HR, and payroll.</p>

        <div class="chat-container">
            <div id="messages"></div>
            <input type="text" id="messageInput" placeholder="Type your message..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()">Send</button>
        </div>

        <script>
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;

                // Display user message
                addMessage(message, 'user');
                input.value = '';

                // Send to API
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: message })
                    });

                    const data = await response.json();
                    addMessage(data.message, 'assistant');
                } catch (error) {
                    addMessage('Error: ' + error.message, 'assistant');
                }
            }

            function addMessage(text, sender) {
                const messagesDiv = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ' + sender;
                messageDiv.textContent = text;
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }

            // Add welcome message
            addMessage('Hello! I\'m Velma, your AI executive assistant. How can I help you today?', 'assistant');
        </script>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "velma"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process chat message

    Args:
        request: Chat request with message and optional context

    Returns:
        Chat response with Velma's reply
    """
    try:
        response = await velma.process_request(
            message=request.message,
            context=request.context,
            channel="api",
            user_id=request.user_id or "anonymous"
        )

        return ChatResponse(
            status=response.get("status", "success"),
            message=response.get("message", ""),
            action=response.get("action", "respond"),
            metadata=response
        )

    except Exception as e:
        logger.error(f"Error processing chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/modules")
async def list_modules():
    """List available Velma modules"""
    return {
        "modules": list(velma.modules.keys()),
        "count": len(velma.modules)
    }


@app.get("/api/config")
async def get_config():
    """Get current configuration (non-sensitive)"""
    return {
        "company_name": config.company_name,
        "timezone": config.timezone,
        "modules_enabled": {
            name: config.get(f'modules.{name}.enabled', True)
            for name in ['calendar', 'communication', 'receptionist', 'hr', 'payroll', 'tasks', 'relationships']
        }
    }


def run_api(host: str = "0.0.0.0", port: int = 8000):
    """Run the API server"""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_api()
