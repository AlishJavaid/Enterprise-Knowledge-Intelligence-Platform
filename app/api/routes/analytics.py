from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_db, require_roles
from app.db.models import User, UserRole
from app.services.analytics_service import get_dashboard_metrics

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin, UserRole.analyst)),
):
    return get_dashboard_metrics(db)