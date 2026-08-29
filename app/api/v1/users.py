from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.user import create_user, get_user_by_email
from app.database import get_db
from app.deps import get_current_user, require_roles
from app.models.user import User, UserRole
from app.schemas.user import UserAdminCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return current_user


@router.get("", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> list[UserRead]:
    return list(db.scalars(select(User).order_by(User.created_at.desc())))


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_managed_user(
    payload: UserAdminCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> UserRead:
    if get_user_by_email(db, payload.email) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    return create_user(db, payload.email, payload.password, payload.full_name, payload.role)
