import unittest
from app import app
from db import db

class TestAppFunctional(unittest.TestCase):
    def setUp(self):
        # Configure test settings
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()  

    # Helper function to register a user
    def register_user(self, username='testuser', password='testpass'):
        return self.client.post('/register', data={
            'username': username,
            'password': password
        }, follow_redirects=True)

    # Helper function to log in a user
    def login_user(self, username='testuser', password='testpass'):
        return self.client.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)

    # Helper function to log out a user
    def logout_user(self):
        return self.client.get('/logout', follow_redirects=True)

    # Test that the home page loads
    def test_home_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    # Test that the login page has a username and password field
    def test_login_form_exists(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Username', response.data)
        self.assertIn(b'Password', response.data)

    # Test that the register page has required fields
    def test_register_form_exists(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Username', response.data)
        self.assertIn(b'Password', response.data)

    # Test that a new user can register
    def test_user_can_register(self):
        response = self.register_user(username='newuser', password='newpass')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)  # Should redirect to login page after registration

    # Test that a registered user can log in and then log out
    def test_user_can_login_and_logout(self):
        self.register_user(username='testuser', password='testpass')

        response = self.login_user(username='testuser', password='testpass')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'My Plants', response.data)  # redirected to my_plants

        response = self.logout_user()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    # Test that adding a plant requires login
    def test_add_plant_requires_login(self):
        response = self.client.get('/add_plant', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Logout', response.data)

    # Test that a logged in user can add a plant
    def test_authenticated_user_can_add_plant(self):
        # Register and log in
        self.register_user(username='plantlover', password='123')
        self.login_user(username='plantlover', password='123')

        response = self.client.post('/add_plant', data={
            'name': 'Cactus',
            'schedule': 14
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Cactus', response.data)

    # Test that a logged in user can view plant details
    def test_authenticated_user_can_view_plant_detail(self):
        self.register_user(username='plantlover', password='123')
        self.login_user(username='plantlover', password='123')

        self.client.post('/add_plant', data={'name': 'Fern', 'schedule': 7})

        response = self.client.get('/my_plants/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Fern', response.data)

    # Test that a logged in user can delete a plant
    def test_authenticated_user_can_delete_plant(self):
        self.register_user(username='plantlover', password='123')
        self.login_user(username='plantlover', password='123')

        self.client.post('/add_plant', data={'name': 'Pothos', 'schedule': 5})

        response = self.client.post('/delete/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Pothos', response.data)


if __name__ == '__main__':
    unittest.main()