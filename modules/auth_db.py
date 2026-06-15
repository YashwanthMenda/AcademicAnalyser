"""
MongoDB user storage and document storage database module.
"""

import os
from datetime import datetime
import bcrypt
from pymongo import MongoClient
from bson import ObjectId

_client = None

def _get_db():
    global _client
    if _client is None:
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        _client = MongoClient(mongo_uri)
    db_name = os.getenv("MONGO_DB_NAME", "academic_analyser")
    return _client[db_name]


def init_db():
    """Initialize MongoDB indexes."""
    try:
        db = _get_db()
        # Create unique index on email
        db.users.create_index("email", unique=True)
        # Create unique index on google_id if it exists
        db.users.create_index("google_id", unique=True, sparse=True)
    except Exception as e:
        print(f"Error initializing MongoDB: {e}")


def _hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password, password_hash):
    if not password_hash:
        return False
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_user(email, name, password):
    """Register a new local user in MongoDB."""
    init_db()
    email_clean = email.lower().strip()
    password_hash = _hash_password(password)

    try:
        db = _get_db()
        db.users.insert_one({
            "email": email_clean,
            "name": name.strip(),
            "password_hash": password_hash,
            "auth_provider": "local",
            "created_at": datetime.utcnow().isoformat()
        })
        return True, "Account created successfully."
    except Exception as e:
        if "duplicate key" in str(e) or "E11000" in str(e):
            return False, "An account with this email already exists."
        return False, f"Failed to create account: {e}"


def authenticate_user(email, password):
    """Authenticate a local user in MongoDB."""
    init_db()
    db = _get_db()
    
    user_doc = db.users.find_one({"email": email.lower().strip()})
    if not user_doc:
        return False, None, "Invalid email or password."

    if user_doc.get("auth_provider") == "google" and not user_doc.get("password_hash"):
        return False, None, "This account uses Google Sign-In."

    if not _verify_password(password, user_doc.get("password_hash")):
        return False, None, "Invalid email or password."

    user = {
        "id": str(user_doc["_id"]),
        "email": user_doc["email"],
        "name": user_doc["name"],
        "auth_provider": user_doc["auth_provider"],
    }
    return True, user, "Login successful."


def get_or_create_google_user(email, name, google_id):
    """Create or fetch a Google-authenticated user in MongoDB."""
    init_db()
    db = _get_db()
    email_clean = email.lower().strip()

    # Find if user already exists by email or google_id
    user_doc = db.users.find_one({"$or": [{"email": email_clean}, {"google_id": google_id}]})

    if user_doc:
        db.users.update_one(
            {"_id": user_doc["_id"]},
            {"$set": {
                "google_id": google_id,
                "auth_provider": "google",
                "name": name.strip()
            }}
        )
        return {
            "id": str(user_doc["_id"]),
            "email": email_clean,
            "name": name.strip(),
            "auth_provider": "google",
        }

    # Otherwise create new user doc
    result = db.users.insert_one({
        "email": email_clean,
        "name": name.strip(),
        "google_id": google_id,
        "auth_provider": "google",
        "created_at": datetime.utcnow().isoformat()
    })
    
    return {
        "id": str(result.inserted_id),
        "email": email_clean,
        "name": name.strip(),
        "auth_provider": "google",
    }


def add_history_record(user_id, title, summary, topics, cleaned_text=None):
    """Create a new history record with summary, topics, and raw cleaned text in MongoDB."""
    init_db()
    try:
        db = _get_db()
        record = {
            "user_id": user_id,
            "title": title,
            "summary": summary,
            "topics": topics,
            "cleaned_text": cleaned_text,
            "quiz_questions": None,
            "user_answers": None,
            "score_percentage": None,
            "correct_count": None,
            "total_questions": None,
            "created_at": datetime.utcnow().isoformat()
        }
        result = db.history.insert_one(record)
        return str(result.inserted_id)
    except Exception as e:
        print(f"Error adding history record: {e}")
        return None


def update_history_quiz(history_id, quiz_questions, user_answers, score_percentage, correct_count, total_questions):
    """Update history record with quiz results in MongoDB."""
    try:
        db = _get_db()
        db.history.update_one(
            {"_id": ObjectId(history_id)},
            {"$set": {
                "quiz_questions": quiz_questions,
                "user_answers": user_answers,
                "score_percentage": score_percentage,
                "correct_count": correct_count,
                "total_questions": total_questions
            }}
        )
        return True
    except Exception as e:
        print(f"Error updating history quiz: {e}")
        return False


def get_user_history(user_id):
    """Retrieve all history records for a user from MongoDB, sorted by date in descending order."""
    init_db()
    try:
        db = _get_db()
        cursor = db.history.find({"user_id": user_id}).sort("created_at", -1)
        history_list = []
        for doc in cursor:
            history_list.append({
                "id": str(doc["_id"]),
                "user_id": doc["user_id"],
                "title": doc["title"],
                "summary": doc.get("summary"),
                "topics": doc.get("topics") or [],
                "quiz_questions": doc.get("quiz_questions"),
                "user_answers": doc.get("user_answers"),
                "score_percentage": doc.get("score_percentage"),
                "correct_count": doc.get("correct_count"),
                "total_questions": doc.get("total_questions"),
                "created_at": doc.get("created_at")
            })
        return history_list
    except Exception as e:
        print(f"Error getting user history: {e}")
        return []


def delete_history_record(history_id, user_id):
    """Delete a specific history record from MongoDB."""
    try:
        db = _get_db()
        db.history.delete_one({"_id": ObjectId(history_id), "user_id": user_id})
        return True
    except Exception as e:
        print(f"Error deleting history: {e}")
        return False


def reset_user_password(email, new_password):
    """Reset the password of a local user by email in MongoDB."""
    init_db()
    password_hash = _hash_password(new_password)
    try:
        db = _get_db()
        email_clean = email.lower().strip()
        user_doc = db.users.find_one({"email": email_clean})
        if not user_doc:
            return False, "No account with this email address exists."
        if user_doc.get("auth_provider") == "google" and not user_doc.get("password_hash"):
            return False, "This account is registered via Google OAuth and does not use a password."
        
        db.users.update_one(
            {"_id": user_doc["_id"]},
            {"$set": {"password_hash": password_hash}}
        )
        return True, "Password reset successfully!"
    except Exception as e:
        return False, f"Database error: {e}"


def user_exists(email):
    """Check if a user with the given email exists in MongoDB."""
    init_db()
    try:
        db = _get_db()
        count = db.users.count_documents({"email": email.lower().strip()})
        return count > 0
    except Exception:
        return False


def create_user_session(user_id):
    """Generate and store a session token for the user."""
    import uuid
    from datetime import timedelta
    try:
        db = _get_db()
        session_token = uuid.uuid4().hex
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "session_token": session_token,
                "session_expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
            }}
        )
        return session_token
    except Exception as e:
        print(f"Error creating user session: {e}")
        return None


def verify_user_session(session_token):
    """Verify a session token and return the associated user details."""
    try:
        db = _get_db()
        user_doc = db.users.find_one({"session_token": session_token})
        if not user_doc:
            return None
            
        expires_at_str = user_doc.get("session_expires_at")
        if expires_at_str:
            expires_at = datetime.fromisoformat(expires_at_str)
            if datetime.utcnow() > expires_at:
                # Expired session
                db.users.update_one(
                    {"_id": user_doc["_id"]},
                    {"$unset": {"session_token": "", "session_expires_at": ""}}
                )
                return None
                
        return {
            "id": str(user_doc["_id"]),
            "email": user_doc["email"],
            "name": user_doc["name"],
            "auth_provider": user_doc.get("auth_provider", "local"),
        }
    except Exception as e:
        print(f"Error verifying user session: {e}")
        return None


def delete_user_session(user_id):
    """Delete the session token for a user (on logout)."""
    try:
        db = _get_db()
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$unset": {"session_token": "", "session_expires_at": ""}}
        )
        return True
    except Exception as e:
        print(f"Error deleting user session: {e}")
        return False
