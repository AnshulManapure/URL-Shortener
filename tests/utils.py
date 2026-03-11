from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def login_user():
    register = client.post(
        "/register",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    
    # Optional but useful
    assert register.status_code in [200, 201, 400]

    response = client.post(
        "/login",
        data={
            "username": "test@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}

original_url = "https://google.com/"