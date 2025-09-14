import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from sqlmodel import select

from app.user.models import User, UserCreate, UserLogin
from app.user.services import user_register, user_login
from app.database.session import DBsession


class TestUserServices:
    """用户服务层测试类"""
    
    @pytest.fixture
    def mock_dbsession(self):
        """模拟数据库会话"""
        session = AsyncMock(spec=DBsession)
        session.exec = AsyncMock()
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        return session
    
    @pytest.fixture
    def sample_user_create(self):
        """示例用户创建数据"""
        return UserCreate(
            name="testuser",
            email="test@example.com",
            password="password123"
        )
    
    @pytest.fixture
    def sample_user_login(self):
        """示例用户登录数据"""
        return UserLogin(
            email="test@example.com",
            password="password123"
        )
    
    @pytest.fixture
    def sample_user(self):
        """示例用户对象"""
        return User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="password123"
        )

    @pytest.mark.asyncio
    async def test_user_register_success(self, mock_dbsession, sample_user_create):
        """测试用户注册成功"""
        # 模拟邮箱和用户名都不存在
        mock_dbsession.exec.return_value.first.return_value = None
        
        # 模拟新用户对象
        new_user = User(id=1, name=sample_user_create.name, 
                       email=sample_user_create.email, 
                       password=sample_user_create.password)
        mock_dbsession.refresh.side_effect = lambda user: setattr(user, 'id', 1)
        
        result = await user_register(sample_user_create, mock_dbsession)
        
        assert result == 1
        mock_dbsession.add.assert_called_once()
        mock_dbsession.commit.assert_called_once()
        mock_dbsession.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_user_register_email_exists(self, mock_dbsession, sample_user_create):
        """测试用户注册时邮箱已存在"""
        # 模拟邮箱已存在
        existing_user = User(id=1, name="existing", email=sample_user_create.email, password="pass")
        mock_dbsession.exec.return_value.first.return_value = existing_user
        
        with pytest.raises(HTTPException) as exc_info:
            await user_register(sample_user_create, mock_dbsession)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "User already exists"
    
    @pytest.mark.asyncio
    async def test_user_register_name_exists(self, mock_dbsession, sample_user_create):
        """测试用户注册时用户名已存在"""
        # 第一次调用返回None（邮箱不存在），第二次调用返回用户（用户名存在）
        mock_dbsession.exec.return_value.first.side_effect = [None, User(id=1, name=sample_user_create.name, email="other@example.com", password="pass")]
        
        with pytest.raises(HTTPException) as exc_info:
            await user_register(sample_user_create, mock_dbsession)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "User already exists"
    
    @pytest.mark.asyncio
    async def test_user_login_success(self, mock_dbsession, sample_user_login, sample_user):
        """测试用户登录成功"""
        # 模拟用户存在且密码正确
        mock_dbsession.exec.return_value.first.return_value = sample_user
        
        result = await user_login(sample_user_login, mock_dbsession)
        
        assert result == sample_user.id
    
    @pytest.mark.asyncio
    async def test_user_login_user_not_found(self, mock_dbsession, sample_user_login):
        """测试用户登录时用户不存在"""
        # 模拟用户不存在
        mock_dbsession.exec.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await user_login(sample_user_login, mock_dbsession)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "User not found"
    
    @pytest.mark.asyncio
    async def test_user_login_invalid_password(self, mock_dbsession, sample_user_login, sample_user):
        """测试用户登录时密码错误"""
        # 模拟用户存在但密码错误
        mock_dbsession.exec.return_value.first.return_value = sample_user
        
        with pytest.raises(HTTPException) as exc_info:
            await user_login(sample_user_login, mock_dbsession)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Invalid password"
