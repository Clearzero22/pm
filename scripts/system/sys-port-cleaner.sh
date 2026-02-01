#!/usr/bin/env bash
#
# 名称：sys-port-cleaner
# 用途：检测并清理指定端口占用的进程
# 依赖：lsof, kill
# 作者：clearzero22
# 日期：2025-02-01
# 版本：1.0.0
#
# 使用示例：
#   ./sys-port-cleaner.sh 3000              # 清理 3000 端口
#   ./sys-port-cleaner.sh --list            # 列出所有占用端口
#   ./sys-port-cleaner.sh --help            # 显示帮助
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 显示帮助信息
show_help() {
    cat << HELP
用法: sys-port-cleaner [选项] [端口]

选项:
  -h, --help              显示此帮助信息
  -l, --list              列出所有监听端口
  -p, --port <端口>       清理指定端口
  -f, --force             强制清理（不询问确认）

示例:
  sys-port-cleaner 3000              # 清理 3000 端口
  sys-port-cleaner --list            # 列出所有占用端口
  sys-port-cleaner -p 8080 -f        # 强制清理 8080 端口
HELP
}

# 列出所有监听端口
list_ports() {
    info "当前监听端口列表："
    echo ""
    
    if ! command -v lsof &> /dev/null; then
        error "需要安装 lsof 命令"
        return 1
    fi
    
    lsof -i -P -n | grep LISTEN || {
        warning "没有找到监听中的端口"
        return 0
    }
}

# 清理指定端口
clean_port() {
    local port=$1
    local force=$2
    
    if [ -z "$port" ]; then
        error "请指定端口号"
        return 1
    fi
    
    # 检查端口号是否为数字
    if ! [[ "$port" =~ ^[0-9]+$ ]]; then
        error "端口号必须是数字"
        return 1
    fi
    
    # 检查端口范围
    if [ "$port" -lt 1 ] || [ "$port" -gt 65535 ]; then
        error "端口号必须在 1-65535 范围内"
        return 1
    fi
    
    info "正在检查端口 $port ..."
    
    # 查找占用端口的进程
    local pid=$(lsof -ti:"$port" 2>/dev/null || true)
    
    if [ -z "$pid" ]; then
        success "端口 $port 未被占用"
        return 0
    fi
    
    # 获取进程信息
    local process_info=$(ps -p "$pid" -o pid,comm,args --no-headers 2>/dev/null || echo "N/A")
    
    echo ""
    warning "端口 $port 被以下进程占用："
    echo "  PID: $pid"
    echo "  进程: $process_info"
    echo ""
    
    # 询问确认
    if [ "$force" != "true" ]; then
        read -p "是否要终止该进程? [y/N] " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            info "操作已取消"
            return 0
        fi
    fi
    
    # 终止进程
    info "正在终止进程 $pid ..."
    
    if kill -9 "$pid" 2>/dev/null; then
        success "端口 $port 已清理"
        
        # 验证
        sleep 0.5
        local check_pid=$(lsof -ti:"$port" 2>/dev/null || true)
        if [ -z "$check_pid" ]; then
            success "端口 $port 确认已释放"
        else
            warning "端口 $port 可能仍被占用，请手动检查"
        fi
    else
        error "无法终止进程 $pid，请检查权限"
        return 1
    fi
}

# 解析命令行参数
MODE=""
PORT=""
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -l|--list)
            MODE="list"
            shift
            ;;
        -p|--port)
            PORT="$2"
            MODE="clean"
            shift 2
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -*)
            error "未知选项: $1"
            show_help
            exit 1
            ;;
        *)
            PORT="$1"
            MODE="clean"
            shift
            ;;
    esac
done

# 主逻辑
case $MODE in
    "list")
        list_ports
        ;;
    "clean")
        clean_port "$PORT" "$FORCE"
        ;;
    "")
        if [ -z "$PORT" ]; then
            show_help
        else
            clean_port "$PORT" "$FORCE"
        fi
        ;;
    *)
        show_help
        ;;
esac
