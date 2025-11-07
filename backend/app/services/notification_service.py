from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import CustomerInbox, ProviderInbox


async def send_customer_notification(
    db: AsyncSession, customer_id: int, order_id: int, message: str
):
    notification = CustomerInbox(
        customer_id=customer_id,
        order_id=order_id,
        message=message,
        created_at=datetime.utcnow(),
        is_read=False,
    )
    db.add(notification)
    await db.commit()


async def send_provider_notification(
    db: AsyncSession, provider_id: int, order_id: int, message: str
):
    notification = ProviderInbox(
        provider_id=provider_id,
        order_id=order_id,
        message=message,
        created_at=datetime.utcnow(),
        is_read=False,
    )
    db.add(notification)
    await db.commit()
