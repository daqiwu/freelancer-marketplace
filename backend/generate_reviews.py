"""
Script to generate review records based on completed orders
Standalone version with minimal dependencies
"""
import asyncio
import random
import os
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, Column, Integer, BigInteger, String, Text, ForeignKey, Enum, DECIMAL, TIMESTAMP, DateTime
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import enum

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
    status = Column(Enum(OrderStatus), default=OrderStatus.pending_review, nullable=False)
    price = Column(DECIMAL(10,2), nullable=False)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

class Review(Base):
    __tablename__ = "reviews"
    id = Column(BigInteger, primary_key=True)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False, unique=True)
    customer_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    provider_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    stars = Column(Integer, nullable=False, default=5)
    content = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP)

# Review templates by star rating
REVIEW_TEMPLATES = {
    5: [
        "Excellent service! Highly professional and exceeded my expectations.",
        "Outstanding work! Very satisfied with the quality and timeliness.",
        "Perfect! The provider was skilled, punctual, and friendly.",
        "Amazing experience! Would definitely hire again.",
        "Top-notch service! Couldn't be happier with the results.",
        "Fantastic job! Very professional and efficient.",
        "Superb quality! Exactly what I needed.",
        "Exceptional service! Highly recommend this provider.",
        "Great work! Very pleased with everything.",
        "Wonderful experience! The provider went above and beyond.",
    ],
    4: [
        "Very good service. Minor delays but overall satisfied.",
        "Good work! Met most of my expectations.",
        "Professional service with a few small issues that were resolved.",
        "Solid performance. Would consider hiring again.",
        "Pretty good! The job was done well with some minor hiccups.",
        "Nice work overall. A few things could be improved.",
        "Good quality service. Communication could be better.",
        "Satisfied with the results. Some room for improvement.",
        "Decent service. Got the job done as expected.",
        "Good experience overall with minor issues.",
    ],
    3: [
        "Okay service. Met basic requirements but nothing special.",
        "Average work. Had some issues but acceptable.",
        "Service was fine. Could have been better in some areas.",
        "Acceptable results. Not great but not bad either.",
        "Mediocre experience. Expected more for the price.",
        "Just okay. Some aspects were good, others not so much.",
        "Average quality. Met minimum expectations.",
        "Fair service. Several things could be improved.",
        "It was alright. Nothing to complain about but nothing impressive.",
        "Moderate satisfaction. Service was adequate.",
    ],
    2: [
        "Below expectations. Several issues need to be addressed.",
        "Not satisfied. Poor communication and delayed completion.",
        "Disappointing service. Quality was subpar.",
        "Had multiple problems. Would not recommend.",
        "Unsatisfactory work. Did not meet requirements.",
        "Poor experience. Many aspects need improvement.",
        "Not happy with the results. Too many issues.",
        "Substandard service. Expected much better.",
        "Frustrating experience. Quality and timeliness were poor.",
        "Unimpressed. Service did not meet promised standards.",
    ],
    1: [
        "Very poor service. Completely unsatisfied.",
        "Terrible experience. Would not recommend at all.",
        "Extremely disappointed. Total waste of money.",
        "Worst service ever. Nothing was done properly.",
        "Absolutely unacceptable. Unprofessional and low quality.",
        "Horrible work. Had to hire someone else to fix it.",
        "Complete disaster. Avoid this provider.",
        "Totally dissatisfied. Nothing went as promised.",
        "Awful experience from start to finish.",
        "Unacceptable service. Major issues throughout.",
    ]
}

def get_database_url():
    """Get database URL from environment"""
    aws_url = os.getenv("AWS_DATABASE_URL")
    if aws_url:
        return aws_url.strip()
    use_docker = os.getenv("USE_DOCKER", "false").lower() == "true"
    if use_docker:
        return os.getenv("DOCKER_DATABASE_URL", "mysql+aiomysql://root:password@db:3306/freelancer_marketplace").strip()
    return os.getenv("LOCAL_DATABASE_URL", "sqlite+aiosqlite:///./freelancer.db").strip()

def get_review_content(stars):
    """Get a random review content based on star rating"""
    return random.choice(REVIEW_TEMPLATES[stars])

async def generate_reviews():
    """Generate review records based on completed orders"""
    database_url = get_database_url()
    print(f"Using database: {database_url}")
    
    engine = create_async_engine(database_url, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as db:
        try:
            # Get all completed orders with providers
            result = await db.execute(
                select(Order).where(
                    Order.status == OrderStatus.completed,
                    Order.provider_id.isnot(None)
                )
            )
            completed_orders = result.scalars().all()
            
            if not completed_orders:
                print("No completed orders with providers found. Please ensure you have completed orders in the database.")
                return
            
            print(f"Found {len(completed_orders)} completed orders eligible for reviews")
            
            # Check existing reviews to avoid duplicates
            existing_reviews_result = await db.execute(select(Review))
            existing_reviews = existing_reviews_result.scalars().all()
            existing_order_ids = {r.order_id for r in existing_reviews}
            
            print(f"Found {len(existing_order_ids)} existing reviews")
            
            # Get user information for display
            users_result = await db.execute(select(User))
            users = {u.id: u.username for u in users_result.scalars().all()}
            
            # List to store generated review info
            reviews_info = []
            skipped_count = 0
            
            # Generate reviews for completed orders
            for order in completed_orders:
                # Skip if review already exists for this order
                if order.id in existing_order_ids:
                    skipped_count += 1
                    continue
                
                # 80% chance of creating a review for a completed order
                if random.random() > 0.8:
                    continue
                
                # Generate star rating with weighted probability
                # More likely to get higher ratings
                star_weights = [0.05, 0.10, 0.15, 0.30, 0.40]  # 1-5 stars
                stars = random.choices([1, 2, 3, 4, 5], weights=star_weights)[0]
                
                # Get review content
                content = get_review_content(stars)
                
                # 10% chance of having no content (just stars)
                if random.random() < 0.1:
                    content = None
                
                # Create review record
                new_review = Review(
                    order_id=order.id,
                    customer_id=order.customer_id,
                    provider_id=order.provider_id,
                    stars=stars,
                    content=content,
                    created_at=order.updated_at if order.updated_at else datetime.utcnow()
                )
                
                db.add(new_review)
                await db.flush()  # Get the review ID
                
                # Store review info
                reviews_info.append({
                    "review_id": new_review.id,
                    "order_id": order.id,
                    "customer": users.get(order.customer_id, "Unknown"),
                    "provider": users.get(order.provider_id, "Unknown"),
                    "stars": stars,
                    "content": content[:50] + "..." if content and len(content) > 50 else content if content else "[No comment]",
                    "order_title": order.title[:30]
                })
                
                print(f"Created review {len(reviews_info)}: Order #{order.id} - {stars} stars")
            
            # Commit all reviews
            await db.commit()
            print("\n" + "="*140)
            print(f"✓ Successfully created {len(reviews_info)} review records!")
            if skipped_count > 0:
                print(f"  Skipped {skipped_count} orders (review already exists)")
            print("="*140 + "\n")
            
            # Print all reviews
            print("GENERATED REVIEWS:")
            print("-" * 140)
            print(f"{'Review ID':<11} {'Order ID':<10} {'Customer':<20} {'Provider':<20} {'Stars':<7} {'Content Preview':<50}")
            print("-" * 140)
            
            for review in reviews_info:
                print(f"{review['review_id']:<11} {review['order_id']:<10} {review['customer']:<20} "
                      f"{review['provider']:<20} {'⭐' * review['stars']:<7} {review['content']:<50}")
            
            print("-" * 140)
            
            # Calculate statistics
            star_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for review in reviews_info:
                star_counts[review['stars']] += 1
            
            avg_stars = sum(r['stars'] for r in reviews_info) / len(reviews_info) if reviews_info else 0
            
            # Save reviews to file
            output_file = "generated_reviews.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("=" * 140 + "\n")
                f.write("GENERATED REVIEWS\n")
                f.write("=" * 140 + "\n\n")
                f.write(f"{'Review ID':<11} {'Order ID':<10} {'Customer':<20} {'Provider':<20} {'Stars':<7} {'Full Content':<80}\n")
                f.write("-" * 140 + "\n")
                
                for review in reviews_info:
                    # Get full content for file
                    full_content = "[No comment]"
                    for r in reviews_info:
                        if r['review_id'] == review['review_id']:
                            result = await db.execute(select(Review).where(Review.id == review['review_id']))
                            db_review = result.scalar_one_or_none()
                            if db_review and db_review.content:
                                full_content = db_review.content
                            break
                    
                    f.write(f"{review['review_id']:<11} {review['order_id']:<10} {review['customer']:<20} "
                           f"{review['provider']:<20} {'⭐' * review['stars']:<7} {full_content}\n")
                
                f.write("-" * 140 + "\n")
                f.write(f"\nTotal reviews generated: {len(reviews_info)}\n")
                f.write(f"Average rating: {avg_stars:.2f} stars\n\n")
                
                f.write("Star Rating Distribution:\n")
                for stars in range(5, 0, -1):
                    count = star_counts[stars]
                    percentage = (count / len(reviews_info) * 100) if reviews_info else 0
                    f.write(f"  {'⭐' * stars} ({stars} stars): {count} ({percentage:.1f}%)\n")
                
                f.write(f"\nGeneration date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
            
            print(f"\n✓ Review details saved to: {output_file}")
            
            print("\nReview Statistics:")
            print(f"Average Rating: {avg_stars:.2f} stars")
            print("\nStar Rating Distribution:")
            for stars in range(5, 0, -1):
                count = star_counts[stars]
                percentage = (count / len(reviews_info) * 100) if reviews_info else 0
                bar = "█" * int(percentage / 2)
                print(f"  {'⭐' * stars} ({stars} stars): {count:3d} ({percentage:5.1f}%) {bar}")
            
        except Exception as e:
            await db.rollback()
            print(f"✗ Error occurred: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await engine.dispose()

if __name__ == "__main__":
    print("Starting review generation...\n")
    asyncio.run(generate_reviews())

