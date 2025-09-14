# backend/app/models/models.py
from sqlalchemy import Column, Integer, BigInteger, String, Text, ForeignKey, Enum, DECIMAL, TIMESTAMP
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

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

class CustomerProfile(Base):
    __tablename__ = "customer_profiles"
    id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    company_name = Column(String(255))
    location = Column(String(255))
    budget_preference = Column(DECIMAL(10,2))
    
    user = relationship("User", back_populates="customer_profile")

class ProviderProfile(Base):
    __tablename__ = "provider_profiles"
    id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    skills = Column(Text)  # JSON 格式字符串
    experience_years = Column(Integer)
    hourly_rate = Column(DECIMAL(10,2))
    availability = Column(String(100))
    
    user = relationship("User", back_populates="provider_profile")

class OrderStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    completed = "completed"
    cancelled = "cancelled"

class Order(Base):
    __tablename__ = "orders"
    id = Column(BigInteger, primary_key=True)
    customer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    provider_id = Column(BigInteger, ForeignKey("users.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
