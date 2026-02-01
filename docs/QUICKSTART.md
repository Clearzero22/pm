# PM 项目管理器 - 快速开始

## 什么是 PM？

PM (Project Manager) 是一个跨平台的项目管理工具，让你可以：
- 统一管理所有项目（开发、学习、阅读、研究）
- 一键启动完整的开发环境（编辑器 + AI + 终端）
- 跨平台同步配置（Linux, macOS, Termux）

---

## 5 分钟快速开始

### 1. 安装

```bash
# 克隆仓库
git clone https://github.com/Clearzero22/pm.git ~/.pm
cd ~/.pm

# 创建符号链接
sudo ln -s ~/.pm/pm /usr/local/bin/pm

# 或添加到 PATH
echo 'export PATH="$HOME/.pm:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 2. 初始化配置

```bash
pm config init
```

这会在 `~/.pm/` 目录创建配置文件。

### 3. 添加项目

```bash
# 方式 1: 命令行
pm add my-project ~/projects/my-app "我的应用" development

# 方式 2: 交互式
pm add -i
```

### 4. 使用项目

```bash
# 列出所有项目
pm list

# 打开项目（进入目录）
pm open my-project

# 启动完整环境（tmux 会话）
pm start my-project

# 查看项目详情
pm info my-project
```

---

## 核心概念

### 项目 (Project)

项目是你想要管理的任何内容：代码仓库、学习笔记、阅读材料等。

每个项目包含：
- **ID**: 唯一标识符
- **名称**: 显示名称
- **路径**: 项目所在目录
- **分类**: development / learning / reading / research
- **工具**: 编辑器、终端、AI 工具等
- **预设**: 布局模板

### 预设 (Preset)

预设定义了项目启动时的窗口布局：

| 预设 | 布局 | 适用场景 |
|------|------|----------|
| `dev-ai` | 编辑器 + AI + 终端 | AI 辅助开发 |
| `dev-standard` | 编辑器 + 终端 | 标准开发 |
| `learning` | 笔记 + 终端（横向） | 学习/研究 |
| `reading` | 文件列表 + 终端（纵向） | 阅读文档 |

### 工具 (Tools)

PM 支持配置各种工具，会根据可用性自动选择：

- **编辑器**: nvim, vim, code, zed, codium...
- **AI 工具**: claude, aider, cursor...
- **终端**: zsh, bash, fish...
- **阅读器**: zathura, evince, preview...

---

## 常用命令

### 项目管理

```bash
# 添加项目
pm add <id> [path] [name] [description] [category]

# 列出项目
pm list
pm ls

# 搜索项目
pm search <关键词>

# 查看详情
pm info <project-id>

# 打开项目（进入目录）
pm open <project-id>

# 启动完整环境
pm start <project-id>

# 编辑配置
pm edit <project-id>

# 删除项目
pm remove <project-id>
pm rm <project-id>
```

### 环境管理

```bash
# 列出 tmux 会话
pm session list

# 附加到会话
pm session attach <session-name>

# 销毁会话
pm session kill <session-name>
```

### 配置管理

```bash
# 初始化配置
pm config init

# 编辑配置
pm config [projects|tools]

# 列出预设
pm preset list
```

### 其他

```bash
# 系统信息
pm info

# 帮助
pm help

# 版本
pm version
```

---

## 配置文件

### 项目配置 (`~/.pm/projects.yaml`)

```yaml
categories:
  - id: "development"
    name: "开发项目"
    icon: "💻"

projects:
  - id: my-app
    name: 我的应用
    description: 这是一个示例项目
    path: "$HOME/projects/my-app"
    category: development
    tools:
      editor: nvim
      terminal: zsh
      ai: claude
    preset: dev-ai
```

### 工具配置 (`~/.pm/tools.yaml`)

```yaml
editors:
  nvim:
    command: nvim
    gui: false
  code:
    command: code
    gui: true

ai_tools:
  claude:
    command: claude
  aider:
    command: aider
```

---

## 使用场景示例

### 场景 1: 日常开发

```bash
# 添加工作项目
pm add work-api ~/projects/work/api "工作 API" development

# 启动开发环境（编辑器 + 终端）
pm start work-api

# 工作结束后退出 tmux
# 按键: Ctrl+b 然后 d
```

### 场景 2: 学习新技术

```bash
# 添加学习项目
pm add learn-rust ~/projects/learn-rust "Rust 学习" learning

# 启动学习环境（笔记 + 终端）
pm start learn-rust
```

### 场景 3: 阅读文档

```bash
# 添加文档项目
pm add docs-react ~/docs/react "React 文档" reading

# 打开文档目录
pm open docs-react
```

### 场景 4: 多项目管理

```bash
# 使用 fzf 快速选择（如果已安装）
pm select

# 或使用搜索
pm search rust

# 或直接输入 ID
pm my-app
```

---

## 高级用法

### 1. 使用环境变量

路径支持环境变量，方便跨平台：

```yaml
path: "$HOME/projects"
path: "$XDG_DOCUMENTS_DIR/work"
path: "$PROJECT_ROOT"
```

### 2. 符号链接

为常用项目创建快捷方式：

```bash
# 添加主目录项目
pm add home "$HOME" "主目录" development

# 快速访问
pm open home
```

### 3. tmux 工作流

```bash
# 启动项目（创建 tmux 会话）
pm start my-app

# 在另一个终端附加到会话
pm session attach my-app

# 查看所有会话
pm session list

# 分离会话（按键）
# Ctrl+b 然后 d

# 销毁会话
pm session kill my-app
```

### 4. 自定义预设

创建自己的布局模板：

```bash
# 编辑预设文件
vi ~/.pm/presets/my-layout.yml
```

```yaml
name: 自定义布局
description: 我的工作布局
layout:
  - type: pane
    tool: editor
    size: 60%
  - type: pane
    tool: terminal
    size: 40%
```

---

## 故障排除

### 问题：命令未找到

```bash
# 检查 PATH
echo $PATH | grep pm

# 手动添加
export PATH="$HOME/.pm:$PATH"

# 或创建符号链接
sudo ln -s ~/.pm/pm /usr/local/bin/pm
```

### 问题：tmux 会话已存在

```bash
# 附加到现有会话
pm session attach my-app

# 或先销毁再启动
pm session kill my-app
pm start my-app
```

### 问题：编辑器未启动

检查工具配置：

```bash
# 编辑工具配置
pm config tools

# 确保编辑器已安装
which nvim
which code
```

### 问题：颜色显示异常

```bash
# 重新初始化配置
pm config init

# 检查终端支持
echo $TERM
```

---

## 下一步

- 📖 阅读 [完整命令参考](COMMANDS.md)
- 🌐 了解 [多平台同步](MULTIPLATFORM.md)
- ⚙️ 查看 [配置详解](CONFIGURATION.md)
- 💡 查看 [常见问题](FAQ.md)
