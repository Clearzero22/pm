#!/bin/bash
# 树莓派快速部署脚本
# 支持 Raspberry Pi OS (ARM64)

set -e

echo "========================================="
echo "  Amazon Crawler - 树莓派部署"
echo "========================================="
echo ""

# 检测树莓派型号
echo "📱 检测树莓派型号..."
if [ -f /proc/device-tree/model ]; then
    model=$(cat /proc/device-tree/model)
    echo "   型号: $model"
else
    echo "   型号: 未检测到"
fi

# 检查架构
ARCH=$(uname -m)
echo "   架构: $ARCH"

if [ "$ARCH" != "aarch64" ]; then
    echo "⚠️  警告: 不是 ARM64 架构，可能需要手动编译"
fi

echo ""

# 更新系统
echo "1️⃣  更新系统..."
sudo apt update
sudo apt upgrade -y
echo "✅ 系统更新完成"
echo ""

# 安装系统依赖
echo "2️⃣  安装系统依赖..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    curl \
    libatk-bridge2.0-0 \
    libxkbcommon0 \
    libgbm1 \
    libnss3 \
    build-essential \
    zlib1g-dev \
    libncurses5-dev

echo "✅ 系统依赖安装完成"
echo ""

# 检查 Python 版本
echo "3️⃣  检查 Python 版本..."
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo "   当前版本: $PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 14 ]); then
    echo "⚠️  Python 版本过低，需要安装 Python 3.14+"
    echo "   编译安装需要较长时间 (30-60分钟)"
    echo ""
    read -p "是否继续编译安装? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "开始编译 Python 3.14..."
        cd /tmp
        wget https://www.python.org/ftp/python/3.14.0/Python-3.14.0.tgz
        tar -xf Python-3.14.0.tgz
        cd Python-3.14.0
        ./configure --enable-optimizations --with-lto
        make -j$(nproc)
        sudo make altinstall
    else
        echo "跳过 Python 安装"
    fi
else
    echo "✅ Python 版本符合要求"
fi
echo ""

# 安装 uv
echo "4️⃣  安装 uv 包管理器..."
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    echo "✅ uv 安装完成"
else
    echo "✅ uv 已安装"
fi
echo ""

# 优化树莓派配置
echo "5️⃣  优化树莓派配置..."

# 增加 SWAP (如果 SWAP 小于 1GB)
SWAP_CURRENT=$(free -m | grep Swap | awk '{print $2}')
if [ "$SWAP_CURRENT" -lt 1024 ]; then
    echo "   增加 SWAP 空间..."
    sudo dphys-swapfile swapfile 2048
    sudo dphys-swapfile swapon
    echo "✅ SWAP 已设置为 2GB"
else
    echo "✅ SWAP 空间充足 ($SWAP_CURRENT MB)"
fi

# GPU 内存最小化 (如果存在 raspi-config)
if command -v raspi-config &> /dev/null; then
    echo "   配置 GPU 内存..."
    sudo raspi-config nonint do_memory_split 16
    echo "✅ GPU 内存已设置为 16MB"
fi

echo ""

# 部署项目
echo "6️⃣  部署项目..."

# 检查项目是否存在
if [ ! -d "python_crawler" ]; then
    echo "   项目目录不存在"
    echo "   请先上传项目到树莓派"
    echo ""
    echo "   使用 SCP 上传:"
    echo "   scp -r python_crawler/ pi@$(hostname).local:~/"
    echo ""
    echo "   或使用 Git 克隆:"
    echo "   git clone <your-repo-url>"
    exit 1
fi

cd python_crawler

# 安装依赖
echo "   安装 Python 依赖..."
uv sync

# 安装 Playwright 浏览器
echo "   安装 Playwright 浏览器 (需要几分钟)..."
uv run playwright install chromium

echo ""
echo "✅ 部署完成！"
echo ""

# 创建日志目录
mkdir -p logs

# 测试运行
echo "7️⃣  测试运行..."
echo "   运行快速测试 (1个商品)..."
uv run python main.py --pages 1 --products 1 --headless

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "🎉 树莓派部署成功！"
    echo "========================================="
    echo ""
    echo "使用方法:"
    echo "  cd ~/python_crawler"
    echo "  uv run python main.py --headless --pages 2 --products 10"
    echo ""
    echo "定时任务 (crontab -e):"
    echo "  0 3 * * * cd ~/python_crawler && ./run_server.sh >> logs/cron.log 2>&1"
    echo ""
else
    echo ""
    echo "❌ 测试失败，请检查错误信息"
    echo ""
    echo "运行验证脚本:"
    echo "  uv run python verify_deployment.py"
    echo ""
fi
