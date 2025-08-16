# 🔧 Expense Manager Backend API

A powerful FastAPI-based backend for expense management with AI-powered features, comprehensive analytics, and intelligent financial insights.

## 🌟 Features

- **🔐 JWT Authentication** - Secure user registration and login with bcrypt password hashing
- **💰 Expense Management** - Complete CRUD operations for expenses and transactions
- **🤖 AI Receipt Processing** - Automatic extraction from images (PNG, JPG) and PDFs using Google AI
- **📊 Financial Analytics** - Spending summaries, trends, and category-wise insights
- **💬 AI Financial Assistant** - Chat-based financial advice using your actual spending data
- **🔍 Smart Categorization** - Automatic expense categorization based on merchant and items
- **📈 Budget Tracking** - Set and monitor spending limits with real-time alerts
- **🔄 Real-time Updates** - Async operations for optimal performance
- **📱 Mobile-Ready API** - RESTful endpoints designed for web and mobile frontends

## 🏗️ Backend Architecture

```mermaid
graph TB
    subgraph "API Layer"
        A[FastAPI Main App]
        B[CORS Middleware]
        C[Exception Handlers]
        D[Request Validation]
    end

    subgraph "Route Handlers"
        E[Users Router]
        F[Expenses Router]
        G[Summary Router]
    end

    subgraph "Services Layer"
        H[Chat Agent Service]
        I[Preprocessor Service]
        J[Authentication Service]
        K[Analytics Service]
    end

    subgraph "Data Layer"
        L[Database Utils]
        M[MongoDB Driver PyMongo]
        N[Connection Pool]
    end

    subgraph "External APIs"
        O[Google AI API]
        P[MongoDB Atlas]
    end

    A --> B
    A --> C
    A --> D
    A --> E
    A --> F
    A --> G

    E --> J
    E --> L
    F --> L
    F --> I
    G --> H
    G --> K
    G --> L

    H --> O
    I --> O

    L --> M
    M --> N
    N --> P

    style A fill:#e1f5fe
    style H fill:#f3e5f5
    style I fill:#f3e5f5
    style O fill:#fff3e0
    style P fill:#fff3e0
```

## ️ Technology Stack

| Category                | Technology                   | Purpose                                      |
| ----------------------- | ---------------------------- | -------------------------------------------- |
| **Web Framework**       | FastAPI >=0.116.1            | High-performance async web framework         |
| **Database**            | MongoDB                      | NoSQL database for flexible document storage |
| **Database Driver**     | PyMongo >=4.14.0             | MongoDB operations and connectivity          |
| **AI Processing**       | Google Generative AI >=0.8.5 | Receipt processing and chat assistant        |
| **Authentication**      | Python-JOSE >=3.5.0          | JWT token handling                           |
| **Password Security**   | PassLib[bcrypt] >=1.7.4      | Secure password hashing                      |
| **Data Validation**     | Pydantic >=2.11.7            | Request/response validation                  |
| **File Processing**     | PDF2Image >=1.17.0           | PDF to image conversion                      |
| **PDF Text Extraction** | PyMuPDF (Fitz)               | Text extraction from PDFs                    |
| **Server**              | Uvicorn[standard] >=0.35.0   | ASGI server with auto-reload                 |

## � Quick Start

### Prerequisites

- **Python 3.12+** (recommended for best performance)
- **MongoDB** (local installation or MongoDB Atlas cloud)
- **Google AI API key** (for AI receipt processing and chat features)

### 1. Environment Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Windows CMD
.venv\Scripts\activate.bat
# macOS/Linux
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Alternative: Using uv (faster package manager)
pip install uv
uv pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the backend directory with the following configuration:

```env
# Database Configuration
DATABASE_URL=mongodb://localhost:27017
DATABASE_NAME=expense_manager
COLLECTION_USERS=users
COLLECTION_EXPENSES=expenses
COLLECTION_TRANSACTIONS=transactions

# JWT Security (IMPORTANT: Change in production!)
SECRET_KEY=your-super-secret-jwt-key-change-in-production-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google AI (Required for AI features)
GEMINI_API_KEY=your-google-ai-api-key-here

# Server Configuration
HOST=127.0.0.1
PORT=8000
DEBUG=true
```

### 4. Database Setup

MongoDB collections will be created automatically with proper indexes when you first run the application.

**Collections Created:**

- `users` - User accounts and profiles
- `expenses` - Individual expense records
- `transactions` - Transaction history and details

### 5. Run the Application

```bash
# Development server with auto-reload
python main.py

# Alternative: Using uvicorn directly
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**🎉 Success!** The API will be available at:

- **API Server**: http://127.0.0.1:8000
- **Interactive Docs**: http://127.0.0.1:8000/docs
- **ReDoc Documentation**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health

## 📡 API Endpoints Overview

### 🔐 Authentication (`/users`)

| Method | Endpoint          | Description         | Auth Required |
| ------ | ----------------- | ------------------- | ------------- |
| POST   | `/users/register` | Register new user   | ❌            |
| POST   | `/users/login`    | User login          | ❌            |
| GET    | `/users/me`       | Get user profile    | ✅            |
| PUT    | `/users/budget`   | Set/update budget   | ✅            |
| DELETE | `/users/me`       | Delete user account | ✅            |

### 💰 Expenses (`/expenses`)

| Method | Endpoint                 | Description                      | Auth Required |
| ------ | ------------------------ | -------------------------------- | ------------- |
| GET    | `/expenses/`             | List user expenses               | ✅            |
| POST   | `/expenses/`             | Create new expense               | ✅            |
| POST   | `/expenses/upload`       | Upload receipt for AI processing | ✅            |
| GET    | `/expenses/transactions` | Get user transactions            | ✅            |
| POST   | `/expenses/transactions` | Create manual transaction        | ✅            |
| DELETE | `/expenses/{id}`         | Delete expense                   | ✅            |

### 📊 Analytics & AI (`/summary`)

| Method | Endpoint              | Description             | Auth Required |
| ------ | --------------------- | ----------------------- | ------------- |
| GET    | `/summary/dashboard`  | Complete dashboard data | ✅            |
| GET    | `/summary/spending`   | Spending summary        | ✅            |
| GET    | `/summary/categories` | Category breakdown      | ✅            |
| GET    | `/summary/trends`     | Monthly spending trends | ✅            |
| GET    | `/summary/recent`     | Recent transactions     | ✅            |
| POST   | `/summary/chat`       | Chat with AI assistant  | ✅            |
| DELETE | `/summary/chat`       | Clear chat history      | ✅            |

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

## 🚀 Production Deployment

### Environment Configuration

```env
# Production Environment Variables
DEBUG=false
SECRET_KEY=your-production-secret-key-at-least-32-characters-long-and-random
DATABASE_URL=mongodb+srv://user:password@cluster.mongodb.net/expense_manager
GEMINI_API_KEY=your-production-google-ai-api-key
HOST=0.0.0.0
PORT=8000

# Security Settings
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM=HS256
```

### Production Checklist

1. **🔒 Security**

   - Generate a strong SECRET_KEY (minimum 32 characters)
   - Use MongoDB with authentication enabled
   - Enable HTTPS with SSL certificates
   - Configure proper CORS origins
   - Implement rate limiting

2. **🗄️ Database**

   - Use MongoDB Atlas or dedicated MongoDB server
   - Set up database backups
   - Configure connection pooling
   - Enable database authentication

3. **📊 Monitoring**

   - Set up application logging
   - Configure health check monitoring
   - Implement error tracking
   - Monitor API performance metrics

4. **🔧 Infrastructure**
   - Use reverse proxy (nginx recommended)
   - Configure load balancing if needed
   - Set up CI/CD pipeline
   - Configure automated deployments

### Docker Production Deployment

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Environment Variables Checklist

**Required:**

- ✅ `SECRET_KEY` - JWT secret key (minimum 32 characters)
- ✅ `GEMINI_API_KEY` - Google AI API key for receipt processing
- ✅ `DATABASE_URL` - MongoDB connection string

**Optional:**

- `DATABASE_NAME` (default: expense_manager)
- `HOST` (default: 127.0.0.1)
- `PORT` (default: 8000)
- `DEBUG` (default: true)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 30)

## 🐳 Docker Support

Build and run with Docker:

```bash
# Build the image
docker build -t expense-manager-backend .

# Run the container
docker run -p 8000:8000 --env-file .env expense-manager-backend

# Or using docker-compose (if docker-compose.yml exists)
docker-compose up --build
```

## 📊 Performance & Monitoring

- **⚡ Async Operations**: All database operations use async/await for non-blocking I/O
- **🔄 Connection Pooling**: MongoDB connection pooling with PyMongo for optimal performance
- **✅ Request Validation**: Pydantic models ensure data integrity and prevent malformed requests
- **🛡️ Error Handling**: Comprehensive exception handling with proper HTTP status codes
- **🌐 CORS Support**: Configured for secure frontend integration
- **📈 Health Monitoring**: Built-in health check endpoint for monitoring

## 🔒 Security Features

### Authentication & Authorization

- **🔐 JWT Authentication**: Secure token-based authentication with configurable expiration
- **🔒 Password Security**: bcrypt hashing with salt for secure password storage
- **🎫 Token Validation**: Automatic token validation on all protected endpoints
- **⏰ Session Management**: Configurable token expiration times

### Data Protection

- **✅ Input Validation**: Pydantic models prevent injection attacks and ensure data integrity
- **🛡️ NoSQL Security**: MongoDB with proper query structure prevents injection
- **🚫 Error Sanitization**: Error responses don't expose sensitive system information
- **🌐 CORS Configuration**: Controlled cross-origin requests for web security

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Failed:**

   - Check MongoDB is running
   - Verify `DATABASE_URL` in .env
   - Ensure database name exists

2. **Authentication Errors:**

   - Verify `SECRET_KEY` is set
   - Check token expiration
   - Ensure proper Authorization header format

3. **File Upload Issues:**

   - Check file size limits
   - Verify supported file types
   - Ensure Gemini AI API key is valid

4. **AI Processing Errors:**
   - Verify `GEMINI_API_KEY` is set correctly
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

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

1. **Fork the repository** and clone your fork
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Set up development environment** following the Quick Start guide
4. **Make your changes** with clear, descriptive commits
5. **Update documentation** if needed
6. **Submit a pull request** with a clear description

## 🆘 Support & Troubleshooting

### Common Issues

1. **🔌 Database Connection Failed**

   ```bash
   # Check MongoDB status
   # Windows
   net start MongoDB
   # macOS
   brew services start mongodb-community
   # Linux
   sudo systemctl start mongod
   ```

2. **🔑 Authentication Errors**

   - Verify `SECRET_KEY` is set in `.env`
   - Check token hasn't expired
   - Ensure Authorization header format: `Bearer <token>`

3. **📁 File Upload Issues**

   - Verify Google AI API key is valid
   - Check file size limits (default: 10MB)
   - Ensure supported file types: PNG, JPG, PDF

4. **🤖 AI Processing Errors**
   - Confirm `GEMINI_API_KEY` is correctly set
   - Check API quota limits in Google Cloud Console
   - Verify internet connectivity

### Getting Help

1. **📚 Check Documentation**: Review API docs at `/docs`
2. **🔍 Search Issues**: Look through existing [GitHub issues](https://github.com/Sanjeev-Kumar78/Expense_Manager/issues)
3. **💬 Ask Questions**: Create a new issue with the `question` label
4. **🐛 Report Bugs**: Use the bug report template
5. **💡 Feature Requests**: Submit enhancement requests

### Health Check

Monitor application status:

```http
GET /health
```

Returns:

- Database connectivity status
- API version information
- Environment configuration (non-sensitive)
- Service uptime

## 📚 Additional Resources

### API Documentation

- **📖 Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **📋 Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **⚙️ OpenAPI Schema**: http://localhost:8000/openapi.json

### Related Documentation

- **🏠 Main Project**: [../README.md](../README.md)
- **🖥️ Frontend**: [../frontend/README.md](../frontend/README.md) (Coming Soon)
- **📝 API Examples**: Check `/docs` for interactive examples

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

**🔧 Expense Manager Backend API v1.0.0**  
Built with ❤️ using FastAPI, MongoDB, and Google AI
