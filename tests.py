import unittest
from app import create_app, db
from app.models import User, Company, Product, Worker, GameState

class BasicTestCase(unittest.TestCase):
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

    def test_user_creation(self):
        """Test user creation and authentication"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()
        
        self.assertTrue(user.check_password('testpass'))
        self.assertFalse(user.check_password('wrongpass'))
        self.assertEqual(user.cash, 100000.0)  # Default starting cash

    def test_company_creation(self):
        """Test company creation"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass')
        db.session.add(user)
        db.session.flush()
        
        company = Company(
            name='Test Company',
            sector='manufacturing',
            owner_id=user.id,
            cash=10000
        )
        db.session.add(company)
        db.session.commit()
        
        self.assertEqual(company.name, 'Test Company')
        self.assertEqual(company.sector, 'manufacturing')
        self.assertEqual(company.owner, user)

    def test_homepage(self):
        """Test homepage loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'IMPERIJUM', response.data)

    def test_registration(self):
        """Test user registration"""
        response = self.client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'testpass',
            'password2': 'testpass'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(user)

if __name__ == '__main__':
    unittest.main()