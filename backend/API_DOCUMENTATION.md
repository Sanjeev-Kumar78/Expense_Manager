# Expense Manager API - Complete Documentation

## 🚀 Overview

The Expense Manager API is a comprehensive expense tracking system with AI-powered receipt processing and financial insights. It provides user authentication, expense management, budget tracking, and an AI assistant for financial advice.

## 🏗️ Architecture

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment configuration template
├── routes/
│   ├── users.py           # User authentication and management
│   ├── expense_transactions.py # Expense and transaction management
│   └── summary.py         # Analytics and AI chat endpoints
├── services/
│   ├── chat_agent.py      # AI financial assistant
│   └── preprocessor.py    # Receipt processing with AI
└── utils/
    ├── db.py              # Database operations
    └── __init__.py        # Package initialization
```

## 🛠️ Setup and Installation

### Prerequisites

- Python 3.8+
- MongoDB (local or MongoDB Atlas)
- Google AI API key (for receipt processing)

### 1. Environment Setup

```bash
# Clone and navigate to the project
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and configure:

```env
# Database Configuration
DATABASE_URL=mongodb://localhost:27017
DATABASE_NAME=expense_manager
COLLECTION_USERS=users
COLLECTION_EXPENSES=expenses
COLLECTION_TRANSACTIONS=transactions

# JWT Security
SECRET_KEY=your-super-secret-jwt-key-change-in-production-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google AI (for receipt processing)
GOOGLE_API_KEY=your-google-ai-api-key-here

# Server Configuration
HOST=127.0.0.1
PORT=8000
DEBUG=true
```

### 3. Database Setup

MongoDB collections will be created automatically with proper indexes when you first run the application.

**Required Collections:**

- `users` - User accounts and profiles
- `expenses` - Individual expense records
- `transactions` - Transaction history and details

### 4. Running the Application

```bash
# Development server with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at:

- **API Server**: http://127.0.0.1:8000
- **Interactive Docs**: http://127.0.0.1:8000/docs
- **ReDoc Documentation**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health

## 📖 API Endpoints

### 🔐 Authentication Endpoints (`/users`)

#### Register User

```http
POST /users/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123",
  "budget": 1000.0
}
```

**Response:**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": "60f7b3b3b3b3b3b3b3b3b3b3",
    "username": "johndoe",
    "email": "john@example.com",
    "budget": 1000.0,
    "total_spent": 0.0,
    "created_at": "2024-01-15T10:30:00"
  }
}
```

#### Login User

```http
POST /users/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

#### Get Current User Info

```http
GET /users/me
Authorization: Bearer <token>
```

#### Update Budget

```http
PUT /users/budget
Authorization: Bearer <token>
Content-Type: application/json

{
  "budget": 1500.0
}
```

#### Delete User Account

```http
DELETE /users/me
Authorization: Bearer <token>
```

### 💰 Expense Management (`/expenses`)

#### Create Manual Expense

```http
POST /expenses/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Lunch at Restaurant",
  "category": "Food",
  "amount": 25.50,
  "description": "Business lunch meeting"
}
```

#### Upload Receipt for Processing

```http
POST /expenses/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: [receipt.jpg/pdf/png]
```

**Supported File Types:**

- Images: PNG, JPG, JPEG
- Documents: PDF, TXT

#### Get User Expenses

```http
GET /expenses/?limit=50&skip=0
Authorization: Bearer <token>
```

#### Get User Transactions

```http
GET /expenses/transactions?limit=50&skip=0
Authorization: Bearer <token>
```

#### Delete Expense

```http
DELETE /expenses/{expense_id}
Authorization: Bearer <token>
```

#### Create Manual Transaction

```http
POST /expenses/transactions
Authorization: Bearer <token>
Content-Type: application/json

{
  "expense_id": "60f7b3b3b3b3b3b3b3b3b3b3",
  "category": "Food",
  "amount": 25.50,
  "description": "Transaction description"
}
```

### 📊 Analytics & Summary (`/summary`)

#### Dashboard Summary

```http
GET /summary/dashboard
Authorization: Bearer <token>
```

**Response includes:**

- User information
- Spending summary with budget comparison
- Recent transactions
- Top spending categories
- Monthly spending trends

#### Detailed Spending Summary

```http
GET /summary/spending
Authorization: Bearer <token>
```

#### Category Breakdown

```http
GET /summary/categories?limit=10
Authorization: Bearer <token>
```

#### Monthly Spending Trends

```http
GET /summary/trends?months=6
Authorization: Bearer <token>
```

#### Recent Transactions

```http
GET /summary/recent?limit=20
Authorization: Bearer <token>
```

#### Chat with AI Assistant

```http
POST /summary/chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "How much did I spend on food this month?"
}
```

#### Clear Chat History

```http
DELETE /summary/chat
Authorization: Bearer <token>
```

## 🤖 AI Features

### Receipt Processing

The system uses Google's Generative AI to process uploaded receipts:

1. **Image Processing**: Automatically extracts text from images
2. **PDF Processing**: Converts PDF pages to images and extracts text
3. **Data Extraction**: Identifies expense details (amount, category, description)
4. **Automatic Categorization**: Suggests appropriate expense categories

### AI Financial Assistant

The chat feature provides:

- **Contextual Responses**: Uses your actual financial data
- **Spending Insights**: Analyzes your transaction patterns
- **Budget Advice**: Helps with financial planning
- **Category Analysis**: Explains spending by category

## 🗃️ Database Schema

### Users Collection

```javascript
{
  "_id": ObjectId,
  "username": String,
  "email": String,
  "password": String (hashed),
  "created_at": DateTime,
  "expenses_id": [String],
  "budget": Number,
  "total_spent": Number,
  "transactions_id": [String]
}
```

### Expenses Collection

```javascript
{
  "_id": ObjectId,
  "title": String,
  "category": String,
  "amount": Number,
  "description": String,
  "created_at": DateTime,
  "user_id": String
}
```

### Transactions Collection

```javascript
{
  "_id": ObjectId,
  "user_id": String,
  "expense_id": String,
  "category": String,
  "amount": Number,
  "description": String,
  "created_at": DateTime
}
```

## 🔒 Security Features

### JWT Authentication

- **Token-based authentication** with configurable expiration
- **Secure password hashing** using bcrypt
- **Automatic token validation** on protected endpoints

### Data Protection

- **Input validation** using Pydantic models
- **SQL injection prevention** with MongoDB
- **Error handling** without exposing sensitive information

## 📱 Usage Examples

### Complete Workflow Example

```python
import requests
import json

# Base URL
BASE_URL = "http://127.0.0.1:8000"

# 1. Register a new user
response = requests.post(f"{BASE_URL}/users/register", json={
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123",
    "budget": 2000.0
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Create an expense
requests.post(f"{BASE_URL}/expenses/",
    headers=headers,
    json={
        "title": "Grocery Shopping",
        "category": "Food",
        "amount": 85.50,
        "description": "Weekly groceries"
    }
)

# 3. Get dashboard summary
dashboard = requests.get(f"{BASE_URL}/summary/dashboard", headers=headers)
print(json.dumps(dashboard.json(), indent=2))

# 4. Chat with AI assistant
chat_response = requests.post(f"{BASE_URL}/summary/chat",
    headers=headers,
    json={"message": "What's my total spending this month?"}
)
print(chat_response.json()["message"])
```

### File Upload Example

```python
# Upload receipt for processing
with open("receipt.jpg", "rb") as f:
    files = {"file": ("receipt.jpg", f, "image/jpeg")}
    response = requests.post(f"{BASE_URL}/expenses/upload",
        headers=headers,
        files=files
    )
print(response.json())
```

## 🚀 Deployment

### Production Configuration

1. **Environment Variables:**

   ```env
   DEBUG=false
   SECRET_KEY=<strong-production-secret>
   DATABASE_URL=<production-mongodb-url>
   HOST=0.0.0.0
   PORT=8000
   ```

2. **CORS Configuration:**
   Update allowed origins in `main.py` for your frontend domain.

3. **Database:**
   Use MongoDB Atlas or a dedicated MongoDB server.

4. **Security:**
   - Use HTTPS in production
   - Implement rate limiting
   - Set up proper CORS policies

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Failed:**

   - Check MongoDB is running
   - Verify DATABASE_URL in .env
   - Ensure database name exists

2. **Authentication Errors:**

   - Verify SECRET_KEY is set
   - Check token expiration
   - Ensure proper Authorization header format

3. **File Upload Issues:**

   - Check file size limits
   - Verify supported file types
   - Ensure Google AI API key is valid

4. **AI Processing Errors:**
   - Verify GOOGLE_API_KEY is set correctly
   - Check API quota limits
   - Ensure file is readable

### Health Check

Monitor application health at `/health` endpoint:

```http
GET /health
```

Returns database status, environment configuration, and overall health.

## 📚 API Documentation

- **Interactive Documentation**: `/docs` (Swagger UI)
- **Alternative Documentation**: `/redoc` (ReDoc)
- **OpenAPI Specification**: `/openapi.json`

## 🤝 Support

For issues and questions:

1. Check the health endpoint: `/health`
2. Review logs for error details
3. Verify environment configuration
4. Check database connectivity

The API provides detailed error messages with timestamps and request paths for debugging.

---

**Expense Manager API v1.0.0** - Complete expense management with AI-powered insights
