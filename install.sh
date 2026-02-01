#!/usr/bin/env bash
#
# 名称：install.sh
# 用途：一键安装常用脚本库
# 依赖：ln, rm, ls
# 作者：clearzero22
# 日期：2025-02-01
# 版本：1.0.0
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的信息
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 默认安装路径
DEFAULT_INSTALL_DIR="$HOME/bin"
INSTALL_DIR="$DEFAULT_INSTALL_DIR"

# 显示帮助信息
show_help() {
    cat << HELP
用法: ./install.sh [选项]

选项:
  -h, --help              显示此帮助信息
  -d, --dir <目录>        指定安装目录 (默认: ~/bin)
  -u, --uninstall         卸载所有脚本

示例:
  ./install.sh                    # 安装到 ~/bin
  ./install.sh -d /usr/local/bin  # 安装到 /usr/local/bin
  ./install.sh --uninstall        # 卸载所有脚本
HELP
}

# 卸载脚本
uninstall() {
    info "开始卸载脚本..."
    
    if [ ! -d "$INSTALL_DIR" ]; then
        warning "安装目录不存在: $INSTALL_DIR"
        exit 0
    fi
    
    # 获取所有脚本
    SCRIPTS=$(find scripts/ -type f -name "*.sh" -o -name "*.py")
    
    if [ -z "$SCRIPTS" ]; then
        warning "没有找到要卸载的脚本"
        exit 0
    fi
    
    for script in $SCRIPTS; do
        # 获取脚本名（去掉扩展名）
        name=$(basename "$script" | sed 's/\.sh$//' | sed 's/\.py$//')
        link="$INSTALL_DIR/$name"
        
        if [ -L "$link" ]; then
            rm "$link"
            info "已删除: $link"
        fi
    done
    
    success "卸载完成！"
}

# 检查依赖
check_dependencies() {
    local missing_deps=()
    
    # 基础依赖
    for cmd in ln rm; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        error "缺少依赖: ${missing_deps[*]}"
        return 1
    fi
    
    return 0
}

# 安装脚本
install_scripts() {
    info "开始安装脚本..."
    
    # 检查依赖
    if ! check_dependencies; then
        error "依赖检查失败，安装中止"
        exit 1
    fi
    
    # 创建安装目录
    if [ ! -d "$INSTALL_DIR" ]; then
        info "创建安装目录: $INSTALL_DIR"
        mkdir -p "$INSTALL_DIR"
    fi
    
    # 获取所有脚本
    SCRIPTS=$(find scripts/ -type f -name "*.sh" -o -name "*.py")
    
    if [ -z "$SCRIPTS" ]; then
        error "没有找到要安装的脚本"
        exit 1
    fi
    
    # 计数器
    local count=0
    local skipped=0
    
    # 遍历所有脚本
    for script in $SCRIPTS; do
        # 获取脚本名（去掉扩展名）
        name=$(basename "$script" | sed 's/\.sh$//' | sed 's/\.py$//')
        link="$INSTALL_DIR/$name"
        
        # 获取完整路径
        script_path="$(pwd)/$script"
        
        # 检查软链接是否存在
        if [ -L "$link" ]; then
            # 检查是否指向正确的路径
            current_target=$(readlink "$link")
            if [ "$current_target" = "$script_path" ]; then
                warning "已存在: $link (跳过)"
                ((skipped++))
            else
                info "更新: $link"
                rm "$link"
                ln -s "$script_path" "$link"
                ((count++))
            fi
        else
            # 创建软链接
            ln -s "$script_path" "$link"
            info "已安装: $link"
            ((count++))
        fi
    done
    
    echo ""
    success "安装完成！"
    echo ""
    echo "统计:"
    echo "  - 安装: $count 个"
    echo "  - 跳过: $skipped 个"
    echo "  - 安装目录: $INSTALL_DIR"
    echo ""
    
    # 检查 INSTALL_DIR 是否在 PATH 中
    if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
        warning "安装目录未在 PATH 中"
        echo ""
        info "请将以下内容添加到你的 ~/.bashrc 或 ~/.zshrc:"
        echo ""
        echo "  export PATH=\"\$PATH:$INSTALL_DIR\""
        echo ""
        info "然后运行: source ~/.bashrc (或 ~/.zshrc)"
    else
        success "安装目录已在 PATH 中"
    fi
}

# 解析命令行参数
UNINSTALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -d|--dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        -u|--uninstall)
            UNINSTALL=true
            shift
            ;;
        *)
            error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
done

# 主逻辑
if [ "$UNINSTALL" = true ]; then
    uninstall
else
    install_scripts
fi
