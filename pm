#!/usr/bin/env bash
#
# 名称：pm (Project Manager)
# 用途：跨平台项目管理器主入口
# 依赖：core/*, ui/*
# 作者：clearzero22
# 日期：2025-02-01
# 版本：1.0.0
#

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PROJECT_ROOT

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# 工具函数
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 初始化环境
pm_init() {
    # Source core modules
    source "$PROJECT_ROOT/core/platform.sh"
    source "$PROJECT_ROOT/core/config.sh"
    source "$PROJECT_ROOT/core/project-registry.sh"
    source "$PROJECT_ROOT/core/tmux-manager.sh"
    source "$PROJECT_ROOT/ui/fzf-selector.sh"
    
    # 初始化配置
    pm_config_init
}

# 显示帮助信息
pm_show_help() {
    cat << HELP
${BOLD}${CYAN}Project Manager (pm) - 跨平台项目管理器${NC}

${BOLD}用法:${NC}
  pm [命令] [选项]

${BOLD}命令:${NC}
  ${BOLD}项目管理:${NC}
    pm list, ls                      列出所有项目
    pm select                        使用 fzf 选择项目
    pm open <project-id>             打开项目（使用默认工具）
    pm start <project-id>            启动完整环境（tmux会话）
    pm add                           添加新项目
    pm add -i, --interactive         交互式添加项目
    pm edit <project-id>             编辑项目配置
    pm remove <project-id>           删除项目
    pm info <project-id>             显示项目详情
    pm search <query>                搜索项目

  ${BOLD}环境管理:${NC}
    pm session list                  列出 tmux 会话
    pm session attach <name>         附加到会话
    pm session kill <name>           销毁会话

  ${BOLD}配置管理:${NC}
    pm config                        编辑配置
    pm config init                   初始化配置
    pm preset list                   列出可用预设

  ${BOLD}其他:${NC}
    pm help                          显示此帮助信息
    pm version                       显示版本信息
    pm info                          显示系统信息

${BOLD}示例:${NC}
  pm                                 # 显示主菜单
  pm select                          # 使用 fzf 选择项目
  pm start my-app                    # 启动项目的完整环境
  pm add -i                          # 交互式添加项目
  pm search rust                     # 搜索包含 'rust' 的项目

${BOLD}项目主页:${NC} https://github.com/your-username/pm-project-manager
HELP
}

# 显示主菜单
pm_show_main_menu() {
    echo ""
    echo "${BOLD}${CYAN}📦 Project Manager${NC}"
    echo ""
    
    # 如果有 fzf，使用 fzf 菜单
    if pm_has_fzf; then
        local choice=$(bash "$PROJECT_ROOT/ui/fzf-selector.sh" menu)
        case "$choice" in
            open) pm_select_and_open ;;
            list) pm_list_projects ;;
            add) pm_add_project_interactive ;;
            search) pm_search_project_interactive ;;
            delete) pm_delete_project_interactive ;;
            config) pm_config_edit projects ;;
            stats) pm_show_stats ;;
            sync) pm_config_sync ;;
        esac
    else
        # 备用文本菜单
        echo "${CYAN}1)${NC} 📂 打开项目"
        echo "${CYAN}2)${NC} 📋 列出所有项目"
        echo "${CYAN}3)${NC} ➕ 添加新项目"
        echo "${CYAN}4)${NC} 🔍 搜索项目"
        echo "${CYAN}5)${NC} 🗑️  删除项目"
        echo "${CYAN}6)${NC} ⚙️  编辑配置"
        echo "${CYAN}7)${NC} ℹ️  系统信息"
        echo "${CYAN}0)${NC} 🚪 退出"
        echo ""
        
        read -p "选择 [0-7]: " choice
        
        case "$choice" in
            1) pm_select_and_open ;;
            2) pm_list_projects ;;
            3) pm_add_project_interactive ;;
            4) pm_search_project_interactive ;;
            5) pm_delete_project_interactive ;;
            6) pm_config_edit projects ;;
            7) pm_show_info ;;
            0|q|Q) echo "再见！"; exit 0 ;;
            *) error "无效选择" ;;
        esac
    fi
}

# 选择并打开项目
pm_select_and_open() {
    local project_id
    
    if pm_has_fzf; then
        project_id=$(bash "$PROJECT_ROOT/ui/fzf-selector.sh" select)
    else
        pm_list_projects
        read -p "输入项目 ID: " project_id
    fi
    
    if [ -n "$project_id" ]; then
        pm_open_project "$project_id"
    fi
}

# 打开项目
pm_open_project() {
    local project_id="$1"
    
    if ! pm_project_exists "$project_id"; then
        error "项目 '$project_id' 不存在"
        return 1
    fi
    
    # 获取项目路径
    local path=$(pm_project_get_path "$project_id")
    
    if [ -z "$path" ]; then
        error "无法获取项目路径"
        return 1
    fi
    
    # 更新访问时间
    pm_project_update_access "$project_id"
    
    # 进入项目目录
    cd "$path"
    
    success "进入项目: $project_id"
    echo "  路径: $path"
    echo ""
    info "当前目录: $(pwd)"
}

# 启动项目（完整环境）
pm_start_project() {
    local project_id="$1"
    
    if ! pm_project_exists "$project_id"; then
        error "项目 '$project_id' 不存在"
        return 1
    fi
    
    # 获取项目信息
    local info=$(pm_project_get_info "$project_id")
    
    # 获取项目路径
    local path=$(pm_project_get_path "$project_id")
    
    # 获取预设（从配置或默认）
    local preset="dev-standard"
    if command -v yq &> /dev/null; then
        preset=$(yq eval ".projects[] | select(.id == \"$project_id\") | .preset // \"dev-standard\"" "$PM_PROJECTS_FILE")
    fi
    
    # 获取工具配置
    local editor="zed"
    local terminal="zsh"
    local ai_tool=""
    
    if command -v yq &> /dev/null; then
        editor=$(yq eval ".projects[] | select(.id == \"$project_id\") | .tools.editor // \"zed\"" "$PM_PROJECTS_FILE")
        terminal=$(yq eval ".projects[] | select(.id == \"$project_id\") | .tools.terminal // \"zsh\"" "$PM_PROJECTS_FILE")
        ai_tool=$(yq eval ".projects[] | select(.id == \"$project_id\") | .tools.ai // \"\"" "$PM_PROJECTS_FILE")
    fi
    
    # 根据预设启动
    local session_name=$(pm_tmux_session_name "$project_id")
    
    if pm_has_tmux; then
        case "$preset" in
            dev-ai)
                pm_tmux_create_layout_dev_ai "$session_name" "$path" "$editor" "$ai_tool" "$terminal"
                ;;
            learning)
                pm_tmux_create_layout_learning "$session_name" "$path" "$editor" "$terminal"
                ;;
            reading)
                pm_tmux_create_layout_reading "$session_name" "$path" "$terminal"
                ;;
            *)
                pm_tmux_create_layout_dev_standard "$session_name" "$path" "$editor" "$terminal"
                ;;
        esac
    else
        # 无 tmux，直接打开
        pm_open_project "$project_id"
    fi
}

# 添加项目
pm_add_project_interactive() {
    pm_project_add_interactive
}

# 搜索项目
pm_search_project_interactive() {
    read -p "输入搜索关键词: " query
    if [ -n "$query" ]; then
        pm_project_search "$query"
    fi
}

# 删除项目
pm_delete_project_interactive() {
    local project_id
    
    if pm_has_fzf; then
        project_id=$(bash "$PROJECT_ROOT/ui/fzf-selector.sh" select)
    else
        pm_list_projects
        read -p "输入项目 ID: " project_id
    fi
    
    if [ -n "$project_id" ]; then
        pm_project_remove "$project_id"
    fi
}

# 列出项目
pm_list_projects() {
    pm_project_list
}

# 显示统计信息
pm_show_stats() {
    echo ""
    echo "${CYAN}📊 统计信息${NC}"
    echo ""
    
    local total=$(pm_project_count)
    echo "  总项目数: $total"
    
    # 按分类统计
    if command -v yq &> /dev/null; then
        echo ""
        echo "  按分类:"
        yq eval '.categories[] | "    - \(.name): \(.projects | map(select(.category == .id)) | length)"' "$PM_PROJECTS_FILE" 2>/dev/null || true
    fi
    
    echo ""
}

# 显示系统信息
pm_show_info() {
    echo ""
    echo "${CYAN}ℹ️  系统信息${NC}"
    echo ""
    pm_platform_info
    echo ""
}

# 显示版本信息
pm_show_version() {
    echo "pm (Project Manager) 1.0.0"
    echo ""
    echo "Copyright (c) 2025 clearzero22"
    echo "Licensed under MIT"
}

# 配置同步（占位）
pm_config_sync() {
    echo ""
    info "配置同步功能开发中..."
    echo ""
}

# 主函数
pm_main() {
    # 初始化
    pm_init
    
    # 解析命令
    local command="${1:-}"
    shift 2>/dev/null || true
    
    case "$command" in
        ""|-h|--help|help)
            pm_show_help
            ;;
        -v|--version|version)
            pm_show_version
            ;;
        list|ls)
            pm_list_projects
            ;;
        select)
            pm_select_and_open
            ;;
        open)
            pm_open_project "$@"
            ;;
        start)
            pm_start_project "$@"
            ;;
        add)
            if [ "$1" = "-i" ] || [ "$1" = "--interactive" ]; then
                pm_add_project_interactive
            else
                pm_project_add "$@"
            fi
            ;;
        edit)
            pm_project_get_info "$@"
            ;;
        remove|rm)
            pm_project_remove "$@"
            ;;
        info)
            if [ -n "$1" ]; then
                pm_project_get_info "$@"
            else
                pm_show_info
            fi
            ;;
        search)
            pm_project_search "$@"
            ;;
        session)
            local session_cmd="${1:-}"
            shift
            case "$session_cmd" in
                list|ls)
                    pm_tmux_list_sessions
                    ;;
                attach)
                    pm_tmux_attach_session "$@"
                    ;;
                kill)
                    pm_tmux_kill_session "$@"
                    ;;
                *)
                    echo "Usage: pm session <list|attach|kill>"
                    ;;
            esac
            ;;
        config)
            case "${1:-}" in
                init)
                    pm_config_init
                    success "配置已初始化"
                    ;;
                *)
                    pm_config_edit "${1:-projects}"
                    ;;
            esac
            ;;
        preset)
            case "${1:-list}" in
                list)
                    echo ""
                    echo "${CYAN}📦 可用预设${NC}"
                    echo ""
                    ls -1 "$PROJECT_ROOT/presets/" | sed 's/.yml$//' | sed 's/^/  /'
                    echo ""
                    ;;
            esac
            ;;
        *)
            # 如果是项目 ID，直接打开
            if pm_project_exists "$command"; then
                pm_open_project "$command"
            else
                # 显示主菜单
                pm_show_main_menu
            fi
            ;;
    esac
}

# 执行主函数
pm_main "$@"
