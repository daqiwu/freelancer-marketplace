# app/test/admin_service_coverage_test.py
"""
Admin service comprehensive tests to boost coverage to 80%+
专门针对admin_service的全面测试以提升覆盖率
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from sqlalchemy import select

from app.models.models import (
    User, Order, OrderStatus, PaymentStatus, ServiceType, LocationEnum
)
from app.services import admin_service


class TestAdminService:
    """管理员服务全面测试"""
    
    @pytest.mark.asyncio
    async def test_get_pending_review_orders(self, db_session, customer_user):
        """测试获取待审核订单列表"""
        # 创建不同状态的订单
        for idx, status in enumerate([
            OrderStatus.pending_review,
            OrderStatus.pending_review,
            OrderStatus.pending,
            OrderStatus.accepted
        ]):
            order = Order(
                id=14000 + idx,
                customer_id=customer_user.id,
                title=f"Order {idx}",
                description="Test",
                service_type=ServiceType.cleaning_repair,
                price=100.0 + idx * 10,
                location=LocationEnum.NORTH,
                address="Test",
                service_start_time=datetime.now() + timedelta(days=1),
                service_end_time=datetime.now() + timedelta(days=1, hours=2),
                status=status,
                payment_status=PaymentStatus.unpaid,
                created_at=datetime.now() - timedelta(minutes=idx),
                updated_at=datetime.now()
            )
            db_session.add(order)
        await db_session.commit()
        
        # 获取待审核订单
        orders = await admin_service.get_pending_review_orders(db_session)
        
        # 应该只返回pending_review状态
        assert len(orders) >= 2
        assert all(o.status == OrderStatus.pending_review for o in orders)
        # 应该按创建时间降序排列（最新的在前）
        for i in range(len(orders) - 1):
            assert orders[i].created_at >= orders[i + 1].created_at
    
    @pytest.mark.asyncio
    async def test_approve_order_success(self, db_session, customer_user):
        """测试成功批准订单"""
        order = Order(
            id=14100,
            customer_id=customer_user.id,
            title="To Approve",
            description="Test",
            service_type=ServiceType.it_technology,
            price=150.0,
            location=LocationEnum.SOUTH,
            address="Test",
            service_start_time=datetime.now() + timedelta(days=1),
            service_end_time=datetime.now() + timedelta(days=1, hours=2),
            status=OrderStatus.pending_review,
            payment_status=PaymentStatus.unpaid,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(order)
        await db_session.commit()
        
        with patch('app.services.admin_service.send_customer_notification', new_callable=AsyncMock):
            approved = await admin_service.approve_order(
                db_session, order.id, approved=True
            )
            
            assert approved.status == OrderStatus.pending
            assert approved.id == order.id
    
    @pytest.mark.asyncio
    async def test_approve_order_not_found(self, db_session):
        """测试批准不存在的订单"""
        with pytest.raises(ValueError, match="Order not found"):
            await admin_service.approve_order(db_session, 99999, approved=True)
    
    @pytest.mark.asyncio
    async def test_approve_order_wrong_status(self, db_session, customer_user):
        """测试批准非待审核状态订单"""
        order = Order(
            id=14101,
            customer_id=customer_user.id,
            title="Already Approved",
            description="Test",
            service_type=ServiceType.education_training,
            price=100.0,
            location=LocationEnum.EAST,
            address="Test",
            service_start_time=datetime.now() + timedelta(days=1),
            service_end_time=datetime.now() + timedelta(days=1, hours=2),
            status=OrderStatus.pending,  # 已经批准过了
            payment_status=PaymentStatus.unpaid,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(order)
        await db_session.commit()
        
        with pytest.raises(ValueError, match="pending_review orders can be approved"):
            await admin_service.approve_order(db_session, order.id, approved=True)
    
    @pytest.mark.asyncio
    async def test_reject_order_success(self, db_session, customer_user):
        """测试成功拒绝订单"""
        order = Order(
            id=14200,
            customer_id=customer_user.id,
            title="To Reject",
            description="Test",
            service_type=ServiceType.life_health,
            price=120.0,
            location=LocationEnum.WEST,
            address="Test",
            service_start_time=datetime.now() + timedelta(days=1),
            service_end_time=datetime.now() + timedelta(days=1, hours=2),
            status=OrderStatus.pending_review,
            payment_status=PaymentStatus.unpaid,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(order)
        await db_session.commit()
        
        reason = "违反服务条款"
        
        with patch('app.services.admin_service.send_customer_notification', new_callable=AsyncMock):
            rejected = await admin_service.approve_order(
                db_session, order.id, approved=False, reject_reason=reason
            )
            
            assert rejected.status == OrderStatus.cancelled
            assert rejected.id == order.id
    
    @pytest.mark.asyncio
    async def test_reject_order_not_found(self, db_session):
        """测试拒绝不存在的订单"""
        with pytest.raises(ValueError, match="Order not found"):
            await admin_service.approve_order(
                db_session, 99999, approved=False, reject_reason="测试原因"
            )
    
    @pytest.mark.asyncio
    async def test_reject_order_wrong_status(self, db_session, customer_user):
        """测试拒绝非待审核状态订单"""
        order = Order(
            id=14201,
            customer_id=customer_user.id,
            title="Completed Order",
            description="Test",
            service_type=ServiceType.design_consulting,
            price=200.0,
            location=LocationEnum.MID,
            address="Test",
            service_start_time=datetime.now(),
            service_end_time=datetime.now() + timedelta(hours=2),
            status=OrderStatus.completed,
            payment_status=PaymentStatus.paid,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(order)
        await db_session.commit()
        
        with pytest.raises(ValueError, match="pending_review orders can be approved"):
            await admin_service.approve_order(
                db_session, order.id, approved=False, reject_reason="测试原因"
            )
    
    @pytest.mark.asyncio
    async def test_list_all_orders_no_filter(self, db_session, customer_user):
        """测试获取所有订单（无筛选）"""
        # 创建多个订单
        for idx in range(5):
            order = Order(
                id=14300 + idx,
                customer_id=customer_user.id,
                title=f"Order {idx}",
                description="Test",
                service_type=ServiceType.other,
                price=100.0,
                location=LocationEnum.NORTH,
                address="Test",
                service_start_time=datetime.now() + timedelta(days=1),
                service_end_time=datetime.now() + timedelta(days=1, hours=2),
                status=OrderStatus.pending,
                payment_status=PaymentStatus.unpaid,
                created_at=datetime.now() - timedelta(days=idx),
                updated_at=datetime.now()
            )
            db_session.add(order)
        await db_session.commit()
        
        orders = await admin_service.list_all_orders(db_session)
        
        assert len(orders) >= 5
        # 应该按创建时间降序排列（默认）
        for i in range(len(orders) - 1):
            assert orders[i].created_at >= orders[i + 1].created_at
    
    @pytest.mark.asyncio
    async def test_list_all_orders_with_status_filter(self, db_session, customer_user):
        """测试按状态筛选订单"""
        # 创建不同状态的订单
        statuses = [
            OrderStatus.pending,
            OrderStatus.accepted,
            OrderStatus.completed,
            OrderStatus.cancelled
        ]
        
        for idx, status in enumerate(statuses):
            order = Order(
                id=14400 + idx,
                customer_id=customer_user.id,
                title=f"Order {status.value}",
                description="Test",
                service_type=ServiceType.cleaning_repair,
                price=100.0,
                location=LocationEnum.SOUTH,
                address="Test",
                service_start_time=datetime.now() + timedelta(days=1),
                service_end_time=datetime.now() + timedelta(days=1, hours=2),
                status=status,
                payment_status=PaymentStatus.unpaid,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db_session.add(order)
        await db_session.commit()
        
        # 筛选completed状态（admin_service使用字符串）
        completed_orders = await admin_service.list_all_orders(
            db_session, status="completed"
        )
        
        assert len(completed_orders) >= 1
        assert all(o.status == OrderStatus.completed for o in completed_orders)
    
    @pytest.mark.asyncio
    async def test_list_all_orders_pagination(self, db_session, customer_user):
        """测试订单分页功能"""
        # 创建多个订单
        for idx in range(5):
            order = Order(
                id=14500 + idx,
                customer_id=customer_user.id,
                title=f"Page Order {idx}",
                description="Test",
                service_type=ServiceType.it_technology,
                price=150.0,
                location=LocationEnum.EAST,
                address="Test",
                service_start_time=datetime.now() + timedelta(days=1),
                service_end_time=datetime.now() + timedelta(days=1, hours=2),
                status=OrderStatus.pending,
                payment_status=PaymentStatus.unpaid,
                created_at=datetime.now() - timedelta(hours=idx),
                updated_at=datetime.now()
            )
            db_session.add(order)
        await db_session.commit()
        
        # 测试第一页（限制2条）
        page1 = await admin_service.list_all_orders(db_session, page=1, limit=2)
        assert len(page1) == 2
        
        # 测试第二页
        page2 = await admin_service.list_all_orders(db_session, page=2, limit=2)
        assert len(page2) >= 2
    
    @pytest.mark.asyncio
    async def test_list_users_by_role_no_filter(self, db_session, customer_user, provider_user, admin_user):
        """测试获取所有用户（无筛选）"""
        users = await admin_service.list_users_by_role(db_session, limit=100)
        
        # 应该包含fixture创建的用户
        assert len(users) >= 3  # customer, provider, admin
    
    @pytest.mark.asyncio
    async def test_list_users_by_role_with_filter(self, db_session, customer_user, provider_user):
        """测试按角色ID筛选用户"""
        # 筛选客户（role_id=1）
        customers = await admin_service.list_users_by_role(db_session, role_id=1, limit=100)
        assert len(customers) >= 1
        assert all(u.role_id == 1 for u in customers)
        
        # 筛选服务商（role_id=2）
        providers = await admin_service.list_users_by_role(db_session, role_id=2, limit=100)
        assert len(providers) >= 1
        assert all(u.role_id == 2 for u in providers)
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, db_session, customer_user):
        """测试成功获取用户信息"""
        user = await admin_service.get_user_by_id(db_session, customer_user.id)
        
        assert user is not None
        assert user.id == customer_user.id
        assert user.username == customer_user.username
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, db_session):
        """测试获取不存在的用户"""
        user = await admin_service.get_user_by_id(db_session, 99999)
        assert user is None
    
    @pytest.mark.asyncio
    async def test_delete_user_by_id_success(self, db_session):
        """测试成功删除用户（验证函数执行）"""
        # 创建一个测试用户
        user = User(
            id=40000,
            username="to_delete",
            email="delete@test.com",
            password_hash="hash",
            role_id=1  # 只传role_id，不传role字符串
        )
        db_session.add(user)
        await db_session.commit()
        
        # 删除用户（此函数会commit）
        await admin_service.delete_user_by_id(db_session, user.id)
        
        # 验证用户已被删除
        check = await db_session.execute(select(User).where(User.id == user.id))
        deleted_user = check.scalars().first()
        assert deleted_user is None
    
    @pytest.mark.asyncio
    async def test_update_order_success(self, db_session, customer_user):
        """测试成功更新订单"""
        order = Order(
            id=14600,
            customer_id=customer_user.id,
            title="Original Title",
            description="Original Description",
            service_type=ServiceType.cleaning_repair,
            price=100.0,
            location=LocationEnum.NORTH,
            address="Original Address",
            service_start_time=datetime.now() + timedelta(days=1),
            service_end_time=datetime.now() + timedelta(days=1, hours=2),
            status=OrderStatus.pending,
            payment_status=PaymentStatus.unpaid,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(order)
        await db_session.commit()
        
        # 更新订单
        update_data = {
            "title": "Updated Title",
            "price": 150.0
        }
        updated_order = await admin_service.update_order(
            db_session, order.id, update_data
        )
        
        assert updated_order.title == "Updated Title"
        assert float(updated_order.price) == 150.0
        assert updated_order.description == "Original Description"  # 未更新的字段应保持不变
    
    @pytest.mark.asyncio
    async def test_update_order_not_found(self, db_session):
        """测试更新不存在的订单"""
        with pytest.raises(ValueError, match="Order not found"):
            await admin_service.update_order(db_session, 99999, {"title": "Test"})
    
    @pytest.mark.asyncio
    async def test_delete_order_success(self, db_session, customer_user):
        """测试成功删除订单"""
        order = Order(
            id=14700,
            customer_id=customer_user.id,
            title="To Delete",
            description="Test",
            service_type=ServiceType.other,
            price=100.0,
            location=LocationEnum.MID,
            address="Test",
            service_start_time=datetime.now() + timedelta(days=1),
            service_end_time=datetime.now() + timedelta(days=1, hours=2),
            status=OrderStatus.pending,
            payment_status=PaymentStatus.unpaid,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(order)
        await db_session.commit()
        
        # 删除订单
        await admin_service.delete_order(db_session, order.id)
        
        # 验证订单已被删除
        check = await db_session.execute(select(Order).where(Order.id == order.id))
        deleted_order = check.scalars().first()
        assert deleted_order is None
