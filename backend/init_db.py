# backend/init_db.py
from sqlalchemy import create_engine
from app.models.models import Base, Role
from app.config import settings
from sqlalchemy.orm import sessionmaker

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
    # Can insert initial roles
    session = SessionLocal()
    for role_name in ["customer", "provider", "admin"]:
        if not session.query(Role).filter_by(role_name=role_name).first():
            session.add(Role(role_name=role_name))
    session.commit()
    session.close()
    print("数据库初始化完成")  # Database initialization completed

if __name__ == "__main__":
    init_db()
