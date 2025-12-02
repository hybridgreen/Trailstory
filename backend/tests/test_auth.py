from fastapi.testclient import TestClient
from app.main import app
from app.config import config

client = TestClient(app)

fakeUser = {
    "email": "delivered+user1@resend.dev",
    "username": "spongebob",
    "password": "YourNameIs123!",
}

fakeUser2 = {
    "email": "samlepineapplecom",
    "username": "spongebob2",
    "password": "YourNameIs123!",
}

fakeUser3 = {
    "email": "delivered+user3@resend.dev",
    "username": "fakeuser3",
    "password": "password123",
}


def test_reset_db():
    response = client.post(
        "/admin/reset", headers={"Authorization": f"Bearer {config.auth.admin_token}"}
    )
    assert response.status_code == 204


def test_create_user():
    response = client.post("/users", data=fakeUser)
    response_data = response.json()

    assert response.status_code == 201
    assert "password" not in response_data["user"]
    assert response_data["user"]["username"] == "spongebob"
    assert "access_token" in response_data
    pass


def test_create_user_missing_field():
    response = client.post("/users", data={"email": "semaklgsadlg@test.com"})
    assert response.status_code >= 400


def test_create_user_duplicate():
    response = client.post("/users", data=fakeUser)
    assert response.status_code >= 400
    assert response.json() == {"detail": "User already exists"}


def test_invalid_email():
    response = client.post("/users", data=fakeUser2)
    assert response.status_code >= 400
    assert response.json() == {"detail": "Invalid email"}


def test_weak_password():
    response = client.post("/users", data=fakeUser3)
    assert response.status_code >= 400
    assert response.json() == {"detail": "Weak Password"}


def test_login_success():
    client.post(
        "/users",
        data={
            "email": "test@example.com",
            "password": "ValidPass123",
            "username": "testuser",
        },
    )

    response = client.post(
        "/auth/login", data={"email": "test@example.com", "password": "ValidPass123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"
    assert data["expires_in"] == 3600
    assert "user" in data
    assert "password" not in data["user"]
    assert data["user"]["email"] == "test@example.com"


def test_login_user_not_found():
    response = client.post(
        "/auth/login", data={"email": "nonexistent@example.com", "password": "anything"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Wrong email or password"}


def test_login_wrong_password():
    client.post(
        "/users",
        data={
            "email": "test@example.com",
            "password": "CorrectPass123",
            "username": "testuser",
        },
    )

    response = client.post(
        "/auth/login", data={"email": "test@example.com", "password": "WrongPassword"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Wrong email or password"}


def test_login_empty_credentials():
    response = client.post("/auth/login", data={"email": "", "password": ""})

    assert response.status_code in [401, 422]


def test_login_token_is_valid_jwt():
    client.post(
        "/users",
        data={
            "email": "test@example.com",
            "password": "ValidPass123",
            "username": "testuser",
        },
    )

    response = client.post(
        "/auth/login", data={"email": "test@example.com", "password": "ValidPass123"}
    )

    token = response.json()["access_token"]

    assert len(token.split(".")) == 3


def test_update_password():
    client.post(
        "/admin/reset", headers={"Authorization": f"Bearer {config.auth.admin_token}"}
    )

    res = client.post("/users", data=fakeUser)
    assert res.status_code == 201

    at = res.json()["access_token"]

    passwords = {
        "old_password": fakeUser["password"],
        "new_password": "ThisIsTheNewPassword123!",
    }

    response = client.put(
        "/users/password", data=passwords, headers={"Authorization": f"Bearer {at}"}
    )

    assert response.status_code == 204


def test_same_passwords():
    client.post(
        "/admin/reset", headers={"Authorization": f"Bearer {config.auth.admin_token}"}
    )

    res = client.post("/users", data=fakeUser)
    assert res.status_code == 201

    at = res.json()["access_token"]

    passwords = {
        "old_password": fakeUser["password"],
        "new_password": fakeUser["password"],
    }

    response = client.put(
        "/users/password", data=passwords, headers={"Authorization": f"Bearer {at}"}
    )

    assert response.status_code == 401
    assert "Please choose a new password" in response.json()["detail"]


def test_wrong_password():
    client.post(
        "/admin/reset", headers={"Authorization": f"Bearer {config.auth.admin_token}"}
    )

    res = client.post("/users", data=fakeUser)
    assert res.status_code == 201

    at = res.json()["access_token"]

    passwords = {
        "old_password": "ThisisWrong12345!",
        "new_password": "ThisisWrong12345!",
    }

    response = client.put(
        "/users/password", data=passwords, headers={"Authorization": f"Bearer {at}"}
    )

    assert response.status_code == 401
    assert "Incorrect password" in response.json()["detail"]
