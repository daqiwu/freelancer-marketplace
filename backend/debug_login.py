#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录问题诊断工具
详细检查登录流程的每一步
"""

import asyncio
import bcrypt
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from app.models.models import User
from app.config import settings

async def debug_login(email: str, password: str):
    """调试登录流程"""
    
    print("=" * 70)
    print("  登录问题诊断工具")
    print("=" * 70)
    print()
    
    # 创建数据库连接
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        try:
            print(f"🔍 步骤 1: 查找用户")
            print(f"   邮箱: {email}")
            
            # 查找用户
            result = await session.execute(
                select(User).where(User.email == email)
            )
            user = result.scalars().first()
            
            if not user:
                print(f"   ❌ 未找到用户！")
                print()
                print("💡 可能的原因:")
                print("   - 邮箱拼写错误")
                print("   - 用户不存在")
                print()
                
                # 列出所有用户邮箱
                print("📋 数据库中的所有用户邮箱:")
                all_users = await session.execute(select(User))
                for u in all_users.scalars():
                    print(f"   - {u.email}")
                
                return False
            
            print(f"   ✅ 找到用户！")
            print(f"   用户ID: {user.id}")
            print(f"   用户名: {user.username}")
            print(f"   邮箱: {user.email}")
            print(f"   角色ID: {user.role_id}")
            print()
            
            print(f"🔐 步骤 2: 检查密码")
            print(f"   尝试的密码: {password}")
            print(f"   密码长度: {len(password)} 字符")
            print(f"   数据库哈希值: {user.password_hash[:50]}...")
            print()
            
            # 验证密码
            try:
                password_bytes = password.encode('utf-8')
                hash_bytes = user.password_hash.encode('utf-8')
                
                print(f"   编码后的密码: {password_bytes}")
                print(f"   编码后的哈希: {hash_bytes[:50]}...")
                print()
                
                is_valid = bcrypt.checkpw(password_bytes, hash_bytes)
                
                if is_valid:
                    print(f"   ✅ 密码验证成功！")
                    print()
                    print("✨ 登录应该可以正常工作")
                    print()
                    print("=" * 70)
                    print("  诊断结果: 一切正常！")
                    print("=" * 70)
                    return True
                else:
                    print(f"   ❌ 密码验证失败！")
                    print()
                    print("💡 问题原因: 密码不匹配")
                    print()
                    
                    # 测试常见密码
                    print("🔍 尝试其他常见密码:")
                    test_passwords = [
                        password,
                        password.strip(),  # 去除空格
                        password.lower(),
                        password.upper(),
                        "password",
                        "123456",
                        "admin",
                    ]
                    
                    for test_pwd in test_passwords:
                        if bcrypt.checkpw(test_pwd.encode('utf-8'), hash_bytes):
                            print(f"   ✅ 找到了！正确的密码是: '{test_pwd}'")
                            return False
                    
                    print(f"   ❌ 都不匹配")
                    print()
                    
                    # 生成新密码
                    print("🔧 解决方案:")
                    print()
                    print(f"方案 1: 重置密码为 '{password}'")
                    new_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
                    print(f"   运行: python reset_user_password.py")
                    print()
                    print(f"方案 2: 手动更新数据库")
                    print(f"   新哈希值: {new_hash}")
                    print(f"   SQL:")
                    print(f"   UPDATE users SET password_hash = '{new_hash}'")
                    print(f"   WHERE email = '{email}';")
                    print()
                    
                    return False
                    
            except Exception as e:
                print(f"   ❌ 验证过程出错: {e}")
                import traceback
                traceback.print_exc()
                return False
                
        except Exception as e:
            print(f"❌ 数据库查询错误: {e}")
            import traceback
            traceback.print_exc()
            return False

async def main():
    print()
    
    # 配置参数 - 根据你的情况修改
    test_email = "yamatoya311@mail.com"
    test_password = "aMKA3P744"
    
    print(f"📧 测试邮箱: {test_email}")
    print(f"🔑 测试密码: {test_password}")
    print()
    print("开始诊断...")
    print()
    
    success = await debug_login(test_email, test_password)
    
    print()
    if success:
        print("✅ 登录功能正常！可以使用以下信息登录:")
        print(f"   邮箱: {test_email}")
        print(f"   密码: {test_password}")
    else:
        print("❌ 登录失败！请按照上面的解决方案操作。")
    print()

if __name__ == "__main__":
    asyncio.run(main())

