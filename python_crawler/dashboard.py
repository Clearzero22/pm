#!/usr/bin/env python
"""
Amazon 分析仪表盘启动脚本
"""
import sys
import os
import subprocess

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """启动 Streamlit 仪表盘"""
    print("=" * 60)
    print("📊 Amazon 分析仪表盘")
    print("=" * 60)
    print("\n正在启动...")
    print("访问地址: http://localhost:8501")
    print("按 Ctrl+C 停止\n")

    # 检查数据文件
    csv_path = "output/amazon_products.csv"
    if not os.path.exists(csv_path):
        print(f"⚠️  警告: 数据文件不存在 {csv_path}")
        print("💡 请先运行: uv run python main.py")
        print()

    # 启动 Streamlit
    subprocess.run([
        "uv", "run", "streamlit", "run",
        "dashboard/app.py",
        "--server.port=8501",
        "--server.headless=true",
    ])


if __name__ == "__main__":
    main()
