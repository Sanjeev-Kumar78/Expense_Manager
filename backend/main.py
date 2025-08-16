from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
import os
from datetime import datetime

# Import routers
from routes.users import router as users_router
from routes.expense_transactions import router as expenses_router
from routes.summary import router as summary_router

# Import database utilities
from utils.db import get_db, close_db

# Application metadata
APP_NAME = "Expense Manager API"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = """
# Expense Manager API

A comprehensive expense management system with the following features:

## Features

### 🔐 User Management
- User registration and authentication with JWT tokens
- Secure password hashing with bcrypt
- User profile management
- Budget setting and tracking

### 💰 Expense Tracking
- Manual expense creation
- Receipt processing with AI (upload images/PDFs)
- Automatic expense categorization
- Transaction management

### 📊 Analytics & Insights
- Spending summaries by category
- Budget vs actual spending comparison
- Monthly spending trends
- Top spending categories analysis

### 🤖 AI Assistant
- Chat with AI financial assistant
- Personalized spending insights
- Financial advice based on your data

## Authentication
Most endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Getting Started
1. Register a new account at `/users/register`
2. Login to get your JWT token at `/users/login`
3. Start adding expenses manually or by uploading receipts
4. View your spending summary and insights

## File Upload Support
The system supports processing receipts in the following formats:
- Images: PNG, JPG, JPEG
- Documents: PDF, TXT

## Environment Variables Required
- `DATABASE_URL`: MongoDB connection string
- `DATABASE_NAME`: MongoDB database name
- `COLLECTION_USERS`: Users collection name
- `COLLECTION_EXPENSES`: Expenses collection name
- `COLLECTION_TRANSACTIONS`: Transactions collection name
- `SECRET_KEY`: JWT secret key
- `GOOGLE_API_KEY`: Google AI API key for receipt processing
"""

# Create FastAPI application
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    # Configure appropriately for production
    allow_origins=[os.getenv("FRONTEND_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handlers


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with additional context."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path),
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": str(exc) if os.getenv("DEBUG") == "true" else "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )

# Include routers
app.include_router(users_router)
app.include_router(expenses_router)
app.include_router(summary_router)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint with API information."""
    return {
        "message": f"Welcome to {APP_NAME}",
        "version": APP_VERSION,
        "status": "active",
        "timestamp": datetime.utcnow(),
        "documentation": "/docs",
        "endpoints": {
            "users": "/users",
            "expenses": "/expenses",
            "summary": "/summary"
        }
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    # Check database connection
    db = get_db()
    db_status = "connected" if db is not None else "disconnected"

    # Check environment variables
    required_env_vars = [
        "DATABASE_NAME",
        "COLLECTION_USERS",
        "COLLECTION_EXPENSES",
        "COLLECTION_TRANSACTIONS",
        "SECRET_KEY"
    ]

    env_status = {}
    for var in required_env_vars:
        env_status[var] = "set" if os.getenv(var) else "missing"

    # Overall health status
    is_healthy = (
        db_status == "connected" and
        all(status == "set" for status in env_status.values())
    )

    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "timestamp": datetime.utcnow(),
        "version": APP_VERSION,
        "database": db_status,
        "environment": env_status,
        "uptime": "Service is running"
    }


# API Information endpoint
@app.get("/info", tags=["Information"])
async def api_info():
    """Get detailed API information and statistics."""

    # Get route information
    routes_info = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes_info.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, 'name', 'Unknown')
            })

    return {
        "api_name": APP_NAME,
        "version": APP_VERSION,
        "description": "Expense management system with AI-powered insights",
        "total_routes": len(routes_info),
        "routes": routes_info,
        "features": [
            "User Authentication (JWT)",
            "Expense Tracking",
            "Receipt Processing (AI)",
            "Spending Analytics",
            "Budget Management",
        ],
        "supported_file_types": [
            "PNG", "JPG", "JPEG", "PDF", "TXT"
        ],
        "timestamp": datetime.utcnow()
    }

# Development server
if __name__ == "__main__":
    # Configuration for development
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    print(f"🌟 Starting {APP_NAME} v{APP_VERSION}")
    print(f"📍 Server will be available at: http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔍 Health Check: http://{host}:{port}/health")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
