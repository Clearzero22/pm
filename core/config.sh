#!/usr/bin/env bash
#
# 名称：config.sh
# 用途：配置管理器（YAML 解析和配置管理）
# 依赖：yq 或 python3
# 作者：clearzero22
# 日期：2025-02-01
# 版本：1.0.0
#

# Source platform module
# 注意：PROJECT_ROOT 由 pm 主脚本导出
source "$PROJECT_ROOT/core/platform.sh"

# 配置文件路径
PM_CONFIG_DIR="$(pm_get_config_dir)"
PM_CONFIG_FILE="$PM_CONFIG_DIR/config.yaml"
PM_PROJECTS_FILE="$PM_CONFIG_DIR/projects.yaml"
PM_TOOLS_FILE="$PM_CONFIG_DIR/tools.yaml"

# 默认配置
PM_DEFAULT_CONFIG=""

# 初始化配置目录和文件
pm_config_init() {
    # 创建配置目录
    if [ ! -d "$PM_CONFIG_DIR" ]; then
        mkdir -p "$PM_CONFIG_DIR"
    fi
    
    # 创建默认项目配置文件
    if [ ! -f "$PM_PROJECTS_FILE" ]; then
        pm_config_create_default_projects
    fi
    
    # 创建默认工具配置文件
    if [ ! -f "$PM_TOOLS_FILE" ]; then
        pm_config_create_default_tools
    fi
}

# 创建默认项目配置
pm_config_create_default_projects() {
    cat > "$PM_PROJECTS_FILE" << 'YAML'
# 项目注册表
# 使用此文件管理你的所有项目

categories:
  - id: "development"
    name: "开发项目"
    icon: "💻"
    color: "blue"
  - id: "learning"
    name: "学习项目"
    icon: "📚"
    color: "green"
  - id: "reading"
    name: "阅读项目"
    icon: "📖"
    color: "yellow"
  - id: "research"
    name: "研究项目"
    icon: "🔬"
    color: "purple"

projects: []
YAML
}

# 创建默认工具配置
pm_config_create_default_tools() {
    cat > "$PM_TOOLS_FILE" << 'YAML'
# 工具链配置
# 定义所有可用的工具及其命令

editors:
  zed:
    command: "zed"
    args: ["."]
    alt_commands: ["zed-editor"]
    gui: true
  code:
    command: "code"
    args: ["."]
    alt_commands: ["code-insiders", "cursor", "vscodium"]
    gui: true
  nvim:
    command: "nvim"
    args: ["."]
    alt_commands: ["vim", "vi"]
    gui: false
  vim:
    command: "vim"
    args: ["."]
    alt_commands: ["vi"]
    gui: false

ai_tools:
  claude:
    command: "claude"
    args: ["--agent"]
    tmux_pane: "right"
    gui: false
  codex:
    command: "codex"
    args: []
    tmux_pane: "right"
    gui: false
  aider:
    command: "aider"
    args: []
    tmux_pane: "right"
    gui: false

terminals:
  zsh:
    command: "zsh"
    args: []
  bash:
    command: "bash"
    args: []
  fish:
    command: "fish"
    args: []

viewers:
  zathura:
    command: "zathura"
    args: []
    gui: true
  okular:
    command: "okular"
    args: []
    gui: true
  less:
    command: "less"
    args: []
    gui: false

note_tools:
  obsidian:
    command: "obsidian"
    args: []
    gui: true
  logseq:
    command: "logseq"
    args: []
    gui: true

utils:
  fzf:
    command: "fzf"
    args: []
  rg:
    command: "rg"
    args: []
  fd:
    command: "fd"
    args: []
  bat:
    command: "bat"
    args: []
  tree:
    command: "tree"
    args: []
YAML
}

# YAML 读取 - 使用 yq
cfg_read_yq() {
    local file="$1"
    local path="$2"
    
    if command -v yq &> /dev/null; then
        yq eval "$path" "$file"
    else
        echo "ERROR: yq not found. Please install yq for YAML parsing."
        return 1
    fi
}

# YAML 读取 - 使用 Python 备用方案
cfg_read_python() {
    local file="$1"
    local path="$2"
    
    if command -v python3 &> /dev/null; then
        python3 -c "
import yaml, sys
with open('$file', 'r') as f:
    data = yaml.safe_load(f)
    keys = '$path'.split('.')
    result = data
    for key in keys:
        result = result[key]
    print(result)
"
    else
        echo "ERROR: Neither yq nor python3 found."
        return 1
    fi
}

# 通用 YAML 读取函数
cfg_read() {
    local file="$1"
    local path="$2"
    
    if [ ! -f "$file" ]; then
        echo "ERROR: Config file not found: $file"
        return 1
    fi
    
    # 优先使用 yq
    if command -v yq &> /dev/null; then
        cfg_read_yq "$file" "$path"
    # 备用方案：使用 Python
    elif command -v python3 &> /dev/null; then
        cfg_read_python "$file" "$path"
    else
        echo "ERROR: No YAML parser available. Please install yq or python3."
        return 1
    fi
}

# 获取所有项目列表
pm_config_get_projects() {
    cfg_read "$PM_PROJECTS_FILE" ".projects[]"
}

# 获取所有分类
pm_config_get_categories() {
    cfg_read "$PM_PROJECTS_FILE" ".categories[]"
}

# 获取工具配置
pm_config_get_tool() {
    local type="$1"
    local name="$2"
    cfg_read "$PM_TOOLS_FILE" ".${type}.${name}"
}

# 检查配置文件是否存在
pm_config_exists() {
    [ -f "$PM_PROJECTS_FILE" ] && [ -f "$PM_TOOLS_FILE" ]
}

# 获取配置目录
pm_config_get_dir() {
    echo "$PM_CONFIG_DIR"
}

# 编辑配置文件
pm_config_edit() {
    local config_type="$1"
    local file
    
    case "$config_type" in
        projects)
            file="$PM_PROJECTS_FILE"
            ;;
        tools)
            file="$PM_TOOLS_FILE"
            ;;
        *)
            echo "Usage: pm_config_edit <projects|tools>"
            return 1
            ;;
    esac
    
    # 使用默认编辑器
    ${EDITOR:-vi} "$file"
}

# 如果直接运行此脚本，初始化配置
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # 检查 PROJECT_ROOT
    if [ -z "$PROJECT_ROOT" ]; then
        echo "ERROR: PROJECT_ROOT not set. Please run via 'pm' script."
        exit 1
    fi
    
    pm_config_init
    echo "Configuration initialized at: $PM_CONFIG_DIR"
    echo "Projects: $PM_PROJECTS_FILE"
    echo "Tools: $PM_TOOLS_FILE"
fi
