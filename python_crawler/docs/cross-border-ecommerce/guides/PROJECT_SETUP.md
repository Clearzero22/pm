# 项目设置指南

> **跨境电商全工作流系统** - 从零开始的开发环境配置

**预计时间**: 30-45 分钟
**难度**: 初级

---

## 目录

1. [系统要求](#系统要求)
2. [快速开始](#快速开始)
3. [详细配置](#详细配置)
4. [验证安装](#验证安装)
5. [常见问题](#常见问题)

---

## 系统要求

### 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| **CPU** | 4 核心 | 8+ 核心 |
| **内存** | 16 GB | 32 GB |
| **存储** | 200 GB SSD | 500 GB NVMe |
| **GPU** | - | RTX 3060 (12GB) 或更高 |
| **网络** | 10 Mbps 上行 | 100 Mbps 上行 |

### 软件要求

| 软件 | 版本 | 说明 |
|------|------|------|
| **操作系统** | Ubuntu 22.04 / macOS 13+ | Windows 支持 WSL2 |
| **Python** | 3.11+ | 推荐 3.11 |
| **Node.js** | 20+ | 前端构建 |
| **Docker** | 24+ | 容器化部署 |
| **PostgreSQL** | 15+ | 数据库 |
| **Redis** | 7+ | 缓存/队列 |

---

## 快速开始

### 一键安装 (Linux/macOS)

```bash
#!/bin/bash
# 快速安装脚本

# 1. 克隆仓库
git clone https://github.com/Clearzero22/ecommerce-system.git
cd ecommerce-system

# 2. 运行安装脚本
chmod +x scripts/setup/install.sh
./scripts/setup/install.sh

# 3. 启动服务
docker-compose up -d

# 4. 访问 Dashboard
open http://localhost:3000
```

### Windows 安装

```powershell
# 1. 安装 WSL2
wsl --install

# 2. 在 WSL2 中运行
wsl
bash
git clone https://github.com/Clearzero22/ecommerce-system.git
cd ecommerce-system
./scripts/setup/install.sh
```

---

## 详细配置

### 1. 系统依赖安装

#### Ubuntu/Debian

```bash
# 更新包管理器
sudo apt-get update

# 安装基础工具
sudo apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    software-properties-common

# 安装 Python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev

# 安装 Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 安装 PostgreSQL
sudo apt-get install -y postgresql postgresql-contrib

# 安装 Redis
sudo apt-get install -y redis-server

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### macOS

```bash
# 安装 Homebrew (如果未安装)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装依赖
brew install python@3.11 node postgresql redis docker-compose

# 安装 uv (Python 包管理器)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Python 环境配置

```bash
# 进入项目目录
cd ecommerce-system

# 创建虚拟环境
python3.11 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 安装 uv (更快的包管理器)
pip install uv

# 安装依赖
uv pip install -r requirements.txt
```

### 3. 数据库初始化

```bash
# 启动 PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql    # macOS

# 创建数据库和用户
sudo -u postgres psql

CREATE DATABASE ecommerce;
CREATE USER ecommerce WITH PASSWORD 'your_password_here';
GRANT ALL PRIVILEGES ON DATABASE ecommerce TO ecommerce;
\q

# 运行迁移
source .venv/bin/activate
alembic upgrade head

# 加载种子数据
python scripts/seed_data.py
```

### 4. 环境变量配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
nano .env
```

**必须配置的关键变量**:

```bash
# ========== 必须修改 ==========
SECRET_KEY=your-secret-key-here-change-me
POSTGRES_PASSWORD=your-database-password

# ========== AI 服务 ==========
OPENAI_API_KEY=sk-your-openai-api-key

# ========== Amazon API ==========
AMAZON_SP_API_CLIENT_ID=your-client-id
AMAZON_SP_API_CLIENT_SECRET=your-client-secret
AMAZON_SP_API_REFRESH_TOKEN=your-refresh-token
AMAZON_SELLER_ID=your-seller-id

# ========== OpenClaw ==========
OPENCLAW_API_TOKEN=your-openclaw-token

# ========== Feishu (可选) ==========
FEISHU_APP_ID=your-app-id
FEISHU_APP_SECRET=your-app-secret
```

### 5. 启动服务

#### 开发模式

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 启动 API 服务
source .venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端开发服务器
cd frontend
npm install
npm run dev
```

#### 生产模式

```bash
# 使用 Docker Compose 启动所有服务
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 检查服务状态
docker-compose ps
```

---

## 验证安装

### 健康检查

```bash
# API 健康检查
curl http://localhost:8000/health

# 预期输出
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00Z"
}

# 数据库连接检查
python scripts/check_db.py

# Redis 连接检查
python scripts/check_redis.py
```

### 访问服务

| 服务 | URL | 默认账号 |
|------|-----|----------|
| **API 文档** | http://localhost:8000/docs | - |
| **Dashboard** | http://localhost:3000 | admin/admin |
| **Grafana** | http://localhost:3001 | admin/admin |
| **MinIO** | http://localhost:9001 | minioadmin/minioadmin |

---

## 常见问题

### Q1: Python 版本不兼容

**问题**: 系统默认 Python 版本过低

**解决**:
```bash
# 使用 pyenv 管理 Python 版本
curl https://pyenv.run | bash
pyenv install 3.11
pyenv global 3.11
```

### Q2: Docker 权限问题

**问题**: Got permission denied while trying to connect to the Docker daemon

**解决**:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Q3: PostgreSQL 连接失败

**问题**: connection refused to PostgreSQL

**解决**:
```bash
# 检查 PostgreSQL 状态
sudo systemctl status postgresql

# 启动 PostgreSQL
sudo systemctl start postgresql

# 检查连接
psql -U ecommerce -d ecommerce
```

### Q4: 端口被占用

**问题**: Address already in use

**解决**:
```bash
# 查看占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>

# 或修改 .env 中的端口
PORT=8001
```

### Q5: GPU 不可用

**问题**: CUDA out of memory / GPU not found

**解决**:
```bash
# 检查 NVIDIA 驱动
nvidia-smi

# 安装 NVIDIA Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

---

## 下一步

安装完成后，建议按以下顺序进行：

1. ✅ 阅读 [README.md](../README.md) 了解系统概览
2. ✅ 查看 [DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md) 了解开发流程
3. ✅ 运行第一个示例: [QUICK_START.md](./QUICK_START.md)
4. ✅ 开始 Phase 1: 基础框架搭建

---

**遇到问题?**
- 查看完整文档: [../README.md](../README.md)
- 提交 Issue: https://github.com/Clearzero22/ecommerce-system/issues
- 加入社区讨论
