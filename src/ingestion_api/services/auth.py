from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.ingestion_api.models import User
from src.ingestion_api.security import create_access_token, verify_password
from src.ingestion_api.services.users import get_user_by_username


def authenticate_user(db: Session, username: str, password: str) -> User:
    user = get_user_by_username(db, username)
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    return user


def issue_token_for_user(user: User) -> str:
    return create_access_token(subject=user.username)
