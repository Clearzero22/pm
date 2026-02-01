# Termux 设置指南

## 📖 目录

- [Termux 简介](#termux-简介)
- [安装 Termux](#安装-termux)
- [基础配置](#基础配置)
- [安装依赖](#安装依赖)
- [pm 配置](#pm-配置)
- [使用技巧](#使用技巧)
- [常见问题](#常见问题)

---

## 📱 Termux 简介

Termux 是 Android 上的高级终端模拟器，无需 root 权限即可运行 Linux 环境。

### 特性
- ✅ 完整的 Linux shell (bash/zsh)
- ✅ 包管理器 (pkg)
- ✅ 支持 tmux、vim、neovim 等工具
- ✅ 支持 SSH 服务器和客户端
- ✅ 支持编程语言 (Python, Go, Rust, Node.js 等)

### 限制
- ❌ 无原生 GUI 应用
- ❌ 部分系统命令受限
- ❌ 性能受设备限制

---

## 📲 安装 Termux

### 方法 1: F-Droid（推荐）

1. 访问 [F-Droid](https://f-droid.org/packages/com.termux/)
2. 下载并安装 Termux APK
3. 允许安装未知来源应用

### 方法 2: GitHub

1. 访问 [Termux GitHub Releases](https://github.com/termux/termux-app/releases)
2. 下载最新的 APK
3. 安装并运行

### 注意事项

- ⚠️ 不要从 Google Play Store 安装（版本过旧）
- ⚠️ 允许 Termux 访问存储权限（如果需要）
- ⚠️ 定期更新 Termux 应用和包

---

## ⚙️ 基础配置

### 更新包管理器

```bash
# 更新包列表
pkg update

# 升级所有包
pkg upgrade
```

### 安装常用工具

```bash
# 基础工具
pkg install git curl wget

# 编辑器
pkg install neovim vim nano

# 终端工具
pkg install tmux zsh fish

# 搜索工具
pkg install fzf ripgrep fd-find bat tree

# 开发工具
pkg install nodejs python go rust
```

### 配置 Zsh

```bash
# 安装 Oh My Zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# 设置 Zsh 为默认 Shell
chsh -s zsh

# 重启 Termux
```

### 配置 Neovim

```bash
# 创建配置目录
mkdir -p ~/.config/nvim

# 创建 init.vim
cat > ~/.config/nvim/init.vim << 'VIM'
set number
set relativenumber
set tabstop=4
set shiftwidth=4
set expandtab
set ignorecase
set smartcase
set mouse=a
syntax on
VIM
```

### 配置 SSH

#### 启用 SSH 服务器

```bash
# 安装 OpenSSH
pkg install openssh

# 设置密码
passwd

# 启动 SSH 服务器
sshd

# 查看设备 IP
ifconfig
```

#### 从电脑连接

```bash
# 在电脑上连接
ssh <termux-user>@<device-ip> -p 8022

# 默认端口是 8022
```

---

## 🔧 安装 pm 依赖

### 安装 yq（YAML 解析）

```bash
# 方法 1: 从 GitHub 下载
wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_arm -O /data/data/com.termux/files/usr/bin/yq
chmod +x /data/data/com.termux/files/usr/bin/yq

# 方法 2: 使用 pkg（如果可用）
pkg install yq

# 验证安装
yq --version
```

### 安装 fzf

```bash
pkg install fzf

# 验证安装
fzf --version
```

### 安装 tmux

```bash
pkg install tmux

# 验证安装
tmux -V
```

### 验证所有依赖

```bash
# 检查依赖
command -v yq && echo "yq: OK" || echo "yq: NOT FOUND"
command -v fzf && echo "fzf: OK" || echo "fzf: NOT FOUND"
command -v tmux && echo "tmux: OK" || echo "tmux: NOT FOUND"
command -v git && echo "git: OK" || echo "git: NOT FOUND"
```

---

## 📦 pm 配置

### 1. 安装 pm

```bash
# 克隆或复制项目到 Termux
git clone <your-repo-url> ~/pm-project-manager

# 或通过 SSH 从电脑传输
scp -r pm-project-manager <termux-ip>:/data/data/com.termux/files/home/

# 进入项目目录
cd ~/pm-project-manager
```

### 2. 创建软链接

```bash
# 创建 bin 目录
mkdir -p ~/bin

# 创建软链接
ln -s $(pwd)/pm ~/bin/pm

# 添加到 PATH
echo 'export PATH="$PATH:~/bin"' >> ~/.zshrc
source ~/.zshrc
```

### 3. 初始化 pm

```bash
# 初始化配置
pm config init

# 检查配置目录
ls -la ~/.pm/
```

### 4. 调整工具配置

编辑 `~/.pm/tools.yaml`，将 GUI 编辑器改为终端编辑器：

```yaml
editors:
  zed:
    command: "nvim"  # 改为 nvim
    args: ["."]
    gui: false      # 改为 false
  code:
    command: "nvim"  # 改为 nvim
    args: ["."]
    gui: false
```

### 5. 添加第一个项目

```bash
# 交互式添加
pm add -i

# 或命令行添加
pm add termux-project "Termux Project" "~/projects/termux-project" development "Termux项目" learning
```

### 6. 测试运行

```bash
# 列出项目
pm list

# 启动项目（使用 learning 预设）
pm start termux-project
```

---

## 💡 使用技巧

### 1. 使用外部键盘

在 Android 设置中配置输入法：
- Hacker's Keyboard
- Termux:API 键盘
- 物理蓝牙键盘

### 2. 长时间运行任务

```bash
# 在 tmux 中运行长时间任务
tmux new -s long-task

# 运行任务
npm run build

# 分离会话（Ctrl+b d）

# 稍后重新连接
tmux attach -t long-task
```

### 3. 从电脑访问 Termux

```bash
# 在 Termux 中启用 SSH
sshd

# 在电脑上通过 SSH 连接
ssh <termux-user>@<device-ip> -p 8022

# 现在可以在电脑上使用 pm
pm list
pm start my-project
```

### 4. 在 tmux 中使用 pm

```bash
# 创建会话
tmux new -s pm-workspace

# 在 tmux 中使用 pm
pm select
pm start my-project

# 切换到不同的项目会话
Ctrl+b s  # 切换会话
```

### 5. 文件访问权限

```bash
# 允许 Termux 访问存储
termux-setup-storage

# 现在可以访问 /sdcard/
cd /sdcard/Download/
```

### 6. 使用外部存储

```bash
# 在外部存储中创建项目
pm add external-project "External Project" "/sdcard/projects/external" development "外部存储项目" learning

# 注意：路径需要使用完整路径
```

### 7. 优化性能

```bash
# 使用轻量级编辑器
pm config tools
# 将 editor 改为 vim 而不是 nvim

# 减少后台进程
# 不要同时运行太多 tmux 会话
```

---

## 🔍 常见问题

### Q1: yq 安装失败

**解决**:
```bash
# 确保下载正确的架构
uname -m

# 对于 ARM 设备
wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_arm -O ~/bin/yq
chmod +x ~/bin/yq
```

### Q2: tmux 会话丢失

**原因**: Termux 被系统杀死

**解决**:
```bash
# 使用 tmux-resurrect 保存会话
git clone https://github.com/tmux-plugins/tmux-resurrect ~/.tmux/plugins/tmux-resurrect

# 在 ~/.tmux.conf 中添加
run-shell ~/.tmux/plugins/tmux-resurrect/resurrect.tmux

# 保存会话
Ctrl+b Ctrl+s
```

### Q3: 存储权限问题

**解决**:
```bash
# 运行存储设置
termux-setup-storage

# 授予 Termux 存储权限
```

### Q4: SSH 无法连接

**解决**:
```bash
# 检查 SSH 服务是否运行
ps aux | grep sshd

# 重启 SSH 服务
pkill sshd
sshd

# 检查端口
netstat -tuln | grep 8022
```

### Q5: 编辑器启动慢

**解决**:
```bash
# 使用更轻量的编辑器
pm config tools
# 将 editor 改为 vim

# 或配置 Neovim 禁用插件
cat > ~/.config/nvim/init.vim << 'VIM'
set number
set relativenumber
" 禁用插件以提升性能
VIM
```

### Q6: 中文显示乱码

**解决**:
```bash
# 安装中文字体
pkg install noto-fonts-cjk

# 设置终端编码
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8
```

---

## 📚 推荐阅读

- [Termux Wiki](https://wiki.termux.com/)
- [Termux Packages](https://github.com/termux/termux-packages)
- [Android 开发与 Termux](https://github.com/termux/termux-app)

---

## 📄 许可证

MIT License
