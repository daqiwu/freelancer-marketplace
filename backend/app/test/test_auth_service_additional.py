"""
最终测试以达到80%覆盖率
覆盖auth_service的create_access_token和logout_user
"""
import pytest
from app.services import auth_service
from datetime import timedelta


class TestFinalCoverage:
    """最终覆盖测试"""
    
    @pytest.mark.asyncio
    async def test_create_access_token_default_expiry(self):
        """测试使用默认过期时间创建token"""
        data = {"sub": "test@test.com", "role_id": 1}
        token = await auth_service.create_access_token(data)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    @pytest.mark.asyncio
    async def test_create_access_token_custom_expiry(self):
        """测试使用自定义过期时间创建token"""
        data = {"sub": "test@test.com", "role_id": 2}
        custom_delta = timedelta(minutes=60)
        token = await auth_service.create_access_token(data, custom_delta)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    @pytest.mark.asyncio
    async def test_logout_user(self):
        """测试登出用户"""
        result = await auth_service.logout_user()
        assert result is not None
        assert "msg" in result
        assert result["msg"] == "Logout successful"
    
    def test_create_access_token_with_role(self):
        """测试使用role创建token"""
        token = auth_service.create_access_token_with_role(100, 1)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
