import json
import pytest
from .client import client


def test_users_admins(client):
    response_admin = client.post(
        "/register",
        json={"username": "boris_admin", "password": "123", "role_": "admin"},
    )
    response_login_admin = client.post(
        "/login", json={"username": "boris_admin", "password": "123"}
    )
    data_login_admin = json.loads(response_login_admin.data.decode())
    access_token_admin = data_login_admin["access_token"]

    response_user = client.post(
        "/register", json={"username": "boris", "password": "123", "role_": "user"}
    )

    response_users = client.get(
        "/users/users", headers={"Authorization": f"Bearer {access_token_admin}"}
    )
    data_users = json.loads(response_users.data.decode())

    assert response_users.status_code == 200
    assert data_users[0]["username"] == "boris"
    user_uuid = data_users[0]["username_uuid"]

    response_user = client.get(
        f"/users/user/{user_uuid}",
        headers={"Authorization": f"Bearer {access_token_admin}"},
    )
    data_user = json.loads(response_user.data.decode())
    assert response_user.status_code == 200
    assert data_user["username"] == "boris"
    assert data_user["role"]["role"] == "user"

    response_user_change_role = client.put(
        f"/users/user/{user_uuid}/changeRole",
        json={"role": "admin"},
        headers={"Authorization": f"Bearer {access_token_admin}"},
    )
    data_change_role = json.loads(response_user_change_role.data.decode())
    assert response_user_change_role.status_code == 201
    assert data_change_role["role"]["role"] == "admin"
    assert data_change_role["username"] == "boris"

    response_user_change_username = client.put(
        f"/users/user/{user_uuid}/changeUsername",
        json={"username": "boris_1"},
        headers={"Authorization": f"Bearer {access_token_admin}"},
    )
    data_change_username = json.loads(response_user_change_username.data.decode())
    assert response_user_change_username.status_code == 201
    assert data_change_username["role"]["role"] == "admin"
    assert data_change_username["username"] == "boris_1"

    response_user_change_password = client.put(
        f"/users/user/{user_uuid}/changePassword",
        json={"password": "12"},
        headers={"Authorization": f"Bearer {access_token_admin}"},
    )
    data_change_password = json.loads(response_user_change_password.data.decode())
    assert response_user_change_password.status_code == 201
    assert data_change_password["role"]["role"] == "admin"
    assert data_change_password["username"] == "boris_1"

    response_login = client.post(
        "/login", json={"username": data_change_username["username"], "password": "12"}
    )
    assert response_login.status_code == 200
