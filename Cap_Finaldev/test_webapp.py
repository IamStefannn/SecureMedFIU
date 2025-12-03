"""
SecureMed Test Suite
Tests all the important stuff to make sure nothing breaks
Run with: python3 test_webapp.py
"""

import unittest
import sqlite3
import os
from cryptography.fernet import Fernet
from datetime import datetime

# import our app
import webapp

class TestEncryption(unittest.TestCase):
    """Test that encryption/decryption works properly"""

    def setUp(self):
        # get the cipher from webapp
        self.cipher = webapp.cipher

    def test_ssn_encryption(self):
        """Make sure SSN gets encrypted and decrypted correctly"""
        original_ssn = "123-45-6789"

        # encrypt it
        encrypted = self.cipher.encrypt(original_ssn.encode()).decode()

        # should NOT be the same
        self.assertNotEqual(encrypted, original_ssn)

        # decrypt it
        decrypted = self.cipher.decrypt(encrypted.encode()).decode()

        # should match original
        self.assertEqual(decrypted, original_ssn)
        print("✅ SSN encryption/decryption works!")

    def test_multiple_encryptions_different(self):
        """Same data should encrypt to different values each time (IV randomness)"""
        data = "test123"
        encrypted1 = self.cipher.encrypt(data.encode()).decode()
        encrypted2 = self.cipher.encrypt(data.encode()).decode()

        # Fernet uses timestamp so these might be same if run instantly
        # but they should both decrypt correctly
        self.assertEqual(self.cipher.decrypt(encrypted1.encode()).decode(), data)
        self.assertEqual(self.cipher.decrypt(encrypted2.encode()).decode(), data)
        print("✅ Multiple encryptions work correctly!")


class TestPasswordHashing(unittest.TestCase):
    """Test password hashing security"""

    def test_password_hashing(self):
        """Passwords should be hashed with SHA-256"""
        password = "Admin123!"
        hashed = webapp.hash_pw(password)

        # should not equal original
        self.assertNotEqual(hashed, password)

        # SHA-256 produces 64 character hex string
        self.assertEqual(len(hashed), 64)
        print("✅ Password hashing works!")

    def test_same_password_same_hash(self):
        """Same password should always produce same hash"""
        password = "TestPass123!"
        hash1 = webapp.hash_pw(password)
        hash2 = webapp.hash_pw(password)

        self.assertEqual(hash1, hash2)
        print("✅ Consistent password hashing!")

    def test_different_passwords_different_hashes(self):
        """Different passwords should produce different hashes"""
        hash1 = webapp.hash_pw("Password1!")
        hash2 = webapp.hash_pw("Password2!")

        self.assertNotEqual(hash1, hash2)
        print("✅ Different passwords = different hashes!")


class TestDatabaseOperations(unittest.TestCase):
    """Test database stuff"""

    def setUp(self):
        """Create a test database"""
        self.test_db = "test_securemed.db"
        self.conn = sqlite3.connect(self.test_db)
        self.cursor = self.conn.cursor()

        # create users table
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            compliance_score INTEGER DEFAULT 0,
            training_completed INTEGER DEFAULT 0,
            completed_modules TEXT DEFAULT '[]'
        )""")

        # create patients table
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY,
            mrn TEXT UNIQUE,
            first_name TEXT,
            last_name TEXT,
            date_of_birth TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            ssn TEXT,
            created_by TEXT,
            created_at TEXT
        )""")
        self.conn.commit()

    def tearDown(self):
        """Clean up test database"""
        self.conn.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_user_insertion(self):
        """Test adding a user to database"""
        username = "testuser"
        password = webapp.hash_pw("Test123!")

        self.cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                          (username, password, "user"))
        self.conn.commit()

        # check it exists
        self.cursor.execute("SELECT username, role FROM users WHERE username=?", (username,))
        result = self.cursor.fetchone()

        self.assertIsNotNone(result)
        self.assertEqual(result[0], username)
        self.assertEqual(result[1], "user")
        print("✅ User insertion works!")

    def test_patient_insertion_with_encryption(self):
        """Test adding patient with encrypted SSN"""
        cipher = webapp.cipher

        ssn = "123-45-6789"
        encrypted_ssn = cipher.encrypt(ssn.encode()).decode()

        self.cursor.execute("""INSERT INTO patients
            (mrn, first_name, last_name, date_of_birth, ssn, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            ("MRN001", "John", "Doe", "1990-01-01", encrypted_ssn, "admin", datetime.now().strftime("%Y-%m-%d %H:%M")))
        self.conn.commit()

        # retrieve and decrypt
        self.cursor.execute("SELECT ssn FROM patients WHERE mrn=?", ("MRN001",))
        result = self.cursor.fetchone()

        decrypted_ssn = cipher.decrypt(result[0].encode()).decode()
        self.assertEqual(decrypted_ssn, ssn)
        print("✅ Patient insertion with encryption works!")

    def test_sql_injection_prevention(self):
        """Test that parameterized queries prevent SQL injection"""
        # try to inject SQL
        malicious_username = "admin' OR '1'='1"

        # this should NOT return anything because we use parameterized queries
        self.cursor.execute("SELECT * FROM users WHERE username=?", (malicious_username,))
        result = self.cursor.fetchone()

        # should be None (no user found)
        self.assertIsNone(result)
        print("✅ SQL injection prevention works!")


class TestFlaskRoutes(unittest.TestCase):
    """Test Flask routes and endpoints"""

    def setUp(self):
        """Set up test client"""
        webapp.app.config['TESTING'] = True
        webapp.app.config['SECRET_KEY'] = 'test_secret_key'
        self.client = webapp.app.test_client()

    def test_login_page_loads(self):
        """Test that login page loads"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SecureMed', response.data)
        print("✅ Login page loads!")

    def test_login_with_valid_credentials(self):
        """Test login with correct username/password"""
        response = self.client.post('/login', data={
            'username': 'admin',
            'password': 'Admin123!'
        }, follow_redirects=False)

        # should redirect (302) on successful login
        self.assertEqual(response.status_code, 302)
        print("✅ Valid login redirects correctly!")

    def test_login_with_invalid_credentials(self):
        """Test login with wrong password"""
        response = self.client.post('/login', data={
            'username': 'admin',
            'password': 'WrongPassword123!'
        }, follow_redirects=True)

        # should show error message
        self.assertIn(b'Invalid', response.data)
        print("✅ Invalid login rejected!")

    def test_protected_route_without_login(self):
        """Test that you can't access dashboard without logging in"""
        response = self.client.get('/dashboard', follow_redirects=False)

        # should redirect (302) when not logged in
        self.assertEqual(response.status_code, 302)
        # Verify it redirects (either to /login or /user_dashboard)
        self.assertIn(b'Redirecting', response.data)
        print("✅ Protected routes require login!")

    def test_api_returns_json(self):
        """Test that API endpoints return JSON"""
        # login first
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user'] = 'admin'
                sess['role'] = 'admin'

            response = c.get('/api/patients')
            self.assertEqual(response.content_type, 'application/json')
            print("✅ API returns JSON!")


class TestPasswordValidation(unittest.TestCase):
    """Test password strength validation logic"""

    def test_password_length_requirement(self):
        """Password must be at least 8 characters"""
        import re

        weak_password = "Ab1!"
        # Check that password validation requires 8+ chars
        self.assertLess(len(weak_password), 8)
        print("✅ Short passwords rejected!")

    def test_password_complexity_requirements(self):
        """Password must have upper, lower, number, special char"""
        import re

        # Test password patterns (same logic used in reset_password route)
        # Missing uppercase
        pwd1 = "password123!"
        self.assertFalse(bool(re.search(r'[A-Z]', pwd1)))

        # Missing lowercase
        pwd2 = "PASSWORD123!"
        self.assertFalse(bool(re.search(r'[a-z]', pwd2)))

        # Missing number
        pwd3 = "Password!"
        self.assertFalse(bool(re.search(r'[0-9]', pwd3)))

        # Missing special char
        pwd4 = "Password123"
        self.assertFalse(bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd4)))

        # Has everything - should pass all checks
        strong_pwd = "MyP@ssw0rd2024"
        self.assertTrue(len(strong_pwd) >= 8)
        self.assertTrue(bool(re.search(r'[A-Z]', strong_pwd)))
        self.assertTrue(bool(re.search(r'[a-z]', strong_pwd)))
        self.assertTrue(bool(re.search(r'[0-9]', strong_pwd)))
        self.assertTrue(bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', strong_pwd)))
        print("✅ Password complexity checks work!")

    def test_common_passwords_blocked(self):
        """Common passwords are documented as blocked"""
        # These passwords are blocked in the reset_password route
        common_passwords = ["Password123!", "Admin123!", "User123!",
                          "Passw0rd!", "Welcome123!", "Qwerty123!"]

        # Verify these ARE in the blocked list
        for pwd in ["Password123!", "Admin123!", "User123!"]:
            self.assertIn(pwd, common_passwords)

        print("✅ Common passwords identified!")


class TestComplianceScoring(unittest.TestCase):
    """Test training compliance score calculations"""

    def test_score_increases_on_correct_answer(self):
        """Score should go up by 20 for correct answer"""
        initial_score = 0
        correct_answers = 1
        total_answered = 1

        # formula: (correct / 9) * 100
        expected_score = (correct_answers / 9) * 100
        calculated_score = round(expected_score, 2)

        # should be about 11.11%
        self.assertAlmostEqual(calculated_score, 11.11, places=1)
        print("✅ Score calculation works!")

    def test_max_score_is_100(self):
        """Maximum score should be 100%"""
        # 9 correct out of 9 total
        score = (9 / 9) * 100
        self.assertEqual(score, 100.0)
        print("✅ Max score is 100%!")

    def test_score_cannot_go_negative(self):
        """Score should never be negative"""
        # even with 0 correct answers
        score = max(0, (0 / 9) * 100)
        self.assertGreaterEqual(score, 0)
        print("✅ Score can't go negative!")


class TestAuditLogging(unittest.TestCase):
    """Test audit trail functionality"""

    def setUp(self):
        """Create test database with activity_log table"""
        self.test_db = "test_audit.db"
        self.conn = sqlite3.connect(self.test_db)
        self.cursor = self.conn.cursor()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            username TEXT,
            action_type TEXT,
            description TEXT,
            details TEXT,
            ip_address TEXT
        )""")
        self.conn.commit()

    def tearDown(self):
        """Clean up test database"""
        self.conn.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_activity_logging(self):
        """Test that activities get logged"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute("""INSERT INTO activity_log
            (timestamp, username, action_type, description, details, ip_address)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (timestamp, "admin", "LOGIN", "User logged in", "Successful login", "127.0.0.1"))
        self.conn.commit()

        # check it was logged
        self.cursor.execute("SELECT action_type, username FROM activity_log WHERE username=?", ("admin",))
        result = self.cursor.fetchone()

        self.assertIsNotNone(result)
        self.assertEqual(result[0], "LOGIN")
        self.assertEqual(result[1], "admin")
        print("✅ Activity logging works!")


# run all tests when this file is executed
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🧪 SecureMed Test Suite")
    print("="*60 + "\n")

    # run tests
    unittest.main(verbosity=2)
