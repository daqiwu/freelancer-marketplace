# app/test/review_test.py
import pytest
from datetime import datetime
from app.models.models import Review


class TestReviews:
    """评价功能测试"""

    @pytest.mark.asyncio
    async def test_get_order_review(self, client, completed_order, customer_user, provider_user, db_session):
        """测试获取订单评价"""
        # 创建评价
        review = Review(
            order_id=completed_order.id,
            customer_id=customer_user.id,
            provider_id=provider_user.id,
            stars=5,
            content="Excellent service!",
            created_at=datetime.now()
        )
        db_session.add(review)
        await db_session.commit()
        
        response = client.get(f"/reviews/order/{completed_order.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["stars"] == 5

    @pytest.mark.asyncio
    async def test_get_provider_reviews(self, client, completed_order, customer_user, provider_user, db_session):
        """测试获取服务商所有评价"""
        # 创建评价
        review = Review(
            order_id=completed_order.id,
            customer_id=customer_user.id,
            provider_id=provider_user.id,
            stars=4,
            content="Good service",
            created_at=datetime.now()
        )
        db_session.add(review)
        await db_session.commit()
        
        response = client.get(f"/reviews/provider/{provider_user.id}")
        assert response.status_code == 200
        data = response.json()
        assert "average_rating" in data
        assert "reviews" in data

    def test_get_nonexistent_order_review(self, client):
        """测试获取不存在订单的评价"""
        response = client.get("/reviews/order/99999")
        assert response.status_code == 404

    def test_get_provider_reviews_no_reviews(self, client, provider_user):
        """测试获取无评价服务商"""
        response = client.get(f"/reviews/provider/{provider_user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["total_reviews"] == 0