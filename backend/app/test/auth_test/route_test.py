from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routes.auth import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    auth_router,
)


class TestAuthRoutes:
    """认证路由层测试类"""

    @pytest.fixture
    def app(self):
        """创建测试应用"""
        app = FastAPI()
        app.include_router(auth_router)
        return app

    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return TestClient(app)

    @pytest.fixture
    def sample_register_data(self):
        """示例注册数据"""
        return {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "role_id": 1,
        }

    @pytest.fixture
    def sample_login_data(self):
        """示例登录数据"""
        return {"email": "test@example.com", "password": "password123"}

    @patch("app.routes.auth.register_user", new_callable=AsyncMock)
    @patch("app.routes.auth.get_db")
    def test_register_success(
        self, mock_get_db, mock_register_user, client, sample_register_data
    ):
        """测试注册成功"""
        mock_register_user.return_value = type(
            "User", (), {"id": 1, "username": "testuser", "email": "test@example.com"}
        )()
        mock_get_db.return_value.__aenter__.return_value = AsyncMock()
        response = client.post("/auth/register", json=sample_register_data)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        mock_register_user.assert_awaited_once()

    def test_register_validation_error(self, client):
        """测试注册数据验证错误"""
        invalid_data = {
            "username": "testuser"
            # 缺少email, password, role_id
        }
        response = client.post("/auth/register", json=invalid_data)
        assert response.status_code == 422

    @patch("app.routes.auth.register_user", new_callable=AsyncMock)
    @patch("app.routes.auth.get_db")
    def test_register_user_exists(
        self, mock_get_db, mock_register_user, client, sample_register_data
    ):
        """测试注册时用户已存在"""
        from fastapi import HTTPException

        mock_register_user.side_effect = HTTPException(
            status_code=400, detail="User already exists"
        )
        mock_get_db.return_value.__aenter__.return_value = AsyncMock()
        response = client.post("/auth/register", json=sample_register_data)
        assert response.status_code == 400
        assert response.json()["detail"] == "User already exists"

    @patch("app.routes.auth.authenticate_user", new_callable=AsyncMock)
    @patch("app.routes.auth.create_access_token_with_role")
    @patch("app.routes.auth.get_db")
    def test_login_success(
        self,
        mock_get_db,
        mock_create_access_token_with_role,
        mock_authenticate_user,
        client,
        sample_login_data,
    ):
        """测试登录成功"""
        mock_authenticate_user.return_value = type(
            "User", (), {"id": 1, "role_id": 1}
        )()
        mock_create_access_token_with_role.return_value = "sometoken"
        mock_get_db.return_value.__aenter__.return_value = AsyncMock()
        response = client.post("/auth/login", json=sample_login_data)
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "sometoken"
        assert data["token_type"] == "bearer"
        mock_authenticate_user.assert_awaited_once()
        mock_create_access_token_with_role.assert_called_once_with(1, 1)

    def test_login_validation_error(self, client):
        """测试登录数据验证错误"""
        invalid_data = {
            "email": "test@example.com"
            # 缺少password
        }
        response = client.post("/auth/login", json=invalid_data)
        assert response.status_code == 422

    @patch("app.routes.auth.authenticate_user", new_callable=AsyncMock)
    @patch("app.routes.auth.get_db")
    def test_login_user_not_found(
        self, mock_get_db, mock_authenticate_user, client, sample_login_data
    ):
        """测试登录时用户不存在"""
        mock_authenticate_user.return_value = None
        mock_get_db.return_value.__aenter__.return_value = AsyncMock()
        response = client.post("/auth/login", json=sample_login_data)
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    def test_register_endpoint_exists(self, client):
        """测试注册端点存在"""
        response = client.post("/auth/register", json={})
        assert response.status_code != 404

    def test_login_endpoint_exists(self, client):
        """测试登录端点存在"""
        response = client.post("/auth/login", json={})
        assert response.status_code != 404
