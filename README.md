# Project Manager (pm)

> 一个统一的跨平台项目管理与启动工具，支持 Linux、macOS、Termux (Android) 和远程服务器。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## ✨ 特性

- 📁 **统一管理** - 集中管理所有项目（开发/学习/阅读/研究）
- 🚀 **快速启动** - 一键启动完整开发环境
- 🖥️ **多会话** - 使用 tmux 管理多个项目会话
- 🤖 **AI 集成** - 支持 Claude、Codex、Aider 等 AI 工具
- 📱 **跨平台** - 支持 Linux、macOS、Termux、远程服务器
- 🎨 **自定义预设** - 灵活的布局和工具配置
- 🔍 **快速搜索** - 使用 fzf 快速查找项目
- ⚡ **高效工作流** - 优化的开发体验

## 📸 快速预览

### 主菜单

```
$ pm

1) 📂 打开项目（选择并进入）
2) 📋 列出所有项目
3) ➕ 添加新项目
4) 🔍 搜索项目
```

### 项目选择（fzf）

```
💻 开发项目
  [1] my-app-frontend    React前端开发       ~/projects/my-app/frontend
  [2] backend-api         Go后端API           ~/projects/backend/api

📚 学习项目
  [3] rust-learning       Rust学习             ~/learning/rust

📖 阅读项目
  [4] book-deep-learning  深度学习书籍         ~/reading/books
```

### tmux 会话布局（AI 开发模式）

```
┌─────────────────────────────────┐
│                                 │
│         Zed 编辑器 (50%)         │
│                                 │
├───────────────────┬─────────────┤
│    Claude (25%)   │  zsh (25%)  │
│                   │             │
└───────────────────┴─────────────┘
```

## 🚀 快速开始

### 1. 安装依赖

**必需依赖：**
- `yq` - YAML 配置解析
- `fzf` - 交互式选择器（推荐）
- `tmux` - 会话管理（推荐）

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install -y yq fzf tmux
```

**macOS:**
```bash
brew install yq fzf tmux
```

**Termux (Android):**
```bash
pkg update
pkg install -y yq fzf tmux
```

### 2. 安装 pm

```bash
# 克隆项目
git clone <your-repo-url>
cd pm-project-manager

# 创建软链接
ln -s $(pwd)/pm ~/bin/pm

# 添加到 PATH
export PATH="\$PATH:~/bin"
```

### 3. 初始化配置

```bash
pm config init
```

### 4. 添加第一个项目

```bash
pm add -i
# 或
pm add my-app "My App" "~/projects/my-app" development "React应用" dev-ai
```

### 5. 开始使用

```bash
# 显示主菜单
pm

# 使用 fzf 选择项目
pm select

# 启动完整环境
pm start my-app
```

## 📖 文档

- **[使用指南](docs/usage.md)** - 完整的使用文档，覆盖所有功能
- **[开发文档](docs/development.md)** - 架构设计和开发指南
- **[预设说明](docs/presets.md)** - 预设模板详解和自定义方法
- **[tmux 指南](docs/tmux-guide.md)** - tmux 高级用法和最佳实践
- **[Termux 设置](docs/termux-setup.md)** - Termux 环境配置和使用技巧

## 🎯 核心功能

### 项目管理

```bash
pm list                    # 列出所有项目
pm select                  # 使用 fzf 选择项目
pm open <project-id>       # 打开项目
pm start <project-id>      # 启动完整环境
pm add                     # 添加新项目
pm remove <project-id>    # 删除项目
pm search <query>         # 搜索项目
```

### 会话管理

```bash
pm session list           # 列出 tmux 会话
pm session attach <name>  # 附加到会话
pm session kill <name>    # 销毁会话
```

### 配置管理

```bash
pm config                 # 编辑配置
pm config init            # 初始化配置
pm preset list            # 列出可用预设
```

## 📦 预设模板

| 预设 | 用途 | 布局 |
|------|------|------|
| `dev-ai` | AI 辅助开发 | 编辑器 + AI + 终端 |
| `dev-standard` | 标准开发 | 编辑器 + 终端 |
| `learning` | 学习笔记 | 编辑器 + 终端 |
| `reading` | 阅读文档 | 文件查看 + 终端 |

## 🏗️ 目录结构

```
pm-project-manager/
├── pm                      # 主入口脚本
├── install.sh              # 安装脚本
├── core/                   # 核心引擎
│   ├── platform.sh         # 平台检测
│   ├── config.sh           # 配置管理
│   ├── project-registry.sh # 项目注册表
│   └── tmux-manager.sh     # tmux 会话管理
├── ui/                     # 用户界面
│   └── fzf-selector.sh     # fzf 选择器
├── presets/                # 预设模板
│   ├── dev-ai.yml
│   ├── dev-standard.yml
│   ├── learning.yml
│   └── reading.yml
├── config/                 # 配置文件目录
│   ├── projects.yaml
│   └── tools.yaml
├── docs/                   # 文档
│   ├── usage.md
│   ├── development.md
│   ├── presets.md
│   ├── tmux-guide.md
│   └── termux-setup.md
└── README.md
```

## 💡 使用场景

### 日常开发

```bash
# 1. 添加项目
pm add my-api "API服务" "~/projects/my-api" development "Go API" dev-ai

# 2. 启动开发环境（自动创建 tmux 会话）
pm start my-api

# 3. 在 AI 窗格中询问问题，编辑器中编写代码，终端中运行测试
```

### 学习新语言

```bash
# 添加学习项目
pm add rust-learning "Rust学习" "~/learning/rust" learning "学习Rust" learning

# 启动学习环境
pm start rust-learning
```

### 多项目管理

```bash
# 快速切换项目
pm 1  # 开发项目
pm 2  # 学习项目
pm 3  # 阅读项目

# 查看 tmux 会话
pm session list
```

### 远程开发

```bash
# 在服务器上添加项目
pm add remote-app "Remote App" "~/projects/remote-app" development "远程开发" dev-standard

# 启动会话
pm start remote-app

# 从本地 SSH 连接
ssh user@server -t tmux attach -t pm-remote-app
```

## 🌟 高级特性

### 自定义预设

在 `presets/` 目录中创建自定义预设 YAML 文件：

```yaml
name: "我的预设"
description: "自定义布局"
layout: "tiled"

panes:
  - name: "editor"
    type: "editor"
    tool: "zed"
    size: "50%"
    position: "left"
```

### 工具链配置

在 `~/.pm/tools.yaml` 中配置自定义工具：

```yaml
editors:
  my-editor:
    command: "my-editor"
    args: ["--project-dir", "."]
    gui: true
```

### 平台适配

pm 自动检测平台并适配：
- **Linux/macOS** - 完整功能，支持 GUI 编辑器
- **Termux** - 无 GUI，自动使用终端编辑器
- **远程服务器** - 终端模式，使用 nvim/vim

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 📧 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。

## 🙏 致谢

- [yq](https://github.com/mikefarah/yq) - YAML 处理
- [fzf](https://github.com/junegunn/fzf) - 命令行模糊查找器
- [tmux](https://github.com/tmux/tmux) - 终端复用器
