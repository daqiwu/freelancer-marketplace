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
            password="password123"  # 在实际应用中这里应该是哈希过的密码
        )

    @pytest.mark.asyncio
    async def test_user_register_success(self, mock_dbsession, sample_user_create):
        """测试用户注册成功"""
        # --- 修改开始 ---
        # 正确的两步模拟方式
        # 1. 创建模拟结果对象
        mock_result = MagicMock()
        # 2. 设置 first() 方法的返回值
        mock_result.first.return_value = None
        # 3. 让 exec 在 await 后返回这个模拟结果
        mock_dbsession.exec.return_value = mock_result
        # --- 修改结束 ---
        
        # 模拟新用户对象
        mock_dbsession.refresh.side_effect = lambda user: setattr(user, 'id', 1)
        
        result = await user_register(sample_user_create, mock_dbsession)
        
        assert result == 1
        mock_dbsession.add.assert_called_once()
        mock_dbsession.commit.assert_called_once()
        mock_dbsession.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_user_register_email_exists(self, mock_dbsession, sample_user_create):
        """测试用户注册时邮箱已存在"""
        existing_user = User(id=1, name="existing", email=sample_user_create.email, password="pass")
        
        # --- 修改开始 ---
        mock_result = MagicMock()
        mock_result.first.return_value = existing_user
        mock_dbsession.exec.return_value = mock_result
        # --- 修改结束 ---
        
        with pytest.raises(HTTPException) as exc_info:
            await user_register(sample_user_create, mock_dbsession)
        
        assert exc_info.value.status_code == 400
        # 假设你的服务代码中对邮箱和用户名的错误提示是一样的
        assert "already exists" in exc_info.value.detail 
    
    @pytest.mark.asyncio
    async def test_user_register_name_exists(self, mock_dbsession, sample_user_create):
        """测试用户注册时用户名已存在"""
        # --- 修改开始 ---
        mock_result = MagicMock()
        # 第一次调用返回None（邮箱不存在），第二次调用返回用户（用户名存在）
        mock_result.first.side_effect = [None, User(id=1, name=sample_user_create.name, email="other@example.com", password="pass")]
        mock_dbsession.exec.return_value = mock_result
        # --- 修改结束 ---
        
        with pytest.raises(HTTPException) as exc_info:
            await user_register(sample_user_create, mock_dbsession)
        
        assert exc_info.value.status_code == 400
        assert "already exists" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_user_login_success(self, mock_dbsession, sample_user_login, sample_user):
        """测试用户登录成功"""
        # 假设你的密码验证逻辑在服务层
        # 这里为了简单，我们让 sample_user 的密码和 sample_user_login 的密码一致
        
        # --- 修改开始 ---
        mock_result = MagicMock()
        mock_result.first.return_value = sample_user
        mock_dbsession.exec.return_value = mock_result
        # --- 修改结束 ---
        
        # 假设你的服务函数会做密码校验，这里我们暂时忽略密码哈希的复杂性
        result = await user_login(sample_user_login, mock_dbsession)
        
        assert result == sample_user.id
    
    @pytest.mark.asyncio
    async def test_user_login_user_not_found(self, mock_dbsession, sample_user_login):
        """测试用户登录时用户不存在"""
        # --- 修改开始 ---
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_dbsession.exec.return_value = mock_result
        # --- 修改结束 ---
        
        with pytest.raises(HTTPException) as exc_info:
            await user_login(sample_user_login, mock_dbsession)
        
        assert exc_info.value.status_code == 404 # 404 Not Found 通常更合适
        assert "User not found" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_user_login_invalid_password(self, mock_dbsession, sample_user_login, sample_user):
        """测试用户登录时密码错误"""
        # 模拟用户存在
        # --- 修改开始 ---
        mock_result = MagicMock()
        mock_result.first.return_value = sample_user
        mock_dbsession.exec.return_value = mock_result
        # --- 修改结束 ---
        
        # 创建一个密码错误的登录对象
        wrong_password_login = UserLogin(email=sample_user_login.email, password="wrongpassword")
        
        with pytest.raises(HTTPException) as exc_info:
            # 使用错误的密码进行登录
            await user_login(wrong_password_login, mock_dbsession)
        
        assert exc_info.value.status_code == 400
        assert "Invalid password" in exc_info.value.detail