import json
import pytest
from .client import client


def test_users_admins(client):
    response_admin = client.post(
        "/register",
        json={"username": "boris_admin", "password": "123", "role_": "admin"},
    )
    response_login_super_admin = client.post(
        "/login", json={"username": "ADMIN", "password": "1234"}
    )
    data_super_admin = json.loads(response_login_super_admin.data.decode())
    access_token_super_admin = data_super_admin["access_token"]

    response_users_admins = client.get(
        "/users/admins", headers={"Authorization": f"Bearer {access_token_super_admin}"}
    )
    data_users_admins = json.loads(response_users_admins.data.decode())

    assert response_users_admins.status_code == 200
    assert data_users_admins[0]["username"] == "boris_admin"
    admin_uuid = data_users_admins[0]["username_uuid"]

    response_users_admin = client.get(
        f"/users/admin/{admin_uuid}",
        headers={"Authorization": f"Bearer {access_token_super_admin}"},
    )
    data_users_admin = json.loads(response_users_admin.data.decode())
    assert response_users_admin.status_code == 200
    assert data_users_admin["username"] == "boris_admin"
    assert data_users_admin["role"]["role"] == "admin"

    response_users_change_role = client.put(
        f"/users/admin/{admin_uuid}/changeRole",
        json={"role": "user"},
        headers={"Authorization": f"Bearer {access_token_super_admin}"},
    )
    data_change_role = json.loads(response_users_change_role.data.decode())
    assert response_users_change_role.status_code == 201
    assert data_change_role["role"]["role"] == "user"
    assert data_change_role["username"] == "boris_admin"

    response_users_change_username = client.put(
        f"/users/admin/{admin_uuid}/changeUsername",
        json={"username": "boris_admin_1"},
        headers={"Authorization": f"Bearer {access_token_super_admin}"},
    )
    data_change_username = json.loads(response_users_change_username.data.decode())
    assert response_users_change_username.status_code == 201
    assert data_change_username["role"]["role"] == "user"
    assert data_change_username["username"] == "boris_admin_1"

    response_users_change_password = client.put(
        f"/users/admin/{admin_uuid}/changePassword",
        json={"password": "12"},
        headers={"Authorization": f"Bearer {access_token_super_admin}"},
    )
    data_change_password = json.loads(response_users_change_password.data.decode())
    assert response_users_change_password.status_code == 201
    assert data_change_password["role"]["role"] == "user"
    assert data_change_password["username"] == "boris_admin_1"

    response_login = client.post(
        "/login", json={"username": data_change_username["username"], "password": "12"}
    )
    assert response_login.status_code == 200

    response_users_change_role = client.put(
        f"/users/admin/{admin_uuid}/changeRole",
        json={"role": "super_admin"},
        headers={"Authorization": f"Bearer {access_token_super_admin}"},
    )
    data_change_role = json.loads(response_users_change_role.data.decode())
    assert response_users_change_role.status_code == 201
    assert data_change_role["role"]["role"] == "super_admin"
    assert data_change_role["username"] == "boris_admin_1"

    response_super_admins = client.get(
        "/users/superAdmins",
        headers={"Authorization": f"Bearer {access_token_super_admin}"},
    )
    data_super_admins = json.loads(response_super_admins.data.decode())
    assert data_super_admins[0]["username"] == "boris_admin_1"
    super_admin_uuid = data_super_admins[0]["role"]["username_uuid"]

    response_super_admin = client.get(
        f"/users/superAdmin/{super_admin_uuid}",
        headers={"Authorization": f"Bearer {access_token_super_admin}"},
    )
    data_super_admin_ = json.loads(response_super_admin.data.decode())
    assert data_super_admin_["username"] == "boris_admin_1"

    response_login_other_super_admin = client.post(
        "/login", json={"username": "boris_admin_1", "password": "12"}
    )
    data_other_super_admin = json.loads(response_login_other_super_admin.data.decode())
    access_token_other_super_admin = data_other_super_admin["access_token"]

    response_super_admin = client.get(
        f"/users/superAdmin/{super_admin_uuid}",
        headers={"Authorization": f"Bearer {access_token_other_super_admin}"},
    )
    data_super_admin_ = json.loads(response_super_admin.data.decode())
    assert data_super_admin_["message"] == "You can not access here!"
    assert response_super_admin.status_code == 409

    response_change_super_admin = client.put(
        f"/users/superAdmin/{super_admin_uuid}",
        json={"username": "boris_admin", "password": "12", "role": "super_admin"},
        headers={"Authorization": f"Bearer {access_token_super_admin}"},
    )
    data_change_super_admin = json.loads(response_change_super_admin.data.decode())
    assert data_change_super_admin["username"] == "boris_admin"
    assert data_change_super_admin["role"]["role"] == "super_admin"
    assert response_change_super_admin.status_code == 200

    response_change_super_admin_not_filled = client.put(
        f"/users/superAdmin/{super_admin_uuid}",
        json={"username": "", "password": "12", "role": "super_admin"},
        headers={"Authorization": f"Bearer {access_token_super_admin}"},
    )
    data_change_super_admin_not_filled = json.loads(
        response_change_super_admin_not_filled.data.decode()
    )
    assert data_change_super_admin_not_filled["message"] == "Fill this."
    assert response_change_super_admin_not_filled.status_code == 403

    response_change_super_admin_delete = client.delete(
        f"/users/superAdmin/{super_admin_uuid}",
        headers={"Authorization": f"Bearer {access_token_super_admin}"},
    )
    data_change_super_admin_deleted = json.loads(
        response_change_super_admin_delete.data.decode()
    )
    assert data_change_super_admin_deleted["message"] == "Super admin deleted."
    assert response_change_super_admin_delete.status_code == 200

    # response_users_admin_delete = client.delete(f'/users/admin/{admin_uuid}', headers={'Authorization': f'Bearer {access_token_super_admin}'})
    # assert response_users_admin_delete.status_code == 200
    # data_super_admin_delete_admin = json.loads(response_users_admin_delete.data.decode())
    # assert data_super_admin_delete_admin['message'] == 'User is deleted!'
