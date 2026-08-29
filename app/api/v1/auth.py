from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.crud.user import any_user_exists, create_user, get_user_by_email
from app.database import get_db
from app.models.user import UserRole
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    if get_user_by_email(db, payload.email) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    # Bootstrap: the very first account in a fresh deployment becomes ADMIN.
    role = UserRole.REPORTER if any_user_exists(db) else UserRole.ADMIN
    user = create_user(db, payload.email, payload.password, payload.full_name, role)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = get_user_by_email(db, payload.email)
    if user is None or not user.is_active or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    token = create_access_token(subject=user.id, role=user.role.value)
    return TokenResponse(access_token=token)
