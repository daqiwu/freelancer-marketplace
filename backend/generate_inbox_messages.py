"""
Script to generate customer_inbox and provider_inbox messages based on existing data
Standalone version with minimal dependencies
"""

import asyncio
import enum
import os
import random
from datetime import datetime, timedelta

from dotenv import load_dotenv
from sqlalchemy import (
    DECIMAL,
    TIMESTAMP,
    BigInteger,
    Boolean,
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
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)


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


# Message templates for customers
CUSTOMER_MESSAGE_TEMPLATES = {
    "order_created": [
        "Your order has been created successfully and is pending review by our admin team.",
        "Thank you for your order! It is currently under review.",
        "Order submitted successfully! Our team will review it shortly.",
    ],
    "order_approved": [
        "Good news! Your order has been approved and is now available for providers.",
        "Your order has passed review and is now live on the platform.",
        "Order approved! Providers can now view and accept your request.",
    ],
    "provider_accepted": [
        "A provider has accepted your order! You can now view their profile and contact details.",
        "Great news! Your order has been accepted by a qualified provider.",
        "Provider assigned! Your service provider is ready to start working on your order.",
    ],
    "order_in_progress": [
        "Your order is now in progress. The provider has started working on it.",
        "Work has begun on your order! Your provider is actively working on your request.",
        "Your order status has been updated to 'In Progress'.",
    ],
    "order_completed": [
        "Your order has been completed! Please review the work and provide feedback.",
        "Service completed! We hope you're satisfied with the results.",
        "Order finished! Don't forget to leave a review for your provider.",
    ],
    "payment_reminder": [
        "Payment reminder: Your order is ready for payment.",
        "Please complete the payment for your order to proceed.",
        "Payment pending for your order. Please process at your earliest convenience.",
    ],
    "general_notification": [
        "Welcome to our platform! Feel free to explore services and post your requirements.",
        "Check out our latest service providers in your area!",
        "Thank you for using our platform. Your satisfaction is our priority.",
    ],
}

# Message templates for providers
PROVIDER_MESSAGE_TEMPLATES = {
    "new_order_available": [
        "New order available in your area! Check it out and apply if interested.",
        "A new service request matching your skills has been posted.",
        "New opportunity! A customer is looking for services you provide.",
    ],
    "order_accepted_confirmation": [
        "You have successfully accepted an order. Please contact the customer to coordinate.",
        "Order accepted! Make sure to deliver quality service and communicate with the customer.",
        "Congratulations! You've been assigned a new order. Review the details carefully.",
    ],
    "customer_contact": [
        "The customer has requested to contact you regarding the order.",
        "New message from customer about your ongoing order.",
        "Customer inquiry: Please respond to the customer's question about the service.",
    ],
    "payment_received": [
        "Payment received for your completed order! Funds will be processed to your account.",
        "Great news! Payment has been confirmed for your service.",
        "Payment successful! Thank you for providing excellent service.",
    ],
    "review_received": [
        "You have received a new review from a customer!",
        "A customer has left feedback on your completed service.",
        "New rating received! Check your profile to see your latest review.",
    ],
    "general_notification": [
        "Welcome to the provider network! Start accepting orders to earn money.",
        "Tip: Complete orders on time to maintain high ratings!",
        "Keep your availability updated to receive more order requests.",
    ],
}


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


async def generate_inbox_messages():
    """Generate customer and provider inbox messages based on existing data"""
    database_url = get_database_url()
    print(f"Using database: {database_url}")

    engine = create_async_engine(database_url, echo=False)
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with AsyncSessionLocal() as db:
        try:
            # Get all users
            users_result = await db.execute(select(User))
            all_users = users_result.scalars().all()

            customers = [u for u in all_users if u.role_id == 1]
            providers = [u for u in all_users if u.role_id == 2]

            print(f"Found {len(customers)} customers and {len(providers)} providers")

            # Get all orders
            orders_result = await db.execute(select(Order))
            all_orders = orders_result.scalars().all()

            print(f"Found {len(all_orders)} orders")

            if not customers and not providers:
                print("No users found. Please generate users first.")
                return

            # Lists to store generated messages
            customer_messages_info = []
            provider_messages_info = []

            # Generate messages for each order
            print("\nGenerating order-related messages...")
            for order in all_orders:
                order_time = order.created_at if order.created_at else datetime.utcnow()

                # Customer messages based on order status
                if order.status == OrderStatus.pending_review:
                    # Order created message
                    message = random.choice(CUSTOMER_MESSAGE_TEMPLATES["order_created"])
                    customer_inbox = CustomerInbox(
                        customer_id=order.customer_id,
                        order_id=order.id,
                        message=f"Order #{order.id}: {message}",
                        created_at=order_time,
                        is_read=random.choice([True, False]),
                    )
                    db.add(customer_inbox)
                    await db.flush()
                    customer_messages_info.append(
                        {
                            "id": customer_inbox.id,
                            "customer_id": order.customer_id,
                            "order_id": order.id,
                            "message": message[:50] + "...",
                            "is_read": customer_inbox.is_read,
                        }
                    )

                elif order.status == OrderStatus.pending:
                    # Order approved message
                    message = random.choice(
                        CUSTOMER_MESSAGE_TEMPLATES["order_approved"]
                    )
                    customer_inbox = CustomerInbox(
                        customer_id=order.customer_id,
                        order_id=order.id,
                        message=f"Order #{order.id}: {message}",
                        created_at=order_time + timedelta(hours=1),
                        is_read=random.choice([True, False]),
                    )
                    db.add(customer_inbox)
                    await db.flush()
                    customer_messages_info.append(
                        {
                            "id": customer_inbox.id,
                            "customer_id": order.customer_id,
                            "order_id": order.id,
                            "message": message[:50] + "...",
                            "is_read": customer_inbox.is_read,
                        }
                    )

                    # Notify nearby providers about new order
                    if providers:
                        selected_providers = random.sample(
                            providers, min(3, len(providers))
                        )
                        for provider in selected_providers:
                            message = random.choice(
                                PROVIDER_MESSAGE_TEMPLATES["new_order_available"]
                            )
                            provider_inbox = ProviderInbox(
                                provider_id=provider.id,
                                order_id=order.id,
                                message=f"New Order #{order.id}: {order.title} - {message}",
                                created_at=order_time
                                + timedelta(hours=1, minutes=random.randint(5, 30)),
                                is_read=random.choice([True, False]),
                            )
                            db.add(provider_inbox)
                            await db.flush()
                            provider_messages_info.append(
                                {
                                    "id": provider_inbox.id,
                                    "provider_id": provider.id,
                                    "order_id": order.id,
                                    "message": message[:50] + "...",
                                    "is_read": provider_inbox.is_read,
                                }
                            )

                elif order.status == OrderStatus.accepted and order.provider_id:
                    # Customer: Provider accepted message
                    message = random.choice(
                        CUSTOMER_MESSAGE_TEMPLATES["provider_accepted"]
                    )
                    customer_inbox = CustomerInbox(
                        customer_id=order.customer_id,
                        order_id=order.id,
                        message=f"Order #{order.id}: {message}",
                        created_at=order_time + timedelta(hours=2),
                        is_read=random.choice([True, False]),
                    )
                    db.add(customer_inbox)
                    await db.flush()
                    customer_messages_info.append(
                        {
                            "id": customer_inbox.id,
                            "customer_id": order.customer_id,
                            "order_id": order.id,
                            "message": message[:50] + "...",
                            "is_read": customer_inbox.is_read,
                        }
                    )

                    # Provider: Acceptance confirmation
                    message = random.choice(
                        PROVIDER_MESSAGE_TEMPLATES["order_accepted_confirmation"]
                    )
                    provider_inbox = ProviderInbox(
                        provider_id=order.provider_id,
                        order_id=order.id,
                        message=f"Order #{order.id}: {message}",
                        created_at=order_time + timedelta(hours=2, minutes=5),
                        is_read=random.choice([True, False]),
                    )
                    db.add(provider_inbox)
                    await db.flush()
                    provider_messages_info.append(
                        {
                            "id": provider_inbox.id,
                            "provider_id": order.provider_id,
                            "order_id": order.id,
                            "message": message[:50] + "...",
                            "is_read": provider_inbox.is_read,
                        }
                    )

                elif order.status == OrderStatus.in_progress and order.provider_id:
                    # Customer: Work in progress
                    message = random.choice(
                        CUSTOMER_MESSAGE_TEMPLATES["order_in_progress"]
                    )
                    customer_inbox = CustomerInbox(
                        customer_id=order.customer_id,
                        order_id=order.id,
                        message=f"Order #{order.id}: {message}",
                        created_at=order_time + timedelta(hours=4),
                        is_read=random.choice([True, False]),
                    )
                    db.add(customer_inbox)
                    await db.flush()
                    customer_messages_info.append(
                        {
                            "id": customer_inbox.id,
                            "customer_id": order.customer_id,
                            "order_id": order.id,
                            "message": message[:50] + "...",
                            "is_read": customer_inbox.is_read,
                        }
                    )

                elif order.status == OrderStatus.completed and order.provider_id:
                    # Customer: Order completed
                    message = random.choice(
                        CUSTOMER_MESSAGE_TEMPLATES["order_completed"]
                    )
                    customer_inbox = CustomerInbox(
                        customer_id=order.customer_id,
                        order_id=order.id,
                        message=f"Order #{order.id}: {message}",
                        created_at=order_time + timedelta(days=1),
                        is_read=random.choice([True, False]),
                    )
                    db.add(customer_inbox)
                    await db.flush()
                    customer_messages_info.append(
                        {
                            "id": customer_inbox.id,
                            "customer_id": order.customer_id,
                            "order_id": order.id,
                            "message": message[:50] + "...",
                            "is_read": customer_inbox.is_read,
                        }
                    )

                    # Provider: Payment received
                    message = random.choice(
                        PROVIDER_MESSAGE_TEMPLATES["payment_received"]
                    )
                    provider_inbox = ProviderInbox(
                        provider_id=order.provider_id,
                        order_id=order.id,
                        message=f"Order #{order.id}: {message}",
                        created_at=order_time + timedelta(days=1, hours=1),
                        is_read=random.choice([True, False]),
                    )
                    db.add(provider_inbox)
                    await db.flush()
                    provider_messages_info.append(
                        {
                            "id": provider_inbox.id,
                            "provider_id": order.provider_id,
                            "order_id": order.id,
                            "message": message[:50] + "...",
                            "is_read": provider_inbox.is_read,
                        }
                    )

            # Generate some general notifications for customers
            print("Generating general notifications for customers...")
            for customer in random.sample(customers, min(10, len(customers))):
                message = random.choice(
                    CUSTOMER_MESSAGE_TEMPLATES["general_notification"]
                )
                customer_inbox = CustomerInbox(
                    customer_id=customer.id,
                    order_id=None,
                    message=f"System Notification: {message}",
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 7)),
                    is_read=random.choice([True, False]),
                )
                db.add(customer_inbox)
                await db.flush()
                customer_messages_info.append(
                    {
                        "id": customer_inbox.id,
                        "customer_id": customer.id,
                        "order_id": None,
                        "message": message[:50] + "...",
                        "is_read": customer_inbox.is_read,
                    }
                )

            # Generate some general notifications for providers
            print("Generating general notifications for providers...")
            for provider in random.sample(providers, min(10, len(providers))):
                message = random.choice(
                    PROVIDER_MESSAGE_TEMPLATES["general_notification"]
                )
                provider_inbox = ProviderInbox(
                    provider_id=provider.id,
                    order_id=None,
                    message=f"System Notification: {message}",
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 7)),
                    is_read=random.choice([True, False]),
                )
                db.add(provider_inbox)
                await db.flush()
                provider_messages_info.append(
                    {
                        "id": provider_inbox.id,
                        "provider_id": provider.id,
                        "order_id": None,
                        "message": message[:50] + "...",
                        "is_read": provider_inbox.is_read,
                    }
                )

            # Commit all messages
            await db.commit()
            print("\n" + "=" * 120)
            print(
                f"✓ Successfully created {len(customer_messages_info)} customer inbox messages!"
            )
            print(
                f"✓ Successfully created {len(provider_messages_info)} provider inbox messages!"
            )
            print("=" * 120 + "\n")

            # Print summary
            print("CUSTOMER INBOX MESSAGES (Sample):")
            print("-" * 120)
            print(
                f"{'ID':<8} {'Customer ID':<13} {'Order ID':<10} {'Message Preview':<70} {'Read':<6}"
            )
            print("-" * 120)
            for msg in customer_messages_info[:10]:
                order_id_str = str(msg["order_id"]) if msg["order_id"] else "N/A"
                read_str = "✓" if msg["is_read"] else "✗"
                print(
                    f"{msg['id']:<8} {msg['customer_id']:<13} {order_id_str:<10} {msg['message']:<70} {read_str:<6}"
                )
            if len(customer_messages_info) > 10:
                print(f"... and {len(customer_messages_info) - 10} more messages")
            print("-" * 120)

            print("\nPROVIDER INBOX MESSAGES (Sample):")
            print("-" * 120)
            print(
                f"{'ID':<8} {'Provider ID':<13} {'Order ID':<10} {'Message Preview':<70} {'Read':<6}"
            )
            print("-" * 120)
            for msg in provider_messages_info[:10]:
                order_id_str = str(msg["order_id"]) if msg["order_id"] else "N/A"
                read_str = "✓" if msg["is_read"] else "✗"
                print(
                    f"{msg['id']:<8} {msg['provider_id']:<13} {order_id_str:<10} {msg['message']:<70} {read_str:<6}"
                )
            if len(provider_messages_info) > 10:
                print(f"... and {len(provider_messages_info) - 10} more messages")
            print("-" * 120)

            # Calculate statistics
            customer_read = sum(1 for m in customer_messages_info if m["is_read"])
            customer_unread = len(customer_messages_info) - customer_read
            provider_read = sum(1 for m in provider_messages_info if m["is_read"])
            provider_unread = len(provider_messages_info) - provider_read

            # Save to file
            output_file = "generated_inbox_messages.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("=" * 120 + "\n")
                f.write("GENERATED INBOX MESSAGES\n")
                f.write("=" * 120 + "\n\n")

                f.write("CUSTOMER INBOX MESSAGES:\n")
                f.write("-" * 120 + "\n")
                f.write(f"{'ID':<8} {'Customer ID':<13} {'Order ID':<10} {'Read':<6}\n")
                f.write("-" * 120 + "\n")
                for msg in customer_messages_info:
                    order_id_str = str(msg["order_id"]) if msg["order_id"] else "N/A"
                    read_str = "Yes" if msg["is_read"] else "No"
                    f.write(
                        f"{msg['id']:<8} {msg['customer_id']:<13} {order_id_str:<10} {read_str:<6}\n"
                    )

                f.write("\n" + "=" * 120 + "\n")
                f.write("PROVIDER INBOX MESSAGES:\n")
                f.write("-" * 120 + "\n")
                f.write(f"{'ID':<8} {'Provider ID':<13} {'Order ID':<10} {'Read':<6}\n")
                f.write("-" * 120 + "\n")
                for msg in provider_messages_info:
                    order_id_str = str(msg["order_id"]) if msg["order_id"] else "N/A"
                    read_str = "Yes" if msg["is_read"] else "No"
                    f.write(
                        f"{msg['id']:<8} {msg['provider_id']:<13} {order_id_str:<10} {read_str:<6}\n"
                    )

                f.write("\n" + "-" * 120 + "\n")
                f.write(f"\nTotal customer messages: {len(customer_messages_info)}\n")
                f.write(f"  Read: {customer_read}, Unread: {customer_unread}\n")
                f.write(f"\nTotal provider messages: {len(provider_messages_info)}\n")
                f.write(f"  Read: {provider_read}, Unread: {provider_unread}\n")
                f.write(
                    f"\nGeneration date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
                )

            print(f"\n✓ Message details saved to: {output_file}")

            print("\nMessage Statistics:")
            print(
                f"Customer Messages: {len(customer_messages_info)} total ({customer_read} read, {customer_unread} unread)"
            )
            print(
                f"Provider Messages: {len(provider_messages_info)} total ({provider_read} read, {provider_unread} unread)"
            )

        except Exception as e:
            await db.rollback()
            print(f"✗ Error occurred: {e}")
            import traceback

            traceback.print_exc()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    print("Starting inbox message generation...\n")
    asyncio.run(generate_inbox_messages())
