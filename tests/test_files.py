import json
import pytest
from .client import client


def test_add_files(client):
    response_register = client.post(
        "/register", json={"username": "boris", "password": "123", "role_": "user"}
    )
    response_login = client.post(
        "/login", json={"username": "boris", "password": "123"}
    )

    access_token = json.loads(response_login.data.decode())["access_token"]

    file_path = "/home/boris/Downloads/profilna_slika.jpg"

    response_add_file = client.post(
        "/add_files",
        data={"file": open(file_path, "rb")},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    data_add_file = json.loads(response_add_file.data.decode())
    assert "name" in data_add_file
    assert response_add_file.status_code == 200
    name = data_add_file["name"]
    user_uuid = data_add_file["username_uuid"]
    name_uuid = data_add_file["name_uuid"]

    response_show_files = client.get(
        "/show_files", headers={"Authorization": f"Bearer {access_token}"}
    )
    data_show_files = json.loads(response_show_files.data.decode())
    assert response_show_files.status_code == 200
    assert data_show_files[0]["name"] == name
    assert data_show_files[0]["name_uuid"] == name_uuid

    response_show_files_file = client.get(
        f"/show_files/{name_uuid}", headers={"Authorization": f"Bearer {access_token}"}
    )
    data_file = json.loads(response_show_files_file.data.decode())
    assert data_file["name"] == name
