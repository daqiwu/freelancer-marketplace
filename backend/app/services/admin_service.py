from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.models import Order, User, ProviderProfile, CustomerProfile

async def list_all_orders(db: AsyncSession, status: str = None):
	"""
	Fetch all orders from the database for admin view.
	"""
	stmt = select(Order)
	if status:
		stmt = stmt.where(Order.status == status)
	result = await db.execute(stmt)
	return result.scalars().all()

async def list_users_by_role(db: AsyncSession, role_id: int = None):
	"""
	Fetch users filtered by role_id (1=customer, 2=provider). If role_id is None, return all users.
	"""
	stmt = select(User)
	if role_id is not None:
		stmt = stmt.where(User.role_id == role_id)
	result = await db.execute(stmt)
	return result.scalars().all()

async def get_user_by_id(db: AsyncSession, id: int):
    """
    Fetch a single user by id.
    """
    return await db.get(User, id)

async def delete_user_by_id(db: AsyncSession, id: int):
    """
    Delete a user by id, including related provider/customer profiles and orders.
    """
    # Delete related provider profile first
    await db.execute(delete(ProviderProfile).where(ProviderProfile.id == id))
    # Delete related customer profile if needed
    await db.execute(delete(CustomerProfile).where(CustomerProfile.id == id))
    # Delete related orders (as customer)
    await db.execute(delete(Order).where(Order.customer_id == id))
    # Delete related orders (as provider)
    await db.execute(delete(Order).where(Order.provider_id == id))
    # Now delete the user
    await db.execute(delete(User).where(User.id == id))
    await db.commit()

