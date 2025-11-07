"""
Unit tests for admin_service.py
Testing business logic with mocked database sessions.
"""
import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import admin_service
from app.models.models import Order, User, OrderStatus


class TestListAllOrders:
    """Tests for list_all_orders function"""

    @pytest.mark.asyncio
    async def test_list_all_orders_no_filter(self):
        """Test listing all orders without status filter"""
        # Mock database session
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            Order(id=1, title="Order 1", status=OrderStatus.pending),
            Order(id=2, title="Order 2", status=OrderStatus.in_progress),
        ]
        mock_db.execute = AsyncMock(return_value=mock_result)

        # Call function
        orders = await admin_service.list_all_orders(mock_db)

        # Assertions
        assert len(orders) == 2
        assert orders[0].id == 1
        assert orders[1].id == 2
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_all_orders_with_status_filter(self):
        """Test listing orders filtered by status"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            Order(id=1, title="Pending Order", status=OrderStatus.pending),
        ]
        mock_db.execute = AsyncMock(return_value=mock_result)

        orders = await admin_service.list_all_orders(mock_db, status="pending")

        assert len(orders) == 1
        assert orders[0].status == OrderStatus.pending

    @pytest.mark.asyncio
    async def test_list_all_orders_with_pagination(self):
        """Test listing orders with pagination"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            Order(id=21, title="Page 2 Order 1"),
            Order(id=22, title="Page 2 Order 2"),
        ]
        mock_db.execute = AsyncMock(return_value=mock_result)

        orders = await admin_service.list_all_orders(mock_db, page=2, limit=20)

        assert len(orders) == 2
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_all_orders_with_sorting_desc(self):
        """Test listing orders with descending sort"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            Order(id=3, title="Latest"),
            Order(id=1, title="Oldest"),
        ]
        mock_db.execute = AsyncMock(return_value=mock_result)

        orders = await admin_service.list_all_orders(
            mock_db, sort_by="created_at", order="desc"
        )

        assert len(orders) == 2
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_all_orders_with_sorting_asc(self):
        """Test listing orders with ascending sort"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        orders = await admin_service.list_all_orders(
            mock_db, sort_by="price", order="asc"
        )

        assert len(orders) == 0
        mock_db.execute.assert_called_once()


class TestListUsersByRole:
    """Tests for list_users_by_role function"""

    @pytest.mark.asyncio
    async def test_list_users_no_role_filter(self):
        """Test listing all users without role filter"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            User(id=1, username="user1", role_id=1),
            User(id=2, username="user2", role_id=2),
            User(id=3, username="admin", role_id=3),
        ]
        mock_db.execute = AsyncMock(return_value=mock_result)

        users = await admin_service.list_users_by_role(mock_db)

        assert len(users) == 3
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_users_by_customer_role(self):
        """Test listing users filtered by customer role"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            User(id=1, username="customer1", role_id=1),
        ]
        mock_db.execute = AsyncMock(return_value=mock_result)

        users = await admin_service.list_users_by_role(mock_db, role_id=1)

        assert len(users) == 1
        assert users[0].role_id == 1

    @pytest.mark.asyncio
    async def test_list_users_with_pagination(self):
        """Test listing users with pagination"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        users = await admin_service.list_users_by_role(mock_db, page=3, limit=10)

        assert len(users) == 0
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_users_with_sorting(self):
        """Test listing users with custom sorting"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            User(id=2, username="buser"),
            User(id=1, username="auser"),
        ]
        mock_db.execute = AsyncMock(return_value=mock_result)

        users = await admin_service.list_users_by_role(
            mock_db, sort_by="username", order="asc"
        )

        assert len(users) == 2
        mock_db.execute.assert_called_once()


class TestGetUserById:
    """Tests for get_user_by_id function"""

    @pytest.mark.asyncio
    async def test_get_user_by_id_found(self):
        """Test getting a user that exists"""
        mock_db = AsyncMock(spec=AsyncSession)
        expected_user = User(id=1, username="testuser", email="test@example.com")
        mock_db.get = AsyncMock(return_value=expected_user)

        user = await admin_service.get_user_by_id(mock_db, 1)

        assert user is not None
        assert user.id == 1
        assert user.username == "testuser"
        mock_db.get.assert_called_once_with(User, 1)

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self):
        """Test getting a user that doesn't exist"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.get = AsyncMock(return_value=None)

        user = await admin_service.get_user_by_id(mock_db, 999)

        assert user is None
        mock_db.get.assert_called_once_with(User, 999)


class TestDeleteUserById:
    """Tests for delete_user_by_id function"""

    @pytest.mark.asyncio
    async def test_delete_user_with_orders(self):
        """Test deleting a user with related orders"""
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Mock order IDs query
        mock_order_result = MagicMock()
        mock_order_result.fetchall.return_value = [(1,), (2,)]
        mock_db.execute = AsyncMock(return_value=mock_order_result)
        mock_db.commit = AsyncMock()

        await admin_service.delete_user_by_id(mock_db, 1)

        # Should be called multiple times for deleting related data
        assert mock_db.execute.call_count >= 7
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user_without_orders(self):
        """Test deleting a user with no related orders"""
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Mock empty order IDs query
        mock_order_result = MagicMock()
        mock_order_result.fetchall.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_order_result)
        mock_db.commit = AsyncMock()

        await admin_service.delete_user_by_id(mock_db, 2)

        # Should still delete profiles and user
        assert mock_db.execute.call_count >= 5
        mock_db.commit.assert_called_once()


class TestGetPendingReviewOrders:
    """Tests for get_pending_review_orders function"""

    @pytest.mark.asyncio
    async def test_get_pending_review_orders(self):
        """Test getting orders pending review"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            Order(id=1, status=OrderStatus.pending_review),
            Order(id=2, status=OrderStatus.pending_review),
        ]
        mock_db.execute = AsyncMock(return_value=mock_result)

        orders = await admin_service.get_pending_review_orders(mock_db)

        assert len(orders) == 2
        assert all(o.status == OrderStatus.pending_review for o in orders)
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_pending_review_orders_empty(self):
        """Test getting pending orders when none exist"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        orders = await admin_service.get_pending_review_orders(mock_db)

        assert len(orders) == 0
        mock_db.execute.assert_called_once()


class TestApproveOrder:
    """Tests for approve_order function"""

    @pytest.mark.asyncio
    async def test_approve_order_success(self):
        """Test approving an order successfully"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_order = Order(
            id=1,
            customer_id=10,
            status=OrderStatus.pending_review,
            updated_at=datetime.now(UTC),
        )
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_order
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        with patch("app.services.admin_service.send_customer_notification") as mock_notify:
            mock_notify.return_value = AsyncMock()
            
            result = await admin_service.approve_order(mock_db, 1, approved=True)

            assert result.status == OrderStatus.pending
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()
            mock_notify.assert_called_once()

    @pytest.mark.asyncio
    async def test_approve_order_not_found(self):
        """Test approving an order that doesn't exist"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="Order not found"):
            await admin_service.approve_order(mock_db, 999, approved=True)

    @pytest.mark.asyncio
    async def test_approve_order_wrong_status(self):
        """Test approving an order with wrong status"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_order = Order(id=1, status=OrderStatus.completed)
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_order
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="Only pending_review orders can be approved"):
            await admin_service.approve_order(mock_db, 1, approved=True)

    @pytest.mark.asyncio
    async def test_reject_order_success(self):
        """Test rejecting an order successfully"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_order = Order(
            id=1,
            customer_id=10,
            status=OrderStatus.pending_review,
            updated_at=datetime.now(UTC),
        )
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_order
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        with patch("app.services.admin_service.send_customer_notification") as mock_notify:
            mock_notify.return_value = AsyncMock()
            
            result = await admin_service.approve_order(
                mock_db, 1, approved=False, reject_reason="Invalid order"
            )

            assert result.status == OrderStatus.cancelled
            mock_db.commit.assert_called_once()
            mock_notify.assert_called_once()

    @pytest.mark.asyncio
    async def test_reject_order_without_reason(self):
        """Test rejecting an order without providing a reason"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_order = Order(id=1, status=OrderStatus.pending_review, customer_id=10)
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_order
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="Reject reason is required"):
            await admin_service.approve_order(mock_db, 1, approved=False)


class TestUpdateOrder:
    """Tests for update_order function"""

    @pytest.mark.asyncio
    async def test_update_order_success(self):
        """Test updating an order successfully"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_order = Order(
            id=1,
            title="Old Title",
            price=100.0,
            status=OrderStatus.pending,
        )
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_order
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        update_data = {"title": "New Title", "price": 150.0}
        result = await admin_service.update_order(mock_db, 1, update_data)

        assert result.title == "New Title"
        assert result.price == 150.0
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_order_not_found(self):
        """Test updating an order that doesn't exist"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="Order not found"):
            await admin_service.update_order(mock_db, 999, {"title": "New"})

    @pytest.mark.asyncio
    async def test_update_order_with_none_values(self):
        """Test updating an order with None values (should skip)"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_order = Order(id=1, title="Original", price=100.0)
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_order
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        update_data = {"title": None, "price": 200.0}
        result = await admin_service.update_order(mock_db, 1, update_data)

        # Title should remain unchanged, price should update
        assert result.title == "Original"
        assert result.price == 200.0


class TestDeleteOrder:
    """Tests for delete_order function"""

    @pytest.mark.asyncio
    async def test_delete_order_success(self):
        """Test deleting an order successfully"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock()
        mock_db.commit = AsyncMock()

        await admin_service.delete_order(mock_db, 1)

        # Should delete CustomerInbox, ProviderInbox, Review, and Order
        assert mock_db.execute.call_count == 4
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_order_cascades(self):
        """Test that deleting order cascades to related records"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock()
        mock_db.commit = AsyncMock()

        await admin_service.delete_order(mock_db, 123)

        # Verify all cascading deletes are called
        assert mock_db.execute.call_count == 4
        mock_db.commit.assert_called_once()
