"""
Script to generate 100 random orders and insert them into the database
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


class PaymentStatus(enum.Enum):
    unpaid = "unpaid"
    paid = "paid"


class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)


class Order(Base):
    __tablename__ = "orders"
    id = Column(BigInteger, primary_key=True)
    customer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    provider_id = Column(BigInteger, ForeignKey("users.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    service_type = Column(Enum(ServiceType), nullable=False)
    status = Column(
        Enum(OrderStatus), default=OrderStatus.pending_review, nullable=False
    )
    price = Column(DECIMAL(10, 2), nullable=False)
    location = Column(Enum(LocationEnum), nullable=False)
    address = Column(String(255))
    service_start_time = Column(DateTime)
    service_end_time = Column(DateTime)
    payment_status = Column(
        Enum(PaymentStatus), default=PaymentStatus.unpaid, nullable=False
    )
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)


# Service templates for different service types
SERVICE_TEMPLATES = {
    ServiceType.cleaning_repair: [
        ("House Deep Cleaning", "Complete deep cleaning service for your home"),
        ("Appliance Repair", "Professional repair service for home appliances"),
        ("Plumbing Fix", "Emergency plumbing repair service"),
        ("AC Maintenance", "Air conditioning maintenance and repair"),
        ("Painting Service", "Interior and exterior painting"),
        ("Carpet Cleaning", "Professional carpet deep cleaning"),
        ("Window Cleaning", "Residential window cleaning service"),
        ("Furniture Repair", "Repair and restoration of furniture"),
    ],
    ServiceType.it_technology: [
        ("Website Development", "Custom website development service"),
        ("Mobile App Development", "iOS and Android app development"),
        ("Computer Repair", "Laptop and desktop repair service"),
        ("Network Setup", "Home and office network installation"),
        ("Data Recovery", "Professional data recovery service"),
        ("Software Installation", "Software setup and configuration"),
        ("Cybersecurity Audit", "Security assessment for your systems"),
        ("Cloud Migration", "Migrate your data to cloud platforms"),
    ],
    ServiceType.education_training: [
        ("Math Tutoring", "One-on-one math tutoring for students"),
        ("English Language Classes", "English language learning course"),
        ("Programming Course", "Learn Python, Java, or JavaScript"),
        ("Music Lessons", "Piano, guitar, and violin lessons"),
        ("Art Classes", "Drawing and painting instruction"),
        ("Fitness Training", "Personal fitness training program"),
        ("Yoga Classes", "Beginner to advanced yoga sessions"),
        ("Cooking Lessons", "Learn to cook various cuisines"),
    ],
    ServiceType.life_health: [
        ("Personal Chef Service", "Healthy meal preparation at home"),
        ("Massage Therapy", "Relaxation and therapeutic massage"),
        ("Nutrition Consulting", "Personalized diet and nutrition plan"),
        ("Elder Care", "Professional elderly care service"),
        ("Pet Sitting", "Pet care while you're away"),
        ("Dog Walking", "Daily dog walking service"),
        ("Housekeeping", "Regular housekeeping service"),
        ("Childcare", "Professional childcare service"),
    ],
    ServiceType.design_consulting: [
        ("Interior Design", "Complete interior design service"),
        ("Graphic Design", "Logo and branding design"),
        ("Business Consulting", "Business strategy consulting"),
        ("Legal Consulting", "Legal advice and consultation"),
        ("Financial Planning", "Personal financial planning service"),
        ("Marketing Strategy", "Digital marketing consultation"),
        ("UI/UX Design", "User interface and experience design"),
        ("Architecture Design", "Building and renovation design"),
    ],
    ServiceType.other: [
        ("Event Planning", "Complete event planning service"),
        ("Photography", "Professional photography service"),
        ("Video Editing", "Video editing and production"),
        ("Translation Service", "Document translation service"),
        ("Moving Service", "Professional moving and packing"),
        ("Gardening", "Garden maintenance and landscaping"),
        ("Car Detailing", "Complete car cleaning and detailing"),
        ("Handyman Service", "General handyman work"),
    ],
}

STREETS = [
    "Main",
    "Oak",
    "Pine",
    "Maple",
    "Cedar",
    "Elm",
    "Park",
    "Washington",
    "Lake",
    "Hill",
]


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


async def generate_orders():
    """Generate 100 random orders and insert into database"""
    database_url = get_database_url()
    print(f"Using database: {database_url}")

    engine = create_async_engine(database_url, echo=False)
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with AsyncSessionLocal() as db:
        try:
            # Get all users by role
            result = await db.execute(select(User))
            all_users = result.scalars().all()

            if not all_users:
                print(
                    "Error: No users found in database. Please run user generation first."
                )
                return

            # Separate users by role (1=customer, 2=provider, 3=admin)
            customers = [u for u in all_users if u.role_id == 1]
            providers = [u for u in all_users if u.role_id == 2]

            print(f"Found {len(customers)} customers and {len(providers)} providers")

            if not customers:
                print("Error: No customers found in database.")
                return

            if not providers:
                print("Error: No providers found in database.")
                return

            # List to store generated orders info
            orders_info = []

            # Generate 100 orders
            for i in range(100):
                # Randomly select customer
                customer = random.choice(customers)

                # Randomly select service type
                service_type = random.choice(list(ServiceType))

                # Get random service from templates
                service_templates = SERVICE_TEMPLATES[service_type]
                title, description = random.choice(service_templates)

                # Randomly determine order status and assign provider accordingly
                status = random.choice(list(OrderStatus))

                # Orders with certain statuses need a provider
                if status in [
                    OrderStatus.accepted,
                    OrderStatus.in_progress,
                    OrderStatus.completed,
                ]:
                    provider = random.choice(providers)
                    provider_id = provider.id
                    provider_username = provider.username
                elif random.random() < 0.3:  # 30% chance of having provider for pending
                    provider = random.choice(providers)
                    provider_id = provider.id
                    provider_username = provider.username
                else:
                    provider_id = None
                    provider_username = "None"

                # Generate random price
                price = round(random.uniform(50, 800), 2)

                # Random location
                location = random.choice(list(LocationEnum))

                # Random address
                address = f"{random.randint(1, 9999)} {random.choice(STREETS)} Street"

                # Generate service times
                days_ahead = random.randint(1, 30)
                service_start = datetime.utcnow() + timedelta(
                    days=days_ahead, hours=random.randint(8, 18)
                )
                service_end = service_start + timedelta(hours=random.randint(1, 8))

                # Payment status based on order status
                if status == OrderStatus.completed:
                    payment_status = PaymentStatus.paid
                elif status in [OrderStatus.in_progress, OrderStatus.accepted]:
                    payment_status = random.choice(
                        [PaymentStatus.paid, PaymentStatus.unpaid]
                    )
                else:
                    payment_status = PaymentStatus.unpaid

                # Create order
                new_order = Order(
                    customer_id=customer.id,
                    provider_id=provider_id,
                    title=title,
                    description=description,
                    service_type=service_type,
                    status=status,
                    price=price,
                    location=location,
                    address=address,
                    service_start_time=service_start,
                    service_end_time=service_end,
                    payment_status=payment_status,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )

                db.add(new_order)
                await db.flush()  # Get the order ID

                # Store order info
                orders_info.append(
                    {
                        "order_id": new_order.id,
                        "customer": customer.username,
                        "provider": provider_username,
                        "title": title,
                        "service_type": service_type.value,
                        "status": status.value,
                        "price": price,
                        "payment_status": payment_status.value,
                    }
                )

                print(f"Created order {i + 1}/100: {title} - {status.value}")

            # Commit all orders
            await db.commit()
            print("\n" + "=" * 120)
            print("✓ Successfully created 100 orders!")
            print("=" * 120 + "\n")

            # Print all orders
            print("GENERATED ORDERS:")
            print("-" * 120)
            print(
                f"{'ID':<5} {'Customer':<20} {'Provider':<20} {'Title':<30} {'Status':<18} {'Price':<10} {'Payment':<10}"
            )
            print("-" * 120)

            for order in orders_info:
                print(
                    f"{order['order_id']:<5} {order['customer']:<20} {order['provider']:<20} "
                    f"{order['title']:<30} {order['status']:<18} ${order['price']:<9.2f} {order['payment_status']:<10}"
                )

            print("-" * 120)

            # Calculate statistics
            status_counts = {}
            for order in orders_info:
                status = order["status"]
                status_counts[status] = status_counts.get(status, 0) + 1

            service_type_counts = {}
            for order in orders_info:
                stype = order["service_type"]
                service_type_counts[stype] = service_type_counts.get(stype, 0) + 1

            # Save orders to file
            output_file = "generated_orders.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("=" * 120 + "\n")
                f.write("GENERATED ORDERS\n")
                f.write("=" * 120 + "\n\n")
                f.write(
                    f"{'ID':<5} {'Customer':<20} {'Provider':<20} {'Title':<30} {'Status':<18} {'Price':<10} {'Payment':<10}\n"
                )
                f.write("-" * 120 + "\n")

                for order in orders_info:
                    f.write(
                        f"{order['order_id']:<5} {order['customer']:<20} {order['provider']:<20} "
                        f"{order['title']:<30} {order['status']:<18} ${order['price']:<9.2f} {order['payment_status']:<10}\n"
                    )

                f.write("-" * 120 + "\n")
                f.write(f"\nTotal orders generated: {len(orders_info)}\n\n")

                f.write("Order Status Distribution:\n")
                for status, count in sorted(status_counts.items()):
                    f.write(f"  {status}: {count}\n")

                f.write("\nService Type Distribution:\n")
                for stype, count in sorted(service_type_counts.items()):
                    f.write(f"  {stype}: {count}\n")

                f.write(
                    f"\nGeneration date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
                )

            print(f"\n✓ Order details saved to: {output_file}")

            print("\nOrder Statistics:")
            print("Status Distribution:")
            for status, count in sorted(status_counts.items()):
                print(f"  {status}: {count}")

            print("\nService Type Distribution:")
            for stype, count in sorted(service_type_counts.items()):
                print(f"  {stype}: {count}")

        except Exception as e:
            await db.rollback()
            print(f"✗ Error occurred: {e}")
            import traceback

            traceback.print_exc()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    print("Starting order generation...\n")
    asyncio.run(generate_orders())
