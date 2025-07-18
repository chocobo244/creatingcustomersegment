"""
Main FastAPI application for Multi-Touch Attribution Platform.
"""
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from backend.app.api.v1.api import api_router
from backend.app.core.database import init_db
from backend.app.utils.logging import (
    setup_logging,
    configure_uvicorn_logging,
    log_api_request,
    get_logger
)
from config.settings import get_settings, get_api_settings


# Setup logging before anything else
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Multi-Touch Attribution API")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    # Application is ready
    logger.info("API startup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Multi-Touch Attribution API")


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    api_settings = get_api_settings()
    
    app = FastAPI(
        title=api_settings.title,
        description=api_settings.description,
        version=api_settings.version,
        debug=api_settings.debug,
        docs_url=api_settings.docs_url if not settings.is_production() else None,
        redoc_url=api_settings.redoc_url if not settings.is_production() else None,
        openapi_url=api_settings.openapi_url if not settings.is_production() else None,
        lifespan=lifespan
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_settings.cors_origins,
        allow_credentials=True,
        allow_methods=api_settings.cors_methods,
        allow_headers=api_settings.cors_headers,
    )
    
    # Add compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Add request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        
        # Generate request ID
        request_id = f"{int(time.time() * 1000)}_{hash(str(request.url))}"
        request.state.request_id = request_id
        
        try:
            response = await call_next(request)
            execution_time = time.time() - start_time
            
            # Log successful request
            log_api_request(
                method=request.method,
                path=str(request.url.path),
                status_code=response.status_code,
                execution_time=execution_time,
                request_id=request_id
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Log failed request
            log_api_request(
                method=request.method,
                path=str(request.url.path),
                status_code=500,
                execution_time=execution_time,
                request_id=request_id,
                error=str(e)
            )
            
            # Re-raise the exception
            raise
    
    # Add custom exception handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions."""
        logger.warning(
            "HTTP exception occurred",
            status_code=exc.status_code,
            detail=exc.detail,
            path=str(request.url.path),
            method=request.method
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": "http_error",
                    "code": exc.status_code,
                    "message": exc.detail,
                    "request_id": getattr(request.state, "request_id", None)
                }
            }
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle value errors."""
        logger.error(
            "Value error occurred",
            error=str(exc),
            path=str(request.url.path),
            method=request.method
        )
        
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "type": "validation_error",
                    "code": 400,
                    "message": str(exc),
                    "request_id": getattr(request.state, "request_id", None)
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        logger.error(
            "Unexpected error occurred",
            error=str(exc),
            error_type=type(exc).__name__,
            path=str(request.url.path),
            method=request.method,
            exc_info=True
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": "internal_error",
                    "code": 500,
                    "message": "An internal server error occurred",
                    "request_id": getattr(request.state, "request_id", None)
                }
            }
        )
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": api_settings.version,
            "environment": settings.environment
        }
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    return app


# Create the application instance
app = create_application()


if __name__ == "__main__":
    """Run the application directly."""
    configure_uvicorn_logging()
    
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None,  # Use our custom logging configuration
    )