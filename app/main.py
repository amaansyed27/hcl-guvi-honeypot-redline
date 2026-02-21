"""
Honeypot API - Main Application

FastAPI application for the Agentic Honey-Pot system.
Uses Google Gemini API (google-genai SDK) for AI capabilities.
"""

import logging
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load .env file first
load_dotenv()

from app.config import get_settings
from app.api.routes import router
from app.api.middleware import APIKeyMiddleware

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("🍯 Starting Honeypot API...")
    logger.info(f"Model: {settings.model_name}")
    
    # Validation
    if settings.api_key == "replace_me_in_cloud_run":
        logger.error("❌ API_KEY IS NOT CONFIGURED! Requests will likely fail auth.")
        logger.error("Please set API_KEY in Cloud Run environment variables.")
    
    # Set Google API key in environment
    if settings.google_api_key:
        os.environ["GOOGLE_API_KEY"] = settings.google_api_key
        logger.info("✅ Google Gemini API key configured from settings")
    
    # Final check for Google key
    api_key_check = os.environ.get("GOOGLE_API_KEY")
    if not api_key_check:
        logger.error("❌ GOOGLE_API_KEY is not set in environment!")
        logger.error("Please set GOOGLE_API_KEY in Cloud Run environment variables.")
    else:
        # Test Gemini connection
        try:
            from google import genai
            client = genai.Client()
            # Minimal health check to the model
            logger.info("✅ Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Gemini client error: {e}")
            logger.error("This usually means GOOGLE_API_KEY is invalid or restricted.")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Honeypot API...")


# Create FastAPI application
app = FastAPI(
    title="Agentic Honey-Pot API",
    description="""
    AI-powered honeypot system for scam detection and intelligence extraction.
    
    ## Features
    - 🎯 Scam message detection
    - 🤖 Autonomous AI agent engagement
    - 🔍 Intelligence extraction (bank accounts, UPI IDs, phishing links)
    - 📊 Multi-turn conversation handling
    - 📤 Automatic GUVI callback integration
    
    ## Authentication
    All endpoints (except /health) require `x-api-key` header.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add API key middleware
app.add_middleware(APIKeyMiddleware)

# Include API routes
app.include_router(router, prefix="/api", tags=["Honeypot"])


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "name": "Agentic Honey-Pot API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    No authentication required. Use for monitoring and load balancer checks.
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "model": settings.model_name
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True
    )
