"""
Unit tests for customer_service.py
Uses mocks to test service layer logic without database
"""
import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.customer_service import (
    publish_order,
    cancel_order,
    get_my_orders,
    get_order_detail,
    get_order_history,
    review_order,
    ReviewData,
)
from app.models.models import (
    Order,
    OrderStatus,
    ServiceType,
    LocationEnum,
    PaymentStatus,
)
from app.models.models import Order, OrderStatus, PaymentStatus, Review


class TestPublishOrder:
    """Test publish_order function."""

    @pytest.mark.asyncio
    async def test_publish_order_success(self):
        """Test successful order publication."""
        # Mock database session
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        # Mock order data
        mock_data = MagicMock()
        mock_data.title = "Test Order"
        mock_data.description = "Test Description"
        mock_data.service_type = "cleaning"
        mock_data.price = 100.0
        mock_data.location = "Test Location"
        mock_data.address = "123 Test St"
        mock_data.service_start_time = None
        mock_data.service_end_time = None
        
        # Mock notification service
        with patch('app.services.customer_service.send_customer_notification', new_callable=AsyncMock):
            order = await publish_order(mock_db, customer_id=1, data=mock_data)
        
        # Assertions
        assert order.title == "Test Order"
        assert order.customer_id == 1
        assert order.status == OrderStatus.pending_review
        assert order.payment_status == PaymentStatus.unpaid
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_order_with_time_range(self):
        """Test order publication with service time range."""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        mock_data = MagicMock()
        mock_data.title = "Scheduled Service"
        mock_data.description = "Service with time"
        mock_data.service_type = "repair"
        mock_data.price = 200.0
        mock_data.location = "Home"
        mock_data.address = "456 Home St"
        mock_data.service_start_time = "2025-12-01T10:00:00+00:00"
        mock_data.service_end_time = "2025-12-01T12:00:00+00:00"
        
        with patch('app.services.customer_service.send_customer_notification', new_callable=AsyncMock):
            order = await publish_order(mock_db, customer_id=2, data=mock_data)
        
        assert order.service_start_time is not None
        assert order.service_end_time is not None


class TestCancelOrder:
    """Test cancel_order function."""

    @pytest.mark.asyncio
    async def test_cancel_pending_order_success(self):
        """Test canceling a pending order."""
        # Mock order
        mock_order = MagicMock(spec=Order)
        mock_order.id = 1
        mock_order.customer_id = 1
        mock_order.status = OrderStatus.pending_review
        mock_order.provider_id = None
        
        # Mock database query result
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = mock_order
        mock_result.scalars.return_value = mock_scalars
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        with patch('app.services.customer_service.send_customer_notification', new_callable=AsyncMock):
            order = await cancel_order(mock_db, customer_id=1, order_id=1)
        
        assert order.status == OrderStatus.cancelled
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_order_not_found(self):
        """Test canceling non-existent order raises error."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = None
        mock_result.scalars.return_value = mock_scalars
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        with pytest.raises(ValueError, match="Order not found"):
            await cancel_order(mock_db, customer_id=1, order_id=999)

    @pytest.mark.asyncio
    async def test_cancel_in_progress_order_fails(self):
        """Test canceling in-progress order raises error."""
        mock_order = MagicMock(spec=Order)
        mock_order.id = 1
        mock_order.customer_id = 1
        mock_order.status = OrderStatus.in_progress
        
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = mock_order
        mock_result.scalars.return_value = mock_scalars
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        with pytest.raises(ValueError, match="can not be cancelled"):
            await cancel_order(mock_db, customer_id=1, order_id=1)

    @pytest.mark.asyncio
    async def test_cancel_order_notifies_provider(self):
        """Test canceling order with provider sends notification."""
        mock_order = MagicMock(spec=Order)
        mock_order.id = 1
        mock_order.customer_id = 1
        mock_order.status = OrderStatus.pending
        mock_order.provider_id = 5  # Has provider
        
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = mock_order
        mock_result.scalars.return_value = mock_scalars
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        with patch('app.services.customer_service.send_customer_notification', new_callable=AsyncMock) as mock_customer_notif, \
             patch('app.services.customer_service.send_provider_notification', new_callable=AsyncMock) as mock_provider_notif:
            await cancel_order(mock_db, customer_id=1, order_id=1)
            
            mock_customer_notif.assert_called_once()
            mock_provider_notif.assert_called_once()


class TestGetMyOrders:
    """Test get_my_orders function."""

    @pytest.mark.asyncio
    async def test_get_my_orders_returns_list(self):
        """Test getting customer's orders returns list."""
        mock_order1 = MagicMock(spec=Order)
        mock_order1.id = 1
        mock_order1.customer_id = 1
        
        mock_order2 = MagicMock(spec=Order)
        mock_order2.id = 2
        mock_order2.customer_id = 1
        
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_order1, mock_order2]
        mock_result.scalars.return_value = mock_scalars
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        orders = await get_my_orders(mock_db, customer_id=1)
        
        assert len(orders) == 2
        assert orders[0].id == 1
        assert orders[1].id == 2

    @pytest.mark.asyncio
    async def test_get_my_orders_empty_list(self):
        """Test getting orders with no results."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        orders = await get_my_orders(mock_db, customer_id=999)
        
        assert orders == []


class TestGetOrderDetail:
    """Test get_order_detail function."""

    @pytest.mark.asyncio
    async def test_get_order_detail_success(self):
        """Test getting order detail successfully."""
        # Create mock order with all required attributes
        mock_order = MagicMock()
        mock_order.id = 1
        mock_order.customer_id = 1
        mock_order.provider_id = 2
        mock_order.title = "Test Order"
        mock_order.description = "Test Description"
        mock_order.service_type = ServiceType.cleaning_repair
        mock_order.status = OrderStatus.completed
        mock_order.price = 100.0
        mock_order.location = LocationEnum.NORTH
        mock_order.address = "Test Address"
        mock_order.service_start_time = None
        mock_order.service_end_time = None
        mock_order.payment_status = PaymentStatus.paid
        mock_order.created_at = datetime.now()
        mock_order.updated_at = datetime.now()
        
        # Mock database execute results
        mock_result1 = MagicMock()
        mock_scalars1 = MagicMock()
        mock_scalars1.first.return_value = mock_order
        mock_result1.scalars.return_value = mock_scalars1
        
        # Mock review query result (no review)
        mock_result2 = MagicMock()
        mock_scalars2 = MagicMock()
        mock_scalars2.first.return_value = None
        mock_result2.scalars.return_value = mock_scalars2
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(side_effect=[mock_result1, mock_result2])
        
        order_detail = await get_order_detail(mock_db, customer_id=1, order_id=1)
        
        assert order_detail["id"] == 1
        assert order_detail["title"] == "Test Order"
        assert order_detail["review"] is None

    @pytest.mark.asyncio
    async def test_get_order_detail_not_found(self):
        """Test getting non-existent order detail returns None."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = None
        mock_result.scalars.return_value = mock_scalars
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        order_detail = await get_order_detail(mock_db, customer_id=1, order_id=999)
        assert order_detail is None


class TestGetOrderHistory:
    """Test get_order_history function."""

    @pytest.mark.asyncio
    async def test_get_order_history_returns_completed_orders(self):
        """Test getting order history returns only completed orders."""
        mock_order1 = MagicMock(spec=Order)
        mock_order1.id = 1
        mock_order1.status = OrderStatus.completed
        
        mock_order2 = MagicMock(spec=Order)
        mock_order2.id = 2
        mock_order2.status = OrderStatus.completed
        
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_order1, mock_order2]
        mock_result.scalars.return_value = mock_scalars
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        orders = await get_order_history(mock_db, customer_id=1)
        
        assert len(orders) == 2
        assert all(order.status == OrderStatus.completed for order in orders)


class TestReviewOrder:
    """Test review_order function."""

    @pytest.mark.asyncio
    @patch("app.services.customer_service.send_customer_notification")
    @patch("app.services.customer_service.send_provider_notification")
    async def test_review_order_success(self, mock_provider_notify, mock_customer_notify):
        """Test submitting a review successfully."""
        mock_order = MagicMock()
        mock_order.payment_status = PaymentStatus.paid
        mock_order.provider_id = 5
        
        # Mock first query (order lookup)
        mock_result1 = MagicMock()
        mock_scalars1 = MagicMock()
        mock_scalars1.first.return_value = mock_order
        mock_result1.scalars.return_value = mock_scalars1
        
        # Mock second query (review lookup - no existing review)
        mock_result2 = MagicMock()
        mock_scalars2 = MagicMock()
        mock_scalars2.first.return_value = None
        mock_result2.scalars.return_value = mock_scalars2
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(side_effect=[mock_result1, mock_result2])
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        
        review_data = ReviewData(order_id=1, stars=5, content="Excellent service!")
        
        await review_order(mock_db, customer_id=1, data=review_data)
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_provider_notify.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.services.customer_service.send_customer_notification")
    @patch("app.services.customer_service.send_provider_notification")
    async def test_review_uncompleted_order_fails(self, mock_provider_notify, mock_customer_notify):
        """Test reviewing unpaid order raises error."""
        mock_order = MagicMock()
        mock_order.payment_status = PaymentStatus.unpaid  # Not paid
        
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = mock_order
        mock_result.scalars.return_value = mock_scalars
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        review_data = ReviewData(order_id=1, stars=5, content="Test")
        
        with pytest.raises(ValueError, match="Only paid orders can be reviewed"):
            await review_order(mock_db, customer_id=1, data=review_data)

    @pytest.mark.asyncio
    @patch("app.services.customer_service.send_customer_notification")
    @patch("app.services.customer_service.send_provider_notification")
    async def test_review_order_without_provider_fails(self, mock_provider_notify, mock_customer_notify):
        """Test reviewing non-existent order raises error."""
        # Mock order not found
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = None
        mock_result.scalars.return_value = mock_scalars
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        review_data = ReviewData(order_id=999, stars=5, content="Test")
        
        with pytest.raises(ValueError, match="Order not found"):
            await review_order(mock_db, customer_id=1, data=review_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
