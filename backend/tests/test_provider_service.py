"""
Unit tests for provider_service.py
Uses mocks to test service layer logic without database
"""
import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.provider_service import (
    list_available_orders,
    accept_order,
    update_order_status,
    list_provider_order_history,
    calculate_provider_total_earnings,
    get_order_detail_for_provider
)
from app.models.models import Order, OrderStatus, PaymentStatus, LocationEnum, ServiceType


class TestListAvailableOrders:
    """Test list_available_orders function."""

    @pytest.mark.asyncio
    async def test_list_available_orders_no_filter(self):
        """Test listing all available orders without filters."""
        mock_order1 = MagicMock(spec=Order)
        mock_order1.id = 1
        mock_order1.status = OrderStatus.pending
        
        mock_order2 = MagicMock(spec=Order)
        mock_order2.id = 2
        mock_order2.status = OrderStatus.pending
        
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_order1, mock_order2]
        mock_result.scalars.return_value = mock_scalars
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        orders = await list_available_orders(mock_db)
        
        assert len(orders) == 2
        assert orders[0].id == 1
        assert orders[1].id == 2

    @pytest.mark.asyncio
    async def test_list_available_orders_with_location_filter(self):
        """Test listing orders filtered by location."""
        mock_order = MagicMock(spec=Order)
        mock_order.id = 1
        mock_order.location = LocationEnum.NORTH
        
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_order]
        mock_result.scalars.return_value = mock_scalars
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        orders = await list_available_orders(mock_db, location=LocationEnum.NORTH)
        
        assert len(orders) == 1
        assert orders[0].location == LocationEnum.NORTH

    @pytest.mark.asyncio
    async def test_list_available_orders_with_price_range(self):
        """Test listing orders filtered by price range."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        orders = await list_available_orders(
            mock_db,
            min_price=100.0,
            max_price=500.0
        )
        
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_available_orders_with_keyword(self):
        """Test listing orders filtered by keyword search."""
        mock_order = MagicMock(spec=Order)
        mock_order.id = 1
        mock_order.title = "Website Development"
        
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_order]
        mock_result.scalars.return_value = mock_scalars
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        orders = await list_available_orders(mock_db, keyword="website")
        
        assert len(orders) == 1


class TestAcceptOrder:
    """Test accept_order function."""

    @pytest.mark.asyncio
    async def test_accept_pending_order_success(self):
        """Test accepting a pending order successfully."""
        mock_order = MagicMock(spec=Order)
        mock_order.id = 1
        mock_order.customer_id = 1
        mock_order.status = OrderStatus.pending
        mock_order.provider_id = None
        
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = mock_order
        mock_result.scalars.return_value = mock_scalars
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        with patch('app.services.provider_service.send_customer_notification', new_callable=AsyncMock), \
             patch('app.services.provider_service.send_provider_notification', new_callable=AsyncMock):
            order = await accept_order(mock_db, provider_id=5, order_id=1)
        
        assert order.provider_id == 5
        assert order.status == OrderStatus.accepted
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_accept_nonexistent_order_fails(self):
        """Test accepting non-existent order raises error."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = None
        mock_result.scalars.return_value = mock_scalars
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        with pytest.raises(ValueError, match="Order not found"):
            await accept_order(mock_db, provider_id=5, order_id=999)

    @pytest.mark.asyncio
    async def test_accept_already_accepted_order_fails(self):
        """Test accepting already accepted order raises error."""
        mock_order = MagicMock(spec=Order)
        mock_order.id = 1
        mock_order.status = OrderStatus.accepted  # Already accepted
        
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = mock_order
        mock_result.scalars.return_value = mock_scalars
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        with pytest.raises(ValueError, match="already been accepted"):
            await accept_order(mock_db, provider_id=5, order_id=1)


class TestUpdateOrderStatus:
    """Test update_order_status function."""

    @pytest.mark.asyncio
    async def test_update_order_status_to_in_progress(self):
        """Test updating order status to in_progress."""
        mock_order = MagicMock(spec=Order)
        mock_order.id = 1
        mock_order.provider_id = 5
        mock_order.customer_id = 1
        mock_order.status = OrderStatus.accepted
        
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = mock_order
        mock_result.scalars.return_value = mock_scalars
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        with patch('app.services.provider_service.send_customer_notification', new_callable=AsyncMock):
            order = await update_order_status(
                mock_db,
                provider_id=5,
                order_id=1,
                new_status=OrderStatus.in_progress
            )
        
        assert order.status == OrderStatus.in_progress
        assert mock_db.commit.call_count == 2  # One for order update, one for notification

    @pytest.mark.asyncio
    async def test_update_order_wrong_provider_fails(self):
        """Test updating order by wrong provider raises error."""
        mock_order = MagicMock(spec=Order)
        mock_order.id = 1
        mock_order.provider_id = 5
        mock_order.status = OrderStatus.accepted
        
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = mock_order
        mock_result.scalars.return_value = mock_scalars
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        with pytest.raises(ValueError, match="Permission"):
            await update_order_status(
                mock_db,
                provider_id=999,  # Different provider
                order_id=1,
                new_status=OrderStatus.in_progress
            )


class TestListProviderOrderHistory:
    """Test list_provider_order_history function."""

    @pytest.mark.asyncio
    async def test_list_provider_order_history(self):
        """Test listing provider's order history."""
        mock_order1 = MagicMock(spec=Order)
        mock_order1.id = 1
        mock_order1.provider_id = 5
        
        mock_order2 = MagicMock(spec=Order)
        mock_order2.id = 2
        mock_order2.provider_id = 5
        
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_order1, mock_order2]
        mock_result.scalars.return_value = mock_scalars
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        orders = await list_provider_order_history(mock_db, provider_id=5)
        
        assert len(orders) == 2
        assert orders[0].provider_id == 5
        assert orders[1].provider_id == 5

    @pytest.mark.asyncio
    async def test_list_provider_order_history_empty(self):
        """Test provider with no history returns empty list."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        orders = await list_provider_order_history(mock_db, provider_id=999)
        
        assert orders == []


class TestCalculateProviderTotalEarnings:
    """Test calculate_provider_total_earnings function."""

    @pytest.mark.asyncio
    async def test_calculate_earnings_with_completed_orders(self):
        """Test calculating earnings with completed paid orders."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 1500.0  # Total earnings
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        earnings = await calculate_provider_total_earnings(mock_db, provider_id=5)
        
        assert earnings == 1500.0

    @pytest.mark.asyncio
    async def test_calculate_earnings_no_orders(self):
        """Test calculating earnings with no completed orders."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0  # No earnings
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        earnings = await calculate_provider_total_earnings(mock_db, provider_id=999)
        
        assert earnings == 0.0


class TestGetOrderDetailForProvider:
    """Test get_order_detail_for_provider function."""

    @pytest.mark.asyncio
    async def test_get_order_detail_success(self):
        """Test getting order detail for provider."""
        # Create mock order with all required attributes
        mock_order = MagicMock()
        mock_order.id = 1
        mock_order.customer_id = 1
        mock_order.provider_id = 5
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
        
        # Mock review with stars attribute
        mock_review = MagicMock()
        mock_review.id = 1
        mock_review.stars = 5
        mock_review.content = "Great job!"
        mock_review.created_at = datetime.now()
        
        # Mock first query (order lookup)
        mock_result1 = MagicMock()
        mock_scalars1 = MagicMock()
        mock_scalars1.first.return_value = mock_order
        mock_result1.scalars.return_value = mock_scalars1
        
        # Mock second query (review lookup)
        mock_result2 = MagicMock()
        mock_scalars2 = MagicMock()
        mock_scalars2.first.return_value = mock_review
        mock_result2.scalars.return_value = mock_scalars2
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(side_effect=[mock_result1, mock_result2])
        
        order_detail = await get_order_detail_for_provider(mock_db, provider_id=5, order_id=1)
        
        assert order_detail["id"] == 1
        assert order_detail["title"] == "Test Order"

    @pytest.mark.asyncio
    async def test_get_order_detail_wrong_provider_fails(self):
        """Test getting order detail by wrong provider returns None."""
        # Mock order not found for wrong provider
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = None
        mock_result.scalars.return_value = mock_scalars
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        order_detail = await get_order_detail_for_provider(mock_db, provider_id=999, order_id=1)
        assert order_detail is None

    @pytest.mark.asyncio
    async def test_get_nonexistent_order_detail_fails(self):
        """Test getting non-existent order detail returns None."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.first.return_value = None
        mock_result.scalars.return_value = mock_scalars
        
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        order_detail = await get_order_detail_for_provider(mock_db, provider_id=5, order_id=999)
        assert order_detail is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
