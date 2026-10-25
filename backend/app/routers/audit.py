import json
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.auth import User, UserRole
from backend.app.models.audit import AuditLog, ImportJob, Notification
from backend.app.services.auth_service import get_current_user, require_roles

router = APIRouter(prefix="/audit", tags=["Audit & Notifications"])


def log_audit_event(
    db: Session,
    action: str,
    user_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[dict] = None,
):
    """Helper to persist audit events."""
    try:
        log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            ip_address=ip_address,
            details_json=json.dumps(details) if details else None,
            created_at=datetime.now(timezone.utc),
        )
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"[AUDIT ERROR] Failed to record audit log: {e}")


def create_notification(
    db: Session,
    title: str,
    message: str,
    user_id: Optional[int] = None,
    notification_type: str = "INFO",
    link: Optional[str] = None,
):
    """Helper to create notifications."""
    try:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link,
            created_at=datetime.now(timezone.utc),
        )
        db.add(notif)
        db.commit()
    except Exception as e:
        print(f"[NOTIFICATION ERROR] Failed to create notification: {e}")


@router.get("/logs")
def get_audit_logs(
    action: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.HOD, UserRole.FACULTY])),
    db: Session = Depends(get_db)
):
    """Retrieves immutable audit trail of system events."""
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    logs = query.order_by(AuditLog.id.desc()).limit(limit).all()
    
    return [
        {
            "id": l.id,
            "user_id": l.user_id,
            "user_email": l.user.email if l.user else "System",
            "action": l.action,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "ip_address": l.ip_address,
            "details": json.loads(l.details_json) if l.details_json else {},
            "created_at": l.created_at,
        }
        for l in logs
    ]


@router.get("/jobs")
def get_import_jobs(
    limit: int = 20,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.HOD, UserRole.FACULTY])),
    db: Session = Depends(get_db)
):
    """Retrieves import job history."""
    jobs = db.query(ImportJob).order_by(ImportJob.id.desc()).limit(limit).all()
    return [
        {
            "id": j.id,
            "user_email": j.user.email if j.user else "System",
            "import_type": j.import_type,
            "file_name": j.file_name,
            "status": j.status,
            "total_rows": j.total_rows,
            "imported_rows": j.imported_rows,
            "failed_rows": j.failed_rows,
            "created_at": j.created_at,
        }
        for j in jobs
    ]


@router.get("/notifications")
def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves alerts and notifications for the authenticated user."""
    notifs = db.query(Notification).filter(
        (Notification.user_id == current_user.id) | (Notification.user_id == None)
    ).order_by(Notification.id.desc()).limit(20).all()

    return [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "notification_type": n.notification_type,
            "is_read": n.is_read,
            "link": n.link,
            "created_at": n.created_at,
        }
        for n in notifs
    ]


@router.post("/notifications/{notif_id}/read")
def mark_notification_read(
    notif_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marks a notification as read."""
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if notif:
        notif.is_read = True
        db.commit()
    return {"message": "Notification marked as read"}
