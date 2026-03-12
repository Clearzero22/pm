#!/bin/bash
# Mac 快速部署脚本
# 支持 Intel 和 Apple Silicon (M1/M2/M3)

set -e

echo "========================================="
echo "  Amazon Crawler - Mac 部署"
echo "========================================="
echo ""

# 检测 Mac 型号
echo "📱 检测 Mac 信息..."
ARCH=$(uname -m)

if [ "$ARCH" = "arm64" ]; then
    CHIP="Apple Silicon (M1/M2/M3)"
else
    CHIP="Intel"
fi

echo "   架构: $ARCH ($CHIP)"

# 检测 macOS 版本
if [ "$(sw_vers)" ]; then
    VERSION=$(sw_vers -productVersion)
    echo "   版本: macOS $VERSION"
fi

echo ""

# 检查 Homebrew
echo "1️⃣  检查 Homebrew..."
if ! command -v brew &> /dev/null; then
    echo "   Homebrew 未安装，正在安装..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # 更新 PATH
    if [ -f "/opt/homebrew/bin/brew" ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        eval "$(/usr/local/bin/brew shellenv)"
    fi
else
    echo "✅ Homebrew 已安装"
    brew --version
fi
echo ""

# 安装 Python
echo "2️⃣  安装 Python 3.14..."
if ! command -v python3.14 &> /dev/null; then
    echo "   安装 Python 3.14..."
    brew install python@3.14

    # 创建链接
    brew unlink python@3.14 2>/dev/null || true
    brew link python@3.14

    echo "✅ Python 3.14 安装完成"
else
    echo "✅ Python 3.14 已安装"
    python3.14 --version
fi
echo ""

# 安装 uv
echo "3️⃣  安装 uv 包管理器..."
if ! command -v uv &> /dev/null; then
    echo "   安装 uv..."
    pip3 install uv
    echo "✅ uv 安装完成"
else
    echo "✅ uv 已安装"
    uv --version
fi
echo ""

# 安装 Git (如果需要)
if ! command -v git &> /dev/null; then
    echo "   安装 Git..."
    brew install git
    echo "✅ Git 安装完成"
fi
echo ""

# 部署项目
echo "4️⃣  部署项目..."

# 检查或创建项目目录
PROJECT_DIR="$HOME/projects/python_crawler"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "   创建项目目录..."
    mkdir -p "$HOME/projects"
    echo ""
    echo "   请选择安装方式:"
    echo "   1. Git 克隆"
    echo "   2. 从现有文件夹复制"
    echo ""
    read -p "选择 (1/2): " -n 1 -r
    echo ""

    if [ "$REPLY" = "1" ]; then
        echo "   请提供 Git 仓库地址:"
        read -p "   URL: " repo_url
        echo ""
        cd "$HOME/projects"
        git clone "$repo_url" python_crawler
    else
        echo "   请输入项目文件夹路径:"
        read -e -p "   路径: " src_path
        echo ""
        mkdir -p "$HOME/projects"
        cp -r "$src_path" "$PROJECT_DIR"
    fi
fi

cd "$PROJECT_DIR"

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

# 测试运行
echo "5️⃣  测试运行..."
echo "   运行快速测试 (1个商品)..."
uv run python main.py --pages 1 --products 1 --headless

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "🎉 Mac 部署成功！"
    echo "========================================="
    echo ""
    echo "使用方法:"
    echo "  cd $PROJECT_DIR"
    echo "  uv run python main.py --headless --pages 2 --products 20"
    echo ""

    # 询问是否设置定时任务
    read -p "是否设置定时任务 (launchd)? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 创建 launchd plist
        cat > ~/Library/LaunchAgents/com.amazon.crawler.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.amazon.crawler</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/zsh</string>
        <string>-c</string>
        <string>cd $PROJECT_DIR && uv run python main.py --headless --pages 2 --products 10</string>
    </array>
    <key>StartCalendarInterval</key>
    <integer>86400</integer>
    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/logs/cron.log</string>
    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/logs/cron.error</string>
</dict>
</plist>
EOF

        echo ""
        echo "✅ launchd 配置已创建"
        echo ""
        echo "加载定时任务:"
        echo "  launchctl load ~/Library/LaunchAgents/com.amazon.crawler.plist"
        echo ""
        echo "立即运行:"
        echo "  launchctl start com.amazon.crawler"
        echo ""
        echo "卸载定时任务:"
        echo "  launchctl unload ~/Library/LaunchAgents/com.amazon.crawler.plist"
    fi
else
    echo ""
    echo "❌ 测试失败，请检查错误信息"
    echo ""
    echo "运行验证脚本:"
    echo "  uv run python verify_deployment.py"
    echo ""
fi
