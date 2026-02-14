# PM 多平台配置指南

跨平台同步你的 PM 项目管理配置。

## 支持平台

| 平台 | 状态 | 备注 |
|------|------|------|
| Linux Desktop | ✅ | 完全支持 |
| Linux Server | ✅ | 无 GUI 模式 |
| macOS | ✅ | 完全支持 |
| Termux | ✅ | Android 终端 |
| WSL | ✅ | Windows 子系统 |

## 快速开始

### 1. 创建你的 dotfiles 仓库

```bash
# 克隆模板
git clone https://github.com/Clearzero22/pm.git pm-temp
cp -r pm-temp/dotfiles-template ~/my-dotfiles
cd ~/my-dotfiles

# 初始化 Git
git init
git add .
git commit -m "Initial dotfiles setup"

# 推送到 GitHub
gh repo create dotfiles --private --source=. --push
```

### 2. 在各平台安装

```bash
# 克隆你的 dotfiles
git clone https://github.com/YOUR_USERNAME/dotfiles.git ~/.dotfiles
cd ~/.dotfiles

# 运行安装脚本
bash install.sh
```

### 3. PM 子模块（推荐）

```bash
cd ~/.dotfiles
git submodule add https://github.com/Clearzero22/pm.git pm
git commit -m "Add pm as submodule"
git push
```

## 配置文件说明

### `.pm/projects.yaml`

项目注册表，使用**环境变量**实现跨平台：

```yaml
projects:
  - id: my-project
    path: "$HOME/projects/my-project"  # 自动展开
    tools:
      editor: nvim  # 跨平台编辑器
      terminal: zsh
```

### `.pm/tools.yaml`

平台特定工具配置，PM 会自动选择可用工具。

## 平台特定建议

### 🖥️ Linux 桌面

```bash
# 推荐编辑器
export PM_EDITOR="codium"  # 或 nvim

# 推荐 GUI 工具
sudo apt install fzf tmux yq python3-yaml
```

### 🖥️ Linux 服务器

```bash
# 无 GUI 配置
# 使用纯终端工具
export PM_EDITOR="nvim"
export PM_TERMINAL="bash"
```

### 🍎 macOS

```bash
# 安装 Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装依赖
brew install fzf tmux yq python3
```

### 📱 Termux (Android)

```bash
# 安装依赖
pkg install fzf tmux python git

# 编辑器选择
export PM_EDITOR="nvim"  # 或 micro
```

## 同步工作流

### 添加新项目（任一平台）

```bash
pm add my-project "$HOME/projects/my-project" "描述" development
cd ~/.dotfiles
git add .pm/projects.yaml
git commit -m "Add my-project"
git push
```

### 其他平台同步

```bash
cd ~/.dotfiles
git pull
```

## 路径处理建议

### 使用环境变量

```yaml
# ✅ 好 - 跨平台兼容
path: "$HOME/projects"
path: "$XDG_DOCUMENTS_DIR/work"

# ❌ 差 - 硬编码路径
path: "/home/user/projects"
path: "/Users/user/projects"
```

### 使用相对路径

```yaml
# 相对于配置目录
path: "../projects/my-project"
```

## 冲突处理

如果多平台同时修改配置：

```bash
cd ~/.dotfiles
git pull --rebase
# 解决冲突后
git add .
git rebase --continue
git push
```

## 常见问题

### Q: 某些平台工具不可用？

A: PM 会自动 fallback。在 `tools.yaml` 中配置多个选项。

### Q: 路径在不同平台不一样？

A: 使用环境变量 `$HOME` 或符号链接。

### Q: 如何忽略平台特定项目？

A: 使用 YAML 注释或单独的配置文件。
