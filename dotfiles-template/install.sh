#!/usr/bin/env bash
#
# PM 跨平台安装脚本
# 支持: Linux, macOS, Termux
#

set -e

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检测平台
detect_platform() {
    if [[ -n "$TERMUX_VERSION" ]]; then
        echo "termux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    else
        echo "unknown"
    fi
}

PLATFORM=$(detect_platform)
info "检测到平台: $PLATFORM"

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PM_DIR="$SCRIPT_DIR/pm"

# 检查 pm 是否存在
if [ ! -d "$PM_DIR" ]; then
    info "PM 未安装，正在克隆..."
    if command -v git &> /dev/null; then
        git clone https://github.com/Clearzero22/pm.git "$PM_DIR"
    else
        error "需要 Git 来安装 PM"
        exit 1
    fi
fi

# 创建符号链接到 ~/.local/bin
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

if [ ! -L "$BIN_DIR/pm" ]; then
    ln -sf "$PM_DIR/pm" "$BIN_DIR/pm"
    success "已创建符号链接: $BIN_DIR/pm"
fi

# 确保 ~/.local/bin 在 PATH 中
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    info "添加 ~/.local/bin 到 PATH..."

    case "$SHELL" in
        */zsh)
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
            info "已添加到 ~/.zshrc"
            ;;
        */bash)
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
            info "已添加到 ~/.bashrc"
            ;;
        *)
            warning "请手动添加以下内容到你的 shell 配置:"
            echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
            ;;
    esac
fi

# 配置目录
CONFIG_DIR="$HOME/.pm"
mkdir -p "$CONFIG_DIR"

# 复制配置文件（如果不存在）
if [ ! -f "$CONFIG_DIR/projects.yaml" ]; then
    cp "$SCRIPT_DIR/.pm/projects.yaml" "$CONFIG_DIR/"
    success "已创建项目配置"
else
    info "项目配置已存在，跳过"
fi

if [ ! -f "$CONFIG_DIR/tools.yaml" ]; then
    cp "$SCRIPT_DIR/.pm/tools.yaml" "$CONFIG_DIR/"
    success "已创建工具配置"
else
    info "工具配置已存在，跳过"
fi

# 平台特定配置
case "$PLATFORM" in
    termux)
        info "Termux 特定配置..."
        # Termux 需要的包
        if ! command -v python &> /dev/null; then
            info "安装 Python (用于 YAML 解析)..."
            pkg install python -y
        fi
        ;;
    macos)
        info "macOS 特定配置..."
        # Homebrew 检查
        if ! command -v brew &> /dev/null; then
            info "建议安装 Homebrew: https://brew.sh"
        fi
        ;;
    linux)
        info "Linux 特定配置..."
        # 检查桌面环境
        if [ -n "$WAYLAND_DISPLAY" ] || [ -n "$DISPLAY" ]; then
            info "检测到桌面环境"
        else
            info "服务器环境（无 GUI）"
        fi
        ;;
esac

# 初始化配置
info "初始化 PM 配置..."
"$BIN_DIR/pm" config init

success "PM 安装完成！"
echo ""
echo "使用方法:"
echo "  pm list          # 列出项目"
echo "  pm add -i        # 添加项目"
echo "  pm open <id>     # 打开项目"
echo ""
echo "请重启终端或运行: source ~/.${SHELL##*/}rc"
