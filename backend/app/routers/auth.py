"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    TokenRefresh,
    PasswordChange,
    MessageResponse,
)
from app.services.auth_service import auth_service
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account
    
    - **email**: Valid email address
    - **username**: Alphanumeric username (3-50 chars)
    - **password**: Strong password (8+ chars, uppercase, lowercase, digit, special char)
    - **full_name**: Optional full name
    """
    user = auth_service.create_user(db, user_data)
    tokens = auth_service.generate_tokens(user)
    
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login with username/email and password
    
    Returns access and refresh tokens
    """
    user = auth_service.authenticate_user(db, login_data)
    tokens = auth_service.generate_tokens(user)
    
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        user=UserResponse.model_validate(user)
    )


@router.post("/login/form", response_model=TokenResponse)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible login endpoint (for Swagger UI)
    """
    login_data = UserLogin(username=form_data.username, password=form_data.password)
    user = auth_service.authenticate_user(db, login_data)
    tokens = auth_service.generate_tokens(user)
    
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        user=UserResponse.model_validate(user)
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token
    """
    tokens = auth_service.refresh_tokens(db, token_data.refresh_token)
    
    # Get user for response
    from app.core.security import decode_token
    payload = decode_token(tokens["access_token"])
    user = auth_service.get_user_by_id(db, int(payload.get("sub")))
    
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's profile
    """
    return UserResponse.model_validate(current_user)


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change current user's password
    
    Requires current password for verification
    """
    auth_service.change_password(
        db,
        current_user,
        password_data.old_password,
        password_data.new_password
    )
    
    return MessageResponse(message="Password changed successfully")
