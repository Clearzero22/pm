# 预设模板详解

## 📦 可用预设

### 1. dev-ai - AI 开发模式

**文件**: `presets/dev-ai.yml`

**布局图**:
```
┌─────────────────────────────────┐
│                                 │
│         编辑器 (50%)             │
│                                 │
├───────────────────┬─────────────┤
│    AI 工具 (25%)  │ 终端 (25%)  │
│                   │             │
└───────────────────┴─────────────┘
```

**窗格配置**:
| 名称 | 类型 | 默认工具 | 大小 | 位置 |
|------|------|----------|------|------|
| editor | editor | zed | 50% | left |
| ai | ai_tool | claude | 25% | right-top |
| terminal | terminal | zsh | 25% | right-bottom |

**推荐工具**:
- 编辑器: zed, code, nvim
- AI 工具: claude, codex, aider

**使用场景**:
- AI 辅助编码
- 代码审查和重构
- 技术问题咨询

**示例**:
```bash
pm add my-app "My App" "~/projects/my-app" development "AI开发" dev-ai
pm start my-app
```

### 2. dev-standard - 标准开发模式

**文件**: `presets/dev-standard.yml`

**布局图**:
```
┌─────────────────────────────────┐
│                                 │
│        编辑器 (70%)             │
│                                 │
├─────────────────────────────────┤
│           终端 (30%)             │
│                                 │
└─────────────────────────────────┘
```

**窗格配置**:
| 名称 | 类型 | 默认工具 | 大小 | 位置 |
|------|------|----------|------|------|
| editor | editor | zed | 70% | left |
| terminal | terminal | zsh | 30% | right |

**推荐工具**:
- 编辑器: zed, code, nvim, vim

**使用场景**:
- 日常开发
- 项目构建和测试
- 代码调试

**示例**:
```bash
pm add backend "Backend" "~/projects/backend" development "后端开发" dev-standard
pm start backend
```

### 3. learning - 学习模式

**文件**: `presets/learning.yml`

**布局图**:
```
┌─────────────────────────────────┐
│                                 │
│       编辑器/笔记 (70%)         │
│                                 │
├─────────────────────────────────┤
│           终端 (30%)             │
│                                 │
└─────────────────────────────────┘
```

**窗格配置**:
| 名称 | 类型 | 默认工具 | 大小 | 位置 |
|------|------|----------|------|------|
| editor | editor | nvim | 70% | top |
| terminal | terminal | zsh | 30% | bottom |

**推荐工具**:
- 编辑器: nvim, vim, code

**使用场景**:
- 学习新语言
- 练习题和实验
- 笔记和文档

**示例**:
```bash
pm add go-learning "Go学习" "~/learning/go" learning "Go语言" learning
pm start go-learning
```

### 4. reading - 阅读模式

**文件**: `presets/reading.yml`

**布局图**:
```
┌─────────────────────────────────┐
│                                 │
│      文件列表/查看器 (50%)       │
│                                 │
├─────────────────────────────────┤
│         终端/笔记 (50%)         │
│                                 │
└─────────────────────────────────┘
```

**窗格配置**:
| 名称 | 类型 | 默认工具 | 大小 | 位置 |
|------|------|----------|------|------|
| viewer | file_viewer | ls | 50% | left |
| terminal | terminal | zsh | 50% | right |

**推荐工具**:
- 查看器: zathura, okular, less, bat
- 笔记: obsidian, logseq

**使用场景**:
- 阅读 PDF/书籍
- 阅读项目文档
- 阅读代码库

**示例**:
```bash
pm add dl-book "深度学习" "~/reading/books/dl" reading "深度学习" reading
pm start dl-book
```

---

## 🎨 创建自定义预设

### 预设文件格式

```yaml
# presets/my-preset.yml
name: "我的预设"
description: "预设描述"
layout: "layout-type"  # tiled, split-horizontal, split-vertical

panes:
  - name: "pane-name"
    type: "pane-type"  # editor, ai_tool, terminal, file_viewer
    tool: "tool-name"
    size: "50%"         # 百分比
    position: "left"    # left, right, top, bottom, left-top, etc.
    args: ["--option"]  # 可选参数

recommended_editors:
  - zed
  - code

recommended_ai_tools:
  - claude
  - codex
```

### 示例：三栏布局

```yaml
name: "三栏开发模式"
description: "编辑器 + AI + 终端（三栏）"
layout: "tiled"

panes:
  - name: "editor"
    type: "editor"
    tool: "zed"
    size: "40%"
    position: "left"
  
  - name: "ai"
    type: "ai_tool"
    tool: "claude"
    size: "30%"
    position: "center"
  
  - name: "terminal"
    type: "terminal"
    tool: "zsh"
    size: "30%"
    position: "right"
```

### 示例：四象限布局

```yaml
name: "四象限布局"
description: "上：编辑器+AI，下：终端+日志"
layout: "tiled"

panes:
  - name: "editor"
    type: "editor"
    tool: "zed"
    size: "50%"
    position: "left-top"
  
  - name: "ai"
    type: "ai_tool"
    tool: "claude"
    size: "50%"
    position: "right-top"
  
  - name: "terminal"
    type: "terminal"
    tool: "zsh"
    size: "50%"
    position: "left-bottom"
  
  - name: "log"
    type: "terminal"
    tool: "zsh"
    size: "50%"
    position: "right-bottom"
    args: ["-c", "tail -f log.txt"]
```

---

## 🔧 预设配置技巧

### 1. 使用不同的 AI 工具

```yaml
panes:
  - name: "ai"
    type: "ai_tool"
    tool: "codex"  # 使用 codex
    args: ["--agent"]
```

### 2. 在终端中运行特定命令

```yaml
panes:
  - name: "dev-server"
    type: "terminal"
    tool: "zsh"
    args: ["-c", "npm run dev"]
```

### 3. 多个终端窗格

```yaml
panes:
  - name: "terminal-main"
    type: "terminal"
    tool: "zsh"
    size: "50%"
  
  - name: "terminal-test"
    type: "terminal"
    tool: "zsh"
    size: "50%"
```

### 4. 文件查看窗格

```yaml
panes:
  - name: "viewer"
    type: "file_viewer"
    tool: "bat"
    args: ["README.md"]
```

---

## 📝 预设最佳实践

1. **保持简洁**: 不要创建太多窗格，避免界面混乱
2. **合理分配空间**: 根据使用频率调整窗格大小
3. **命名清晰**: 窗格名称应该描述其用途
4. **文档化**: 为预设添加清晰的描述
5. **复用**: 相似的场景可以共享预设

---

## 🔄 预设与工具配置

预设中引用的工具需要在 `~/.pm/tools.yaml` 中定义：

```yaml
editors:
  zed:
    command: "zed"
    args: ["."]
    gui: true

ai_tools:
  claude:
    command: "claude"
    args: ["--agent"]
    tmux_pane: "right"

terminals:
  zsh:
    command: "zsh"
    args: []
```

确保预设中引用的工具在工具配置中存在。
