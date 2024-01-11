import json
import pytest
from .client import client


def test_register(client):
    response_register = client.post(
        "/register", json={"username": "boris", "password": "123", "role_": "user"}
    )

    assert response_register.status_code == 200
    data_register = json.loads(response_register.data.decode())
    assert data_register["message"] == "You are register successfully!"

    response_register = client.post(
        "/register", json={"username": "boris", "password": "123", "role_": "user"}
    )
    assert response_register.status_code == 400

    response_admin = client.post(
        "/register",
        json={"username": "boris_admin", "password": "123", "role_": "admin"},
    )
    assert response_admin.status_code == 200

    response_login = client.post(
        "/login", json={"username": "boris", "password": "123"}
    )
    assert response_login.status_code == 200
    data_login = json.loads(response_login.data.decode())
    assert data_login["message"] == "You are logged in!"
    assert "access_token" in data_login

    response_login_admin = client.post(
        "/login", json={"username": "boris_admin", "password": "123"}
    )
    assert response_login_admin.status_code == 200
    data_admin = json.loads(response_login_admin.data.decode())
    assert data_admin["message"] == "You are logged as admin!"
    assert "access_token" in data_admin

    response_login_super_admin = client.post(
        "/login", json={"username": "ADMIN", "password": "1234"}
    )
    assert response_login_super_admin.status_code == 200
    data_super_admin = json.loads(response_login_super_admin.data.decode())
    assert data_super_admin["message"] == "You are logged as super_admin"
    assert "access_token" in data_super_admin

    access_token_super_admin = data_super_admin["access_token"]
    access_token_admin = data_admin["access_token"]
    access_token_user = data_login["access_token"]

    response_users_user = client.get(
        "/users", headers={"Authorization": f"Bearer {access_token_user}"}
    )
    response_users_admin = client.get(
        "/users", headers={"Authorization": f"Bearer {access_token_admin}"}
    )
    response_users_super_admin = client.get(
        "/users", headers={"Authorization": f"Bearer {access_token_super_admin}"}
    )

    assert response_users_user.status_code == 409
    assert response_users_admin.status_code == 200

    data_users_admin = json.loads(response_users_admin.data.decode())
    assert data_users_admin[2]["role"]["role"] == "super_admin"
    assert data_users_admin[1]["role"]["role"] == "admin"
    assert data_users_admin[0]["role"]["role"] == "user"

    assert response_users_super_admin.status_code == 200
