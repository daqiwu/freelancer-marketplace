from datetime import UTC, datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import get_db
from app.dependencies import get_current_user
from app.models.models import Order, OrderStatus, PaymentStatus, Review

review_router = APIRouter(prefix="/reviews", tags=["reviews"])


class CreateReviewRequest(BaseModel):
    order_id: int
    stars: int
    content: str = None


class CreateReviewResponse(BaseModel):
    review_id: int
    order_id: int
    stars: int
    content: str = None
    message: str


class ProviderRatingResponse(BaseModel):
    provider_id: int
    average_rating: float
    total_reviews: int


@review_router.post(
    "/", response_model=CreateReviewResponse, status_code=status.HTTP_201_CREATED
)
async def create_review(
    data: CreateReviewRequest,
    current_user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建评价（需要认证）"""
    # 检查该订单是否已评价
    result = await db.execute(select(Review).where(Review.order_id == data.order_id))
    existing = result.scalars().first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This order has already been reviewed",
        )

    # 获取订单信息
    order_result = await db.execute(select(Order).where(Order.id == data.order_id))
    order = order_result.scalars().first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found or you don't have permission to review this order",
        )

    # 验证订单属于当前用户（customer）
    if order.customer_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only review your own orders",
        )

    # 验证订单已完成且已支付
    if order.status != OrderStatus.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only review completed orders",
        )

    if order.payment_status != PaymentStatus.paid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only review paid orders",
        )

    # 创建评价
    new_review = Review(
        order_id=data.order_id,
        customer_id=order.customer_id,
        provider_id=order.provider_id,
        stars=data.stars,
        content=data.content,
        created_at=datetime.now(UTC),
    )

    db.add(new_review)
    await db.commit()
    await db.refresh(new_review)

    return CreateReviewResponse(
        review_id=new_review.id,
        order_id=new_review.order_id,
        stars=new_review.stars,
        content=new_review.content,
        message="Review created successfully.",
    )


@review_router.get("/provider/me/rating", response_model=ProviderRatingResponse)
async def get_my_provider_rating(
    current_user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """获取当前 Provider 的评分（需要认证）"""
    from sqlalchemy import func

    result = await db.execute(
        select(func.avg(Review.stars), func.count(Review.id)).where(
            Review.provider_id == current_user_id
        )
    )
    avg_rating, total_reviews = result.first()

    return ProviderRatingResponse(
        provider_id=current_user_id,
        average_rating=float(avg_rating) if avg_rating else 0.0,
        total_reviews=total_reviews if total_reviews else 0,
    )


@review_router.get("/provider/me/reviews", response_model=List[dict])
async def get_my_provider_reviews(
    current_user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """获取当前 Provider 的所有评价（需要认证）"""
    result = await db.execute(
        select(Review).where(Review.provider_id == current_user_id)
    )
    reviews = result.scalars().all()

    return [
        {
            "order_id": r.order_id,
            "customer_id": r.customer_id,
            "stars": r.stars,
            "content": r.content,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reviews
    ]


@review_router.get(
    "/provider/{provider_id}/rating", response_model=ProviderRatingResponse
)
async def get_provider_rating(provider_id: int, db: AsyncSession = Depends(get_db)):
    """获取服务商评分（公开接口）"""
    from sqlalchemy import func

    result = await db.execute(
        select(func.avg(Review.stars), func.count(Review.id)).where(
            Review.provider_id == provider_id
        )
    )
    avg_rating, total_reviews = result.first()

    return ProviderRatingResponse(
        provider_id=provider_id,
        average_rating=float(avg_rating) if avg_rating else 0.0,
        total_reviews=total_reviews if total_reviews else 0,
    )


@review_router.get("/provider/{provider_id}", response_model=List[dict])
async def get_provider_reviews(provider_id: int, db: AsyncSession = Depends(get_db)):
    """获取服务商的所有评价（公开接口）"""
    result = await db.execute(select(Review).where(Review.provider_id == provider_id))
    reviews = result.scalars().all()

    return [
        {
            "order_id": r.order_id,
            "customer_id": r.customer_id,
            "stars": r.stars,
            "content": r.content,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reviews
    ]


@review_router.get("/order/{order_id}", response_model=dict)
async def get_order_review(order_id: int, db: AsyncSession = Depends(get_db)):
    """根据订单ID获取评价（公开接口）"""
    result = await db.execute(select(Review).where(Review.order_id == order_id))
    review = result.scalars().first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found for this order",
        )

    return {
        "order_id": review.order_id,
        "customer_id": review.customer_id,
        "provider_id": review.provider_id,
        "stars": review.stars,
        "content": review.content,
        "created_at": review.created_at.isoformat() if review.created_at else None,
    }
