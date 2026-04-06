from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.ingestion_api.auth_schemas import UserCreate, UserResponse, UserUpdate
from src.ingestion_api.database import get_db
from src.ingestion_api.dependencies import get_current_user
from src.ingestion_api.models import User
from src.ingestion_api.services.users import (
    create_user,
    get_user_by_email,
    get_user_by_username,
    list_users,
    update_user,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    if get_user_by_username(db, payload.username):
        raise HTTPException(status_code=409, detail="Username already exists")
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=409, detail="Email already exists")

    user = create_user(db, payload)
    return UserResponse.model_validate(user)


@router.get("", response_model=list[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[UserResponse]:
    users = list_users(db, skip=skip, limit=limit)
    return [UserResponse.model_validate(user) for user in users]


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
def patch_me(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    user = update_user(db, current_user, payload)
    return UserResponse.model_validate(user)
