# app/test/admin_test/orders_test.py
import pytest


class TestAdminOrders:
    """管理员订单管理测试"""

    def test_get_all_orders(self, client, admin_token, sample_order):
        """测试获取所有订单"""
        response = client.get(
            "/admin/orders",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

    def test_get_pending_review_orders(self, client, admin_token, sample_order):
        """测试获取待审核订单"""
        response = client.get(
            "/admin/orders/pending-review",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

    def test_approve_order_success(self, client, admin_token, sample_order):
        """测试审批通过订单"""
        response = client.post(
            f"/admin/orders/{sample_order.id}/approve",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"approved": True}
        )
        assert response.status_code == 200

    def test_reject_order_with_reason(self, client, admin_token, sample_order):
        """测试拒绝订单"""
        response = client.post(
            f"/admin/orders/{sample_order.id}/approve",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "approved": False,
                "reject_reason": "Inappropriate content"
            }
        )
        assert response.status_code == 200

    def test_update_order(self, client, admin_token, sample_order):
        """测试更新订单信息"""
        response = client.put(
            f"/admin/orders/{sample_order.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Updated Title",
                "price": 200.0
            }
        )
        assert response.status_code == 200

    def test_delete_order(self, client, admin_token, sample_order):
        """测试删除订单"""
        response = client.delete(
            f"/admin/orders/{sample_order.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

    def test_non_admin_access_denied(self, client, customer_token, sample_order):
        """测试非管理员访问拒绝"""
        response = client.get(
            "/admin/orders",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert response.status_code == 403