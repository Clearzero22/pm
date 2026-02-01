#!/usr/bin/env bash
#
# 名称：fzf-selector.sh
# 用途：fzf 项目选择器 UI
# 依赖：fzf, core/config.sh, core/project-registry.sh
# 作者：clearzero22
# 日期：2025-02-01
# 版本：1.0.0
#

# Source dependencies
# 注意：PROJECT_ROOT 由 pm 主脚本导出
source "$PROJECT_ROOT/core/config.sh"
source "$PROJECT_ROOT/core/project-registry.sh"
source "$PROJECT_ROOT/core/platform.sh"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# 检查 fzf 是否可用
check_fzf() {
    if ! pm_has_fzf; then
        echo "${RED}[ERROR]${NC} fzf 未安装。请先安装 fzf:"
        echo "  Linux/macOS: brew install fzf 或 sudo apt install fzf"
        echo "  Termux: pkg install fzf"
        return 1
    fi
    return 0
}

# 生成项目列表格式
format_projects_for_fzf() {
    local filter_category="${1:-}"
    
    if ! command -v yq &> /dev/null; then
        return 1
    fi
    
    # 按分类分组
    local categories=$(yq eval '.categories[] | .id' "$PM_PROJECTS_FILE" 2>/dev/null)
    
    for cat in $categories; do
        if [ -n "$filter_category" ] && [ "$cat" != "$filter_category" ]; then
            continue
        fi
        
        local cat_icon=$(yq eval '.categories[] | select(.id == "'"$cat"'") | .icon' "$PM_PROJECTS_FILE" 2>/dev/null)
        local cat_name=$(yq eval '.categories[] | select(.id == "'"$cat"'") | .name' "$PM_PROJECTS_FILE" 2>/dev/null)
        
        echo "# ${cat_icon} ${cat_name}"
        
        # 获取该分类下的项目
        yq eval '.projects[] | select(.category == "'"$cat"'") | "[\(.hotkey // "-")] \(.name) | \(.description // "无描述") | \(.path)"' "$PM_PROJECTS_FILE" 2>/dev/null | while IFS= read -r line; do
            echo "  $line"
        done
        
        echo ""
    done
}

# 生成项目预览信息
generate_preview() {
    local selected="$1"
    local project_id=$(echo "$selected" | grep -oP '\(\K[^)]+' | head -1)
    
    if [ -z "$project_id" ]; then
        return 0
    fi
    
    # 获取项目详细信息
    local info=$(pm_project_get_info "$project_id")
    
    if [ -n "$info" ]; then
        echo -e "${CYAN}📦 项目详情${NC}"
        echo ""
        echo "$info"
    fi
}

# fzf 选择器 - 选择项目
pm_fzf_select_project() {
    check_fzf || return 1
    
    local query="${1:-}"
    
    # 生成项目列表
    local projects_list=$(format_projects_for_fzf)
    
    if [ -z "$projects_list" ]; then
        echo "${YELLOW}[WARNING]${NC} 没有找到项目。请先添加项目: pm add"
        return 1
    fi
    
    # 使用 fzf 选择
    local selected=$(echo "$projects_list" | \
        fzf \
            --prompt="选择项目 > " \
            --query="$query" \
            --delimiter="|" \
            --nth=1..2 \
            --height=50% \
            --layout=reverse \
            --border \
            --preview-window="right:40%" \
            --preview="bash '$PROJECT_ROOT/ui/fzf-selector.sh' preview {}" \
            --header="Enter: 打开项目 | Ctrl-E: 编辑配置 | Ctrl-D: 删除项目" \
            --bind="ctrl-e:become(bash '$PROJECT_ROOT/ui/fzf-selector.sh' edit {})" \
            --bind="ctrl-d:become(bash '$PROJECT_ROOT/ui/fzf-selector.sh' delete {})")
    
    if [ -n "$selected" ]; then
        # 提取项目 ID
        local project_id=$(echo "$selected" | grep -oP '\(\K[^)]+' | head -1)
        
        if [ -n "$project_id" ]; then
            echo "$project_id"
            return 0
        fi
    fi
    
    return 1
}

# fzf 预览功能
pm_fzf_preview() {
    local line="$1"
    
    # 跳过分类行（以 # 开头）
    if [[ "$line" =~ ^\# ]]; then
        return 0
    fi
    
    # 提取项目 ID
    local project_id=$(echo "$line" | grep -oP '\(\K[^)]+' | head -1)
    
    if [ -z "$project_id" ]; then
        return 0
    fi
    
    # 生成预览
    generate_preview "$line"
}

# 编辑项目配置
pm_fzf_edit_config() {
    local line="$1"
    local project_id=$(echo "$line" | grep -oP '\(\K[^)]+' | head -1)
    
    if [ -z "$project_id" ]; then
        return 0
    fi
    
    # 打开配置文件编辑器
    ${EDITOR:-vi} "$PM_PROJECTS_FILE"
}

# 删除项目
pm_fzf_delete_project() {
    local line="$1"
    local project_id=$(echo "$line" | grep -oP '\(\K[^)]+' | head -1)
    
    if [ -z "$project_id" ]; then
        return 0
    fi
    
    pm_project_remove "$project_id"
}

# fzf 选择器 - 选择工具
pm_fzf_select_tool() {
    local tool_type="$1"  # editor, ai_tool, terminal, etc.
    local current_tool="${2:-}"
    
    check_fzf || return 1
    
    # 获取工具列表
    local tools_list=$(yq eval ".${tool_type} | to_entries | \"\(.key) (\(.value.command))\"" "$PM_TOOLS_FILE" 2>/dev/null)
    
    if [ -z "$tools_list" ]; then
        return 1
    fi
    
    # 使用 fzf 选择
    local selected=$(echo "$tools_list" | \
        fzf \
            --prompt="选择 $tool_type > " \
            --query="$current_tool" \
            --height=30% \
            --layout=reverse \
            --border)
    
    if [ -n "$selected" ]; then
        local tool_name=$(echo "$selected" | cut -d' ' -f1)
        echo "$tool_name"
        return 0
    fi
    
    return 1
}

# fzf 选择器 - 选择分类
pm_fzf_select_category() {
    check_fzf || return 1
    
    # 获取分类列表
    local categories=$(yq eval '.categories[] | "\(.icon) \(.name) | \(.id)"' "$PM_PROJECTS_FILE" 2>/dev/null)
    
    if [ -z "$categories" ]; then
        return 1
    fi
    
    # 使用 fzf 选择
    local selected=$(echo "$categories" | \
        fzf \
            --prompt="选择分类 > " \
            --height=30% \
            --layout=reverse \
            --border)
    
    if [ -n "$selected" ]; then
        local category_id=$(echo "$selected" | grep -oP '\|\s*\K[^|]+$')
        echo "$category_id"
        return 0
    fi
    
    return 1
}

# 显示所有项目（fzf 模式）
pm_fzf_list_projects() {
    check_fzf || return 1
    
    local projects_list=$(format_projects_for_fzf)
    
    if [ -z "$projects_list" ]; then
        echo "${YELLOW}[WARNING]${NC} 没有找到项目。请先添加项目: pm add"
        return 1
    fi
    
    # 使用 fzf 显示（只读模式）
    echo "$projects_list" | \
        fzf \
            --prompt="项目列表 > " \
            --no-multi \
            --height=80% \
            --layout=reverse \
            --border \
            --preview-window="right:40%" \
            --preview="bash '$PROJECT_ROOT/ui/fzf-selector.sh' preview {}" \
            --header="Esc: 退出"
}

# 主菜单（fzf 版本）
pm_fzf_main_menu() {
    check_fzf || return 1
    
    local options="
1) 📂 打开项目（选择并进入）
2) 📋 列出所有项目
3) ➕ 添加新项目
4) 🔍 搜索项目
5) 🗑️  删除项目
6) ⚙️  编辑配置
7) 📊 项目统计
8) 🔄 同步配置
"

    local choice=$(echo "$options" | \
        fzf \
            --prompt="主菜单 > " \
            --height=40% \
            --layout=reverse \
            --border \
            --header="选择操作" \
            --cycle)
    
    case "$choice" in
        "1)"*) echo "open" ;;
        "2)"*) echo "list" ;;
        "3)"*) echo "add" ;;
        "4)"*) echo "search" ;;
        "5)"*) echo "delete" ;;
        "6)"*) echo "config" ;;
        "7)"*) echo "stats" ;;
        "8)"*) echo "sync" ;;
        *) echo "" ;;
    esac
}

# 如果直接运行此脚本
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # 检查 PROJECT_ROOT
    if [ -z "$PROJECT_ROOT" ]; then
        echo "ERROR: PROJECT_ROOT not set. Please run via 'pm' script."
        exit 1
    fi
    
    case "${1:-select}" in
        select)
            pm_fzf_select_project "${2:-}"
            ;;
        preview)
            pm_fzf_preview "$2"
            ;;
        edit)
            pm_fzf_edit_config "$2"
            ;;
        delete)
            pm_fzf_delete_project "$2"
            ;;
        list)
            pm_fzf_list_projects
            ;;
        tool)
            pm_fzf_select_tool "$2" "${3:-}"
            ;;
        category)
            pm_fzf_select_category
            ;;
        menu)
            pm_fzf_main_menu
            ;;
        *)
            echo "Usage: $0 <select|preview|edit|delete|list|tool|category|menu>"
            ;;
    esac
fi
