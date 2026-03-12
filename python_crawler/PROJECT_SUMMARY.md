# Amazon Crawler 项目开发总结

> **项目周期**: 2026-03-12 至今
> **仓库**: https://github.com/Clearzero22/amazon-crawler-feishu (私有)
> **当前版本**: v1.0.0

---

## 📋 目录

1. [项目概述](#项目概述)
2. [开发时间线](#开发时间线)
3. [核心功能](#核心功能)
4. [技术架构](#技术架构)
5. [文档体系](#文档体系)
6. [集成方案](#集成方案)
7. [未来优化](#未来优化)

---

## 项目概述

### 项目愿景

构建一个**全栈式 Amazon 商品数据采集平台**，实现：

- **智能采集**: Playwright 驱动的浏览器自动化爬虫
- **数据可视化**: Streamlit 实时数据仪表板
- **云端同步**: 飞书多维表格 API 集成
- **远程控制**: OpenClaw 消息网关集成
- **自动化**: Claude Code Skill + Cron 定时任务

### 核心价值

| 维度 | 实现方案 |
|------|----------|
| **性能** | 多进程并行爬取，4x 性能提升 |
| **可靠性** | 无头部署、断点续传、错误重试 |
| **可扩展性** | 模块化设计，支持多种爬取模式 |
| **可维护性** | 完整文档体系、自动化测试 |

---

## 开发时间线

### Phase 1: 基础爬虫 (Commit #1-5)

**时间**: 2026-03-12 早期

```
60931ad → 86c6a94 → 4ed1555 → 10f1c6e → 82c0249
   ↓          ↓          ↓          ↓          ↓
初始化     文档      颜色修复    Ghostty    Best Sellers
PM项目      完善      输出       配置       爬虫实现
```

**核心交付**:
- ✅ Playwright 浏览器自动化
- ✅ Amazon Best Sellers 页面爬取
- ✅ 商品数据解析和 CSV 导出
- ✅ 响应式窗口适配

### Phase 2: 功能扩展 (Commit #6-11)

**时间**: 2026-03-12 中期

```
c3a1e01 → 6b1b11e → 63c391b → f2e158a → 09eda7b → 5603398
   ↓          ↓          ↓          ↓          ↓          ↓
项目文档    变体提取   Dashboard   搜索爬虫    修复优化    TODO更新
```

**核心交付**:
- ✅ 商品变体 (variants) 提取
- ✅ Streamlit 数据可视化仪表板
- ✅ Amazon 关键词搜索爬虫 (独立类实现)
- ✅ 直接导航方法优化

### Phase 3: 性能优化 (Commit #12-17)

**时间**: 2026-03-12 中后期

```
79b5837 → ceb34e5 → 30c71ca → 6ba955d → a961b0c → e5cd1c6
   ↓          ↓          ↓          ↓          ↓          ↓
并行测试    多进程爬虫  大规模测试   4x性能     无头模式    部署指南
```

**核心交付**:
- ✅ Playwright 并行标签页测试套件
- ✅ 真正的多进程 + 多窗口并行爬虫
- ✅ 25 任务同时执行的大规模测试
- ✅ 4x 性能优化的并行爬虫
- ✅ 服务器端无头部署支持
- ✅ 跨平台部署脚本 (Linux/macOS/Raspberry Pi)

### Phase 4: 自动化与集成 (Commit #18-24)

**时间**: 2026-03-12 后期

```
6029509 → 00ecf85 → 91f452d → b1137dd → 895d22b → 1fbbf2b
   ↓          ↓          ↓          ↓          ↓          ↓
验证脚本    Claude    飞书集成    API实现    文档完善    OpenClaw
           Code Skill           实际调用              集成指南
```

**核心交付**:
- ✅ 部署验证脚本修复
- ✅ Claude Code Skill 自动化集成
- ✅ 飞书多维表格数据同步
- ✅ 飞书 API 实际调用实现
- ✅ 完整项目文档体系
- ✅ OpenClaw 消息网关集成

---

## 核心功能

### 1. Amazon Best Sellers 爬虫

**文件**: `src/crawler.py`

**功能**:
- 自动翻页爬取 Best Sellers 商品
- 商品标题、价格、评分、评论数提取
- 商品变体 (颜色/尺寸) 识别
- 图片链接保存
- CSV 导出

**使用方式**:
```bash
./run_automation.sh --pages 2 --products 20
```

### 2. Amazon 搜索爬虫

**文件**: `src/search_crawler.py`

**功能**:
- 关键词搜索商品
- 直接导航到搜索结果页
- 搜索结果商品提取
- 支持任意关键词

**使用方式**:
```bash
./run_automation.sh --mode search --keyword "water bottle"
```

### 3. 并行爬虫

**文件**: `optimized_parallel_crawler.py`

**性能指标**:
- **4x 性能提升**: 25 任务并行执行
- **多进程 + 多窗口**: 充分利用系统资源
- **智能限流**: 避免被封禁

**使用方式**:
```bash
./run_automation.sh --parallel --tasks 25
```

### 4. Streamlit 仪表板

**文件**: `dashboard/app.py`

**功能**:
- 实时数据可视化
- 价格分布、评分统计
- 商品图片预览
- 数据导出功能

**使用方式**:
```bash
./run_dashboard.sh
```

### 5. 飞书数据同步

**文件**: `src/feishu_sync.py`

**功能**:
- API 认证 (tenant_access_token)
- 批量记录创建 (50 条/批次)
- 速率限制处理 (0.05s 延迟)
- 错误重试机制

**使用方式**:
```bash
./run_automation.sh --feishu
```

### 6. OpenClaw 集成

**文件**: `~/.openclaw/skills/amazon-crawler/SKILL.md`

**功能**:
- Telegram/WhatsApp/Discord 消息触发
- 远程爬虫执行
- 结果推送通知
- 定时任务支持

**使用方式**:
```bash
# Telegram
/amazon quick-run --pages 2

# WhatsApp
/amazon full-pipeline --feishu
```

---

## 技术架构

### 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| **爬虫引擎** | Playwright | 浏览器自动化 |
| **数据处理** | Pandas | CSV 数据处理 |
| **可视化** | Streamlit | Web 仪表板 |
| **云同步** | Feishu Bitable API | 数据存储 |
| **消息网关** | OpenClaw | 远程控制 |
| **包管理** | uv | Python 依赖管理 |
| **脚本** | Bash | 自动化脚本 |

### 项目结构

```
python_crawler/
├── src/                    # 核心源码
│   ├── crawler.py         # Best Sellers 爬虫
│   ├── search_crawler.py  # 搜索爬虫
│   ├── parser.py          # HTML 解析器
│   ├── product_detail_parser.py  # 商品详情解析
│   ├── feishu_sync.py     # 飞书同步
│   └── utils.py           # 工具函数
├── dashboard/              # Streamlit 仪表板
│   └── app.py             # 仪表板主程序
├── config/                 # 配置文件
│   └── feishu_config.template.yaml
├── output/                 # 数据输出
│   └── *.csv              # 爬取结果
├── *.sh                   # 部署脚本
│   ├── run_automation.sh  # 自动化脚本
│   ├── run_dashboard.sh   # 仪表板启动
│   ├── deploy_*.sh        # 跨平台部署
│   └── run_server.sh      # 服务器模式
├── *.py                   # 工具脚本
│   ├── main.py            # 主入口
│   ├── crawler_report.py  # 报告生成
│   ├── server_runner.py   # 服务器运行器
│   └── test_*.py          # 测试套件
└── docs/                   # 文档 (当前目录)
    ├── *.md               # 各类指南
    └── README.md          # 项目说明
```

### 数据流

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Amazon     │────▶│  Parser     │────▶│  Pandas     │
│  (Playwright│     │  (BeautifulSoup│    │  DataFrame  │
│   Browser)  │     │   /Regex)   │     │             │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                                 │
                        ┌────────────────────────┘
                        │
            ┌───────────▼───────────┐
            │                       │
    ┌───────▼──────┐      ┌────────▼────────┐
    │   CSV Export │      │  Streamlit      │
    │  (本地存储)   │      │  Dashboard      │
    └───────┬──────┘      └─────────────────┘
            │
    ┌───────▼───────────┐
    │                   │
┌───▼────┐      ┌──────▼────────┐
│ Feishu │      │  OpenClaw     │
│ Bitable│      │  Notification │
│  API   │      │  (Telegram/   │
└────────┘      │   WhatsApp)   │
                └───────────────┘
```

---

## 文档体系

### 用户文档

| 文档 | 内容 | 受众 |
|------|------|------|
| **README.md** | 项目介绍、快速开始 | 所有用户 |
| **AUTOMATION_GUIDE.md** | 自动化脚本使用 | 运维人员 |
| **HEADLESS_DEPLOYMENT_GUIDE.md** | 无头部署指南 | 运维人员 |
| **AMAZON_TO_FEISHU_GUIDE.md** | 飞书集成指南 | 数据分析师 |
| **OPENCLAW_INTEGRATION_GUIDE.md** | OpenClaw 集成 | 开发者 |

### 技术文档

| 文档 | 内容 | 受众 |
|------|------|------|
| **AI_AGENT_INTEGRATION.md** | AI Agent 集成方案 | 架构师 |
| **FEISHU_BITABLE_INTEGRATION.md** | 飞书 API 详情 | 开发者 |
| **FULL_WORKFLOW_GUIDE.md** | 完整工作流 | 产品经理 |
| **COMPETITIVE_ANALYSIS.md** | 竞品分析 | 决策者 |

### 专项文档

| 文档 | 内容 |
|------|------|
| **AMAZON_LOGIN_AUTOMATION.md** | 登录自动化方案 |
| **AMAZON_LOGIN_PERSISTENCE.md** | 登录状态持久化 |
| **AMAZON_BROWSER_LOGIN.md** | 浏览器登录流程 |
| **DATA_REQUIREMENTS.md** | 数据需求规范 |
| **SECURITY_AND_PRIVACY.md** | 安全与隐私 |

---

## 集成方案

### Claude Code Skill 集成

**配置**: `~/.claude/skills/`

**功能**:
- 自然语言触发爬虫
- 自动参数解析
- 结果可视化

**示例**:
```
"运行 Amazon 爬虫，爬取 Best Sellers，2 页，20 个商品"
```

### OpenClaw 消息集成

**配置**: `~/.openclaw/skills/amazon-crawler/`

**支持频道**:
- Telegram: `/amazon quick-run --pages 2`
- WhatsApp: `/amazon search --keyword "water bottle"`
- Discord: `/amazon full-pipeline --feishu`

### 飞书多维表格集成

**配置**: `config/feishu_config.yaml`

**数据映射**:
| CSV 字段 | 飞书字段 | 类型 |
|----------|----------|------|
| asin | ASIN | 文本 |
| title | 商品标题 | 文本 |
| price | 价格 | 数字 |
| rating | 评分 | 数字 |
| url | 商品链接 | URL |

---

## 未来优化

### 短期优化 (1-2 周)

#### 1. 性能优化

**现状**:
- 单机并行爬取，25 任务上限
- 速率限制依赖人工调节

**优化方案**:
- ✨ **动态速率限制**: 根据响应时间自动调节
- ✨ **智能重试**: 指数退避 + 错误分类
- ✨ **缓存层**: Redis 缓存已爬取商品

```python
# 智能速率限制示例
class AdaptiveRateLimiter:
    def adjust_delay(self, response_time: float):
        if response_time > 5:
            self.delay *= 1.5  # 响应慢，增加延迟
        elif response_time < 1:
            self.delay *= 0.8  # 响应快，减少延迟
```

#### 2. 数据质量

**现状**:
- 部分字段解析失败时留空
- 无数据验证机制

**优化方案**:
- ✨ **数据验证**: Pydantic 模型验证
- ✨ **智能填充**: 基于历史数据推断
- ✨ **异常检测**: 标记异常价格/评分

```python
# Pydantic 数据模型
from pydantic import BaseModel, validator

class AmazonProduct(BaseModel):
    asin: str
    title: str
    price: float

    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
```

#### 3. 监控告警

**现状**:
- 无实时监控
- 错误仅日志记录

**优化方案**:
- ✨ **Prometheus 指标**: 爬取速率、成功率
- ✨ **Grafana 仪表板**: 实时监控
- ✨ **告警规则**: 失败率 > 10% 触发告警

### 中期优化 (1-2 月)

#### 1. 分布式爬虫

**现状**:
- 单机运行，扩展性有限

**优化方案**:
- ✨ **任务队列**: Celery + Redis
- ✨ **Worker 集群**: 多台机器并行爬取
- ✨ **负载均衡**: 自动分配任务

```python
# Celery 任务定义
from celery import Celery

app = Celery('amazon_crawler', broker='redis://localhost:6379')

@app.task
def crawl_best_sellers(page: int):
    crawler = AmazonCrawler()
    return crawler.crawl(page)
```

#### 2. 反反爬

**现状**:
- 固定 User-Agent
- 无代理轮换

**优化方案**:
- ✨ **User-Agent 池**: 随机轮换
- ✨ **代理池**: 多地区 IP 轮换
- ✨ **指纹识别**: 浏览器指纹随机化

#### 3. 数据分析

**现状**:
- 原始数据导出
- 无分析能力

**优化方案**:
- ✨ **价格趋势**: 历史价格追踪
- ✨ **竞品分析**: 同类商品对比
- ✨ **机会识别**: 高评分低价商品推荐

### 长期优化 (3-6 月)

#### 1. AI 增强

**优化方案**:
- ✨ **智能分类**: AI 自动分类商品
- ✨ **评论分析**: 情感分析、关键词提取
- ✨ **图像识别**: 商品图片分析

```python
# AI 评论分析示例
from transformers import pipeline

sentiment = pipeline("sentiment-analysis")

def analyze_reviews(reviews: List[str]):
    results = sentiment(reviews)
    positive = sum(1 for r in results if r['label'] == 'POSITIVE')
    return positive / len(results)
```

#### 2. 平台扩展

**现状**:
- 仅支持 Amazon

**优化方案**:
- ✨ **多平台支持**: eBay、AliExpress、Temu
- ✨ **统一接口**: 抽象爬虫基类
- ✨ **配置驱动**: YAML 配置爬取规则

#### 3. SaaS 化

**优化方案**:
- ✨ **Web UI**: Django/FastAPI 后端
- ✨ **用户系统**: 多用户隔离
- ✨ **订阅模式**: 按使用量计费

---

## 技术债务

### 需要清理

| 问题 | 影响 | 优先级 |
|------|------|--------|
| 硬编码配置 | 维护困难 | 高 |
| 缺少单元测试 | 回归风险 | 高 |
| 文档冗余 | 查找困难 | 中 |
| 旧分支残留 | 混淆 | 低 |

### 建议清理方案

```bash
# 1. 删除旧分支
git branch -D python_crawler_branch

# 2. 添加单元测试
# pytest tests/

# 3. 整合重复文档
# 创建 docs/index.md 作为索引

# 4. 配置外部化
# 创建 config/settings.yaml
```

---

## 总结

### 项目成果

| 指标 | 数值 |
|------|------|
| **Git 提交** | 24 条 |
| **Python 文件** | 10+ 个 |
| **文档文件** | 25+ 个 |
| **集成方案** | 3 个 (Claude/OpenClaw/Feishu) |
| **代码行数** | 3000+ 行 |

### 核心竞争力

1. **全栈集成**: 从爬取到可视化的完整链路
2. **多端控制**: 本地/远程/消息三种方式
3. **云端同步**: 飞书多维表格实时同步
4. **完整文档**: 25+ 篇技术文档

### 后续建议

1. **优先性能优化**: 动态限流 + 缓存层
2. **添加监控**: Prometheus + Grafana
3. **完善测试**: 单元测试 + 集成测试
4. **清理技术债务**: 删除旧分支、整合文档

---

**创建时间**: 2026-03-12
**文档版本**: 1.0.0
**作者**: Clearzero22
**许可**: MIT License
