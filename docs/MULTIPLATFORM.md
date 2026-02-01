# PM 多平台同步指南

## 概述

PM 支持在多个平台间同步配置，让你在任何设备上都有一致的项目管理体验。

---

## 支持的平台

| 平台 | 状态 | GUI | 备注 |
|------|------|-----|------|
| Linux Desktop | ✅ 完全支持 | ✅ | 推荐使用 |
| Linux Server | ✅ 完全支持 | ❌ | 无 GUI 模式 |
| macOS | ✅ 完全支持 | ✅ | 原生支持 |
| Termux | ✅ 完全支持 | ❌ | Android 终端 |
| WSL | ✅ 完全支持 | ❌ | Windows 子系统 |
| FreeBSD | ⚠️ 部分支持 | ⚠️ | 需要手动配置 |

---

## 方案 1: Git 同步（推荐）

### 架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Linux PC   │     │   macOS     │     │   Termux    │
│             │     │             │     │             │
│  ~/.dotfiles│◄────│  ~/.dotfiles│◄────│  ~/.dotfiles│
│             │     │             │     │             │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┴───────────────────┘
                           │
                    ┌──────▼──────┐
                    │   GitHub    │
                    │  dotfiles   │
                    │  (private)  │
                    └─────────────┘
```

### 设置步骤

#### 1. 创建 dotfiles 仓库

```bash
# 克隆 PM 模板
git clone https://github.com/Clearzero22/pm.git pm-temp
cp -r pm-temp/dotfiles-template ~/my-dotfiles
cd ~/my-dotfiles

# 添加 PM 作为子模块
git submodule add https://github.com/Clearzero22/pm.git pm

# 推送到 GitHub
gh repo create dotfiles --private --source=. --push
```

#### 2. 在各平台安装

**Linux / macOS:**
```bash
git clone --recurse-submodules https://github.com/YOUR_USERNAME/dotfiles.git ~/.dotfiles
cd ~/.dotfiles
bash install.sh
```

**Termux:**
```bash
pkg install git python
git clone --recurse-submodules https://github.com/YOUR_USERNAME/dotfiles.git ~/.dotfiles
cd ~/.dotfiles
bash install.sh
```

#### 3. 同步配置

**添加项目后：**
```bash
cd ~/.dotfiles
git add .pm/projects.yaml
git commit -m "Add new project"
git push
```

**其他设备更新：**
```bash
cd ~/.dotfiles
git pull
```

**快速同步（使用 sync.sh）：**
```bash
bash ~/.dotfiles/sync.sh "update config"
```

---

## 方案 2: Syncthing 同步

### 适合场景

- 不想使用 Git
- 需要实时自动同步
- 私有网络环境

### 设置步骤

#### 1. 安装 Syncthing

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install syncthing

# macOS
brew install syncthing
```

**Termux:**
```bash
pkg install syncthing
```

#### 2. 配置 Syncthing

```bash
# 启动 Syncthing
syncthing

# 打开 Web UI
# http://127.0.0.1:8384
```

#### 3. 共享配置目录

在各设备上添加同步文件夹：
- 路径：`~/.pm`
- 设备：选择你的其他设备

---

## 跨平台配置最佳实践

### 1. 使用环境变量

**❌ 不推荐：硬编码路径**
```yaml
path: "/home/user/projects"      # Linux
path: "/Users/user/projects"      # macOS
path: "/data/data/com.termux/..." # Termux
```

**✅ 推荐：环境变量**
```yaml
path: "$HOME/projects"
path: "$HOME/Documents/work"
```

### 2. 使用跨平台工具

**编辑器：**
| 平台 | 推荐编辑器 | 安装 |
|------|-----------|------|
| 全平台 | nvim | `sudo apt install neovim` |
| 全平台 | vim | 内置 |
| Linux | codium | `sudo apt install codium` |
| macOS | code | `brew install --cask visual-studio-code` |
| Termux | micro | `pkg install micro` |

**终端：**
| 平台 | 推荐终端 |
|------|----------|
| 全平台 | zsh |
| 全平台 | bash |
| Linux/macOS | fish |

### 3. 平台特定配置

**创建平台特定配置文件：**

```
~/.dotfiles/
├── .pm/
│   ├── projects.yaml       # 通用配置
│   ├── tools.yaml          # 工具配置
│   ├── projects-linux.yaml # Linux 特定
│   ├── projects-macos.yaml # macOS 特定
│   └── projects-termux.yaml # Termux 特定
```

**在配置中引入：**
```yaml
# projects.yaml
imports:
  - "projects-$PLATFORM.yaml"
```

### 4. 使用符号链接

为不同平台的相同逻辑位置创建符号链接：

```bash
# Termux
ln -s /storage/emulated/0/Documents ~/Documents

# 现在可以使用统一路径
path: "$HOME/Documents/projects"
```

---

## 平台特定注意事项

### Linux Desktop

**推荐配置：**
```yaml
tools:
  editor: codium    # GUI 编辑器
  ai: claude        # AI 工具
  terminal: zsh
preset: dev-ai      # 使用 AI 预设
```

**依赖安装：**
```bash
sudo apt install tmux fzf yq python3-yaml neovim
```

---

### Linux Server

**推荐配置：**
```yaml
tools:
  editor: nvim      # 终端编辑器
  terminal: bash
preset: dev-standard
```

**注意：**
- 无 GUI 工具
- 使用 tmux 进行会话管理
- 考虑使用 screen（如果 tmux 不可用）

---

### macOS

**推荐配置：**
```yaml
tools:
  editor: code      # VS Code
  terminal: zsh
preset: dev-ai
```

**依赖安装：**
```bash
brew install tmux fzf yq python3 neovim
```

**macOS 特定：**
- 使用 `open` 命令打开文件
- 路径不区分大小写
- 配置目录：`~/Library/Application Support/pm`

---

### Termux (Android)

**推荐配置：**
```yaml
tools:
  editor: micro      # Termux 友好
  terminal: bash
preset: dev-standard
```

**依赖安装：**
```bash
pkg install tmux fzf python git neovim
```

**Termux 特定：**
- 存储路径：`/storage/emulated/0/`
- 需要授予存储权限
- 使用 `termux-open` 打开文件

**额外配置：**
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export PM_EDITOR="micro"
export HOME="/storage/emulated/0"
```

---

## 常见问题

### Q: 不同平台的路径怎么办？

**A:** 使用环境变量和符号链接

```bash
# 创建统一的目录结构
mkdir -p ~/projects
ln -s /storage/emulated/0/projects ~/projects  # Termux
```

### Q: 如何处理平台特定的项目？

**A:** 使用分类或标签

```yaml
projects:
  - id: my-app-linux
    platform: linux
    tags: [linux-only]

  - id: my-app-macos
    platform: macos
    tags: [macos-only]
```

### Q: 同步冲突怎么办？

**A:** 使用 git rebase

```bash
cd ~/.dotfiles
git pull --rebase
# 解决冲突
git add .
git rebase --continue
git push
```

### Q: 如何忽略某些平台的配置？

**A:** 使用 .gitignore

```
# .gitignore
.pm/projects-termux.yaml
.pm/projects-local.yaml
```

---

## 示例配置

### 完整的跨平台配置

```yaml
# .pm/projects.yaml
categories:
  - id: "development"
    name: "开发项目"
    icon: "💻"

projects:
  # 跨平台项目
  - id: dotfiles
    name: Dotfiles配置
    description: 跨平台配置文件
    path: "$HOME/.dotfiles"
    category: development
    tools:
      editor: nvim
      terminal: zsh
    preset: dev-standard

  # Linux 特定
  - id: linux-app
    name: Linux应用
    path: "$HOME/projects/linux-app"
    category: development
    platforms: [linux]

  # Termux 特定
  - id: termux-scripts
    name: Termux脚本
    path: "$HOME/projects/termux"
    category: development
    platforms: [termux]
```

---

## 下一步

- [配置详解](CONFIGURATION.md)
- [命令参考](COMMANDS.md)
- [常见问题](FAQ.md)
