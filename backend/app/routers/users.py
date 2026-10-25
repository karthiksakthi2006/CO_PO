from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.auth import User, UserRole
from backend.app.schemas.auth import UserResponse, UserCreate, UserUpdate
from backend.app.services.auth_service import hash_password, get_current_user, require_roles

router = APIRouter(prefix="/users", tags=["User Administration"])


@router.get("", response_model=List[UserResponse])
def list_users(
    role: Optional[UserRole] = None,
    department_id: Optional[int] = None,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.HOD])),
    db: Session = Depends(get_db)
):
    """Lists registered users, filtered by role and department."""
    query = db.query(User)
    
    # Restrict HOD to their department
    if current_user.role == UserRole.HOD and current_user.department_id:
        query = query.filter(User.department_id == current_user.department_id)
    elif department_id:
        query = query.filter(User.department_id == department_id)

    if role:
        query = query.filter(User.role == role)

    return query.order_by(User.id.desc()).all()


@router.post("", response_model=UserResponse)
def create_user(
    user_in: UserCreate,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN])),
    db: Session = Depends(get_db)
):
    """Creates a new user account with role assignment."""
    existing = db.query(User).filter(User.email == user_in.email.strip().lower()).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered")

    new_user = User(
        email=user_in.email.strip().lower(),
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        institution_id=user_in.institution_id or current_user.institution_id,
        department_id=user_in.department_id,
        student_id=user_in.student_id,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN])),
    db: Session = Depends(get_db)
):
    """Updates user status, department, or role."""
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user_update.full_name is not None:
        target_user.full_name = user_update.full_name
    if user_update.role is not None:
        target_user.role = user_update.role
    if user_update.is_active is not None:
        target_user.is_active = user_update.is_active
    if user_update.department_id is not None:
        target_user.department_id = user_update.department_id

    db.commit()
    db.refresh(target_user)
    return target_user
