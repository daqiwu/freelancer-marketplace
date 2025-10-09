# backend/app/models/models.py
from sqlalchemy import Column, Integer, BigInteger, String, Text, ForeignKey, Enum, DECIMAL, TIMESTAMP
from sqlalchemy.orm import relationship, declarative_base
import enum
import bcrypt

Base = declarative_base()

class OrderStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    in_progress = "in_progress"
    completed = "completed"
    reviewed = "reviewed"
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
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class CustomerProfile(Base):
    __tablename__ = "customer_profiles"
    id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    location = Column(Enum(LocationEnum), nullable=False)
    address = Column(String(255))
    budget_preference = Column(DECIMAL(10,2))
    
    user = relationship("User", back_populates="customer_profile")

class ProviderProfile(Base):
    __tablename__ = "provider_profiles"
    id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    skills = Column(Text)  # JSON格式字符串  # JSON format string
    experience_years = Column(Integer)
    hourly_rate = Column(DECIMAL(10,2))
    availability = Column(String(100))
    
    user = relationship("User", back_populates="provider_profile")

class Order(Base):
    __tablename__ = "orders"
    id = Column(BigInteger, primary_key=True)
    customer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    provider_id = Column(BigInteger, ForeignKey("users.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    price = Column(DECIMAL(10,2))
    location = Column(Enum(LocationEnum), nullable=False)
    address = Column(String(255))
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)