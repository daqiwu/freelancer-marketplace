# app/test/notification_test.py
import pytest
from datetime import datetime
from app.models.models import CustomerInbox, ProviderInbox


class TestNotifications:
    """通知功能测试"""

    @pytest.mark.asyncio
    async def test_get_customer_notifications(self, client, customer_token, customer_user, db_session, sample_order):
        """测试获取客户通知"""
        # 创建测试通知 - 为SQLite测试数据库添加显式id
        notification = CustomerInbox(
            id=50001,  # 显式指定id以支持SQLite内存数据库
            customer_id=customer_user.id,
            order_id=sample_order.id,
            message="Test notification",
            is_read=False,
            created_at=datetime.now()
        )
        db_session.add(notification)
        await db_session.commit()
        
        response = client.get(
            "/notifications/customer",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    @pytest.mark.asyncio
    async def test_get_provider_notifications(self, client, provider_token, provider_user, db_session, accepted_order):
        """测试获取服务商通知"""
        # 创建测试通知 - 为SQLite测试数据库添加显式id
        notification = ProviderInbox(
            id=60001,  # 显式指定id以支持SQLite内存数据库
            provider_id=provider_user.id,
            order_id=accepted_order.id,
            message="Test notification",
            is_read=False,
            created_at=datetime.now()
        )
        db_session.add(notification)
        await db_session.commit()
        
        response = client.get(
            "/notifications/provider",
            headers={"Authorization": f"Bearer {provider_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    @pytest.mark.asyncio
    async def test_mark_notification_as_read(self, client, customer_token, customer_user, db_session, sample_order):
        """测试标记通知为已读"""
        # 创建测试通知 - 为SQLite测试数据库添加显式id
        notification = CustomerInbox(
            id=50002,  # 显式指定id以支持SQLite内存数据库
            customer_id=customer_user.id,
            order_id=sample_order.id,
            message="Test notification",
            is_read=False,
            created_at=datetime.now()
        )
        db_session.add(notification)
        await db_session.commit()
        await db_session.refresh(notification)
        
        response = client.post(
            f"/notifications/read/{notification.id}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert response.status_code == 200