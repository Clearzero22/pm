#!/usr/bin/env bash
#
# 快速同步脚本
# 用法: ./sync.sh [commit message]
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }

DOTFILES="$HOME/.dotfiles"

# 检查目录
if [ ! -d "$DOTFILES" ]; then
    echo "错误: ~/.dotfiles 不存在"
    exit 1
fi

cd "$DOTFILES"

# 拉取最新
info "拉取最新配置..."
git pull --rebase

# 检查 PM 配置变更
if [ -f ".pm/projects.yaml" ]; then
    git add .pm/projects.yaml
fi

if [ -f ".pm/tools.yaml" ]; then
    git add .pm/tools.yaml
fi

# 提交
if [ -n "$1" ]; then
    git commit -m "$1"
    success "已提交: $1"
else
    git commit -m "Update pm config $(date +%Y-%m-%d)"
    success "已提交配置更新"
fi

# 推送
info "推送到 GitHub..."
git push

success "同步完成！"
