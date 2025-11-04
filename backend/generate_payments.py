"""
Script to generate payment records based on existing orders
Standalone version with minimal dependencies
"""

import asyncio
import enum
import hashlib
import os
import random
from datetime import datetime, timedelta

from dotenv import load_dotenv
from sqlalchemy import (
    DECIMAL,
    TIMESTAMP,
    BigInteger,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables
load_dotenv()

# Define models
Base = declarative_base()


class OrderStatus(enum.Enum):
    pending_review = "pending_review"
    pending = "pending"
    accepted = "accepted"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class PaymentStatus(enum.Enum):
    unpaid = "unpaid"
    paid = "paid"


class PaymentMethodEnum(enum.Enum):
    simulated = "simulated"


class PaymentStatusEnum(enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)


class Order(Base):
    __tablename__ = "orders"
    id = Column(BigInteger, primary_key=True)
    customer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    provider_id = Column(BigInteger, ForeignKey("users.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(
        Enum(OrderStatus), default=OrderStatus.pending_review, nullable=False
    )
    price = Column(DECIMAL(10, 2), nullable=False)
    payment_status = Column(
        Enum(PaymentStatus), default=PaymentStatus.unpaid, nullable=False
    )
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)


class Payment(Base):
    __tablename__ = "payments"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False, unique=True)
    customer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    provider_id = Column(BigInteger, ForeignKey("users.id"))
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(
        Enum(PaymentMethodEnum), default=PaymentMethodEnum.simulated
    )
    status = Column(Enum(PaymentStatusEnum), default=PaymentStatusEnum.pending)
    transaction_id = Column(String(255), unique=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)


def generate_transaction_id(order_id, customer_id, timestamp):
    """Generate a unique transaction ID"""
    data = f"{order_id}_{customer_id}_{timestamp}_{random.randint(1000, 9999)}"
    hash_obj = hashlib.sha256(data.encode())
    return f"TXN{hash_obj.hexdigest()[:20].upper()}"


def get_database_url():
    """Get database URL from environment"""
    aws_url = os.getenv("AWS_DATABASE_URL")
    if aws_url:
        return aws_url.strip()
    use_docker = os.getenv("USE_DOCKER", "false").lower() == "true"
    if use_docker:
        return os.getenv(
            "DOCKER_DATABASE_URL",
            "mysql+aiomysql://root:password@db:3306/freelancer_marketplace",
        ).strip()
    return os.getenv(
        "LOCAL_DATABASE_URL", "sqlite+aiosqlite:///./freelancer.db"
    ).strip()


async def generate_payments():
    """Generate payment records based on existing orders"""
    database_url = get_database_url()
    print(f"Using database: {database_url}")

    engine = create_async_engine(database_url, echo=False)
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with AsyncSessionLocal() as db:
        try:
            # Get all orders
            result = await db.execute(select(Order))
            all_orders = result.scalars().all()

            if not all_orders:
                print(
                    "Error: No orders found in database. Please generate orders first."
                )
                return

            print(f"Found {len(all_orders)} orders in database")

            # Check existing payments to avoid duplicates
            existing_payments_result = await db.execute(select(Payment))
            existing_payments = existing_payments_result.scalars().all()
            existing_order_ids = {p.order_id for p in existing_payments}

            print(f"Found {len(existing_order_ids)} existing payment records")

            # List to store generated payment info
            payments_info = []
            skipped_count = 0

            # Generate payments for orders
            for order in all_orders:
                # Skip if payment already exists for this order
                if order.id in existing_order_ids:
                    skipped_count += 1
                    continue

                # Determine if we should create a payment for this order
                should_create_payment = False
                payment_status_enum = PaymentStatusEnum.pending

                # Orders with paid payment_status should have completed payments
                if order.payment_status == PaymentStatus.paid:
                    should_create_payment = True
                    payment_status_enum = PaymentStatusEnum.completed

                # Orders that are accepted or in_progress might have pending payments
                elif order.status in [OrderStatus.accepted, OrderStatus.in_progress]:
                    if random.random() < 0.7:  # 70% chance of creating payment
                        should_create_payment = True
                        if random.random() < 0.3:  # 30% chance it's completed
                            payment_status_enum = PaymentStatusEnum.completed
                        else:
                            payment_status_enum = PaymentStatusEnum.pending

                # Pending orders might have pending payments
                elif order.status == OrderStatus.pending:
                    if random.random() < 0.3:  # 30% chance of creating payment
                        should_create_payment = True
                        payment_status_enum = PaymentStatusEnum.pending

                # Small chance of failed payments
                if (
                    should_create_payment and random.random() < 0.05
                ):  # 5% chance of failure
                    payment_status_enum = PaymentStatusEnum.failed

                if not should_create_payment:
                    continue

                # Generate transaction ID
                timestamp = datetime.utcnow().timestamp()
                transaction_id = generate_transaction_id(
                    order.id, order.customer_id, timestamp
                )

                # Create payment record
                new_payment = Payment(
                    order_id=order.id,
                    customer_id=order.customer_id,
                    provider_id=order.provider_id,
                    amount=order.price,
                    payment_method=PaymentMethodEnum.simulated,
                    status=payment_status_enum,
                    transaction_id=transaction_id,
                    created_at=(
                        order.created_at if order.created_at else datetime.utcnow()
                    ),
                    updated_at=datetime.utcnow(),
                )

                db.add(new_payment)
                await db.flush()  # Get the payment ID

                # Store payment info
                payments_info.append(
                    {
                        "payment_id": new_payment.id,
                        "order_id": order.id,
                        "customer_id": order.customer_id,
                        "provider_id": (
                            order.provider_id if order.provider_id else "None"
                        ),
                        "amount": float(order.price),
                        "status": payment_status_enum.value,
                        "transaction_id": transaction_id,
                        "order_title": order.title[:30],
                    }
                )

                print(
                    f"Created payment {len(payments_info)}: Order #{order.id} - ${order.price} - {payment_status_enum.value}"
                )

            # Commit all payments
            await db.commit()
            print("\n" + "=" * 130)
            print(f"✓ Successfully created {len(payments_info)} payment records!")
            if skipped_count > 0:
                print(f"  Skipped {skipped_count} orders (payment already exists)")
            print("=" * 130 + "\n")

            # Print all payments
            print("GENERATED PAYMENTS:")
            print("-" * 130)
            print(
                f"{'Payment ID':<12} {'Order ID':<10} {'Customer ID':<13} {'Provider ID':<13} {'Amount':<10} {'Status':<12} {'Transaction ID':<25}"
            )
            print("-" * 130)

            for payment in payments_info:
                print(
                    f"{payment['payment_id']:<12} {payment['order_id']:<10} {payment['customer_id']:<13} "
                    f"{str(payment['provider_id']):<13} ${payment['amount']:<9.2f} {payment['status']:<12} {payment['transaction_id']:<25}"
                )

            print("-" * 130)

            # Calculate statistics
            status_counts = {}
            total_amount = 0
            for payment in payments_info:
                status = payment["status"]
                status_counts[status] = status_counts.get(status, 0) + 1
                total_amount += payment["amount"]

            # Save payments to file
            output_file = "generated_payments.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("=" * 130 + "\n")
                f.write("GENERATED PAYMENTS\n")
                f.write("=" * 130 + "\n\n")
                f.write(
                    f"{'Payment ID':<12} {'Order ID':<10} {'Customer ID':<13} {'Provider ID':<13} {'Amount':<10} {'Status':<12} {'Transaction ID':<25}\n"
                )
                f.write("-" * 130 + "\n")

                for payment in payments_info:
                    f.write(
                        f"{payment['payment_id']:<12} {payment['order_id']:<10} {payment['customer_id']:<13} "
                        f"{str(payment['provider_id']):<13} ${payment['amount']:<9.2f} {payment['status']:<12} {payment['transaction_id']:<25}\n"
                    )

                f.write("-" * 130 + "\n")
                f.write(f"\nTotal payments generated: {len(payments_info)}\n")
                f.write(f"Total amount: ${total_amount:.2f}\n\n")

                f.write("Payment Status Distribution:\n")
                for status, count in sorted(status_counts.items()):
                    f.write(f"  {status}: {count}\n")

                f.write(
                    f"\nGeneration date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
                )

            print(f"\n✓ Payment details saved to: {output_file}")

            print("\nPayment Statistics:")
            print(f"Total Amount: ${total_amount:.2f}")
            print("\nStatus Distribution:")
            for status, count in sorted(status_counts.items()):
                print(f"  {status}: {count}")

        except Exception as e:
            await db.rollback()
            print(f"✗ Error occurred: {e}")
            import traceback

            traceback.print_exc()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    print("Starting payment generation...\n")
    asyncio.run(generate_payments())
