#!/usr/bin/env bash
#
# 一键设置你的 dotfiles 仓库
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

info() { echo -e "${CYAN}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查参数
REPO_NAME="${1:-my-dotfiles}"

info "创建你的 dotfiles 仓库..."

# 创建目录
DOTFILES_DIR="$HOME/$REPO_NAME"
if [ -d "$DOTFILES_DIR" ]; then
    error "目录已存在: $DOTFILES_DIR"
    exit 1
fi

mkdir -p "$DOTFILES_DIR"
cd "$DOTFILES_DIR"

# 初始化 Git
git init

# 复制模板
TEMPLATE_DIR="$(dirname "${BASH_SOURCE[0]}")"
cp -r "$TEMPLATE_DIR/.pm" "$DOTFILES_DIR/"
cp "$TEMPLATE_DIR/install.sh" "$DOTFILES_DIR/"
cp "$TEMPLATE_DIR/sync.sh" "$DOTFILES_DIR/"
cp "$TEMPLATE_DIR/README.md" "$DOTFILES_DIR/"

# 添加 PM 作为子模块
info "添加 PM 作为子模块..."
git submodule add https://github.com/Clearzero22/pm.git pm

# 初始提交
git add .
git commit -m "Initial dotfiles setup with PM"

success "dotfiles 创建完成: $DOTFILES_DIR"

echo ""
info "下一步:"
echo "  1. 创建 GitHub 仓库:"
echo "     gh repo create $REPO_NAME --private --source=$DOTFILES_DIR --push"
echo ""
echo "  2. 在其他设备上:"
echo "     git clone --recurse-submodules https://github.com/YOUR_USERNAME/$REPO_NAME.git ~/.dotfiles"
echo "     cd ~/.dotfiles && bash install.sh"
echo ""
echo "  3. 快速同步:"
echo "     bash ~/.dotfiles/sync.sh 'update config'"
