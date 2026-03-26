"""FastAPI application main entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import auth, projects, scenes, elements, templates, themes, ai, export_api
from app.core.config import get_settings
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    settings = get_settings()
    if settings.debug:
        print(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Initialize database tables
    init_db()
    
    yield
    
    # Shutdown
    if settings.debug:
        print("Shutting down application")


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="API for AI Stream Scene Builder - create professional streaming layouts",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routers
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
    app.include_router(projects.router, prefix="/api/v1", tags=["projects"])
    app.include_router(scenes.router, prefix="/api/v1", tags=["scenes"])
    app.include_router(elements.router, prefix="/api/v1", tags=["elements"])
    app.include_router(templates.router, prefix="/api/v1", tags=["templates"])
    app.include_router(themes.router, prefix="/api/v1", tags=["themes"])
    app.include_router(ai.router, prefix="/api/v1", tags=["ai"])
    app.include_router(export_api.router, prefix="/api/v1", tags=["export"])
    
    # Global exception handler
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail,
                }
            }
        )
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": settings.app_version}
    
    @app.get("/")
    async def root():
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs"
        }
    
    return app


app = create_application()
