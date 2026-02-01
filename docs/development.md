# Cross-Platform Project Manager - 开发文档

## 🎯 项目概述

打造一个统一的跨平台项目管理与启动工具，支持 Linux、macOS、Termux (Android) 和远程服务器。

## 📁 目录结构

```
pm-project-manager/
├── README.md                    # 项目说明
├── install.sh                   # 跨平台安装脚本
├── pm                           # 主入口脚本（软链接）
│
├── core/                        # 核心引擎
│   ├── platform.sh              # 平台检测
│   ├── config.sh                # 配置管理器
│   ├── project-registry.sh      # 项目注册表管理
│   ├── launcher.sh              # 环境启动器
│   └── tmux-manager.sh          # tmux 会话管理
│
├── ui/                          # 用户界面
│   ├── fzf-selector.sh          # fzf 项目选择器
│   ├── menu.sh                  # 文本菜单（备用）
│   └── status-view.sh           # 项目状态视图
│
├── presets/                     # 预设模板
│   ├── dev-ai.yml               # AI开发模式 (claude/codex + zed + 终端)
│   ├── dev-standard.yml         # 标准开发模式 (zed + 终端)
│   ├── learning.yml             # 学习模式 (笔记 + 文档 + 终端)
│   ├── reading.yml              # 阅读模式 (pdf/markdown + 笔记)
│   └── research.yml             # 研究模式 (论文 + 笔记 + 工具)
│
├── tools/                       # 工具链定义
│   ├── editors.yml              # 编辑器配置 (zed, code, vim, nvim)
│   ├── ai-tools.yml             # AI工具 (claude, codex, aider)
│   ├── terminals.yml            # 终端工具 (zsh, bash, fish)
│   └── utils.yml                # 工具 (fzf, rg, fd, bat)
│
├── config/                      # 配置文件目录
│   ├── projects.yaml            # 项目注册表（主配置）
│   ├── tools.yaml               # 工具别名和路径
│   └── platform.yaml            # 平台特定配置
│
├── templates/                   # 新项目模板
│   ├── template-dev.sh          # 开发项目模板
│   ├── template-learning.sh     # 学习项目模板
│   └── template-reading.sh      # 阅读项目模板
│
├── tests/                       # 测试脚本
│   └── test-*.sh
│
└── docs/                        # 文档
    ├── development.md           # 本文件
    ├── usage.md                 # 使用指南
    ├── presets.md               # 预设说明
    ├── tmux-guide.md            # tmux 会话管理指南
    └── termux-setup.md          # Termux 设置指南
```

## 🔧 核心功能设计

### 1. 项目注册表

**数据结构 (config/projects.yaml):**

```yaml
projects:
  - id: "my-app-frontend"
    name: "My App Frontend"
    category: "development"
    path: "~/projects/my-app/frontend"
    description: "React前端开发"
    tags: ["react", "typescript", "frontend"]
    platform: ["linux", "macos"]
    tools:
      editor: "zed"
      terminal: "zsh"
      ai: "claude"
    preset: "dev-ai"
    hotkey: "1"
    last_accessed: "2025-02-01T10:30:00Z"

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
```

### 2. 工具链定义

```yaml
editors:
  zed:
    command: "zed"
    args: ["."]
    alt_commands: ["zed-editor"]
  code:
    command: "code"
    args: ["."]
    alt_commands: ["code-insiders", "cursor"]
  nvim:
    command: "nvim"
    args: ["."]
    alt_commands: ["vim", "vi"]

ai_tools:
  claude:
    command: "claude"
    args: ["--agent"]
    tmux_pane: "right"
  codex:
    command: "codex"
    args: []
    tmux_pane: "right"
```

### 3. 预设模板

```yaml
name: "AI开发模式"
description: "Claude/Codex + 编辑器 + 终端"
layout: "tiled"
panes:
  - name: "main"
    type: "editor"
    tool: "zed"
    size: "50%"
  - name: "ai"
    type: "ai_tool"
    tool: "claude"
    size: "25%"
  - name: "terminal"
    type: "terminal"
    tool: "zsh"
    size: "25%"
```

## 🚀 核心命令设计

```bash
pm                            # 显示主菜单
pm list                       # 列出所有项目
pm select                     # 使用 fzf 选择项目
pm open <project-id>          # 打开项目（使用默认工具）
pm start <project-id>         # 启动完整环境（tmux会话）
pm add                        # 添加新项目
pm edit <project-id>          # 编辑项目配置
pm remove <project-id>        # 删除项目
pm preset <preset-name>       # 查看可用预设
pm config                     # 编辑配置
pm sync                       # 同步配置（远程/本地）
pm help                       # 显示帮助
```

## 🔍 平台兼容性

| 平台 | Shell | 支持工具 | 特殊处理 |
|------|-------|----------|----------|
| Linux (桌面) | bash/zsh | 全部 | 默认支持 |
| macOS (桌面) | zsh | 全部 | 路径处理 `~` |
| Termux (Android) | zsh | 有限 | 无 GUI 编辑器，用 nvim/vim |
| Remote Server | bash | 无GUI | 仅终端工具 |

## 📝 开发阶段

### Phase 1: 核心框架
- [x] 目录结构设计
- [ ] 平台检测模块
- [ ] 配置管理器 (YAML 解析)
- [ ] 项目注册表管理
- [ ] 基础 CLI 命令

### Phase 2: 用户界面
- [ ] fzf 项目选择器
- [ ] 项目列表展示
- [ ] 项目详情视图
- [ ] 主菜单

### Phase 3: 环境启动
- [ ] 单工具启动器
- [ ] tmux 会话管理器
- [ ] 预设模板系统
- [ ] 自定义工具组合

### Phase 4: 高级功能
- [ ] 配置同步
- [ ] 快捷键支持
- [ ] 项目搜索
- [ ] 使用统计

## 🔧 技术栈

- **Shell**: Bash/Zsh (兼容模式)
- **配置格式**: YAML
- **YAML解析**: yq 或 Python
- **UI**: fzf
- **会话管理**: tmux
- **版本控制**: Git (用于配置同步)
