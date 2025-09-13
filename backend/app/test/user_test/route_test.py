import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.user.routes import user_router
from app.user.models import UserCreate, UserLogin, UserCreateResponse, UserLoginResponse


class TestUserRoutes:
    """用户路由层测试类"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用"""
        app = FastAPI()
        app.include_router(user_router)
        return app
    
    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_user_create_data(self):
        """示例用户注册数据"""
        return {
            "name": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
    
    @pytest.fixture
    def sample_user_login_data(self):
        """示例用户登录数据"""
        return {
            "email": "test@example.com",
            "password": "password123"
        }
    
    @pytest.fixture
    def mock_dbsession(self):
        """模拟数据库会话"""
        session = AsyncMock()
        return session

    @patch('app.user.routes.user_register')
    @patch('app.user.routes.DBsession')
    def test_register_success(self, mock_db_session, mock_user_register, client, sample_user_create_data):
        """测试用户注册成功"""
        # 模拟服务层返回用户ID
        mock_user_register.return_value = 1
        mock_db_session.return_value = AsyncMock()
        
        response = client.post("/user/register", json=sample_user_create_data)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == 1
        mock_user_register.assert_called_once()
    
    @patch('app.user.routes.user_register')
    @patch('app.user.routes.DBsession')
    def test_register_validation_error(self, mock_db_session, mock_user_register, client):
        """测试用户注册数据验证错误"""
        # 测试缺少必填字段
        invalid_data = {
            "name": "testuser"
            # 缺少email和password
        }
        
        response = client.post("/user/register", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
        mock_user_register.assert_not_called()
    
    @patch('app.user.routes.user_register')
    @patch('app.user.routes.DBsession')
    def test_register_user_exists(self, mock_db_session, mock_user_register, client, sample_user_create_data):
        """测试用户注册时用户已存在"""
        from fastapi import HTTPException
        
        # 模拟服务层抛出用户已存在的异常
        mock_user_register.side_effect = HTTPException(status_code=400, detail="User already exists")
        mock_db_session.return_value = AsyncMock()
        
        response = client.post("/user/register", json=sample_user_create_data)
        
        assert response.status_code == 400
        response_data = response.json()
        assert response_data["detail"] == "User already exists"
    
    @patch('app.user.routes.user_login')
    @patch('app.user.routes.DBsession')
    def test_login_success(self, mock_db_session, mock_user_login, client, sample_user_login_data):
        """测试用户登录成功"""
        # 模拟服务层返回用户ID
        mock_user_login.return_value = 1
        mock_db_session.return_value = AsyncMock()
        
        response = client.post("/user/login", json=sample_user_login_data)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == 1
        mock_user_login.assert_called_once()
    
    @patch('app.user.routes.user_login')
    @patch('app.user.routes.DBsession')
    def test_login_validation_error(self, mock_db_session, mock_user_login, client):
        """测试用户登录数据验证错误"""
        # 测试缺少必填字段
        invalid_data = {
            "email": "test@example.com"
            # 缺少password
        }
        
        response = client.post("/user/login", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
        mock_user_login.assert_not_called()
    
    @patch('app.user.routes.user_login')
    @patch('app.user.routes.DBsession')
    def test_login_user_not_found(self, mock_db_session, mock_user_login, client, sample_user_login_data):
        """测试用户登录时用户不存在"""
        from fastapi import HTTPException
        
        # 模拟服务层抛出用户不存在的异常
        mock_user_login.side_effect = HTTPException(status_code=400, detail="User not found")
        mock_db_session.return_value = AsyncMock()
        
        response = client.post("/user/login", json=sample_user_login_data)
        
        assert response.status_code == 400
        response_data = response.json()
        assert response_data["detail"] == "User not found"
    
    @patch('app.user.routes.user_login')
    @patch('app.user.routes.DBsession')
    def test_login_invalid_password(self, mock_db_session, mock_user_login, client, sample_user_login_data):
        """测试用户登录时密码错误"""
        from fastapi import HTTPException
        
        # 模拟服务层抛出密码错误的异常
        mock_user_login.side_effect = HTTPException(status_code=400, detail="Invalid password")
        mock_db_session.return_value = AsyncMock()
        
        response = client.post("/user/login", json=sample_user_login_data)
        
        assert response.status_code == 400
        response_data = response.json()
        assert response_data["detail"] == "Invalid password"
    
    def test_register_endpoint_exists(self, client):
        """测试注册端点存在"""
        # 发送无效数据来测试端点是否存在
        response = client.post("/user/register", json={})
        # 应该返回验证错误而不是404
        assert response.status_code != 404
    
    def test_login_endpoint_exists(self, client):
        """测试登录端点存在"""
        # 发送无效数据来测试端点是否存在
        response = client.post("/user/login", json={})
        # 应该返回验证错误而不是404
        assert response.status_code != 404
