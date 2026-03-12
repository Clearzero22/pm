# 部署指南

> **跨境电商全工作流系统** - 从开发到生产的完整部署方案

**版本**: v1.0.0
**更新时间**: 2026-03-12

---

## 目录

1. [部署架构](#部署架构)
2. [本地开发环境](#本地开发环境)
3. [生产环境部署](#生产环境部署)
4. [Docker 部署](#docker-部署)
5. [监控运维](#监控运维)
6. [备份恢复](#备份恢复)

---

## 部署架构

### 推荐架构 (Solo/小团队)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         本地部署架构                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    开发机/服务器                                  │   │
│  │                 (Ubuntu 22.04 / macOS)                          │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │                                                                 │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │   │
│  │  │   Docker     │  │ PostgreSQL   │  │    Redis     │         │   │
│  │  │  Compose     │  │   :5432      │  │    :6379     │         │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘         │   │
│  │                                                                 │   │
│  │  ┌─────────────────────────────────────────────────────────┐   │   │
│  │  │              Docker Services                            │   │   │
│  │  ├─────────────────────────────────────────────────────────┤   │   │
│  │  │  • API Gateway      (port: 8000)                        │   │   │
│  │  │  • Selection Service (port: 8001)                        │   │   │
│  │  │  • Creative Service  (port: 8002)                        │   │   │
│  │  │  • AI Service       (port: 8006, GPU)                   │   │   │
│  │  │  • MinIO            (port: 9000)                        │   │   │
│  │  │  • Nginx            (port: 80/443)                      │   │   │
│  │  └─────────────────────────────────────────────────────────┘   │   │
│  │                                                                 │   │
│  │  ┌──────────────┐  ┌──────────────┐                          │   │
│  │  │ OpenClaw     │  │   Feishu     │                          │   │
│  │  │ Gateway      │  │   Bitable    │                          │   │
│  │  │ (port:18789) │  │   (备份)      │                          │   │
│  │  └──────────────┘  └──────────────┘                          │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  外部云服务 (可选):                                                       │
│  • GPU 服务器 (用于 Stable Diffusion) - Lambda Labs / RunPod            │
│  • 向量数据库 (Pinecone) - 按需付费                                      │
│  • 云存储 (AWS S3) - 备份                                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| **服务器** | 4C/16G/200G SSD | 8C/32G/500G NVMe |
| **GPU (可选)** | - | RTX 3060 (12GB) 或更高 |
| **网络** | 10 Mbps 上行 | 100 Mbps 上行 |
| **备份** | 外置硬盘 1TB | NAS 4TB+ |

---

## 本地开发环境

### 一键安装脚本

```bash
#!/bin/bash
# scripts/setup/install.sh

set -e

echo "🛒 跨境电商全工作流系统 - 本地开发环境安装"
echo ""

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检测操作系统
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo "${GREEN}✓ 检测到系统: ${MACHINE}${NC}"

# 1. 安装依赖
echo ""
echo "${YELLOW}[1/6] 安装系统依赖...${NC}"

if [[ "$MACHINE" == "Linux" ]]; then
    sudo apt-get update
    sudo apt-get install -y \
        python3.11 python3.11-venv python3-pip \
        nodejs npm postgresql redis-server \
        docker.io docker-compose \
        git curl wget
elif [[ "$MACHINE" == "Mac" ]]; then
    if ! command -v brew &> /dev/null; then
        echo "请先安装 Homebrew: https://brew.sh/"
        exit 1
    fi
    brew install python@3.11 node postgresql redis docker-compose
fi

echo "${GREEN}✓ 系统依赖安装完成${NC}"

# 2. 克隆项目
echo ""
echo "${YELLOW}[2/6] 克隆项目...${NC}"

PROJECT_DIR="$HOME/ecommerce-system"
if [ -d "$PROJECT_DIR" ]; then
    echo "项目已存在，跳过克隆"
else
    git clone https://github.com/Clearzero22/ecommerce-system.git "$PROJECT_DIR"
fi
cd "$PROJECT_DIR"

echo "${GREEN}✓ 项目准备完成${NC}"

# 3. Python 环境
echo ""
echo "${YELLOW}[3/6] 设置 Python 环境...${NC}"

if command -v uv &> /dev/null; then
    echo "使用 uv 安装依赖..."
    uv venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
else
    echo "使用 venv 安装依赖..."
    python3.11 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
fi

echo "${GREEN}✓ Python 环境设置完成${NC}"

# 4. Node.js 环境
echo ""
echo "${YELLOW}[4/6] 设置 Node.js 环境...${NC}"

cd frontend
npm install
npm run build
cd ..

echo "${GREEN}✓ Node.js 环境设置完成${NC}"

# 5. 数据库初始化
echo ""
echo "${YELLOW}[5/6] 初始化数据库...${NC}"

# 启动 PostgreSQL
sudo systemctl start postgresql || brew services start postgresql

# 创建数据库
createdb ecommerce || true

# 运行迁移
source .venv/bin/activate
alembic upgrade head

# 加载种子数据
python scripts/seed_data.py

echo "${GREEN}✓ 数据库初始化完成${NC}"

# 6. 配置文件
echo ""
echo "${YELLOW}[6/6] 生成配置文件...${NC}"

cp .env.example .env

# 生成密钥
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env

echo "${GREEN}✓ 配置文件生成完成${NC}"
echo ""
echo "${GREEN}🎉 安装完成！${NC}"
echo ""
echo "下一步："
echo "  1. 编辑 .env 文件，配置 API 密钥"
echo "  2. 启动服务: docker-compose up -d"
echo "  3. 访问 Dashboard: http://localhost:3000"
```

### 环境变量配置

```bash
# .env.example

# ========== 基础配置 ==========
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# ========== 数据库 ==========
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ecommerce
POSTGRES_USER=ecommerce
POSTGRES_PASSWORD=your-password-here

# ========== Redis ==========
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# ========== MinIO ==========
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=ecommerce-assets

# ========== AI 服务 ==========
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo

# Stability AI (Stable Diffusion)
STABILITY_API_KEY=...

# Hugging Face (可选)
HF_API_KEY=...

# ========== Amazon ==========
AMAZON_SP_API_CLIENT_ID=...
AMAZON_SP_API_CLIENT_SECRET=...
AMAZON_SELLER_ID=...
AMAZON_MARKETPLACE_ID=ATVPDKIKX0DER  # US

# ========== OpenClaw ==========
OPENCLAW_GATEWAY_URL=http://localhost:18789
OPENCLAW_API_TOKEN=your-token-here

# ========== Feishu ==========
FEISHU_APP_ID=...
FEISHU_APP_SECRET=...
FEISHU_BITABLE_APP_TOKEN=...
FEISHU_TABLE_ID=...

# ========== 监控 ==========
SENTRY_DSN=...
ENABLE_METRICS=true
```

---

## 生产环境部署

### Docker Compose 部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    container_name: ecommerce-postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7-alpine
    container_name: ecommerce-redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # MinIO
  minio:
    image: minio/minio:latest
    container_name: ecommerce-minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ACCESS_KEY}
      MINIO_ROOT_PASSWORD: ${MINIO_SECRET_KEY}
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"
    restart: unless-stopped

  # API Gateway
  api-gateway:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ecommerce-api-gateway
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000
    env_file:
      - .env
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./backend:/app
      - asset_data:/app/assets
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - minio
    restart: unless-stopped

  # Selection Service
  selection-service:
    build:
      context: ./backend/services/selection
      dockerfile: Dockerfile
    container_name: ecommerce-selection
    command: uvicorn main:app --host 0.0.0.0 --port 8001
    env_file:
      - .env
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
    volumes:
      - ./backend/services/selection:/app
    ports:
      - "8001:8001"
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # Creative Service (with GPU)
  creative-service:
    build:
      context: ./backend/services/creative
      dockerfile: Dockerfile.gpu
    container_name: ecommerce-creative
    command: uvicorn main:app --host 0.0.0.0 --port 8002
    env_file:
      - .env
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
    volumes:
      - ./backend/services/creative:/app
      - /dev/shm:/dev/shm  # 共享内存
    ports:
      - "8002:8002"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    depends_on:
      - postgres
      - minio
    restart: unless-stopped

  # Celery Worker
  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ecommerce-celery
    command: celery -A tasks worker --loglevel=info
    env_file:
      - .env
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./backend:/app
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # Nginx
  nginx:
    image: nginx:alpine
    container_name: ecommerce-nginx
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./frontend/dist:/usr/share/nginx/html:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - api-gateway
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  minio_data:
  asset_data:

networks:
  default:
    name: ecommerce-network
```

### 启动命令

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看特定服务
docker-compose logs -f api-gateway

# 重启服务
docker-compose restart api-gateway

# 停止所有服务
docker-compose down

# 停止并删除数据
docker-compose down -v
```

---

## 监控运维

### Prometheus + Grafana

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: ecommerce-prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: ecommerce-grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana-dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3001:3000"
    restart: unless-stopped

  alertmanager:
    image: prom/alertmanager:latest
    container_name: ecommerce-alertmanager
    volumes:
      - ./monitoring/alertmanager.yml:/etc/alertmanager/alertmanager.yml
    ports:
      - "9093:9093"
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
```

### 关键指标

```python
# backend/api/monitoring/metrics.py

from prometheus_client import Counter, Histogram, Gauge

# API 指标
api_requests = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

api_latency = Histogram(
    'api_latency_seconds',
    'API request latency',
    ['method', 'endpoint']
)

# 业务指标
products_analyzed = Counter(
    'products_analyzed_total',
    'Total products analyzed'
)

images_generated = Counter(
    'images_generated_total',
    'Total images generated',
    ['type']
)

orders_processed = Counter(
    'orders_processed_total',
    'Total orders processed'
)

# 系统指标
active_tasks = Gauge(
    'active_celery_tasks',
    'Number of active Celery tasks'
)

queue_size = Gauge(
    'celery_queue_size',
    'Number of tasks in queue'
)
```

### 告警规则

```yaml
# monitoring/alerts.yml
groups:
  - name: ecommerce_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(api_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"

      - alert: SlowAPIResponse
        expr: histogram_quantile(0.95, api_latency_seconds) > 1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "API response time is too slow"

      - alert: QueueBacklog
        expr: celery_queue_size > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Celery queue backlog detected"

      - alert: LowInventory
        expr: inventory_level{quantity < 10} > 0
        for: 1m
        labels:
          severity: info
        annotations:
          summary: "Low inventory alert"
```

---

## 备份恢复

### 自动备份脚本

```bash
#!/bin/bash
# scripts/backup/backup.sh

set -e

BACKUP_DIR="/backup/ecommerce"
DATE=$(date +%Y%m%d_%H%M%S)

echo "🗄️ 开始备份..."

# 1. 数据库备份
echo "备份数据库..."
docker exec ecommerce-postgres pg_dump -U ecommerce ecommerce \
    > "$BACKUP_DIR/db_$DATE.sql"

# 2. 文件备份
echo "备份文件..."
tar -czf "$BACKUP_DIR/files_$DATE.tar.gz" \
    /var/lib/docker/volumes/ecommerce_minio_data/_data

# 3. 配置备份
echo "备份配置..."
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" \
    .env docker-compose.yml

# 4. 清理旧备份 (保留最近 30 天)
find "$BACKUP_DIR" -name "*.sql" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "✅ 备份完成: $DATE"
```

### 恢复脚本

```bash
#!/bin/bash
# scripts/backup/restore.sh

if [ -z "$1" ]; then
    echo "用法: $0 <备份日期 (格式: YYYYMMDD_HHMMSS)>"
    exit 1
fi

BACKUP_DIR="/backup/ecommerce"
DATE=$1

echo "🔄 开始恢复..."

# 1. 恢复数据库
echo "恢复数据库..."
docker exec -i ecommerce-postgres psql -U ecommerce ecommerce \
    < "$BACKUP_DIR/db_$DATE.sql"

# 2. 恢复文件
echo "恢复文件..."
tar -xzf "$BACKUP_DIR/files_$DATE.tar.gz" \
    -C /var/lib/docker/volumes/ecommerce_minio_data/_data

# 3. 恢复配置
echo "恢复配置..."
tar -xzf "$BACKUP_DIR/config_$DATE.tar.gz" -C /app

echo "✅ 恢复完成，请重启服务"
docker-compose restart
```

---

**下一步**: 开始实施 Phase 1 - 基础框架搭建
