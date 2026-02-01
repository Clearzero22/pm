# PM - Project Manager

> 跨平台项目管理与启动工具 | 统一管理开发、学习、阅读项目

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/github-Clearzero22%2Fpm-brightgreen.svg)](https://github.com/Clearzero22/pm)

---

## ✨ 特性

- 📁 **统一管理** - 集中管理所有项目（开发/学习/阅读/研究）
- 🚀 **快速启动** - 一键启动完整开发环境（编辑器 + AI + 终端）
- 🖥️ **多会话** - 使用 tmux 管理多个项目会话
- 🤖 **AI 集成** - 支持 Claude、Codex、Aider 等 AI 工具
- 📱 **跨平台** - 支持 Linux、macOS、Termux、远程服务器
- 🎨 **自定义预设** - 灵活的布局和工具配置
- 🔍 **快速搜索** - 使用 fzf 快速查找项目
- ⚡ **高效工作流** - 优化的开发体验

---

## 🚀 5 分钟快速开始

### 1. 安装

```bash
# 克隆仓库
git clone https://github.com/Clearzero22/pm.git ~/.pm
cd ~/.pm

# 添加到 PATH
echo 'export PATH="$HOME/.pm:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 2. 初始化

```bash
pm config init
```

### 3. 添加项目

```bash
pm add my-app ~/projects/my-app "我的应用" development
```

### 4. 启动项目

```bash
pm start my-app
```

---

## 📖 完整文档

| 文档 | 说明 |
|------|------|
| **[快速开始](docs/QUICKSTART.md)** | 5 分钟上手指南 |
| **[命令参考](docs/COMMANDS.md)** | 所有命令完整说明 |
| **[配置详解](docs/CONFIGURATION.md)** | 配置文件和选项 |
| **[多平台同步](docs/MULTIPLATFORM.md)** | 跨设备配置同步 |
| **[常见问题](docs/FAQ.md)** | 问题排查和解决 |

---

## 📸 预览

### 主菜单（fzf）

```
💻 开发项目
  [1] my-app-frontend    React前端       ~/projects/my-app
  [2] backend-api         Go后端API       ~/projects/backend

📚 学习项目
  [3] rust-learning       Rust学习        ~/learning/rust
```

### tmux 布局（AI 开发模式）

```
┌─────────────────────────────────┐
│                                 │
│         编辑器 (50%)             │
│                                 │
├───────────────────┬─────────────┤
│    AI (25%)       │  zsh (25%)  │
│                   │             │
└───────────────────┴─────────────┘
```

---

## 💻 核心命令

```bash
# 项目管理
pm list                  # 列出所有项目
pm add -i               # 交互式添加
pm open <project-id>     # 打开项目
pm start <project-id>    # 启动完整环境
pm search <query>       # 搜索项目

# 会话管理
pm session list         # 列出 tmux 会话
pm session attach       # 附加到会话

# 配置管理
pm config               # 编辑配置
pm preset list          # 列出预设
```

---

## 📦 预设模板

| 预设 | 布局 | 适用场景 |
|------|------|----------|
| `dev-ai` | 编辑器 + AI + 终端 | AI 辅助开发 |
| `dev-standard` | 编辑器 + 终端 | 标准开发 |
| `learning` | 笔记 + 终端 | 学习/研究 |
| `reading` | 文件列表 + 终端 | 阅读文档 |

---

## 🌟 使用场景

### 日常开发

```bash
# 添加工作项目
pm add work-api ~/work/api "工作API" development

# 启动 AI 辅助开发环境
pm start work-api --preset dev-ai
```

### 学习新技术

```bash
# 添加学习项目
pm add learn-rust ~/learn/rust "Rust学习" learning

# 启动学习环境
pm start learn-rust --preset learning
```

### 跨平台同步

```bash
# 使用 Git 同步配置
git clone https://github.com/yourusername/dotfiles.git ~/.dotfiles
cd ~/.dotfiles && bash install.sh
```

详见 [多平台同步指南](docs/MULTIPLATFORM.md)

---

## 🏗️ 项目结构

```
pm/
├── pm                      # 主入口脚本
├── install.sh              # 安装脚本
├── core/                   # 核心模块
│   ├── platform.sh         # 平台检测
│   ├── config.sh           # 配置管理
│   ├── project-registry.sh # 项目注册表
│   └── tmux-manager.sh     # tmux 管理
├── ui/                     # 用户界面
│   └── fzf-selector.sh     # fzf 选择器
├── presets/                # 预设模板
│   ├── dev-ai.yml
│   ├── dev-standard.yml
│   ├── learning.yml
│   └── reading.yml
└── docs/                   # 文档
    ├── QUICKSTART.md
    ├── COMMANDS.md
    ├── CONFIGURATION.md
    ├── MULTIPLATFORM.md
    └── FAQ.md
```

---

## 🔧 配置示例

### 项目配置 (~/.pm/projects.yaml)

```yaml
categories:
  - id: "development"
    name: "开发项目"
    icon: "💻"

projects:
  - id: my-app
    name: 我的应用
    path: "$HOME/projects/my-app"
    category: development
    tools:
      editor: nvim
      terminal: zsh
      ai: claude
    preset: dev-ai
```

### 工具配置 (~/.pm/tools.yaml)

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

## 🤝 贡献

欢迎贡献！请查看 [开发文档](docs/development.md)

1. Fork 项目
2. 创建分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🙏 致谢

- [yq](https://github.com/mikefarah/yq) - YAML 处理
- [fzf](https://github.com/junegunn/fzf) - 命令行模糊查找器
- [tmux](https://github.com/tmux/tmux) - 终端复用器

---

## 📧 联系方式

- GitHub: [Clearzero22/pm](https://github.com/Clearzero22/pm)
- Issues: [提交问题](https://github.com/Clearzero22/pm/issues)

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**
