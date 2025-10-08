import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.models import User
from app.services.auth_service import register_user, authenticate_user

from httpx import AsyncClient

class TestUserServices:
    """用户服务层测试类"""
    
    @pytest.fixture
    def mock_db(self):
        """模拟异步数据库会话"""
        session = AsyncMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        return session
    
    @pytest.fixture
    def sample_user(self):
        """示例用户对象"""
        return User(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="$2b$12$abcdefghijklmnopqrstuv",  # 假设为bcrypt hash
            role_id=1
        )

    @pytest.mark.asyncio
    async def test_register_user_success(self, mock_db):
        """测试用户注册成功"""
        # 模拟邮箱不存在
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute.return_value = mock_result

        # 模拟refresh设置id
        def refresh_side_effect(user):
            user.id = 1
        mock_db.refresh.side_effect = refresh_side_effect

        user = await register_user(
            mock_db, "testuser", "test@example.com", "password123", 1
        )
        assert user.id == 1
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, mock_db, sample_user, monkeypatch):
        """测试用户认证成功"""
        # mock scalars().first() 返回 sample_user
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_user
        mock_db.execute.return_value = mock_result

        # mock 密码校验
        monkeypatch.setattr(sample_user, "verify_password", lambda pwd: pwd == "password123")

        user = await authenticate_user(mock_db, "test@example.com", "password123")
        assert user == sample_user

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, mock_db):
        """测试用户认证失败-用户不存在"""
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute.return_value = mock_result

        user = await authenticate_user(mock_db, "notfound@example.com", "password123")
        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, mock_db, sample_user, monkeypatch):
        """测试用户认证失败-密码错误"""
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = sample_user
        mock_db.execute.return_value = mock_result

        monkeypatch.setattr(sample_user, "verify_password", lambda pwd: False)

        user = await authenticate_user(mock_db, "test@example.com", "wrongpassword")
        assert user is None

@pytest.mark.asyncio
async def test_register_and_login_api():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        # 清理测试用户
        await ac.delete("http://localhost:8000/auth/test/cleanup?username=apitestuser")

        # 注册
        register_data = {
            "username": "apitestuser",
            "email": "apitestuser@example.com",
            "password": "apitestpass",
            "role_id": 1
        }
        reg_resp = await ac.post("http://localhost:8000/auth/register", json=register_data)
        print(reg_resp.text)  # 调试用
        assert reg_resp.status_code == 200
        assert reg_resp.json()["email"] == "apitestuser@example.com"

        # 登录
        login_data = {
            "email": "apitestuser@example.com",
            "password": "apitestpass"
        }
        login_resp = await ac.post("http://localhost:8000/auth/login", json=login_data)
        assert login_resp.status_code == 200
        assert "access_token" in login_resp.json()