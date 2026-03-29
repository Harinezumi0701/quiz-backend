from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.constants import APP_VERSION
from app.db.session import get_db
from app.utils.response import success_response

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health_check(db: Session = Depends(get_db)):
    db_status = "disconnected"
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        pass
    return success_response(
        data={"status": "ok", "database": db_status, "version": APP_VERSION},
    )
