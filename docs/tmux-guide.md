# tmux 会话管理指南

## 📖 目录

- [tmux 基础](#tmux-基础)
- [pm 的 tmux 集成](#pm-的-tmux-集成)
- [常用命令](#常用命令)
- [高级用法](#高级用法)
- [会话管理最佳实践](#会话管理最佳实践)

---

## 🖥️ tmux 基础

### 什么是 tmux？

tmux (terminal multiplexer) 是一个终端复用器，允许：
- 在单个终端窗口中运行多个终端会话
- 分离和重新连接会话
- 在会话中创建多个窗口和窗格

### 基本概念

- **会话 (Session)**: 最顶层的容器，包含窗口
- **窗口 (Window)**: 会话中的标签页，包含窗格
- **窗格 (Pane)**: 窗口中的分割区域

---

## 🔗 pm 的 tmux 集成

### 会话命名

所有 pm 创建的会话都使用以下命名规则：
```
pm-<project-id>
```

例如：
- `pm-my-app`
- `pm-rust-learning`
- `pm-dl-book`

### 会话布局

pm 创建的会话根据预设自动配置布局：

#### dev-ai 布局
```
Session: pm-my-app
├─ Window 0
│  ├─ Pane 0: 编辑器 (50%)
│  └─ Pane 1: AI 工具 (25%)
│  └─ Pane 2: 终端 (25%)
```

#### dev-standard 布局
```
Session: pm-my-app
├─ Window 0
│  ├─ Pane 0: 编辑器 (70%)
│  └─ Pane 1: 终端 (30%)
```

---

## 📋 常用命令

### 会话管理

```bash
# 列出所有会话
tmux ls
# 或
pm session list

# 附加到会话
tmux attach -t pm-my-app
# 或
pm session attach pm-my-app

# 分离当前会话
# 快捷键: Ctrl+b d

# 创建新会话
tmux new -s my-session

# 销毁会话
tmux kill-session -t pm-my-app
# 或
pm session kill pm-my-app

# 重命名会话
tmux rename-session -t pm-my-app new-name
```

### 窗口管理

```bash
# 创建新窗口
tmux new-window

# 切换到下一个窗口
# 快捷键: Ctrl+b n

# 切换到上一个窗口
# 快捷键: Ctrl+b p

# 切换到指定编号的窗口
# 快捷键: Ctrl+b 0-9

# 列出所有窗口
# 快捷键: Ctrl+b w

# 关闭当前窗口
# 快捷键: Ctrl+b &
```

### 窗格管理

```bash
# 水平分割窗格
# 快捷键: Ctrl+b "

# 垂直分割窗格
# 快捷键: Ctrl+b %

# 切换到下一个窗格
# 快捷键: Ctrl+b o

# 切换到指定方向的窗格
# 快捷键: Ctrl+b 方向键

# 关闭当前窗格
# 快捷键: Ctrl+b x

# 切换窗格布局
# 快捷键: Ctrl+b 空格

# 最大化当前窗格
# 快捷键: Ctrl+b z
```

### 复制粘贴模式

```bash
# 进入复制模式
# 快捷键: Ctrl+b [

# 在复制模式下：
# 空格 - 开始选择
# Enter - 复制选择

# 粘贴
# 快捷键: Ctrl+b ]
```

---

## 🚀 高级用法

### 在 tmux 中使用 pm

```bash
# 在 tmux 会话中启动新项目
pm start another-project

# 这会创建新的 tmux 会话
# 切换会话：Ctrl+b s
```

### 在多个项目间切换

```bash
# 列出所有会话
tmux ls

# 切换会话
# 方法 1: 先分离，再附加
tmux detach  # Ctrl+b d
tmux attach -t pm-rust-learning

# 方法 2: 在 tmux 中切换
Ctrl+b s  # 显示会话列表
```

### 跨设备使用 tmux

```bash
# 在 Android 上创建会话
pm start my-project

# 在电脑上通过 SSH 连接
ssh user@android -t tmux attach -t pm-my-project

# 在电脑和 Android 之间共享同一个会话
```

### tmux 配置

创建 `~/.tmux.conf`：

```bash
# 改变前缀键从 Ctrl+b 到 Ctrl+a
set -g prefix C-a
unbind C-b
bind C-a send-prefix

# 启用鼠标支持
set -g mouse on

# 设置窗口和窗格索引从 1 开始
set -g base-index 1
setw -g pane-base-index 1

# 设置状态栏
set -g status-style 'bg=#1e1e1e fg=white'
setw -g window-status-current-style 'fg=green bold'

# 启用 vi 模式
setw -g mode-keys vi
```

加载配置：
```bash
tmux source-file ~/.tmux.conf
```

### 自定义快捷键

在 `~/.tmux.conf` 中添加：

```bash
# 快速在 pm 项目间切换
bind P command-prompt -p "Project: " "run-shell 'pm attach %1'"

# 快速启动新项目
bind N command-prompt -p "Project: " "run-shell 'pm start %1'"

# 垂直分割并运行命令
bind V split-window -h -c "#{pane_current_path}"

# 水平分割并运行命令
bind H split-window -v -c "#{pane_current_path}"
```

### 保存和恢复会话

使用 tmux-resurrect 插件：

```bash
# 安装 TPM (Tmux Plugin Manager)
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm

# 在 ~/.tmux.conf 中添加
set -g @plugin 'tmux-plugins/tmux-resurrect'
run '~/.tmux/plugins/tpm/tpm'

# 安装插件
# 快捷键: Ctrl+b I

# 保存会话
# 快捷键: Ctrl+b Ctrl+s

# 恢复会话
# 快捷键: Ctrl+b Ctrl+r
```

---

## 📊 会话管理最佳实践

### 1. 为每个项目使用独立会话

```bash
# ✅ 好的做法
pm start project-a
pm start project-b

# ❌ 不推荐：在一个会话中管理多个项目
```

### 2. 使用描述性的会话名称

pm 自动使用项目 ID，无需手动命名。

### 3. 定期清理旧会话

```bash
# 列出会话
tmux ls

# 销毁不需要的会话
tmux kill-session -t pm-old-project
```

### 4. 使用快捷键提高效率

```bash
# 常用快捷键
Ctrl+b c  # 创建新窗口
Ctrl+b ,  # 重命名窗口
Ctrl+b %  # 垂直分割
Ctrl+b " # 水平分割
Ctrl+b o  # 切换窗格
Ctrl+b d  # 分离会话
Ctrl+b [  # 进入复制模式
Ctrl+b ]  # 粘贴
```

### 5. 使用 tmux 的持久化特性

```bash
# 长时间运行的任务
tmux new -s long-task
tmux send-keys -t long-task 'npm run build' Enter

# 分离会话，任务继续运行
Ctrl+b d

# 稍后重新连接查看进度
tmux attach -t long-task
```

---

## 🔍 故障排除

### 问题：无法附加到会话

**原因**: 会话已在其他地方附加

**解决**:
```bash
# 强制附加
tmux attach -d -t pm-my-app

# 或使用不同的客户端模式
tmux attach -t pm-my-app -d
```

### 问题：窗格布局混乱

**解决**:
```bash
# 重置布局
Ctrl+b 空格

# 或手动调整
# 最大化窗格
Ctrl+b z

# 恢复正常布局
Ctrl+b z
```

### 问题：快捷键冲突

**解决**:

在 `~/.tmux.conf` 中改变前缀键：
```bash
set -g prefix C-a
unbind C-b
```

---

## 📚 更多资源

- [tmux 官方文档](https://github.com/tmux/tmux/wiki)
- [tmux 实用指南](https://github.com/hamvocke/dotfiles/blob/master/tmux/.tmux.conf)
- [tmux 插件管理](https://github.com/tmux-plugins/tpm)

---

## 📄 许可证

MIT License
