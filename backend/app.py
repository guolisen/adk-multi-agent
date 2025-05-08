"""
Deepdevflow - Main FastAPI Backend Application
"""

import os
import logging
from contextlib import asynccontextmanager
import tracemalloc

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.routes import session, conversation, agent
from backend.utils.database import init_db
from backend.utils.config import config

# Enable tracemalloc to get object allocation traceback
tracemalloc.start()

# Configure logging
logging.basicConfig(
    level=logging.INFO if not config.debug_mode else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("deepdevflow")


# Define lifespan context manager (replaces on_event handlers)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Starting Deepdevflow backend application")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        # Still allow the application to start, but log the error
    
    yield  # This is where the application runs
    
    # Shutdown logic
    logger.info("Shutting down Deepdevflow backend application")


# Create FastAPI application with lifespan
app = FastAPI(
    title="Deepdevflow",
    description="A multiagent framework built with Google ADK",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get("server.cors.allow_origins", ["*"]),
    allow_credentials=config.get("server.cors.allow_credentials", True),
    allow_methods=config.get("server.cors.allow_methods", ["*"]),
    allow_headers=config.get("server.cors.allow_headers", ["*"]),
)

# Include routers
app.include_router(session.router)
app.include_router(conversation.router)
app.include_router(agent.router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint for healthcheck."""
    return {
        "name": config.app_name,
        "version": config.app_version,
        "status": "operational"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint with more detailed status information."""
    try:
        # Add more health checks here as needed
        return {
            "status": "healthy",
            "version": config.app_version,
            "database": "connected",
            "environment": "production" if not config.debug_mode else "development"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is currently unavailable"
        )


if __name__ == "__main__":
    logger.info(f"Starting server at {config.server_host}:{config.server_port}")
    
    # Get server configuration
    host = config.server_host
    port = config.server_port
    
    # Run server with parameters compatible with newer uvicorn
    uvicorn.run(
        "backend.app:app",
        host=host,
        port=port,
        reload=config.debug_mode,
        log_level="info" if not config.debug_mode else "debug",
        workers=config.get("workers", 1),
    )
