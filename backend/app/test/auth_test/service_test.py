"""
Unit tests for auth service utility functions
Service layer is tested indirectly through route tests since it uses async database operations.
"""
import pytest
from app.services import auth_service


class TestAuthServiceUtils:
    """认证服务工具函数测试"""

    def test_create_access_token_with_role(self):
        """测试创建包含角色的访问令牌"""
        token = auth_service.create_access_token_with_role(123, 1)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        
    def test_create_access_token_with_different_roles(self):
        """测试不同角色的令牌创建"""
        customer_token = auth_service.create_access_token_with_role(1, 1)
        provider_token = auth_service.create_access_token_with_role(2, 2)
        admin_token = auth_service.create_access_token_with_role(3, 3)
        
        assert customer_token != provider_token
        assert provider_token != admin_token
        assert customer_token != admin_token
