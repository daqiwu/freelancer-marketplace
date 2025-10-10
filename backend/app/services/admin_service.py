
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Order

async def list_all_orders(db: AsyncSession):
	result = await db.execute(select(Order))
	return result.scalars().all()
