# backend/init_db.py
from sqlalchemy import create_engine
from app.models.models import Base, Role
from sqlalchemy.orm import sessionmaker
import os

DB_USER = os.getenv("DB_USER", "freelancer")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "freelancer_marketplace")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
    # 可以插入初始角色
    session = SessionLocal()
    for role_name in ["customer", "provider", "admin"]:
        if not session.query(Role).filter_by(role_name=role_name).first():
            session.add(Role(role_name=role_name))
    session.commit()
    session.close()
    print("数据库初始化完成")

if __name__ == "__main__":
    init_db()
