import google.generativeai as genai
import os
import dotenv
from utils.db import get_all_transactions, get_spending_summary, get_categories

dotenv.load_dotenv()
genai.configure(
    api_key=os.getenv("GOOGLE_API_KEY"),
    transport="grpc"
)

# Store conversation history
conversation_history = []


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


def support_agent(user_message: str, user_id: str = None):
    """
    Handles user messages and provides streaming responses using the generative AI model.
    Maintains conversation context and uses user's financial data for better assistance.

    Args:
        user_message: The message from the user.
        user_id: The user's ID for fetching personalized data.

    Yields:
        Chunks of the response from the AI model.
    """
    global conversation_history

    # Fetch user's financial data
    financial_data = get_user_financial_data(user_id)

    # Create context-aware system prompt
    system_prompt = f"""
    You are a helpful financial assistant for an expense management application.
    
    User's Financial Context:
    - Total Transactions: {financial_data['total_transactions']}
    - Available Categories: {', '.join([cat.get('name', '') for cat in financial_data['categories']])}
    - Recent Spending Summary: {financial_data['spending_summary']}
    
    Help the user with their expense management questions, provide insights about their spending,
    and assist with financial planning based on their transaction history.
    """

    # Add system context if this is the start of conversation
    if not conversation_history:
        conversation_history.append({"role": "user", "parts": [system_prompt]})

    # Add user message to history
    conversation_history.append({"role": "user", "parts": [user_message]})

    model = genai.GenerativeModel("models/gemini-2.5-flash")

    # Use conversation history for context
    response = model.generate_content(conversation_history, stream=True)

    assistant_response = ""

    for chunk in response:
        if chunk.text:
            chunk_text = chunk.text.strip()

            if chunk_text:
                cleaned_chunk = chunk_text.replace('*', '')
                assistant_response += cleaned_chunk
                yield cleaned_chunk

    # Add assistant response to history
    if assistant_response:
        conversation_history.append(
            {"role": "model", "parts": [assistant_response]})


def clear_conversation():
    """Clear the conversation history."""
    global conversation_history
    conversation_history = []
