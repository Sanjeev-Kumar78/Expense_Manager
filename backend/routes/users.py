from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from typing import Optional
from utils.db import (
    insert_user,
    get_user_by_email,
    get_user_by_id,
    delete_user,
    get_user_id_by_username
)

# Router setup
router = APIRouter(prefix="/users", tags=["users"])
security = HTTPBearer()

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    budget: float = 0.0


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    budget: float
    total_spent: float
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseModel):
    email: Optional[str] = None

# Utility functions


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(email: str, password: str):
    """Authenticate a user by email and password."""
    user = get_user_by_email(email)
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get the current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(credentials.credentials,
                             SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    user = get_user_by_email(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


def convert_user_to_response(user_doc: dict) -> UserResponse:
    """Convert MongoDB user document to UserResponse model."""
    return UserResponse(
        id=str(user_doc["_id"]),
        username=user_doc["username"],
        email=user_doc["email"],
        budget=user_doc.get("budget", 0.0),
        total_spent=user_doc.get("total_spent", 0.0),
        created_at=user_doc["created_at"]
    )

# Routes


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    """Register a new user."""
    # Check if user already exists
    existing_user = get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    existing_username = get_user_id_by_username(user.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create user document
    hashed_password = get_password_hash(user.password)
    user_doc = {
        "username": user.username,
        "email": user.email,
        "password": hashed_password,
        "created_at": datetime.utcnow(),
        "expenses_id": [],
        "budget": user.budget,
        "total_spent": 0.0,
        "transactions_id": []
    }

    # Insert user into database
    if not insert_user(user_doc):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

    # Get the created user to return with token
    created_user = get_user_by_email(user.email)
    if not created_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created user"
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=convert_user_to_response(created_user)
    )


@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin):
    """Login a user and return JWT token."""
    user = authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=convert_user_to_response(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    return convert_user_to_response(current_user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(current_user: dict = Depends(get_current_user)):
    """Delete the current user account."""
    user_id = str(current_user["_id"])

    if not delete_user(user_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

    return {"message": "User deleted successfully"}


@router.put("/budget", response_model=UserResponse)
async def update_user_budget(
    budget_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update user's budget."""
    from utils.db import update_budget

    new_budget = budget_data.get("budget")
    if new_budget is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Budget value is required"
        )

    if not isinstance(new_budget, (int, float)) or new_budget < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Budget must be a positive number"
        )

    user_id = str(current_user["_id"])
    if not update_budget(user_id, float(new_budget)):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update budget"
        )

    # Get updated user data
    updated_user = get_user_by_id(user_id)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve updated user data"
        )

    return convert_user_to_response(updated_user)
    password: str
