from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.ingestion_api.auth_schemas import TokenResponse
from src.ingestion_api.database import get_db
from src.ingestion_api.services.auth import authenticate_user, issue_token_for_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    user = authenticate_user(db=db, username=form_data.username, password=form_data.password)
    token = issue_token_for_user(user)
    return TokenResponse(access_token=token)
