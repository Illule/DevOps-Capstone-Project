"""
Health check endpoint.

Used by:
  - Kubernetes liveness/readiness probes
  - Docker HEALTHCHECK
  - Load balancers
  - Monitoring systems
"""

from sqlalchemy import text
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Application health check.

    Verifies that the API is running and the database is reachable.
    Returns 200 with status details if healthy, 503 if the database
    is unreachable.
    """
    # Check database connectivity
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    status = "healthy" if db_status == "healthy" else "unhealthy"
    status_code = 200 if status == "healthy" else 503

    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=status_code,
        content={
            "status": status,
            "database": db_status,
            "service": "bookshelf-api",
        },
    )
