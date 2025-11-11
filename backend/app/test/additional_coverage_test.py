# app/test/additional_coverage_test.py
"""
Additional tests to increase code coverage for low-coverage modules
针对低覆盖率模块的额外测试
"""
import pytest
from datetime import datetime, timedelta, UTC
from app.models.models import (
    User, Order, Review, ServiceType, OrderStatus, 
    LocationEnum, CustomerProfile, ProviderProfile, Role
)
from app.services.security_classifier_service import SecurityClassifierService


class TestSecurityClassifierAdditional:
    """安全分类器额外测试"""
    
    def test_classify_issue_sca(self):
        """测试 SCA 问题分类"""
        service = SecurityClassifierService()
        result = service.classify_issue(
            "CVE-2023-1234 vulnerability found",
            "This package has a known security vulnerability"
        )
        assert result["issue_type"] == "SCA"
        assert result["severity"] in ["critical", "high", "medium", "low"]
    
    def test_classify_issue_sast(self):
        """测试 SAST 问题分类"""
        service = SecurityClassifierService()
        result = service.classify_issue(
            "SQL Injection vulnerability",
            "User input is not properly sanitized"
        )
        assert result["issue_type"] == "SAST"
    
    def test_classify_issue_dast(self):
        """测试 DAST 问题分类"""
        service = SecurityClassifierService()
        result = service.classify_issue(
            "Runtime vulnerability detected during penetration testing",
            "DAST scan found authentication bypass vulnerability"
        )
        assert result["issue_type"] == "DAST"
    
    def test_classify_issue_default(self):
        """测试默认分类"""
        service = SecurityClassifierService()
        result = service.classify_issue(
            "Unknown issue",
            "Some random problem"
        )
        assert result["issue_type"] in ["SCA", "SAST", "DAST", "OTHER"]
    
    def test_classify_issue_with_multiple_keywords(self):
        """测试多个关键词的问题分类"""
        service = SecurityClassifierService()
        result = service.classify_issue(
            "SQL injection and XSS vulnerability",
            "Multiple security issues found"
        )
        assert result["issue_type"] in ["SAST", "DAST"]
        assert result["type"] in ["sast", "dast"]
    
    def test_severity_levels(self):
        """测试不同严重级别"""
        service = SecurityClassifierService()
        
        # Critical severity
        result1 = service.classify_issue(
            "Critical SQL injection",
            "Critical vulnerability with high risk"
        )
        # Just check it returns a valid severity
        assert result1["severity"] in ["critical", "high", "medium", "low"]
        
        # Medium severity
        result2 = service.classify_issue(
            "Medium warning",
            "This is a medium priority issue"
        )
        assert result2["severity"] in ["critical", "high", "medium", "low"]


class TestModelsAdditional:
    """数据模型额外测试"""
    
    @pytest.mark.asyncio
    async def test_user_creation(self, db_session):
        """测试用户创建"""
        user = User(
            id=6000,
            username="test_new_user",
            email="newuser@test.com",
            password_hash="hashed_password",
            role_id=1,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.id == 6000
        assert user.username == "test_new_user"
        assert user.email == "newuser@test.com"
    
    @pytest.mark.asyncio
    async def test_order_status_transitions(self, db_session, customer_user):
        """测试订单状态转换"""
        order = Order(
            id=7000,
            title="Status Test Order",
            description="Testing status changes",
            service_type=ServiceType.it_technology,
            price=150.0,
            location="NORTH",
            address="Test Address",
            service_start_time=datetime.now() + timedelta(days=1),
            service_end_time=datetime.now() + timedelta(days=1, hours=2),
            status=OrderStatus.pending_review,
            customer_id=customer_user.id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(order)
        await db_session.commit()
        
        # Test status transition: pending_review -> published
        order.status = OrderStatus.published
        await db_session.commit()
        await db_session.refresh(order)
        assert order.status == OrderStatus.published
        
        # Test status transition: published -> accepted
        order.status = OrderStatus.accepted
        await db_session.commit()
        await db_session.refresh(order)
        assert order.status == OrderStatus.accepted
    
    @pytest.mark.asyncio
    async def test_review_creation(self, db_session, customer_user, provider_user, completed_order):
        """测试评价创建"""
        review = Review(
            order_id=completed_order.id,
            customer_id=customer_user.id,
            provider_id=provider_user.id,
            stars=5,
            content="Excellent work!",
            created_at=datetime.now()
        )
        db_session.add(review)
        await db_session.commit()
        await db_session.refresh(review)
        
        assert review.stars == 5
        assert review.content == "Excellent work!"
        assert review.order_id == completed_order.id


class TestEnumTypes:
    """枚举类型测试"""
    
    def test_service_type_enum(self):
        """测试服务类型枚举"""
        assert ServiceType.cleaning_repair.value == "cleaning_repair"
        assert ServiceType.it_technology.value == "it_technology"
        assert ServiceType.education_training.value == "education_training"
        assert ServiceType.life_health.value == "life_health"
        assert ServiceType.design_consulting.value == "design_consulting"
        assert ServiceType.other.value == "other"
    
    def test_order_status_enum(self):
        """测试订单状态枚举"""
        assert OrderStatus.pending_review.value == "pending_review"
        assert OrderStatus.pending.value == "pending"
        assert OrderStatus.published.value == "published"
        assert OrderStatus.accepted.value == "accepted"
        assert OrderStatus.in_progress.value == "in_progress"
        assert OrderStatus.completed.value == "completed"
        assert OrderStatus.cancelled.value == "cancelled"
        assert OrderStatus.rejected.value == "rejected"
    
    def test_location_enum(self):
        """测试位置枚举"""
        assert LocationEnum.NORTH.value == "NORTH"
        assert LocationEnum.SOUTH.value == "SOUTH"
        assert LocationEnum.EAST.value == "EAST"
        assert LocationEnum.WEST.value == "WEST"
        assert LocationEnum.CENTRAL.value == "CENTRAL"


class TestUserPasswordVerification:
    """用户密码验证测试"""
    
    @pytest.mark.asyncio
    async def test_password_verification_success(self, db_session):
        """测试密码验证成功"""
        from app.utils.security import get_password_hash
        
        user = User(
            id=8000,
            username="password_test_user",
            email="passtest@test.com",
            password_hash=get_password_hash("testpassword123"),
            role_id=1,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Test password verification
        assert user.verify_password("testpassword123") is True
    
    @pytest.mark.asyncio
    async def test_password_verification_failure(self, db_session):
        """测试密码验证失败"""
        from app.utils.security import get_password_hash
        
        user = User(
            id=9000,
            username="password_test_user2",
            email="passtest2@test.com",
            password_hash=get_password_hash("correctpassword"),
            role_id=1,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Test password verification with wrong password
        assert user.verify_password("wrongpassword") is False


class TestOrderBusinessLogic:
    """订单业务逻辑测试"""
    
    @pytest.mark.asyncio
    async def test_order_price_validation(self, db_session, customer_user):
        """测试订单价格验证"""
        # Create an order with valid price
        order = Order(
            id=10000,
            title="Price Test Order",
            description="Testing price",
            service_type=ServiceType.cleaning_repair,
            price=50.0,
            location="NORTH",
            address="Test Address",
            service_start_time=datetime.now() + timedelta(days=1),
            service_end_time=datetime.now() + timedelta(days=1, hours=2),
            status=OrderStatus.published,
            customer_id=customer_user.id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(order)
        await db_session.commit()
        await db_session.refresh(order)
        
        assert order.price == 50.0
        assert order.price > 0
    
    @pytest.mark.asyncio
    async def test_order_time_validation(self, db_session, customer_user):
        """测试订单时间验证"""
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=3)
        
        order = Order(
            id=11000,
            title="Time Test Order",
            description="Testing time",
            service_type=ServiceType.it_technology,
            price=100.0,
            location="SOUTH",
            address="Test Address",
            service_start_time=start_time,
            service_end_time=end_time,
            status=OrderStatus.published,
            customer_id=customer_user.id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db_session.add(order)
        await db_session.commit()
        await db_session.refresh(order)
        
        assert order.service_end_time > order.service_start_time
        duration = order.service_end_time - order.service_start_time
        assert duration.total_seconds() > 0
