import time

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_list_users():
    timestamp = int(time.time())
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # Register and login as admin
        username = f"admintestuser_{timestamp}"
        await ac.delete(f"http://localhost:8000/auth/test/cleanup?username={username}")
        register_data = {
            "username": username,
            "email": f"admintestuser_{timestamp}@example.com",
            "password": "admintestpass",
            "role_id": 3,
        }
        reg_resp = await ac.post(
            "http://localhost:8000/auth/register", json=register_data
        )
        assert reg_resp.status_code == 200
        login_data = {
            "email": f"admintestuser_{timestamp}@example.com",
            "password": "admintestpass",
        }
        login_resp = await ac.post("http://localhost:8000/auth/login", json=login_data)
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # List users
        resp = await ac.get("http://localhost:8000/admin/users/", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data and "total" in data
        assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_admin_get_user():
    timestamp = int(time.time()) + 1
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # Register and login as admin
        username = f"admintestuser2_{timestamp}"
        await ac.delete(f"http://localhost:8000/auth/test/cleanup?username={username}")
        register_data = {
            "username": username,
            "email": f"admintestuser2_{timestamp}@example.com",
            "password": "admintestpass",
            "role_id": 3,
        }
        reg_resp = await ac.post(
            "http://localhost:8000/auth/register", json=register_data
        )
        assert reg_resp.status_code == 200
        login_data = {
            "email": f"admintestuser2_{timestamp}@example.com",
            "password": "admintestpass",
        }
        login_resp = await ac.post("http://localhost:8000/auth/login", json=login_data)
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get user by id (admin's own id)
        user_id = reg_resp.json().get("user_id", None)
        if not user_id:
            # fallback: list users and get id
            list_resp = await ac.get(
                "http://localhost:8000/admin/users/", headers=headers
            )
            user_id = list_resp.json()["items"][0]["id"]
        resp = await ac.get(
            f"http://localhost:8000/admin/users/{user_id}", headers=headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == user_id
        assert data["username"] == username


@pytest.mark.asyncio
async def test_admin_delete_user():
    timestamp = int(time.time()) + 2
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # Register and login as admin
        username = f"admintestuser3_{timestamp}"
        await ac.delete(f"http://localhost:8000/auth/test/cleanup?username={username}")
        register_data = {
            "username": username,
            "email": f"admintestuser3_{timestamp}@example.com",
            "password": "admintestpass",
            "role_id": 3,
        }
        reg_resp = await ac.post(
            "http://localhost:8000/auth/register", json=register_data
        )
        assert reg_resp.status_code == 200
        login_data = {
            "email": f"admintestuser3_{timestamp}@example.com",
            "password": "admintestpass",
        }
        login_resp = await ac.post("http://localhost:8000/auth/login", json=login_data)
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # List users and get id
        list_resp = await ac.get("http://localhost:8000/admin/users/", headers=headers)
        user_id = None
        for u in list_resp.json()["items"]:
            if u["username"] == username:
                user_id = u["id"]
        assert user_id is not None

        # Delete user
        del_resp = await ac.delete(
            f"http://localhost:8000/admin/users/{user_id}", headers=headers
        )
        assert del_resp.status_code == 200
        data = del_resp.json()
        assert (
            "detail" in data
            and f"User {user_id} deleted successfully." in data["detail"]
        )


@pytest.mark.asyncio
async def test_admin_list_orders():
    timestamp = int(time.time()) + 3
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # Register and login as admin
        username = f"admintestuser4_{timestamp}"
        await ac.delete(f"http://localhost:8000/auth/test/cleanup?username={username}")
        register_data = {
            "username": username,
            "email": f"admintestuser4_{timestamp}@example.com",
            "password": "admintestpass",
            "role_id": 3,
        }
        reg_resp = await ac.post(
            "http://localhost:8000/auth/register", json=register_data
        )
        assert reg_resp.status_code == 200
        login_data = {
            "email": f"admintestuser4_{timestamp}@example.com",
            "password": "admintestpass",
        }
        login_resp = await ac.post("http://localhost:8000/auth/login", json=login_data)
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # List orders
        resp = await ac.get("http://localhost:8000/admin/orders", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data and "total" in data
        assert isinstance(data["items"], list)
