# Amazon Crawler Automation Guide

自动化运行 Amazon 爬虫项目并生成数据报告。

## 功能概述

| 功能 | 说明 |
|------|------|
| **自动化爬取** | 一键运行 Best Sellers 或搜索模式爬虫 |
| **数据报告** | 自动生成 Markdown + JSON 统计报告 |
| **远程执行** | 支持 SSH 远程服务器部署 |
| **灵活配置** | 自定义页数、产品数、输出路径 |
| **Skill 集成** | Claude Code skill 支持 |

## 快速开始

### 1. 本地运行（推荐）

```bash
# Best Sellers 模式 - 默认配置
./run_automation.sh

# 自定义配置
./run_automation.sh --pages 2 --products 20

# 搜索模式
./run_automation.sh --mode search --keyword "water bottle" --pages 2 --products 20
```

### 2. 远程服务器运行

```bash
# 在远程服务器上运行
./run_automation.sh --mode search --keyword "blender" --remote user@server.com

# 查看远程服务器上的文件
./run_automation.sh --mode bestsellers --remote pi@192.168.1.100 --pages 3 --products 30
```

### 3. 使用 Claude Code Skill

```bash
# 启动 Claude Code 后
/amazon-crawler quick-run --mode bestsellers --pages 2 --products 20

# 或使用 Skill 工具调用
```

## 命令行参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--mode` | `-m` | 模式：`bestsellers` 或 `search` | `bestsellers` |
| `--keyword` | `-k` | 搜索关键词（search 模式必需） | - |
| `--pages` | `-p` | 爬取页数 | `2` |
| `--products` | `-n` | 每页产品数 | `20` |
| `--output` | `-o` | 输出 CSV 文件路径 | `output/amazon_products_YYYYMMDD_HHMMSS.csv` |
| `--no-headless` | - | 显示浏览器窗口 | headless |
| `--no-report` | - | 跳过报告生成 | 生成报告 |
| `--remote` | `-r` | 远程服务器 (user@host) | 本地 |
| `--help` | `-h` | 显示帮助信息 | - |

## 使用示例

### 场景 1: 监控竞品价格

```bash
# 搜索特定关键词，按价格排序
uv run python main.py --search "wireless earbuds" --sort price-asc --pages 3 --products 30

# 自动化脚本
./run_automation.sh --mode search --keyword "wireless earbuds" --pages 3 --products 30
```

### 场景 2: 发现高评分低价机会

```bash
# 搜索并按评分排序
./run_automation.sh --mode search --keyword "kitchen scale" --sort review-rank --pages 2

# 查看报告中的 Top Opportunities
cat output/*_report.md
```

### 场景 3: 定时任务 (Cron)

```bash
# 编辑 crontab
crontab -e

# 每天凌晨 2 点运行
0 2 * * * cd /path/to/python_crawler && ./run_automation.sh --pages 2 --products 20 >> logs/cron.log 2>&1
```

### 场景 4: 远程服务器部署

```bash
# 1. 确保 SSH 访问
ssh user@server "cd /path/to/python_crawler && uv run python verify_deployment.py"

# 2. 运行远程爬取
./run_automation.sh --mode bestsellers --remote user@server --pages 2 --products 20

# 3. 结果会自动传输回本地
```

## 数据报告说明

### 报告内容

运行后会生成两种格式的报告：

| 文件 | 格式 | 内容 |
|------|------|------|
| `{csv_name}_report.md` | Markdown | 完整分析报告 |
| `{csv_name}_report.json` | JSON | 原始统计数据 |

### 报告章节

1. **Executive Summary** - 总览统计
   - 产品总数
   - 价格范围、平均值
   - 评分分布

2. **Price Distribution** - 价格分布
   - 各价位段产品数量
   - 四分位数统计

3. **Rating Distribution** - 评分分布
   - 各评分区间产品数
   - 高评分产品统计

4. **Top Opportunities** - 选品机会
   - 高评分低价产品列表
   - 可直接点击的产品链接

5. **Top Rated Products** - 热门产品
   - 评分最高的产品排名

6. **Data Quality** - 数据质量
   - 缺失值检查
   - 数据完整性报告

### 单独生成报告

如果已有 CSV 文件，可以单独生成报告：

```bash
# 基础报告
uv run python crawler_report.py output/amazon_products.csv

# 指定输出文件名
uv run python crawler_report.py output/amazon_products.csv --output my_report.md

# 输出 JSON 到终端
uv run python crawler_report.py output/amazon_products.csv --json
```

## 远程部署指南

### 前置条件

远程服务器需要满足：

```bash
# Python 3.14+
python3 --version

# uv 包管理器
uv --version

# Playwright 浏览器
uv run playwright install chromium
```

### 快速部署

```bash
# 1. 复制项目到服务器
rsync -av --exclude='.venv' --exclude='__pycache__' \
    python_crawler/ user@server:/path/to/python_crawler/

# 2. SSH 登录并安装依赖
ssh user@server
cd /path/to/python_crawler
uv sync
uv run playwright install chromium

# 3. 验证部署
uv run python verify_deployment.py

# 4. 测试运行
uv run python main.py --headless --pages 1 --products 5
```

### 自动化部署脚本

使用项目提供的部署脚本：

```bash
# Raspberry Pi
./deploy_raspberry_pi.sh

# Linux (Ubuntu/Debian/CentOS)
./deploy_linux.sh

# macOS
./deploy_mac.sh
```

## 项目结构

```
python_crawler/
├── run_automation.sh              # 自动化脚本
├── crawler_report.py              # 报告生成器
├── main.py                        # 爬虫入口
├── src/
│   ├── crawler.py                 # Best Sellers 爬虫
│   ├── search_crawler.py          # 搜索爬虫
│   └── utils.py                   # 工具函数
├── output/                        # 输出目录
│   ├── amazon_products.csv        # CSV 数据
│   ├── amazon_products_report.md  # Markdown 报告
│   └── amazon_products_report.json # JSON 统计
└── .claude/
    └── skills/
        └── amazon-crawler/
            └── skill.md           # Claude Code Skill
```

## Claude Code Skill 使用

### Skill 位置

```
~/.claude/skills/amazon-crawler/skill.md
```

### 使用方式

在 Claude Code 中：

```
# 直接运行爬虫
/amazon-crawler quick-run

# 指定参数
/amazon-crawler remote-run --mode search --keyword "coffee maker"

# 生成报告
/amazon-crawler generate-report --csv output/amazon_products.csv
```

### Skill 功能

| 功能 | 说明 |
|------|------|
| **Quick Run** | 本地快速运行 |
| **Remote Run** | 远程服务器执行 |
| **Generate Report** | 生成数据报告 |
| **Parse CSV** | 解析 CSV 数据 |

## 故障排除

### 问题 1: FileNotFoundError

```
Error: No such file or directory: 'output/output/file.csv'
```

**解决方案**: 确保 `src/utils.py` 中的 `write_to_csv` 函数已更新为自动创建目录。

### 问题 2: 远程执行失败

```
Error: ssh: Could not resolve hostname
```

**解决方案**:
- 检查 SSH 连接: `ssh user@host`
- 确认远程服务器上项目路径正确
- 验证远程服务器环境: `uv run python verify_deployment.py`

### 问题 3: 报告生成失败

```
Error: No valid price data
```

**解决方案**:
- 检查 CSV 文件是否包含有效数据
- 确保 CSV 有 `price` 和 `rating` 列
- 使用 `--log-level DEBUG` 调试爬虫

## 最佳实践

1. **从少量数据开始**: 先用 1 页、5 个产品测试
2. **使用 headless 模式**: 服务器上必须启用
3. **定期备份数据**: 保存历史 CSV 用于趋势分析
4. **合理安排频率**: 避免频繁请求导致 IP 被封
5. **监控日志**: 使用 `--log-level DEBUG` 调试问题

## 常见问题

**Q: 如何让爬虫每天自动运行？**

A: 使用 cron (Linux/Mac) 或 Task Scheduler (Windows):

```bash
# crontab -e
0 2 * * * cd /path/to/python_crawler && ./run_automation.sh --pages 2 --products 20
```

**Q: 远程运行时结果会传回来吗？**

A: 是的，脚本会自动尝试将 CSV 文件传输回本地。

**Q: 报告可以自定义吗？**

A: 可以修改 `crawler_report.py` 中的 `CrawlerReport` 类来自定义报告格式和内容。

**Q: 如何在 Docker 中运行？**

A: 参考 `HEADLESS_DEPLOYMENT_GUIDE.md` 中的 Docker 部署章节。

## 相关文档

- [README.md](README.md) - 项目主文档
- [HEADLESS_DEPLOYMENT_GUIDE.md](HEADLESS_DEPLOYMENT_GUIDE.md) - 无头部署指南
- [dashboard/README.md](dashboard/README.md) - 数据可视化仪表盘

---

**创建时间**: 2026-03-12
**作者**: Claude Code
**许可**: MIT
