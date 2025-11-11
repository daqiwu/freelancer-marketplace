# app/test/customer_test/payments_test.py
import pytest


class TestCustomerPayments:
    """客户支付功能测试"""

    def test_pay_completed_order(self, client, customer_token, completed_order):
        """测试支付已完成订单"""
        response = client.post(
            f"/customer/orders/pay/{completed_order.id}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["payment_status"] == "paid"

    def test_pay_non_completed_order(self, client, customer_token, accepted_order):
        """测试支付未完成订单失败"""
        response = client.post(
            f"/customer/orders/pay/{accepted_order.id}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert response.status_code == 400

    def test_pay_already_paid_order(self, client, customer_token, completed_order):
        """测试重复支付失败"""
        # 先支付一次
        client.post(
            f"/customer/orders/pay/{completed_order.id}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        # 再次支付
        response = client.post(
            f"/customer/orders/pay/{completed_order.id}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert response.status_code == 400

    def test_pay_others_order(self, client, provider_token, completed_order):
        """测试支付他人订单失败"""
        response = client.post(
            f"/customer/orders/pay/{completed_order.id}",
            headers={"Authorization": f"Bearer {provider_token}"}
        )
        assert response.status_code == 403

    def test_pay_nonexistent_order(self, client, customer_token):
        """测试支付不存在订单"""
        response = client.post(
            "/customer/orders/pay/99999",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert response.status_code == 404