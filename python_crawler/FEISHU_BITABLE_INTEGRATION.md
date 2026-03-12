# 飞书多维表格数据集成技术文档

> **将爬虫数据、电商迁移数据无缝集成到飞书多维表格，实现数据可视化、团队协作和自动化工作流**
>
> 本文档详细描述如何对接飞书开放平台 API，将采集和处理的电商商品数据同步到飞书多维表格（Bitable）中。

---

## 目录

1. [飞书多维表格概述](#1-飞书多维表格概述)
2. [技术架构设计](#2-技术架构设计)
3. [飞书开放平台 API](#3-飞书开放平台-api)
4. [数据模型映射](#4-数据模型映射)
5. [核心模块实现](#5-核心模块实现)
6. [数据同步策略](#6-数据同步策略)
7. [自动化工作流](#7-自动化工作流)
8. [完整代码实现](#8-完整代码实现)
9. [部署与配置](#9-部署与配置)

---

## 1. 飞书多维表格概述

### 1.1 什么是飞书多维表格

飞书多维表格（Bitable）是飞书推出的一款**低代码数据库工具**，兼具表格的易用性和数据库的强大功能。

**核心特性：**
- 📊 **多种字段类型** - 文本、数字、日期、人员、附件、关联记录等
- 🔗 **数据关联** - 支持表与表之间的关联引用
- 🤖 **自动化流程** - 支持触发器和自动化动作
- 📱 **多端同步** - PC、移动端实时同步
- 👥 **协作权限** - 细粒度的权限控制
- 🔌 **开放 API** - 完整的 RESTful API 支持

### 1.2 应用场景

| 场景 | 描述 | 适用表结构 |
|------|------|------------|
| **商品数据管理** | 存储采集的商品信息 | 商品主表 + 图片表 + 评价表 |
| **审核流程管理** | 跟踪 AI 优化和人工审核状态 | 审核记录表 + 操作日志表 |
| **任务调度监控** | 监控爬虫任务执行状态 | 任务队列表 + 执行日志表 |
| **数据看板** | 可视化展示业务数据 | 统计汇总表 + 图表视图 |

### 1.3 与传统 Excel/CSV 对比

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           数据存储方案对比                                    │
├──────────────────┬──────────────────┬──────────────────┬────────────────────┤
│       特性        │   CSV/Excel     │    本地数据库     │   飞书多维表格      │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ 数据共享         │ ❌ 文件传输      │ ❌ 局域网/同步    │ ✅ 云端实时共享     │
│ 协作编辑         │ ❌ 冲突风险      │ ❌ 不支持         │ ✅ 多人同时编辑     │
│ 权限控制         │ ❌ 无             │ ⚠️ 应用级         │ ✅ 字段/行级        │
│ API 访问         │ ❌ 需自行实现    │ ⚠️ 需开发接口     │ ✅ 原生 REST API   │
│ 移动端支持       │ ⚠️ 有限          │ ❌ 需开发         │ ✅ 原生 App        │
│ 自动化工作流     │ ❌ 无             │ ⚠️ 需开发         │ ✅ 内置自动化      │
│ 数据量限制       │ ⚠️ 文件大小限制  │ ✅ 大             │ ⚠️ 单表 50 万行     │
│ 离线访问         │ ✅ 支持          │ ✅ 支持           │ ❌ 需联网          │
└──────────────────┴──────────────────┴──────────────────┴────────────────────┘
```

---

## 2. 技术架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           数据集成架构                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        数据源层 (Data Sources)                       │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │  淘宝爬虫    │  │  1688 爬虫    │  │  亚马逊数据  │              │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │   │
│  └─────────┼─────────────────┼─────────────────┼───────────────────────┘   │
│            │                 │                 │                            │
│            ▼                 ▼                 ▼                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        数据处理层 (Processing)                       │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │  数据清洗    │  │  AI 优化引擎  │  │  格式转换    │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        同步服务层 (Sync Service)                     │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │                    FeishuBitableClient                      │   │   │
│  │  │  ┌────────────┐  ┌────────────┐  ┌────────────┐             │   │   │
│  │  │  │  批量写入  │  │  增量更新  │  │  数据查询  │             │   │   │
│  │  │  └────────────┘  └────────────┘  └────────────┘             │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        飞书多维表格 (Bitable)                        │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │  商品数据表  │  │  审核记录表  │  │  任务监控表  │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流向

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   爬虫采集   │────►│  本地存储   │────►│  同步服务   │────►│  飞书表格   │
│  (实时)     │     │  (JSON/DB)  │     │  (定时)     │     │  (云端)     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
  原始商品数据        临时缓存          API 批量写入        团队共享查看
  HTML 解析          数据清洗          增量同步          自动化工作流
```

### 2.3 同步模式

| 同步模式 | 触发方式 | 适用场景 | 优点 | 缺点 |
|----------|----------|----------|------|------|
| **实时同步** | 每条数据采完立即同步 | 重要数据、紧急任务 | 数据最新 | API 调用频繁 |
| **批量同步** | 达到阈值后批量同步 | 大批量采集任务 | 效率高、API 调用少 | 有延迟 |
| **定时同步** | 定时任务触发 | 定期更新数据 | 可预测、易管理 | 灵活性差 |
| **手动同步** | 用户手动触发 | 特殊场景 | 完全可控 | 需要人工介入 |

---

## 3. 飞书开放平台 API

### 3.1 API 认证机制

飞书开放平台使用 **OAuth 2.0** 和 **Tenant Access Token** 两种认证方式。

#### 3.1.1 自建应用认证流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   应用配置   │     │  获取 Token  │     │  API 请求   │     │  返回数据   │
│  App ID     │────►│  POST /auth │────►│  + Token    │────►│  JSON       │
│  App Secret │     │  tenant_access_token │  Header   │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

#### 3.1.2 Token 获取

```python
import requests
from typing import Optional


class FeishuAuth:
    """飞书认证模块"""
    
    API_BASE = "https://open.feishu.cn/open-apis"
    
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self._token: Optional[str] = None
        self._token_expire: int = 0
    
    def get_tenant_access_token(self) -> str:
        """获取 Tenant Access Token"""
        import time
        
        # Token 缓存（有效期 2 小时）
        if self._token and time.time() < self._token_expire:
            return self._token
        
        url = f"{self.API_BASE}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        response = requests.post(url, json=payload)
        data = response.json()
        
        if data.get("code") != 0:
            raise Exception(f"获取 Token 失败：{data}")
        
        self._token = data["tenant_access_token"]
        self._token_expire = time.time() + data["expire"] - 300  # 提前 5 分钟过期
        
        return self._token
```

### 3.2 多维表格核心 API

#### 3.2.1 API 概览

| API | 方法 | 端点 | 说明 |
|-----|------|------|------|
| **获取应用列表** | GET | `/open-apis/bitable/v1/apps` | 获取当前应用下的所有表格 |
| **获取数据表列表** | GET | `/open-apis/bitable/v1/apps/{app_token}/tables` | 获取指定应用的数据表 |
| **读取记录** | GET | `/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records` | 读取表中记录 |
| **创建记录** | POST | `/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records` | 创建新记录 |
| **批量创建记录** | POST | `/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch` | 批量创建（最多 500 条） |
| **更新记录** | PUT | `/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}` | 更新记录 |
| **删除记录** | DELETE | `/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}` | 删除记录 |
| **搜索记录** | POST | `/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/search` | 搜索记录 |

#### 3.2.2 字段类型映射

| 飞书字段类型 | Python 类型 | 说明 | 示例 |
|-------------|------------|------|------|
| `text` | `str` | 文本 | `"商品名称"` |
| `number` | `float/int` | 数字 | `99.99` |
| `single_select` | `str` | 单选 | `"已通过"` |
| `multi_select` | `List[str]` | 多选 | `["淘宝", "热销"]` |
| `date` | `str` | 日期 | `"2024-01-15"` |
| `datetime` | `int` | 时间戳（毫秒） | `1705305600000` |
| `checkbox` | `bool` | 复选框 | `True` |
| `url` | `str` | 链接 | `"https://..."` |
| `image` | `List[Dict]` | 图片 | `[{"url": "..."}]` |
| `attachment` | `List[Dict]` | 附件 | `[{"name": "file.pdf"}]` |
| `user` | `List[str]` | 人员（user_id） | `["ou_xxx"]` |
| `phone` | `str` | 手机号 | `"13800138000"` |
| `email` | `str` | 邮箱 | `"test@example.com"` |
| `currency` | `float` | 货币 | `99.99` |
| `formula` | 自动计算 | 公式 | 无需设置 |

---

## 4. 数据模型映射

### 4.1 电商商品数据表结构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           商品数据表 (products)                              │
├──────────────────┬──────────────────┬───────────────────────────────────────┤
│     字段名称      │     字段类型      │              说明                     │
├──────────────────┼──────────────────┼───────────────────────────────────────┤
│ 商品名称          │ text             │ 商品标题（必填）                      │
│ 商品 ID           │ text             │ 源平台商品 ID（唯一标识）             │
│ 源平台            │ single_select    │ 淘宝/1688/速卖通/亚马逊              │
│ 源链接            │ url              │ 原始商品页面链接                      │
│ 价格              │ currency         │ 商品售价                              │
│ 原价              │ currency         │ 划线价/原价                           │
│ 货币单位          │ single_select    │ CNY/USD/EUR/JPY                      │
│ 销量              │ number           │ 月销量/总销量                         │
│ 评分              │ number           │ 平均评分（0-5）                       │
│ 评价数量          │ number           │ 评价总数                              │
│ 品牌              │ text             │ 品牌名称                              │
│ 店铺名称          │ text             │ 卖家店铺名称                          │
│ 分类              │ text             │ 商品分类                              │
│ 主图              │ image            │ 商品主图                              │
│ 图片列表          │ attachment       │ 商品图片附件                          │
│ 商品描述          │ long_text        │ 详细描述                              │
│ 特点列表          │ long_text        │ 卖点/特点（JSON）                     │
│ 规格参数          │ long_text        │ 规格参数（JSON）                      │
│ 关键词            │ multi_select     │ SEO 关键词                             │
│ 采集时间          │ datetime         │ 数据抓取时间                          │
│ 更新时间          │ datetime         │ 最后更新时间                          │
│ 数据状态          │ single_select    │ 待处理/处理中/已完成/失败            │
│ 负责人            │ user             │ 负责该商品的运营人员                  │
│ 备注              │ long_text        │ 内部备注                              │
└──────────────────┴──────────────────┴───────────────────────────────────────┘
```

### 4.2 审核记录表结构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          审核记录表 (reviews)                                │
├──────────────────┬──────────────────┬───────────────────────────────────────┤
│     字段名称      │     字段类型      │              说明                     │
├──────────────────┼──────────────────┼───────────────────────────────────────┤
│ 审核单号          │ text             │ 唯一标识（自动生成）                  │
│ 关联商品          │ link             │ 关联商品表记录                        │
│ 原始标题          │ text             │ AI 优化前的标题                        │
│ 优化后标题        │ text             │ AI 优化后的标题                        │
│ 最终标题          │ text             │ 人工审核确认的标题                    │
│ 原始描述          │ long_text        │ AI 优化前的描述                        │
│ 优化后描述        │ long_text        │ AI 优化后的描述                        │
│ 最终描述          │ long_text        │ 人工审核确认的描述                    │
│ 五点描述          │ long_text        │ 五点描述（JSON）                      │
│ 关键词列表        │ multi_select     │ 优化后的关键词                        │
│ 审核状态          │ single_select    │ 待审核/审核中/已通过/已拒绝/需修改   │
│ 审核人            │ user             │ 审核操作人员                          │
│ 审核意见          │ long_text        │ 审核备注/修改意见                     │
│ 创建时间          │ datetime         │ 记录创建时间                          │
│ 审核时间          │ datetime         │ 审核完成时间                          │
└──────────────────┴──────────────────┴───────────────────────────────────────┘
```

### 4.3 任务监控表结构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          任务监控表 (tasks)                                  │
├──────────────────┬──────────────────┬───────────────────────────────────────┤
│     字段名称      │     字段类型      │              说明                     │
├──────────────────┼──────────────────┼───────────────────────────────────────┤
│ 任务 ID           │ text             │ 唯一标识                              │
│ 任务名称          │ text             │ 任务描述                              │
│ 任务类型          │ single_select    │ 采集/优化/同步/上传                   │
│ 任务状态          │ single_select    │ 待执行/执行中/已完成/失败/已取消     │
│ 优先级            │ single_select    │ 低/中/高/紧急                         │
│ 源 URL            │ url              │ 目标采集链接                          │
│ 目标平台          │ single_select    │ 目标平台名称                          │
│ 进度              │ number           │ 执行进度（0-100）                     │
│ 开始时间          │ datetime         │ 任务开始时间                          │
│ 结束时间          │ datetime         │ 任务完成时间                          │
│ 耗时（秒）        │ number           │ 执行耗时                              │
│ 执行日志          │ long_text        │ 详细执行日志                          │
│ 错误信息          │ long_text        │ 失败时的错误信息                      │
│ 重试次数          │ number           │ 重试次数                              │
│ 创建人            │ user             │ 任务创建人                            │
│ 执行人            │ user             │ 任务执行人                            │
└──────────────────┴──────────────────┴───────────────────────────────────────┘
```

### 4.4 Python 数据模型

```python
# src/models/feishu_models.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class PlatformType(str, Enum):
    """平台类型"""
    TAOBAO = "淘宝"
    ALIBABA_1688 = "1688"
    ALIEXPRESS = "速卖通"
    AMAZON = "亚马逊"


class DataStatus(str, Enum):
    """数据状态"""
    PENDING = "待处理"
    PROCESSING = "处理中"
    COMPLETED = "已完成"
    FAILED = "失败"


class ReviewStatus(str, Enum):
    """审核状态"""
    PENDING = "待审核"
    IN_REVIEW = "审核中"
    APPROVED = "已通过"
    REJECTED = "已拒绝"
    NEEDS_EDIT = "需修改"


@dataclass
class ProductRecord:
    """商品记录"""
    # 基本信息
    product_name: str
    product_id: str
    platform: PlatformType
    source_url: str
    price: float
    original_price: Optional[float] = None
    currency: str = "CNY"
    
    # 销售信息
    sales_count: Optional[int] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    
    # 商品详情
    brand: Optional[str] = None
    shop_name: Optional[str] = None
    category: Optional[str] = None
    
    # 媒体资源
    main_image_url: Optional[str] = None
    image_urls: List[str] = field(default_factory=list)
    
    # 描述信息
    description: Optional[str] = None
    features: List[str] = field(default_factory=list)
    specifications: Dict[str, str] = field(default_factory=dict)
    
    # 元数据
    keywords: List[str] = field(default_factory=list)
    crawl_time: datetime = field(default_factory=datetime.now)
    update_time: Optional[datetime] = None
    
    # 管理信息
    status: DataStatus = DataStatus.PENDING
    owner_user_id: Optional[str] = None
    remarks: Optional[str] = None
    
    def to_feishu_fields(self) -> Dict[str, Any]:
        """转换为飞书字段格式"""
        fields = {
            "商品名称": self.product_name,
            "商品 ID": self.product_id,
            "源平台": self.platform.value,
            "源链接": self.source_url,
            "价格": self.price,
            "货币单位": self.currency,
            "采集时间": int(self.crawl_time.timestamp() * 1000),
            "数据状态": self.status.value,
        }
        
        # 可选字段
        if self.original_price:
            fields["原价"] = self.original_price
        if self.sales_count:
            fields["销量"] = self.sales_count
        if self.rating:
            fields["评分"] = self.rating
        if self.review_count:
            fields["评价数量"] = self.review_count
        if self.brand:
            fields["品牌"] = self.brand
        if self.shop_name:
            fields["店铺名称"] = self.shop_name
        if self.category:
            fields["分类"] = self.category
        if self.description:
            fields["商品描述"] = self.description
        if self.features:
            fields["特点列表"] = "\n".join(self.features)
        if self.keywords:
            fields["关键词"] = self.keywords
        if self.remarks:
            fields["备注"] = self.remarks
        
        # 图片处理
        if self.main_image_url:
            fields["主图"] = [{"url": self.main_image_url}]
        
        return fields
    
    @classmethod
    def from_feishu_fields(cls, fields: Dict[str, Any], record_id: str = "") -> "ProductRecord":
        """从飞书字段创建"""
        return cls(
            product_name=fields.get("商品名称", ""),
            product_id=fields.get("商品 ID", ""),
            platform=PlatformType(fields.get("源平台", "淘宝")),
            source_url=fields.get("源链接", ""),
            price=float(fields.get("价格", 0)),
            original_price=fields.get("原价"),
            currency=fields.get("货币单位", "CNY"),
            sales_count=fields.get("销量"),
            rating=fields.get("评分"),
            review_count=fields.get("评价数量"),
            brand=fields.get("品牌"),
            shop_name=fields.get("店铺名称"),
            category=fields.get("分类"),
            description=fields.get("商品描述"),
            features=fields.get("特点列表", "").split("\n") if fields.get("特点列表") else [],
            keywords=fields.get("关键词", []),
            status=DataStatus(fields.get("数据状态", "待处理")),
            remarks=fields.get("备注"),
        )


@dataclass
class ReviewRecord:
    """审核记录"""
    review_id: str
    product_record_id: str
    
    # 标题相关
    original_title: str
    optimized_title: str
    final_title: Optional[str] = None
    
    # 描述相关
    original_description: str
    optimized_description: str
    final_description: Optional[str] = None
    
    # 其他
    bullet_points: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    
    # 审核信息
    status: ReviewStatus = ReviewStatus.PENDING
    reviewer_user_id: Optional[str] = None
    review_comments: Optional[str] = None
    
    created_time: datetime = field(default_factory=datetime.now)
    reviewed_time: Optional[datetime] = None
    
    def to_feishu_fields(self) -> Dict[str, Any]:
        """转换为飞书字段格式"""
        return {
            "审核单号": self.review_id,
            "原始标题": self.original_title,
            "优化后标题": self.optimized_title,
            "最终标题": self.final_title or "",
            "原始描述": self.original_description,
            "优化后描述": self.optimized_description,
            "最终描述": self.final_description or "",
            "五点描述": "\n".join(self.bullet_points),
            "关键词列表": self.keywords,
            "审核状态": self.status.value,
            "审核意见": self.review_comments,
            "创建时间": int(self.created_time.timestamp() * 1000),
        }
```

---

## 5. 核心模块实现

### 5.1 飞书多维表格客户端

```python
# src/feishu/bitable_client.py
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import time


@dataclass
class BitableRecord:
    """飞书表格记录"""
    record_id: str
    fields: Dict[str, Any]
    created_time: int
    updated_time: int


class FeishuBitableClient:
    """
    飞书多维表格客户端
    
    功能:
    - 认证管理（Token 获取和刷新）
    - 数据表操作（增删改查）
    - 批量操作支持
    - 自动重试和错误处理
    """
    
    API_BASE = "https://open.feishu.cn/open-apis"
    
    def __init__(
        self,
        app_id: str,
        app_secret: str,
        app_token: str,
        timeout: int = 30,
    ):
        """
        初始化客户端
        
        Args:
            app_id: 飞书应用 App ID
            app_secret: 飞书应用 App Secret
            app_token: 多维表格应用 Token（从表格 URL 获取）
            timeout: 请求超时时间（秒）
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.app_token = app_token
        self.timeout = timeout
        
        self._access_token: Optional[str] = None
        self._token_expire: int = 0
        
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
        })
    
    def _get_access_token(self) -> str:
        """获取访问令牌（带缓存）"""
        if self._access_token and time.time() < self._token_expire:
            return self._access_token
        
        url = f"{self.API_BASE}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        response = requests.post(url, json=payload, timeout=self.timeout)
        data = response.json()
        
        if data.get("code") != 0:
            raise FeishuAPIError(f"获取 Token 失败：{data.get('msg')}")
        
        self._access_token = data["tenant_access_token"]
        self._token_expire = time.time() + data["expire"] - 300
        
        return self._access_token
    
    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        发送 API 请求
        
        Args:
            method: HTTP 方法
            endpoint: API 端点（不包含基础 URL）
            **kwargs: 传递给 requests 的其他参数
            
        Returns:
            API 响应数据
        """
        url = f"{self.API_BASE}{endpoint}"
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self._get_access_token()}"
        
        # 重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.request(
                    method,
                    url,
                    headers=headers,
                    timeout=self.timeout,
                    **kwargs
                )
                
                data = response.json()
                
                if data.get("code") != 0:
                    raise FeishuAPIError(
                        f"API 错误：{data.get('msg')}",
                        code=data.get("code")
                    )
                
                return data
                
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise FeishuAPIError(f"请求失败：{e}")
                time.sleep(2 ** attempt)  # 指数退避
    
    # ==================== 数据表操作 ====================
    
    def get_tables(self) -> List[Dict[str, Any]]:
        """获取所有数据表"""
        endpoint = f"/bitable/v1/apps/{self.app_token}/tables"
        result = self._request("GET", endpoint)
        return result.get("data", {}).get("items", [])
    
    def get_table_info(self, table_id: str) -> Dict[str, Any]:
        """获取数据表详情"""
        endpoint = f"/bitable/v1/apps/{self.app_token}/tables/{table_id}"
        result = self._request("GET", endpoint)
        return result.get("data", {})
    
    def get_fields(self, table_id: str) -> List[Dict[str, Any]]:
        """获取数据表字段"""
        endpoint = f"/bitable/v1/apps/{self.app_token}/tables/{table_id}/fields"
        result = self._request("GET", endpoint)
        return result.get("data", {}).get("items", [])
    
    # ==================== 记录操作 ====================
    
    def get_record(
        self,
        table_id: str,
        record_id: str,
    ) -> Optional[BitableRecord]:
        """获取单条记录"""
        endpoint = f"/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/{record_id}"
        result = self._request("GET", endpoint)
        data = result.get("data", {})
        
        if data:
            return BitableRecord(
                record_id=data["record_id"],
                fields=data["fields"],
                created_time=data["created_time"],
                updated_time=data["updated_time"]
            )
        return None
    
    def get_records(
        self,
        table_id: str,
        page_size: int = 100,
        page_token: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[BitableRecord]:
        """
        获取记录列表（支持分页）
        
        Args:
            table_id: 数据表 ID
            page_size: 每页数量（最大 500）
            page_token: 分页令牌
            filter: 过滤条件
            
        Returns:
            记录列表
        """
        all_records = []
        
        while True:
            endpoint = f"/bitable/v1/apps/{self.app_token}/tables/{table_id}/records"
            params = {"page_size": min(page_size, 500)}
            
            if page_token:
                params["page_token"] = page_token
            
            if filter:
                params["filter"] = filter
            
            result = self._request("GET", endpoint, params=params)
            data = result.get("data", {})
            
            for item in data.get("items", []):
                all_records.append(BitableRecord(
                    record_id=item["record_id"],
                    fields=item["fields"],
                    created_time=item["created_time"],
                    updated_time=item["updated_time"]
                ))
            
            # 检查是否有下一页
            if not data.get("has_more"):
                break
            
            page_token = data.get("page_token")
        
        return all_records
    
    def create_record(
        self,
        table_id: str,
        fields: Dict[str, Any],
    ) -> BitableRecord:
        """
        创建记录
        
        Args:
            table_id: 数据表 ID
            fields: 字段数据（字典格式）
            
        Returns:
            创建的记录
        """
        endpoint = f"/bitable/v1/apps/{self.app_token}/tables/{table_id}/records"
        payload = {"fields": fields}
        
        result = self._request("POST", endpoint, json=payload)
        data = result.get("data", {})
        
        return BitableRecord(
            record_id=data["record_id"],
            fields=data["fields"],
            created_time=data["created_time"],
            updated_time=data["updated_time"]
        )
    
    def batch_create_records(
        self,
        table_id: str,
        records: List[Dict[str, Any]],
    ) -> List[BitableRecord]:
        """
        批量创建记录（最多 500 条）
        
        Args:
            table_id: 数据表 ID
            records: 记录列表，每项包含 fields 字典
            
        Returns:
            创建的记录列表
        """
        created_records = []
        
        # 分批处理（每批 500 条）
        batch_size = 500
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            endpoint = f"/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/batch"
            payload = {
                "records": [{"fields": r} for r in batch]
            }
            
            result = self._request("POST", endpoint, json=payload)
            
            for item in result.get("data", {}).get("items", []):
                created_records.append(BitableRecord(
                    record_id=item["record_id"],
                    fields=item["fields"],
                    created_time=item["created_time"],
                    updated_time=item["updated_time"]
                ))
        
        return created_records
    
    def update_record(
        self,
        table_id: str,
        record_id: str,
        fields: Dict[str, Any],
    ) -> BitableRecord:
        """
        更新记录
        
        Args:
            table_id: 数据表 ID
            record_id: 记录 ID
            fields: 要更新的字段
            
        Returns:
            更新后的记录
        """
        endpoint = f"/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/{record_id}"
        payload = {"fields": fields}
        
        result = self._request("PUT", endpoint, json=payload)
        data = result.get("data", {})
        
        return BitableRecord(
            record_id=data["record_id"],
            fields=data["fields"],
            created_time=data["created_time"],
            updated_time=data["updated_time"]
        )
    
    def batch_update_records(
        self,
        table_id: str,
        records: List[Dict[str, Any]],
    ) -> List[BitableRecord]:
        """
        批量更新记录
        
        Args:
            table_id: 数据表 ID
            records: 记录列表，每项包含 record_id 和 fields
            
        Returns:
            更新后的记录列表
        """
        endpoint = f"/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/batch"
        payload = {
            "records": [
                {"record_id": r["record_id"], "fields": r["fields"]}
                for r in records
            ]
        }
        
        result = self._request("PUT", endpoint, json=payload)
        
        updated_records = []
        for item in result.get("data", {}).get("items", []):
            updated_records.append(BitableRecord(
                record_id=item["record_id"],
                fields=item["fields"],
                created_time=item["created_time"],
                updated_time=item["updated_time"]
            ))
        
        return updated_records
    
    def delete_record(
        self,
        table_id: str,
        record_id: str,
    ) -> bool:
        """
        删除记录
        
        Args:
            table_id: 数据表 ID
            record_id: 记录 ID
            
        Returns:
            是否删除成功
        """
        endpoint = f"/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/{record_id}"
        result = self._request("DELETE", endpoint)
        return result.get("code") == 0
    
    def batch_delete_records(
        self,
        table_id: str,
        record_ids: List[str],
    ) -> int:
        """
        批量删除记录
        
        Args:
            table_id: 数据表 ID
            record_ids: 记录 ID 列表
            
        Returns:
            删除的记录数量
        """
        endpoint = f"/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/batch"
        payload = {"record_ids": record_ids}
        
        result = self._request("DELETE", endpoint, json=payload)
        return len(result.get("data", {}).get("items", []))
    
    # ==================== 搜索功能 ====================
    
    def search_records(
        self,
        table_id: str,
        search_text: str,
        field_names: Optional[List[str]] = None,
    ) -> List[BitableRecord]:
        """
        搜索记录
        
        Args:
            table_id: 数据表 ID
            search_text: 搜索文本
            field_names: 指定搜索字段（不指定则搜索全部）
            
        Returns:
            匹配的记录列表
        """
        endpoint = f"/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/search"
        payload = {
            "search_text": search_text,
        }
        
        if field_names:
            payload["field_names"] = field_names
        
        result = self._request("POST", endpoint, json=payload)
        
        records = []
        for item in result.get("data", {}).get("items", []):
            records.append(BitableRecord(
                record_id=item["record_id"],
                fields=item["fields"],
                created_time=item["created_time"],
                updated_time=item["updated_time"]
            ))
        
        return records


class FeishuAPIError(Exception):
    """飞书 API 错误"""
    def __init__(self, message: str, code: Optional[int] = None):
        super().__init__(message)
        self.code = code
```

### 5.2 数据同步服务

```python
# src/feishu/sync_service.py
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json

from .bitable_client import FeishuBitableClient, BitableRecord, FeishuAPIError
from src.models.feishu_models import ProductRecord, ReviewRecord, DataStatus


logger = logging.getLogger(__name__)


class DataSyncService:
    """
    数据同步服务
    
    功能:
    - 将本地数据同步到飞书多维表格
    - 支持增量同步和全量同步
    - 自动处理字段映射和数据转换
    - 同步状态追踪和错误处理
    """
    
    def __init__(
        self,
        client: FeishuBitableClient,
        table_config: Dict[str, str],
    ):
        """
        初始化同步服务
        
        Args:
            client: 飞书客户端实例
            table_config: 表配置 {表名：表 ID}
        """
        self.client = client
        self.table_config = table_config
        
        # 同步统计
        self.stats = {
            "created": 0,
            "updated": 0,
            "failed": 0,
            "skipped": 0,
        }
    
    async def sync_product(
        self,
        product: ProductRecord,
        table_id: Optional[str] = None,
        update_if_exists: bool = True,
    ) -> Optional[BitableRecord]:
        """
        同步单个商品记录
        
        Args:
            product: 商品记录
            table_id: 目标表 ID（默认使用配置的商品表）
            update_if_exists: 如果记录已存在是否更新
            
        Returns:
            同步后的记录
        """
        table_id = table_id or self.table_config.get("products")
        
        if not table_id:
            raise ValueError("未配置商品表 ID")
        
        try:
            # 检查是否已存在（通过商品 ID）
            existing = await self._find_by_product_id(table_id, product.product_id)
            
            if existing:
                if update_if_exists:
                    # 更新现有记录
                    fields = product.to_feishu_fields()
                    fields["更新时间"] = int(datetime.now().timestamp() * 1000)
                    
                    record = self.client.update_record(table_id, existing.record_id, fields)
                    self.stats["updated"] += 1
                    logger.info(f"更新商品记录：{product.product_id}")
                    return record
                else:
                    self.stats["skipped"] += 1
                    logger.debug(f"跳过已存在的商品：{product.product_id}")
                    return existing
            
            # 创建新记录
            fields = product.to_feishu_fields()
            record = self.client.create_record(table_id, fields)
            self.stats["created"] += 1
            logger.info(f"创建商品记录：{product.product_id}")
            return record
            
        except FeishuAPIError as e:
            self.stats["failed"] += 1
            logger.error(f"同步商品失败 {product.product_id}: {e}")
            return None
    
    async def sync_products_batch(
        self,
        products: List[ProductRecord],
        table_id: Optional[str] = None,
        batch_size: int = 100,
    ) -> Dict[str, int]:
        """
        批量同步商品记录
        
        Args:
            products: 商品记录列表
            table_id: 目标表 ID
            batch_size: 批次大小
            
        Returns:
            同步统计信息
        """
        table_id = table_id or self.table_config.get("products")
        
        if not table_id:
            raise ValueError("未配置商品表 ID")
        
        logger.info(f"开始批量同步 {len(products)} 个商品...")
        
        # 重置统计
        self.stats = {"created": 0, "updated": 0, "failed": 0, "skipped": 0}
        
        # 获取现有记录（用于判断是否更新）
        existing_records = self.client.get_records(table_id, page_size=500)
        existing_map = {
            r.fields.get("商品 ID"): r 
            for r in existing_records
        }
        
        # 分批处理
        create_batch = []
        update_batch = []
        
        for product in products:
            existing = existing_map.get(product.product_id)
            
            if existing:
                fields = product.to_feishu_fields()
                fields["更新时间"] = int(datetime.now().timestamp() * 1000)
                update_batch.append({
                    "record_id": existing.record_id,
                    "fields": fields
                })
            else:
                create_batch.append(product.to_feishu_fields())
        
        # 批量创建
        if create_batch:
            for i in range(0, len(create_batch), batch_size):
                batch = create_batch[i:i + batch_size]
                try:
                    self.client.batch_create_records(table_id, batch)
                    self.stats["created"] += len(batch)
                    logger.info(f"批量创建 {len(batch)} 条记录")
                except FeishuAPIError as e:
                    self.stats["failed"] += len(batch)
                    logger.error(f"批量创建失败：{e}")
        
        # 批量更新
        if update_batch:
            for i in range(0, len(update_batch), batch_size):
                batch = update_batch[i:i + batch_size]
                try:
                    self.client.batch_update_records(table_id, batch)
                    self.stats["updated"] += len(batch)
                    logger.info(f"批量更新 {len(batch)} 条记录")
                except FeishuAPIError as e:
                    self.stats["failed"] += len(batch)
                    logger.error(f"批量更新失败：{e}")
        
        logger.info(f"批量同步完成：{self.stats}")
        return self.stats
    
    async def sync_review(
        self,
        review: ReviewRecord,
        table_id: Optional[str] = None,
    ) -> Optional[BitableRecord]:
        """
        同步审核记录
        
        Args:
            review: 审核记录
            table_id: 目标表 ID
            
        Returns:
            同步后的记录
        """
        table_id = table_id or self.table_config.get("reviews")
        
        if not table_id:
            raise ValueError("未配置审核表 ID")
        
        try:
            fields = review.to_feishu_fields()
            
            if review.reviewed_time:
                fields["审核时间"] = int(review.reviewed_time.timestamp() * 1000)
            
            record = self.client.create_record(table_id, fields)
            logger.info(f"创建审核记录：{review.review_id}")
            return record
            
        except FeishuAPIError as e:
            logger.error(f"同步审核记录失败 {review.review_id}: {e}")
            return None
    
    async def _find_by_product_id(
        self,
        table_id: str,
        product_id: str,
    ) -> Optional[BitableRecord]:
        """通过商品 ID 查找记录"""
        records = self.client.search_records(
            table_id,
            product_id,
            field_names=["商品 ID"]
        )
        
        if records:
            return records[0]
        return None
    
    def get_stats(self) -> Dict[str, int]:
        """获取同步统计"""
        return self.stats
```

### 5.3 图片上传模块

```python
# src/feishu/image_uploader.py
import requests
from typing import List, Dict, Any
from pathlib import Path


class FeishuImageUploader:
    """
    飞书图片上传器
    
    飞书多维表格的图片字段需要先将图片上传到飞书云文档，
    然后使用返回的 token 来设置图片字段。
    """
    
    API_BASE = "https://open.feishu.cn/open-apis"
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}",
        })
    
    def upload_image_from_url(self, image_url: str, folder_token: str) -> Dict[str, Any]:
        """
        从 URL 上传图片到飞书云文档
        
        Args:
            image_url: 图片 URL
            folder_token: 云文档文件夹 token
            
        Returns:
            上传结果，包含 file_token
        """
        # 1. 下载图片
        response = requests.get(image_url)
        if response.status_code != 200:
            raise Exception(f"下载图片失败：{image_url}")
        
        image_data = response.content
        
        # 2. 准备上传
        file_name = image_url.split("/")[-1].split("?")[0]
        if not file_name.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
            file_name += ".jpg"
        
        # 3. 上传文件
        upload_url = f"{self.API_BASE}/drive/v1/medias/upload"
        
        files = {
            "media": (file_name, image_data, "image/jpeg")
        }
        
        data = {
            "folder_token": folder_token,
        }
        
        response = self.session.post(upload_url, files=files, data=data)
        result = response.json()
        
        if result.get("code") != 0:
            raise Exception(f"上传图片失败：{result.get('msg')}")
        
        return result.get("data", {})
    
    def upload_image_from_file(self, file_path: str, folder_token: str) -> Dict[str, Any]:
        """
        从本地文件上传图片
        
        Args:
            file_path: 本地图片文件路径
            folder_token: 云文档文件夹 token
            
        Returns:
            上传结果
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在：{file_path}")
        
        with open(file_path, "rb") as f:
            image_data = f.read()
        
        upload_url = f"{self.API_BASE}/drive/v1/medias/upload"
        
        files = {
            "media": (file_path.name, image_data, "image/jpeg")
        }
        
        data = {
            "folder_token": folder_token,
        }
        
        response = self.session.post(upload_url, files=files, data=data)
        result = response.json()
        
        if result.get("code") != 0:
            raise Exception(f"上传图片失败：{result.get('msg')}")
        
        return result.get("data", {})
    
    def convert_to_image_field(
        self,
        file_token: str,
        name: str = "",
    ) -> Dict[str, Any]:
        """
        将上传的文件转换为图片字段格式
        
        Args:
            file_token: 上传返回的 file_token
            name: 图片名称
            
        Returns:
            图片字段格式（用于设置到多维表格）
        """
        return {
            "name": name or "image",
            "file_token": file_token,
        }
```

---

## 6. 数据同步策略

### 6.1 同步模式实现

```python
# src/feishu/sync_strategies.py
from abc import ABC, abstractmethod
from typing import List, Any
from datetime import datetime, timedelta
import asyncio


class SyncStrategy(ABC):
    """同步策略基类"""
    
    @abstractmethod
    async def sync(self, data: List[Any], **kwargs) -> dict:
        """执行同步"""
        pass


class RealTimeSyncStrategy(SyncStrategy):
    """
    实时同步策略
    
    每条数据采完立即同步到飞书
    适用于重要数据、紧急任务
    """
    
    def __init__(self, sync_service):
        self.sync_service = sync_service
    
    async def sync(self, data: List[Any], **kwargs) -> dict:
        results = []
        for item in data:
            result = await self.sync_service.sync_product(item)
            results.append(result)
            # 避免 API 限流
            await asyncio.sleep(0.1)
        
        return self.sync_service.get_stats()


class BatchSyncStrategy(SyncStrategy):
    """
    批量同步策略
    
    达到阈值后批量同步
    适用于大批量采集任务
    """
    
    def __init__(self, sync_service, batch_size: int = 100):
        self.sync_service = sync_service
        self.batch_size = batch_size
    
    async def sync(self, data: List[Any], **kwargs) -> dict:
        return await self.sync_service.sync_products_batch(
            data,
            batch_size=self.batch_size
        )


class ScheduledSyncStrategy(SyncStrategy):
    """
    定时同步策略
    
    按固定时间间隔同步
    适用于定期更新数据
    """
    
    def __init__(self, sync_service, interval_minutes: int = 30):
        self.sync_service = sync_service
        self.interval = timedelta(minutes=interval_minutes)
        self.last_sync: datetime = None
    
    async def sync(self, data: List[Any], **kwargs) -> dict:
        now = datetime.now()
        
        # 检查是否到达同步时间
        if self.last_sync and (now - self.last_sync) < self.interval:
            return {"skipped": len(data), "reason": "未到同步时间"}
        
        result = await self.sync_service.sync_products_batch(data)
        self.last_sync = now
        
        return result
```

### 6.2 数据去重策略

```python
# src/feishu/deduplication.py
from typing import List, Set, Dict, Any
from src.models.feishu_models import ProductRecord


class DeduplicationStrategy:
    """数据去重策略"""
    
    def __init__(self, client):
        self.client = client
    
    def get_existing_ids(self, table_id: str) -> Set[str]:
        """获取现有记录 ID 集合"""
        records = self.client.get_records(table_id, page_size=500)
        return {r.fields.get("商品 ID") for r in records}
    
    def deduplicate(
        self,
        products: List[ProductRecord],
        existing_ids: Set[str],
        keep_newest: bool = True,
    ) -> List[ProductRecord]:
        """
        去重处理
        
        Args:
            products: 待处理的商品列表
            existing_ids: 现有记录 ID 集合
            keep_newest: 是否保留最新的
            
        Returns:
            去重后的商品列表
        """
        seen = set()
        result = []
        
        for product in products:
            if product.product_id in existing_ids:
                # 已存在，根据策略决定是否保留
                if keep_newest and product.product_id not in seen:
                    result.append(product)
                    seen.add(product.product_id)
            else:
                # 新数据，直接添加
                result.append(product)
                seen.add(product.product_id)
        
        return result
```

### 6.3 错误处理和重试

```python
# src/feishu/error_handler.py
import asyncio
import logging
from typing import Callable, Any, Optional
from functools import wraps


logger = logging.getLogger(__name__)


class RetryConfig:
    """重试配置"""
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential: bool = True,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential = exponential


def retry_on_error(config: Optional[RetryConfig] = None):
    """
    错误重试装饰器
    
    用法:
        @retry_on_error(RetryConfig(max_retries=3))
        async def my_api_call():
            ...
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(config.max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == config.max_retries - 1:
                        break
                    
                    # 计算延迟时间
                    if config.exponential:
                        delay = min(config.base_delay * (2 ** attempt), config.max_delay)
                    else:
                        delay = config.base_delay
                    
                    logger.warning(
                        f"{func.__name__} 失败，{config.max_retries - attempt - 1} "
                        f"次后重试，延迟 {delay:.1f}s: {e}"
                    )
                    
                    await asyncio.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator
```

---

## 7. 自动化工作流

### 7.1 飞书自动化配置

飞书多维表格支持内置的自动化工作流，可以配置触发器和动作：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           自动化工作流示例                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  触发器                          动作                                        │
│  ┌─────────────────┐           ┌─────────────────────────────────────────┐ │
│  │ 当记录被创建时   │──────────►│ 1. 发送飞书消息通知负责人                │ │
│  │ (商品表)        │           │ 2. 创建关联的审核记录                   │ │
│  └─────────────────┘           │ 3. 更新任务状态为"处理中"               │ │
│                                └─────────────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────┐           ┌─────────────────────────────────────────┐ │
│  │ 当审核状态变更   │──────────►│ 1. 审核通过：生成上传模板               │ │
│  │ 为"已通过"时     │           │ 2. 审核拒绝：发送通知给创建人          │ │
│  └─────────────────┘           │ 3. 记录操作日志                         │ │
│                                └─────────────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────┐           ┌─────────────────────────────────────────┐ │
│  │ 每天上午 9 点     │──────────►│ 1. 统计昨日采集数据                     │ │
│  │ (定时触发)      │           │ 2. 生成日报发送到群聊                   │ │
│  └─────────────────┘           │ 3. 清理过期临时数据                     │ │
│                                └─────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 飞书机器人通知

```python
# src/feishu/bot_notifier.py
import requests
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class NotificationMessage:
    """通知消息"""
    title: str
    content: str
    mention_users: List[str] = None
    link: str = None


class FeishuBotNotifier:
    """
    飞书机器人通知器
    
    通过 Webhook 发送消息到飞书群聊
    """
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_text_message(
        self,
        content: str,
        mention_users: List[str] = None,
    ) -> bool:
        """
        发送文本消息
        
        Args:
            content: 消息内容
            mention_users: 要@的用户 ID 列表
        """
        payload = {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }
        
        if mention_users:
            mentions = "\n".join([f"<at user_id='{uid}'></at>" for uid in mention_users])
            payload["content"]["text"] += "\n" + mentions
        
        response = requests.post(self.webhook_url, json=payload)
        return response.json().get("code") == 0
    
    def send_post_message(
        self,
        message: NotificationMessage,
    ) -> bool:
        """
        发送富文本消息（卡片）
        
        Args:
            message: 消息对象
        """
        elements = [
            {
                "tag": "plain_text",
                "content": message.content,
            }
        ]
        
        if message.link:
            elements.append({
                "tag": "a",
                "text": "查看详情",
                "href": message.link,
                "style": {"link": True}
            })
        
        payload = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": message.title,
                        "content": [elements]
                    }
                }
            }
        }
        
        response = requests.post(self.webhook_url, json=payload)
        return response.json().get("code") == 0
    
    def send_sync_report(
        self,
        stats: Dict[str, int],
        duration: float,
    ) -> bool:
        """
        发送同步报告
        
        Args:
            stats: 同步统计信息
            duration: 耗时（秒）
        """
        content = f"""
📊 数据同步报告

✅ 新增：{stats.get('created', 0)} 条
🔄 更新：{stats.get('updated', 0)} 条
⏭️ 跳过：{stats.get('skipped', 0)} 条
❌ 失败：{stats.get('failed', 0)} 条

⏱️ 耗时：{duration:.1f} 秒
        """
        
        return self.send_text_message(content.strip())
```

### 7.3 定时任务调度

```python
# src/feishu/scheduler.py
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Callable, Awaitable, Optional
import aiojobs


logger = logging.getLogger(__name__)


class TaskScheduler:
    """
    任务调度器
    
    支持:
    - 定时执行
    - 延迟执行
    - 周期性执行
    """
    
    def __init__(self, max_concurrent: int = 10):
        self.scheduler = await aiojobs.create_scheduler(max_concurrent=max_concurrent)
        self.scheduled_tasks = {}
    
    async def start(self):
        """启动调度器"""
        logger.info("任务调度器已启动")
    
    async def stop(self):
        """停止调度器"""
        await self.scheduler.close()
        logger.info("任务调度器已停止")
    
    def schedule_once(
        self,
        name: str,
        coro: Awaitable,
        delay_seconds: float = 0,
    ):
        """
        调度一次性任务
        
        Args:
            name: 任务名称
            coro: 协程对象
            delay_seconds: 延迟时间（秒）
        """
        async def wrapper():
            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)
            try:
                await coro
                logger.info(f"任务完成：{name}")
            except Exception as e:
                logger.error(f"任务失败 {name}: {e}")
        
        self.scheduled_tasks[name] = wrapper
        return self.scheduler.spawn(wrapper())
    
    def schedule_interval(
        self,
        name: str,
        coro_func: Callable[[], Awaitable],
        interval_seconds: int,
    ):
        """
        调度周期性任务
        
        Args:
            name: 任务名称
            coro_func: 协程函数
            interval_seconds: 执行间隔
        """
        async def wrapper():
            while True:
                try:
                    await coro_func()
                    logger.info(f"周期任务完成：{name}")
                except Exception as e:
                    logger.error(f"周期任务失败 {name}: {e}")
                
                await asyncio.sleep(interval_seconds)
        
        self.scheduled_tasks[name] = wrapper
        return self.scheduler.spawn(wrapper())
    
    def schedule_cron(
        self,
        name: str,
        coro_func: Callable[[], Awaitable],
        hour: int,
        minute: int,
    ):
        """
        按 Cron 表达式调度（简化版）
        
        Args:
            name: 任务名称
            coro_func: 协程函数
            hour: 执行小时
            minute: 执行分钟
        """
        async def wrapper():
            while True:
                now = datetime.now()
                next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                if now >= next_run:
                    next_run = next_run + timedelta(days=1)
                
                delay = (next_run - now).total_seconds()
                logger.info(f"任务 {name} 将在 {delay:.0f} 秒后执行")
                
                await asyncio.sleep(delay)
                
                try:
                    await coro_func()
                    logger.info(f"Cron 任务完成：{name}")
                except Exception as e:
                    logger.error(f"Cron 任务失败 {name}: {e}")
        
        self.scheduled_tasks[name] = wrapper
        return self.scheduler.spawn(wrapper())
```

---

## 8. 完整代码实现

### 8.1 主程序入口

```python
# main_feishu.py
import asyncio
import click
import logging
from pathlib import Path
import json
from datetime import datetime

from src.feishu.bitable_client import FeishuBitableClient
from src.feishu.sync_service import DataSyncService
from src.feishu.bot_notifier import FeishuBotNotifier
from src.models.feishu_models import ProductRecord, PlatformType, DataStatus


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """飞书多维表格数据同步工具"""
    pass


@cli.command()
@click.option("--config", default="config/feishu.yaml", help="配置文件路径")
def init(config):
    """初始化飞书应用配置"""
    import yaml
    
    config_path = Path(config)
    if not config_path.exists():
        # 创建示例配置
        example_config = {
            "feishu": {
                "app_id": "cli_xxxxxxxxxxxxx",
                "app_secret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                "app_token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            },
            "tables": {
                "products": "tblxxxxxxxxxxxxxx",
                "reviews": "tblyyyyyyyyyyyy",
                "tasks": "tblzzzzzzzzzzzzzz",
            },
            "bot": {
                "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx",
            }
        }
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(example_config, f, allow_unicode=True)
        
        click.echo(f"示例配置已创建：{config_path}")
        click.echo("请编辑配置文件填入实际的 App ID、App Secret 和 Table ID")
    else:
        click.echo(f"配置文件已存在：{config_path}")


@cli.command()
@click.option("--config", default="config/feishu.yaml", help="配置文件路径")
@click.option("--input", "input_file", required=True, help="输入数据文件（JSON）")
@click.option("--batch", is_flag=True, help="使用批量模式")
def sync(config, input_file, batch):
    """同步数据到飞书多维表格"""
    import yaml
    
    # 加载配置
    with open(config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    
    # 加载数据
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 初始化客户端
    client = FeishuBitableClient(
        app_id=cfg["feishu"]["app_id"],
        app_secret=cfg["feishu"]["app_secret"],
        app_token=cfg["feishu"]["app_token"],
    )
    
    # 初始化同步服务
    sync_service = DataSyncService(
        client=client,
        table_config=cfg["tables"],
    )
    
    async def run():
        start_time = datetime.now()
        
        # 转换数据模型
        products = []
        for item in data:
            product = ProductRecord(
                product_name=item.get("title", ""),
                product_id=item.get("asin", "") or item.get("product_id", ""),
                platform=PlatformType(item.get("platform", "淘宝")),
                source_url=item.get("url", ""),
                price=float(item.get("price", 0)),
                original_price=item.get("original_price"),
                currency=item.get("currency", "CNY"),
                sales_count=item.get("sales_count"),
                rating=item.get("rating"),
                review_count=item.get("review_count"),
                brand=item.get("brand"),
                shop_name=item.get("shop_name"),
                category=item.get("category"),
                main_image_url=item.get("main_image"),
                image_urls=item.get("images", []),
                description=item.get("description"),
                features=item.get("features", []),
                keywords=item.get("keywords", []),
                status=DataStatus.PENDING,
            )
            products.append(product)
        
        if batch:
            # 批量模式
            stats = await sync_service.sync_products_batch(products)
        else:
            # 单条模式
            for product in products:
                await sync_service.sync_product(product)
            stats = sync_service.get_stats()
        
        duration = (datetime.now() - start_time).total_seconds()
        
        # 发送通知
        if "bot" in cfg:
            notifier = FeishuBotNotifier(cfg["bot"]["webhook_url"])
            notifier.send_sync_report(stats, duration)
        
        click.echo(f"同步完成：{stats}")
    
    asyncio.run(run())


@cli.command()
@click.option("--config", default="config/feishu.yaml", help="配置文件路径")
@click.option("--table", "table_id", required=True, help="数据表 ID")
@click.option("--query", help="搜索关键词")
def query(config, table_id, query):
    """查询飞书表格数据"""
    import yaml
    
    with open(config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    
    client = FeishuBitableClient(
        app_id=cfg["feishu"]["app_id"],
        app_secret=cfg["feishu"]["app_secret"],
        app_token=cfg["feishu"]["app_token"],
    )
    
    if query:
        records = client.search_records(table_id, query)
        click.echo(f"找到 {len(records)} 条记录:")
        for r in records:
            click.echo(f"  - {r.fields}")
    else:
        records = client.get_records(table_id, page_size=100)
        click.echo(f"共 {len(records)} 条记录:")
        for r in records[:10]:
            click.echo(f"  - {r.fields}")


@cli.command()
@click.option("--config", default="config/feishu.yaml", help="配置文件路径")
def list_tables(config):
    """列出所有数据表"""
    import yaml
    
    with open(config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    
    client = FeishuBitableClient(
        app_id=cfg["feishu"]["app_id"],
        app_secret=cfg["feishu"]["app_secret"],
        app_token=cfg["feishu"]["app_token"],
    )
    
    tables = client.get_tables()
    
    click.echo("数据表列表:")
    for table in tables:
        click.echo(f"  {table['name']} (ID: {table['id']})")


if __name__ == "__main__":
    cli()
```

### 8.2 配置文件示例

```yaml
# config/feishu.yaml
# 飞书应用配置

feishu:
  # 自建应用的 App ID 和 App Secret
  # 在 https://open.feishu.cn/app 创建应用后获取
  app_id: "cli_xxxxxxxxxxxxx"
  app_secret: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  
  # 多维表格应用 Token
  # 从表格 URL 获取：https://xxxxxx.feishu.cn/base/xxxxxxxxxxxxxxxx
  #                                        ^^^^^^^^^^^^^^^^^^^^
  app_token: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 数据表配置
# 表 ID 从表格设置中获取
tables:
  products: "tblxxxxxxxxxxxxxx"   # 商品数据表
  reviews: "tblyyyyyyyyyyyy"      # 审核记录表
  tasks: "tblzzzzzzzzzzzzzz"      # 任务监控表

# 飞书机器人配置（可选）
bot:
  # 在飞书群聊中添加机器人后获取 Webhook URL
  webhook_url: "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxxxxxxxx"

# 同步配置
sync:
  # 默认同步模式：realtime / batch / scheduled
  mode: batch
  # 批量同步阈值
  batch_size: 100
  # 定时同步间隔（分钟）
  interval_minutes: 30

# 日志配置
logging:
  level: INFO
  file: logs/feishu_sync.log
```

---

## 9. 部署与配置

### 9.1 环境准备

```bash
# 1. 安装依赖
uv add feishu-openai aiojobs pyyaml

# 或手动安装
pip install requests aiojobs pyyaml click
```

### 9.2 飞书应用创建步骤

```
1. 访问飞书开放平台：https://open.feishu.cn/

2. 登录企业管理员账号

3. 点击「创建应用」
   - 应用类型：自建应用
   - 应用名称：电商数据同步工具

4. 获取凭证
   - 在「凭证与基础信息」页面获取 App ID 和 App Secret

5. 配置权限
   - 进入「权限管理」
   - 添加以下权限：
     * 多维表格：读取/写入应用的数据表
     * 云文档：读取/写入文件
     * 机器人：发送消息

6. 发布应用
   - 点击「版本管理与发布」
   - 创建新版本并发布

7. 添加到工作台
   - 在「安装与设置」中添加到企业
```

### 9.3 多维表格创建步骤

```
1. 在飞书中创建多维表格
   - 点击「+」→「多维表格」
   - 选择「从模板创建」或「空白创建」

2. 配置数据表结构
   - 根据第 4 节的字段设计创建字段
   - 设置字段类型和验证规则

3. 获取表 ID
   - 点击表右上角「...」→「关于本表」
   - 复制数据表 ID（tbl 开头）

4. 获取应用 Token
   - 从表格 URL 复制 app_token
   - 格式：https://xxx.feishu.cn/base/APP_TOKEN/TABLE_ID
```

### 9.4 快速启动

```bash
# 1. 初始化配置
uv run python main_feishu.py init

# 2. 编辑配置文件
vim config/feishu.yaml

# 3. 测试连接
uv run python main_feishu.py list_tables --config config/feishu.yaml

# 4. 同步数据
uv run python main_feishu.py sync \
  --config config/feishu.yaml \
  --input data/processed/products.json \
  --batch

# 5. 查询数据
uv run python main_feishu.py query \
  --config config/feishu.yaml \
  --table tblxxxxxxxxxxxxxx \
  --query "商品名称"
```

---

## 附录

### A. API 限流说明

| API 类型 | 限流 | 说明 |
|----------|------|------|
| 读取记录 | 50 次/秒 | 单应用 |
| 写入记录 | 20 次/秒 | 单应用 |
| 批量操作 | 5 次/秒 | 单应用 |
| 图片上传 | 10 次/秒 | 单应用 |

### B. 常见问题

| 问题 | 解决方案 |
|------|----------|
| Token 过期 | 实现自动刷新机制（代码已包含） |
| 字段类型不匹配 | 检查字段类型映射表 |
| 批量操作失败 | 确保单批不超过 500 条 |
| 图片无法显示 | 需要先上传到云文档获取 token |

### C. 最佳实践

1. **使用批量 API** - 减少 API 调用次数
2. **实现本地缓存** - 避免重复读取
3. **错误重试机制** - 处理临时故障
4. **增量同步** - 只同步变化的数据
5. **监控告警** - 配置失败通知

---

*文档版本：0.1.0 | 最后更新：2026-03-12*
