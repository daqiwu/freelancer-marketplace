# app/test/user_test/model_test.py (最终正确版)

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models.models import User
from app.routes.auth import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)


class TestUserORMModel:
    """User ORM模型测试-User ORM Model Tests"""

    def test_user_orm_model_creation(self):
        """测试User ORM模型实例化"""
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hashedpassword",
            role_id=2,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        assert user.id == 1
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password_hash == "hashedpassword"
        assert user.role_id == 2
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)


class TestAuthPydanticModels:
    """认证相关Pydantic模型测试"""

    def test_register_request_validation(self):
        req = RegisterRequest(
            username="testuser",
            email="test@example.com",
            password="password123",
            role_id=1,
        )
        assert req.username == "testuser"
        assert req.email == "test@example.com"
        assert req.password == "password123"
        assert req.role_id == 1

    def test_register_request_validation_error(self):
        with pytest.raises(ValidationError):
            RegisterRequest(
                username="testuser", email="test@example.com", password="password123"
            )
        with pytest.raises(ValidationError):
            RegisterRequest(username="testuser", email="test@example.com", role_id=1)
        with pytest.raises(ValidationError):
            RegisterRequest(email="test@example.com", password="password123", role_id=1)

    def test_register_response(self):
        resp = RegisterResponse(id=1, username="testuser", email="test@example.com")
        assert resp.id == 1
        assert resp.username == "testuser"
        assert resp.email == "test@example.com"

    def test_login_request_validation(self):
        req = LoginRequest(email="test@example.com", password="password123")
        assert req.email == "test@example.com"
        assert req.password == "password123"

    def test_login_request_validation_error(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="test@example.com")
        with pytest.raises(ValidationError):
            LoginRequest(password="password123")

    def test_token_response(self):
        resp = TokenResponse(access_token="sometoken")
        assert resp.access_token == "sometoken"
        assert resp.token_type == "bearer"
