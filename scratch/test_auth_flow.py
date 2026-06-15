import sys
import os

# Add root folder to path so modules can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from modules.auth_db import create_user, authenticate_user, user_exists, reset_user_password, init_db
import sqlite3

def run_test():
    init_db()
    email = "test_reset_user@example.com"
    name = "Test Reset User"
    old_pw = "old_secret_123"
    new_pw = "new_secret_456"

    print("--- Starting Auth Flow Database Test ---")

    # 1. Clean up user if they already exist
    conn = sqlite3.connect("data/users.db")
    conn.execute("DELETE FROM users WHERE email = ?", (email,))
    conn.commit()
    conn.close()

    # 2. Verify user doesn't exist
    assert not user_exists(email), "User should not exist initially"
    print("[OK] Initial user check passed")

    # 3. Create user
    success, msg = create_user(email, name, old_pw)
    assert success, f"Failed to create user: {msg}"
    print("[OK] User creation passed")

    # 4. Verify user exists
    assert user_exists(email), "User should exist now"
    print("[OK] User existence verification passed")

    # 5. Authenticate with old password
    success, user, msg = authenticate_user(email, old_pw)
    assert success, f"Failed to authenticate with old password: {msg}"
    assert user["name"] == name, "Authenticated user name mismatch"
    print("[OK] Old password authentication passed")

    # 6. Reset password
    success, msg = reset_user_password(email, new_pw)
    assert success, f"Failed to reset password: {msg}"
    print("[OK] Password reset query passed")

    # 7. Authenticate with old password (should fail)
    success, user, msg = authenticate_user(email, old_pw)
    assert not success, "Authentication with old password should have failed"
    print("[OK] Old password rejection after reset passed")

    # 8. Authenticate with new password (should succeed)
    success, user, msg = authenticate_user(email, new_pw)
    assert success, f"Failed to authenticate with new password: {msg}"
    assert user["name"] == name, "Authenticated user name mismatch"
    print("[OK] New password authentication passed")

    # 9. Clean up
    conn = sqlite3.connect("data/users.db")
    conn.execute("DELETE FROM users WHERE email = ?", (email,))
    conn.commit()
    conn.close()
    print("[OK] Cleanup completed successfully")

    print("\nALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_test()
