# Amazon Crawler

基于 Playwright 的亚马逊商品爬虫，支持 **Best Sellers 榜单** 和 **关键词搜索** 两种模式。

## 功能特性

### 核心功能

| 功能 | 描述 |
|------|------|
| **双模式爬取** | Best Sellers 榜单 + 关键词搜索 |
| **深度提取** | 点击进入商品详情页，获取完整信息 |
| **人类行为模拟** | 随机滚动、随机暂停，模拟真实用户浏览 |
| **多页支持** | 自动翻页抓取，智能去重 |
| **多图片提取** | 自动提取商品高清图片（最多10张） |
| **搜索排序** | 支持按价格、评分、发布时间排序 |
| **详细日志** | DEBUG/INFO 级别可调，实时追踪抓取进度 |

### 提取的数据字段

| 字段 | 说明 | 示例 |
|------|------|------|
| `asin` | 亚马逊商品ID | `B0BZYCJK89` |
| `title` | 商品标题 | `Owala FreeSip Insulated Stainless Steel Water Bottle...` |
| `price` | 价格 | `$29.99` |
| `rating` | 评分 | `4.7 out of 5 stars` |
| `description` | 商品描述 | `24-ounce insulated stainless-steel water bottle...` |
| `image_count` | 图片数量 | `8` |
| `images` | 图片URL列表（用 ` | ` 分隔） | `https://m.media-amazon.com/images/I/...` |
| `url` | 商品详情页链接 | `https://www.amazon.com/dp/B0BZYCJK89` |

## 快速开始

### 环境要求

- Python >= 3.14
- uv (Python 包管理器)

### 安装

```bash
# 安装依赖
uv sync

# 安装 Playwright 浏览器
uv run playwright install chromium
```

### 基本使用

#### 模式 1: Best Sellers 榜单（默认）

```bash
# 默认配置：1页，5个商品
uv run python main.py

# 自定义配置
uv run python main.py --pages 2 --products 10

# 无头模式（后台运行）
uv run python main.py --headless
```

#### 模式 2: 关键词搜索

```bash
# 基础搜索
uv run python main.py --search "water bottle"

# 按评分排序（找高评分商品）
uv run python main.py --search "blender" --sort review-rank

# 按价格从低到高排序
uv run python main.py --search "coffee maker" --sort price-asc

# 指定类别搜索
uv run python main.py --search "headphones" --category electronics

# 组合参数
uv run python main.py --search "mouse" --pages 2 --products 10 --sort price-desc --headless
```

#### 完整参数示例

```bash
# Best Sellers 模式
uv run python main.py \
  --log-level DEBUG \
  --pages 3 \
  --products 20 \
  --headless \
  --output best_sellers.csv

# 搜索模式
uv run python main.py \
  --search "wireless earbuds" \
  --sort review-rank \
  --category electronics \
  --pages 2 \
  --products 15 \
  --headless \
  --output search_results.csv
```

## 命令行参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| **通用参数** ||||
| `--log-level` | INFO/DEBUG/WARNING/ERROR | INFO | 日志级别 |
| `--pages` | 数字 | 1 | 抓取多少页 |
| `--products` | 数字 | 5 | 每页提取多少个商品 |
| `--headless` | flag | False | 是否显示浏览器窗口 |
| `--output` | 文件名 | amazon_products.csv | 输出 CSV 文件名 |
| **搜索模式参数** ||||
| `--search` | 字符串 | - | 搜索关键词（启用搜索模式） |
| `--sort` | relevance/price-asc/price-desc/review-rank/date-desc | relevance | 搜索结果排序方式 |
| `--category` | 字符串 | - | Amazon 类别过滤（如 kitchen, electronics） |

## 项目结构

```
python_crawler/
├── main.py                          # CLI 入口（双模式支持）
├── test_search.py                   # 搜索功能测试脚本
├── src/
│   ├── __init__.py                  # 包初始化
│   ├── crawler.py                   # Best Sellers 爬虫
│   ├── search_crawler.py            # 关键词搜索爬虫 ⭐ NEW
│   ├── product_detail_parser.py     # 详情页解析
│   ├── parser.py                    # 列表页解析（备用）
│   └── utils.py                     # CSV 工具函数
├── output/                          # 输出目录
│   └── amazon_products.csv
├── pyproject.toml                   # uv 项目配置
└── .gitignore                       # Git 忽略规则
```

## 输出示例

```csv
asin,title,price,rating,description,image_count,images,url
B0BZYCJK89,"Owala FreeSip Insulated Stainless Steel Water Bottle...",29.99,"4.7 out of 5 stars","24-ounce insulated stainless-steel...",8,"https://m.media-amazon.com/images/I/61sS-XIvEXL._AC_SL1500_.jpg | ...",https://www.amazon.com/dp/B0BZYCJK89
```

## 技术架构

### 浏览器自动化 (Playwright)

```python
# 启动浏览器
browser = p.chromium.launch(headless=False)
page = browser.new_page()

# 导航到页面
page.goto(url, wait_until="domcontentloaded")

# 人类滚动模拟
for i in range(5):
    scroll_distance = random.randint(300, 800)
    page.evaluate(f"window.scrollBy(0, {scroll_distance})")
    page.wait_for_timeout(random.randint(500, 2000))
```

### 数据提取策略

```python
# 策略 1: 主图（data-old-hires 属性）
hires = main_img.get_attribute("data-old-hires")

# 策略 2: 缩略图转高清
if "_AC_US" in src:
    base = src.split("/I/")[1].split("._")[0]
    high_res = f"https://m.media-amazon.com/images/I/{base}._AC_SL1500_.jpg"

# 策略 3: 商品描述（Feature Bullets）
bullets = page.locator("#feature-bullets ul li").all()
```

### 反爬虫措施

| 措施 | 实现 |
|------|------|
| User-Agent | 模拟真实浏览器 |
| 随机延迟 | 每次操作 0.5-2 秒随机暂停 |
| 滚动模拟 | 随机滚动距离 300-800px |
| DOM 等待 | 等待元素完全加载 |

## 开发说明

### 添加新的数据字段

编辑 `src/product_detail_parser.py`：

```python
def extract_your_field(page) -> str:
    """提取自定义字段"""
    selector = "your-css-selector"
    el = page.locator(selector).first
    return el.text_content(timeout=2000) or "N/A"
```

### 调试技巧

```bash
# 启用 DEBUG 日志查看详细信息
uv run python main.py --log-level DEBUG

# 关闭无头模式，观察浏览器操作
uv run python main.py --pages 1 --products 1
```

## 常见问题

**Q: 为什么有些商品图片提取失败？**
A: Amazon 页面结构因地区而异，调试时可查看实际 HTML 结构调整选择器。

**Q: 如何加快抓取速度？**
A: 使用 `--headless` 模式，减少 `--products` 数量，或调整暂停时间。

**Q: 抓取会被封吗？**
A: 本爬虫已加入人类行为模拟，但仍建议控制抓取频率，避免大量并发请求。

---

## 使用场景示例

### 场景 1: 找高评分低价格商品（选品机会）

```bash
# 搜索水杯，按评分排序
uv run python main.py --search "water bottle" --sort review-rank --pages 2 --products 20

# 然后用仪表盘分析结果
bash run_dashboard.sh
# 在"选品建议"标签页查看高评分低价机会
```

### 场景 2: 价格竞争分析

```bash
# 搜索蓝牙耳机，按价格从低到高排序
uv run python main.py --search "bluetooth headphones" --sort price-asc --pages 3 --products 30
```

### 场景 3: 新品追踪

```bash
# 搜索新品，按发布时间排序
uv run python main.py --search "smart watch" --sort date-desc --pages 2
```

### 场景 4: 特定类别搜索

```bash
# 只在厨房类别搜索
uv run python main.py --search "air fryer" --category kitchen --sort review-rank
```

---

## 📊 数据可视化仪表盘

### 快速启动

```bash
# 使用启动脚本（推荐）
bash run_dashboard.sh

# 或手动启动
source .venv-dashboard/bin/activate
streamlit run dashboard/app.py
```

访问: http://localhost:8501

### 仪表盘功能

| 功能 | 描述 |
|------|------|
| 📊 **价格分析** | 价格分布直方图、价格区间饼图 |
| ⭐ **评分分析** | 评分箱线图、评分区间统计 |
| 🎨 **变体分析** | 变体分类分布、变体TOP榜单 |
| 🎯 **选品建议** | 高评分低价机会、风险商品提醒 |
| 🔍 **数据筛选** | 价格、评分、变体分类过滤 |
| 📋 **原始数据** | 完整数据表格查看 |

### 更新数据

```bash
# 1. 运行爬虫抓取新数据
uv run python main.py --pages 2 --products 20

# 2. 刷新仪表盘页面（浏览器按 R 键或 F5）
```

详细文档请查看: [dashboard/README.md](dashboard/README.md)

## License

MIT

## 作者

Created with Claude Code + Playwright
