# app/test/user_test/model_test.py (最终正确版)

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from app.user.models import User, UserCreate, UserCreateResponse, UserLogin, UserLoginResponse


class TestUserModels:
    """用户模型测试类"""
    
    def test_user_model_creation(self):
        """测试User模型创建"""
        user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="password123"
        )
        assert user.id == 1
        assert user.name == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "password123"
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
    
    def test_user_model_with_defaults(self):
        """测试User模型使用默认值"""
        user = User(
            name="testuser",
            email="test@example.com",
            password="password123"
        )
        assert user.name == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "password123"
        assert user.id is None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
    
    def test_user_create_model_validation(self):
        """测试UserCreate模型验证"""
        user_create = UserCreate(
            name="testuser",
            email="test@example.com",
            password="password123"
        )
        assert user_create.name == "testuser"
        assert user_create.email == "test@example.com"
        assert user_create.password == "password123"
    
    def test_user_create_model_validation_errors(self):
        """测试UserCreate模型验证错误"""
        # 测试缺少必填字段
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(name="testuser")
        
        errors = exc_info.value.errors()
        assert len(errors) >= 2  # 缺少email和password
        
        # 测试 name 字段长度超限
        with pytest.raises(ValidationError):
            UserCreate(
                name="a" * 51,
                email="test@example.com",
                password="password123"
            )
        
        # 测试 email 字段长度超限
        with pytest.raises(ValidationError):
            UserCreate(
                name="testuser",
                email="a" * 51,
                password="password123"
            )
    
    def test_user_create_response_model(self):
        """测试UserCreateResponse模型"""
        response = UserCreateResponse(id=1)
        assert response.id == 1
    
    def test_user_login_model_validation(self):
        """测试UserLogin模型验证"""
        user_login = UserLogin(
            email="test@example.com",
            password="password123"
        )
        assert user_login.email == "test@example.com"
        assert user_login.password == "password123"
    
    def test_user_login_model_validation_errors(self):
        """测试UserLogin模型验证错误"""
        # 测试缺少必填字段
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(email="test@example.com")
        
        errors = exc_info.value.errors()
        assert len(errors) >= 1  # 缺少password
        
        # 测试 email 字段长度超限
        with pytest.raises(ValidationError):
            UserLogin(
                email="a" * 51,
                password="password123"
            )

    def test_user_login_response_model(self):
        """测试UserLoginResponse模型"""
        response = UserLoginResponse(id=1)
        assert response.id == 1
    
    def test_user_model_field_constraints(self):
        """测试User模型字段约束"""
        user1 = User(name="user1", email="user1@example.com", password="pass1")
        user2 = User(name="user2", email="user2@example.com", password="pass2")
        assert user1.name == "user1"
        assert user2.name == "user2"
        assert user1.email == "user1@example.com"
        assert user2.email == "user2@example.com"
    
    def test_user_model_datetime_fields(self):
        """测试User模型时间字段"""
        user = User(
            name="testuser",
            email="test@example.com",
            password="password123"
        )
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_model_json_serialization(self):
        """测试User模型JSON序列化"""
        user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="password123"
        )
        user_dict = user.model_dump()
        assert isinstance(user_dict, dict)
        assert user_dict["id"] == 1
        assert user_dict["name"] == "testuser"
        assert user_dict["email"] == "test@example.com"
        assert user_dict["password"] == "password123"
    
    def test_user_create_model_json_serialization(self):
        """测试UserCreate模型JSON序列化"""
        user_create = UserCreate(
            name="testuser",
            email="test@example.com",
            password="password123"
        )
        user_dict = user_create.model_dump()
        assert isinstance(user_dict, dict)
        assert user_dict["name"] == "testuser"
        assert user_dict["email"] == "test@example.com"
        assert user_dict["password"] == "password123"
    
    def test_user_login_model_json_serialization(self):
        """测试UserLogin模型JSON序列化"""
        user_login = UserLogin(
            email="test@example.com",
            password="password123"
        )
        user_dict = user_login.model_dump()
        assert isinstance(user_dict, dict)
        assert user_dict["email"] == "test@example.com"
        assert user_dict["password"] == "password123"