# Project Manager (pm) - 使用指南

## 📖 目录

- [快速开始](#快速开始)
- [核心概念](#核心概念)
- [项目管理](#项目管理)
- [环境启动](#环境启动)
- [tmux 会话管理](#tmux-会话管理)
- [配置管理](#配置管理)
- [预设模板](#预设模板)
- [平台适配](#平台适配)
- [常见用例](#常见用例)
- [故障排除](#故障排除)

---

## 🚀 快速开始

### 1. 安装依赖

**必需依赖：**
- `yq` - YAML 配置解析
- `fzf` - 交互式选择器（可选，但强烈推荐）
- `tmux` - 会话管理（可选）

**安装方法：**

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install -y yq fzf tmux
```

#### macOS
```bash
brew install yq fzf tmux
```

#### Termux (Android)
```bash
pkg update
pkg install -y yq fzf tmux
```

### 2. 安装 pm

```bash
# 进入项目目录
cd /path/to/pm-project-manager

# 创建软链接到 PATH
ln -s $(pwd)/pm ~/bin/pm

# 确保 ~/bin 在 PATH 中
export PATH="\$PATH:~/bin"
```

### 3. 初始化配置

```bash
# 首次运行会自动初始化配置
pm config init
```

配置文件位置：
- Linux/Termux: `~/.pm/`
- macOS: `~/Library/Application Support/pm/`

### 4. 添加第一个项目

```bash
# 交互式添加
pm add -i

# 或直接添加
pm add my-app "My App" "~/projects/my-app" development "React应用" dev-standard
```

### 5. 使用项目

```bash
# 显示主菜单
pm

# 使用 fzf 选择项目
pm select

# 启动完整环境
pm start my-app
```

---

## 💡 核心概念

### 项目 (Project)

项目是 pm 管理的基本单位，包含以下信息：
- `id` - 唯一标识符
- `name` - 显示名称
- `path` - 项目路径
- `category` - 分类（development/learning/reading/research）
- `description` - 描述
- `tags` - 标签列表
- `platform` - 支持的平台
- `tools` - 使用的工具
- `preset` - 默认预设
- `hotkey` - 快捷键编号

### 预设 (Preset)

预设定义了项目的启动方式，包括：
- 布局（tiled, split-horizontal, split-vertical）
- 窗格配置（类型、工具、大小、位置）
- 推荐工具

### 工具链 (Tool Chain)

pm 支持的工具类型：
- 编辑器: zed, code, nvim, vim
- AI 工具: claude, codex, aider
- 终端: zsh, bash, fish
- 查看器: zathura, okular, less
- 笔记工具: obsidian, logseq

---

## 📁 项目管理

### 查看项目

```bash
# 列出所有项目
pm list
pm ls

# 按分类查看
pm list development
pm list learning

# 使用 fzf 浏览
pm select

# 显示项目详情
pm info my-app
```

### 添加项目

#### 交互式添加（推荐）

```bash
pm add -i
# 或
pm add --interactive
```

交互式流程：
1. 输入项目 ID
2. 输入项目名称
3. 输入项目路径
4. 选择分类（1-4）
5. 输入描述（可选）
6. 选择预设（1-4）

#### 命令行添加

```bash
pm add <id> <name> <path> <category> [description] [preset]

# 示例
pm add my-app "My App" "~/projects/my-app" development "React前端" dev-ai
pm add rust-learning "Rust学习" "~/learning/rust" learning "学习Rust语言" learning
pm add dl-book "深度学习" "~/reading/books/dl" reading "深度学习书籍" reading
```

### 编辑项目

```bash
# 显示项目信息
pm info my-app

# 直接编辑配置文件
pm config projects
```

### 删除项目

```bash
# 使用 fzf 选择并删除
pm select
# 在 fzf 中按 Ctrl-D

# 直接删除
pm remove my-app
pm rm my-app
```

### 搜索项目

```bash
# 搜索关键词
pm search rust
pm search react
pm search "deep learning"
```

搜索范围：
- 项目名称
- 项目描述
- 标签

---

## 🛠️ 环境启动

### 打开项目

```bash
# 直接打开项目（仅进入目录）
pm open my-app

# 使用快捷键
pm 1
pm 2
```

### 启动完整环境

```bash
# 使用项目预设启动
pm start my-app

# 指定预设启动
pm start my-app --preset dev-ai

# 自定义工具启动
pm start my-app --editor nvim --ai codex --terminal fish
```

### 使用场景示例

#### 场景 1: AI 开发模式

```bash
# 前提：项目使用 dev-ai 预设
pm start my-app

# 等效于手动创建：
# - 左窗格: Zed 编辑器
# - 右上: Claude 对话
# - 右下: zsh 终端
```

#### 场景 2: 标准开发模式

```bash
# 项目使用 dev-standard 预设
pm start my-app

# 布局：
# - 左窗格: 编辑器
# - 右窗格: 终端
```

#### 场景 3: 学习模式

```bash
pm start rust-learning

# 布局：
# - 上窗格: nvim（笔记/代码）
# - 下窗格: 终端
```

#### 场景 4: 阅读模式

```bash
pm start dl-book

# 布局：
# - 左窗格: 文件列表
# - 右窗格: 终端（笔记）
```

---

## 🖥️ tmux 会话管理

### 列出会话

```bash
pm session list
pm session ls
```

输出示例：
```
pm-my-app: 3 windows (created Sat Feb  1 10:00:00 2025) (attached)
```

### 附加到会话

```bash
# 附加到指定会话
pm session attach pm-my-app

# 或在 tmux 中使用
tmux attach -t pm-my-app
```

### 销毁会话

```bash
# 使用 pm 销毁
pm session kill pm-my-app

# 或使用 tmux 命令
tmux kill-session -t pm-my-app
```

### 会话命名规则

所有 pm 创建的会话都使用 `pm-<project-id>` 格式命名。

---

## ⚙️ 配置管理

### 配置文件位置

- **项目配置**: `~/.pm/projects.yaml` (或 macOS 对应路径)
- **工具配置**: `~/.pm/tools.yaml`

### 查看配置

```bash
# 查看项目配置
pm config projects

# 查看工具配置
pm config tools
```

### 编辑配置

```bash
# 编辑项目配置（使用默认编辑器）
pm config projects

# 编辑工具配置
pm config tools

# 使用指定编辑器
EDITOR=nvim pm config projects
```

### 重新初始化配置

```bash
pm config init
```

### 自定义工具配置

在 `~/.pm/tools.yaml` 中添加自定义工具：

```yaml
editors:
  my-editor:
    command: "my-editor"
    args: ["--project-dir", "."]
    alt_commands: ["me"]
    gui: true

ai_tools:
  my-ai:
    command: "my-ai-tool"
    args: ["--agent-mode"]
    tmux_pane: "right"
    gui: false
```

### 自定义分类

在 `~/.pm/projects.yaml` 中添加分类：

```yaml
categories:
  - id: "work"
    name: "工作项目"
    icon: "💼"
    color: "blue"
  - id: "personal"
    name: "个人项目"
    icon: "🏠"
    color: "green"
```

---

## 📦 预设模板

### 查看可用预设

```bash
pm preset list
```

### dev-ai - AI 开发模式

**用途**: AI 辅助开发

**布局**:
```
┌──────────────┬──────────────┐
│              │              │
│   编辑器      │   AI 工具     │
│   (50%)      │   (25%)      │
│              │              │
├──────────────┴──────────────┤
│                          终端  │
│                          (25%) │
└───────────────────────────────┘
```

**推荐工具**:
- 编辑器: zed, code, nvim
- AI 工具: claude, codex, aider

**使用**:
```bash
pm add my-app "My App" "~/projects/my-app" development "AI开发项目" dev-ai
pm start my-app
```

### dev-standard - 标准开发模式

**用途**: 标准开发流程

**布局**:
```
┌──────────────┬──────────────┐
│              │              │
│   编辑器      │   终端       │
│   (70%)      │   (30%)      │
│              │              │
└──────────────┴──────────────┘
```

**推荐工具**:
- 编辑器: zed, code, nvim, vim

**使用**:
```bash
pm add my-app "My App" "~/projects/my-app" development "标准开发" dev-standard
pm start my-app
```

### learning - 学习模式

**用途**: 学习笔记和练习

**布局**:
```
┌──────────────────────────────┐
│          编辑器/笔记          │
│          (70%)                │
├──────────────────────────────┤
│          终端                │
│          (30%)                │
└──────────────────────────────┘
```

**推荐工具**:
- 编辑器: nvim, vim

**使用**:
```bash
pm add rust-learning "Rust学习" "~/learning/rust" learning "Rust语言" learning
pm start rust-learning
```

### reading - 阅读模式

**用途**: 阅读 PDF/文档 + 笔记

**布局**:
```
┌──────────────┬──────────────┐
│              │              │
│   文件列表    │   终端/笔记  │
│   (50%)      │   (50%)      │
│              │              │
└──────────────┴──────────────┘
```

**推荐工具**:
- 查看器: zathura, okular, less

**使用**:
```bash
pm add dl-book "深度学习" "~/reading/dl" reading "深度学习书籍" reading
pm start dl-book
```

---

## 📱 平台适配

### Linux (桌面)

完整支持所有功能：
- ✅ GUI 编辑器
- ✅ tmux 会话
- ✅ fzf 选择器

```bash
# 典型工作流
pm select          # 选择项目
pm start my-app     # 启动完整环境
```

### macOS (桌面)

完整支持所有功能，注意路径处理：
- ✅ GUI 编辑器（Zed, VS Code）
- ✅ tmux 会话
- ✅ fzf 选择器

```bash
# Homebrew 安装依赖
brew install yq fzf tmux zed

# 正常使用
pm
```

### Termux (Android)

限制：无 GUI 编辑器

```bash
# 安装依赖
pkg update
pkg install yq fzf tmux neovim

# 配置文件位置: ~/.pm/

# 使用终端编辑器
pm add my-app "My App" "~/projects/my-app" development "Termux项目" learning
pm start my-app  # 自动使用 nvim
```

**Termux 特定配置**:

在 `~/.pm/tools.yaml` 中设置默认工具：
```yaml
editors:
  zed:
    command: "nvim"  # Termux 无 GUI
    args: ["."]
    gui: false
```

### 远程服务器 (SSH)

限制：通常无 GUI

```bash
# SSH 登录
ssh user@server

# 安装依赖
sudo apt install yq fzf tmux neovim

# 使用
pm add my-app "My App" "~/projects/my-app" development "服务器项目" dev-standard
pm start my-app  # 使用 nvim + 终端
```

### 混合使用场景

**在 Android Termux 上启动项目，然后通过 SSH 在电脑上编辑：**

```bash
# 在 Termux 中
pm start my-app  # 创建 tmux 会话

# 在电脑上 SSH
ssh user@android -t tmux attach -t pm-my-app
```

---

## 🎯 常见用例

### 用例 1: 日常开发工作流

```bash
# 1. 添加新项目
pm add my-api "API服务" "~/projects/my-api" development "Go API" dev-ai

# 2. 启动开发环境
pm start my-api

# 3. 在 AI 窗格中询问问题
# 4. 在编辑器中编写代码
# 5. 在终端中运行测试
```

### 用例 2: 多项目管理

```bash
# 列出所有项目
pm list

# 快速切换
pm 1           # 开发项目
pm 2           # 学习项目
pm 3           # 阅读项目

# 查看会话
pm session list

# 切换会话
tmux switch -t pm-rust-learning
```

### 用例 3: 学习新语言

```bash
# 1. 添加学习项目
pm add go-learning "Go学习" "~/learning/go" learning "学习Go语言" learning

# 2. 启动学习环境
pm start go-learning

# 3. 在上窗格做笔记和练习
# 4. 在下窗格运行代码
```

### 用例 4: 研究论文 + 笔记

```bash
# 1. 添加研究项目
pm add ml-research "ML研究" "~/research/ml" research "机器学习研究" reading

# 2. 启动阅读环境
pm start ml-research

# 3. 左窗格查看论文
# 4. 右窗格做笔记
```

### 用例 5: 远程开发

```bash
# 1. 在服务器上添加项目
pm add remote-app "Remote App" "~/projects/remote-app" development "远程开发" dev-standard

# 2. 启动会话
pm start remote-app

# 3. 从本地 SSH 连接
ssh user@server -t tmux attach -t pm-remote-app
```

### 用例 6: 快速查看项目

```bash
# 搜索项目
pm search api

# 快速查看
pm info my-api

# 仅打开项目（不启动 tmux）
pm open my-api
```

### 用例 7: 批量管理项目

```bash
# 列出所有开发项目
pm list development

# 列出所有学习项目
pm list learning

# 删除不用的项目
pm remove old-project
```

---

## 🔧 故障排除

### 问题：yq 命令未找到

**解决方案**:

```bash
# Linux
sudo apt install yq

# macOS
brew install yq

# Termux
pkg install yq
```

### 问题：fzf 未安装

**解决方案**:

pm 可以在没有 fzf 的情况下工作，但会使用备用文本菜单。

```bash
# 安装 fzf 以获得更好体验
brew install fzf  # macOS
sudo apt install fzf  # Linux
pkg install fzf  # Termux
```

### 问题：tmux 会话已存在

**解决方案**:

```bash
# 查看现有会话
pm session list

# 附加到会话
pm session attach pm-my-app

# 或销毁会话重新创建
pm session kill pm-my-app
pm start my-app
```

### 问题：GUI 编辑器无法启动

**原因**: 可能是在无 GUI 环境中（Termux/SSH）

**解决方案**:

```bash
# 使用终端编辑器
pm start my-app --editor nvim

# 或修改项目配置使用 nvim
pm config projects
# 将 editor 改为 nvim
```

### 问题：项目路径不存在

**解决方案**:

```bash
# 创建项目目录
mkdir -p ~/projects/my-app

# 或添加项目时自动创建
pm add my-app "My App" "~/projects/my-app" development "项目描述" dev-standard
```

### 问题：配置文件损坏

**解决方案**:

```bash
# 重新初始化配置
pm config init

# 或手动备份后删除
mv ~/.pm ~/.pm.backup
pm config init
```

### 问题：tmux 窗格启动失败

**检查**:

```bash
# 检查工具是否可用
which zed
which claude
which zsh

# 检查工具配置
cat ~/.pm/tools.yaml
```

**解决方案**:

```bash
# 使用可用工具
pm start my-app --editor nvim --terminal bash
```

---

## 📚 更多资源

### 相关文档
- [开发文档](./development.md) - 架构设计和开发指南
- [预设说明](./presets.md) - 预设模板详解
- [tmux 指南](./tmux-guide.md) - tmux 高级用法
- [Termux 设置](./termux-setup.md) - Termux 环境配置

### 社区和支持

如有问题或建议，请提交 Issue 或 Pull Request。

---

## 📄 许可证

MIT License
