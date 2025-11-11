"""
Test configuration for integration tests in app/test directory.
"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.config import get_db
from app.models.models import Base, User, Role, Order, Review, Payment, CustomerInbox, ProviderInbox
from app.utils.security import get_password_hash
from datetime import datetime, timedelta

# 使用异步内存数据库进行测试
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)
TestingSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Global test session
_test_session = None


async def get_test_session():
    """Get the test database session"""
    global _test_session
    if _test_session is None:
        raise RuntimeError("Test session not initialized")
    return _test_session


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    """Setup and teardown test database"""
    global _test_session
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    _test_session = TestingSessionLocal()
    
    # Create roles
    roles = [
        Role(id=1, role_name="customer"),
        Role(id=2, role_name="provider"),
        Role(id=3, role_name="admin")
    ]
    _test_session.add_all(roles)
    await _test_session.commit()
    
    # Override dependency
    app.dependency_overrides[get_db] = get_test_session
    
    yield _test_session
    
    # Cleanup
    await _test_session.close()
    _test_session = None
    app.dependency_overrides.clear()
    
    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(setup_db):
    """Get database session for tests"""
    return setup_db


@pytest.fixture(scope="function")
def client(setup_db):
    """创建同步测试客户端 (用于简单测试)"""
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def customer_user(db_session):
    """创建测试客户用户"""
    user = User(
        id=100,  # Explicit ID for SQLite testing
        username="test_customer",
        email="customer@test.com",
        password_hash=get_password_hash("password123"),
        role_id=1,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def provider_user(db_session):
    """创建测试服务商用户"""
    user = User(
        id=200,  # Explicit ID for SQLite testing
        username="test_provider",
        email="provider@test.com",
        password_hash=get_password_hash("password123"),
        role_id=2,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db_session):
    """创建测试管理员用户"""
    user = User(
        id=300,  # Explicit ID for SQLite testing
        username="test_admin",
        email="admin@test.com",
        password_hash=get_password_hash("password123"),
        role_id=3,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def customer_token(client, customer_user):
    """获取客户Token"""
    response = client.post(
        "/auth/login",
        json={"email": "customer@test.com", "password": "password123"}
    )
    if response.status_code != 200:
        raise Exception(f"Login failed: {response.status_code}, {response.text}")
    return response.json()["access_token"]


@pytest.fixture
def provider_token(client, provider_user):
    """获取服务商Token"""
    response = client.post(
        "/auth/login",
        json={"email": "provider@test.com", "password": "password123"}
    )
    if response.status_code != 200:
        raise Exception(f"Login failed: {response.status_code}, {response.text}")
    return response.json()["access_token"]


@pytest.fixture
def admin_token(client, admin_user):
    """获取管理员Token"""
    response = client.post(
        "/auth/login",
        json={"email": "admin@test.com", "password": "password123"}
    )
    if response.status_code != 200:
        raise Exception(f"Login failed: {response.status_code}, {response.text}")
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def sample_order(db_session, customer_user):
    """创建示例订单"""
    from app.models.models import ServiceType, OrderStatus
    now = datetime.now()
    order = Order(
        id=1000,  # Explicit ID for SQLite testing
        title="Test Order",
        description="Test Description",
        service_type=ServiceType.cleaning_repair,
        price=100.0,
        location="NORTH",
        address="123 Test St",
        service_start_time=now + timedelta(days=1),
        service_end_time=now + timedelta(days=1, hours=2),
        status=OrderStatus.pending_review,
        customer_id=customer_user.id,
        created_at=now,
        updated_at=now
    )
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)
    return order


@pytest_asyncio.fixture
async def published_order(db_session, customer_user):
    """创建已发布订单"""
    from app.models.models import ServiceType, OrderStatus
    now = datetime.now()
    order = Order(
        id=2000,  # Explicit ID for SQLite testing
        title="Published Order",
        description="Test Description",
        service_type=ServiceType.cleaning_repair,
        price=150.0,
        location="SOUTH",
        address="456 Test Ave",
        service_start_time=now + timedelta(days=2),
        service_end_time=now + timedelta(days=2, hours=3),
        status=OrderStatus.published,
        customer_id=customer_user.id,
        created_at=now,
        updated_at=now
    )
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)
    return order


@pytest_asyncio.fixture
async def accepted_order(db_session, customer_user, provider_user):
    """创建已接受订单"""
    from app.models.models import ServiceType, OrderStatus
    now = datetime.now()
    order = Order(
        id=3000,  # Explicit ID for SQLite testing
        title="Accepted Order",
        description="Test Description",
        service_type=ServiceType.it_technology,
        price=200.0,
        location="EAST",
        address="789 Test Blvd",
        service_start_time=now + timedelta(days=3),
        service_end_time=now + timedelta(days=3, hours=4),
        status=OrderStatus.accepted,
        customer_id=customer_user.id,
        provider_id=provider_user.id,
        created_at=now,
        updated_at=now
    )
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)
    return order


@pytest_asyncio.fixture
async def completed_order(db_session, customer_user, provider_user):
    """创建已完成订单"""
    from app.models.models import ServiceType, OrderStatus
    now = datetime.now()
    order = Order(
        id=4000,  # Explicit ID for SQLite testing
        title="Completed Order",
        description="Test Description",
        service_type=ServiceType.life_health,
        price=250.0,
        location="WEST",
        address="101 Test Road",
        service_start_time=now - timedelta(days=1),
        service_end_time=now - timedelta(hours=20),
        status=OrderStatus.completed,
        customer_id=customer_user.id,
        provider_id=provider_user.id,
        created_at=now,
        updated_at=now
    )
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)
    return order
