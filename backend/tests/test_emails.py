from fastapi.testclient import TestClient
from app.main import app
import pytest
from app.errors import AuthenticationError
from app.config import config
from app.security import verify_onetime_token, create_one_time_token, hash_token
from db.queries.one_time_tokens import (
    register_reset_token,
    get_one_time_token,
    register_verify_token,
)
from time import sleep
from freezegun import freeze_time

client = TestClient(app)


def reset():
    client.post(
        "/admin/reset", headers={"Authorization": f"Bearer {config.auth.admin_token}"}
    )


@pytest.fixture(scope="function")
def setup():
    reset()

    test_user = {
        "email": "delivered@resend.dev",
        "username": "spongebob",
        "password": "YourNameIs123!",
    }

    user = client.post("/users", data=test_user)
    user_response = user.json()
    sleep(0.5) # Pause during setup to avoid Resend Errors
    return user_response


def test_verify_ott(setup):
    user = setup["user"]
    token = create_one_time_token()
    register_reset_token(user["id"], hash_token(token))
    result = verify_onetime_token(token)

    assert result == user["id"]


def test_used_ott(setup):
    user = setup["user"]
    token = create_one_time_token()
    register_reset_token(user["id"], hash_token(token))
    verify_onetime_token(token)
    with pytest.raises(AuthenticationError) as result:
        verify_onetime_token(token)

    assert "Invalid or expired token" in result.exconly()


def test_invalid_token(setup):
    user = setup["user"]
    token = create_one_time_token()
    fake_token = create_one_time_token()
    register_reset_token(user["id"], hash_token(token))

    with pytest.raises(AuthenticationError) as result:
        verify_onetime_token(fake_token)

    assert "Invalid or expired token" in result.exconly()


def test_verify_ott_expired(setup):
    user = setup["user"]

    with freeze_time("2025-01-01 12:00:00"):
        token = create_one_time_token()
        register_reset_token(user["id"], hash_token(token))

    with freeze_time("2025-01-01 14:00:00"):
        with pytest.raises(AuthenticationError):
            verify_onetime_token(token)


def test_reset_pwd(setup):
    email = {"email": setup["user"]["email"]}
    response = client.post("/auth/password/reset/", data=email)
    response_data = response.json()

    assert response.status_code == 200
    assert "password reset link shortly" in response_data["message"]


def test_unknown_email():
    email = {"email": "bounced@resend.dev"}
    response = client.post("/auth/password/reset", data=email)
    response_data = response.json()

    assert response.status_code == 200
    assert "password reset link shortly" in response_data["message"]


def test_confirm_pwd(setup):
    password = {"password": "YourNameIs456!"}

    token = create_one_time_token()
    db_token = register_reset_token(setup["user"]["id"], hash_token(token))

    print(db_token.token == hash_token(token))
    print(db_token.user_id == setup["user"]["id"])
    print(get_one_time_token(hash_token(token)).id == db_token.id)

    response = client.post(f"/auth/password/confirm/?token={token}", data=password)

    assert response.status_code == 204


def test_confirm_pwd_faketoken(setup):
    password = {"password": "YourNameIs456!"}

    token = create_one_time_token()
    db_token = register_reset_token(setup["user"]["id"], hash_token(token))

    print(db_token.token == hash_token(token))
    print(db_token.user_id == setup["user"]["id"])
    print(get_one_time_token(hash_token(token)).id == db_token.id)

    response = client.post(
        f"/auth/password/confirm/?token={create_one_time_token()}", data=password
    )

    assert response.status_code == 401


def test_verify_email(setup):
    token = create_one_time_token()
    db_token = register_verify_token(setup["user"]["id"], hash_token(token))
    print(db_token.token == hash_token(token))
    print(db_token.user_id == setup["user"]["id"])

    response = client.post(f"/auth/email/verify/confirm/?token={token}")

    assert response.status_code == 204


def test_send_verify_email(setup):
    token = create_one_time_token()
    db_token = register_verify_token(setup["user"]["id"], hash_token(token))
    print(db_token.token == hash_token(token))
    print(db_token.user_id == setup["user"]["id"])

    response = client.post(
        "/auth/email/verify",
        headers={"Authorization": f"Bearer {setup['access_token']}"},
    )

    assert response.status_code == 204
