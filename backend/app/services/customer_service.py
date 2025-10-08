from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Order, OrderStatus
from datetime import datetime, UTC
from sqlalchemy.future import select

async def publish_order(db: AsyncSession, customer_id: int, data):
    # 数据校验已在 Pydantic 层完成
    order = Order(
        customer_id=customer_id,
        title=data.title,
        description=data.description,
        price=data.price,
        location=data.location,
        address=data.address,
        status=OrderStatus.pending,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    # TODO: 发送通知到客户 inbox，可在此扩展
    return order

async def cancel_order(db: AsyncSession, customer_id: int, order_id: int):
    # 查找订单
    result = await db.execute(select(Order).where(Order.id == order_id, Order.customer_id == customer_id))
    order = result.scalars().first()
    if not order:
        raise ValueError("Order not found or permission denied.")
    # 只有 pending 或 accepted 状态可取消
    if order.status not in [OrderStatus.pending, OrderStatus.accepted]:
        raise ValueError("The order can not be cancelled!")
    order.status = OrderStatus.cancelled
    order.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(order)
    # TODO: 发送通知到客户和服务商 inbox
    return order