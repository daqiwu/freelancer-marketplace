#!/usr/bin/env python3
"""
测试运行脚本
用于运行指定模块或全部测试
"""

import subprocess
import sys
import os

def run_tests(test_path="app/test/"):
    """运行测试"""
    # 切换到项目根目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # 运行pytest
    cmd = [
        sys.executable, "-m", "pytest",
        test_path,
        "-v",
        "--tb=short"
    ]

    print(f"运行测试路径: {test_path}")
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
    # 支持命令行参数指定测试路径
    test_path = sys.argv[1] if len(sys.argv) > 1 else "app/test/"
    sys.exit(run_tests(test_path))
