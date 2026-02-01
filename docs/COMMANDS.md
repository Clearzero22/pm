# PM 命令完整参考

## 目录

- [项目管理](#项目管理)
- [环境管理](#环境管理)
- [配置管理](#配置管理)
- [其他命令](#其他命令)
- [选项说明](#选项说明)

---

## 项目管理

### pm add

添加新项目到注册表。

**语法：**
```bash
pm add <id> [path] [name] [description] [category]
pm add -i
pm add --interactive
```

**参数：**
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `id` | 项目唯一标识符 | 必填 |
| `path` | 项目路径 | 当前目录 |
| `name` | 项目显示名称 | 与 id 相同 |
| `description` | 项目描述 | "无描述" |
| `category` | 分类 | `dev` |

**选项：**
| 选项 | 说明 |
|------|------|
| `-i, --interactive` | 交互式添加 |

**示例：**
```bash
# 基本用法
pm add my-app

# 完整参数
pm add my-app ~/projects/my-app "我的应用" "个人项目" development

# 交互式
pm add -i
```

---

### pm list / pm ls

列出所有项目。

**语法：**
```bash
pm list
pm ls
```

**输出示例：**
```
📋 项目列表

   1. my-app
      我的应用
      /home/user/projects/my-app

   2. learn-rust
      Rust 学习
      /home/user/learn-rust
```

---

### pm search

搜索项目。

**语法：**
```bash
pm search <query>
```

**参数：**
| 参数 | 说明 |
|------|------|
| `query` | 搜索关键词 |

**搜索范围：**
- 项目 ID
- 项目名称
- 项目描述
- 项目路径

**示例：**
```bash
pm search rust
pm search work
```

---

### pm info

显示项目详细信息。

**语法：**
```bash
pm info [project-id]
```

**参数：**
| 参数 | 说明 |
|------|------|
| `project-id` | 项目 ID（不提供则显示系统信息） |

**输出示例：**
```
📦 项目详情

  ID:       my-app
  名称:     我的应用
  描述:     个人项目
  分类:     development
  路径:     /home/user/projects/my-app
```

---

### pm open

打开项目（进入项目目录）。

**语法：**
```bash
pm open <project-id>
```

**行为：**
1. 检查项目是否存在
2. 更新访问时间
3. 切换到项目目录

**示例：**
```bash
pm open my-app
# 相当于 cd ~/projects/my-app
```

---

### pm start

启动完整项目环境（tmux 会话）。

**语法：**
```bash
pm start <project-id>
```

**行为：**
1. 根据项目预设创建 tmux 会话
2. 启动配置的工具（编辑器、终端等）
3. 附加到会话

**预设布局：**
| 预设 | 布局 |
|------|------|
| `dev-ai` | 编辑器 (左) + AI (中) + 终端 (右) |
| `dev-standard` | 编辑器 (上) + 终端 (下) |
| `learning` | 笔记 (左) + 终端 (右) 横向 |
| `reading` | 文件列表 (上) + 终端 (下) 纵向 |

**示例：**
```bash
pm start my-app

# tmux 操作：
# Ctrl+b c  - 新建窗口
# Ctrl+b o  - 切换窗格
# Ctrl+b d  - 分离会话
```

---

### pm select

交互式选择项目（需要 fzf）。

**语法：**
```bash
pm select
```

**快捷键：**
| 按键 | 功能 |
|------|------|
| `Enter` | 打开项目 |
| `Ctrl+E` | 编辑配置 |
| `Ctrl+D` | 删除项目 |
| `Esc` | 取消 |

---

### pm edit

编辑项目配置。

**语法：**
```bash
pm edit <project-id>
```

**行为：**
- 打开配置文件编辑器
- 光标定位到项目位置

---

### pm remove / pm rm

删除项目。

**语法：**
```bash
pm remove <project-id>
pm rm <project-id>
```

**行为：**
- 仅删除配置记录
- 不删除实际项目文件

**示例：**
```bash
pm remove old-project
```

---

## 环境管理

### pm session list

列出所有 tmux 会话。

**语法：**
```bash
pm session list
pm session ls
```

---

### pm session attach

附加到 tmux 会话。

**语法：**
```bash
pm session attach [session-name]
```

**参数：**
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `session-name` | 会话名称 | 最近使用的会话 |

---

### pm session kill

销毁 tmux 会话。

**语法：**
```bash
pm session kill <session-name>
```

**示例：**
```bash
pm session kill my-app
```

---

## 配置管理

### pm config

管理 PM 配置。

**语法：**
```bash
pm config
pm config init
pm config [projects|tools]
```

**子命令：**
| 子命令 | 说明 |
|--------|------|
| (无) | 编辑项目配置 |
| `init` | 初始化配置文件 |
| `projects` | 编辑项目注册表 |
| `tools` | 编辑工具配置 |

**示例：**
```bash
# 初始化
pm config init

# 编辑项目配置
pm config
vi ~/.pm/projects.yaml

# 编辑工具配置
pm config tools
```

---

### pm preset list

列出所有可用预设。

**语法：**
```bash
pm preset list
```

**输出示例：**
```
📦 可用预设

  dev-ai
  dev-standard
  learning
  reading
```

---

## 其他命令

### pm help

显示帮助信息。

**语法：**
```bash
pm help
pm -h
pm --help
```

---

### pm version

显示版本信息。

**语法：**
```bash
pm version
pm -v
pm --version
```

---

### pm (无参数)

显示主菜单或选择界面。

**语法：**
```bash
pm
```

**行为：**
- 如果安装了 fzf：显示交互式菜单
- 否则：显示文本菜单

---

## 选项说明

### 全局选项

| 选项 | 说明 |
|------|------|
| `-h, --help` | 显示帮助 |
| `-v, --version` | 显示版本 |
| `--` | 结束选项解析 |

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `PM_CONFIG_DIR` | 配置目录 | `~/.pm` |
| `PM_PROJECTS_FILE` | 项目配置文件 | `~/.pm/projects.yaml` |
| `PM_TOOLS_FILE` | 工具配置文件 | `~/.pm/tools.yaml` |
| `EDITOR` | 默认编辑器 | `vi` |

---

## 退出码

| 代码 | 说明 |
|------|------|
| `0` | 成功 |
| `1` | 一般错误 |
| `2` | 用法错误 |
| `127` | 命令未找到 |

---

## 相关文档

- [快速开始](QUICKSTART.md)
- [配置详解](CONFIGURATION.md)
- [多平台同步](MULTIPLATFORM.md)
- [常见问题](FAQ.md)
