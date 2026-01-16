"""
GNC Calculations API - Main Application Entry Point

This FastAPI application provides engineering calculations for spacecraft
Guidance, Navigation, and Control (GNC) systems. It is designed to be
modular and extensible for future agent/tool integration.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import gnc


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    yield
    # Shutdown
    print("Shutting down GNC Calculations API")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Professional-grade GNC calculations for spacecraft engineering",
    lifespan=lifespan,
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(gnc.router, prefix=f"{settings.api_prefix}/gnc", tags=["GNC"])


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {"status": "healthy", "version": settings.app_version}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }
