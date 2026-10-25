from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.auth import User, UserRole
from backend.app.schemas.auth import Token, UserResponse, UserLogin, PasswordChange
from backend.app.services.auth_service import verify_password, create_access_token, hash_password, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


from backend.app.routers.audit import log_audit_event

@router.post("/login", response_model=Token)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 compatible login endpoint."""
    user = db.query(User).filter(User.email == form_data.username.strip().lower()).first()
    client_ip = request.client.host if request.client else "unknown"

    if not user or not verify_password(form_data.password, user.hashed_password):
        log_audit_event(db, action="LOGIN_FAILED", entity_type="USER", entity_id=form_data.username, ip_address=client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

    log_audit_event(db, action="LOGIN_SUCCESS", user_id=user.id, entity_type="USER", entity_id=str(user.id), ip_address=client_ip)

    access_token = create_access_token(data={"sub": user.email, "role": user.role.value})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "full_name": user.full_name,
        "email": user.email,
    }


@router.post("/login-json", response_model=Token)
def login_json(request: Request, credentials: UserLogin, db: Session = Depends(get_db)):
    """JSON body login endpoint for modern frontend clients."""
    user = db.query(User).filter(User.email == credentials.email.strip().lower()).first()
    client_ip = request.client.host if request.client else "unknown"

    if not user or not verify_password(credentials.password, user.hashed_password):
        log_audit_event(db, action="LOGIN_FAILED", entity_type="USER", entity_id=credentials.email, ip_address=client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

    log_audit_event(db, action="LOGIN_SUCCESS", user_id=user.id, entity_type="USER", entity_id=str(user.id), ip_address=client_ip)

    access_token = create_access_token(data={"sub": user.email, "role": user.role.value})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "full_name": user.full_name,
        "email": user.email,
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns currently authenticated user profile."""
    return current_user


@router.post("/change-password")
def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Allows authenticated user to change their password."""
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    if len(data.new_password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters long")

    current_user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"message": "Password updated successfully"}
