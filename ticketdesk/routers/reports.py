from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_staff
from ..models import User
from ..services import report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/sla")
def sla(sort: str = Query("open", max_length=60), user: User = Depends(require_staff),
        db: Session = Depends(get_db)):
    return report_service.sla_report(db, user, sort)


@router.get("/volume")
def volume(days: int = Query(30, ge=1, le=365), user: User = Depends(require_staff), db: Session = Depends(get_db)):
    return report_service.volume_report(db, user, days)
