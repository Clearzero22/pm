# OpenClaw + Amazon Crawler 集成指南

> **通过 OpenClaw 网关，随时随地通过消息控制 Amazon 爬虫运行**

---

## 📋 目录

1. [架构概述](#架构概述)
2. [前置准备](#前置准备)
3. [集成步骤](#集成步骤)
4. [使用场景](#使用场景)
5. [自动化工作流](#自动化工作流)
6. [故障排除](#故障排除)

---

## 架构概述

### 系统架构

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  WhatsApp/      │────▶│                 │────▶│                 │
│  Telegram/      │     │  OpenClaw       │     │  Amazon         │
│  Discord        │     │  Gateway        │     │  Crawler        │
│  (消息)         │     │  (18789端口)    │     │  (Python)       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Feishu         │
                       │  Bitable        │
                       │  (数据同步)     │
                       └─────────────────┘
```

### 数据流

```
用户消息 → OpenClaw Gateway → Skill 触发 → Python Crawler → CSV 输出 → Feishu 同步 → 结果返回
```

### 核心组件

| 组件 | 作用 | 技术栈 |
|------|------|--------|
| **OpenClaw Gateway** | 消息路由 & Agent 控制平面 | Node.js 22+ |
| **Skill 插件** | 封装爬虫操作为可调用技能 | SKILL.md + Bash |
| **Amazon Crawler** | 数据采集核心 | Python + Playwright |
| **Feishu Sync** | 数据同步到多维表格 | Python API |

---

## 前置准备

### 1. 安装 OpenClaw

```bash
# 使用 npm 安装
npm install -g openclaw@latest

# 或使用 Homebrew (macOS)
brew install openclaw

# 验证安装
openclaw --version
```

### 2. 配置 Gateway

```bash
# 初始化配置
openclaw onboard

# 或手动创建配置文件
cat > ~/.openclaw/openclaw.json << 'EOF'
{
  "gateway": {
    "port": 18789,
    "bind": "loopback"
  },
  "channels": {
    "telegram": { "enabled": true },
    "whatsapp": { "enabled": true }
  },
  "agents": {
    "defaults": {
      "model": "anthropic/claude-sonnet-4-6"
    }
  }
}
EOF
```

### 3. 登录消息频道

```bash
# Telegram
openclaw channels login --channel telegram

# WhatsApp (会显示 QR 码)
openclaw channels login --channel whatsapp

# Discord
openclaw channels login --channel discord
```

### 4. 启动 Gateway

```bash
# 前台运行
openclaw gateway

# 后台运行
openclaw gateway --daemon

# 检查状态
openclaw health
```

---

## 集成步骤

### 步骤 1: 创建 OpenClaw Skill

**Skill 文件位置**: `~/.openclaw/skills/amazon-crawler/SKILL.md`

```markdown
---
name: amazon-crawler
description: Amazon product crawler with Feishu Bitable integration. Run Best Sellers or keyword search crawlers, generate reports, and sync data to Feishu.
metadata: {
  "openclaw": {
    "emoji": "🛒",
    "requires": {
      "bins": ["uv", "python3"],
      "anyBins": ["python"]
    }
  }
}
---

# Amazon Crawler

## Overview

This skill controls the Amazon product crawler system. Run crawlers, generate reports, and sync data to Feishu Bitable.

## Quick Run

Run a quick crawl with default settings:

```
/amazon-crawler quick-run --mode bestsellers --pages 2 --products 20
```

## Search Mode

Search for specific products:

```
/amazon-crawler search --keyword "water bottle" --pages 2 --products 20
```

## Remote Execution

Run on a remote headless server:

```
/amazon-crawler remote --server user@host --pages 3 --products 30
```

## Feishu Sync

Sync latest data to Feishu Bitable:

```
/amazon-crawler sync-feishu --csv output/amazon_products.csv
```

## Full Pipeline

Crawl + Report + Sync in one command:

```
/amazon-crawler full-pipeline --mode bestsellers --pages 2 --feishu
```
```

### 步骤 2: 安装 Skill 到 OpenClaw

```bash
# 方法 1: 使用符号链接 (推荐)
ln -s /path/to/python_crawler ~/.openclaw/skills/amazon-crawler

# 方法 2: 复制 Skill 文件
mkdir -p ~/.openclaw/skills/amazon-crawler
cp /path/to/python_crawler/OPENCLAW_SKILL.md ~/.openclaw/skills/amazon-crawler/SKILL.md

# 方法 3: 使用 ClawHub (如果已发布)
clawhub install amazon-crawler
```

### 步骤 3: 验证 Skill 加载

```bash
# 检查 Skill 是否加载
openclaw skills list

# 查看详细技能信息
openclaw skills info --skill amazon-crawler

# 测试 Skill
openclaw agent --message "List available skills"
```

### 步骤 4: 创建执行脚本

**脚本位置**: `~/.openclaw/skills/amazon-crawler/run.sh`

```bash
#!/bin/bash
# OpenClaw Amazon Crawler Runner

set -e

# 配置
PROJECT_DIR="/run/media/clearzero22/fedora1/home/clearzero22/projects/01_my_script/python_crawler"
cd "$PROJECT_DIR"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 解析命令
COMMAND=$1
shift

case "$COMMAND" in
  quick-run)
    echo -e "${GREEN}🛒 Running Amazon Crawler...${NC}"
    ./run_automation.sh --pages 2 --products 20 --headless
    ;;

  search)
    KEYWORD=$1
    echo -e "${GREEN}🔍 Searching Amazon for: $KEYWORD${NC}"
    ./run_automation.sh --mode search --keyword "$KEYWORD" --pages 2 --products 20 --headless
    ;;

  remote)
    SERVER=$1
    echo -e "${GREEN}🌐 Running on remote server: $SERVER${NC}"
    ./run_automation.sh --pages 2 --products 20 --remote "$SERVER" --headless
    ;;

  sync-feishu)
    CSV_FILE=${1:-"output/amazon_products_latest.csv"}
    echo -e "${GREEN}📊 Syncing to Feishu Bitable...${NC}"
    uv run python src/feishu_sync.py "$CSV_FILE"
    ;;

  full-pipeline)
    echo -e "${GREEN}🚀 Running full pipeline...${NC}"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    OUTPUT="output/amazon_products_${TIMESTAMP}.csv"

    # Step 1: Crawl
    ./run_automation.sh --pages 2 --products 20 --output "$OUTPUT" --headless

    # Step 2: Report
    echo -e "${YELLOW}📈 Generating report...${NC}"
    uv run python crawler_report.py "$OUTPUT"

    # Step 3: Sync
    if [[ "$1" == "--feishu" ]]; then
      echo -e "${YELLOW}☁️ Syncing to Feishu...${NC}"
      uv run python src/feishu_sync.py "$OUTPUT"
    fi

    echo -e "${GREEN}✅ Pipeline complete!${NC}"
    ;;

  status)
    echo "=== Amazon Crawler Status ==="
    echo ""
    echo "Latest outputs:"
    ls -lh output/*.csv 2>/dev/null | tail -5 || echo "No CSV files found"
    echo ""
    echo "Feishu config:"
    if [[ -f "config/feishu_config.yaml" ]]; then
      echo "✓ Feishu configured"
    else
      echo "✗ Feishu not configured"
    fi
    ;;

  *)
    echo "Usage: $0 {quick-run|search|remote|sync-feishu|full-pipeline|status}"
    exit 1
    ;;
esac
```

```bash
# 设置执行权限
chmod +x ~/.openclaw/skills/amazon-crawler/run.sh
```

---

## 使用场景

### 场景 1: 通过 Telegram 快速爬取

```bash
# 1. 发送消息给 OpenClaw Bot
# "运行 Amazon 爬虫，爬取 Best Sellers，2 页"

# 2. OpenClaw 接收消息并触发 Skill
# 3. 爬虫执行完成后返回结果
```

**Telegram 示例对话**:
```
你: /amazon quick-run --pages 2 --products 20

OpenClaw: 🛒 启动 Amazon 爬虫...
✓ 爬取完成: 40 条商品
📊 价格范围: $5.99 - $89.99
⭐ 平均评分: 4.2
📄 报告已生成: output/amazon_products_20260312_report.md
```

### 场景 2: 定时任务 + 结果推送

```bash
# 创建 cron 任务
cat > ~/.openclaw/crons/daily-amazon-crawl.sh << 'EOF'
#!/bin/bash
# 每日 Amazon 爬取任务

# 1. 运行爬虫
cd /path/to/python_crawler
./run_automation.sh --pages 3 --products 30 --headless

# 2. 获取最新 CSV
LATEST_CSV=$(ls -t output/*.csv | head -1)

# 3. 生成报告
uv run python crawler_report.py "$LATEST_CSV"

# 4. 同步到飞书
uv run python src/feishu_sync.py "$LATEST_CSV"

# 5. 发送通知到 Telegram
openclaw message send \
  --channel telegram \
  --to @your_username \
  --message "✅ Amazon 爬取完成! $(wc -l < "$LATEST_CSV") 条商品已同步到飞书"
EOF

chmod +x ~/.openclaw/crons/daily-amazon-crawl.sh

# 添加到 crontab (每天凌晨 2 点运行)
(crontab -l 2>/dev/null; echo "0 2 * * * ~/.openclaw/crons/daily-amazon-crawl.sh") | crontab -
```

### 场景 3: 远程服务器执行

```bash
# 通过 OpenClaw 触发远程爬取
# Telegram: "在服务器 pi@192.168.1.100 上运行爬虫"

# OpenClaw 执行:
ssh pi@192.168.1.100 "cd /home/pi/python_crawler && ./run_automation.sh --pages 2 --products 20 --headless"

# 结果返回:
# "✅ 远程爬取完成! 已传输 40 条商品数据"
```

### 场景 4: 多平台数据同步

```bash
# 爬取 → 分析 → 飞书 → 通知
./run_automation.sh --pages 2 --products 20 --feishu

# 通过 OpenClaw 广播到多个频道
openclaw message send --channel whatsapp --to +15550101 --message "Amazon 数据已更新"
openclaw message send --channel telegram --to @channel --message "📊 飞书表格已更新"
```

---

## 自动化工作流

### 工作流 1: 智能爬取决策

```bash
#!/bin/bash
# ~/.openclaw/skills/amazon-crawler/smart-crawl.sh

# 检查上次爬取时间
LAST_CRAWL=$(stat -c %Y output/amazon_products_latest.csv 2>/dev/null || echo 0)
NOW=$(date +%s)
AGE=$((NOW - LAST_CRAWL))
HOURS_OLD=$((AGE / 3600))

# 如果数据超过 24 小时，自动爬取
if [[ $HOURS_OLD -gt 24 ]]; then
  echo "数据已过期 (${HOURS_OLD} 小时前)，开始爬取..."
  ./run_automation.sh --pages 2 --products 20 --headless --feishu
else
  echo "数据新鲜 (${HOURS_OLD} 小时前)，跳过爬取"
fi
```

### 工作流 2: 竞品监控

```bash
#!/bin/bash
# ~/.openclaw/skills/amazon-crawler/competitor-watch.sh

KEYWORDS=("water bottle" "blender" "coffee maker")

for keyword in "${KEYWORDS[@]}"; do
  echo "监控关键词: $keyword"

  # 爬取数据
  ./run_automation.sh \
    --mode search \
    --keyword "$keyword" \
    --pages 1 \
    --products 10 \
    --headless

  # 分析机会
  LATEST_CSV=$(ls -t output/*.csv | head -1)
  OPPORTUNITIES=$(uv run python -c "
import pandas as pd
import sys
df = pd.read_csv('$LATEST_CSV')
df['price_num'] = df['price'].str.extract(r'([\d,]+\.?\d*)').astype(float)
df['rating_num'] = df['rating'].str.extract(r'([\d.]+)').astype(float)
ops = df[(df['rating_num'] >= 4.5) & (df['price_num'] < 30)].head(3)
for _, row in ops.iterrows():
    print(f\"• {row['title'][:40]}... \${row['price_num']:.2f} {row['rating']}\")
" 2>/dev/null)

  if [[ -n "$OPPORTUNITIES" ]]; then
    openclaw message send \
      --channel telegram \
      --to @your_username \
      --message "🎯 发现机会产品 ($keyword):\n$OPPORTUNITIES"
  fi

  sleep 10  # 避免请求过快
done
```

### 工作流 3: 价格变化追踪

```bash
#!/bin/bash
# ~/.openclaw/skills/amazon-crawler/price-tracker.sh

# 比较两次爬取的数据
OLD_CSV="output/amazon_products_previous.csv"
NEW_CSV="output/amazon_products_latest.csv"

if [[ ! -f "$OLD_CSV" ]]; then
  cp "$NEW_CSV" "$OLD_CSV"
  exit 0
fi

# 检测价格下降
uv run python -c "
import pandas as pd

old = pd.read_csv('$OLD_CSV')
new = pd.read_csv('$NEW_CSV')

# 提取价格
old['price_num'] = old['price'].str.extract(r'([\d,]+\.?\d*)').astype(float)
new['price_num'] = new['price'].str.extract(r'([\d,]+\.?\d*)').astype(float)

# 合并数据
merged = old.merge(new, on='asin', suffixes=('_old', '_new'))
merged['price_change'] = merged['price_num_new'] - merged['price_num_old']

# 找出降价商品
deals = merged[merged['price_change'] < 0].sort_values('price_change')

for _, row in deals.head(5).iterrows():
    savings = abs(row['price_change'])
    print(f\"💰 {row['title'][:40]}... 降价 \${savings:.2f} (现价 \${row['price_num_new']:.2f})\")
" 2>/dev/null | while read -r deal; do
  openclaw message send \
    --channel telegram \
    --to @your_username \
    --message "$deal"
done

# 更新基准
cp "$NEW_CSV" "$OLD_CSV"
```

---

## 故障排除

### 问题 1: Skill 无法加载

**症状**: `openclaw skills list` 中看不到 amazon-crawler

**解决方案**:
```bash
# 1. 检查 Skill 文件是否存在
ls -la ~/.openclaw/skills/amazon-crawler/SKILL.md

# 2. 验证 YAML 格式
cat ~/.openclaw/skills/amazon-crawler/SKILL.md | head -10

# 3. 重启 Gateway
openclaw gateway restart

# 4. 检查日志
openclaw logs --tail 50
```

### 问题 2: 执行脚本无权限

**症状**: `Permission denied` 错误

**解决方案**:
```bash
chmod +x ~/.openclaw/skills/amazon-crawler/run.sh
chmod +x /path/to/python_crawler/run_automation.sh
```

### 问题 3: 远程执行失败

**症状**: SSH 连接或命令执行失败

**解决方案**:
```bash
# 1. 测试 SSH 连接
ssh user@server "echo 'Connection OK'"

# 2. 配置 SSH 密钥 (避免密码输入)
ssh-copy-id user@server

# 3. 检查远程环境
ssh user@server "cd /path/to/python_crawler && uv run python verify_deployment.py"
```

### 问题 4: 飞书同步失败

**症状**: `Feishu configuration incomplete` 错误

**解决方案**:
```bash
# 1. 检查配置文件
cat config/feishu_config.yaml

# 2. 或使用环境变量
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"
export FEISHU_BITABLE_APP_TOKEN="bascnxxx"
export FEISHU_TABLE_ID="tblxxx"

# 3. 测试连接
uv run python src/feishu_sync.py --test-connection
```

### 问题 5: 消息发送失败

**症状**: `openclaw message send` 失败

**解决方案**:
```bash
# 1. 检查 Gateway 状态
openclaw health

# 2. 检查频道状态
openclaw channels status

# 3. 重新登录频道
openclaw channels login --channel telegram

# 4. 测试消息
openclaw message send --to @your_username --message "Test message"
```

---

## 高级配置

### 配置 1: 多环境支持

```json
// ~/.openclaw/openclaw.json
{
  "skills": {
    "entries": {
      "amazon-crawler": {
        "enabled": true,
        "env": {
          "PROJECT_DIR": "/path/to/python_crawler",
          "REMOTE_SERVER": "user@server",
          "FEISHU_CONFIG": "config/feishu_config.yaml"
        },
        "config": {
          "defaultPages": 2,
          "defaultProducts": 20,
          "autoSyncFeishu": true
        }
      }
    }
  }
}
```

### 配置 2: 消息路由规则

```json
// ~/.openclaw/openclaw.json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "allowFrom": ["@your_username", "@trusted_contact"],
      "agent": "amazon-bot"
    },
    "whatsapp": {
      "enabled": true,
      "allowFrom":["+15550101"],
      "groups": {
        "*": { "requireMention": true }
      }
    }
  },
  "messages": {
    "groupChat": {
      "mentionPatterns": ["@amazon", "@crawler"]
    }
  }
}
```

### 配置 3: 定时任务集成

```bash
# OpenClaw Cron 集成
openclaw cron create \
  --schedule "0 2 * * *" \
  --command "~/.openclaw/skills/amazon-crawler/run.sh quick-run"

# 列出定时任务
openclaw cron list

# 手动触发
openclaw cron run --job-id <id>
```

---

## 相关文档

- [OpenClaw 官方文档](https://docs.openclaw.ai)
- [Amazon 爬虫项目 README](./README.md)
- [飞书集成指南](./AMAZON_TO_FEISHU_GUIDE.md)
- [OpenClaw Skill 使用指南](/home/clearzero22/.claude/skills/openclaw/OPENCLAW_GUIDE.md)

---

**创建时间**: 2026-03-12
**版本**: 1.0.0
