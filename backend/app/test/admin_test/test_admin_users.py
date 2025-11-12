# app/test/admin_test/users_test.py
import pytest


class TestAdminUsers:
    """管理员用户管理测试"""

    def test_get_all_users(self, client, admin_token, customer_user):
        """测试获取所有用户"""
        response = client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

    def test_filter_users_by_role(self, client, admin_token, customer_user):
        """测试按角色筛选用户"""
        response = client.get(
            "/admin/users?role_id=1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

    def test_delete_user_success(self, client, admin_token, customer_user):
        """测试删除用户成功"""
        response = client.delete(
            f"/admin/users/{customer_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

    def test_delete_admin_user_forbidden(self, client, admin_token, admin_user):
        """测试删除管理员用户失败"""
        response = client.delete(
            f"/admin/users/{admin_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 403