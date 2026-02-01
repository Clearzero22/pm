# PM 常见问题

---

## 安装问题

### Q: 命令未找到

**症状：**
```
pm: command not found
```

**原因：** PM 不在 PATH 中

**解决方案：**

```bash
# 方案 1: 添加到 PATH
echo 'export PATH="$HOME/.pm:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 方案 2: 创建符号链接
sudo ln -s ~/.pm/pm /usr/local/bin/pm

# 方案 3: 使用完整路径
~/.pm/pm list
```

---

### Q: 权限被拒绝

**症状：**
```
bash: ./pm: Permission denied
```

**解决方案：**
```bash
chmod +x pm
```

---

### Q: 依赖缺失

**症状：**
```
yq: command not found
python: command not found
```

**解决方案：**

**Linux:**
```bash
sudo apt install yq python3
```

**macOS:**
```bash
brew install yq python3
```

**Termux:**
```bash
pkg install python yq
```

---

## 配置问题

### Q: 配置文件不存在

**症状：**
```
Error: ~/.pm/projects.yaml not found
```

**解决方案：**
```bash
pm config init
```

---

### Q: YAML 语法错误

**症状：**
```
Error: invalid YAML syntax
```

**常见原因：**

1. **缩进错误**
```yaml
# ❌ 错误
projects:
- id: my-app
name: MyApp  # 缩进不正确

# ✅ 正确
projects:
  - id: my-app
    name: MyApp
```

2. **引号未闭合**
```yaml
# ❌ 错误
description: "我的项目

# ✅ 正确
description: "我的项目"
```

3. **特殊字符未转义**
```yaml
# ❌ 错误
path: C:\Users\name

# ✅ 正确
path: "C:\\Users\\name"
```

---

### Q: 路径包含空格

**症状：**
```
Error: path not found
```

**解决方案：**
```yaml
# 使用引号
path: "$HOME/My Projects/app"

# 或使用转义
path: $HOME/My\ Projects/app
```

---

## 使用问题

### Q: tmux 会话已存在

**症状：**
```
Error: tmux session "my-app" already exists
```

**解决方案：**

```bash
# 附加到现有会话
pm session attach my-app

# 或先销毁再启动
pm session kill my-app
pm start my-app
```

---

### Q: 编辑器未启动

**症状：**
```
启动项目后编辑器没有打开
```

**原因：**
1. 编辑器未安装
2. GUI 程序在服务器上
3. 配置的工具名称错误

**解决方案：**

```bash
# 检查编辑器是否可用
which nvim

# 检查配置
pm config tools

# 更换编辑器
pm edit my-project
# 修改 editor: nvim
```

---

### Q: 环境变量不生效

**症状：**
```
项目中的环境变量没有设置
```

**原因：** PM 不自动设置环境变量

**解决方案：**

在项目的 `.env` 文件或 shell 配置中设置：

```bash
# ~/projects/my-app/.env
export NODE_ENV=development
export API_KEY="your-key"
```

或在 `~/.zshrc` 中：
```bash
source ~/projects/my-app/.env
```

---

### Q: 项目路径不正确

**症状：**
```
Error: project path does not exist
```

**解决方案：**

```bash
# 检查路径是否正确
ls "$HOME/projects/my-app"

# 使用绝对路径
pm edit my-project
# 修改 path 为绝对路径

# 或创建目录
mkdir -p ~/projects/my-app
```

---

## 性能问题

### Q: 项目列表加载慢

**症状：**
```
pm list 命令响应很慢
```

**原因：**
1. 项目数量过多
2. 网络路径
3. YAML 解析慢

**解决方案：**

```bash
# 使用搜索代替列表
pm search keyword

# 或使用分类过滤
# （手动编辑 projects.yaml）
```

---

### Q: fzf 选择卡顿

**症状：**
```
pm select 时 fzf 响应慢
```

**解决方案：**

```bash
# 更新 fzf
# Linux
sudo apt update && sudo apt install fzf

# macOS
brew upgrade fzf
```

---

## 多平台问题

### Q: 不同平台路径不同

**症状：**
```
Linux 和 macOS 上路径不一致
```

**解决方案：**

使用环境变量：
```yaml
# ❌ 不推荐
path: "/home/user/projects"      # Linux
path: "/Users/user/projects"      # macOS

# ✅ 推荐
path: "$HOME/projects"
```

---

### Q: Termux 上无法使用 GUI 工具

**症状：**
```
Termux 启动编辑器失败
```

**原因：** Termux 不支持 GUI

**解决方案：**

```yaml
tools:
  editor: micro      # Termux 友好
  # editor: code     # 不会工作
```

---

### Q: Git 同步冲突

**症状：**
```
git pull 时出现冲突
```

**解决方案：**

```bash
cd ~/.dotfiles

# 使用 rebase
git pull --rebase

# 解决冲突后
git add .
git rebase --continue
git push
```

---

## 高级问题

### Q: 如何备份配置？

**解决方案：**

```bash
# 方案 1: Git 同步
cd ~/.pm
git init
git add .
git commit -m "backup"

# 方案 2: 手动备份
cp -r ~/.pm ~/.pm.backup.$(date +%Y%m%d)

# 方案 3: 使用 rsync
rsync -av ~/.pm/ ~/backup/pm/
```

---

### Q: 如何迁移配置？

**解决方案：**

```bash
# 导出配置
tar czf pm-config.tar.gz ~/.pm

# 在新设备上导入
tar xzf pm-config.tar.gz -C ~/
```

---

### Q: 如何调试问题？

**解决方案：**

```bash
# 启用调试模式
export PM_DEBUG=1
pm list

# 查看详细日志
pm list 2>&1 | tee debug.log

# 检查配置
yq eval '.' ~/.pm/projects.yaml
```

---

## 错误代码

| 代码 | 说明 | 解决方法 |
|------|------|----------|
| `1` | 一般错误 | 查看错误信息 |
| `2` | 用法错误 | 检查命令语法 |
| `127` | 命令未找到 | 检查 PATH 和安装 |
| `130` | 用户中断 | 正常退出 |

---

## 获取帮助

### 内置帮助

```bash
pm help           # 查看帮助
pm --help         # 查看选项
pm version        # 查看版本
pm info           # 系统信息
```

### 日志位置

```bash
# 日志文件
~/.pm/pm.log

# 查看日志
cat ~/.pm/pm.log
tail -f ~/.pm/pm.log
```

### 报告问题

在 GitHub 报告问题时，请包含：

1. PM 版本 (`pm version`)
2. 系统信息 (`pm info`)
3. 错误信息
4. 复现步骤

```bash
# 收集诊断信息
pm version > bug-report.txt
pm info >> bug-report.txt
pm list 2>&1 >> bug-report.txt
```

---

## 相关资源

- [快速开始](QUICKSTART.md)
- [命令参考](COMMANDS.md)
- [配置详解](CONFIGURATION.md)
- [多平台同步](MULTIPLATFORM.md)
- [GitHub 仓库](https://github.com/Clearzero22/pm)
