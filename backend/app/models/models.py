# backend/app/models/models.py
from sqlalchemy import Column, Integer, BigInteger, String, Text, ForeignKey, Enum, DECIMAL, TIMESTAMP, DateTime, Boolean
from sqlalchemy.orm import relationship, declarative_base
import enum
import bcrypt
from datetime import datetime

Base = declarative_base()

class ServiceType(enum.Enum):
    cleaning_repair = "cleaning_repair"
    it_technology = "it_technology"
    education_training = "education_training"
    life_health = "life_health"
    design_consulting = "design_consulting"
    other = "other"

class OrderStatus(enum.Enum):
    pending_review = "pending_review"
    pending = "pending"
    accepted = "accepted"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

class LocationEnum(enum.Enum):
    NORTH = "NORTH"
    SOUTH = "SOUTH"
    EAST = "EAST"
    WEST = "WEST"
    MID = "MID"

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    role_name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    role = relationship("Role")
    customer_profile = relationship("CustomerProfile", uselist=False, back_populates="user")
    provider_profile = relationship("ProviderProfile", uselist=False, back_populates="user")

    def verify_password(self, password: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        except Exception as e:
            print(f"Password verification error: {e}")
            return False

class CustomerProfile(Base):
    __tablename__ = "customer_profiles"
    id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    location = Column(Enum(LocationEnum), nullable=False)
    address = Column(String(255))
    budget_preference = Column(DECIMAL(10,2))
    balance = Column(DECIMAL(10,2), default=0)  # 账户余额  # Account balance
    
    user = relationship("User", back_populates="customer_profile")

class ProviderProfile(Base):
    __tablename__ = "provider_profiles"
    id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    skills = Column(Text)  # JSON格式字符串  # JSON format string
    experience_years = Column(Integer)
    hourly_rate = Column(DECIMAL(10,2))
    availability = Column(String(100))
    
    user = relationship("User", back_populates="provider_profile")

class PaymentStatus(enum.Enum):
    unpaid = "unpaid"  
    paid = "paid"     

class Order(Base):
    __tablename__ = "orders"
    id = Column(BigInteger, primary_key=True)
    customer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    provider_id = Column(BigInteger, ForeignKey("users.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    service_type = Column(Enum(ServiceType), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending_review, nullable=False)
    price = Column(DECIMAL(10,2), nullable=False)
    location = Column(Enum(LocationEnum), nullable=False)
    address = Column(String(255))
    service_start_time = Column(DateTime)
    service_end_time = Column(DateTime)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.unpaid, nullable=False)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

class PaymentMethodEnum(enum.Enum):
    simulated = "simulated"

class PaymentStatusEnum(enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"

class Payment(Base):
    __tablename__ = "payments"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False, unique=True)
    customer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    provider_id = Column(BigInteger, ForeignKey("users.id"))
    amount = Column(DECIMAL(10,2), nullable=False)
    payment_method = Column(Enum(PaymentMethodEnum), default=PaymentMethodEnum.simulated)
    status = Column(Enum(PaymentStatusEnum), default=PaymentStatusEnum.pending)
    transaction_id = Column(String(255), unique=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

class Review(Base):
    __tablename__ = "reviews"
    id = Column(BigInteger, primary_key=True)  # 评价ID  # Review ID
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False, unique=True)  # 订单ID (唯一)  # Order ID (unique)
    customer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)  # 客户ID  # Customer ID
    provider_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)  # 服务商ID  # Provider ID
    stars = Column(Integer, nullable=False, default=5)  # 星级（1-5，默认5）  # Stars (1-5, default 5)
    content = Column(Text, nullable=True)  # 评价内容  # Review content
    created_at = Column(TIMESTAMP)  # 创建时间  # Created time

    # 关联订单  # Relationship to order
    order = relationship("Order", backref="review")
    # 关联客户  # Relationship to customer
    customer = relationship("User", foreign_keys=[customer_id])
    # 关联服务商  # Relationship to provider
    provider = relationship("User", foreign_keys=[provider_id])

class CustomerInbox(Base):
    __tablename__ = "customer_inbox"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    customer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=True)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)

class ProviderInbox(Base):
    __tablename__ = "provider_inbox"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    provider_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=True)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)

class SecurityIssueType(enum.Enum):
    """Security issue classification types"""
    SCA = "SCA"  # Software Composition Analysis
    SAST = "SAST"  # Static Application Security Testing
    DAST = "DAST"  # Dynamic Application Security Testing
    UNKNOWN = "UNKNOWN"

class SecuritySeverity(enum.Enum):
    """Security issue severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class SecurityIssueStatus(enum.Enum):
    """Security issue status"""
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"

class SecurityIssue(Base):
    """Security issue tracking and classification"""
    __tablename__ = "security_issues"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    
    # AI Classification Results
    issue_type = Column(Enum(SecurityIssueType), nullable=False)
    severity = Column(Enum(SecuritySeverity), nullable=False)
    confidence_score = Column(DECIMAL(5, 2), nullable=False)
    
    # Issue Details
    affected_component = Column(String(500))
    vulnerability_id = Column(String(100))
    
    # Classification Details
    detection_method = Column(String(100))
    tags = Column(Text)
    
    # Remediation
    remediation_suggestion = Column(Text)
    remediation_priority = Column(Integer)
    estimated_effort = Column(String(50))
    
    # Tracking
    status = Column(Enum(SecurityIssueStatus), default=SecurityIssueStatus.OPEN)
    reported_by = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(BigInteger, ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    # Relationships
    reporter = relationship("User", foreign_keys=[reported_by])
    assignee = relationship("User", foreign_keys=[assigned_to])