import unittest
from app import create_app, db
from app.models import User

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        """Test password hashing functionality"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('secret')
        self.assertFalse(user.check_password('wrong'))
        self.assertTrue(user.check_password('secret'))

    def test_user_registration_form(self):
        """Test user registration through form submission"""
        response = self.client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful', response.data)
        
        # Verify user was created in database
        user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'new@example.com')
        self.assertEqual(user.cash, 100000.0)  # Default starting cash

    def test_user_registration_password_mismatch(self):
        """Test registration fails with password mismatch"""
        response = self.client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'testpass123',
            'password2': 'differentpass'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Field must be equal to password', response.data)
        
        # Verify user was not created
        user = User.query.filter_by(username='newuser').first()
        self.assertIsNone(user)

    def test_duplicate_username_registration(self):
        """Test registration fails with duplicate username"""
        # Create first user
        user1 = User(username='testuser', email='test1@example.com')
        user1.set_password('password')
        db.session.add(user1)
        db.session.commit()
        
        # Try to register with same username
        response = self.client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'test2@example.com',
            'password': 'password',
            'password2': 'password'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Username already exists', response.data)

    def test_duplicate_email_registration(self):
        """Test registration fails with duplicate email"""
        # Create first user
        user1 = User(username='testuser1', email='test@example.com')
        user1.set_password('password')
        db.session.add(user1)
        db.session.commit()
        
        # Try to register with same email
        response = self.client.post('/auth/register', data={
            'username': 'testuser2',
            'email': 'test@example.com',
            'password': 'password',
            'password2': 'password'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email already registered', response.data)

    def test_user_login_success(self):
        """Test successful user login"""
        # Create user
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        # Login
        response = self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        # Should redirect to main page after login
        self.assertIn(b'IMPERIJUM', response.data)

    def test_user_login_invalid_username(self):
        """Test login fails with invalid username"""
        response = self.client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'password'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid username or password', response.data)

    def test_user_login_invalid_password(self):
        """Test login fails with invalid password"""
        # Create user
        user = User(username='testuser', email='test@example.com')
        user.set_password('correctpassword')
        db.session.add(user)
        db.session.commit()
        
        # Try login with wrong password
        response = self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid username or password', response.data)

    def test_user_logout(self):
        """Test user logout functionality"""
        # Create and login user
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        # Login first
        self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password'
        })
        
        # Then logout
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_login_redirect_to_next_page(self):
        """Test login redirects to next page if specified"""
        # Create user
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        # Try to access protected page, should redirect to login with next parameter
        response = self.client.get('/game/dashboard')
        self.assertEqual(response.status_code, 302)
        
        # Login with next parameter
        response = self.client.post('/auth/login?next=/game/dashboard', data={
            'username': 'testuser',
            'password': 'password'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_redirect_from_auth_pages(self):
        """Test authenticated users are redirected from login/register pages"""
        # Create and login user
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        # Login
        self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password'
        })
        
        # Try to access login page while authenticated
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 302)  # Should redirect
        
        # Try to access register page while authenticated
        response = self.client.get('/auth/register')
        self.assertEqual(response.status_code, 302)  # Should redirect

if __name__ == '__main__':
    unittest.main()