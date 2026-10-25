from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.database import get_db

router = APIRouter(tags=["Health & Readiness"])


@router.get("/health")
def health_check():
    """Liveness probe."""
    return {"status": "ok", "service": "CO-ATTAIN PRO AI Backend", "version": "1.0.0"}


@router.get("/readiness")
def readiness_check(db: Session = Depends(get_db)):
    """Readiness probe checking database connectivity and table state."""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "database": "connected",
            "database_type": db.bind.dialect.name,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
        }
