"""Utils package initializer.

Expose commonly used database helpers from utils.db with explicit names to reduce
import-time side-effects.
"""
from .db import (
    get_db,
    get_collection_expense,
    get_collection_users,
    get_collection_transactions,
    validate_schema,
    insert_user,
    insert_expense,
    insert_transaction,
    get_user_id_by_username,
    get_user_by_email,
    get_user_by_id,
    update_budget,
    delete_expense,
    delete_user,
    get_all_transactions,
    get_spending_summary,
    get_categories,
    close_db,
)

__all__ = [name for name in dir() if not name.startswith("_")]
