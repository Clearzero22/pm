#!/bin/bash
# Amazon Crawler - 服务器部署脚本
# 用于在无显示器的服务器上运行爬虫

set -e

echo "========================================"
echo "  Amazon Crawler - 服务器部署"
echo "========================================"
echo ""

# 检查依赖
echo "1. 检查系统依赖..."
if ! command -v python &> /dev/null; then
    echo "❌ Python 未安装"
    exit 1
fi

if ! command -v uv &> /dev/null; then
    echo "❌ uv 未安装，正在安装..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

echo "✅ 依赖检查完成"
echo ""

# 检查 Playwright 浏览器
echo "2. 检查 Playwright 浏览器..."
if [ ! -d "$HOME/.cache/ms-playwright" ]; then
    echo "正在安装 Playwright 浏览器..."
    uv run playwright install chromium
    echo "✅ 浏览器安装完成"
else
    echo "✅ 浏览器已安装"
fi
echo ""

# 安装服务器依赖
echo "3. 检查服务器依赖..."
if command -v apt-get &> /dev/null; then
    echo "检测到 Debian/Ubuntu 系统"

    # 检查是否已安装依赖
    if ! dpkg -l | grep -q "libatk-bridge2.0-0"; then
        echo "安装必要的系统库..."
        sudo apt-get update -qq
        sudo apt-get install -y \
            libatk-bridge2.0-0 \
            libxkbcommon0 \
            libgbm1 \
            > /dev/null 2>&1
        echo "✅ 系统库安装完成"
    else
        echo "✅ 系统库已安装"
    fi
elif command -v yum &> /dev/null; then
    echo "检测到 RHEL/CentOS 系统"
    # Add RHEL support if needed
fi
echo ""

# 创建必要的目录
echo "4. 创建输出目录..."
mkdir -p output logs
echo "✅ 目录创建完成"
echo ""

# 运行爬虫
echo "5. 运行爬虫..."
echo ""
echo "========================================"
uv run python main.py \
    --pages 1 \
    --products 5 \
    --headless \
    --output "output/amazon_$(date +%Y%m%d_%H%M%S).csv"

echo ""
echo "========================================"
echo "✅ 爬取完成！"
echo ""
