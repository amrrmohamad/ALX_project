import unittest
import sqlite3
import os
from werkzeug.security import generate_password_hash
from ST_GitHub import app, init_db

class TestFlaskApp(unittest.TestCase):
    """
    A suite of test cases for the Flask application to ensure correct routing,
    user authentication, and database interactions.
    """

    def create_app(self):
        """
        Create a Flask application for testing.
        """
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret_key'
        # Use an in-memory database for testing
        app.config['DATABASE'] = ':memory:'
        return app

    def setUp(self):
        """Setup the database for testing."""
        self.app = self.create_app()
        self.client = self.app.test_client()
        
        # Initialize the in-memory database and create tables
        with self.app.app_context():
            init_db()

    def tearDown(self):
        """Clean up after each test."""
        # No need to remove the file if using in-memory database
        pass

    def test_home_redirects_to_login(self):
        """
        Test Case: Accessing the home page without being logged in.
        Expectation: Should redirect to the login page.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)  # 302 indicates a redirect
        self.assertEqual(response.location, '/login')

    # still has error
    def test_login_with_valid_credentials(self):
        """
        Test Case: Logging in with valid credentials.
        Expectation: Should redirect to the home page.
        """
        username = 'testuser'
        password = generate_password_hash('testpassword')
        email = 'test@example.com'
        
        with self.app.app_context():
            conn = sqlite3.connect(':memory:')
            conn.execute("CREATE TABLE users (username TEXT UNIQUE, password TEXT, email TEXT)")
            conn.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", 
                         (username, password, email))
            conn.commit()
        
        response = self.client.post('/login', data={
            'username': username,
            'password': 'testpassword',
        })
        self.assertEqual(response.status_code, 302)  # Redirects to home page

    def test_login_with_invalid_credentials(self):
        """
        Test Case: Logging in with invalid credentials.
        Expectation: Should return an error message.
        """
        with self.app.app_context():
            conn = sqlite3.connect(':memory:')
            conn.execute("CREATE TABLE users (username TEXT UNIQUE, password TEXT, email TEXT)")
            conn.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                        ('testuser', generate_password_hash('testpassword'), 'testuser@example.com'))
            conn.commit()

        response = self.client.post('/login', data=dict(
            username='testuser',
            password='wrongpassword'
        ))

        self.assertEqual(response.status_code, 400)  # Error message due to incorrect password

    # still has error
    def test_signup_with_new_user(self):
        """
        Test Case: Signing up with a new user.
        Expectation: Should redirect to the home page.
        """
        response = self.client.post('/signup', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword'
        })
        self.assertEqual(response.status_code, 302)  # Redirects to home page

    def test_signup_with_existing_username(self):
        """
        Test Case: Signing up with an existing username.
        Expectation: Should return an error message.
        """
        username = 'existinguser'
        password = generate_password_hash('password')
        email = 'existing@example.com'
        
        with self.app.app_context():
            conn = sqlite3.connect(':memory:')
            conn.execute("CREATE TABLE users (username TEXT UNIQUE, password TEXT, email TEXT)")
            conn.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", 
                         (username, password, email))
            conn.commit()

        response = self.client.post('/signup', data={
            'username': username,
            'email': 'newemail@example.com',
            'password': 'newpassword'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'user name or email is already exist', response.data)

    def test_signup_with_existing_email(self):
        """
        Test Case: Signing up with an existing email.
        Expectation: Should return an error message.
        """
        username = 'uniqueuser'
        password = generate_password_hash('password')
        email = 'unique@example.com'
        
        with self.app.app_context():
            conn = sqlite3.connect(':memory:')
            conn.execute("CREATE TABLE users (username TEXT UNIQUE, password TEXT, email TEXT)")
            conn.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", 
                         (username, password, email))
            conn.commit()

        response = self.client.post('/signup', data={
            'username': 'anotheruser',
            'email': email,
            'password': 'newpassword'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'user name or email is already exist', response.data)

    def test_login_page_render(self):
        """
        Test Case: Accessing the login page.
        Expectation: Should render the login page without errors.
        """
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome Back', response.data)

    # still has error
    def test_home_page_render(self):
        """
        Test Case: Accessing the home page.
        Expectation: Should render the home page without errors.
        """
        with self.client.session_transaction() as session:
            session['username'] = 'testuser'
    
        response = self.client.get('/home')  # Ensure correct URL
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the Home Page', response.data)

    def test_logout_page_render(self):
        """
        Test Case: Accessing the logout page.
        Expectation: Should render the logout page without errors.
        """
        # Ensure user is logged in before logout
        with self.client.session_transaction() as session:
            session['username'] = 'testuser'
        
        response = self.client.get('/logout')  # Ensure correct URL
        self.assertEqual(response.status_code, 302)  # Should redirect after logout
        # Check if redirected to the login page or another page
        self.assertEqual(response.location, '/login')

    def test_signup_page_render(self):
        """
        Test Case: Accessing the signup page.
        Expectation: Should render the signup page without errors.
        """
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign Up', response.data)

if __name__ == '__main__':
    unittest.main()
