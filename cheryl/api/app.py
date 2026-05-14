"""
Cheryl FastAPI Application
REST API for interacting with Cheryl
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
from pathlib import Path

from ..core import Cheryl
from ..utils import Config, get_logger

logger = get_logger(__name__)

# Get the frontend directory path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

# Initialize FastAPI app
app = FastAPI(
    title="Cheryl API",
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

# Mount static files (frontend)
if FRONTEND_DIR.exists():
    # Mount CSS, JS, and other static assets
    if (FRONTEND_DIR / "css").exists():
        app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
    if (FRONTEND_DIR / "js").exists():
        app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")
    if (FRONTEND_DIR / "images").exists():
        app.mount("/images", StaticFiles(directory=str(FRONTEND_DIR / "images")), name="images")

    logger.info(f"Serving frontend from: {FRONTEND_DIR}")
else:
    logger.warning(f"Frontend directory not found: {FRONTEND_DIR}")

# Global Cheryl instance
config = Config()
cheryl = None


@app.on_event("startup")
async def startup_event():
    """Initialize Cheryl on startup"""
    global cheryl
    cheryl = Cheryl(config)
    logger.info("Cheryl API started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global cheryl
    if cheryl:
        await cheryl.shutdown()
    logger.info("Cheryl API stopped")


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
@app.get("/")
async def root():
    """Redirect to frontend dashboard"""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    else:
        # Fallback to API documentation
        return RedirectResponse(url="/docs")


@app.get("/favicon.svg")
async def favicon():
    """Serve favicon"""
    favicon_file = FRONTEND_DIR / "favicon.svg"
    if favicon_file.exists():
        return FileResponse(favicon_file, media_type="image/svg+xml")
    return {"error": "Favicon not found"}


@app.get("/favicon.ico")
async def favicon_ico():
    """Serve favicon (fallback for browsers requesting .ico)"""
    # Redirect to SVG version
    return RedirectResponse(url="/favicon.svg")


@app.get("/{page_name}.html")
async def serve_page(page_name: str):
    """Serve HTML pages from frontend"""
    page_file = FRONTEND_DIR / f"{page_name}.html"
    if page_file.exists():
        return FileResponse(page_file)
    raise HTTPException(status_code=404, detail="Page not found")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "cheryl"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process chat message

    Args:
        request: Chat request with message and optional context

    Returns:
        Chat response with Cheryl's reply
    """
    try:
        response = await cheryl.process_request(
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
    """List available Cheryl modules"""
    return {
        "modules": list(cheryl.modules.keys()),
        "count": len(cheryl.modules)
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
