from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_db
from app.models.models import CustomerInbox, ProviderInbox
from typing import List

notification_router = APIRouter(prefix="/notification", tags=["notification"])

@notification_router.get("/customer_inbox/{customer_id}", response_model=List[dict])
async def get_customer_inbox(customer_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        CustomerInbox.__table__.select().where(CustomerInbox.customer_id == customer_id).order_by(CustomerInbox.created_at.desc())
    )
    return [dict(row) for row in result.fetchall()]

@notification_router.get("/provider_inbox/{provider_id}", response_model=List[dict])
async def get_provider_inbox(provider_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        ProviderInbox.__table__.select().where(ProviderInbox.provider_id == provider_id).order_by(ProviderInbox.created_at.desc())
    )
    return [dict(row) for row in result.fetchall()]