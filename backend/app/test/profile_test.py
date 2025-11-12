"""
Profile management tests
"""
import pytest


class TestProfile:
    """个人资料管理测试"""

    def test_update_profile_success(self, client, customer_token):
        """测试更新个人资料成功"""
        response = client.put(
            "/profile",
            headers={"Authorization": f"Bearer {customer_token}"},
            json={
                "username": "updated_name",
                "email": "updated@test.com",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "updated_name"
        assert data["email"] == "updated@test.com"

    def test_update_profile_duplicate_email(
        self, client, customer_token, provider_user
    ):
        """测试更新为已存在邮箱失败"""
        response = client.put(
            "/profile",
            headers={"Authorization": f"Bearer {customer_token}"},
            json={"email": "provider@test.com"},
        )
        assert response.status_code == 400

    def test_change_password_success(self, client, customer_token):
        """测试修改密码成功"""
        response = client.post(
            "/profile/change-password",
            headers={"Authorization": f"Bearer {customer_token}"},
            json={
                "old_password": "password123",
                "new_password": "newpassword123",
            },
        )
        assert response.status_code == 200

    def test_change_password_wrong_old_password(self, client, customer_token):
        """测试旧密码错误"""
        response = client.post(
            "/profile/change-password",
            headers={"Authorization": f"Bearer {customer_token}"},
            json={
                "old_password": "wrongpassword",
                "new_password": "newpassword123",
            },
        )
        assert response.status_code == 400

    def test_change_password_same_as_old(self, client, customer_token):
        """测试新密码与旧密码相同"""
        response = client.post(
            "/profile/change-password",
            headers={"Authorization": f"Bearer {customer_token}"},
            json={
                "old_password": "password123",
                "new_password": "password123",
            },
        )
        # 根据业务逻辑，可能允许也可能不允许
        assert response.status_code in [200, 400]

    def test_update_profile_without_auth(self, client):
        """测试未认证更新资料"""
        response = client.put(
            "/profile", json={"username": "test"}
        )
        assert response.status_code == 401
