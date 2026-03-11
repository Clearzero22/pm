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
