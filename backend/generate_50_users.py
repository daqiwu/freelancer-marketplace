"""
Script to generate 50 random users and insert them into the database
Standalone version with minimal dependencies
"""
import asyncio
import bcrypt
import random
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, Column, Integer, BigInteger, String, Text, ForeignKey, Enum, DECIMAL, TIMESTAMP
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import enum

# Load environment variables
load_dotenv()

# Define models
Base = declarative_base()

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

class CustomerProfile(Base):
    __tablename__ = "customer_profiles"
    id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    location = Column(Enum(LocationEnum), nullable=False)
    address = Column(String(255))
    budget_preference = Column(DECIMAL(10,2))
    balance = Column(DECIMAL(10,2), default=0)

class ProviderProfile(Base):
    __tablename__ = "provider_profiles"
    id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    skills = Column(Text)
    experience_years = Column(Integer)
    hourly_rate = Column(DECIMAL(10,2))
    availability = Column(String(100))

# Lists for generating random data
first_names = [
    "Alice", "Bob", "Charlie", "David", "Emma", "Frank", "Grace", "Henry",
    "Isabella", "Jack", "Kate", "Liam", "Mia", "Noah", "Olivia", "Peter",
    "Quinn", "Rachel", "Sam", "Tina", "Uma", "Victor", "Wendy", "Xander",
    "Yara", "Zack", "Amy", "Ben", "Chloe", "Daniel", "Eva", "Fred",
    "Gina", "Harry", "Iris", "Jake", "Kelly", "Leo", "Mary", "Nick",
    "Oscar", "Paula", "Roy", "Sara", "Tom", "Ursula", "Vince", "Willow",
    "Xavier", "Yvonne"
]

last_names = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "White", "Harris", "Clark",
    "Lewis", "Robinson", "Walker", "Young", "Allen", "King", "Wright", "Scott",
    "Torres", "Hill", "Green", "Adams", "Baker", "Nelson", "Carter", "Mitchell",
    "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins",
    "Stewart", "Morris"
]

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def get_database_url():
    """Get database URL from environment"""
    aws_url = os.getenv("AWS_DATABASE_URL")
    if aws_url:
        return aws_url.strip()
    use_docker = os.getenv("USE_DOCKER", "false").lower() == "true"
    if use_docker:
        return os.getenv("DOCKER_DATABASE_URL", "mysql+aiomysql://root:password@db:3306/freelancer_marketplace").strip()
    return os.getenv("LOCAL_DATABASE_URL", "sqlite+aiosqlite:///./freelancer.db").strip()

async def generate_users():
    """Generate 50 random users and insert into database"""
    database_url = get_database_url()
    print(f"Using database: {database_url}")
    
    engine = create_async_engine(database_url, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as db:
        try:
            # Get roles from database
            result = await db.execute(select(Role))
            roles = result.scalars().all()
            
            if not roles:
                print("Error: No roles found in database. Please run database initialization first.")
                return
            
            # Create a dictionary of roles for easy access
            role_dict = {role.role_name: role.id for role in roles}
            print(f"Available roles: {list(role_dict.keys())}")
            
            # List to store generated user credentials
            user_credentials = []
            
            # Generate 50 users
            for i in range(50):
                # Generate random username and email
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                username = f"{first_name.lower()}{last_name.lower()}{random.randint(100, 999)}"
                email = f"{username}@example.com"
                
                # Generate a simple password
                password = f"Pass{random.randint(1000, 9999)}!"
                
                # Hash the password
                password_hash = hash_password(password)
                
                # Randomly assign role (customer or provider)
                role_choice = random.choice(["customer", "provider"])
                role_id = role_dict.get(role_choice, role_dict.get("customer"))
                
                # Create user
                new_user = User(
                    username=username,
                    email=email,
                    password_hash=password_hash,
                    role_id=role_id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db.add(new_user)
                await db.flush()  # Get the user ID
                
                # Create profile based on role
                if role_choice == "customer":
                    customer_profile = CustomerProfile(
                        id=new_user.id,
                        location=random.choice(list(LocationEnum)),
                        address=f"{random.randint(1, 999)} {random.choice(['Main', 'Oak', 'Pine', 'Maple', 'Cedar'])} Street",
                        budget_preference=round(random.uniform(50, 500), 2),
                        balance=round(random.uniform(100, 2000), 2)
                    )
                    db.add(customer_profile)
                else:  # provider
                    skills = random.sample([
                        "Cleaning", "Repair", "Programming", "Design", "Teaching",
                        "Consulting", "Photography", "Writing", "Translation", "Marketing"
                    ], k=random.randint(2, 4))
                    
                    provider_profile = ProviderProfile(
                        id=new_user.id,
                        skills=", ".join(skills),
                        experience_years=random.randint(1, 15),
                        hourly_rate=round(random.uniform(20, 150), 2),
                        availability="Monday-Friday"
                    )
                    db.add(provider_profile)
                
                # Store credentials
                user_credentials.append({
                    "username": username,
                    "password": password,
                    "email": email,
                    "role": role_choice
                })
                
                print(f"Created user {i+1}/50: {username} ({role_choice})")
            
            # Commit all users
            await db.commit()
            print("\n" + "="*100)
            print("✓ Successfully created 50 users!")
            print("="*100 + "\n")
            
            # Print all user credentials
            print("USER CREDENTIALS:")
            print("-" * 100)
            print(f"{'No.':<5} {'Username':<25} {'Password':<15} {'Email':<40} {'Role':<10}")
            print("-" * 100)
            
            for idx, cred in enumerate(user_credentials, 1):
                print(f"{idx:<5} {cred['username']:<25} {cred['password']:<15} {cred['email']:<40} {cred['role']:<10}")
            
            print("-" * 100)
            
            # Save credentials to file
            output_file = "generated_users_credentials.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("=" * 100 + "\n")
                f.write("GENERATED USER CREDENTIALS\n")
                f.write("=" * 100 + "\n\n")
                f.write(f"{'No.':<5} {'Username':<25} {'Password':<15} {'Email':<40} {'Role':<10}\n")
                f.write("-" * 100 + "\n")
                
                for idx, cred in enumerate(user_credentials, 1):
                    f.write(f"{idx:<5} {cred['username']:<25} {cred['password']:<15} {cred['email']:<40} {cred['role']:<10}\n")
                
                f.write("-" * 100 + "\n")
                f.write(f"\nTotal users generated: {len(user_credentials)}\n")
                f.write(f"Generation date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
            
            print(f"\n✓ Credentials saved to: {output_file}")
            
        except Exception as e:
            await db.rollback()
            print(f"✗ Error occurred: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await engine.dispose()

if __name__ == "__main__":
    print("Starting user generation...\n")
    asyncio.run(generate_users())

