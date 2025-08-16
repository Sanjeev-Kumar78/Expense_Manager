from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import os
import tempfile
from routes.users import get_current_user
from utils.db import (
    insert_expense,
    insert_transaction,
    get_collection_expense,
    get_collection_transactions,
    delete_expense,
    get_user_by_id
)
from services.preprocessor import process_receipt

# Router setup
router = APIRouter(prefix="/expenses", tags=["expenses"])


# Pydantic models
class ExpenseCreate(BaseModel):
    title: str
    category: str
    amount: float
    description: str


class TransactionCreate(BaseModel):
    expense_id: str
    category: str
    amount: float
    description: str


class ExpenseResponse(BaseModel):
    id: str
    title: str
    category: str
    amount: float
    description: str
    created_at: datetime
    user_id: str


class TransactionResponse(BaseModel):
    id: str
    user_id: str
    expense_id: str
    category: str
    amount: float
    description: str
    created_at: datetime


# Utility functions
def convert_expense_to_response(expense_doc: dict) -> ExpenseResponse:
    """Convert MongoDB expense document to ExpenseResponse model."""
    return ExpenseResponse(
        id=str(expense_doc["_id"]),
        title=expense_doc["title"],
        category=expense_doc["category"],
        amount=expense_doc["amount"],
        description=expense_doc["description"],
        created_at=expense_doc["created_at"],
        user_id=expense_doc["user_id"]
    )


def convert_transaction_to_response(transaction_doc: dict) -> TransactionResponse:
    """Convert MongoDB transaction document to TransactionResponse model."""
    return TransactionResponse(
        id=str(transaction_doc["_id"]),
        user_id=transaction_doc["user_id"],
        expense_id=transaction_doc["expense_id"],
        category=transaction_doc["category"],
        amount=transaction_doc["amount"],
        description=transaction_doc["description"],
        created_at=transaction_doc["created_at"]
    )


# Routes
@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense: ExpenseCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new expense manually."""
    user_id = str(current_user["_id"])

    # Create expense document
    expense_doc = {
        "title": expense.title,
        "category": expense.category,
        "amount": expense.amount,
        "description": expense.description,
        "created_at": datetime.utcnow(),
        "user_id": user_id
    }

    # Insert expense into database
    if not insert_expense(expense_doc):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create expense"
        )

    # Get the created expense to return
    expense_collection = get_collection_expense()
    if expense_collection is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )

    created_expense = expense_collection.find_one({
        "user_id": user_id,
        "title": expense.title,
        "amount": expense.amount
    }, sort=[("created_at", -1)])

    if not created_expense:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created expense"
        )

    return convert_expense_to_response(created_expense)


@router.post("/upload", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_expense_from_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Create expense(s) by uploading and processing a receipt file."""
    user_id = str(current_user["_id"])

    # Validate file type
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.pdf', '.txt'}
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_extension} not supported. Allowed types: {', '.join(allowed_extensions)}"
        )

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        # Process the receipt using the preprocessor service
        result = process_receipt(temp_file_path, user_id)

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to process receipt: {result['error']}"
            )

        # Extract expense data from result
        if "expenses" not in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No expense data found in processed receipt"
            )

        expense_data = result["expenses"]

        # Create expense document
        expense_doc = {
            "title": expense_data.get("title", "Receipt Expense"),
            "category": expense_data.get("category", "Miscellaneous"),
            "amount": float(expense_data.get("amount", 0.0)),
            "description": expense_data.get("description", "Expense from uploaded receipt"),
            "created_at": datetime.utcnow(),
            "user_id": user_id
        }

        # Insert expense into database
        if not insert_expense(expense_doc):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create expense from receipt"
            )

        # Create corresponding transaction
        transaction_doc = {
            "user_id": user_id,
            "expense_id": "auto-generated",  # Will be updated with actual expense ID
            "category": expense_doc["category"],
            "amount": expense_doc["amount"],
            "description": expense_doc["description"],
            "created_at": datetime.utcnow()
        }

        # Insert transaction
        insert_transaction(transaction_doc)

        return {
            "message": "Expense created successfully from receipt",
            "expense": expense_doc,
            "processed_data": result
        }

    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except:
            pass


@router.get("/", response_model=List[ExpenseResponse])
async def get_user_expenses(
    current_user: dict = Depends(get_current_user),
    limit: Optional[int] = 50,
    skip: Optional[int] = 0
):
    """Get all expenses for the current user."""
    user_id = str(current_user["_id"])

    expense_collection = get_collection_expense()
    if expense_collection is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )

    # Query user's expenses with pagination
    expenses_cursor = expense_collection.find(
        {"user_id": user_id}
    ).sort("created_at", -1).skip(skip).limit(limit)

    expenses = []
    for expense_doc in expenses_cursor:
        expenses.append(convert_expense_to_response(expense_doc))

    return expenses


@router.get("/transactions", response_model=List[TransactionResponse])
async def get_user_transactions(
    current_user: dict = Depends(get_current_user),
    limit: Optional[int] = 50,
    skip: Optional[int] = 0
):
    """Get all transactions for the current user."""
    user_id = str(current_user["_id"])

    transaction_collection = get_collection_transactions()
    if transaction_collection is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )

    # Query user's transactions with pagination
    transactions_cursor = transaction_collection.find(
        {"user_id": user_id}
    ).sort("created_at", -1).skip(skip).limit(limit)

    transactions = []
    for transaction_doc in transactions_cursor:
        transactions.append(convert_transaction_to_response(transaction_doc))

    return transactions


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_expense(
    expense_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete an expense and its associated transactions."""
    user_id = str(current_user["_id"])

    # Verify expense belongs to user
    expense_collection = get_collection_expense()
    if expense_collection is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )

    # Check if expense exists and belongs to user
    from bson import ObjectId
    try:
        expense_query_id = ObjectId(expense_id)
    except:
        expense_query_id = expense_id

    expense = expense_collection.find_one({"_id": expense_query_id})
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    if expense["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this expense"
        )

    # Delete expense (this will also clean up transactions and user references)
    if not delete_expense(expense_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete expense"
        )

    return {"message": "Expense deleted successfully"}


@router.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new transaction manually."""
    user_id = str(current_user["_id"])

    # Create transaction document
    transaction_doc = {
        "user_id": user_id,
        "expense_id": transaction.expense_id,
        "category": transaction.category,
        "amount": transaction.amount,
        "description": transaction.description,
        "created_at": datetime.utcnow()
    }

    # Insert transaction into database
    if not insert_transaction(transaction_doc):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create transaction"
        )

    # Get the created transaction to return
    transaction_collection = get_collection_transactions()
    if transaction_collection is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )

    created_transaction = transaction_collection.find_one({
        "user_id": user_id,
        "expense_id": transaction.expense_id,
        "amount": transaction.amount
    }, sort=[("created_at", -1)])

    if not created_transaction:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created transaction"
        )

    return convert_transaction_to_response(created_transaction)
