"""Routes package initializer.

Expose each router for easy inclusion in the main application.
"""
from .users import router as users_router
from .expense_transactions import router as expenses_router
from .summary import router as summary_router

__all__ = [
    "users_router",
    "expenses_router",
    "summary_router",
]
