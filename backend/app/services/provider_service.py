from typing import List, Optional
from datetime import datetime, UTC

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.models.models import Order, OrderStatus, LocationEnum, PaymentStatus, Review
from app.services.notification_service import send_customer_notification, send_provider_notification


async def list_available_orders(
    db: AsyncSession,
    *,
    location: Optional[LocationEnum] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    keyword: Optional[str] = None,
) -> List[Order]:
    """
    Return orders that are currently pending (available to providers),
    with optional filters.
    """
    query = select(Order).where(Order.status == OrderStatus.pending)

    if location is not None:
        query = query.where(Order.location == location)
    if min_price is not None:
        query = query.where(Order.price >= min_price)
    if max_price is not None:
        query = query.where(Order.price <= max_price)
    if keyword:
        like_expr = f"%{keyword.strip()}%"
        query = query.where((Order.title.ilike(like_expr)) | (Order.description.ilike(like_expr)))

    result = await db.execute(query.order_by(Order.created_at.desc()))
    return list(result.scalars().all())


async def accept_order(
    db: AsyncSession,
    *,
    provider_id: int,
    order_id: int,
) -> Order:
    """
    Provider accepts an order: only allowed when order is pending.
    Sets provider_id and updates status to accepted.
    """
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalars().first()
    if not order:
        raise ValueError("Order not found.")

    if order.status != OrderStatus.pending:
        # Match requested failure message semantics
        raise ValueError("The order has already been accepted!")

    order.provider_id = provider_id
    order.status = OrderStatus.accepted
    order.updated_at = datetime.now(UTC)

    await db.commit()
    await db.refresh(order)
    # 通知客户
    await send_customer_notification(
        db, order.customer_id, order.id,
        f"Your order: {order.id} has been accepted by the provider: {provider_id}."
    )
    # 通知服务商
    await send_provider_notification(
        db, provider_id, order.id,
        f"You have successfully accepted the order: {order.id}."
    )
    return order


async def update_order_status(
    db: AsyncSession,
    *,
    provider_id: int,
    order_id: int,
    new_status: OrderStatus,
) -> Order:
    """
    Provider updates the status of an accepted order.
    Allowed transitions:
    - accepted -> in_progress
    - in_progress -> completed
    Only the assigned provider can update.
    """
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalars().first()
    if not order:
        raise ValueError("Order not found.")

    if order.provider_id != provider_id:
        raise ValueError("Permission denied: not your order.")

    if new_status not in {OrderStatus.in_progress, OrderStatus.completed}:
        raise ValueError("Unsupported status update.")

    # Validate state transitions
    if new_status == OrderStatus.in_progress and order.status != OrderStatus.accepted:
        raise ValueError("Order must be accepted before starting.")
    if new_status == OrderStatus.completed and order.status not in {OrderStatus.in_progress}:
        raise ValueError("Order must be in progress before completing.")

    order.status = new_status
    order.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(order)
    # 通知逻辑
    if new_status == OrderStatus.in_progress:
        await send_customer_notification(
            db, order.customer_id, order.id,
            f"The status of your order: {order.id} has been updated to ‘in_progress’ by the provider: {provider_id}."
        )
        await send_provider_notification(
            db, provider_id, order.id,
            f"You have successfully updated the status of the order: {order.id} to ‘in_progress’."
        )
    elif new_status == OrderStatus.completed:
        await send_customer_notification(
            db, order.customer_id, order.id,
            f"The status of your order: {order.id} has been updated to ‘completed’ by the provider: {provider_id}."
        )
        await send_provider_notification(
            db, provider_id, order.id,
            f"You have successfully updated the status of the order: {order.id} to ‘completed’."
        )
    return order


async def list_provider_order_history(
    db: AsyncSession,
    *,
    provider_id: int,
):
    """
    Return all orders associated with the provider, ordered by most recent update.
    """
    result = await db.execute(
        select(Order).where(Order.provider_id == provider_id).order_by(Order.updated_at.desc())
    )
    return list(result.scalars().all())


async def calculate_provider_total_earnings(
    db: AsyncSession,
    *,
    provider_id: int,
):
    """
    Calculate the provider's total earnings as the sum of prices for orders
    that have been paid. Returns 0.0 when none.
    """
    result = await db.execute(
        select(func.coalesce(func.sum(Order.price), 0)).where(
            (Order.provider_id == provider_id)
            & (Order.payment_status == PaymentStatus.paid)
        )
    )
    total = result.scalar() or 0
    return float(total)


async def get_order_detail_for_provider(
    db: AsyncSession,
    *,
    provider_id: int,
    order_id: int,
) -> Optional[dict]:
    """
    Get order detail for a provider-owned order. Include the review if it exists.
    """
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.provider_id == provider_id)
    )
    order = result.scalars().first()
    if not order:
        return None

    review_data = None
    # 查询评价（如果存在）
    review_result = await db.execute(
        select(Review).where(Review.order_id == order_id)
    )
    review = review_result.scalars().first()
    if review:
        review_data = {
            "review_id": review.id,
            "stars": review.stars,
            "content": review.content,
            "created_at": str(review.created_at),
        }

    return {
        "id": order.id,
        "customer_id": order.customer_id,
        "provider_id": order.provider_id,
        "title": order.title,
        "description": order.description,
        "service_type": order.service_type.value,
        "status": order.status.value,
        "price": float(order.price) if order.price is not None else 0.0,
        "location": order.location.value,
        "address": order.address,
        "service_start_time": str(order.service_start_time) if order.service_start_time else None,
        "service_end_time": str(order.service_end_time) if order.service_end_time else None,
        "payment_status": order.payment_status.value,
        "created_at": str(order.created_at),
        "updated_at": str(order.updated_at),
        "review": review_data,
    }