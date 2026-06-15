import sys
import os

# Add root folder to path so modules can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from modules.auth_db import (
    create_user,
    user_exists,
    authenticate_user,
    create_user_session,
    verify_user_session,
    delete_user_session,
    init_db,
    _get_db
)

def run_test():
    init_db()
    db = _get_db()
    email = "test_session_user@example.com"
    name = "Test Session User"
    password = "secret_password_123"

    print("--- Starting Auth Session Database Test ---")

    # 1. Clean up user if they already exist
    db.users.delete_many({"email": email})
    print("[OK] Initial user cleanup completed")

    # 2. Create user
    success, msg = create_user(email, name, password)
    assert success, f"Failed to create user: {msg}"
    print("[OK] User creation passed")

    # 3. Authenticate to get user document info
    success, user, msg = authenticate_user(email, password)
    assert success, f"Failed to authenticate user: {msg}"
    user_id = user["id"]
    print(f"[OK] Authentication passed, user ID: {user_id}")

    # 4. Verify no session exists initially
    # Note: fresh user doesn't have session_token or it is unset
    user_doc = db.users.find_one({"email": email})
    assert "session_token" not in user_doc or user_doc["session_token"] is None, "Should not have session token initially"
    print("[OK] Initial empty session check passed")

    # 5. Create user session
    token = create_user_session(user_id)
    assert token is not None, "Failed to create session token"
    print(f"[OK] Session token created: {token}")

    # 6. Verify user session
    verified_user = verify_user_session(token)
    assert verified_user is not None, "Failed to verify session token"
    assert verified_user["email"] == email, "Verified session email mismatch"
    assert verified_user["id"] == user_id, "Verified session ID mismatch"
    print("[OK] Session token verification passed")

    # 7. Invalidate user session (logout)
    delete_user_session(user_id)
    print("[OK] Session token delete requested")

    # 8. Verify session token is no longer valid
    verified_user_after = verify_user_session(token)
    assert verified_user_after is None, "Session token should be invalid after delete"
    print("[OK] Session token invalidation verification passed")

    # 9. Clean up test user
    db.users.delete_many({"email": email})
    print("[OK] Test user cleanup passed")

    print("\nALL SESSION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_test()
