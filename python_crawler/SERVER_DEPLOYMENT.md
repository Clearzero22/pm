# Amazon Crawler - 服务器部署指南

## 环境要求

### Linux 服务器系统要求

| 组件 | 要求 |
|------|------|
| 操作系统 | Ubuntu 20.04+, Debian 11+, CentOS 8+, RHEL 8+ |
| Python | >= 3.14 |
| 内存 | >= 2GB (推荐 4GB) |
| 磁盘 | >= 10GB 可用空间 |

### 系统依赖

#### Debian/Ubuntu
```bash
# 安装依赖
sudo apt-get update
sudo apt-get install -y \
    python3 \
    python3-venv \
    curl \
    git \
    libatk-bridge2.0-0 \
    libxkbcommon0 \
    libgbm1 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2
```

#### CentOS/RHEL
```bash
sudo yum install -y \
    python3 \
    curl \
    git \
    alsa-lib \
    atk \
    cups-libs \
    gtk3 \
    libXcomposite \
    libXcursor \
    libXdamage \
    libXext \
    libXi \
    libXrandr \
    libXScrnSaver \
    libXtst \
    pango \
    xorg-x11-fonts-100dpi \
    xorg-x11-fonts-75dpi \
    xorg-x11-utils \
    xorg-x11-xauth
```

---

## 快速部署

### 1. 安装 uv 包管理器

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 克隆/上传项目

```bash
# 从 Git 克隆
git clone <your-repo-url>
cd python_crawler

# 或直接上传项目文件
scp -r python_crawler/ user@server:/path/to/
```

### 3. 安装依赖

```bash
# 安装 Python 依赖
uv sync

# 安装 Playwright 浏览器
uv run playwright install chromium --with-deps
```

### 4. 测试运行

```bash
# 测试无头模式
uv run python main.py --pages 1 --products 2 --headless
```

---

## 运行方式

### 方式 1: 直接运行 (简单)

```bash
# Best Sellers 模式
uv run python main.py --pages 1 --products 10 --headless

# 搜索模式
uv run python main.py --search "water bottle" --products 10 --headless
```

### 方式 2: 使用服务器脚本

```bash
# 给脚本执行权限
chmod +x run_server.sh

# 运行
./run_server.sh
```

### 方式 3: 使用服务器运行器

```bash
# Best Sellers
python server_runner.py --bestsellers --pages 2 --products 20

# 搜索
python server_runner.py --search "blender" --pages 2 --products 20 --sort review-rank
```

---

## 定时任务 (Cron)

### 设置定时爬取

```bash
# 编辑 crontab
crontab -e
```

### Cron 示例

```bash
# 每天凌晨 2 点运行 Best Sellers 爬虫
0 2 * * * cd /path/to/python_crawler && uv run python main.py --pages 2 --products 20 --headless >> logs/cron.log 2>&1

# 每 6 小时搜索热门关键词
0 */6 * * * cd /path/to/python_crawler && uv run python main.py --search "water bottle" --products 30 --headless >> logs/search.log 2>&1

# 每周一早上 8 点爬取本周新品
0 8 * * 1 cd /path/to/python_crawler && uv run python main.py --search "new releases" --sort date-desc --headless >> logs/weekly.log 2>&1
```

---

## Docker 部署 (推荐)

### Dockerfile

```dockerfile
FROM python:3.14-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    libatk-bridge2.0-0 \
    libxkbcommon0 \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装依赖
RUN uv sync
RUN uv run playwright install chromium --with-deps

# 创建输出目录
RUN mkdir -p output logs

# 设置环境变量
ENV PYTHONUNBUFFERED=1
DISPLAY=:99

# 运行命令
CMD ["uv", "run", "python", "main.py", "--headless", "--pages", "1", "--products", "10"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  crawler:
    build: .
    volumes:
      - ./output:/app/output
      - ./logs:/app/logs
    environment:
      - TZ=Asia/Shanghai
    restart: unless-stopped
```

### 运行 Docker

```bash
# 构建镜像
docker build -t amazon-crawler .

# 运行容器
docker run -v $(pwd)/output:/app/output amazon-crawler

# 使用 docker-compose
docker-compose up -d
```

---

## 监控与日志

### 日志位置

```
python_crawler/
├── logs/
│   ├── crawler_20250312_020000.log
│   ├── crawler_20250312_060000.log
│   └── ...
└── output/
    ├── bestsellers_20250312_020000.csv
    └── search_water_bottle_20250312_020000.csv
```

### 日志轮转

创建 `/etc/logrotate.d/amazon-crawler`:

```
/path/to/python_crawler/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

---

## 故障排查

### 问题 1: 浏览器无法启动

```bash
# 检查是否安装了依赖
uv run playwright install chromium --with-deps

# 检查系统库
ldd ~/.cache/ms-playwright/chromium-*/chrome-linux/chrome
```

### 问题 2: 显示相关错误

```bash
# 使用虚拟显示
sudo apt-get install xvfb
xvfb-run uv run python main.py --headless
```

### 问题 3: 内存不足

```bash
# 创建 swap 文件
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 性能优化

### 1. 调整并发数

```python
# 根据服务器配置调整
# 低配服务器 (2GB RAM)
--pages 1 --products 5

# 中配服务器 (4GB RAM)
--pages 2 --products 10

# 高配服务器 (8GB+ RAM)
--pages 3 --products 20
```

### 2. 使用优化版并行爬虫

```bash
# 优化版 (4.2x 速度)
uv run python optimized_parallel_crawler.py
```

### 3. 设置代理

```python
# 在 crawler.py 中添加
context = browser.new_context(
    proxy={"server": "http://proxy.example.com:8080"}
)
```

---

## 安全建议

1. **使用环境变量存储敏感信息**
   ```bash
   export AMAZON_PROXY="http://proxy:8080"
   export API_KEY="your-key"
   ```

2. **限制日志权限**
   ```bash
   chmod 700 logs/
   ```

3. **定期更新依赖**
   ```bash
   uv sync --upgrade
   ```

4. **使用防火墙**
   ```bash
   # 只允许出站连接
   sudo ufw default deny incoming
   sudo ufw default allow outgoing
   sudo ufw enable
   ```
