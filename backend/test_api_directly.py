#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试 API 登录
模拟前端请求，检查后端响应
"""

import requests
import json

def test_login():
    print("=" * 70)
    print("  直接测试后端 API 登录")
    print("=" * 70)
    print()
    
    # 配置
    backend_url = "http://localhost:8000/api/v1/auth/login"
    email = "yamatoya311@mail.com"
    password = "aMKA3P744"
    
    print(f"🌐 后端地址: {backend_url}")
    print(f"📧 邮箱: {email}")
    print(f"🔑 密码: {password}")
    print()
    
    # 准备请求数据
    payload = {
        "email": email,
        "password": password
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("📤 发送登录请求...")
    print(f"   请求体: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        # 发送请求
        response = requests.post(
            backend_url,
            json=payload,
            headers=headers,
            timeout=5
        )
        
        print(f"📥 收到响应:")
        print(f"   状态码: {response.status_code}")
        print(f"   响应头: {dict(response.headers)}")
        print()
        
        # 解析响应
        try:
            response_data = response.json()
            print(f"   响应体:")
            print(f"   {json.dumps(response_data, indent=2)}")
        except:
            print(f"   响应体（原始）: {response.text}")
        
        print()
        
        # 判断结果
        if response.status_code == 200:
            print("✅ 登录成功！")
            print(f"   Token: {response_data.get('access_token', 'N/A')[:50]}...")
            print()
            print("=" * 70)
            print("  结论: 后端 API 工作正常！")
            print("  问题可能在前端配置或网络请求")
            print("=" * 70)
            return True
        elif response.status_code == 401:
            print("❌ 登录失败: 401 Unauthorized")
            print()
            print("💡 这意味着:")
            print("   - 邮箱或密码错误")
            print("   - 后端密码验证失败")
            print()
            print("🔧 解决方案:")
            print("   1. 确认密码重置成功: python debug_login.py")
            print("   2. 检查数据库中的密码哈希")
            return False
        else:
            print(f"❌ 登录失败: HTTP {response.status_code}")
            print()
            print("💡 其他错误，查看响应详情")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误: 无法连接到后端服务器")
        print()
        print("💡 可能的原因:")
        print("   1. 后端服务未启动")
        print("   2. 端口错误（应该是 8000）")
        print("   3. 防火墙阻止")
        print()
        print("🔧 解决方案:")
        print("   启动后端: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        print("   后端响应太慢或未响应")
        return False
        
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print()
    test_login()
    print()

