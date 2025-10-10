from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_db
from app.models.models import CustomerInbox, ProviderInbox
from app.dependencies import get_current_user

notification_router = APIRouter(prefix="/notification", tags=["notification"])

@notification_router.get("/customer_inbox")
async def get_customer_inbox(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    result = await db.execute(
        CustomerInbox.__table__.select().where(CustomerInbox.customer_id == current_user_id).order_by(CustomerInbox.created_at.desc())
    )
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]

@notification_router.get("/provider_inbox")
async def get_provider_inbox(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    result = await db.execute(
        ProviderInbox.__table__.select().where(ProviderInbox.provider_id == current_user_id).order_by(ProviderInbox.created_at.desc())
    )
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]