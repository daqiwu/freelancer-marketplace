from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.models import Order, User, ProviderProfile, CustomerProfile, Review, CustomerInbox, ProviderInbox

async def list_all_orders(db: AsyncSession, status: str = None, page: int = 1, limit: int = 20, sort_by: str = "created_at", order: str = "desc"):
    """
    Fetch all orders from the database for admin view, with pagination and sorting.
    """
    stmt = select(Order)
    if status:
        stmt = stmt.where(Order.status == status)
    # Sorting
    sort_column = getattr(Order, sort_by, None)
    if sort_column is not None:
        if order == "desc":
            stmt = stmt.order_by(sort_column.desc())
        else:
            stmt = stmt.order_by(sort_column.asc())
    # Pagination
    stmt = stmt.offset((page - 1) * limit).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def list_users_by_role(db: AsyncSession, role_id: int = None, page: int = 1, limit: int = 20, sort_by: str = "created_at", order: str = "desc"):
    """
    Fetch users filtered by role_id (1=customer, 2=provider), with pagination and sorting. If role_id is None, return all users.
    """
    stmt = select(User)
    if role_id is not None:
        stmt = stmt.where(User.role_id == role_id)
    # Sorting
    sort_column = getattr(User, sort_by, None)
    if sort_column is not None:
        if order == "desc":
            stmt = stmt.order_by(sort_column.desc())
        else:
            stmt = stmt.order_by(sort_column.asc())
    # Pagination
    stmt = stmt.offset((page - 1) * limit).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_user_by_id(db: AsyncSession, id: int):
    """
    Fetch a single user by id.
    """
    return await db.get(User, id)

async def delete_user_by_id(db: AsyncSession, id: int):
    """
    Delete a user by id, including related provider/customer profiles, orders, and reviews.
    """
    # Delete related provider profile first
    await db.execute(delete(ProviderProfile).where(ProviderProfile.id == id))
    # Delete related customer profile if needed
    await db.execute(delete(CustomerProfile).where(CustomerProfile.id == id))

    # Find all order ids for this user (as customer or provider)
    order_ids_result = await db.execute(
        select(Order.id).where((Order.customer_id == id) | (Order.provider_id == id))
    )
    order_ids = [row[0] for row in order_ids_result.fetchall()]

    # Delete provider_inbox and customer_inbox rows referencing these orders
    if order_ids:
        await db.execute(delete(ProviderInbox).where(ProviderInbox.order_id.in_(order_ids)))
        await db.execute(delete(CustomerInbox).where(CustomerInbox.order_id.in_(order_ids)))
        # Delete reviews referencing these orders
        await db.execute(delete(Review).where(Review.order_id.in_(order_ids)))

    # Delete related orders (as customer)
    await db.execute(delete(Order).where(Order.customer_id == id))
    # Delete related orders (as provider)
    await db.execute(delete(Order).where(Order.provider_id == id))
    # Now delete the user
    await db.execute(delete(User).where(User.id == id))
    await db.commit()

