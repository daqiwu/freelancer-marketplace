from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    CustomerInbox,
    CustomerProfile,
    Order,
    OrderStatus,
    ProviderInbox,
    ProviderProfile,
    Review,
    User,
)
from app.services.notification_service import send_customer_notification


async def list_all_orders(
    db: AsyncSession,
    status: str = None,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "created_at",
    order: str = "desc",
):
    """
    Fetch all orders from the database for admin view, with pagination and sorting.
    """
    stmt = select(Order)
    if status:
        stmt = stmt.where(Order.status == status)
    # Sorting
    sort_column = getattr(Order, sort_by, None)
    if sort_column is not None:
        if order == "desc":
            stmt = stmt.order_by(sort_column.desc())
        else:
            stmt = stmt.order_by(sort_column.asc())
    # Pagination
    stmt = stmt.offset((page - 1) * limit).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def list_users_by_role(
    db: AsyncSession,
    role_id: int = None,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "created_at",
    order: str = "desc",
):
    """
    Fetch users filtered by role_id (1=customer, 2=provider), with pagination and sorting. If role_id is None, return all users.
    """
    stmt = select(User)
    if role_id is not None:
        stmt = stmt.where(User.role_id == role_id)
    # Sorting
    sort_column = getattr(User, sort_by, None)
    if sort_column is not None:
        if order == "desc":
            stmt = stmt.order_by(sort_column.desc())
        else:
            stmt = stmt.order_by(sort_column.asc())
    # Pagination
    stmt = stmt.offset((page - 1) * limit).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_user_by_id(db: AsyncSession, id: int):
    """
    Fetch a single user by id.
    """
    return await db.get(User, id)


async def delete_user_by_id(db: AsyncSession, id: int):
    """
    Delete a user by id, including related provider/customer profiles, orders, and reviews.
    """
    # Delete related provider profile first
    await db.execute(delete(ProviderProfile).where(ProviderProfile.id == id))
    # Delete related customer profile if needed
    await db.execute(delete(CustomerProfile).where(CustomerProfile.id == id))

    # Find all order ids for this user (as customer or provider)
    order_ids_result = await db.execute(
        select(Order.id).where((Order.customer_id == id) | (Order.provider_id == id))
    )
    order_ids = [row[0] for row in order_ids_result.fetchall()]

    # Delete provider_inbox and customer_inbox rows referencing these orders
    if order_ids:
        await db.execute(
            delete(ProviderInbox).where(ProviderInbox.order_id.in_(order_ids))
        )
        await db.execute(
            delete(CustomerInbox).where(CustomerInbox.order_id.in_(order_ids))
        )
        # Delete reviews referencing these orders
        await db.execute(delete(Review).where(Review.order_id.in_(order_ids)))

    # Delete related orders (as customer)
    await db.execute(delete(Order).where(Order.customer_id == id))
    # Delete related orders (as provider)
    await db.execute(delete(Order).where(Order.provider_id == id))
    # Now delete the user
    await db.execute(delete(User).where(User.id == id))
    await db.commit()


async def get_pending_review_orders(db: AsyncSession):
    """获取所有待审核订单"""
    result = await db.execute(
        select(Order)
        .where(Order.status == OrderStatus.pending_review)
        .order_by(Order.created_at.desc())
    )
    return result.scalars().all()


async def approve_order(
    db: AsyncSession, order_id: int, approved: bool, reject_reason: str = None
):
    """管理员审批订单"""
    # 查找订单
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalars().first()

    if not order:
        raise ValueError("Order not found")

    if order.status != OrderStatus.pending_review:
        raise ValueError("Only pending_review orders can be approved")

    if approved:
        # 批准订单
        order.status = OrderStatus.pending
        order.updated_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(order)

        # 通知客户
        await send_customer_notification(
            db,
            order.customer_id,
            order.id,
            f"Your order #{order.id} has been approved by admin and is now available for providers to accept.",
        )
        return order
    else:
        # 拒绝订单
        if not reject_reason:
            raise ValueError("Reject reason is required when rejecting an order")

        order.status = OrderStatus.cancelled
        order.updated_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(order)

        # 通知客户
        await send_customer_notification(
            db,
            order.customer_id,
            order.id,
            f"Your order #{order.id} has been rejected. Reason: {reject_reason}",
        )
        return order


async def update_order(db: AsyncSession, order_id: int, update_data: dict):
    """管理员更新订单"""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalars().first()

    if not order:
        raise ValueError("Order not found")

    # 更新订单字段
    for key, value in update_data.items():
        if hasattr(order, key) and value is not None:
            setattr(order, key, value)

    order.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(order)
    return order


async def delete_order(db: AsyncSession, order_id: int):
    """管理员删除订单"""
    # 先删除相关的通知和评价
    await db.execute(delete(CustomerInbox).where(CustomerInbox.order_id == order_id))
    await db.execute(delete(ProviderInbox).where(ProviderInbox.order_id == order_id))
    await db.execute(delete(Review).where(Review.order_id == order_id))

    # 删除订单
    await db.execute(delete(Order).where(Order.id == order_id))
    await db.commit()
