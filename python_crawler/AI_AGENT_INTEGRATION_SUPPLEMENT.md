# AI 智能体集成补充指南

> **完整落地 AI 智能体系统所需的额外组件和注意事项**
>
> 本文档补充说明在实现 AI 智能体集成过程中容易被忽略但至关重要的内容。

---

## 目录

1. [安全与合规](#1-安全与合规)
2. [监控与可观测性](#2-监控与可观测性)
3. [性能优化](#3-性能优化)
4. [测试与质量保证](#4-测试与质量保证)
5. [运维与部署](#5-运维与部署)
6. [变更管理](#6-变更管理)
7. [成本优化](#7-成本优化)
8. [知识库与文档](#8-知识库与文档)

---

## 1. 安全与合规

### 1.1 凭据安全管理

```
⚠️ 高风险区域：API Keys、数据库密码、第三方服务凭据
```

**必须实现的安全措施：**

| 措施 | 说明 | 实现方式 |
|------|------|----------|
| **密钥加密存储** | 不明文存储敏感信息 | HashiCorp Vault / AWS Secrets Manager |
| **密钥轮换** | 定期更换 API 密钥 | 自动化轮换脚本（90 天周期） |
| **最小权限原则** | 每个服务只授予必要权限 | IAM 角色细分 |
| **审计日志** | 记录所有敏感操作 | 结构化日志 + SIEM 集成 |

```yaml
# secrets/README.md
# 密钥管理清单

# 必须存储到密钥管理服务的凭据：
- ANTHROPIC_API_KEY
- OPENAI_API_KEY
- FEISHU_APP_SECRET
- AMAZON_SELLER_PASSWORD
- DATABASE_URL
- REDIS_PASSWORD

# 密钥轮换计划：
| 密钥类型 | 轮换周期 | 负责人 | 最后轮换日期 |
|----------|----------|--------|--------------|
| LLM API Key | 90 天 | 运维团队 | 2024-01-15 |
| 飞书应用密钥 | 180 天 | 运维团队 | 2024-02-01 |
| 数据库密码 | 90 天 | DBA | 2024-01-10 |
```

### 1.2 数据隐私保护

```python
# src/security/data_privacy.py
from typing import Any, Dict, List
import re
from dataclasses import dataclass


@dataclass
class PrivacyConfig:
    """隐私配置"""
    # 需要脱敏的字段
    sensitive_fields: List[str] = None
    # 需要加密的字段
    encrypt_fields: List[str] = None
    # 数据保留期限（天）
    retention_days: int = 90


class DataPrivacyHandler:
    """
    数据隐私处理器
    
    功能:
    - 敏感数据脱敏
    - PII（个人身份信息）检测
    - 数据加密存储
    - 自动数据清理
    """
    
    # PII 检测正则
    PII_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone_cn': r'1[3-9]\d{9}',
        'phone_us': r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        'id_card_cn': r'[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]',
        'credit_card': r'\b(?:\d{4}[- ]?){3}\d{4}\b',
    }
    
    def __init__(self, config: PrivacyConfig):
        self.config = config
    
    def mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        脱敏敏感数据
        
        Args:
            data: 原始数据
            
        Returns:
            脱敏后的数据
        """
        masked = data.copy()
        
        for field in self.config.sensitive_fields or []:
            if field in masked:
                masked[field] = self._mask_value(masked[field])
        
        # 检测并脱敏 PII
        for key, value in masked.items():
            if isinstance(value, str):
                for pii_type, pattern in self.PII_PATTERNS.items():
                    if re.search(pattern, value):
                        masked[key] = re.sub(pattern, '[REDACTED]', value)
        
        return masked
    
    def _mask_value(self, value: str) -> str:
        """脱敏单个值"""
        if not value:
            return value
        
        if len(value) <= 4:
            return '*' * len(value)
        
        return value[:2] + '*' * (len(value) - 4) + value[-2:]
```

### 1.3 合规检查清单

```markdown
# compliance/checklist.md

## 数据保护合规

- [ ] GDPR 合规（欧盟用户数据）
  - [ ] 用户同意管理
  - [ ] 数据可携带权
  - [ ] 被遗忘权实现
  - [ ] DPO（数据保护官）指定

- [ ] CCPA 合规（加州消费者隐私法）
  - [ ] 隐私政策更新
  - [ ] "不要出售我的信息"选项

- [ ] 中国网络安全法
  - [ ] 数据本地化存储
  - [ ] 出境数据评估
  - [ ] 网络安全等级保护

## 平台合规

- [ ] 亚马逊 API 使用政策
  - [ ] 速率限制遵守
  - [ ] 数据使用限制
  - [ ] 品牌使用规范

- [ ] 飞书开放平台政策
  - [ ] 应用审核要求
  - [ ] 用户数据保护
  - [ ] API 调用规范

## 行业合规

- [ ] PCI DSS（支付卡行业数据安全标准）
- [ ] SOC 2 Type II（服务组织控制）
- [ ] ISO 27001（信息安全管理体系）
```

---

## 2. 监控与可观测性

### 2.1 监控指标体系

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           监控指标金字塔                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                              ┌─────────┐                                    │
│                             /  业务指标  \                                   │
│                            / 成功率/成本 /                                  │
│                           ───────────────                                   │
│                          /    应用指标     \                                │
│                         /  延迟/错误率/QPS  \                               │
│                        ───────────────────────                              │
│                       /      系统指标         \                             │
│                      /  CPU/内存/磁盘/网络    \                            │
│                     ───────────────────────────────                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**核心监控指标：**

```yaml
# monitoring/metrics.yaml
metrics:
  # 业务指标
  business:
    - name: task_success_rate
      description: 任务成功率
      formula: success_tasks / total_tasks * 100
      alert_threshold: < 95%
      
    - name: cost_per_task
      description: 单任务成本
      formula: total_api_cost / completed_tasks
      alert_threshold: > $0.50
      
    - name: avg_processing_time
      description: 平均处理时间
      unit: seconds
      alert_threshold: > 300s

  # 应用指标
  application:
    - name: api_latency_p99
      description: API P99 延迟
      unit: ms
      alert_threshold: > 2000ms
      
    - name: error_rate
      description: 错误率
      formula: error_requests / total_requests * 100
      alert_threshold: > 1%
      
    - name: llm_token_usage
      description: LLM Token 使用量
      unit: tokens/minute
      track_by: [model, provider]

  # 系统指标
  system:
    - name: cpu_usage
      alert_threshold: > 80%
    - name: memory_usage
      alert_threshold: > 85%
    - name: disk_usage
      alert_threshold: > 90%
    - name: network_io
      unit: Mbps
```

### 2.2 分布式追踪

```python
# src/observability/tracing.py
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from functools import wraps
import time


def setup_tracing(service_name: str, otlp_endpoint: str):
    """设置 OpenTelemetry 追踪"""
    provider = TracerProvider()
    processor = BatchSpanProcessor(
        OTLPSpanExporter(endpoint=otlp_endpoint)
    )
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    
    return trace.get_tracer(service_name)


def traced_span(span_name: str):
    """
    追踪装饰器
    
    用法:
        @traced_span("crawl_product")
        async def crawl_product(url):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            
            with tracer.start_as_current_span(span_name) as span:
                # 添加属性
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("args.url", str(args[0]) if args else "")
                
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("success", True)
                    return result
                except Exception as e:
                    span.set_attribute("success", False)
                    span.record_exception(e)
                    raise
                finally:
                    duration = time.time() - start_time
                    span.set_attribute("duration_ms", duration * 1000)
        
        return wrapper
    return decorator


# 使用示例
tracer = setup_tracing(
    service_name="agent-crawler",
    otlp_endpoint="http://jaeger:4317"
)

@tracer.start_as_current_span("agent_tool_execution")
async def execute_tool(tool_name: str, parameters: dict):
    """执行工具并追踪"""
    span = trace.get_current_span()
    span.set_attribute("tool.name", tool_name)
    span.set_attribute("tool.parameters", str(parameters))
    
    # ... 执行逻辑
```

### 2.3 日志聚合与分析

```yaml
# logging/loki-config.yaml
# Grafana Loki 配置

auth_enabled: false

server:
  http_listen_port: 3100

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

limits_config:
  retention_period: 720h  # 30 天
  enforce_metric_name: false

# LogQL 查询示例
queries:
  # 查询错误日志
  error_logs: '{level="error"} |= ""'
  
  # 查询特定工具的日志
  tool_logs: '{tool="crawl_taobao"} | json'
  
  # 统计每分钟请求数
  request_rate: sum(rate({job="agent"}[1m])) by (endpoint)
  
  # 查询慢请求
  slow_requests: '{job="agent"} | duration_ms > 5000'
```

### 2.4 告警配置

```yaml
# monitoring/alerts/prometheus_rules.yaml
groups:
  - name: agent_alerts
    interval: 30s
    rules:
      # 高错误率告警
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) 
          / sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "高错误率检测到"
          description: "错误率 {{ $value | humanizePercentage }} 超过阈值 5%"
      
      # API 延迟过高
      - alert: HighAPILatency
        expr: |
          histogram_quantile(0.99, 
            rate(http_request_duration_seconds_bucket[5m])
          ) > 2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "API 延迟过高"
          description: "P99 延迟 {{ $value | humanize }}s 超过阈值 2s"
      
      # LLM API 成本异常
      - alert: HighLLMCost
        expr: |
          sum(rate(llm_token_usage_total[1h])) * 0.00002 > 10
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "LLM API 成本异常"
          description: "每小时成本 ${{ $value }} 超过阈值 $10"
      
      # 任务积压
      - alert: TaskQueueBacklog
        expr: task_queue_size > 1000
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "任务队列积压"
          description: "队列中有 {{ $value }} 个待处理任务"
      
      # 服务不可用
      - alert: ServiceDown
        expr: up{job="agent-bot"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "服务不可用"
          description: "Agent Bot 服务已宕机超过 2 分钟"
```

---

## 3. 性能优化

### 3.1 缓存策略

```python
# src/optimization/cache.py
import asyncio
import hashlib
import json
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
import aioredis


class CacheConfig:
    """缓存配置"""
    # LLM 响应缓存（相同输入返回相同输出）
    LLM_RESPONSE_TTL = timedelta(hours=24)
    # 爬虫数据缓存
    CRAWLER_DATA_TTL = timedelta(hours=1)
    # API 响应缓存
    API_RESPONSE_TTL = timedelta(minutes=30)


class SmartCache:
    """
    智能缓存系统
    
    功能:
    - 多层缓存（内存 + Redis）
    - 缓存预热
    - 缓存失效策略
    - 缓存命中率监控
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        memory_cache_size: int = 1000,
    ):
        self.redis = aioredis.from_url(redis_url)
        self.memory_cache: Dict[str, Any] = {}
        self.max_size = memory_cache_size
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        # 先查内存缓存
        if key in self.memory_cache:
            self.hits += 1
            return self.memory_cache[key]
        
        # 再查 Redis
        data = await self.redis.get(key)
        if data:
            self.hits += 1
            result = json.loads(data)
            # 回写内存缓存
            if len(self.memory_cache) < self.max_size:
                self.memory_cache[key] = result
            return result
        
        self.misses += 1
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: timedelta = CacheConfig.LLM_RESPONSE_TTL,
    ):
        """设置缓存"""
        # 写入内存缓存
        if len(self.memory_cache) >= self.max_size:
            # 简单 LRU：删除第一个
            self.memory_cache.pop(next(iter(self.memory_cache)))
        self.memory_cache[key] = value
        
        # 写入 Redis
        await self.redis.setex(
            key,
            int(ttl.total_seconds()),
            json.dumps(value)
        )
    
    def get_hit_rate(self) -> float:
        """获取缓存命中率"""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total


# 使用装饰器实现自动缓存
def cached(ttl: timedelta = CacheConfig.LLM_RESPONSE_TTL):
    """缓存装饰器"""
    cache = SmartCache()
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = cache._generate_key(func.__name__, *args, **kwargs)
            
            cached_result = await cache.get(key)
            if cached_result is not None:
                return cached_result
            
            result = await func(*args, **kwargs)
            await cache.set(key, result, ttl)
            return result
        
        return wrapper
    return decorator


# 使用示例
@cached(ttl=timedelta(hours=24))
async def call_llm_api(prompt: str, model: str) -> str:
    """调用 LLM API（带缓存）"""
    # ... 实际 API 调用
    pass
```

### 3.2 并发控制

```python
# src/optimization/concurrency.py
import asyncio
from typing import List, Any, Callable
from dataclasses import dataclass
import time


@dataclass
class RateLimitConfig:
    """速率限制配置"""
    calls_per_second: float = 10
    burst_size: int = 20
    retry_delay: float = 1.0


class RateLimiter:
    """
    速率限制器
    
    实现令牌桶算法
    """
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.tokens = config.burst_size
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """获取令牌"""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            
            # 补充令牌
            self.tokens = min(
                self.config.burst_size,
                self.tokens + elapsed * self.config.calls_per_second
            )
            self.last_update = now
            
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.config.calls_per_second
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1


class ConcurrentExecutor:
    """
    并发执行器
    
    功能:
    - 并发数控制
    - 速率限制
    - 错误重试
    - 超时控制
    """
    
    def __init__(
        self,
        max_concurrency: int = 10,
        rate_limiter: RateLimiter = None,
        max_retries: int = 3,
        timeout: float = 30.0,
    ):
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.rate_limiter = rate_limiter
        self.max_retries = max_retries
        self.timeout = timeout
    
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs,
    ) -> Any:
        """带重试的执行"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                last_exception = TimeoutError(f"执行超时 ({self.timeout}s)")
            except Exception as e:
                last_exception = e
            
            if attempt < self.max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # 指数退避
        
        raise last_exception
    
    async def execute_batch(
        self,
        tasks: List[Callable],
        batch_size: int = 10,
    ) -> List[Any]:
        """批量执行任务"""
        results = []
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            
            async def run_task(func):
                async with self.semaphore:
                    if self.rate_limiter:
                        await self.rate_limiter.acquire()
                    return await self.execute_with_retry(func)
            
            batch_results = await asyncio.gather(
                *[run_task(task) for task in batch],
                return_exceptions=True
            )
            
            results.extend(batch_results)
        
        return results
```

### 3.3 数据库优化

```sql
-- database/optimization.sql

-- 1. 创建索引优化查询
CREATE INDEX IF NOT EXISTS idx_products_status 
ON products(status);

CREATE INDEX IF NOT EXISTS idx_products_crawl_time 
ON products(crawl_time DESC);

CREATE INDEX IF NOT EXISTS idx_reviews_status_created 
ON reviews(status, created_at DESC);

-- 2. 分区表（大数据量场景）
CREATE TABLE products_partitioned (
    LIKE products INCLUDING ALL
) PARTITION BY RANGE (crawl_time);

-- 按月分区
CREATE TABLE products_2024_01 
PARTITION OF products_partitioned
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- 3. 物化视图加速统计查询
CREATE MATERIALIZED VIEW mv_daily_stats AS
SELECT 
    DATE(crawl_time) as date,
    platform,
    COUNT(*) as product_count,
    AVG(price) as avg_price,
    SUM(sales_count) as total_sales
FROM products
GROUP BY DATE(crawl_time), platform;

-- 定期刷新
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_stats;

-- 4. 查询优化示例
-- ❌ 慢查询：全表扫描
SELECT * FROM products 
WHERE EXTRACT(DAY FROM crawl_time) = 15;

-- ✅ 优化后：使用索引
SELECT * FROM products 
WHERE crawl_time >= '2024-01-15' 
  AND crawl_time < '2024-01-16';
```

---

## 4. 测试与质量保证

### 4.1 测试策略

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           测试金字塔                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                              ┌─────────┐                                    │
│                             /  E2E 测试  \                                  │
│                            /   (5%)     /                                   │
│                           ─────────────                                     │
│                          /  集成测试    \                                   │
│                         /    (20%)     /                                    │
│                        ─────────────────                                    │
│                       /    单元测试      \                                  │
│                      /     (75%)        /                                   │
│                     ──────────────────────                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 单元测试示例

```python
# tests/unit/test_crawler_tools.py
import pytest
from unittest.mock import AsyncMock, patch
from src.agents.tools.crawler_tools import TaobaoCrawlerTool, ToolResult


class TestTaobaoCrawlerTool:
    """淘宝爬虫工具测试"""
    
    @pytest.fixture
    def crawler_tool(self):
        return TaobaoCrawlerTool()
    
    @pytest.mark.asyncio
    async def test_successful_crawl(self, crawler_tool):
        """测试成功爬取"""
        mock_product = AsyncMock()
        mock_product.title = "测试商品"
        mock_product.price = "99.99"
        mock_product.images = ["http://example.com/img.jpg"]
        
        with patch.object(crawler_tool, '_mock_crawler') as mock:
            mock.fetch_product.return_value = mock_product
            
            result = await crawler_tool.execute(
                url="https://item.taobao.com/test.htm"
            )
            
            assert isinstance(result, ToolResult)
            assert result.success is True
            assert result.data["title"] == "测试商品"
            assert result.data["price"] == "99.99"
    
    @pytest.mark.asyncio
    async def test_invalid_url(self, crawler_tool):
        """测试无效 URL"""
        result = await crawler_tool.execute(url="invalid_url")
        
        assert result.success is False
        assert "URL" in result.error
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, crawler_tool):
        """测试速率限制"""
        import time
        
        start = time.time()
        
        # 连续调用 10 次
        for _ in range(10):
            await crawler_tool.execute(url="https://item.taobao.com/test.htm")
        
        elapsed = time.time() - start
        
        # 验证有适当的延迟（假设限制 1 次/秒）
        assert elapsed >= 9.0  # 至少 9 秒延迟


# tests/unit/test_optimizer_tools.py
class TestProductOptimizerTool:
    """商品优化工具测试"""
    
    @pytest.fixture
    def optimizer_tool(self):
        return ProductOptimizerTool()
    
    @pytest.mark.asyncio
    async def test_optimize_product(self, optimizer_tool):
        """测试商品优化"""
        product_data = {
            "title": "夏季透气运动鞋",
            "description": "这是一款透气舒适的运动鞋...",
            "price": "199",
        }
        
        result = await optimizer_tool.execute(
            product_data=product_data,
            target_market="US"
        )
        
        assert result.success is True
        assert "title" in result.data
        assert "bullet_points" in result.data
        assert len(result.data["bullet_points"]) == 5
```

### 4.3 集成测试

```python
# tests/integration/test_feishu_sync.py
import pytest
import os
from src.feishu.bitable_client import FeishuBitableClient


@pytest.mark.integration
class TestFeishuIntegration:
    """飞书集成测试"""
    
    @pytest.fixture
    def client(self):
        return FeishuBitableClient(
            app_id=os.getenv("TEST_FEISHU_APP_ID"),
            app_secret=os.getenv("TEST_FEISHU_APP_SECRET"),
            app_token=os.getenv("TEST_FEISHU_APP_TOKEN"),
        )
    
    def test_get_tables(self, client):
        """测试获取数据表列表"""
        tables = client.get_tables()
        
        assert isinstance(tables, list)
        assert len(tables) > 0
        assert "id" in tables[0]
        assert "name" in tables[0]
    
    def test_create_and_delete_record(self, client):
        """测试创建和删除记录"""
        table_id = os.getenv("TEST_TABLE_ID")
        
        # 创建
        record = client.create_record(
            table_id=table_id,
            fields={"商品名称": "测试商品", "价格": 99.99}
        )
        
        assert record.record_id is not None
        assert record.fields["商品名称"] == "测试商品"
        
        # 删除
        deleted = client.delete_record(table_id, record.record_id)
        assert deleted is True


# tests/integration/test_llm_integration.py
class TestLLMIntegration:
    """LLM 集成测试"""
    
    @pytest.mark.asyncio
    async def test_tool_calling(self):
        """测试工具调用解析"""
        llm = LLMIntegration(provider="anthropic")
        
        messages = [{"role": "user", "content": "帮我采集这个商品"}]
        tools = [
            {
                "name": "crawl_taobao",
                "description": "采集淘宝商品",
                "input_schema": {...}
            }
        ]
        
        response = await llm.chat_with_tools(
            messages=messages,
            tools=tools,
            system_prompt="你是一个电商助手"
        )
        
        # 验证返回格式
        assert "type" in response
        assert response["type"] in ["text", "tool_call"]
```

### 4.4 E2E 测试

```python
# tests/e2e/test_full_pipeline.py
import pytest
import asyncio
from src.agents.orchestrator import AgentOrchestrator


@pytest.mark.e2e
class TestFullPipeline:
    """端到端全流程测试"""
    
    @pytest.fixture
    def orchestrator(self):
        return AgentOrchestrator(config={
            "feishu": {
                "app_id": os.getenv("FEISHU_APP_ID"),
                "app_secret": os.getenv("FEISHU_APP_SECRET"),
                "app_token": os.getenv("FEISHU_APP_TOKEN"),
            }
        })
    
    @pytest.mark.asyncio
    async def test_crawl_optimize_sync_pipeline(self, orchestrator):
        """测试完整流程：采集 → 优化 → 同步"""
        instruction = """
        请帮我完成以下任务：
        1. 采集这个淘宝商品：https://item.taobao.com/xxx.htm
        2. 优化商品信息，目标市场美国
        3. 同步到飞书表格
        """
        
        context = await orchestrator.execute_task(instruction)
        
        # 验证流程完成
        assert context.status == "completed"
        assert len(context.results) >= 3  # 至少 3 个工具执行
        
        # 验证每个步骤
        crawl_result = context.results[0]
        assert crawl_result.success is True
        assert "title" in crawl_result.data
        
        optimize_result = context.results[1]
        assert optimize_result.success is True
        assert "bullet_points" in optimize_result.data
        
        sync_result = context.results[2]
        assert sync_result.success is True
```

### 4.5 测试覆盖率要求

```yaml
# pyproject.toml
[tool.pytest]
addopts = """
  --cov=src
  --cov-report=html
  --cov-report=term-missing
  --cov-fail-under=80
"""

# 覆盖率要求
coverage:
  run:
    branch: true
  report:
    exclude_lines:
      - pragma: no cover
      - def __repr__
      - raise NotImplementedError
    fail_under: 80
    show_missing: true

# 最低要求:
# - 单元测试覆盖率：>= 80%
# - 关键模块覆盖率：>= 90%
# - 集成测试：所有 API 端点
# - E2E 测试：核心业务流程 100%
```

---

## 5. 运维与部署

### 5.1 CI/CD 流水线

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # 代码质量检查
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install ruff mypy
          pip install -e .
      
      - name: Run linter
        run: ruff check src/
      
      - name: Run type checker
        run: mypy src/

  # 单元测试
  test:
    runs-on: ubuntu-latest
    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install pytest pytest-cov pytest-asyncio
          pip install -e .
      
      - name: Run tests
        run: pytest tests/unit --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  # 集成测试
  integration-test:
    runs-on: ubuntu-latest
    needs: [test]
    environment: staging
    steps:
      - uses: actions/checkout@v3
      
      - name: Run integration tests
        env:
          FEISHU_APP_ID: ${{ secrets.TEST_FEISHU_APP_ID }}
          FEISHU_APP_SECRET: ${{ secrets.TEST_FEISHU_APP_SECRET }}
        run: |
          pytest tests/integration -v

  # 构建 Docker 镜像
  build:
    runs-on: ubuntu-latest
    needs: [lint, integration-test]
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t agent-bot:${{ github.sha }} .
      
      - name: Push to registry
        run: |
          docker tag agent-bot:${{ github.sha }} registry.example.com/agent-bot:latest
          docker push registry.example.com/agent-bot:latest

  # 部署到生产
  deploy:
    runs-on: ubuntu-latest
    needs: [build]
    environment: production
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          kubectl set image deployment/agent-bot \
            agent-bot=registry.example.com/agent-bot:${{ github.sha }}
```

### 5.2 健康检查端点

```python
# src/health.py
from aiohttp import web
import asyncio
import time
from typing import Dict, Any


class HealthCheckHandler:
    """健康检查处理器"""
    
    def __init__(self, dependencies: Dict[str, Any]):
        self.dependencies = dependencies
        self.start_time = time.time()
    
    async def handle_liveness(self, request: web.Request) -> web.Response:
        """
        存活探针
        
        检查服务是否运行
        """
        return web.json_response({
            "status": "alive",
            "uptime_seconds": time.time() - self.start_time,
        })
    
    async def handle_readiness(self, request: web.Request) -> web.Response:
        """
        就绪探针
        
        检查服务是否准备好接收流量
        """
        checks = {}
        all_healthy = True
        
        # 检查数据库连接
        checks["database"] = await self._check_database()
        
        # 检查 Redis 连接
        checks["redis"] = await self._check_redis()
        
        # 检查 LLM API 可达性
        checks["llm_api"] = await self._check_llm_api()
        
        # 检查飞书 API 可达性
        checks["feishu_api"] = await self._check_feishu_api()
        
        all_healthy = all(v.get("healthy") for v in checks.values())
        
        status_code = 200 if all_healthy else 503
        
        return web.json_response({
            "status": "ready" if all_healthy else "not_ready",
            "checks": checks,
        }, status=status_code)
    
    async def _check_database(self) -> Dict[str, Any]:
        """检查数据库"""
        try:
            # 执行简单查询
            await asyncio.wait_for(
                self.dependencies["db"].execute("SELECT 1"),
                timeout=5.0
            )
            return {"healthy": True}
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def _check_redis(self) -> Dict[str, Any]:
        """检查 Redis"""
        try:
            await self.dependencies["redis"].ping()
            return {"healthy": True}
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def _check_llm_api(self) -> Dict[str, Any]:
        """检查 LLM API"""
        try:
            # 简单 API 调用
            await asyncio.wait_for(
                self.dependencies["llm"].client.models.list(),
                timeout=10.0
            )
            return {"healthy": True}
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def _check_feishu_api(self) -> Dict[str, Any]:
        """检查飞书 API"""
        try:
            await asyncio.wait_for(
                self.dependencies["feishu"].get_tables(),
                timeout=10.0
            )
            return {"healthy": True}
        except Exception as e:
            return {"healthy": False, "error": str(e)}


def setup_health_endpoints(app: web.Application, dependencies: Dict[str, Any]):
    """设置健康检查端点"""
    handler = HealthCheckHandler(dependencies)
    
    app.router.add_get("/health/live", handler.handle_liveness)
    app.router.add_get("/health/ready", handler.handle_readiness)
```

### 5.3 Kubernetes 部署配置

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-bot
  labels:
    app: agent-bot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent-bot
  template:
    metadata:
      labels:
        app: agent-bot
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
    spec:
      containers:
        - name: agent-bot
          image: registry.example.com/agent-bot:latest
          ports:
            - containerPort: 8080
          env:
            - name: ANTHROPIC_API_KEY
              valueFrom:
                secretKeyRef:
                  name: agent-secrets
                  key: anthropic-api-key
            - name: FEISHU_APP_ID
              valueFrom:
                secretKeyRef:
                  name: agent-secrets
                  key: feishu-app-id
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
      imagePullSecrets:
        - name: registry-secret

---
apiVersion: v1
kind: Service
metadata:
  name: agent-bot
spec:
  selector:
    app: agent-bot
  ports:
    - port: 80
      targetPort: 8080
  type: ClusterIP

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: agent-bot-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: agent-bot
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

---

## 6. 变更管理

### 6.1 版本控制策略

```markdown
# CHANGELOG.md 格式

## [1.2.0] - 2024-01-15

### Added
- 新增 1688 平台爬虫支持
- 新增关键词研究工具
- 新增飞书机器人命令帮助

### Changed
- 优化 LLM 缓存策略，命中率提升至 65%
- 改进错误处理机制
- 更新依赖版本

### Fixed
- 修复淘宝爬虫图片提取失败问题
- 修复飞书同步时区错误
- 修复内存泄漏问题

### Security
- 升级 cryptography 库修复安全漏洞
- 实施密钥轮换机制

### Breaking Changes
- `crawl_taobao` 工具参数变更：`max_images` 默认值从 20 改为 10
```

### 6.2 回滚策略

```yaml
# k8s/rollback.yaml
# 自动回滚配置

apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-bot
spec:
  rollbackTo:
    revision: 2  # 回滚到上一个稳定版本
  
  # 渐进式发布策略
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  
  # 金丝雀发布注解
  annotations:
    canary.weight: "0"  # 初始 0% 流量
    canary.step: "0"    # 发布步骤

---
# 回滚检查脚本
# scripts/health_check.sh
#!/bin/bash

set -e

ENDPOINT="${1:-http://localhost/health/ready}"
MAX_RETRIES=30
RETRY_INTERVAL=10

echo "Checking health: $ENDPOINT"

for i in $(seq 1 $MAX_RETRIES); do
    response=$(curl -s -o /dev/null -w "%{http_code}" "$ENDPOINT")
    
    if [ "$response" = "200" ]; then
        echo "✓ Health check passed (attempt $i)"
        exit 0
    fi
    
    echo "✗ Health check failed (attempt $i, status: $response)"
    sleep $RETRY_INTERVAL
done

echo "✗ Health check failed after $MAX_RETRIES attempts"
exit 1
```

---

## 7. 成本优化

### 7.1 LLM 成本监控

```python
# src/optimization/cost_tracker.py
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List
import json


@dataclass
class TokenUsage:
    """Token 使用记录"""
    timestamp: datetime
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost: float
    task_id: str = ""


class CostTracker:
    """
    成本追踪器
    
    功能:
    - 实时成本计算
    - 预算告警
    - 成本分析
    - 优化建议
    """
    
    # 模型定价（每 1000 tokens）
    PRICING = {
        "claude-sonnet-4-20250514": {"input": 0.003, "output": 0.015},
        "claude-opus-20240229": {"input": 0.015, "output": 0.075},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    }
    
    def __init__(self, budget_limit: float = 1000.0):
        self.budget_limit = budget_limit
        self.usage_records: List[TokenUsage] = []
        self.daily_budget = budget_limit / 30
    
    def record_usage(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        task_id: str = "",
    ):
        """记录 Token 使用"""
        pricing = self.PRICING.get(model, {"input": 0, "output": 0})
        
        cost = (
            prompt_tokens * pricing["input"] + 
            completion_tokens * pricing["output"]
        ) / 1000
        
        record = TokenUsage(
            timestamp=datetime.now(),
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost=cost,
            task_id=task_id,
        )
        
        self.usage_records.append(record)
        
        # 检查预算
        if self.get_today_cost() > self.daily_budget:
            self.send_budget_alert()
    
    def get_today_cost(self) -> float:
        """获取今日成本"""
        today = datetime.now().date()
        return sum(
            r.cost for r in self.usage_records
            if r.timestamp.date() == today
        )
    
    def get_cost_by_model(self) -> Dict[str, float]:
        """按模型统计成本"""
        costs: Dict[str, float] = {}
        for record in self.usage_records:
            costs[record.model] = costs.get(record.model, 0) + record.cost
        return costs
    
    def get_optimization_suggestions(self) -> List[str]:
        """获取优化建议"""
        suggestions = []
        
        # 分析模型使用
        model_costs = self.get_cost_by_model()
        
        # 如果使用过多昂贵模型
        if model_costs.get("claude-opus-20240229", 0) > 100:
            suggestions.append(
                "考虑将部分任务迁移到 Claude Sonnet 以降低成本"
            )
        
        # 检查缓存命中率
        # ...
        
        return suggestions
    
    def send_budget_alert(self):
        """发送预算告警"""
        today_cost = self.get_today_cost()
        alert_message = f"""
⚠️ 预算告警

今日成本：${today_cost:.2f}
日预算：${self.daily_budget:.2f}
使用率：{today_cost / self.daily_budget * 100:.1f}%

建议:
1. 检查是否有不必要的 LLM 调用
2. 考虑使用更便宜的模型
3. 提高缓存命中率
        """
        # 发送告警（飞书/邮件/短信）
        print(alert_message)
```

### 7.2 成本优化建议

```markdown
# optimization/cost_tips.md

## LLM 成本优化

### 1. 模型选择策略

| 任务类型 | 推荐模型 | 成本节省 |
|----------|----------|----------|
| 简单分类 | GPT-3.5-turbo | 80% vs GPT-4 |
| 文案生成 | Claude Sonnet | 50% vs Claude Opus |
| 复杂推理 | Claude Opus | - |
| 代码生成 | GPT-4-turbo | - |

### 2. 缓存策略

- 实现 LLM 响应缓存（相同 prompt 返回相同结果）
- 缓存 TTL：24 小时
- 预期缓存命中率：60-70%
- 成本节省：~65%

### 3. Prompt 优化

- 精简 system prompt
- 使用 few-shot 而非 zero-shot
- 限制 max_tokens

### 4. 批量处理

- 合并多个小任务为一批
- 减少 API 调用次数
- 利用 batch API（如有）

## 基础设施成本

### 1. 容器优化

- 使用 spot 实例（节省 70%）
- 自动缩容到 0（无流量时）
- 选择合适实例类型

### 2. 数据库优化

- 使用连接池
- 实施查询缓存
- 定期清理旧数据

### 3. 代理成本

- 使用代理池轮换
- 避免请求失败重试过多
- 选择性价比高的代理服务商
```

---

## 8. 知识库与文档

### 8.1 文档结构

```
docs/
├── README.md                    # 项目概述
├── getting-started.md           # 快速开始
├── architecture/
│   ├── overview.md             # 架构概述
│   ├── components.md           # 组件说明
│   └── data-flow.md            # 数据流
├── user-guide/
│   ├── installation.md         # 安装指南
│   ├── configuration.md        # 配置说明
│   ├── usage.md                # 使用手册
│   └── troubleshooting.md      # 故障排查
├── developer-guide/
│   ├── code-style.md           # 代码规范
│   ├── testing.md              # 测试指南
│   ├── contributing.md         # 贡献指南
│   └── api-reference/          # API 文档
├── operations/
│   ├── deployment.md           # 部署指南
│   ├── monitoring.md           # 监控指南
│   ├── backup-restore.md       # 备份恢复
│   └── incident-response.md    # 应急响应
├── knowledge-base/
│   ├── faq.md                  # 常见问题
│   ├── best-practices.md       # 最佳实践
│   └── case-studies/           # 案例研究
└── changelog.md                # 变更日志
```

### 8.2 运行手册模板

```markdown
# operations/runbook.md

## 日常运维检查清单

### 每日检查

- [ ] 检查服务健康状态
  ```bash
  curl http://agent-bot/health/ready
  ```

- [ ] 检查错误日志
  ```bash
  grep "ERROR" logs/agent.log | tail -50
  ```

- [ ] 检查任务队列
  ```bash
  redis-cli LLEN task_queue
  ```

- [ ] 检查成本消耗
  - 查看成本仪表盘
  - 确认未超预算

### 每周检查

- [ ] 检查系统更新
  ```bash
  uv sync --latest
  ```

- [ ] 检查证书有效期
  ```bash
  openssl x509 -in cert.pem -noout -dates
  ```

- [ ] 备份数据验证
  - 恢复测试备份
  - 验证数据完整性

- [ ] 性能指标审查
  - P99 延迟趋势
  - 错误率趋势
  - 缓存命中率

### 每月检查

- [ ] 密钥轮换
- [ ] 依赖安全审计
- [ ] 容量规划审查
- [ ] 灾难恢复演练
```

### 8.3 故障排查指南

```markdown
# operations/troubleshooting.md

## 常见问题排查

### 问题：任务执行失败

**症状**: 任务状态显示 failed

**排查步骤**:

1. 查看任务日志
   ```bash
   kubectl logs deployment/agent-bot | grep "task_id=xxx"
   ```

2. 检查依赖服务
   ```bash
   # 检查数据库
   psql -h db-host -U user -c "SELECT 1"
   
   # 检查 Redis
   redis-cli ping
   
   # 检查 LLM API
   curl -I https://api.anthropic.com
   ```

3. 检查资源使用
   ```bash
   kubectl top pod agent-bot-xxx
   ```

**常见原因**:
- LLM API 限流 → 等待或升级配额
- 数据库连接超时 → 检查网络和连接池
- 内存不足 → 增加资源限制

### 问题：飞书同步失败

**症状**: sync_to_feishu 工具返回错误

**排查步骤**:

1. 验证 Token 有效性
   ```bash
   curl -X GET "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
     -H "Content-Type: application/json" \
     -d '{"app_id":"xxx","app_secret":"xxx"}'
   ```

2. 检查权限配置
   - 登录飞书开放平台
   - 确认应用有「多维表格」权限

3. 检查表 ID 配置
   - 确认 config/feishu.yaml 中 table_id 正确

**解决方案**:
- Token 过期 → 等待自动刷新或重启服务
- 权限不足 → 联系管理员添加权限
- 表 ID 错误 → 更新配置
```

---

## 附录：完整检查清单

### 上线前检查清单

```markdown
# pre-launch-checklist.md

## 安全
- [ ] 所有敏感配置已移至密钥管理服务
- [ ] 实施了最小权限原则
- [ ] 启用了审计日志
- [ ] 完成了安全扫描

## 性能
- [ ] 缓存命中率 > 60%
- [ ] P99 延迟 < 2s
- [ ] 并发测试通过
- [ ] 负载测试通过

## 可靠性
- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试全部通过
- [ ] E2E 测试全部通过
- [ ] 故障恢复测试通过

## 监控
- [ ] 关键指标已配置
- [ ] 告警规则已设置
- [ ] 仪表盘已创建
- [ ] 日志聚合正常

## 文档
- [ ] 用户文档完成
- [ ] 运维手册完成
- [ ] API 文档完成
- [ ] 故障排查指南完成

## 合规
- [ ] 隐私政策审查通过
- [ ] 数据保护合规审查通过
- [ ] 第三方服务合规审查通过
```

---

*文档版本：0.1.0 | 最后更新：2026-03-12*
