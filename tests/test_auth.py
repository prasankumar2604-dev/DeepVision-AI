"""
====================================================
DeepVision AI — Comprehensive Security & Auth Tests
Direct Authentication & Forensic Model Test Suite
====================================================
"""

import os
import sys
import unittest
import tempfile

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import Security & Auth modules
from auth_utils import (
    validate_password_strength,
    validate_email_syntax,
    normalize_email,
    hash_password,
    verify_and_update_password,
    generate_reset_token,
    hash_reset_token,
    generate_csrf_token,
    validate_csrf_token,
)
from database import create_database, get_connection
import app as app_module
from app import app


class DeepVisionSecurityUnitTests(unittest.TestCase):
    """Unit tests for cryptographic functions, password policy, and email validation."""

    def test_strong_password_validation(self):
        # 1. Too short (< 12 chars)
        ok, errs = validate_password_strength("Short1!Aa")
        self.assertFalse(ok)
        self.assertTrue(any("12 characters" in e for e in errs))

        # 2. Missing uppercase
        ok, errs = validate_password_strength("alllowercase123!@#")
        self.assertFalse(ok)
        self.assertTrue(any("uppercase" in e for e in errs))

        # 3. Missing lowercase
        ok, errs = validate_password_strength("ALLUPPERCASE123!@#")
        self.assertFalse(ok)
        self.assertTrue(any("lowercase" in e for e in errs))

        # 4. Missing number
        ok, errs = validate_password_strength("NoNumbersHere!@#$Aa")
        self.assertFalse(ok)
        self.assertTrue(any("number" in e for e in errs))

        # 5. Missing special character
        ok, errs = validate_password_strength("NoSpecialSymbols1234Aa")
        self.assertFalse(ok)
        self.assertTrue(any("special" in e for e in errs))

        # 6. Meets all security criteria (minimum 12 chars, upper, lower, number, symbol)
        ok, errs = validate_password_strength("ComplexGold#2026Secure")
        self.assertTrue(ok)
        self.assertEqual(len(errs), 0)

    def test_email_syntax_and_normalization(self):
        # Normalization
        self.assertEqual(normalize_email("  User.Test@Example.COM  "), "user.test@example.com")

        # Valid syntax
        ok, norm, err = validate_email_syntax("forensics.analyst@deepvision.ai")
        self.assertTrue(ok)
        self.assertEqual(norm, "forensics.analyst@deepvision.ai")

        # Malformed emails
        bad_emails = [
            "missingatdomain.com",
            "@missinglocal.com",
            "missingdomain@",
            "user with spaces@domain.com",
            "",
            None,
        ]
        for bad in bad_emails:
            ok, _, err = validate_email_syntax(bad)
            self.assertFalse(ok, f"Expected {bad} to fail validation")
            self.assertTrue(len(err) > 0)

    def test_legacy_password_verification_and_upgrade(self):
        # Plaintext backward compatibility
        plain = "Prasan@2001"
        is_valid, needs_rehash = verify_and_update_password(plain, plain)
        self.assertTrue(is_valid)
        self.assertTrue(needs_rehash)

        # Modern hashed password
        hashed = hash_password(plain)
        is_valid2, needs_rehash2 = verify_and_update_password(hashed, plain)
        self.assertTrue(is_valid2)
        self.assertFalse(needs_rehash2)

        # Incorrect password
        is_valid3, _ = verify_and_update_password(hashed, "WrongPassword#123")
        self.assertFalse(is_valid3)

    def test_csrf_token_validation(self):
        token = generate_csrf_token()
        self.assertEqual(len(token), 64)
        self.assertTrue(validate_csrf_token(token, token))
        self.assertFalse(validate_csrf_token(token, "invalid_csrf_token"))
        self.assertFalse(validate_csrf_token("", token))


class DeepVisionIntegrationFlowTests(unittest.TestCase):
    """End-to-end integration tests using an isolated test SQLite database."""

    def setUp(self):
        # Create temporary isolated test database
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.db_fd)

        # Re-point application to test database
        app.config["TESTING"] = True
        app.config["DATABASE_PATH"] = self.db_path
        app_module.DATABASE = self.db_path
        create_database(self.db_path)

        self.client = app.test_client()

    def tearDown(self):
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass

    def _get_csrf_token(self):
        """Helper to obtain a valid CSRF token from the session via GET request."""
        self.client.get("/")
        with self.client.session_transaction() as sess:
            if "_csrf_token" not in sess:
                sess["_csrf_token"] = generate_csrf_token()
            return sess["_csrf_token"]

    def test_unauthorized_routes_redirect_to_login(self):
        protected_routes = ["/dashboard", "/detect", "/history", "/change-password"]
        for route in protected_routes:
            res = self.client.get(route, follow_redirects=False)
            self.assertEqual(res.status_code, 302)
            self.assertTrue("/login" in res.headers["Location"])

    def test_direct_signup_and_direct_login_flow(self):
        csrf = self._get_csrf_token()

        # 1. Weak password rejected
        res = self.client.post("/signup", data={
            "csrf_token": csrf,
            "username": "tester",
            "email": "test@example.com",
            "password": "weak",
            "confirm_password": "weak",
        }, follow_redirects=True)
        self.assertIn(b"Password requirement failed", res.data)

        # 2. Malformed email rejected
        res = self.client.post("/signup", data={
            "csrf_token": csrf,
            "username": "tester",
            "email": "not-an-email",
            "password": "ValidPassword#2026",
            "confirm_password": "ValidPassword#2026",
        }, follow_redirects=True)
        self.assertIn(b"Invalid email format", res.data)

        # 3. Direct valid signup (no OTP required)
        res = self.client.post("/signup", data={
            "csrf_token": csrf,
            "username": "DirectUser",
            "email": "direct.user@deepvision.ai",
            "password": "StrongPassword#2026",
            "confirm_password": "StrongPassword#2026",
        }, follow_redirects=False)

        # Redirects straight to login
        self.assertEqual(res.status_code, 302)
        self.assertTrue("/login" in res.headers["Location"])

        # Verify user is immediately active in database
        conn = get_connection(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = 'direct.user@deepvision.ai'")
        user = c.fetchone()
        self.assertIsNotNone(user, "User should be created directly in database")
        self.assertEqual(user["is_verified"], 1)
        self.assertEqual(user["username"], "DirectUser")
        conn.close()

        # 4. Direct login with correct email and password (no 2FA / OTP step)
        res = self.client.post("/login", data={
            "csrf_token": csrf,
            "email": "direct.user@deepvision.ai",
            "password": "StrongPassword#2026",
        }, follow_redirects=False)

        # Grants access directly to dashboard
        self.assertEqual(res.status_code, 302)
        self.assertTrue("/dashboard" in res.headers["Location"])

        # Verify session state
        with self.client.session_transaction() as sess:
            self.assertIn("user_id", sess)
            self.assertEqual(sess["username"], "DirectUser")

        # Authenticated user can immediately access dashboard
        res = self.client.get("/dashboard")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"DirectUser", res.data)

    def test_brute_force_lockout_after_five_failed_logins(self):
        csrf = self._get_csrf_token()

        conn = get_connection(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (username, email, password, is_verified) VALUES (?, ?, ?, 1)",
            ("LockoutUser", "lockout@deepvision.ai", hash_password("ValidPassword#2026"))
        )
        conn.commit()
        conn.close()

        # Submit 5 incorrect password attempts
        for i in range(5):
            self.client.post("/login", data={
                "csrf_token": csrf,
                "email": "lockout@deepvision.ai",
                "password": f"WrongAttempt{i}!123",
            }, follow_redirects=True)

        # Verify user is now locked out
        conn = get_connection(self.db_path)
        c = conn.cursor()
        c.execute("SELECT locked_until, failed_login_attempts FROM users WHERE email = 'lockout@deepvision.ai'")
        user = c.fetchone()
        self.assertIsNotNone(user["locked_until"])
        self.assertGreaterEqual(user["failed_login_attempts"], 5)
        conn.close()

        # 6th attempt even with correct password is blocked due to lockout
        res = self.client.post("/login", data={
            "csrf_token": csrf,
            "email": "lockout@deepvision.ai",
            "password": "ValidPassword#2026",
        }, follow_redirects=True)
        self.assertIn(b"Account temporarily locked", res.data)

    def test_forgot_and_reset_password_flow(self):
        csrf = self._get_csrf_token()

        conn = get_connection(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (username, email, password, is_verified) VALUES (?, ?, ?, 1)",
            ("ResetUser", "reset@deepvision.ai", hash_password("OldPassword#2026"))
        )
        user_id = c.lastrowid
        conn.commit()
        conn.close()

        # 1. Request password reset
        res = self.client.post("/forgot-password", data={
            "csrf_token": csrf,
            "email": "reset@deepvision.ai",
        }, follow_redirects=True)
        self.assertIn(b"password reset instructions have been dispatched", res.data)

        # 2. Check token in database
        conn = get_connection(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM password_resets WHERE user_id = ? AND used_at IS NULL", (user_id,))
        reset_rec = c.fetchone()
        self.assertIsNotNone(reset_rec)

        # Create known raw token and update token hash
        known_token = "secure-random-test-token-123"
        c.execute("UPDATE password_resets SET token_hash = ? WHERE id = ?", (hash_reset_token(known_token), reset_rec["id"]))
        conn.commit()
        conn.close()

        # 3. Access reset password page
        res = self.client.get(f"/reset-password?token={known_token}")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Set New", res.data)

        # 4. Submit new password
        res = self.client.post("/reset-password", data={
            "csrf_token": csrf,
            "token": known_token,
            "new_password": "BrandNewPassword#2026",
            "confirm_password": "BrandNewPassword#2026",
        }, follow_redirects=False)

        self.assertEqual(res.status_code, 302)
        self.assertTrue("/login" in res.headers["Location"])

        # 5. Token is now marked used
        conn = get_connection(self.db_path)
        c = conn.cursor()
        c.execute("SELECT used_at FROM password_resets WHERE id = ?", (reset_rec["id"],))
        self.assertIsNotNone(c.fetchone()["used_at"])

        # 6. Reusing the token fails
        res = self.client.get(f"/reset-password?token={known_token}", follow_redirects=True)
        self.assertIn(b"Password reset link is invalid or has already been used", res.data)
        conn.close()

    def test_authenticated_change_password_flow(self):
        csrf = self._get_csrf_token()

        conn = get_connection(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (username, email, password, is_verified) VALUES (?, ?, ?, 1)",
            ("PassChangeUser", "change@deepvision.ai", hash_password("CurrentPassword#2026"))
        )
        user_id = c.lastrowid
        conn.commit()
        conn.close()

        # Simulate authenticated session
        with self.client.session_transaction() as sess:
            sess["user_id"] = user_id
            sess["username"] = "PassChangeUser"
            sess["_csrf_token"] = csrf

        # 1. Invalid current password fails
        res = self.client.post("/change-password", data={
            "csrf_token": csrf,
            "current_password": "WrongPassword#2026",
            "new_password": "NewStrongPassword#2026",
            "confirm_password": "NewStrongPassword#2026",
        }, follow_redirects=True)
        self.assertIn(b"Current password entered is incorrect", res.data)

        # 2. Valid password change succeeds
        res = self.client.post("/change-password", data={
            "csrf_token": csrf,
            "current_password": "CurrentPassword#2026",
            "new_password": "NewStrongPassword#2026",
            "confirm_password": "NewStrongPassword#2026",
        }, follow_redirects=False)

        self.assertEqual(res.status_code, 302)
        self.assertTrue("/dashboard" in res.headers["Location"])

    def test_model_prediction_and_history_workflow(self):
        csrf = self._get_csrf_token()

        conn = get_connection(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (username, email, password, is_verified) VALUES (?, ?, ?, 1)",
            ("PredictUser", "predict.user@deepvision.ai", hash_password("Password#2026Deep"))
        )
        user_id = c.lastrowid
        conn.commit()
        conn.close()

        # Authenticate session
        with self.client.session_transaction() as sess:
            sess["user_id"] = user_id
            sess["username"] = "PredictUser"
            sess["_csrf_token"] = csrf

        # Upload a real sample image from static/uploads/00004.jpg
        sample_img_path = os.path.join(os.path.dirname(__file__), "..", "static", "uploads", "00004.jpg")
        self.assertTrue(os.path.exists(sample_img_path), "Sample test image must exist")

        with open(sample_img_path, "rb") as img_file:
            res = self.client.post("/predict", data={
                "csrf_token": csrf,
                "image": (img_file, "00004_test.jpg"),
            }, content_type="multipart/form-data")

        self.assertEqual(res.status_code, 200)
        self.assertTrue(b"Authentic Image (Real)" in res.data or b"Deepfake Detected" in res.data)
        self.assertIn(b"Confidence Score", res.data)

        # Verify entry was saved to predictions table in database
        conn = get_connection(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM predictions WHERE user_id = ?", (user_id,))
        pred_record = c.fetchone()
        self.assertIsNotNone(pred_record, "Prediction should be persisted to predictions table")
        self.assertIn(pred_record["prediction"], ["Real", "Fake"])
        self.assertGreater(pred_record["confidence"], 0)
        conn.close()

        # Check /history route
        history_res = self.client.get("/history")
        self.assertEqual(history_res.status_code, 200)
        self.assertIn(b"00004_test.jpg", history_res.data)


if __name__ == "__main__":
    unittest.main()
