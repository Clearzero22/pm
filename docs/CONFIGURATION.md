# PM 配置详解

## 配置目录结构

```
~/.pm/
├── projects.yaml      # 项目注册表
├── tools.yaml         # 工具配置
├── presets/           # 自定义预设
│   ├── dev-ai.yml
│   ├── dev-standard.yml
│   ├── learning.yml
│   └── reading.yml
└── config.sh          # 环境变量（可选）
```

---

## 项目配置 (projects.yaml)

### 完整示例

```yaml
# 分类定义
categories:
  - id: "development"
    name: "开发项目"
    icon: "💻"
    color: "blue"
    description: "软件开发项目"

  - id: "learning"
    name: "学习项目"
    icon: "📚"
    color: "green"
    description: "学习笔记和教程"

  - id: "reading"
    name: "阅读项目"
    icon: "📖"
    color: "yellow"
    description: "阅读材料和文档"

  - id: "research"
    name: "研究项目"
    icon: "🔬"
    color: "purple"
    description: "研究和调研"

# 项目列表
projects:
  # 基本项目
  - id: my-app
    name: 我的应用
    description: 这是一个个人项目
    path: "$HOME/projects/my-app"
    category: development
    created_at: "2025-01-01T00:00:00Z"
    last_accessed: "2025-01-01T12:00:00Z"

  # 完整配置项目
  - id: work-api
    name: 工作 API
    description: 公司后端 API 项目
    path: "$HOME/work/api"
    category: development
    tags: [work, backend, go]
    tools:
      editor: nvim
      terminal: zsh
      ai: claude
    preset: dev-ai
    env:
      GO_ENV: development
      DB_HOST: localhost
    created_at: "2025-01-15T09:00:00Z"
    last_accessed: "2025-01-20T14:30:00Z"

  # 学习项目
  - id: learn-rust
    name: Rust 学习
    description: 学习 Rust 编程语言
    path: "$HOME/learn/rust"
    category: learning
    tools:
      editor: nvim
      terminal: bash
    preset: learning
```

### 项目字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✅ | 唯一标识符 |
| `name` | string | ✅ | 显示名称 |
| `description` | string | ❌ | 项目描述 |
| `path` | string | ✅ | 项目路径（支持环境变量） |
| `category` | string | ✅ | 分类 ID |
| `tags` | array | ❌ | 标签列表 |
| `tools` | object | ❌ | 工具配置 |
| `preset` | string | ❌ | 预设名称 |
| `env` | object | ❌ | 环境变量 |
| `created_at` | datetime | ❌ | 创建时间 |
| `last_accessed` | datetime | ❌ | 最后访问时间 |

### 工具配置 (tools)

```yaml
tools:
  # 编辑器
  editor: nvim           # vim, code, zed, codium

  # AI 工具
  ai: claude             # aider, cursor, codex

  # 终端
  terminal: zsh          # bash, fish

  # 阅读器
  viewer: zathura        # evince, preview
```

### 环境变量 (env)

```yaml
env:
  NODE_ENV: development
  API_KEY: "your-key"
  DEBUG: "true"
```

---

## 工具配置 (tools.yaml)

### 完整示例

```yaml
# 编辑器配置
editors:
  # 终端编辑器
  nvim:
    command: nvim
    gui: false
    args: ["+NERDTree"]
  vim:
    command: vim
    gui: false
  nano:
    command: nano
    gui: false
  micro:
    command: micro
    gui: false

  # GUI 编辑器 - Linux
  codium:
    command: codium
    gui: true
    args: ["--new-window"]
  gedit:
    command: gedit
    gui: true

  # GUI 编辑器 - macOS
  vscode:
    command: code
    gui: true
    args: ["--new-window"]
  bbedit:
    command: bbedit
    gui: true
  textmate:
    command: mate
    gui: true

  # GUI 编辑器 - 跨平台
  zed:
    command: zed
    gui: true
  sublime:
    command: subl
    gui: true

# AI 工具配置
ai_tools:
  claude:
    command: claude
    gui: false
  aider:
    command: aider
    gui: false
  cursor:
    command: cursor
    gui: true
  codex:
    command: codex
    gui: false

# 终端配置
terminals:
  zsh:
    command: zsh
  bash:
    command: bash
  fish:
    command: fish
  nu:
    command: nu

# 阅读器配置
viewers:
  # 终端阅读器
  less:
    command: less
    gui: false
  bat:
    command: bat
    gui: false

  # PDF 阅读器
  zathura:
    command: zathura
    gui: true
  evince:
    command: evince
    gui: true
  mupdf:
    command: mupdf
    gui: true

  # macOS
  preview:
    command: open
    gui: true
    args: ["-a", "Preview"]

  # Termux
  termux-open:
    command: termux-open
    gui: true

# 笔记工具
note_tools:
  obsidian:
    command: obsidian
    gui: true
  logseq:
    command: logseq
    gui: true
  joplin:
    command: joplin
    gui: true
```

### 工具字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `command` | string | ✅ | 命令名称 |
| `gui` | boolean | ❌ | 是否为 GUI 程序 |
| `args` | array | ❌ | 命令参数 |

---

## 预设配置 (presets/*.yml)

### 预设结构

```yaml
name: 预设名称
description: 预设描述
layout:
  - type: pane          # pane | window
    tool: editor        # 工具类型
    size: 60%           # 窗格大小
    command: nvim       # 可选：覆盖命令
  - type: pane
    tool: terminal
    size: 40%
```

### 内置预设

#### dev-ai.yml

```yaml
name: AI 开发环境
description: 编辑器 + AI 工具 + 终端
layout:
  - type: pane
    tool: editor
    size: 50%
  - type: pane
    tool: ai
    size: 25%
  - type: pane
    tool: terminal
    size: 25%
split: horizontal
```

#### dev-standard.yml

```yaml
name: 标准开发环境
description: 编辑器 + 终端
layout:
  - type: pane
    tool: editor
    size: 60%
  - type: pane
    tool: terminal
    size: 40%
split: horizontal
```

#### learning.yml

```yaml
name: 学习环境
description: 笔记 + 终端
layout:
  - type: pane
    tool: note
    size: 50%
  - type: pane
    tool: terminal
    size: 50%
split: vertical
```

#### reading.yml

```yaml
name: 阅读环境
description: 文件列表 + 终端
layout:
  - type: pane
    tool: viewer
    size: 30%
  - type: pane
    tool: terminal
    size: 70%
split: horizontal
```

### 自定义预设

创建 `~/.pm/presets/my-preset.yml`：

```yaml
name: 我的工作空间
description: 自定义布局
layout:
  - type: pane
    tool: editor
    size: 70%
  - type: pane
    tool: terminal
    size: 30%
split: horizontal

# 可选：会话后命令
post_hook:
  - command: "tmux select-pane -t 0"
  - command: "tmux send-keys 'vim .' Enter"
```

---

## 环境变量

### Shell 环境变量

```bash
# 配置目录
export PM_CONFIG_DIR="$HOME/.pm"

# 项目文件
export PM_PROJECTS_FILE="$PM_CONFIG_DIR/projects.yaml"
export PM_TOOLS_FILE="$PM_CONFIG_DIR/tools.yaml"

# 默认工具
export PM_EDITOR="nvim"
export PM_TERMINAL="zsh"
export PM_AI_TOOL="claude"

# 默认预设
export PM_PRESET="dev-standard"
```

### 在 shell 配置中添加

**~/.zshrc 或 ~/.bashrc：**
```bash
# PM 配置
export PM_EDITOR="nvim"
export PM_TERMINAL="zsh"

# 添加到 PATH
export PATH="$HOME/.pm:$PATH"
```

---

## 配置验证

### 检查配置语法

```bash
# 检查 YAML 语法
yq eval '.' ~/.pm/projects.yaml

# 检查项目是否存在
pm info my-project
```

### 常见配置错误

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| `syntax error` | YAML 格式错误 | 检查缩进和引号 |
| `project not found` | 项目 ID 不存在 | 使用 `pm list` 查看 |
| `path not found` | 项目路径不存在 | 检查路径或创建目录 |
| `tool not found` | 工具未安装 | 安装工具或更换工具 |

---

## 配置模板

### 最小配置

```yaml
categories:
  - id: "dev"
    name: "开发"
    icon: "💻"

projects:
  - id: my-app
    name: 我的应用
    path: "$HOME/projects/my-app"
    category: dev
```

### 完整配置

```yaml
categories:
  - id: "development"
    name: "开发项目"
    icon: "💻"
    color: "blue"
  - id: "learning"
    name: "学习项目"
    icon: "📚"
    color: "green"

projects:
  - id: work-api
    name: 工作后端
    description: Go 后端 API
    path: "$HOME/work/api"
    category: development
    tags: [work, backend, go]
    tools:
      editor: nvim
      terminal: zsh
      ai: claude
    preset: dev-ai
    env:
      GO_ENV: development
    created_at: "2025-01-15T09:00:00Z"
    last_accessed: "2025-01-20T14:30:00Z"
```

---

## 下一步

- [命令参考](COMMANDS.md)
- [多平台同步](MULTIPLATFORM.md)
- [常见问题](FAQ.md)
