"""
Honeypot API - Main Application

FastAPI application for the Agentic Honey-Pot system.
"""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import router
from app.api.middleware import APIKeyMiddleware

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
    logger.info(f"GUVI Callback URL: {settings.guvi_callback_url}")
    
    # Verify Google API key is set
    if not settings.google_api_key:
        logger.error("❌ GOOGLE_API_KEY is not set!")
    else:
        logger.info("✅ Google API key configured")
    
    # Set Google API key in environment for ADK
    os.environ["GOOGLE_API_KEY"] = settings.google_api_key
    
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
