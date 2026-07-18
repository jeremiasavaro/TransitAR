from uuid import uuid4

from fastapi.testclient import TestClient


def test_register_login_logout_flow(client: TestClient) -> None:
    unique_email = f"user-{uuid4().hex[:10]}@example.com"
    password = "secret123"

    register_resp = client.post(
        "/user/register",
        json={"email": unique_email, "password": password},
    )
    assert register_resp.status_code == 201

    login_resp = client.post(
        "/user/login",
        json={"email": unique_email, "password": password},
    )
    assert login_resp.status_code == 200
    login_payload = login_resp.json()
    token = login_payload["access_token"]
    assert login_payload["token_type"] == "bearer"

    auth_headers = {"Authorization": f"Bearer {token}"}

    protected_ok = client.post(
        "/chat/", json={"message": "hello"}, headers=auth_headers
    )
    assert protected_ok.status_code == 201

    logout_resp = client.post("/user/logout", headers=auth_headers)
    assert logout_resp.status_code == 200

    protected_after_logout = client.post(
        "/chat/", json={"message": "hello again"}, headers=auth_headers
    )
    assert protected_after_logout.status_code == 401
