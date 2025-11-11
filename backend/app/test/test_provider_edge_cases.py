"""
测试provider_service的边界情况
目标：提升provider_service到接近100%覆盖率
"""
import pytest
from decimal import Decimal
from app.models.models import Order, OrderStatus, ServiceType, LocationEnum
from app.services import provider_service


class TestProviderServiceEdgeCases:
    """测试provider_service的边界条件"""
    
    @pytest.mark.asyncio
    async def test_update_status_not_accepted_to_in_progress(self, db_session, provider_user, customer_user):
        """测试从非accepted状态更新到in_progress应该失败"""
        # 创建pending状态的订单
        order = Order(
            id=90001,
            title="Test Order",
            description="Test",
            price=Decimal("100.00"),
            status=OrderStatus.pending,
            customer_id=customer_user.id,
            provider_id=provider_user.id,
            service_type=ServiceType.it_technology,
            location=LocationEnum.EAST
        )
        db_session.add(order)
        await db_session.commit()
        
        # 尝试从pending直接到in_progress应该失败
        with pytest.raises(ValueError, match="Order must be accepted before starting"):
            await provider_service.update_order_status(
                db_session,
                provider_id=provider_user.id,
                order_id=order.id,
                new_status=OrderStatus.in_progress
            )
    
    @pytest.mark.asyncio
    async def test_update_status_not_in_progress_to_completed(self, db_session, provider_user, customer_user):
        """测试从非in_progress状态更新到completed应该失败"""
        # 创建accepted状态的订单
        order = Order(
            id=90002,
            title="Test Order",
            description="Test",
            price=Decimal("100.00"),
            status=OrderStatus.accepted,
            customer_id=customer_user.id,
            provider_id=provider_user.id,
            service_type=ServiceType.it_technology,
            location=LocationEnum.EAST
        )
        db_session.add(order)
        await db_session.commit()
        
        # 尝试从accepted直接到completed应该失败
        with pytest.raises(ValueError, match="Order must be in progress before completing"):
            await provider_service.update_order_status(
                db_session,
                provider_id=provider_user.id,
                order_id=order.id,
                new_status=OrderStatus.completed
            )
