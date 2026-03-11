from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    response = client.post(
        url="/register",
        json={
            "email":"test@example.com",
            "password":"password123"
        }
    )
    assert response.status_code == 200


def test_login():
    response = client.post(
        url="/register",
        json={
            "email":"test@example.com",
            "password":"password123"
        }
    )
    assert response.status_code == 200
    
    response = client.post(
        url="/login",
        data={
            "username": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    
    #Check if token exists
    token = response.json()["access_token"]
    assert token is not None