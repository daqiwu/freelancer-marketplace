from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Review, Order, OrderStatus, PaymentStatus
from datetime import datetime, UTC
from sqlalchemy.future import select
from typing import List
from app.services.notification_service import send_customer_notification, send_provider_notification

async def publish_order(db: AsyncSession, customer_id: int, data):
    # 数据校验已在 Pydantic 层完成  # Data validation is done in Pydantic layer
    order = Order(
        customer_id=customer_id,
        title=data.title,
        description=data.description,
        price=data.price,
        location=data.location,
        address=data.address,
        status=OrderStatus.pending,
        payment_status=PaymentStatus.unpaid,  # 新增，默认未支付  # New, default unpaid
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    # 通知客户
    await send_customer_notification(
        db, customer_id, order.id,
        f"You have successfully published the order: {order.id}."
    )
    # TODO: 发送通知到客户 inbox，可在此扩展  # TODO: Send notification to customer inbox, can be extended here
    return order

async def cancel_order(db: AsyncSession, customer_id: int, order_id: int):
    # 查找订单  # Find order
    result = await db.execute(select(Order).where(Order.id == order_id, Order.customer_id == customer_id))
    order = result.scalars().first()
    if not order:
        raise ValueError("Order not found or permission denied.")
    # 只有 pending 或 accepted 状态可取消  # Only orders with pending or accepted status can be cancelled
    if order.status not in [OrderStatus.pending, OrderStatus.accepted]:
        raise ValueError("The order can not be cancelled!")
    prev_status = order.status
    order.status = OrderStatus.cancelled
    order.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(order)
    # 通知客户
    await send_customer_notification(
        db, customer_id, order.id,
        f"You have successfully cancelled the order: {order.id}."
    )
    # 如果之前是 accepted，还要通知服务商
    if prev_status == OrderStatus.accepted and order.provider_id:
        await send_provider_notification(
            db, order.provider_id, order.id,
            f"Your order has been cancelled by the customer: {customer_id}."
        )
    return order

async def get_my_orders(db: AsyncSession, customer_id: int) -> List[Order]:
    result = await db.execute(
        select(Order)
        .where(
            Order.customer_id == customer_id,
            Order.status.in_([
                OrderStatus.pending,
                OrderStatus.accepted,
                OrderStatus.in_progress
            ])
        )
        .order_by(Order.created_at.desc())
    )
    return result.scalars().all()

async def get_order_detail(db: AsyncSession, customer_id: int, order_id: int) -> Order:
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id, Order.customer_id == customer_id)
    )
    return result.scalars().first()

async def get_order_history(db: AsyncSession, customer_id: int) -> List[Order]:
    """
    获取该用户所有历史订单（不限制订单状态）
    Get all historical orders of the user (no status restriction)
    """
    result = await db.execute(
        select(Order)
        .where(Order.customer_id == customer_id)
        .order_by(Order.created_at.desc())
    )
    return result.scalars().all()

class ReviewData:
    def __init__(self, order_id: int, stars: int, content: str = None):
        self.order_id = order_id
        self.stars = stars
        self.content = content

async def review_order(db: AsyncSession, customer_id: int, data: ReviewData):
    # 查找订单  # Find order
    result = await db.execute(
        select(Order).where(Order.id == data.order_id, Order.customer_id == customer_id)
    )
    order = result.scalars().first()
    if not order:
        raise ValueError("Order not found or permission denied.")
    # 仅允许已完成且已支付订单评价  # Only allow review for completed and paid orders
    if order.status != OrderStatus.completed or order.payment_status != PaymentStatus.paid:
        raise ValueError("Only completed and paid orders can be reviewed!")
    # 检查是否已评价  # Check if already reviewed
    review_result = await db.execute(
        select(Review).where(Review.order_id == data.order_id)
    )
    if review_result.scalars().first():
        raise ValueError("Order already reviewed!")
    # 创建评价  # Create review
    review = Review(
        order_id=data.order_id,
        customer_id=customer_id,
        provider_id=order.provider_id,
        stars=data.stars,
        content=data.content,
        created_at=datetime.now(UTC)
    )
    db.add(review)
    # 更新订单状态为 reviewed  # Update order status to reviewed
    order.status = OrderStatus.reviewed
    order.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(review)
    await db.refresh(order)
    # 通知客户
    await send_customer_notification(
        db, customer_id, order.id,
        f"You have successfully reviewed the order: {order.id}."
    )
    # 通知服务商
    if order.provider_id:
        await send_provider_notification(
            db, order.provider_id, order.id,
            f"The customer: {customer_id} has reviewed your order: {order.id}."
        )
    return review