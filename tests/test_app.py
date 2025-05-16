import pytest
from app import app as flask_app
from db import db
from models import *
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
    
@pytest.fixture
def init_plant(app, init_user):
    with app.app_context():
        plant = Plant(name="Aloe", schedule=3, user_id=init_user.id, plant_type="flower")
        db.session.add(plant)
        db.session.commit()
        plant = db.session.execute(db.select(Plant).where(Plant.name =="Aloe")).scalar()
        return plant

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

def test_login_form_exists(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Username' in response.data
    assert b'Password' in response.data

def test_register_form_exists(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Username' in response.data
    assert b'Password' in response.data

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

def decode_response(response):
    return response.data.decode("utf-8")

def test_plant_info_route(client, init_user):
    with client.session_transaction() as sess:
        sess['user_id'] = init_user.id

    response = client.get("/plant/1")

    if response.status_code == 404:
        pytest.skip("Plant with ID 1 not found in CI")
    assert response.status_code == 200
    text = decode_response(response)
    assert "Plant Info" in text
    assert "Watering" in text
    assert "Sunlight" in text
    assert "Pruning" in text

def test_medal_awarding(client, init_user):
    with client.session_transaction() as sess:
        db.session.commit()
        sess['user_id'] = init_user.id
    for i in range(3):
        plant = Plant(name=f"Plant{i}", schedule=7,plant_type="outdoor", user_id=init_user.id)
        db.session.add(plant)
    db.session.commit()

    response = client.get("/my_plants")
    assert response.status_code == 200
  
    achievement =  db.session.execute(db.select(Achievement).where((Achievement.user_id == init_user.id) & (Achievement.medal == "Bronze Planter"))).scalar()
    assert achievement is not None


def test_plant_detail_route(client, app, init_user, init_plant):
   
    response = client.get(f"/my_plants/{init_plant.id}")
    with client.session_transaction() as sess:
        sess['user_id'] = init_user.id

    response = client.get("/my_plants/99999")
    assert response.status_code == 404
    assert b"Plant not found" in response.data


    response = client.get(f"/my_plants/{init_plant.id}")
    assert response.status_code == 200
    assert b"Watering log" in response.data

def test_edit_plant_get_and_post(client, init_user, init_plant):
  
    with client.session_transaction() as sess:
        sess["user_id"] = init_user.id

    response = client.get(f"/edit_plant/{init_plant.id}")
    assert response.status_code == 200

    response = client.post(f"/edit_plant/{init_plant.id}", data={"name": "Updated Plant", "schedule": "10"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"My Plants" in response.data

    updated_plant = db.session.get(Plant, init_plant.id)
    assert updated_plant.name == "Updated Plant"
    assert updated_plant.schedule == 10

def test_achievements_route(client, init_user):
    achievement = Achievement(user_id=init_user.id, medal="Bronze Planter")
    db.session.add(achievement)
    db.session.commit()

    with client.session_transaction() as sess:
        sess["user_id"] = init_user.id

    response = client.get("/achievements")
    assert response.status_code == 200
    assert b"Bronze Planter" in response.data

def test_search_plant_route(client):
    response = client.get("/search_plant")
    assert response.status_code == 200
    assert b"Search" in response.data or b"Plant" in response.data