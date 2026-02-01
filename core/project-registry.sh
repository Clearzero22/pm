#!/usr/bin/env bash
#
# 名称：project-registry.sh
# 用途：项目注册表核心模块
# 依赖：core/config.sh, yq
# 作者：clearzero22
# 日期：2025-02-01
# 版本：1.0.0
#

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 工具函数
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
echo_c() { echo -e "$1"; }

# 检查项目是否存在
pm_project_exists() {
    local project_id="$1"

    if [ -z "$project_id" ]; then
        return 1
    fi

    if command -v yq &> /dev/null; then
        local count=$(yq eval ".projects[] | select(.id == \"$project_id\") | .id" "$PM_PROJECTS_FILE" 2>/dev/null | wc -l)
        [ "$count" -gt 0 ]
    elif command -v python3 &> /dev/null; then
        python3 - "$project_id" "$PM_PROJECTS_FILE" << PYPY
import yaml
import sys

project_id = sys.argv[1]
file_path = sys.argv[2]

with open(file_path, 'r') as f:
    data = yaml.safe_load(f)

projects = data.get('projects', [])
found = any(p.get('id') == project_id for p in projects)
sys.exit(0 if found else 1)
PYPY
    else
        # 最后的 fallback：使用 grep（可能不准确）
        grep -q "id: $project_id$" "$PM_PROJECTS_FILE" 2>/dev/null
    fi
}

# 获取项目路径
pm_project_get_path() {
    local project_id="$1"

    if [ -z "$project_id" ]; then
        return 1
    fi

    if command -v yq &> /dev/null; then
        yq eval ".projects[] | select(.id == \"$project_id\") | .path" "$PM_PROJECTS_FILE" 2>/dev/null
    elif command -v python3 &> /dev/null; then
        python3 - "$project_id" "$PM_PROJECTS_FILE" << PYPY
import yaml
import sys

project_id = sys.argv[1]
file_path = sys.argv[2]

with open(file_path, 'r') as f:
    data = yaml.safe_load(f)

projects = data.get('projects', [])
for p in projects:
    if p.get('id') == project_id:
        print(p.get('path', ''))
        break
PYPY
    else
        # Fallback: grep and extract
        grep -A 10 "id: $project_id" "$PM_PROJECTS_FILE" 2>/dev/null | grep "path:" | sed 's/.*path: *//'
    fi
}

# 获取项目详情
pm_project_get_info() {
    local project_id="$1"

    if [ -z "$project_id" ]; then
        echo "错误：缺少项目 ID"
        return 1
    fi

    if ! pm_project_exists "$project_id"; then
        echo "错误：项目 '$project_id' 不存在"
        return 1
    fi

    echo ""
    echo_c "${CYAN}📦 项目详情${NC}"
    echo ""

    if command -v yq &> /dev/null; then
        local name=$(yq eval ".projects[] | select(.id == \"$project_id\") | .name" "$PM_PROJECTS_FILE" 2>/dev/null)
        local desc=$(yq eval ".projects[] | select(.id == \"$project_id\") | .description" "$PM_PROJECTS_FILE" 2>/dev/null)
        local path=$(yq eval ".projects[] | select(.id == \"$project_id\") | .path" "$PM_PROJECTS_FILE" 2>/dev/null)
        local category=$(yq eval ".projects[] | select(.id == \"$project_id\") | .category" "$PM_PROJECTS_FILE" 2>/dev/null)

        echo_c "  ${BLUE}ID:${NC}       $project_id"
        echo_c "  ${BLUE}名称:${NC}     $name"
        echo_c "  ${BLUE}描述:${NC}     $desc"
        echo_c "  ${BLUE}分类:${NC}     $category"
        echo_c "  ${BLUE}路径:${NC}     $path"
    elif command -v python3 &> /dev/null; then
        python3 - "$project_id" "$PM_PROJECTS_FILE" << PYPY
import yaml
import sys

project_id = sys.argv[1]
file_path = sys.argv[2]

with open(file_path, 'r') as f:
    data = yaml.safe_load(f)

projects = data.get('projects', [])
for p in projects:
    if p.get('id') == project_id:
        print(f"  ID:       {p.get('id', 'N/A')}")
        print(f"  名称:     {p.get('name', 'N/A')}")
        print(f"  描述:     {p.get('description', 'N/A')}")
        print(f"  分类:     {p.get('category', 'N/A')}")
        print(f"  路径:     {p.get('path', 'N/A')}")
        break
PYPY
    else
        # Fallback: display raw section
        sed -n "/- id: $project_id$/,/^- id:/p" "$PM_PROJECTS_FILE" 2>/dev/null | head -n -1
    fi

    echo ""
}

# 更新项目访问时间
pm_project_update_access() {
    local project_id="$1"

    if [ -z "$project_id" ]; then
        return 1
    fi

    # 更新 last_accessed 字段
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    if command -v yq &> /dev/null; then
        yq eval ".projects[] |= select(.id == \"$project_id\") .last_accessed = \"$timestamp\"" -i "$PM_PROJECTS_FILE" 2>/dev/null
    fi
}

# 列出所有项目
pm_project_list() {
    echo ""
    echo_c "${CYAN}📋 项目列表${NC}"
    echo ""

    if command -v yq &> /dev/null; then
        local projects=$(yq eval '.projects[] | .id' "$PM_PROJECTS_FILE" 2>/dev/null)

        if [ -z "$projects" ]; then
            echo_c "${YELLOW}没有找到项目${NC}"
            echo ""
            echo_c "使用 ${CYAN}pm add${NC} 添加新项目"
            echo ""
            return
        fi

        local count=0
        for pid in $projects; do
            count=$((count + 1))
            local name=$(yq eval ".projects[] | select(.id == \"$pid\") | .name" "$PM_PROJECTS_FILE" 2>/dev/null)
            local path=$(yq eval ".projects[] | select(.id == \"$pid\") | .path" "$PM_PROJECTS_FILE" 2>/dev/null)

            printf "  ${GREEN}%2d${NC}. ${BLUE}%s${NC}\n" "$count" "$pid"
            printf "      ${CYAN}%s${NC}\n" "$name"
            printf "      %s\n\n" "$path"
        done
    elif command -v python3 &> /dev/null; then
        python3 << PYPY
import yaml
import os

file_path = os.path.expanduser("$PM_PROJECTS_FILE")

with open(file_path, 'r') as f:
    data = yaml.safe_load(f)

projects = data.get('projects', [])

if not projects:
    print("  没找到项目")
    print("")
    print("  使用 pm add 添加新项目")
else:
    for i, p in enumerate(projects, 1):
        print(f"  {i:2d}. {p.get('id', 'N/A')}")
        print(f"      {p.get('name', 'N/A')}")
        print(f"      {p.get('path', 'N/A')}")
        print()
PYPY
    else
        warning "需要 yq 或 python3 来显示项目列表"
        return 1
    fi
}

# 统计项目数量
pm_project_count() {
    if command -v yq &> /dev/null; then
        yq eval '.projects | length' "$PM_PROJECTS_FILE" 2>/dev/null
    else
        grep -c "^  id:" "$PM_PROJECTS_FILE" 2>/dev/null || echo "0"
    fi
}

# 搜索项目
pm_project_search() {
    local query="$1"

    if [ -z "$query" ]; then
        echo "错误：请提供搜索关键词"
        return 1
    fi

    echo ""
    echo_c "${CYAN}🔍 搜索结果: '$query'${NC}"
    echo ""

    if command -v yq &> /dev/null; then
        local found=false
        local projects=$(yq eval '.projects[] | .id' "$PM_PROJECTS_FILE" 2>/dev/null)

        for pid in $projects; do
            local name=$(yq eval ".projects[] | select(.id == \"$pid\") | .name" "$PM_PROJECTS_FILE" 2>/dev/null)
            local desc=$(yq eval ".projects[] | select(.id == \"$pid\") | .description" "$PM_PROJECTS_FILE" 2>/dev/null)
            local path=$(yq eval ".projects[] | select(.id == \"$pid\") | .path" "$PM_PROJECTS_FILE" 2>/dev/null)

            if [[ "$pid" == *"$query"* ]] || [[ "$name" == *"$query"* ]] || [[ "$desc" == *"$query"* ]] || [[ "$path" == *"$query"* ]]; then
                echo_c "  ${BLUE}$pid${NC}"
                echo_c "    ${CYAN}$name${NC}"
                echo "    $desc"
                echo "    $path"
                echo ""
                found=true
            fi
        done

        if [ "$found" = false ]; then
            echo "  未找到匹配的项目"
            echo ""
        fi
    elif command -v python3 &> /dev/null; then
        python3 - "$query" "$PM_PROJECTS_FILE" << PYPY
import yaml
import sys

query = sys.argv[1].lower()
file_path = sys.argv[2]

with open(file_path, 'r') as f:
    data = yaml.safe_load(f)

projects = data.get('projects', [])
found = False

for p in projects:
    pid = p.get('id', '')
    name = p.get('name', '')
    desc = p.get('description', '')
    path = p.get('path', '')

    if (query in pid.lower() or query in name.lower() or
        query in desc.lower() or query in path.lower()):
        print(f"  {pid}")
        print(f"    {name}")
        print(f"    {desc}")
        print(f"    {path}")
        print()
        found = True

if not found:
    print("  未找到匹配的项目")
    print()
PYPY
    else
        warning "需要 yq 或 python3 来搜索项目"
        return 1
    fi
}

# 添加项目
pm_project_add() {
    local project_id="$1"
    local project_path="${2:-$(pwd)}"
    local name="${3:-$project_id}"
    local description="${4:-无描述}"
    local category="${5:-dev}"

    if [ -z "$project_id" ]; then
        echo "错误：缺少项目 ID"
        echo "用法: pm add <project-id> [path] [name] [description] [category]"
        return 1
    fi

    if pm_project_exists "$project_id"; then
        echo "错误：项目 '$project_id' 已存在"
        return 1
    fi

    if [ ! -d "$project_path" ]; then
        echo "错误：路径 '$project_path' 不存在"
        return 1
    fi

    # 获取绝对路径
    project_path=$(cd "$project_path" && pwd)

    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    if command -v yq &> /dev/null; then
        # 使用 yq 添加项目
        yq eval ".projects += {
            \"id\": \"$project_id\",
            \"name\": \"$name\",
            \"description\": \"$description\",
            \"path\": \"$project_path\",
            \"category\": \"$category\",
            \"created_at\": \"$timestamp\",
            \"last_accessed\": \"$timestamp\",
            \"tools\": {\"editor\": \"zed\", \"terminal\": \"zsh\"},
            \"preset\": \"dev-standard\"
        }" -i "$PM_PROJECTS_FILE" 2>/dev/null
    else
        # 使用 Python 作为 fallback
        if command -v python3 &> /dev/null; then
            python3 - << PYPY
import yaml
import os

file_path = os.path.expanduser("$PM_PROJECTS_FILE")

# 读取现有配置
with open(file_path, 'r') as f:
    data = yaml.safe_load(f)

# 添加新项目
new_project = {
    'id': '$project_id',
    'name': '$name',
    'description': '$description',
    'path': '$project_path',
    'category': '$category',
    'created_at': '$timestamp',
    'last_accessed': '$timestamp',
    'tools': {'editor': 'zed', 'terminal': 'zsh'},
    'preset': 'dev-standard'
}

data['projects'].append(new_project)

# 写回文件
with open(file_path, 'w') as f:
    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
PYPY
        else
            error "需要 yq 或 python3 来添加项目"
            return 1
        fi
    fi

    echo_c "${GREEN}✓${NC} 项目 '$project_id' 已添加"
    echo "  路径: $project_path"
}

# 交互式添加项目
pm_project_add_interactive() {
    echo ""
    echo_c "${CYAN}➕ 添加新项目${NC}"
    echo ""

    read -p "项目 ID: " project_id
    [ -z "$project_id" ] && echo "错误：项目 ID 不能为空" && return 1

    if pm_project_exists "$project_id"; then
        echo "错误：项目 '$project_id' 已存在"
        return 1
    fi

    read -p "项目名称 [$project_id]: " name
    name=${name:-$project_id}

    read -p "项目路径 [$(pwd)]: " path
    path=${path:-$(pwd)}

    read -p "描述: " description
    description=${description:-无描述}

    echo ""
    echo "可用分类:"
    if command -v yq &> /dev/null; then
        yq eval '.categories[] | "  - \(.id): \(.name)"' "$PM_PROJECTS_FILE" 2>/dev/null
    fi
    read -p "分类 [dev]: " category
    category=${category:-dev}

    pm_project_add "$project_id" "$path" "$name" "$description" "$category"
}

# 删除项目
pm_project_remove() {
    local project_id="$1"

    if [ -z "$project_id" ]; then
        echo "错误：缺少项目 ID"
        return 1
    fi

    if ! pm_project_exists "$project_id"; then
        echo "错误：项目 '$project_id' 不存在"
        return 1
    fi

    # 确认删除
    read -p "确认删除项目 '$project_id'? [y/N] " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "取消删除"
        return 0
    fi

    if command -v yq &> /dev/null; then
        yq eval ".projects |= map(select(.id != \"$project_id\"))" -i "$PM_PROJECTS_FILE" 2>/dev/null
    else
        warning "yq 未安装，请手动删除配置"
        return 1
    fi

    echo_c "${GREEN}✓${NC} 项目 '$project_id' 已删除"
}

# 导出所有函数
export -f pm_project_exists
export -f pm_project_get_path
export -f pm_project_get_info
export -f pm_project_update_access
export -f pm_project_list
export -f pm_project_count
export -f pm_project_search
export -f pm_project_add
export -f pm_project_add_interactive
export -f pm_project_remove
