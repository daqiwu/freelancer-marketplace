from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Review, Order, OrderStatus, PaymentStatus
from datetime import datetime, UTC
from sqlalchemy.future import select
from typing import List
from app.services.notification_service import send_customer_notification, send_provider_notification

async def publish_order(db: AsyncSession, customer_id: int, data):
    # 数据校验已在 Pydantic 层完成  # Data validation is done in Pydantic layer
    from datetime import datetime as dt
    
    # 解析时间字符串
    service_start_time = None
    service_end_time = None
    if data.service_start_time:
        service_start_time = dt.fromisoformat(data.service_start_time.replace('Z', '+00:00'))
    if data.service_end_time:
        service_end_time = dt.fromisoformat(data.service_end_time.replace('Z', '+00:00'))
    
    order = Order(
        customer_id=customer_id,
        title=data.title,
        description=data.description,
        service_type=data.service_type,
        price=data.price,
        location=data.location,
        address=data.address,
        service_start_time=service_start_time,
        service_end_time=service_end_time,
        status=OrderStatus.pending_review,  # 默认状态改为 pending_review
        payment_status=PaymentStatus.unpaid,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    # 通知客户
    await send_customer_notification(
        db, customer_id, order.id,
        "您的订单已发布，等待管理员审核"
    )
    return order

async def cancel_order(db: AsyncSession, customer_id: int, order_id: int):
    # 查找订单  # Find order
    result = await db.execute(select(Order).where(Order.id == order_id, Order.customer_id == customer_id))
    order = result.scalars().first()
    if not order:
        raise ValueError("Order not found or permission denied.")
    # 允许取消 pending_review 和 pending 状态的订单
    if order.status not in [OrderStatus.pending_review, OrderStatus.pending]:
        raise ValueError("The order can not be cancelled!")
    prev_status = order.status
    order.status = OrderStatus.cancelled
    order.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(order)
    # 通知客户
    await send_customer_notification(
        db, customer_id, order.id,
        f"订单已取消"
    )
    # 如果订单已被接单，通知服务商
    if order.provider_id:
        await send_provider_notification(
            db, order.provider_id, order.id,
            f"订单 #{order_id} 已被客户取消"
        )
    return order

async def get_my_orders(db: AsyncSession, customer_id: int) -> List[Order]:
    result = await db.execute(
        select(Order)
        .where(
            Order.customer_id == customer_id,
            Order.status.in_([
                OrderStatus.pending_review,
                OrderStatus.pending,
                OrderStatus.accepted,
                OrderStatus.in_progress
            ])
        )
        .order_by(Order.created_at.desc())
    )
    return result.scalars().all()

async def get_order_detail(db: AsyncSession, customer_id: int, order_id: int) -> dict:
    """
    获取订单详情。如果订单已评价，则返回review内容，否则review部分为空。
    """
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.customer_id == customer_id)
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
            "created_at": str(review.created_at)
        }

    return {
        "id": order.id,
        "customer_id": order.customer_id,
        "provider_id": order.provider_id,
        "title": order.title,
        "description": order.description,
        "service_type": order.service_type.value,
        "status": order.status.value,
        "price": float(order.price),
        "location": order.location.value,
        "address": order.address,
        "service_start_time": str(order.service_start_time) if order.service_start_time else None,
        "service_end_time": str(order.service_end_time) if order.service_end_time else None,
        "payment_status": order.payment_status.value,
        "created_at": str(order.created_at),
        "updated_at": str(order.updated_at),
        "review": review_data
    }

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
    if order.payment_status != PaymentStatus.paid:
        raise ValueError("Only paid orders can be reviewed!")
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
    await db.commit()
    await db.refresh(review)
    # 通知服务商
    if order.provider_id:
        await send_provider_notification(
            db, order.provider_id, order.id,
            f"客户对订单 #{order.id} 进行了评价（{data.stars}星）"
        )
    return review