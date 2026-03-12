# API 设计规范

> **跨境电商全工作流系统** - RESTful API 设计标准

**版本**: v1.0.0
**更新时间**: 2026-03-12

---

## 目录

1. [设计原则](#设计原则)
2. [API 规范](#api-规范)
3. [端点定义](#端点定义)
4. [数据模型](#数据模型)
5. [错误处理](#错误处理)
6. [认证授权](#认证授权)

---

## 设计原则

### RESTful 设计

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         RESTful API 设计原则                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. 资源导向 (Resource-Oriented)                                        │
│     • URL 表示资源 (名词，复数)                                         │
│     • HTTP 方法表示操作                                                 │
│                                                                         │
│  2. 统一接口 (Uniform Interface)                                       │
│     • GET    - 查询资源                                                 │
│     • POST   - 创建资源                                                 │
│     • PUT    - 完整更新资源                                             │
│     • PATCH  - 部分更新资源                                             │
│     • DELETE - 删除资源                                                 │
│                                                                         │
│  3. 无状态 (Stateless)                                                  │
│     • 每个请求包含所有必要信息                                          │
│     • 不依赖服务端会话状态                                              │
│                                                                         │
│  4. 可缓存 (Cacheable)                                                  │
│     • 响应明确标识是否可缓存                                            │
│     • 使用 ETag/Last-Modified                                           │
│                                                                         │
│  5. 分层系统 (Layered System)                                          │
│     • 客户端不知道是否连接到终端服务器                                  │
│     • 支持代理、负载均衡、缓存                                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### URL 命名规范

| 规范 | 示例 | 说明 |
|------|------|------|
| **使用名词** | `/products` | 不是 `/getProducts` |
| **使用复数** | `/orders` | 不是 `/order` |
| **小写+连字符** | `/order-items` | 不是 `/orderItems` |
| **层级关系** | `/products/{id}/listings` | 表示父子关系 |
| **版本控制** | `/api/v1/products` | 非兼容变更时升级版本 |

---

## API 规范

### 基础格式

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          URL 结构                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  https://api.ecommerce.com/api/v{version}/{resource}/{id}               │
│         │            │         │             │                         │
│         │            │         │             └─ 资源标识符               │
│         │            │         └─────────────── 资源名称                 │
│         │            └───────────────────────── API 版本                 │
│         └────────────────────────────────────── API 网关                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 分页规范

```http
GET /api/v1/products?page=1&limit=20&sort=created_at:desc
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `page` | integer | 1 | 页码 (从 1 开始) |
| `limit` | integer | 20 | 每页数量 (max: 100) |
| `sort` | string | created_at:desc | 排序字段:方向 |
| `fields` | string | * | 返回字段 (逗号分隔) |

**响应格式**:
```json
{
  "data": [...],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  },
  "links": {
    "self": "/api/v1/products?page=1",
    "first": "/api/v1/products?page=1",
    "last": "/api/v1/products?page=5",
    "next": "/api/v1/products?page=2",
    "prev": null
  }
}
```

### 过滤规范

```http
GET /api/v1/products?status=active&category=electronics&price_min=10&price_max=100
```

| 过滤类型 | 格式 | 示例 |
|----------|------|------|
| 精确匹配 | `field=value` | `status=active` |
| 多值匹配 | `field=v1,v2` | `status=active,pending` |
| 范围匹配 | `field_min/max` | `price_min=10&price_max=100` |
| 搜索 | `q=keyword` | `q=wireless+mouse` |
| 日期范围 | `field_start/end` | `created_start=2024-01-01` |

---

## 端点定义

### 核心端点

#### 产品相关

```
GET    /api/v1/products
       获取产品列表
       Query: page, limit, status, category, q

POST   /api/v1/products
       创建产品
       Body: ProductCreate

GET    /api/v1/products/{id}
       获取产品详情

PUT    /api/v1/products/{id}
       更新产品

DELETE /api/v1/products/{id}
       删除产品

GET    /api/v1/products/{id}/listings
       获取产品的所有上架信息
```

#### 上架相关

```
GET    /api/v1/listings
       获取上架列表

POST   /api/v1/listings
       创建上架

GET    /api/v1/listings/{id}
       获取上架详情

PATCH  /api/v1/listings/{id}
       部分更新上架

DELETE /api/v1/listings/{id}
       删除上架

POST   /api/v1/listings/batch
       批量操作
       Body: { action: "update_price", items: [...] }
```

#### 订单相关

```
GET    /api/v1/orders
       获取订单列表

GET    /api/v1/orders/{id}
       获取订单详情

GET    /api/v1/orders/{id}/items
       获取订单明细

PATCH  /api/v1/orders/{id}/status
       更新订单状态
```

#### 客户相关

```
GET    /api/v1/customers
       获取客户列表

GET    /api/v1/customers/{id}
       获取客户详情

GET    /api/v1/customers/{id}/orders
       获取客户订单

GET    /api/v1/customers/{id}/messages
       获取客户消息
```

#### 消息相关

```
GET    /api/v1/messages
       获取消息列表

GET    /api/v1/messages/{id}
       获取消息详情

POST   /api/v1/messages/{id}/reply
       回复消息

PATCH  /api/v1/messages/{id}/status
       更新消息状态

POST   /api/v1/messages/batch-read
       批量标记已读
```

### AI 服务端点

```
POST   /api/v1/ai/image/remove-background
       移除图片背景

POST   /api/v1/ai/image/compose-scene
       场景合成

POST   /api/v1/ai/image/generate-product-set
       生成完整产品图片集

POST   /api/v1/ai/copywriting/generate
       生成文案

POST   /api/v1/ai/copywriting/optimize
       优化文案

POST   /api/v1/ai/keywords/generate
       生成关键词

GET    /api/v1/ai/customer/suggest-reply
       AI 客服建议回复
```

### 选品服务端点

```
POST   /api/v1/selection/analyze
       分析竞品

GET    /api/v1/selection/trends
       获取趋势数据

POST   /api/v1/selection/profit-calc
       利润计算

GET    /api/v1/selection/opportunities
       获取机会产品
```

### 财务服务端点

```
GET    /api/v1/finance/revenue
       收入统计

GET    /api/v1/finance/costs
       成本统计

GET    /api/v1/finance/profit
       利润分析

GET    /api/v1/finance/cashflow
       现金流预测
```

---

## 数据模型

### 请求模型

#### 创建产品

```json
{
  "asin": "B0BZYCJK89",
  "title": "Wireless Mouse with RGB Lighting",
  "brand": "Logitech",
  "category_id": "uuid-here",
  "images": ["url1", "url2"],
  "attributes": {
    "color": "Black",
    "wireless": true,
    "dpi": "16000"
  }
}
```

#### 创建上架

```json
{
  "product_id": "uuid-here",
  "marketplace": "US",
  "seller_sku": "MOUSE-BLK-001",
  "standard_price": 29.99,
  "quantity": 100,
  "fulfillment_type": "FBA"
}
```

#### AI 图片生成请求

```json
{
  "product_image": "base64 or URL",
  "scenes": ["minimalist_white", "modern_living", "kitchen_counter"],
  "generate_variants": true,
  "optimize_for_amazon": true
}
```

### 响应模型

#### 产品响应

```json
{
  "data": {
    "id": "uuid",
    "asin": "B0BZYCJK89",
    "title": "Wireless Mouse",
    "brand": "Logitech",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

#### 错误响应

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "asin",
        "message": "ASIN is required"
      }
    ]
  }
}
```

---

## 错误处理

### HTTP 状态码

| 状态码 | 说明 | 使用场景 |
|--------|------|----------|
| 200 | OK | 成功获取/更新/删除 |
| 201 | Created | 成功创建资源 |
| 204 | No Content | 成功删除，无返回内容 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证 |
| 403 | Forbidden | 无权限 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突 |
| 422 | Unprocessable Entity | 验证失败 |
| 429 | Too Many Requests | 速率限制 |
| 500 | Internal Server Error | 服务器错误 |

### 错误码规范

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          错误码结构                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  格式: {SERVICE}_{ERROR_TYPE}_{SPECIFIC_ERROR}                          │
│                                                                         │
│  示例:                                                                   │
│  • PRODUCT_VALIDATION_ASIN_REQUIRED                                     │
│  • LISTING_CONFLICT_SKU_EXISTS                                          │
│  • AI_SERVICE_RATE_LIMIT_EXCEEDED                                       │
│  • AUTHENTICATION_INVALID_TOKEN                                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 错误响应结构

```json
{
  "error": {
    "code": "PRODUCT_VALIDATION_ASIN_REQUIRED",
    "message": "ASIN is required and cannot be empty",
    "details": {
      "field": "asin",
      "constraint": "required",
      "provided_value": null
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "req_abc123"
  },
  "request": {
    "method": "POST",
    "url": "/api/v1/products",
    "body": {"title": "Test"}
  }
}
```

---

## 认证授权

### JWT 认证

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### API Key 认证

```http
X-API-Key: sk_ecommerce_abc123...
```

### 请求流程

```
┌──────────┐         ┌──────────┐         ┌──────────┐         ┌──────────┐
│  Client  │────────▶│   API    │────────▶│  Auth    │────────▶│ Database │
│          │ Token   │ Gateway  │ Forward  │ Service  │ Verify  │          │
└──────────┘         └──────────┘         └──────────┘         └──────────┘
                           │                                            │
                           │ Valid Token                                │
                           ▼                                            │
                    ┌──────────┐                                      │
                    │ Business │                                      │
                    │  Logic   │                                      │
                    └──────────┘                                      │
```

### 权限范围 (Scopes)

| Scope | 说明 |
|-------|------|
| `products:read` | 读取产品 |
| `products:write` | 创建/更新产品 |
| `orders:read` | 读取订单 |
| `messages:write` | 发送消息 |
| `admin:*` | 管理员全部权限 |

---

## API 版本控制

### 版本策略

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          版本控制策略                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  URL 版本 (推荐):                                                        │
│  • /api/v1/products                                                    │
│  • /api/v2/products                                                    │
│                                                                         │
│  Header 版本:                                                           │
│  • Accept: application/vnd.ecommerce.v1+json                            │
│  • Accept: application/vnd.ecommerce.v2+json                            │
│                                                                         │
│  版本弃用:                                                              │
│  • 至少提前 6 个月通知                                                  │
│  • 响应头添加: Deprecation, Sunset                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 响应头

```http
X-API-Version: 1.0.0
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1609459200
X-Request-Id: req_abc123
```

---

## 速率限制

### 限制规则

| 层级 | 限制 | 窗口 |
|------|------|------|
| **匿名** | 100 请求/hour | 滚动窗口 |
| **已认证** | 1000 请求/hour | 滚动窗口 |
| **管理员** | 无限制 | - |

### 响应头

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1609459200
Retry-After: 3600
```

---

## 批量操作

### 批量创建

```http
POST /api/v1/listings/batch
Content-Type: application/json

{
  "action": "create",
  "items": [
    {"product_id": "uuid-1", "marketplace": "US", ...},
    {"product_id": "uuid-2", "marketplace": "UK", ...}
  ]
}
```

### 批量更新

```http
PATCH /api/v1/listings/batch
Content-Type: application/json

{
  "action": "update_price",
  "items": [
    {"id": "uuid-1", "price": 29.99},
    {"id": "uuid-2", "price": 19.99}
  ]
}
```

### 批量响应

```json
{
  "data": {
    "success": 95,
    "failed": 5,
    "total": 100,
    "errors": [
      {
        "index": 5,
        "error": "LISTING_VALIDATION_PRICE_INVALID"
      }
    ]
  },
  "job_id": "batch_job_abc123"
}
```

---

**下一步**: 查看 [06_AMAZON_API.md](./06_AMAZON_API.md)
