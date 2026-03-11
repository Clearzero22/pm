# Amazon 爬虫项目 - 开发时间线

记录项目从零到完成的开发过程。

## 2026-03-12

### ✅ 项目初始化

- [x] **01:41** - 创建项目目录 `python_crawler`
- [x] **01:42** - 使用 `uv init` 初始化项目
- [x] **01:42** - 安装核心依赖：`playwright`, `pandas`
- [x] **01:45** - 安装 Playwright Chromium 浏览器
- [x] **01:45** - 创建项目目录结构：`src/`, `output/`

### ✅ 核心架构设计

- [x] **01:45** - 设计模块化架构
  - `src/crawler.py` - 主爬虫逻辑
  - `src/parser.py` - 数据解析
  - `src/utils.py` - 工具函数
- [x] **01:46** - 实现 `write_to_csv()` - CSV 写入函数
- [x] **01:46** - 实现 `deduplicate()` - 去重函数
- [x] **01:46** - 实现基础爬虫类 `AmazonCrawler`
- [x] **01:46** - 实现 `parse_product_card()` - 商品卡片解析

### ✅ 第一版爬虫（列表页抓取）

- [x] **01:47** - 实现列表页商品卡片解析
  - 商品名称、价格、评分、评论数、图片链接
- [x] **01:47** - 实现多页翻页逻辑
- [x] **01:47** - 添加日志系统（logging 模块）
- [x] **01:47** - 创建 CLI 入口 `main.py` 支持命令行参数

### 🔧 调试与问题修复

- [x] **01:48** - 发现问题：`#zg-center-div` 选择器超时
- [x] **01:48** - 创建调试脚本 `debug_page.py`
  - 保存页面 HTML 为 `debug_page.html`
  - 保存截图 `debug_screenshot.png`
- [x] **01:48** - 分析页面结构，发现商品数据在 `data-a-carousel-options` JSON 中
- [x] **01:49** - 创建 `debug_selectors.py` 测试多种选择器
- [x] **01:49** - 更新解析器支持 JSON 数据提取
- [x] **01:49** - 修复：使用 `[data-asin]` 选择器成功定位商品

### ✅ 功能升级：深度提取

- [x] **01:53** - 设计新架构：点击进入详情页提取
- [x] **01:53** - 创建 `src/product_detail_parser.py`
  - `human_like_scroll()` - 人类行为模拟滚动
  - `extract_title()` - 标题提取
  - `extract_price()` - 价格提取
  - `extract_rating()` - 评分提取
  - `extract_description()` - 描述提取
  - `extract_images()` - 多图片提取
- [x] **01:53** - 重写 `src/crawler.py` 支持详情页导航
  - 点击商品链接
  - 等待详情页加载
  - 提取完整数据
  - 返回列表页继续下一个

### 🔧 图片提取问题修复

- [x] **01:54** - 创建 `debug_images.py` 调试图片选择器
- [x] **01:54** - 发现问题：Amazon 使用 `m.media-amazon.com` 而非 `images-amazon`
- [x] **01:54** - 修复图片提取逻辑
  - 主图：使用 `data-old-hires` 属性
  - 缩略图：转换为高清版本 `_AC_SL1500_.jpg`
- [x] **01:54** - 修复 `startswith` 参数错误（列表 → 元组）

### ✅ 测试验证

- [x] **01:55** - 首次完整测试成功
  - 抓取 2 个商品
  - 每个商品 8 张图片
  - 数据完整保存到 CSV
- [x] **01:56** - 验证 CSV 输出格式正确

### ✅ 项目收尾

- [x] **01:57** - 创建 `.gitignore` 排除调试文件
- [x] **01:57** - Git 提交：`82c0249` - feat: add Amazon Best Sellers crawler with Playwright
- [x] **01:58** - 创建 `README.md` 项目文档

---

## 功能完成清单

### 核心功能

- [x] 浏览器自动化（Playwright + Chromium）
- [x] Amazon Best Sellers 列表页解析
- [x] 商品详情页深度提取
- [x] 多图片提取与高清转换
- [x] 多页翻页支持
- [x] 数据去重（ASIN）
- [x] CSV 导出

### 人类行为模拟

- [x] 随机滚动距离（300-800px）
- [x] 随机暂停时间（0.5-2秒）
- [x] 滚动到页面底部检测
- [x] 滚动回顶部

### 数据提取字段

- [x] ASIN（商品ID）
- [x] 标题（title）
- [x] 价格（price）
- [x] 评分（rating）
- [x] 描述（description）
- [x] 图片 URLs（images）
- [x] 图片数量（image_count）
- [x] 商品链接（url）

### 工程化

- [x] CLI 参数支持（`--pages`, `--products`, `--headless`, `--log-level`）
- [x] 日志系统（DEBUG/INFO 级别）
- [x] 错误处理与重试
- [x] uv 包管理
- [x] .gitignore 配置
- [x] Git 版本控制
- [x] README 文档

### 调试工具

- [x] `debug_page.py` - 页面结构调试
- [x] `debug_selectors.py` - 选择器测试
- [x] `debug_images.py` - 图片提取调试

---

## 技术栈总结

| 类别 | 技术 | 用途 |
|------|------|------|
| 包管理 | uv | 依赖管理 |
| 浏览器自动化 | Playwright | 网页抓取 |
| 浏览器 | Chromium | 页面渲染 |
| 数据处理 | pandas | CSV 处理（备用） |
| 日志 | logging | 调试追踪 |

---

## 项目统计

```
文件数：     10 个核心文件
代码行数：   967+ 行
开发时间：   ~20 分钟
测试商品：   成功提取 2+ 个完整商品
图片提取：   每个商品 8+ 张高清图片
```

---

## 待优化事项（可选）

- [ ] 添加代理支持
- [ ] 添加验证码识别
- [ ] 支持多地区 Amazon（.cn, .uk, .de）
- [ ] 添加进度条显示
- [ ] 支持断点续传
- [ ] 添加数据验证
- [ ] 图片下载到本地


---

## 自动化选品功能

### Phase 1: 核心算法

- [ ] 创建 `src/selection/` 模块目录
- [ ] 实现配置文件 (`config.py`)
- [ ] 实现评分引擎 (`scorer.py`)
  - [ ] 多维度评分逻辑
  - [ ] 权重配置
  - [ ] 评分计算
- [ ] 实现风险评估器 (`risk_assessor.py`)
  - [ ] 积极信号检测
  - [ ] 风险信号检测
  - [ ] 风险等级判定
- [ ] 实现自动选品器 (`selector.py`)
  - [ ] 数据过滤
  - [ ] 综合排序
  - [ ] 报告生成

### Phase 2: 定时任务

- [ ] 实现调度器 (`scheduler.py`)
  - [ ] 定时爬取
  - [ ] 自动选品
  - [ ] 结果通知

### Phase 3: 仪表盘集成

- [ ] 添加智能选品 Tab
- [ ] 参数配置面板
- [ ] 结果可视化展示

### 相关文档

- [x] `AUTO_SELECTION_GUIDE.md` - 自动化选品实现指南

---

## 飞书多维表格集成

### Phase 1: API 封装

- [ ] 创建 `src/feishu/` 模块目录
- [ ] 创建配置文件结构 (`config/feishu_config.yaml`)
- [ ] 实现 API 客户端 (`client.py`)
  - [ ] 认证与 Token 管理
  - [ ] API 请求封装
  - [ ] 错误处理与重试
- [ ] 实现字段映射器 (`mapper.py`)
  - [ ] CSV 到飞书字段映射
  - [ ] 类型转换
- [ ] 实现多维表格同步器 (`bitable.py`)
  - [ ] 批量创建记录
  - [ ] 批量更新记录
  - [ ] Upsert 逻辑

### Phase 2: 集成

- [ ] 修改爬虫支持飞书同步
- [ ] 添加命令行参数 `--sync-feishu`
- [ ] 创建独立同步脚本 `sync_to_feishu.py`
- [ ] 集成到定时任务

### 飞书配置

- [ ] 创建飞书应用
- [ ] 配置多维表格权限
- [ ] 创建商品主表
- [ ] 创建选品推荐表
- [ ] 创建同步日志表

### 相关文档

- [x] `FEISHU_INTEGRATION_GUIDE.md` - 飞书多维表格集成指南

---

## 2026-03-12 (Continued)

### ✅ 数据可视化仪表盘

- [x] 创建 `dashboard/app.py` - Streamlit 数据分析仪表盘
  - 📊 价格分析：直方图、饼图
  - ⭐ 评分分析：箱线图、区间统计
  - 🎨 变体分析：分布、TOP榜单
  - 🎯 选品建议：高评分低价机会、风险提醒
  - 🖼️ 图片展示：商品图片画廊
  - 📋 数据表格：完整数据查看
- [x] 创建独立虚拟环境 `.venv-dashboard`（解决 pandas 版本冲突）
- [x] 创建 `run_dashboard.sh` 启动脚本
- [x] 修复多个 bug：缩进错误、图片URL分割、颜色序列等
- [x] Commit: `63c391b` - feat: add Streamlit data visualization dashboard

### ✅ 关键词搜索功能（方案B）

- [x] 创建 `src/search_crawler.py` - 独立搜索爬虫类
  - 支持关键词搜索（URL 编码）
  - 5种排序方式：relevance, price-asc, price-desc, review-rank, date-desc
  - 可选类别过滤
  - 自动生成输出文件名
- [x] 更新 `main.py` 添加搜索模式 CLI 参数
  - `--search KEYWORD` - 启用搜索模式
  - `--sort` - 排序方式
  - `--category` - 类别过滤
- [x] 创建 `test_search.py` 测试脚本
- [x] 修复搜索爬虫导航逻辑
  - 问题：点击搜索结果链接失败（选择器不匹配）
  - 解决：改为直接构造商品URL导航 `https://www.amazon.com/dp/{ASIN}`
- [x] 修复依赖冲突（移除 dev 依赖组中的 streamlit）
- [x] 测试验证：成功搜索 "water bottle" 提取 3 个商品
- [x] Commit: `f2e158a` - feat: add Amazon keyword search crawler (Plan B)
- [x] Commit: `09eda7b` - fix: improve search crawler with direct navigation method

### 新增 CLI 使用示例

```bash
# 基础搜索
uv run python main.py --search "water bottle"

# 按评分排序
uv run python main.py --search "blender" --sort review-rank

# 按价格从低到高
uv run python main.py --search "coffee maker" --sort price-asc

# 组合参数
uv run python main.py --search "mouse" --category electronics --pages 2 --products 15
```
