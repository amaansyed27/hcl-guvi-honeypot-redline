"""
API Authentication Middleware

Handles x-api-key authentication for the honeypot API.
"""

from fastapi import Request, HTTPException
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# API Key header scheme
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


async def verify_api_key(api_key: str = None) -> bool:
    """Verify the provided API key."""
    if not api_key:
        return False
    return api_key == settings.api_key


class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Middleware to verify API key on protected routes.
    
    Allows:
    - /health endpoint without auth
    - /docs, /redoc, /openapi.json for API documentation
    
    Requires x-api-key header for all other routes.
    """
    
    # Paths that don't require authentication
    EXEMPT_PATHS = {
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico"
    }
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Allow exempt paths
        if path in self.EXEMPT_PATHS:
            return await call_next(request)
        
        # Check API key
        api_key = request.headers.get("x-api-key")
        
        if not api_key:
            logger.warning(f"Missing API key for request to {path}")
            return JSONResponse(
                status_code=401,
                content={
                    "status": "error",
                    "message": "Missing API key. Include 'x-api-key' header."
                }
            )
        
        if not await verify_api_key(api_key):
            logger.warning(f"Invalid API key for request to {path}")
            return JSONResponse(
                status_code=403,
                content={
                    "status": "error",
                    "message": "Invalid API key."
                }
            )
        
        # Valid API key, proceed
        response = await call_next(request)
        return response


def get_api_key_dependency(api_key: str = None):
    """
    FastAPI dependency for route-level API key verification.
    
    Usage:
        @app.post("/protected")
        async def protected_route(api_key: str = Depends(get_api_key_dependency)):
            ...
    """
    async def verify(request: Request):
        api_key = request.headers.get("x-api-key")
        if not api_key or not await verify_api_key(api_key):
            raise HTTPException(
                status_code=403,
                detail="Invalid or missing API key"
            )
        return api_key
    
    return verify
