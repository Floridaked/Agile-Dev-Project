import pytest
from app import app as flask_app
from db import db
from models.user import User
from models.plant import Plant
from models.complete import Complete
from datetime import datetime

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
        return user

# ---------- UNIT TESTS ----------

def test_user_password_hashing(init_user):
    assert init_user.check_password("testpass") is True
    assert init_user.check_password("wrongpass") is False

def test_plant_completed_method(app, init_user):
    with app.app_context():
        plant = Plant(name="Cactus", schedule=5, user_id=init_user.id)
        db.session.add(plant)
        db.session.commit()

        plant.completed()
        db.session.commit()

        assert plant.water_count == 1
        assert plant.watered is True
        assert len(plant.completes) == 1

def test_plant_count_down(app, init_user):
    with app.app_context():
        plant = Plant(name="Aloe", schedule=3, user_id=init_user.id)
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

    response = client.post("/add_plant", data={"name": "TestPlant", "schedule": 4})
    assert response.status_code == 302  # redirect after adding

def test_water_plant(client, app, init_user):
    with app.app_context():
        plant = Plant(name="Fern", schedule=7, user_id=init_user.id)
        db.session.add(plant)
        db.session.commit()
        plant_id = plant.id

    with client.session_transaction() as sess:
        sess["user_id"] = init_user.id

    response = client.post(f"/watered/{plant_id}")
    assert response.status_code == 302

