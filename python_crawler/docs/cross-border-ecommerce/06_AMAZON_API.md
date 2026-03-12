# Amazon SP-API 集成指南

> **跨境电商全工作流系统** - Amazon Selling Partner API 完整集成方案

**版本**: v1.0.0
**更新时间**: 2026-03-12

---

## 目录

1. [SP-API 简介](#sp-api-简介)
2. [开发者注册](#开发者注册)
3. [认证流程](#认证流程)
4. [核心 API](#核心-api)
5. [批量操作](#批量操作)
6. [最佳实践](#最佳实践)

---

## SP-API 简介

### 什么是 SP-API

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Amazon Selling Partner API                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  SP-API 是 Amazon 的官方 API，允许第三方应用以编程方式访问 Amazon       │
│  卖家账户数据和管理操作。                                               │
│                                                                         │
│  核心能力:                                                               │
│  • 商品管理 (目录、价格、库存)                                          │
│  • 订单管理 (报告、状态)                                                │
│  • 广告管理 (Sponsored Products/Brands)                                │
│  • 财务管理 (付款报告)                                                  │
│  • 数据报告 (库存、销售、流量)                                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### API 覆盖范围

| API 类别 | 主要功能 |
|----------|----------|
| **Catalog API** | 商品搜索、分类浏览 |
| **Listings API** | 创建/更新商品信息 |
| **Orders API** | 订单获取、状态更新 |
| **Inventory API** | 库存管理、补货建议 |
| **Pricing API** | 价格更新、竞争价格 |
| **Fulfillment API** | FBA 库存、入舱 |
| **Merchant API** | 报告下载、数据导出 |
| **A+ Content** | A+ 页面管理 |
| **Ads API** | 广告活动管理 |

---

## 开发者注册

### 注册流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      开发者注册流程                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Step 1: 注册开发者账号                                                  │
│    ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  https://developer.amazonservices.com                           │   │
│  │  • 注册卖家开发者账号                                            │   │
│  │  • 获取 Client ID 和 Client Secret                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│    │                                                                    │
│    ▼                                                                    │
│  Step 2: 创建应用                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  • 应用名称: E-commerce Automation System                       │   │
│  │  • 应用类型: 自建应用 (Self-Hosted)                              │   │
│  │  • 回调 URL: https://your-domain.com/callback                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│    │                                                                    │
│    ▼                                                                    │
│  Step 3: 申请权限                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  必需权限:                                                       │   │
│  │  • read_catalog_data                                           │   │
│  │  • write_catalog_data                                          │   │
│  │  • read_orders_data                                            │   │
│  │  • read_inventory_data                                         │   │
│  │  • write_inventory_data                                        │   │
│  │  • read_pricing_data                                           │   │
│  │  • write_pricing_data                                          │   │
│  │  • read_financial_data                                         │   │
│  │  • read_advertising_data                                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│    │                                                                    │
│    ▼                                                                    │
│  Step 4: LWA 授权                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  • 使用 Login with Amazon (LWA) 进行授权                         │   │
│  │  • 获取 refresh_token                                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│    │                                                                    │
│    ▼                                                                    │
│  Step 5: 配置卖家账户                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  • 在卖家中心授权应用                                             │   │
│  │  • 获取 Seller ID                                                │   │
│  │  • 配置 Marketplace ID                                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 配置参数

```bash
# .env - Amazon API 配置

# ========== 应用凭证 ==========
AMAZON_SP_API_CLIENT_ID=amzn1.application-oa2-client.xxx
AMAZON_SP_API_CLIENT_SECRET=amzn1.oa2-csg.xxx

# ========== 授权凭证 ==========
AMAZON_SP_API_REFRESH_TOKEN=Atzr|xxx
AMAZON_SELLER_ID=A2NXXXXXX
AMAZON_MARKETPLACE_ID=ATVPDKIKX0DER  # US

# ========== 其他市场 ==========
# UK: A1F83G8C2ARO7P
# DE: A1PA6795UKMFR9
# FR: A13V1IB3VIYZZH
# IT: APJ6JRA9NG5V4
# ES: A1RKKUPIHCS9HS
# JP: A1VC38T7YXB5NI
# CA: A2EUQ1WTGCTBG2
# AU: A39IBJ37TRQ1BG

# ========== API 端点 ==========
AMAZON_SP_API_ENDPOINT=https://sellingpartnerapi-na.amazon.com
# 欧洲区: https://sellingpartnerapi-eu.amazon.com
# 远东区: https://sellingpartnerapi-fe.amazon.com

# ========== 数据端点 ==========
AMAZON_SP_API_DATA_ENDPOINT=https://sellingpartnerapi-na.amazon.com
```

---

## 认证流程

### OAuth 2.0 流程

```python
# backend/integrations/amazon/auth.py

import requests
import base64
import hashlib
import secrets
from datetime import datetime, timedelta

class AmazonSPAuth:
    """Amazon SP-API 认证管理器"""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = None
        self.token_expires_at = None

        # API 端点
        self.auth_url = "https://api.amazon.com/auth/o2/token"

    def get_access_token(self) -> str:
        """获取有效的访问令牌"""
        # 如果令牌仍然有效，直接返回
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token

        # 刷新令牌
        return self._refresh_token()

    def _refresh_token(self) -> str:
        """刷新访问令牌"""
        headers = {
            "Content-Type": "application/json",
        }

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        response = requests.post(
            self.auth_url,
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()

        result = response.json()
        self.access_token = result["access_token"]

        # 设置过期时间（提前5分钟刷新）
        expires_in = result.get("expires_in", 3600)
        self.token_expires_at = datetime.now() + timedelta(
            seconds=expires_in - 300
        )

        return self.access_token

    def get_auth_headers(self) -> dict:
        """获取认证头"""
        token = self.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "x-amz-access-token": token,  # 某些端点需要
        }

# 使用示例
auth = AmazonSPAuth(
    client_id=os.getenv("AMAZON_SP_API_CLIENT_ID"),
    client_secret=os.getenv("AMAZON_SP_API_CLIENT_SECRET"),
    refresh_token=os.getenv("AMAZON_SP_API_REFRESH_TOKEN")
)

headers = auth.get_auth_headers()
```

### 请求签名

```python
# backend/integrations/amazon/signature.py

import hashlib
import hmac
import urllib.parse
from datetime import datetime

def sign_request(
    method: str,
    url: str,
    params: dict,
    headers: dict,
    aws_access_key: str,
    aws_secret_key: str,
    region: str = "us-east-1"
) -> dict:
    """
    AWS Signature V4 签名

    SP-API 使用 AWS Signature V4 进行请求签名
    """

    # 1. 创建规范请求
    canonical_uri = urllib.parse.urlparse(url).path
    canonical_querystring = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

    canonical_headers = ""
    signed_headers = ""
    for key in sorted(headers.keys()):
        lower_key = key.lower()
        canonical_headers += f"{lower_key}:{headers[key]}\n"
        if signed_headers:
            signed_headers += ";"
        signed_headers += lower_key

    payload_hash = hashlib.sha256("".encode()).hexdigest()

    canonical_request = "\n".join([
        method,
        canonical_uri,
        canonical_querystring,
        canonical_headers,
        signed_headers,
        payload_hash
    ])

    # 2. 创建待签字符串
    algorithm = "AWS4-HMAC-SHA256"
    amz_date = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    date_stamp = amz_date[:8]
    credential_scope = f"{date_stamp}/{region}/execute-api/aws4_request"

    string_to_sign = "\n".join([
        algorithm,
        amz_date,
        credential_scope,
        hashlib.sha256(canonical_request.encode()).hexdigest()
    ])

    # 3. 计算签名
    def sign(key, msg):
        return hmac.new(key, msg.encode(), hashlib.sha256).digest()

    k_date = sign(("AWS4" + aws_secret_key).encode(), date_stamp)
    k_region = sign(k_date, region)
    k_service = sign(k_region, "execute-api")
    k_signing = sign(k_service, "aws4_request")

    signature = hmac.new(
        k_signing,
        string_to_sign.encode(),
        hashlib.sha256
    ).hexdigest()

    # 4. 添加签名头
    authorization_header = (
        f"{algorithm} Credential={aws_access_key}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )

    headers["Authorization"] = authorization_header
    headers["x-amz-date"] = amz_date

    return headers
```

---

## 核心 API

### 1. Listings API

#### 创建/更新商品

```python
# backend/integrations/amazon/listings.py

from typing import List, Dict
import httpx

class AmazonListingsAPI:
    """Amazon Listings API 封装"""

    def __init__(self, auth: AmazonSPAuth, marketplace_id: str):
        self.auth = auth
        self.marketplace_id = marketplace_id
        self.base_url = "https://sellingpartnerapi-na.amazon.com"

    async def create_listing(
        self,
        seller_sku: str,
        product_data: dict
    ) -> dict:
        """创建商品上架"""

        url = f"{self.base_url}/listings/2021-08-01/items/{self.marketplace_id}/{seller_sku}"

        headers = self.auth.get_auth_headers()
        headers["Content-Type"] = "application/json"

        payload = {
            "productType": product_data["product_type"],
            "patches": [
                {
                    "op": "replace",
                    "path": "/attributes",
                    "value": product_data["attributes"]
                }
            ],
            "requirements": "LISTING"  # LISTING, OFFER, LISTING_OFFER
        }

        async with httpx.AsyncClient() as client:
            response = await client.put(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

    async def get_listing(self, seller_sku: str) -> dict:
        """获取商品信息"""

        url = f"{self.base_url}/listings/2021-08-01/items/{self.marketplace_id}/{seller_sku}"

        headers = self.auth.get_auth_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()

    async def patch_listing(
        self,
        seller_sku: str,
        patches: List[dict]
    ) -> dict:
        """部分更新商品"""

        url = f"{self.base_url}/listings/2021-08-01/items/{self.marketplace_id}/{seller_sku}"

        headers = self.auth.get_auth_headers()
        headers["Content-Type"] = "application/json"

        payload = {"patches": patches}

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

    async def delete_listing(self, seller_sku: str) -> dict:
        """删除商品上架"""

        url = f"{self.base_url}/listings/2021-08-01/items/{self.marketplace_id}/{seller_sku}"

        headers = self.auth.get_auth_headers()

        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
```

#### 批量操作

```python
async def batch_create_listings(
    self,
    listings: List[dict]
) -> dict:
    """批量创建商品上架

    SP-API 本身不支持批量，这里使用并发请求模拟批量操作
    """

    tasks = [
        self.create_listing(item["seller_sku"], item)
        for item in listings
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    success_count = sum(1 for r in results if not isinstance(r, Exception))
    failed_count = len(results) - success_count

    return {
        "total": len(listings),
        "success": success_count,
        "failed": failed_count,
        "results": results
    }
```

### 2. Inventory API

```python
# backend/integrations/amazon/inventory.py

class AmazonInventoryAPI:
    """Amazon Inventory API 封装"""

    def __init__(self, auth: AmazonSPAuth):
        self.auth = auth
        self.base_url = "https://sellingpartnerapi-na.amazon.com"

    async def get_inventory_summary(
        self,
        granularity_type: str = "Marketplace",
        granularity_id: str = None
    ) -> dict:
        """获取库存摘要"""

        url = f"{self.base_url}/inventory/management/v1/inventorySummary"

        headers = self.auth.get_auth_headers()
        params = {
            "granularityType": granularity_type,
            "granularityId": granularity_id or self.marketplace_id,
            "marketplaceIds": self.marketplace_id
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

    async def update_inventory(
        self,
        seller_sku: str,
        quantity: int,
        fulfillment_type: str = "AFN_MFN"
    ) -> dict:
        """更新库存"""

        url = f"{self.base_url}/inventory/management/v1/inventory"

        headers = self.auth.get_auth_headers()
        headers["Content-Type"] = "application/json"

        payload = {
            "messages": [
                {
                    "messageId": str(uuid.uuid4()),
                    "messageType": "InventoryUpdate",
                    "payload": {
                        "inventoryUpdate": {
                            "seller_sku": seller_sku,
                            "quantity": quantity,
                            "fulfillment_type": fulfillment_type
                        }
                    }
                }
            ]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
```

### 3. Orders API

```python
# backend/integrations/amazon/orders.py

class AmazonOrdersAPI:
    """Amazon Orders API 封装"""

    def __init__(self, auth: AmazonSPAuth):
        self.auth = auth
        self.base_url = "https://sellingpartnerapi-na.amazon.com"

    async def get_orders(
        self,
        created_after: str = None,
        marketplace_ids: List[str] = None,
        order_statuses: List[str] = None,
        max_results: int = 50
    ) -> dict:
        """获取订单列表"""

        url = f"{self.base_url}/orders/v0/orders"

        headers = self.auth.get_auth_headers()
        params = {
            "MarketplaceIds": marketplace_ids or [self.marketplace_id],
            "MaxResultsPerPage": min(max_results, 100)
        }

        if created_after:
            params["CreatedAfter"] = created_after
        if order_statuses:
            params["OrderStatuses"] = ",".join(order_statuses)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

    async def get_order(self, amazon_order_id: str) -> dict:
        """获取订单详情"""

        url = f"{self.base_url}/orders/v0/orders/{amazon_order_id}"

        headers = self.auth.get_auth_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()

    async def get_order_items(
        self,
        amazon_order_id: str
    ) -> dict:
        """获取订单明细"""

        url = f"{self.base_url}/orders/v0/orders/{amazon_order_id}/orderItems"

        headers = self.auth.get_auth_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
```

### 4. Pricing API

```python
# backend/integrations/amazon/pricing.py

class AmazonPricingAPI:
    """Amazon Pricing API 封装"""

    def __init__(self, auth: AmazonSPAuth):
        self.auth = auth
        self.base_url = "https://sellingpartnerapi-na.amazon.com"

    async def get_competitive_pricing(
        self,
        asin: str,
        marketplace_id: str
    ) -> dict:
        """获取竞争定价"""

        url = f"{self.base_url}/products/pricing/v0/competitivePrice"

        headers = self.auth.get_auth_headers()
        params = {
            "MarketplaceId": marketplace_id,
            "Asin": asin,
            "ItemType": "Asin"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

    async def get_product_pricing(
        self,
        asin: str,
        marketplace_id: str
    ) -> dict:
        """获取商品定价"""

        url = f"{self.base_url}/products/pricing/v0/price"

        headers = self.auth.get_auth_headers()
        params = {
            "MarketplaceId": marketplace_id,
            "Asin": asin,
            "ItemType": "Asin"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

    async def update_price(
        self,
        seller_sku: str,
        standard_price: float,
        sale_price: float = None
    ) -> dict:
        """更新价格"""

        url = f"{self.base_url}/pricing/v0/price"

        headers = self.auth.get_auth_headers()
        headers["Content-Type"] = "application/json"

        payload = {
            "messages": [
                {
                    "messageId": str(uuid.uuid4()),
                    "messageType": "Price",
                    "payload": {
                        "StandardPrice": {
                            "SellerSKU": seller_sku,
                            "StandardPrice": str(standard_price),
                            "Currency": "USD"
                        }
                    }
                }
            ]
        }

        if sale_price:
            payload["messages"][0]["payload"]["SalePrice"] = {
                "SellerSKU": seller_sku,
                "SalePrice": str(sale_price),
                "Currency": "USD",
                "StartDate": datetime.now().isoformat()
            }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
```

---

## 批量操作

### 报告系统

SP-API 的批量操作主要通过报告系统实现：

```python
# backend/integrations/amazon/reports.py

class AmazonReportsAPI:
    """Amazon Reports API 封装"""

    def __init__(self, auth: AmazonSPAuth):
        self.auth = auth
        self.base_url = "https://sellingpartnerapi-na.amazon.com"

    async def create_report(
        self,
        report_type: str,
        data_start_time: str = None,
        data_end_time: str = None,
        marketplace_ids: List[str] = None
    ) -> dict:
        """创建报告请求

        常用报告类型:
        - GET_MERCHANT_LISTINGS_ALL_DATA
        - GET_FLAT_FILE_OPEN_LISTINGS_DATA
        - GET_ORDER_REPORT_DATA
        - GET_FBA_FULFILLMENT_CURRENT_INVENTORY_DATA
        - GET_LEDGER_SUMMARY_VIEW_DATA
        """

        url = f"{self.base_url}/reports/2021-06-30/reports"

        headers = self.auth.get_auth_headers()
        headers["Content-Type"] = "application/json"

        payload = {
            "reportType": report_type,
            "marketplaceIds": marketplace_ids or [self.marketplace_id],
            "dataStartTime": data_start_time,
            "dataEndTime": data_end_time
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

    async def get_report(self, report_id: str) -> dict:
        """获取报告状态"""

        url = f"{self.base_url}/reports/2021-06-30/reports/{report_id}"

        headers = self.auth.get_auth_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()

    async def get_report_document(
        self,
        report_document_id: str
    ) -> bytes:
        """下载报告文档"""

        url = f"{self.base_url}/reports/2021-06-30/documents/{report_document_id}"

        headers = self.auth.get_auth_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=60)
            response.raise_for_status()

            # 如果是加密的，需要解密
            payload = response.json()
            if payload.get("encryptionDetails"):
                # 解密逻辑
                payload_data = self._decrypt_document(payload)
            else:
                payload_data = payload["payload"]

            # 下载实际内容
            document_url = payload["url"]
            doc_response = await client.get(document_url, timeout=60)

            return doc_response.content

    async def wait_for_report(
        self,
        report_id: str,
        timeout: int = 300
    ) -> dict:
        """等待报告完成"""

        start_time = time.time()

        while time.time() - start_time < timeout:
            report = await self.get_report(report_id)

            processing_status = report.get("processingStatus")

            if processing_status == "DONE":
                return report
            elif processing_status in ["CANCELLED", "FATAL"]:
                raise Exception(f"Report processing failed: {processing_status}")

            await asyncio.sleep(5)

        raise TimeoutError("Report processing timeout")
```

---

## 最佳实践

### 1. 速率限制处理

```python
# backend/integrations/amazon/rate_limiter.py

import time
import asyncio
from typing import Callable

class AmazonRateLimiter:
    """Amazon API 速率限制器"""

    def __init__(
        self,
        requests_per_second: float = 2.0,
        burst_size: int = 10
    ):
        self.rate = requests_per_second
        self.burst = burst_size
        self.tokens = burst_size
        self.last_update = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self):
        """获取令牌"""
        async with self._lock:
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(
                self.burst,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now

            if self.tokens < 1:
                sleep_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(sleep_time)
                self.tokens = 0
            else:
                self.tokens -= 1

    async def call_with_limit(self, func: Callable, *args, **kwargs):
        """在速率限制下调用函数"""
        await self.acquire()
        return await func(*args, **kwargs)

# 使用示例
limiter = AmazonRateLimiter(requests_per_second=2.0)

# 包装 API 调用
result = await limiter.call_with_limit(
    listings_api.get_listing,
    seller_sku="MOUSE-BLK-001"
)
```

### 2. 错误处理

```python
# backend/integrations/amazon/errors.py

class AmazonAPIError(Exception):
    """Amazon API 错误基类"""
    pass

class AmazonQuotaExceededError(AmazonAPIError):
    """配额超限"""
    pass

class AmazonAuthenticationError(AmazonAPIError):
    """认证失败"""
    pass

class AmazonThrottlingError(AmazonAPIError):
    """请求被限流"""
    pass

async def handle_amazon_response(response: httpx.Response):
    """处理 Amazon API 响应"""

    if response.status_code == 200:
        return response.json()

    elif response.status_code == 401:
        raise AmazonAuthenticationError("Authentication failed")

    elif response.status_code == 429:
        retry_after = int(response.headers.get("X-RetryAfter", 60))
        raise AmazonThrottlingError(
            f"Rate limited. Retry after {retry_after} seconds"
        )

    elif response.status_code == 503:
        raise AmazonAPIError("Service temporarily unavailable")

    else:
        error_data = response.json()
        raise AmazonAPIError(
            f"API Error: {error_data.get('errors', 'Unknown error')}"
        )
```

### 3. 数据同步策略

```python
# backend/integrations/amazon/sync.py

class AmazonDataSync:
    """Amazon 数据同步器"""

    def __init__(
        self,
        orders_api: AmazonOrdersAPI,
        listings_api: AmazonListingsAPI
    ):
        self.orders_api = orders_api
        self.listings_api = listings_api

    async def sync_orders(
        self,
        hours: int = 24,
        sync_to_db: Callable = None
    ):
        """同步最近 N 小时的订单"""

        created_after = (datetime.now() - timedelta(hours=hours)).isoformat()

        orders_data = await self.orders_api.get_orders(
            created_after=created_after
        )

        orders = orders_data.get("payload", {}).get("Orders", [])

        for order_summary in orders:
            order_id = order_summary["AmazonOrderId"]

            # 获取完整订单数据
            order_detail = await self.orders_api.get_order(order_id)
            order_items = await self.orders_api.get_order_items(order_id)

            # 合并数据
            full_order = {
                **order_detail,
                "items": order_items.get("payload", {}).get("OrderItems", [])
            }

            # 同步到数据库
            if sync_to_db:
                await sync_to_db(full_order)

        return len(orders)
```

---

**下一步**: 查看 [08_SECURITY.md](./08_SECURITY.md)
