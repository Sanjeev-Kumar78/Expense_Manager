from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from routes.users import get_current_user
from utils.db import (
    get_all_transactions,
    get_spending_summary,
    get_categories,
    get_collection_transactions,
    get_user_by_id
)
from services.chat_agent import support_agent, clear_conversation

# Router setup
router = APIRouter(prefix="/summary", tags=["summary"])

# Pydantic models


class SpendingSummary(BaseModel):
    total_spent: float
    budget: float
    remaining_budget: float
    budget_utilization_percentage: float
    categories: Dict[str, Dict[str, Any]]


class MonthlySpending(BaseModel):
    month: str
    year: int
    total_amount: float
    transaction_count: int


class CategorySpending(BaseModel):
    category: str
    total_amount: float
    transaction_count: int
    percentage_of_total: float


class RecentTransaction(BaseModel):
    id: str
    category: str
    amount: float
    description: str
    created_at: datetime


class DashboardSummary(BaseModel):
    user_info: Dict[str, Any]
    spending_summary: SpendingSummary
    recent_transactions: List[RecentTransaction]
    top_categories: List[CategorySpending]
    monthly_trends: List[MonthlySpending]


class ChatMessage(BaseModel):
    message: str

# Utility functions


def calculate_budget_metrics(user_data: dict, total_spent: float) -> Dict[str, float]:
    """Calculate budget-related metrics."""
    budget = user_data.get("budget", 0.0)
    remaining = max(0, budget - total_spent)
    utilization = (total_spent / budget * 100) if budget > 0 else 0

    return {
        "budget": budget,
        "remaining_budget": remaining,
        "budget_utilization_percentage": min(100, utilization)
    }


def get_monthly_spending_trends(user_id: str, months: int = 6) -> List[MonthlySpending]:
    """Get monthly spending trends for the user."""
    transaction_collection = get_collection_transactions()
    if transaction_collection is None:
        return []

    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=months * 30)

    # Aggregation pipeline for monthly trends
    from bson import ObjectId
    try:
        user_query_id = ObjectId(user_id) if len(user_id) == 24 else user_id
    except:
        user_query_id = user_id

    pipeline = [
        {
            "$match": {
                "user_id": user_query_id,
                "created_at": {"$gte": start_date, "$lte": end_date}
            }
        },
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$created_at"},
                    "month": {"$month": "$created_at"}
                },
                "total_amount": {"$sum": "$amount"},
                "transaction_count": {"$sum": 1}
            }
        },
        {
            "$sort": {"_id.year": 1, "_id.month": 1}
        }
    ]

    try:
        results = list(transaction_collection.aggregate(pipeline))
        monthly_trends = []

        for result in results:
            month_names = [
                "", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
            ]
            month_name = month_names[result["_id"]["month"]]

            monthly_trends.append(MonthlySpending(
                month=month_name,
                year=result["_id"]["year"],
                total_amount=result["total_amount"],
                transaction_count=result["transaction_count"]
            ))

        return monthly_trends
    except Exception as e:
        print(f"Error getting monthly trends: {e}")
        return []


def get_top_categories(user_id: str, limit: int = 5) -> List[CategorySpending]:
    """Get top spending categories for the user."""
    spending_summary = get_spending_summary(user_id)
    if not spending_summary:
        return []

    # Calculate total spending
    total_spending = sum(cat_data["total"]
                         for cat_data in spending_summary.values())

    # Sort categories by total spending
    sorted_categories = sorted(
        spending_summary.items(),
        key=lambda x: x[1]["total"],
        reverse=True
    )[:limit]

    top_categories = []
    for category, data in sorted_categories:
        percentage = (data["total"] / total_spending *
                      100) if total_spending > 0 else 0
        top_categories.append(CategorySpending(
            category=category,
            total_amount=data["total"],
            transaction_count=data["count"],
            percentage_of_total=percentage
        ))

    return top_categories


def get_recent_transactions_summary(user_id: str, limit: int = 10) -> List[RecentTransaction]:
    """Get recent transactions for the user."""
    transactions = get_all_transactions(user_id)

    # Sort by created_at and limit
    recent_transactions = sorted(
        transactions,
        key=lambda x: x.get("created_at", datetime.min),
        reverse=True
    )[:limit]

    result = []
    for transaction in recent_transactions:
        result.append(RecentTransaction(
            id=str(transaction["_id"]),
            category=transaction.get("category", "Unknown"),
            amount=transaction.get("amount", 0.0),
            description=transaction.get("description", ""),
            created_at=transaction.get("created_at", datetime.utcnow())
        ))

    return result

# Routes


@router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard_summary(current_user: dict = Depends(get_current_user)):
    """Get comprehensive dashboard summary for the user."""
    user_id = str(current_user["_id"])

    # Get spending summary
    spending_data = get_spending_summary(user_id)
    total_spent = current_user.get("total_spent", 0.0)

    # Calculate budget metrics
    budget_metrics = calculate_budget_metrics(current_user, total_spent)

    # Create spending summary
    spending_summary = SpendingSummary(
        total_spent=total_spent,
        budget=budget_metrics["budget"],
        remaining_budget=budget_metrics["remaining_budget"],
        budget_utilization_percentage=budget_metrics["budget_utilization_percentage"],
        categories=spending_data
    )

    # Get other dashboard components
    recent_transactions = get_recent_transactions_summary(user_id)
    top_categories = get_top_categories(user_id)
    monthly_trends = get_monthly_spending_trends(user_id)

    # User info
    user_info = {
        "id": user_id,
        "username": current_user["username"],
        "email": current_user["email"],
        "created_at": current_user["created_at"]
    }

    return DashboardSummary(
        user_info=user_info,
        spending_summary=spending_summary,
        recent_transactions=recent_transactions,
        top_categories=top_categories,
        monthly_trends=monthly_trends
    )


@router.get("/spending", response_model=SpendingSummary)
async def get_spending_summary_detail(current_user: dict = Depends(get_current_user)):
    """Get detailed spending summary."""
    user_id = str(current_user["_id"])

    # Get spending data
    spending_data = get_spending_summary(user_id)
    total_spent = current_user.get("total_spent", 0.0)

    # Calculate budget metrics
    budget_metrics = calculate_budget_metrics(current_user, total_spent)

    return SpendingSummary(
        total_spent=total_spent,
        budget=budget_metrics["budget"],
        remaining_budget=budget_metrics["remaining_budget"],
        budget_utilization_percentage=budget_metrics["budget_utilization_percentage"],
        categories=spending_data
    )


@router.get("/categories", response_model=List[CategorySpending])
async def get_category_breakdown(
    current_user: dict = Depends(get_current_user),
    limit: Optional[int] = 10
):
    """Get spending breakdown by categories."""
    user_id = str(current_user["_id"])
    return get_top_categories(user_id, limit)


@router.get("/trends", response_model=List[MonthlySpending])
async def get_spending_trends(
    current_user: dict = Depends(get_current_user),
    months: Optional[int] = 6
):
    """Get monthly spending trends."""
    user_id = str(current_user["_id"])
    return get_monthly_spending_trends(user_id, months)


@router.get("/recent", response_model=List[RecentTransaction])
async def get_recent_transactions(
    current_user: dict = Depends(get_current_user),
    limit: Optional[int] = 20
):
    """Get recent transactions."""
    user_id = str(current_user["_id"])
    return get_recent_transactions_summary(user_id, limit)


@router.post("/chat")
async def chat_with_ai(
    message: ChatMessage,
    current_user: dict = Depends(get_current_user)
):
    """Chat with AI financial assistant."""
    user_id = str(current_user["_id"])

    try:
        # Get AI response using the chat agent (synchronous generator)
        response_chunks = []
        for chunk in support_agent(message.message, user_id):
            response_chunks.append(chunk)

        full_response = "".join(response_chunks)

        return {
            "message": full_response,
            "user_message": message.message,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}"
        )


@router.delete("/chat")
async def clear_chat_history(current_user: dict = Depends(get_current_user)):
    """Clear chat conversation history."""
    try:
        clear_conversation()
        return {"message": "Chat history cleared successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing chat history: {str(e)}"
        )
