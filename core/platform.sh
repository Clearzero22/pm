#!/usr/bin/env bash
#
# 名称：platform.sh
# 用途：平台检测模块
# 依赖：无
# 作者：clearzero22
# 日期：2025-02-01
# 版本：1.0.0
#

# 检测当前平台
# 输出: linux | macos | termux
pm_detect_platform() {
    # Termux 检测
    if [ -n "$TERMUX_VERSION" ]; then
        echo "termux"
        return 0
    fi
    
    # macOS 检测
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
        return 0
    fi
    
    # 默认为 Linux
    echo "linux"
    return 0
}

# 检测是否为图形界面环境
pm_is_gui() {
    local platform=$(pm_detect_platform)
    
    # Termux 无 GUI
    if [ "$platform" = "termux" ]; then
        return 1
    fi
    
    # 检测 DISPLAY (Linux) 或 GUI 相关变量 (macOS)
    if [ -n "$DISPLAY" ] || [ -n "$WAYLAND_DISPLAY" ]; then
        return 0
    fi
    
    return 1
}

# 检测 tmux 是否可用
pm_has_tmux() {
    command -v tmux &> /dev/null
}

# 检测 fzf 是否可用
pm_has_fzf() {
    command -v fzf &> /dev/null
}

# 检测 yq 是否可用（YAML 解析）
pm_has_yq() {
    command -v yq &> /dev/null
}

# 检测 Python 是否可用（备选 YAML 解析）
pm_has_python() {
    command -v python3 &> /dev/null || command -v python &> /dev/null
}

# 获取平台特定的 Shell
pm_get_shell() {
    echo "$SHELL"
}

# 获取平台特定的配置目录
pm_get_config_dir() {
    local platform=$(pm_detect_platform)
    
    case "$platform" in
        "macos")
            echo "$HOME/Library/Application Support/pm"
            ;;
        "termux")
            echo "$HOME/.pm"
            ;;
        *)
            echo "$HOME/.pm"
            ;;
    esac
}

# 获取平台特定的数据目录
pm_get_data_dir() {
    local platform=$(pm_detect_platform)
    
    case "$platform" in
        "macos")
            echo "$HOME/Library/Application Support/pm"
            ;;
        "termux")
            echo "$HOME/.pm/data"
            ;;
        *)
            # Linux 使用 XDG 标准或回退到 ~/.pm
            if [ -n "$XDG_DATA_HOME" ]; then
                echo "$XDG_DATA_HOME/pm"
            else
                echo "$HOME/.pm/data"
            fi
            ;;
    esac
}

# 展开路径中的 ~ 为完整路径
pm_expand_path() {
    local path="$1"
    echo "${path/#\~/$HOME}"
}

# 检测工具是否可用（支持备用命令）
m_check_tool() {
    local tool="$1"
    shift
    local alt_tools=("$@")
    
    if command -v "$tool" &> /dev/null; then
        echo "$tool"
        return 0
    fi
    
    for alt in "${alt_tools[@]}"; do
        if command -v "$alt" &> /dev/null; then
            echo "$alt"
            return 0
        fi
    done
    
    return 1
}

# 获取平台信息摘要
pm_platform_info() {
    local platform=$(pm_detect_platform)
    local gui=$(pm_is_gui && echo "yes" || echo "no")
    local tmux=$(pm_has_tmux && echo "yes" || echo "no")
    local fzf=$(pm_has_fzf && echo "yes" || echo "no")
    
    echo "Platform: $platform"
    echo "GUI: $gui"
    echo "Tmux: $tmux"
    echo "Fzf: $fzf"
    echo "Shell: $(pm_get_shell)"
    echo "Config Dir: $(pm_get_config_dir)"
}

# 如果直接运行此脚本，显示平台信息
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    pm_platform_info
fi
