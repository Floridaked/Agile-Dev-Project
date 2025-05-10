import pytest
from app import app, db
from models import Plant, Complete
from datetime import datetime

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_add_plant(client):
    response = client.post("/add_plant", data={"name": "Test Basil", "schedule": 3}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Test Basil" in response.data

    with app.app_context():
        plant = db.session.query(Plant).filter_by(name="Test Basil").first()
        assert plant is not None
        assert plant.schedule == 3

def test_plant_detail(client):
    with app.app_context():
        plant = Plant(name="Detail Plant", schedule=5)
        db.session.add(plant)
        db.session.commit()
        plant_id = plant.id

    response = client.get(f"/my_plants/{plant_id}")
    assert response.status_code == 200
    assert b"Detail Plant" in response.data

def test_delete_plant(client):
    with app.app_context():
        plant = Plant(name="Delete Me", schedule=5)
        db.session.add(plant)
        db.session.commit()
        plant_id = plant.id

    response = client.post(f"/delete/{plant_id}", follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        deleted = db.session.get(Plant, plant_id)
        assert deleted is None

def test_watered_endpoint(client):
    with app.app_context():
        plant = Plant(name="Water Me", schedule=7)
        db.session.add(plant)
        db.session.commit()
        plant_id = plant.id

    with app.app_context():
        plant = db.session.get(Plant, plant_id)
        plant.watered = True
        new_log = Complete(date=datetime.now().isoformat(), plant=plant)
        db.session.add(new_log)
        db.session.commit()

        assert plant.watered is True
        assert len(plant.completes) == 1

def test_search_plant(client, monkeypatch):
    fake_response = {
        "data": [
            {"id": 1, "common_name": "Mock Plant", "scientific_name": ["Mockus plantus"]}
        ]
    }

    class MockResponse:
        def __init__(self):
            self.status_code = 200
        def json(self):
            return fake_response

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr("requests.get", mock_get)
    response = client.post("/results", data={"query": "mock"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Mock Plant" in response.data
