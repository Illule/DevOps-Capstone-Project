"""
FastAPI application entry point.

Assembles the app by:
  1. Creating the FastAPI instance with metadata for Swagger UI.
  2. Configuring CORS middleware.
  3. Including all route modules under the /api prefix.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import books, health, reviews, stats

# ---------------------------------------------------------------------------
# Application Factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "📚 BookShelf — A personal reading tracker and review platform. "
        "Manage your book collection, track reading progress, "
        "and write reviews."
    ),
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc alternative
    openapi_url="/openapi.json",
)

# ---------------------------------------------------------------------------
# CORS Middleware
# ---------------------------------------------------------------------------
# Allows the React frontend (running on a different port) to call the API.
# In production (Kubernetes), the Ingress handles routing and this is less
# critical, but we keep it for direct access and development flexibility.

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Register Routers
# ---------------------------------------------------------------------------
# All routes are mounted under /api so that Kubernetes Ingress can route
# /api/* → backend and / → frontend cleanly.

app.include_router(health.router, prefix="/api")
app.include_router(health.router)  # Also responds directly to /health
app.include_router(books.router, prefix="/api")
app.include_router(reviews.router, prefix="/api")
app.include_router(stats.router, prefix="/api")

# ---------------------------------------------------------------------------
# Prometheus Observability Metrics
# ---------------------------------------------------------------------------
# Automatically tracks HTTP request count, latencies, status codes, and
# exposes standard Prometheus scrape endpoint at /api/metrics.
try:
    from prometheus_fastapi_instrumentator import Instrumentator

    Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        excluded_handlers=["/api/health", "/api/metrics"],
    ).instrument(app).expose(app, endpoint="/api/metrics", tags=["Monitoring"])
except ImportError:
    pass  # Allow fallback if package not installed locally during lightweight testing


# ---------------------------------------------------------------------------
# Root endpoint (informational)
# ---------------------------------------------------------------------------


@app.get("/", tags=["Root"])
def root():
    """Root endpoint — confirms the API is running."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/health",
    }
