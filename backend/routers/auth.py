"""
Authentication Router
=====================
Handles user registration, login, and profile management.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
import logging

from models.schemas import (
    UserCreate, UserLogin, User, Token, UserWithToken,
    SuccessResponse, ErrorResponse
)
from core.database import user_db
from core.auth import (
    verify_password, get_password_hash, create_access_token,
    validate_token
)

logger = logging.getLogger(__name__)

router = APIRouter()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependency to get current authenticated user from token

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    username = validate_token(token)
    if username is None:
        raise credentials_exception

    user_dict = user_db.get_user_by_username(username)
    if user_dict is None:
        raise credentials_exception

    # Check if user is active
    if not user_dict.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    return User(**user_dict)


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user (alias for get_current_user)"""
    return current_user


@router.post("/register", response_model=UserWithToken, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """
    Register a new user

    Args:
        user: User registration data (username, email, password, full_name)

    Returns:
        User data with access token

    Raises:
        HTTPException: If username/email already exists
    """
    try:
        # Check if username or email already exists
        if user_db.get_user_by_username(user.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        if user_db.get_user_by_email(user.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash password and create user
        hashed_password = get_password_hash(user.password)
        user_dict = user_db.create_user(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            full_name=user.full_name
        )

        # Generate token
        access_token = create_access_token(data={"sub": user.username})

        logger.info(f"✅ New user registered: {user.username}")

        return UserWithToken(
            user=User(**user_dict),
            token=Token(access_token=access_token, token_type="bearer")
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=UserWithToken)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login with username and password

    Args:
        form_data: OAuth2 form with username and password

    Returns:
        User data with access token

    Raises:
        HTTPException: If credentials are invalid
    """
    # Get user from database
    user_dict = user_db.get_user_by_username(form_data.username)

    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(form_data.password, user_dict["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user_dict.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    # Update last login
    user_db.update_last_login(form_data.username)

    # Generate token
    access_token = create_access_token(data={"sub": form_data.username})

    logger.info(f"✅ User logged in: {form_data.username}")

    # Refresh user data with updated last_login
    user_dict = user_db.get_user_by_username(form_data.username)

    return UserWithToken(
        user=User(**user_dict),
        token=Token(access_token=access_token, token_type="bearer")
    )


@router.post("/login/json", response_model=UserWithToken)
async def login_json(credentials: UserLogin):
    """
    Login with JSON body (alternative to form data)

    Args:
        credentials: UserLogin with username and password

    Returns:
        User data with access token
    """
    user_dict = user_db.get_user_by_username(credentials.username)

    if not user_dict or not verify_password(credentials.password, user_dict["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    if not user_dict.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    user_db.update_last_login(credentials.username)
    access_token = create_access_token(data={"sub": credentials.username})

    logger.info(f"✅ User logged in (JSON): {credentials.username}")

    user_dict = user_db.get_user_by_username(credentials.username)

    return UserWithToken(
        user=User(**user_dict),
        token=Token(access_token=access_token, token_type="bearer")
    )


@router.get("/me", response_model=User)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user profile

    Returns:
        Current user data
    """
    return current_user


@router.get("/verify")
async def verify_token_endpoint(current_user: User = Depends(get_current_user)):
    """
    Verify if token is valid

    Returns:
        Success message if token is valid
    """
    return SuccessResponse(
        success=True,
        message="Token is valid",
        data={"username": current_user.username}
    )
