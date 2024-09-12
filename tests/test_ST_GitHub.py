import unittest
from unittest.mock import patch
import os
import tempfile
import sqlite3
from flask import Flask, session
import requests
from ST_GitHub import app, init_db

class FlaskAppTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create a temporary database file and initialize it."""
        cls.db_fd, cls.db_path = tempfile.mkstemp()
        os.close(cls.db_fd)
        app.config['DATABASE'] = cls.db_path
        init_db()

    @classmethod
    def tearDownClass(cls):
        """Remove the temporary database file."""
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def setUp(self):
        """Create a test client and set up context."""
        self.client = app.test_client()
        app.testing = True
        with self.client:
            self.client.get('/logout')  # Ensure the user is logged out before each test

    def tearDown(self):
        """Clean up after each test."""
        pass

    def test_home_if_logged_in(self):
        with self.client.session_transaction() as sess:
            sess['username'] = 'testuser'

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_home_redirect_if_not_logged_in(self):
        """Test that unauthorized users are redirected to login."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertEqual(response.headers['Location'], '/login')  # Check redirection to login page

    def test_login_get(self):
        """Test that the login page loads successfully."""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Log in', response.data)  # Adjust this if necessary

    def test_login_post_success(self):
        """Test login with valid credentials."""
        self.client.post('/signup', data=dict(username='testuser', email='testuser@example.com', password='password'))
        response = self.client.post('/login', data=dict(username='testuser', email='testuser@example.com', password='password'))
        self.assertEqual(response.status_code, 302)  # Redirect on successful login
        self.assertEqual(response.headers['Location'], '/')  # Redirect to home page

    def test_login_post_fail(self):
        """Test login with invalid credentials."""
        response = self.client.post('/login', data=dict(username='cxvxv', email='test@gmail.com', password='wrongpassword'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Check user name or password', response.data)

    def test_signup_get(self):
        """Test that the signup page loads successfully."""
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign Up', response.data)  # Adjust this if necessary

    def test_signup_post_success(self):
        """Test signup with valid details."""
        response = self.client.post('/signup', data=dict(username='newuser', email='newuser@example.com', password='password'))
        self.assertEqual(response.status_code, 302)  # Redirect on successful signup
        self.assertEqual(response.headers['Location'], '/')  # Redirect to home page

    def test_signup_post_duplicate_user(self):
        """Test signup with a duplicate username."""
        self.client.post('/signup', data=dict(username='duplicateuser', email='duplicate@example.com', password='password'))
        response = self.client.post('/signup', data=dict(username='duplicateuser', email='duplicate@example.com', password='password'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'user name or email is already exist', response.data)

    @patch('requests.get')
    def test_get_github_stats(self, mock_get):
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = b'{"login": "testuser", "avatar_url": "http://example.com/avatar", "public_repos": 10, "followers": 5, "following": 3, "created_at": "2020-01-01T00:00:00Z", "repos": [{"name": "repo1", "stargazers_count": 10, "forks_count": 2, "html_url": "http://example.com/repo1"}]}'
        mock_get.return_value = mock_response

        response = self.client.get('/github-stats/testuser')
        self.assertEqual(response.status_code, 200)

    #def test_get_user_readme(self):
    #    """Test fetching README from a GitHub repo."""
    #    response = self.client.get('/get_readme/ALX_project/Hello-World')  # Replace with a valid repo
    #    self.assertEqual(response.status_code, 200)
    #    data = response.get_json()
    #    self.assertIn('content', data)

    def test_github_stats_user_not_found(self):
        """Test fetching GitHub user stats for a non-existent user."""
        response = self.client.get('/github-stats/amrrmogf22hamad')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn('Error', data)

    def test_github_readme_not_found(self):
        """Test fetching README from a non-existent GitHub repo."""
        response = self.client.get('/get_readme/octocat/Invalid-Repo')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn('error', data)

    def test_logout(self):
        """Test that the user is logged out and redirected to login."""
        self.client.post('/signup', data=dict(username='testuser', email='testuser@example.com', password='password'))
        self.client.post('/login', data=dict(username='testuser', email='testuser@example.com', password='password'))
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/login')

if __name__ == '__main__':
    unittest.main()
