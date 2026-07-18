from uuid import uuid4

import pytest


@pytest.fixture()
def registered_user(client):
    """Registers a new user and returns their credentials."""
    email = f"test-{uuid4().hex[:10]}@example.com"
    password = "testpass123"
    resp = client.post(
        "/user/register",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 201
    return {"email": email, "password": password}


@pytest.fixture()
def auth_headers(client, registered_user):
    """Logs in the registered user and returns the authorization headers."""
    resp = client.post(
        "/user/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
