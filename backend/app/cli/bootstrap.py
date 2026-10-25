"""
Initial Admin Bootstrap CLI
Creates or verifies the initial Super Admin account using environment variables or safe terminal input.
Usage:
  python -m backend.app.cli.bootstrap
"""

import os
import sys
from backend.app.database import SessionLocal, Base, engine
import backend.app.models
from backend.app.models.auth import User, UserRole
from backend.app.services.auth_service import hash_password


def bootstrap_admin():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    admin_email = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "admin@apex.edu").strip().lower()
    admin_password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "Admin@12345")
    admin_name = os.getenv("BOOTSTRAP_ADMIN_NAME", "System Administrator")

    existing_admin = db.query(User).filter(User.email == admin_email).first()
    if existing_admin:
        print(f"[BOOTSTRAP] Administrator already exists with email: {admin_email}")
        db.close()
        return

    new_admin = User(
        email=admin_email,
        hashed_password=hash_password(admin_password),
        full_name=admin_name,
        role=UserRole.SUPER_ADMIN,
        is_active=True,
    )
    db.add(new_admin)
    db.commit()
    print(f"[BOOTSTRAP] Successfully created Super Admin: {admin_email}")
    db.close()


if __name__ == "__main__":
    bootstrap_admin()
