import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add root folder to path so modules can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from modules.auth_db import (
    create_user,
    authenticate_user,
    user_exists,
    reset_user_password,
    add_history_record,
    update_history_quiz,
    get_user_history,
    delete_history_record,
    init_db,
    _get_db
)
from bson import ObjectId

def run_test():
    print("--- Starting MongoDB Integration Test ---")
    
    try:
        # Check if MongoDB is running by attempting to get DB
        db = _get_db()
        db.command("ping")
        print("[OK] MongoDB connection verified (Ping successful)")
    except Exception as e:
        print(f"[ERROR] Could not connect to MongoDB at {os.getenv('MONGO_URI', 'mongodb://localhost:27017/')}.")
        print("Please make sure MongoDB is running locally on port 27017.")
        print(f"Details: {e}")
        sys.exit(1)

    init_db()
    
    email = "test_mongo_user@example.com"
    name = "Test Mongo User"
    old_pw = "old_mongo_pw_123"
    new_pw = "new_mongo_pw_456"

    # 1. Clean up user if they already exist
    db.users.delete_many({"email": email})
    print("[OK] Pre-test database clean-up done")

    # 2. Check user doesn't exist
    assert not user_exists(email), "User should not exist initially"
    print("[OK] Initial user_exists check passed")

    # 3. Create user
    success, msg = create_user(email, name, old_pw)
    assert success, f"Failed to create user: {msg}"
    print("[OK] User creation passed")

    # 4. Check duplicate registration fails
    success, msg = create_user(email, "Another Name", old_pw)
    assert not success, "Duplicate registration should have failed"
    assert "exists" in msg.lower(), f"Unexpected message: {msg}"
    print("[OK] Duplicate user registration prevention passed")

    # 5. Authenticate user
    success, user, msg = authenticate_user(email, old_pw)
    assert success, f"Failed to authenticate: {msg}"
    assert user["name"] == name, "Authenticated user name mismatch"
    assert "id" in user, "User dictionary should contain string id"
    user_id = user["id"]
    print(f"[OK] Authentication passed (User ID: {user_id})")

    # 6. Reset password
    success, msg = reset_user_password(email, new_pw)
    assert success, f"Failed to reset password: {msg}"
    print("[OK] Password reset passed")

    # 7. Authenticate with old password (should fail)
    success, user, msg = authenticate_user(email, old_pw)
    assert not success, "Authentication with old password should have failed after reset"
    print("[OK] Rejection of old password after reset passed")

    # 8. Authenticate with new password (should succeed)
    success, user, msg = authenticate_user(email, new_pw)
    assert success, f"Failed to authenticate with new password: {msg}"
    print("[OK] Authentication with new password passed")

    # 9. Test Study Session History & Document Storage
    print("\n--- Testing Study Session & Document Storage ---")
    title = "Test PDF Document"
    summary = "This is a mockup summary of the document contents."
    topics = ["Topic A", "Topic B", "Topic C"]
    cleaned_text = "This is the raw extracted text of the test PDF document saved in MongoDB."

    # Cleanup history records for this user
    db.history.delete_many({"user_id": user_id})

    history_id = add_history_record(
        user_id=user_id,
        title=title,
        summary=summary,
        topics=topics,
        cleaned_text=cleaned_text
    )
    assert history_id is not None, "Failed to add study history record"
    print(f"[OK] Study history record created (ID: {history_id})")

    # Verify history is saved and cleaned_text is stored
    history_list = get_user_history(user_id)
    assert len(history_list) == 1, f"Expected 1 history record, got {len(history_list)}"
    record = history_list[0]
    assert record["id"] == history_id, "History ID mismatch"
    assert record["title"] == title, "Title mismatch"
    assert record["summary"] == summary, "Summary mismatch"
    assert record["topics"] == topics, "Topics list mismatch"
    
    # Query MongoDB directly to check raw document storage
    stored_doc = db.history.find_one({"_id": ObjectId(history_id)})
    assert stored_doc is not None
    assert stored_doc.get("cleaned_text") == cleaned_text, "Raw document storage (cleaned_text) mismatch"
    print("[OK] Study history retrieval and raw document storage verified")

    # 10. Update study record with quiz results
    quiz_questions = [
        {"question": "Q1", "options": ["A", "B"], "correct": "A", "explanation": "Exp1"},
        {"question": "Q2", "options": ["C", "D"], "correct": "D", "explanation": "Exp2"}
    ]
    user_answers = ["A", "C"]
    score_percentage = 50.0
    correct_count = 1
    total_questions = 2

    success = update_history_quiz(
        history_id=history_id,
        quiz_questions=quiz_questions,
        user_answers=user_answers,
        score_percentage=score_percentage,
        correct_count=correct_count,
        total_questions=total_questions
    )
    assert success, "Failed to update history record with quiz details"
    print("[OK] History record updated with quiz results")

    # Verify updated values
    history_list = get_user_history(user_id)
    record = history_list[0]
    assert record["quiz_questions"] == quiz_questions, "Quiz questions mismatch"
    assert record["user_answers"] == user_answers, "User answers mismatch"
    assert record["score_percentage"] == score_percentage, "Score percentage mismatch"
    assert record["correct_count"] == correct_count, "Correct count mismatch"
    assert record["total_questions"] == total_questions, "Total questions mismatch"
    print("[OK] Quiz results verification passed")

    # 11. Delete history record
    success = delete_history_record(history_id, user_id)
    assert success, "Failed to delete history record"
    
    history_list = get_user_history(user_id)
    assert len(history_list) == 0, "History record was not deleted"
    print("[OK] History record deletion verified")

    # 12. Cleanup database test user
    db.users.delete_many({"email": email})
    print("[OK] Cleanup database test user completed")

    print("\nALL MONGO TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_test()
