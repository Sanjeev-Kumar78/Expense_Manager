"""Services package initializer.

Expose useful service functions without wildcard imports to reduce circular import risk.
"""
from .chat_agent import support_agent, get_user_financial_data
from .preprocessor import process_receipt

__all__ = [
    "support_agent",
    "get_user_financial_data",
    "process_receipt",
]
