from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from bson import ObjectId
import datetime
import os
import dotenv

dotenv.load_dotenv()
db: Database | None = None

SCHEMAS = {
    "expenses": {
        "title": "string",
        "category": "string",
        "amount": "float",
        "description": "string",
        "created_at": "datetime",
        "user_id": "string"
    },
    "users": {
        "username": "string",
        "email": "string",
        "password": "string",
        "created_at": "datetime",
        "expenses_id": "array",
        "budget": "float",
        "total_spent": "float",
        "transactions_id": "array"
    },
    "transactions": {
        "user_id": "string",
        "expense_id": "string",
        "category": "string",
        "amount": "float",
        "description": "string",
        "created_at": "datetime"
    }
}


def get_db() -> Database | None:
    try:
        global db
        if db is None:
            # validate envs early
            url = os.getenv("DATABASE_URL")
            name = os.getenv("DATABASE_NAME")
            users_coll = os.getenv("COLLECTION_USERS")
            if not name or not users_coll:
                raise RuntimeError(
                    "Missing DATABASE_NAME or COLLECTION_USERS environment variable")
            client = MongoClient(url) if url else MongoClient()
            db = client[name]
            # correct PyMongo API
            db[users_coll].create_index({"email": 1}, unique=True)
            db[users_coll].create_index({"username": 1}, unique=True)
            print(f"Connected to database: {name}")
        return db
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


def get_collection_expense() -> Collection:
    # Get the expenses collection
    db = get_db()
    if db is not None:
        return db[os.getenv("COLLECTION_EXPENSES")]
    return None


def get_collection_users() -> Collection:
    # Get the users collection
    db = get_db()
    if db is not None:
        return db[os.getenv("COLLECTION_USERS")]
    return None


def get_collection_transactions() -> Collection:
    # Get the transactions collection
    db = get_db()
    if db is not None:
        return db[os.getenv("COLLECTION_TRANSACTIONS")]
    return None


def validate_schema(collection_name: str, document: dict) -> bool:
    schema = SCHEMAS.get(collection_name)
    if schema is None:
        print(f"Unknown collection: {collection_name}")
        return False

    TYPE_MAP = {
        "string": str,
        "float": float,
        "datetime": datetime.datetime,
        "array": list,
    }

    for field, field_type in schema.items():
        if field not in document:
            print(f"Missing field: {field}")
            return False
        expected = TYPE_MAP.get(field_type)
        if expected is None:
            print(f"Unknown type in schema for field '{field}': {field_type}")
            return False
        if not isinstance(document[field], expected):
            print(
                f"Invalid type for field '{field}': expected {field_type}, got {type(document[field]).__name__}")
            return False
    return True


def insert_user(user: dict) -> bool:
    # Insert a new user into the database
    if not validate_schema("users", user):
        return False
    collection = get_collection_users()
    if collection is not None and not collection.find_one({"$or": [{"email": user["email"]}, {"username": user["username"]}]}):
        collection.insert_one(user)
        return True
    return False


def insert_expense(expense: dict) -> bool:
    # Insert a new expense into the database and update the user's references/total_spent
    if not validate_schema("expenses", expense):
        return False
    exp_coll = get_collection_expense()
    user_coll = get_collection_users()
    if exp_coll is None:
        return False

    try:
        result = exp_coll.insert_one(expense)
        exp_id = result.inserted_id
    except Exception:
        return False

    # Try to update user: push expense id (stored as string) and increment total_spent
    try:
        user_id_val = expense.get("user_id")
        if user_id_val and user_coll is not None:
            try:
                user_query_id = ObjectId(user_id_val) if isinstance(
                    user_id_val, str) and len(user_id_val) == 24 else user_id_val
            except Exception:
                user_query_id = user_id_val

            # store the expense id as string to be compatible with possible client-side usage
            try:
                user_coll.update_one({"_id": user_query_id}, {
                                     "$push": {"expenses_id": str(exp_id)}})
            except Exception:
                pass

            # increment total_spent by the expense amount if numeric
            try:
                amt = expense.get("amount")
                if isinstance(amt, (int, float)):
                    user_coll.update_one({"_id": user_query_id}, {
                                         "$inc": {"total_spent": amt}})
            except Exception:
                pass
    except Exception:
        pass

    return True


def insert_transaction(transaction: dict) -> bool:
    # Insert a new transaction and update the user's transactions list and total_spent
    if not validate_schema("transactions", transaction):
        return False
    tx_coll = get_collection_transactions()
    user_coll = get_collection_users()
    if tx_coll is None:
        return False

    try:
        result = tx_coll.insert_one(transaction)
        tx_id = result.inserted_id
    except Exception:
        return False

    # Update user: push transaction id (as string) and increment total_spent
    try:
        user_id_val = transaction.get("user_id")
        if user_id_val and user_coll is not None:
            try:
                user_query_id = ObjectId(user_id_val) if isinstance(
                    user_id_val, str) and len(user_id_val) == 24 else user_id_val
            except Exception:
                user_query_id = user_id_val

            try:
                user_coll.update_one({"_id": user_query_id}, {
                                     "$push": {"transactions_id": str(tx_id)}})
            except Exception:
                pass

            try:
                amt = transaction.get("amount")
                if isinstance(amt, (int, float)):
                    user_coll.update_one({"_id": user_query_id}, {
                                         "$inc": {"total_spent": amt}})
            except Exception:
                pass
    except Exception:
        pass

    return True


def get_user_id_by_username(username: str) -> str:
    # Get a user ID by their username
    collection = get_collection_users()
    if collection is not None:
        user = collection.find_one({"username": username})
        if user is not None:
            return str(user["_id"])
    return None


def get_user_by_email(email: str) -> dict:
    # Get a user by their email address
    collection = get_collection_users()
    if collection is not None:
        user = collection.find_one({"email": email})
        return user
    return None


def get_user_by_id(user_id: str) -> dict:
    # Get a user by their ID
    collection = get_collection_users()
    if collection is not None:
        try:
            # convert the string to ObjectId when possible
            query_id = ObjectId(user_id) if isinstance(
                user_id, str) and len(user_id) == 24 else user_id
        except Exception:
            query_id = user_id
        user = collection.find_one({"_id": query_id})
        return user
    return None


def update_budget(user_id: str, new_budget: float) -> bool:
    # Update the budget for a user
    collection = get_collection_users()
    if collection is not None:
        result = collection.update_one({"_id": ObjectId(user_id)}, {
                                       "$set": {"budget": new_budget}})
        return result.modified_count > 0
    return False


def delete_expense(expense_id: str) -> bool:
    # Delete an expense and clean up associated transactions and user references
    exp_coll = get_collection_expense()
    if exp_coll is None:
        return False
    tx_coll = get_collection_transactions()
    user_coll = get_collection_users()

    # try to convert to ObjectId for the expense query
    try:
        query_id = ObjectId(expense_id)
    except Exception:
        query_id = expense_id

    # find the expense first so we can update user's total_spent and user refs
    try:
        expense = exp_coll.find_one({"_id": query_id})
        if expense is None:
            # also try string-id form if we searched by ObjectId
            if isinstance(query_id, ObjectId):
                expense = exp_coll.find_one({"_id": expense_id})
                query_id = expense_id if expense is not None else query_id
        if expense is None:
            return False
    except Exception:
        return False

    # collect transaction ids associated with this expense (both forms)
    tx_ids = []
    if tx_coll is not None:
        try:
            cursor = tx_coll.find(
                {"$or": [{"expense_id": expense_id}, {"expense_id": query_id}]})
            for tx in cursor:
                tx_ids.append(tx.get("_id"))
        except Exception:
            tx_ids = []

    # delete the expense
    try:
        result = exp_coll.delete_one({"_id": query_id})
    except Exception:
        return False

    if result.deleted_count == 0:
        return False

    # delete associated transactions
    if tx_coll is not None:
        try:
            tx_coll.delete_many(
                {"$or": [{"expense_id": expense_id}, {"expense_id": query_id}]})
        except Exception:
            pass

    # update user: remove expense id from expenses_id, remove transaction ids from transactions_id,
    # and decrement total_spent by the expense amount if present
    if user_coll is not None:
        try:
            user_id_val = expense.get("user_id")
            if user_id_val is not None:
                # try to convert user id to ObjectId when possible
                try:
                    user_query_id = ObjectId(user_id_val) if isinstance(
                        user_id_val, str) and len(user_id_val) == 24 else user_id_val
                except Exception:
                    user_query_id = user_id_val

                update_ops = {}
                # remove expense id (both string and ObjectId forms)
                update_ops.setdefault("$pull", {})
                update_ops["$pull"].setdefault("expenses_id", None)
                # MongoDB $pull expects a value, but we can't pass two values at once; perform two pulls if needed
                try:
                    # pull string form
                    user_coll.update_one({"_id": user_query_id}, {
                                         "$pull": {"expenses_id": expense_id}})
                except Exception:
                    pass
                try:
                    # pull ObjectId form if applicable
                    if isinstance(query_id, ObjectId):
                        user_coll.update_one({"_id": user_query_id}, {
                                             "$pull": {"expenses_id": query_id}})
                except Exception:
                    pass

                # remove transaction ids from user's transactions_id
                if tx_ids:
                    try:
                        # pullAll with list of ObjectId or string ids as stored
                        # prepare lists for string and ObjectId forms
                        str_ids = [
                            str(tid) for tid in tx_ids if not isinstance(tid, ObjectId)]
                        obj_ids = [
                            tid for tid in tx_ids if isinstance(tid, ObjectId)]
                        if str_ids:
                            user_coll.update_one({"_id": user_query_id}, {
                                                 "$pullAll": {"transactions_id": str_ids}})
                        if obj_ids:
                            user_coll.update_one({"_id": user_query_id}, {
                                                 "$pullAll": {"transactions_id": obj_ids}})
                    except Exception:
                        pass

                # decrement total_spent if amount present and numeric
                try:
                    amt = expense.get("amount")
                    if isinstance(amt, (int, float)):
                        user_coll.update_one({"_id": user_query_id}, {
                                             "$inc": {"total_spent": -amt}})
                except Exception:
                    pass
        except Exception:
            pass

    return True


def delete_user(user_id: str) -> bool:
    # Delete a user from the database
    collection = get_collection_users()
    if collection is not None:
        result = collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
    return False


def get_all_transactions(user_id: str = None) -> list:
    """Get all transactions for a user"""
    collection = get_collection_transactions()
    if collection is not None:
        if user_id:
            try:
                query_id = ObjectId(user_id) if isinstance(
                    user_id, str) and len(user_id) == 24 else user_id
            except Exception:
                query_id = user_id
            return list(collection.find({"user_id": query_id}))
        return list(collection.find({}))
    return []


def get_spending_summary(user_id: str = None) -> dict:
    """Get spending summary for a user"""
    collection = get_collection_transactions()
    if collection is not None and user_id:
        try:
            query_id = ObjectId(user_id) if isinstance(
                user_id, str) and len(user_id) == 24 else user_id
        except Exception:
            query_id = user_id

        pipeline = [
            {"$match": {"user_id": query_id}},
            {"$group": {
                "_id": "$category",
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1}
            }}
        ]
        return {doc["_id"]: {"total": doc["total"], "count": doc["count"]}
                for doc in collection.aggregate(pipeline)}
    return {}


def get_categories(user_id: str = None) -> list:
    """Get distinct categories for a user"""
    collection = get_collection_transactions()
    if collection is not None:
        if user_id:
            try:
                query_id = ObjectId(user_id) if isinstance(
                    user_id, str) and len(user_id) == 24 else user_id
            except Exception:
                query_id = user_id
            categories = collection.distinct("category", {"user_id": query_id})
        else:
            categories = collection.distinct("category")
        return [{"name": cat} for cat in categories if cat]
    return []


def close_db() -> None:
    # Close the database connection
    db = get_db()
    if db is not None:
        db.client.close()
        print("Database connection closed.")
