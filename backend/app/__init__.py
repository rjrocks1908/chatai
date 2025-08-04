from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback

from app.config import get_settings
from app.api.v1.api import api_router
from app.core.exceptions import APIException

settings = get_settings()


def create_app():
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI Coding Agent API - A Claude-style coding assistant",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(api_router)

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "AI Coding Agent API",
            "version": settings.app_version,
            "status": "running",
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "version": settings.app_version,
            "api_key_configured": bool(settings.google_api_key),
        }

    @app.exception_handler(APIException)
    async def api_exception_handler(request, exc: APIException):
        """Handle custom API exceptions"""
        traceback.print_exc()
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.detail,
                "status_code": exc.status_code,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException):
        """Handle HTTP exceptions"""
        traceback.print_exc()
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.detail,
                "status_code": exc.status_code,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        """Handle general exceptions"""
        traceback.print_exc()
        if settings.debug:
            # In debug mode, return detailed error info
            return JSONResponse(
                status_code=500,
                content={
                    "error": True,
                    "message": f"Internal server error: {str(exc)}",
                    "type": type(exc).__name__,
                    "status_code": 500,
                },
            )
        else:
            # In production, return generic error message
            return JSONResponse(
                status_code=500,
                content={
                    "error": True,
                    "message": "Internal server error",
                    "status_code": 500,
                },
            )

    return app
