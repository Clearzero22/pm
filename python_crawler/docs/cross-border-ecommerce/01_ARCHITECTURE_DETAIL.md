# 系统架构详细设计

> **跨境电商全工作流系统** - 技术架构深度解析

**版本**: v1.0.0
**更新时间**: 2026-03-12

---

## 目录

1. [架构原则](#架构原则)
2. [分层架构](#分层架构)
3. [微服务拆分](#微服务拆分)
4. [数据架构](#数据架构)
5. [通信协议](#通信协议)
6. [安全设计](#安全设计)
7. [扩展性设计](#扩展性设计)

---

## 架构原则

### 核心设计理念

```
┌─────────────────────────────────────────────────────────────────┐
│                     SOLID + KISS + DRY                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  S │ Single Responsibility  │ 每个服务只做一件事                 │
│  O │ Open/Closed            │ 对扩展开放，对修改关闭             │
│  L │ Liskov Substitution    │ 可替换的实现                      │
│  I │ Interface Segregation  │ 专一接口，避免胖接口               │
│  D │ Dependency Inversion   │ 依赖抽象而非具体                  │
│                                                                  │
│  KISS │ Keep It Simple, Stupid │ 追求极致简洁                   │
│  DRY  │ Don't Repeat Yourself  │ 避免重复，抽象复用             │
│  YAGNI │ You Aren't Gonna Need It │ 只做现在需要的              │
└─────────────────────────────────────────────────────────────────┘
```

### 技术选型标准

| 考量因素 | 权重 | 评估标准 |
|----------|------|----------|
| **学习曲线** | ⭐⭐⭐⭐⭐ | Solo/小团队能快速上手 |
| **开发效率** | ⭐⭐⭐⭐⭐ | 快速迭代，减少样板代码 |
| **生态成熟** | ⭐⭐⭐⭐ | 有丰富的第三方库 |
| **社区活跃** | ⭐⭐⭐ | 问题能快速找到解决方案 |
| **长期维护** | ⭐⭐⭐ | 项目有持续维护承诺 |

---

## 分层架构

### 四层架构模型

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Presentation Layer (表现层)                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ Web Dashboard│  │ Mobile App   │  │ Browser Ext. │  │ OpenClaw   │ │
│  │ (React/Vue)  │  │ (React Native│  │ (Chrome)     │  │ (Messages) │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/WS/WC
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        API Gateway Layer (API 网关层)                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    FastAPI Gateway                              │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │  • 认证授权 (JWT)  • 请求路由  • 限流熔断  • 日志监控            │   │
│  │  • API 版本控制   • 文档生成  • 异常处理  • 响应缓存           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ gRPC/REST
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       Business Logic Layer (业务逻辑层)                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│  │ Selection   │ │  Creative   │ │ Operations  │ │  Customer   │      │
│  │ Service     │ │  Service    │ │  Service    │ │  Service    │      │
│  │ (选品)      │ │  (创作)     │ │  (运营)     │ │  (客服)     │      │
│  ├─────────────┤ ├─────────────┤ ├─────────────┤ ├─────────────┤      │
│  │ • 竞品分析  │ │ • AI修图    │ │ • 批量上架  │ │ • 消息聚合  │      │
│  │ • 趋势预测  │ │ • AI文案    │ │ • 库存管理  │ │ • AI回复    │      │
│  │ • 利润计算  │ │ • 提示词    │ │ • 价格监控  │ │ • 退款处理  │      │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘      │
│                                                                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                      │
│  │  Finance    │ │   AI Engine │ │ Integration │                      │
│  │ Service     │ │   Service   │ │  Service    │                      │
│  │ (财务)      │ │  (AI引擎)   │ │  (集成)     │                      │
│  ├─────────────┤ ├─────────────┤ ├─────────────┤                      │
│  │ • 收入统计  │ │ • LLM调用   │ │ • Amazon    │                      │
│  │ • 成本追踪  │ │ • SD生成    │ │ • 1688      │                      │
│  │ • 利润分析  │ │ • 向量检索  │ │ • 物流      │                      │
│  └─────────────┘ └─────────────┘ └─────────────┘                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ SQL/NoSQL
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Data Layer (数据层)                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ PostgreSQL   │  │    Redis     │  │   MinIO/S3   │  │ Vector DB  │ │
│  │ (关系数据库) │  │  (缓存/队列) │  │  (对象存储)   │  │ (向量数据库)│ │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤  ├────────────┤ │
│  │ • 产品数据   │  │ • 会话缓存   │  │ • 图片/视频  │  │ • 嵌入向量  │ │
│  │ • 订单数据   │  │ • 任务队列   │  │ • 文档       │  │ • 知识库    │ │
│  │ • 客户数据   │  │ • 速率限制   │  │ • 备份       │  │ • 语义搜索  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ API
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    External Integration Layer (外部集成层)              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ Amazon SP-API│  │   AI APIs    │  │  Payment     │  │  Logistics │ │
│  │              │  │              │  │  Gateway     │  │  API       │ │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤  ├────────────┤ │
│  │ • Listings   │  │ • OpenAI     │  │ • Stripe     │  │ • FedEx    │ │
│  │ • Orders     │  │ • Claude     │  │ • PayPal     │  │ • UPS      │ │
│  │ • Inventory  │  │ • Stability  │  │ • WC         │  │ • DHL      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 层级职责

| 层级 | 职责 | 技术 |
|------|------|------|
| **表现层** | 用户交互、数据展示 | React, Vue, React Native |
| **API 网关层** | 请求路由、认证授权、限流熔断 | FastAPI, Nginx |
| **业务逻辑层** | 核心业务逻辑、数据处理 | Python 3.11+ |
| **数据层** | 数据持久化、缓存、文件存储 | PostgreSQL, Redis, MinIO |
| **外部集成层** | 第三方服务对接 | SP-API, OpenAI, 等 |

---

## 微服务拆分

### 服务边界

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          微服务拓扑图                                   │
└─────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────┐
                    │       API Gateway           │
                    │  (FastAPI + Service Mesh)   │
                    └──────────────┬──────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐        ┌───────────────┐        ┌───────────────┐
│  Selection    │        │   Creative    │        │  Operations   │
│   Service     │        │    Service    │        │    Service    │
├───────────────┤        ├───────────────┤        ├───────────────┤
│ Port: 8001    │        │ Port: 8002    │        │ Port: 8003    │
│ • 竞品分析    │        │ • AI修图      │        │ • 批量上架    │
│ • 趋势预测    │        │ • AI文案      │        │ • 库存管理    │
│ • 利润计算    │        │ • 提示词      │        │ • 价格监控    │
└───────────────┘        └───────────────┘        └───────────────┘
        │                          │                          │
        └──────────────────────────┼──────────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐        ┌───────────────┐        ┌───────────────┐
│   Customer    │        │    Finance    │        │     AI        │
│   Service     │        │    Service    │        │   Service     │
├───────────────┤        ├───────────────┤        ├───────────────┤
│ Port: 8004    │        │ Port: 8005    │        │ Port: 8006    │
│ • 消息聚合    │        │ • 收入统计    │        │ • LLM调用     │
│ • AI回复      │        │ • 成本追踪    │        │ • SD生成      │
│ • 退款处理    │        │ • 利润分析    │        │ • 向量检索    │
└───────────────┘        └───────────────┘        └───────────────┘
        │                          │                          │
        └──────────────────────────┼──────────────────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │      Shared Services        │
                    ├─────────────────────────────┤
                    │ • Integration (8007)        │
                    │ • Notification (8008)      │
                    │ • File Storage (8009)       │
                    │ • Task Queue (8010)         │
                    └─────────────────────────────┘
```

### 服务间通信

#### 同步通信 (REST/gRPC)

```python
# 服务间调用示例 (使用 HTTP REST)
from httpx import AsyncClient

async def get_product_info(asin: str):
    """从选品服务获取产品信息"""
    async with AsyncClient() as client:
        response = await client.get(
            f"http://selection-service:8001/api/v1/products/{asin}"
        )
        return response.json()

# 使用 gRPC (高性能场景)
import grpc
from proto import selection_pb2, selection_pb2_grpc

async def get_product_grpc(asin: str):
    """使用 gRPC 调用选品服务"""
    async with grpc.aio.insecure_channel('selection-service:50051') as channel:
        stub = selection_pb2_grpc.SelectionServiceStub(channel)
        request = selection_pb2.ProductRequest(asin=asin)
        response = await stub.GetProduct(request)
        return response
```

#### 异步通信 (消息队列)

```python
# 使用 Celery + Redis 进行异步任务
from celery import Celery

# 定义任务
@app.task(name="selection.analyze_competitor")
def analyze_competitor(asin: str):
    """分析竞品 (异步执行)"""
    crawler = CompetitorCrawler()
    return crawler.analyze(asin)

# 触发任务
def start_analysis(asin: str):
    """启动竞品分析"""
    task = analyze_competitor.delay(asin)
    return {"task_id": task.id}

# 任务状态查询
def get_task_status(task_id: str):
    """查询任务状态"""
    result = AsyncResult(task_id)
    return {
        "status": result.status,
        "result": result.result if result.ready() else None
    }
```

### 服务发现与注册

```python
# 使用 Consul 进行服务发现
from consulate import Consul

consul = Consul(host="localhost", port=8500)

# 服务注册
def register_service():
    consul.agent.service.register(
        name="selection-service",
        service_id="selection-1",
        address="192.168.1.100",
        port=8001,
        tags=["selection", "crawler"],
        check=consul.agent.service.check.http(
            "http://192.168.1.100:8001/health",
            interval="10s"
        )
    )

# 服务发现
def discover_service(service_name: str):
    """发现可用服务"""
    services = consul.agent.service.services(service_name)
    return services[0] if services else None

# 健康检查
def health_check():
    """服务健康检查"""
    return {"status": "healthy", "timestamp": datetime.now()}
```

---

## 数据架构

### 数据模型设计

```sql
-- 核心实体关系图

┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   Product   │───────│  Listing    │───────│   Order     │
│  (产品)     │ 1:N   │  (上架)     │ 1:N   │  (订单)     │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │       │ id (PK)     │
│ asin (UK)   │       │ product_id  │       │ amazon_id   │
│ title       │       │ marketplace │       │ status      │
│ category_id │       │ sku         │       │ total       │
│            │       │ price       │       │ currency    │
└─────────────┘       └─────────────┘       └─────────────┘
       │                       │                    │
       │                       │                    │
       ▼                       ▼                    ▼
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  Category   │       │   Asset     │       │  Customer   │
│  (类目)     │       │  (素材)     │       │  (客户)     │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │       │ id (PK)     │
│ name        │       │ product_id  │       │ amazon_id   │
│ path        │       │ type        │       │ name        │
│ parent_id   │       │ url         │       │ email       │
└─────────────┘       │ metadata    │       │ messages[]  │
                     └─────────────┘       └─────────────┘
```

### PostgreSQL Schema

```sql
-- 产品表
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asin VARCHAR(20) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    category_id UUID REFERENCES categories(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 上架表
CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id),
    marketplace VARCHAR(10) NOT NULL, -- US, UK, DE, etc.
    sku VARCHAR(50),
    price DECIMAL(10, 2),
    quantity INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, deleted
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(product_id, marketplace)
);

-- 订单表
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    amazon_id VARCHAR(50) UNIQUE NOT NULL,
    customer_id UUID REFERENCES customers(id),
    marketplace VARCHAR(10) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    total DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    order_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引优化
CREATE INDEX idx_products_asin ON products(asin);
CREATE INDEX idx_listings_product ON listings(product_id);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date DESC);
```

### Redis 数据结构

```python
# Redis 使用场景

# 1. 会话缓存
redis.setex(f"session:{session_id}", 3600, json.dumps(user_data))

# 2. 速率限制
redis.incr(f"rate_limit:{user_id}:{endpoint}")
redis.expire(f"rate_limit:{user_id}:{endpoint}", 60)

# 3. 缓存热门数据
redis.setex(f"product:{asin}", 86400, json.dumps(product_data))

# 4. 任务队列
from celery import Celery
app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def process_image(image_url: str):
    """异步处理图片"""
    # ...
    pass

# 5. 实时统计
redis.incr(f"stats:views:{product_id}")
redis.expire(f"stats:views:{product_id}", 86400)

# 6. 消息队列 (Pub/Sub)
redis.publish("events:orders", json.dumps(order_event))
```

### Vector Database (知识库)

```python
# 使用 Pinecone/Weaviate 作为向量数据库
import pinecone

# 初始化
pinecone.init(api_key="xxx", environment="us-west1-gcp")
index = pinecone.Index("ecommerce-kb")

# 存储知识
def store_knowledge(id: str, text: str, metadata: dict):
    """存储知识到向量数据库"""
    embedding = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )["data"][0]["embedding"]

    index.upsert([(id, embedding, metadata)])

# 语义搜索
def search_knowledge(query: str, top_k: int = 5):
    """语义搜索知识库"""
    query_embedding = openai.Embedding.create(
        input=query,
        model="text-embedding-ada-002"
    )["data"][0]["embedding"]

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    return results
```

---

## 通信协议

### API 规范

```yaml
# RESTful API 设计规范

# 基础路径
base_url: https://api.ecommerce.com/v1

# 资源命名 (复数名词)
/resources:
  products: /products
  listings: /listings
  orders: /orders
  customers: /customers

# HTTP 方法映射
methods:
  GET: /products          # 列表
  GET: /products/{id}     # 详情
  POST: /products         # 创建
  PUT: /products/{id}     # 更新
  DELETE: /products/{id}  # 删除
  PATCH: /products/{id}   # 部分更新

# 查询参数
parameters:
  pagination: page, limit, offset
  filtering: status=active,category=electronics
  sorting: sort=created_at:desc
  searching: q=keyword

# 响应格式
response:
  success:
    code: 200
    data: { ... }
    meta: { page: 1, limit: 20, total: 100 }
  error:
    code: 400
    error: { message: "Validation failed", code: "VALIDATION_ERROR" }
```

### WebSocket 实时通信

```python
# 使用 FastAPI + WebSocket 实现实时通信
from fastapi import WebSocket
from typing import Dict

class ConnectionManager:
    """WebSocket 连接管理器"""
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    async def broadcast(self, message: dict):
        """广播消息到所有连接"""
        for connection in self.active_connections.values():
            await connection.send_json(message)

    async def send_to_user(self, user_id: str, message: dict):
        """发送消息到特定用户"""
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    user_id = verify_token(token)
    await manager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            # 处理消息
            await manager.send_to_user(user_id, {"echo": data})
    except WebSocketDisconnect:
        manager.disconnect(user_id)
```

---

## 安全设计

### 认证授权

```python
# JWT 认证实现
from datetime import datetime, timedelta
from jose import JWTError, jwt

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = None):
    """创建访问令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """验证令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# FastAPI 依赖注入
from fastapi import Depends, HTTPException, status

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    return payload
```

### 数据加密

```python
# 敏感数据加密
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher_suite = Fernet(key)

def encrypt_data(data: str) -> str:
    """加密数据"""
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data.decode()

def decrypt_data(encrypted_data: str) -> str:
    """解密数据"""
    decrypted_data = cipher_suite.decrypt(encrypted_data.encode())
    return decrypted_data.decode()
```

### API 限流

```python
# 使用 Redis 实现速率限制
from fastapi import HTTPException

async def rate_limit(user_id: str, limit: int = 100, window: int = 60):
    """速率限制"""
    key = f"rate_limit:{user_id}"
    current = redis.get(key)

    if current is None:
        redis.setex(key, window, 1)
        return True

    if int(current) >= limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    redis.incr(key)
    return True
```

---

## 扩展性设计

### 水平扩展

```yaml
# Docker Compose 扩展示例
version: '3.8'
services:
  # API 网关 (多实例)
  api-gateway:
    image: ecommerce/api-gateway:latest
    deploy:
      replicas: 3
    environment:
      - INSTANCE_ID=${HOSTNAME}

  # 选品服务 (多实例)
  selection-service:
    image: ecommerce/selection:latest
    deploy:
      replicas: 2

  # 创作服务 (多实例)
  creative-service:
    image: ecommerce/creative:latest
    deploy:
      replicas: 2
    # GPU 支持
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 负载均衡

```nginx
# Nginx 负载均衡配置
upstream api_backend {
    # 负载均衡算法
    least_conn;

    server api-gateway-1:8000 weight=3;
    server api-gateway-2:8000 weight=2;
    server api-gateway-3:8000 weight=1;

    # 健康检查
    keepalive 32;
}

server {
    listen 80;
    server_name api.ecommerce.com;

    location / {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        # 超时设置
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

---

**下一步**: 查看 [02_DATABASE_SCHEMA.md](./02_DATABASE_SCHEMA.md) 了解数据模型设计
