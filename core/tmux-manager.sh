#!/usr/bin/env bash
#
# 名称：tmux-manager.sh
# 用途：tmux 会话管理器（创建、附加、销毁会话）
# 依赖：tmux, core/config.sh
# 作者：clearzero22
# 日期：2025-02-01
# 版本：1.0.0
#

# Source dependencies
# 注意：PROJECT_ROOT 由 pm 主脚本导出
source "$PROJECT_ROOT/core/platform.sh"
source "$PROJECT_ROOT/core/config.sh"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# 工具函数
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查 tmux 是否可用
check_tmux() {
    if ! pm_has_tmux; then
        error "tmux 未安装。请先安装 tmux:"
        echo "  Linux: sudo apt install tmux 或 sudo yum install tmux"
        echo "  macOS: brew install tmux"
        echo "  Termux: pkg install tmux"
        return 1
    fi
    return 0
}

# 获取会话名称
pm_tmux_session_name() {
    local project_id="$1"
    echo "pm-${project_id}"
}

# 检查会话是否存在
pm_tmux_session_exists() {
    local session_name="$1"
    tmux has-session -t "$session_name" 2>/dev/null
    return $?
}

# 创建新会话
pm_tmux_create_session() {
    local session_name="$1"
    local path="$2"
    
    check_tmux || return 1
    
    if pm_tmux_session_exists "$session_name"; then
        warning "会话 '$session_name' 已存在"
        return 0
    fi
    
    info "创建 tmux 会话: $session_name"
    tmux new-session -d -s "$session_name" -c "$path"
    success "会话创建成功"
}

# 附加到会话
pm_tmux_attach_session() {
    local session_name="$1"
    
    check_tmux || return 1
    
    if ! pm_tmux_session_exists "$session_name"; then
        error "会话 '$session_name' 不存在"
        return 1
    fi
    
    info "附加到会话: $session_name"
    tmux attach-session -t "$session_name"
}

# 创建布局会话（AI 开发模式）
pm_tmux_create_layout_dev_ai() {
    local session_name="$1"
    local path="$2"
    local editor="${3:-zed}"
    local ai_tool="${4:-claude}"
    local terminal="${5:-zsh}"
    
    check_tmux || return 1
    
    # 如果会话已存在，直接附加
    if pm_tmux_session_exists "$session_name"; then
        info "会话已存在，直接附加"
        pm_tmux_attach_session "$session_name"
        return 0
    fi
    
    info "创建 AI 开发会话: $session_name"
    
    # 创建新会话
    tmux new-session -d -s "$session_name" -c "$path"
    
    # 垂直分割（左: 编辑器, 右: AI + 终端）
    tmux split-window -h -t "$session_name" -p 50 -c "$path"
    
    # 在右侧水平分割（上: AI, 下: 终端）
    tmux split-window -v -t "$session_name:0.1" -p 50 -c "$path"
    
    # 左窗格：启动编辑器（如果是 GUI 编辑器，打开新窗口）
    if pm_is_gui; then
        # GUI 编辑器，发送到后台
        (cd "$path" && $editor . &>/dev/null &)
        # 窗格切换到 zsh
        tmux send-keys -t "$session_name:0.0" "$terminal" C-m
    else
        # 终端编辑器
        tmux send-keys -t "$session_name:0.0" "$editor ." C-m
    fi
    
    # 右上窗格：启动 AI 工具
    tmux send-keys -t "$session_name:0.1" "$ai_tool --agent" C-m
    
    # 右下窗格：启动终端
    tmux send-keys -t "$session_name:0.2" "$terminal" C-m
    
    # 选择 AI 窗格
    tmux select-pane -t "$session_name:0.1"
    
    success "AI 开发会话创建成功"
    
    # 自动附加
    pm_tmux_attach_session "$session_name"
}

# 创建标准开发布局
pm_tmux_create_layout_dev_standard() {
    local session_name="$1"
    local path="$2"
    local editor="${3:-zed}"
    local terminal="${4:-zsh}"
    
    check_tmux || return 1
    
    if pm_tmux_session_exists "$session_name"; then
        pm_tmux_attach_session "$session_name"
        return 0
    fi
    
    info "创建标准开发会话: $session_name"
    
    # 创建新会话
    tmux new-session -d -s "$session_name" -c "$path"
    
    # 垂直分割
    tmux split-window -h -t "$session_name" -p 30 -c "$path"
    
    # 左窗格：编辑器
    if pm_is_gui; then
        (cd "$path" && $editor . &>/dev/null &)
        tmux send-keys -t "$session_name:0.0" "$terminal" C-m
    else
        tmux send-keys -t "$session_name:0.0" "$editor ." C-m
    fi
    
    # 右窗格：终端
    tmux send-keys -t "$session_name:0.1" "$terminal" C-m
    
    # 选择终端窗格
    tmux select-pane -t "$session_name:0.1"
    
    success "标准开发会话创建成功"
    pm_tmux_attach_session "$session_name"
}

# 创建学习布局
pm_tmux_create_layout_learning() {
    local session_name="$1"
    local path="$2"
    local editor="${3:-nvim}"
    local terminal="${4:-zsh}"
    
    check_tmux || return 1
    
    if pm_tmux_session_exists "$session_name"; then
        pm_tmux_attach_session "$session_name"
        return 0
    fi
    
    info "创建学习会话: $session_name"
    
    # 创建新会话
    tmux new-session -d -s "$session_name" -c "$path"
    
    # 水平分割（上: 笔记/编辑器, 下: 终端）
    tmux split-window -v -t "$session_name" -p 30 -c "$path"
    
    # 上窗格：编辑器
    tmux send-keys -t "$session_name:0.0" "$editor ." C-m
    
    # 下窗格：终端
    tmux send-keys -t "$session_name:0.1" "$terminal" C-m
    
    success "学习会话创建成功"
    pm_tmux_attach_session "$session_name"
}

# 创建阅读布局
pm_tmux_create_layout_reading() {
    local session_name="$1"
    local path="$2"
    local terminal="${3:-zsh}"
    
    check_tmux || return 1
    
    if pm_tmux_session_exists "$session_name"; then
        pm_tmux_attach_session "$session_name"
        return 0
    fi
    
    info "创建阅读会话: $session_name"
    
    # 创建新会话
    tmux new-session -d -s "$session_name" -c "$path"
    
    # 垂直分割（左: 文件查看, 右: 笔记/终端）
    tmux split-window -h -t "$session_name" -p 50 -c "$path"
    
    # 左窗格：显示文件列表
    tmux send-keys -t "$session_name:0.0" "ls -la" C-m
    
    # 右窗格：终端
    tmux send-keys -t "$session_name:0.1" "$terminal" C-m
    
    success "阅读会话创建成功"
    pm_tmux_attach_session "$session_name"
}

# 销毁会话
pm_tmux_kill_session() {
    local session_name="$1"
    
    check_tmux || return 1
    
    if ! pm_tmux_session_exists "$session_name"; then
        warning "会话 '$session_name' 不存在"
        return 0
    fi
    
    read -p "确认销毁会话 '$session_name'? [y/N] " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        tmux kill-session -t "$session_name"
        success "会话已销毁"
    else
        info "操作已取消"
    fi
}

# 列出所有会话
pm_tmux_list_sessions() {
    check_tmux || return 1
    
    local sessions=$(tmux list-sessions 2>/dev/null)
    
    if [ -z "$sessions" ]; then
        info "没有活动的 tmux 会话"
        return 0
    fi
    
    echo ""
    echo "${CYAN}🖥️  活动的 tmux 会话${NC}"
    echo ""
    echo "$sessions"
    echo ""
}

# 根据预设创建布局
pm_tmux_create_from_preset() {
    local preset="$1"
    local session_name="$2"
    local path="$3"
    shift 3
    local tools=("$@")
    
    case "$preset" in
        dev-ai)
            pm_tmux_create_layout_dev_ai "$session_name" "$path" "${tools[0]:-zed}" "${tools[1]:-claude}" "${tools[2]:-zsh}"
            ;;
        dev-standard)
            pm_tmux_create_layout_dev_standard "$session_name" "$path" "${tools[0]:-zed}" "${tools[1]:-zsh}"
            ;;
        learning)
            pm_tmux_create_layout_learning "$session_name" "$path" "${tools[0]:-nvim}" "${tools[1]:-zsh}"
            ;;
        reading)
            pm_tmux_create_layout_reading "$session_name" "$path" "${tools[0]:-zsh}"
            ;;
        *)
            error "未知的预设: $preset"
            return 1
            ;;
    esac
}

# 检查是否在 tmux 会话中
pm_tmux_in_session() {
    [ -n "$TMUX" ]
}

# 获取当前会话名称
pm_tmux_current_session() {
    if pm_tmux_in_session; then
        tmux display-message -p '#S'
    fi
}

# 如果直接运行此脚本
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # 检查 PROJECT_ROOT
    if [ -z "$PROJECT_ROOT" ]; then
        echo "ERROR: PROJECT_ROOT not set. Please run via 'pm' script."
        exit 1
    fi
    
    case "${1:-list}" in
        list|ls)
            pm_tmux_list_sessions
            ;;
        attach)
            shift
            pm_tmux_attach_session "$@"
            ;;
        kill)
            shift
            pm_tmux_kill_session "$@"
            ;;
        create)
            shift
            pm_tmux_create_session "$@"
            ;;
        dev-ai)
            shift
            pm_tmux_create_layout_dev_ai "$@"
            ;;
        dev-standard)
            shift
            pm_tmux_create_layout_dev_standard "$@"
            ;;
        learning)
            shift
            pm_tmux_create_layout_learning "$@"
            ;;
        reading)
            shift
            pm_tmux_create_layout_reading "$@"
            ;;
        *)
            echo "Usage: $0 <list|attach|kill|create|dev-ai|dev-standard|learning|reading>"
            ;;
    esac
fi
