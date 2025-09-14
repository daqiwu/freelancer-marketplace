#!/usr/bin/env python3
"""
测试运行脚本
用于运行用户模块的测试
"""

import subprocess
import sys
import os

def run_tests():
    """运行测试"""
    # 确保在正确的目录中
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 运行pytest
    cmd = [
        sys.executable, "-m", "pytest",
        "app/test/user_test/",
        "-v",
        "--tb=short"
    ]
    
    print("运行用户模块测试...")
    print(f"命令: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=True)
        print("-" * 50)
        print("✅ 所有测试通过!")
        return 0
    except subprocess.CalledProcessError as e:
        print("-" * 50)
        print(f"❌ 测试失败，退出码: {e.returncode}")
        return e.returncode

if __name__ == "__main__":
    sys.exit(run_tests())
