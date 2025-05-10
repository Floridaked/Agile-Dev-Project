import unittest
from app import app
from db import db
from models.user import User
from models.plant import Plant
from models.complete import Complete
from datetime import datetime
from flask import *

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test_secret"
    })
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.drop_all()

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

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def init_user(app):
    with app.app_context():
        user = User(username="testuser")
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()
        user = db.session.execute(db.select(User).where(User.username =="testuser")).scalar()
        return user

# ---------- UNIT TESTS ----------

def test_user_password_hashing(init_user):
    assert init_user.check_password("testpass") is True
    assert init_user.check_password("wrongpass") is False

def test_plant_completed_method(app, init_user):
    with app.app_context():
        plant = Plant(name="Cactus", schedule=5, user_id=init_user.id, plant_type="flower")
        db.session.add(plant)
        db.session.commit()

        plant.completed()
        db.session.commit()

        assert plant.water_count == 1
        assert plant.watered is True
        assert len(plant.completes) == 1

def test_plant_count_down(app, init_user):
    with app.app_context():
        plant = Plant(name="Aloe", schedule=3, user_id=init_user.id, plant_type="flower")
        db.session.add(plant)
        db.session.commit()
        assert plant.count_down() == 0  # never watered, should return 0

        plant.completed()
        db.session.commit()
        assert plant.count_down() == 3  # watered today

# ---------- FUNCTIONAL TESTS ----------

def test_home_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<title>" in response.data  # assuming templates have <title>

def test_register_and_login(client, app):
    response = client.post("/register", data={"username": "user1", "password": "pass1"})
    assert response.status_code == 302  # redirect to login

    response = client.post("/login", data={"username": "user1", "password": "pass1"})
    assert response.status_code == 302  # redirect to /my_plants

def test_my_plants_requires_login(client):
    response = client.get("/my_plants")
    assert response.status_code == 302  # redirect to login

def test_add_plant(client, app, init_user):
    with client.session_transaction() as sess:
        sess["user_id"] = init_user.id
    first_watered_date = datetime.today().strftime("%Y-%m-%d")

    response = client.post("/add_plant", data={"name": "TestPlant", "schedule": 4, "plant_type": "flower","first_watered": first_watered_date})
    assert response.status_code == 302  # redirect after adding

def test_water_plant(client, app, init_user):
    with app.app_context():
        plant = Plant(name="Fern", schedule=7, user_id=init_user.id, plant_type="flower")
        db.session.add(plant)
        db.session.commit()
        plant_id = plant.id

    with client.session_transaction() as sess:
        sess["user_id"] = init_user.id

    response = client.post(f"/watered/{plant_id}")
    assert response.status_code == 302

def test_plants_when_logged_in(client):
    client.post('/register', data={'username': 'jim', 'password': '123'})
    client.post('/login', data={'username': 'jim', 'password': '123'})
    first_watered_date = datetime.today().strftime("%Y-%m-%d")
    
    client.post('/add_plant', data={'name': 'Rose', 'schedule': '5',"plant_type": "flower","first_watered": first_watered_date})

    res = client.get('/my_plants')
    
    assert b'Rose' in res.data  
    assert res.status_code == 200

def test_delete_plant(client, app, init_user):
    with app.app_context():
        # Add a plant for the user to delete
        plant = Plant(name="Rose", schedule=3, user_id=init_user.id, plant_type="flower")
        db.session.add(plant)
        db.session.commit()

        plant_id = plant.id

    with client.session_transaction() as sess:
        sess["user_id"] = init_user.id
    response = client.post(f"/delete/{plant_id}", follow_redirects=True)

    assert response.status_code == 200

    deleted_plant = db.session.get(Plant, plant_id)
    assert deleted_plant is None 

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