#!/bin/bash
# Linux 服务器快速部署脚本
# 支持 Ubuntu/Debian 和 CentOS/RHEL

set -e

echo "========================================="
echo "  Amazon Crawler - Linux 部署"
echo "========================================="
echo ""

# 检测 Linux 发行版
echo "📱 检测 Linux 发行版..."
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
    VERSION=$VERSION_ID
    echo "   发行版: $DISTRO $VERSION"
else
    echo "   无法检测发行版"
    DISTRO="unknown"
fi

ARCH=$(uname -m)
echo "   架构: $ARCH"
echo ""

# 根据发行版安装依赖
if [ "$DISTRO" = "ubuntu" ] || [ "$DISTRO" = "debian" ]; then
    # Ubuntu/Debian
    echo "1️⃣  Ubuntu/Debian 系统准备..."

    echo "   更新系统..."
    sudo apt update
    sudo apt upgrade -y

    echo "   安装基础工具..."
    sudo apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        git \
        curl \
        wget \
        vim

    echo "   安装 Playwright 依赖..."
    sudo apt install -y \
        libatk-bridge2.0-0 \
        libxkbcommon0 \
        libgbm \
        libnss3 \
        libxcomposite1 \
        libxdamage1 \
        libxrandr2 \
        libasound2

elif [ "$DISTRO" = "centos" ] || [ "$DISTRO" = "rhel" ] || [ "$DISTRO" = "fedora" ]; then
    # CentOS/RHEL
    echo "1️⃣  CentOS/RHEL 系统准备..."

    # 启用 EPEL (CentOS 7)
    if [ "$DISTRO" = "centos" ] || [ "$DISTRO" = "rhel" ]; then
        sudo yum install -y epel-release
    fi

    echo "   更新系统..."
    sudo yum update -y

    echo "   安装基础工具..."
    sudo yum install -y \
        python3 \
        python3-devel \
        python3-pip \
        git \
        curl \
        wget

    echo "   安装 Playwright 依赖..."
    sudo yum install -y \
        alsa-lib \
        atk \
        cups-libs \
        gtk3 \
        libXcomposite \
        libXcursor \
        libXdamage \
        libXext \
        libXi \
        libXrandr \
        libXScrnSaver \
        libXtst \
        pango \
        xorg-x11-fonts-100dpi \
        xorg-x11-fonts-75dpi \
        xorg-x11-utils \
        nss \
        libgbm
else
    echo "⚠️  未知的发行版，尝试通用安装..."
    # 通用安装
    sudo apt install -y python3 python3-pip git curl || \
    sudo yum install -y python3 python3-pip git curl
fi

echo "✅ 系统准备完成"
echo ""

# 安装 uv
echo "2️⃣  安装 uv 包管理器..."
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    echo "✅ uv 安装完成"
else
    echo "✅ uv 已安装"
fi
echo ""

# 优化系统配置
echo "3️⃣ 优化系统配置..."

# 增加 SWAP
if [ ! -f /swapfile ]; then
    echo "   创建 SWAP 文件..."
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "✅ SWAP 已创建 (2GB)"
else
    echo "✅ SWAP 已存在"
fi

# 文件描述符限制
echo "   配置文件描述符限制..."
echo '* soft nofile 65536' | sudo tee -a /etc/security/limits.conf
echo '* hard nofile 65536' | sudo tee -a /etc/security/limits.conf
echo "✅ 文件描述符限制已配置"

echo ""

# 部署项目
echo "4️⃣  部署项目..."

# 检查项目目录
if [ ! -d "python_crawler" ]; then
    echo "   项目目录不存在，请先部署项目："
    echo ""
    echo "   # 使用 Git"
    echo "   git clone <your-repo-url>"
    echo ""
    echo "   # 或上传项目"
    echo "   scp -r python_crawler/ user@server:/path/to/"
    echo ""
    exit 1
fi

cd python_crawler

# 安装依赖
echo "   安装 Python 依赖..."
uv sync

# 安装浏览器
echo "   安装 Playwright 浏览器..."
uv run playwright install chromium

echo ""
echo "✅ 部署完成！"
echo ""

# 创建日志目录
mkdir -p logs

# 配置防火墙 (如果需要)
if command -v ufw &> /dev/null; then
    echo "5️⃣  配置防火墙..."
    sudo ufw allow 22
    sudo ufw allow 80
    sudo ufw allow 443
    sudo ufw --force enable
    echo "✅ 防火墙已配置"
fi

# 测试运行
echo "6️⃣  测试运行..."
echo "   运行快速测试 (1个商品)..."
uv run python main.py --pages 1 --products 1 --headless

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "🎉 Linux 部署成功！"
    echo "========================================="
    echo ""
    echo "使用方法:"
    echo "  cd python_crawler"
    echo "  uv run python main.py --headless --pages 2 --products 20"
    echo ""
    echo "定时任务 (crontab -e):"
    echo "  0 2 * * * cd /path/to/python_crawler && uv run python main.py --headless >> logs/cron.log 2>&1"
    echo ""

    # 询问是否设置定时任务
    read -p "是否设置定时任务? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "请编辑 crontab:"
        echo "  crontab -e"
        echo ""
        echo "添加以下内容 (每天凌晨 2 点运行):"
        echo "  0 2 * * * cd $(pwd) && uv run python main.py --headless --pages 2 --products 10 >> logs/cron.log 2>&1"
    fi
else
    echo ""
    echo "❌ 测试失败，请检查错误信息"
    echo ""
    echo "运行验证脚本:"
    echo "  uv run python verify_deployment.py"
    echo ""
fi
