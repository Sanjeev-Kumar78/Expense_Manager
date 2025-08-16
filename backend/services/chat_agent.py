import google.generativeai as genai
import os
import dotenv
from utils.db import get_all_transactions, get_spending_summary, get_categories

dotenv.load_dotenv()
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY"),
    transport="grpc"
)


def get_user_financial_data(user_id: str = None):
    """
    Fetch user's financial data including transactions, spending, and other details
    for better AI assistance.

    Args:
        user_id: The user's ID to fetch data for (optional for now)

    Returns:
        dict: Financial data summary
    """

    try:
        # Fetch user's transactions
        transactions = get_all_transactions(user_id)

        # Get spending summary
        spending_summary = get_spending_summary(user_id)

        # Get available categories
        categories = get_categories(user_id)

        return {
            "transactions": transactions,
            "spending_summary": spending_summary,
            "categories": categories,
            "total_transactions": len(transactions) if transactions else 0
        }
    except Exception as e:
        print(f"Error fetching user financial data: {e}")
        return {
            "transactions": [],
            "spending_summary": {},
            "categories": [],
            "total_transactions": 0
        }


def support_agent(user_message: str, user_context: dict = None):
    """
    Handles user messages and provides streaming responses using the generative AI model.
    Uses user's financial data for better assistance. Each request is stateless.

    Args:
        user_message: The message from the user.
        user_context: Complete user context including budget, transactions, and spending data.

    Yields:
        Chunks of the response from the AI model.
    """

    # Use provided context or fetch basic data if only user_id provided
    if isinstance(user_context, str):
        # Backward compatibility: if user_context is just user_id
        user_id = user_context
        financial_data = get_user_financial_data(user_id)
        user_context = {
            "user_id": user_id,
            "transactions": financial_data.get("transactions", []),
            "spending_summary": financial_data.get("spending_summary", {}),
            "categories": financial_data.get("categories", []),
            "total_transactions": financial_data.get("total_transactions", 0)
        }
    elif user_context is None:
        user_context = {
            "user_id": "unknown",
            "transactions": [],
            "spending_summary": {},
            "categories": [],
            "total_transactions": 0
        }

    # Create enhanced context-aware system prompt
    budget_info = ""
    if user_context.get("budget") and user_context.get("total_spent") is not None:
        budget_info = f"""
    Budget Information:
    - Budget: ${user_context.get("budget", 0):.2f}
    - Total Spent: ${user_context.get("total_spent", 0):.2f}
    - Remaining Budget: ${user_context.get("remaining_budget", 0):.2f}
    - Budget Utilization: {user_context.get("budget_utilization", 0):.1f}%
    """

    recent_transactions_info = ""
    if user_context.get("recent_transactions"):
        recent_transactions_info = f"""
    Recent Transactions ({len(user_context['recent_transactions'])} items):
    """ + "\n    ".join([f"- {t.category}: ${t.amount:.2f} ({t.description})" for t in user_context['recent_transactions'][:5]])

    top_categories_info = ""
    if user_context.get("top_categories"):
        top_categories_info = f"""
    Top Spending Categories:
    """ + "\n    ".join([f"- {c.category}: ${c.total_amount:.2f} ({c.percentage_of_total:.1f}%)" for c in user_context['top_categories'][:3]])

    system_prompt = f"""
    You are a helpful financial assistant for an expense management application.
    
    User's Financial Context:
    - User ID: {user_context.get('user_id', 'unknown')}
    - Username: {user_context.get('username', 'User')}
    {budget_info}
    - Total Transactions: {user_context.get('total_transactions', len(user_context.get('transactions', [])))}
    - Available Categories: {', '.join([cat.get('name', '') for cat in user_context.get('categories', [])])}
    {recent_transactions_info}
    {top_categories_info}
    
    Help the user with their expense management questions, provide insights about their spending,
    and assist with financial planning based on their transaction history and budget information.
    Be specific with dollar amounts and percentages when providing advice.
    
    User Question: {user_message}
    """

    model = genai.GenerativeModel("models/gemini-2.5-flash")

    # Generate response without maintaining conversation history
    response = model.generate_content(system_prompt, stream=True)

    for chunk in response:
        if chunk.text:
            chunk_text = chunk.text.strip()

            if chunk_text:
                cleaned_chunk = chunk_text.replace('*', '')
                yield cleaned_chunk
