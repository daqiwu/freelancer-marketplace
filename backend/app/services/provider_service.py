from typing import List, Optional
from datetime import datetime, UTC

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.models.models import Order, OrderStatus, LocationEnum


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
    # TODO: send inbox notifications to provider and customer
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
    that have been completed or reviewed. Returns 0.0 when none.
    """
    result = await db.execute(
        select(func.coalesce(func.sum(Order.price), 0)).where(
            (Order.provider_id == provider_id)
            & (Order.status.in_([OrderStatus.completed, OrderStatus.reviewed]))
        )
    )
    total = result.scalar() or 0
    # SQLAlchemy may return Decimal; cast to float for API responses
    return float(total)