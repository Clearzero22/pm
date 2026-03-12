# 测试指南

> **跨境电商全工作流系统** - 测试策略与最佳实践

**版本**: v1.0.0
**更新时间**: 2026-03-12

---

## 目录

1. [测试策略](#测试策略)
2. [单元测试](#单元测试)
3. [集成测试](#集成测试)
4. [E2E 测试](#e2e-测试)
5. [性能测试](#性能测试)
6. [测试工具](#测试工具)

---

## 测试策略

### 测试层级

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          测试层级金字塔                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                          /     E2E      \                               │
│                         /   (10%)       \                              │
│                        /__________________\                             │
│                       /                     \                            │
│                      /      集成测试         \                           │
│                     /        (20%)           \                          │
│                    /__________________________\                       │
│                   /                            \                      │
│                  /        单元测试 (70%)         \                     │
│                 /________________________________\                    │
│                                                                         │
│  单元测试: 快速、隔离、可重复                                             │
│  集成测试: 模块交互、数据库、API                                          │
│  E2E 测试: 用户流程、真实浏览器                                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 测试覆盖率目标

| 模块类型 | 覆盖率目标 | 说明 |
|----------|------------|------|
| **核心业务** | 90%+ | 订单、支付、库存 |
| **AI 功能** | 80%+ | 图像处理、文案生成 |
| **API 层** | 85%+ | 所有端点 |
| **工具函数** | 95%+ | 纯函数 |
| **总体** | 80%+ | 项目整体 |

---

## 单元测试

### Pytest 配置

```python
# pytest.ini
[tool:pytest]
minversion = "7.0"
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# 标记
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
    gpu: Tests requiring GPU
    api: API tests

# 覆盖率
addopts =
    --cov=backend
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80

# 超时
timeout = 300

# 警告
filterwarnings =
    error
    ignore::DeprecationWarning
```

### 单元测试示例

```python
# tests/unit/test_selection_service.py
import pytest
from unittest.mock import Mock, patch, AsyncMock
from decimal import Decimal

from backend.services.selection.service import SelectionService
from backend.services.selection.models import ProductAnalysis


class TestSelectionService:
    """选品服务单元测试"""

    @pytest.fixture
    def service(self):
        """创建服务实例"""
        mock_db = Mock()
        mock_cache = Mock()
        return SelectionService(mock_db, mock_cache)

    @pytest.fixture
    def sample_product_data(self):
        """示例产品数据"""
        return {
            "asin": "B0BZYCJK89",
            "title": "Wireless Mouse",
            "price": Decimal("29.99"),
            "rating": 4.5,
            "review_count": 1000
        }

    # ========== 基础测试 ==========

    def test_calculate_profit_margin(self, service):
        """测试: 利润率计算"""
        # Arrange
        revenue = Decimal("100.00")
        cost = Decimal("70.00")

        # Act
        margin = service._calculate_profit_margin(revenue, cost)

        # Assert
        assert margin == Decimal("30.00")
        assert isinstance(margin, Decimal)

    def test_calculate_profit_margin_zero_revenue(self, service):
        """测试: 零收入抛出异常"""
        # Arrange
        revenue = Decimal("0.00")
        cost = Decimal("50.00")

        # Act & Assert
        with pytest.raises(ValueError, match="Revenue must be positive"):
            service._calculate_profit_margin(revenue, cost)

    # ========== Mock 测试 ==========

    @pytest.mark.asyncio
    async def test_fetch_product_data_success(self, service, sample_product_data):
        """测试: 成功获取产品数据"""
        # Arrange
        asin = "B0BZYCJK89"
        service.http_client.get = AsyncMock(
            return_value=Mock(json=Mock(return_value=sample_product_data))
        )

        # Act
        result = await service.fetch_product_data(asin)

        # Assert
        assert result["asin"] == asin
        service.http_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_product_data_cached(self, service, sample_product_data):
        """测试: 使用缓存"""
        # Arrange
        asin = "B0BZYCJK89"
        service.cache.get.return_value = sample_product_data

        # Act
        result = await service.fetch_product_data(asin)

        # Assert
        assert result == sample_product_data
        service.cache.get.assert_called_with(f"product:{asin}")
        service.http_client.get.assert_not_called()

    # ========== 参数化测试 ==========

    @pytest.mark.parametrize("price,expected_tier", [
        (Decimal("10.00"), "low"),
        (Decimal("50.00"), "medium"),
        (Decimal("100.00"), "high"),
    ])
    def test_determine_price_tier(self, service, price, expected_tier):
        """测试: 价格分层"""
        # Act
        tier = service._determine_price_tier(price)

        # Assert
        assert tier == expected_tier

    # ========== 异常测试 ==========

    @pytest.mark.asyncio
    async def test_fetch_product_data_network_error(self, service):
        """测试: 网络错误处理"""
        # Arrange
        service.http_client.get = AsyncMock(
            side_effect=ConnectionError("Network error")
        )

        # Act & Assert
        with pytest.raises(ConnectionError):
            await service.fetch_product_data("B0BZYCJK89")

    # ========== Fixture 测试 ==========

    @pytest.fixture
    def mock_amazon_response(self):
        """Mock Amazon API 响应"""
        return {
            "payload": {
                "Products": [
                    {
                        "Asin": "B0BZYCJK89",
                        "Title": "Test Product",
                        "AttributeSets": [
                            {
                                "Title": "Test Product",
                                "Feature": "Test Feature"
                            }
                        ]
                    }
                ]
            }
        }

    def test_parse_amazon_response(self, service, mock_amazon_response):
        """测试: 解析 Amazon 响应"""
        # Act
        result = service._parse_amazon_response(mock_amazon_response)

        # Assert
        assert len(result) == 1
        assert result[0]["asin"] == "B0BZYCJK89"
        assert result[0]["title"] == "Test Product"
```

### 测试数据库隔离

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from api.main import app
from api.database import Base, get_db

# 测试数据库
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """创建测试数据库"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

---

## 集成测试

### API 集成测试

```python
# tests/integration/test_products_api.py
import pytest
from fastapi.testclient import TestClient

class TestProductsAPI:
    """产品 API 集成测试"""

    @pytest.fixture
    def client(self, db_session):
        """创建测试客户端"""
        from api.main import app
        from api.dependencies import get_db

        def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db
        yield TestClient(app)
        app.dependency_overrides.clear()

    @pytest.fixture
    def auth_headers(self, user_factory):
        """创建认证头"""
        user = user_factory(email="test@example.com")
        token = create_access_token(user.id)
        return {"Authorization": f"Bearer {token}"}

    def test_create_product_success(self, client, auth_headers):
        """测试: 创建产品成功"""
        # Arrange
        payload = {
            "asin": "B0BZYCJK89",
            "title": "Test Product",
            "brand": "Test Brand",
            "price": 29.99
        }

        # Act
        response = client.post(
            "/api/v1/products",
            json=payload,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["asin"] == "B0BZYCJK89"
        assert data["title"] == "Test Product"

    def test_create_product_duplicate_asin(self, client, auth_headers, product_factory):
        """测试: 重复 ASIN"""
        # Arrange
        existing_product = product_factory(asin="B0BZYCJK89")
        payload = {
            "asin": "B0BZYCJK89",
            "title": "Another Product"
        }

        # Act
        response = client.post(
            "/api/v1/products",
            json=payload,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 409
        data = response.json()
        assert "duplicate" in data["error"]["code"].lower()

    def test_get_products_pagination(self, client, product_factory):
        """测试: 产品分页"""
        # Arrange
        for i in range(25):
            product_factory(asin=f"B0{i:06d}")

        # Act
        response = client.get("/api/v1/products?page=1&limit=10")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 10
        assert data["meta"]["total"] == 25
        assert data["meta"]["page"] == 1
        assert data["meta"]["pages"] == 3

    def test_get_products_filter_by_status(self, client, product_factory):
        """测试: 按状态过滤"""
        # Arrange
        product_factory(status="active")
        product_factory(status="inactive")
        product_factory(status="active")

        # Act
        response = client.get("/api/v1/products?status=active")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert all(p["status"] == "active" for p in data["data"])

    def test_update_product_not_found(self, client, auth_headers):
        """测试: 更新不存在的产品"""
        # Arrange
        payload = {"title": "Updated Title"}

        # Act
        response = client.patch(
            "/api/v1/products/nonexistent-id",
            json=payload,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 404
```

### 数据库集成测试

```python
# tests/integration/test_database.py
import pytest
from sqlalchemy.orm import Session

class TestDatabaseIntegration:
    """数据库集成测试"""

    def test_create_and_retrieve_product(self, db: Session):
        """测试: 创建和检索产品"""
        # Arrange
        from api.models import Product
        product = Product(
            asin="B0BZYCJK89",
            title="Test Product",
            brand="Test Brand"
        )
        db.add(product)
        db.commit()

        # Act
        retrieved = db.query(Product).filter(
            Product.asin == "B0BZYCJK89"
        ).first()

        # Assert
        assert retrieved is not None
        assert retrieved.title == "Test Product"
        assert retrieved.asin == "B0BZYCJK89"

    def test_product_listing_relationship(self, db: Session):
        """测试: 产品与上架关系"""
        # Arrange
        from api.models import Product, Listing

        product = Product(asin="B0BZYCJK89", title="Test")
        listing = Listing(
            product=product,
            marketplace="US",
            sku="TEST-001"
        )
        db.add_all([product, listing])
        db.commit()

        # Act
        retrieved = db.query(Product).first()

        # Assert
        assert len(retrieved.listings) == 1
        assert retrieved.listings[0].marketplace == "US"

    def test_cascade_delete(self, db: Session):
        """测试: 级联删除"""
        # Arrange
        from api.models import Product, Listing

        product = Product(asin="B0BZYCJK89", title="Test")
        listing = Listing(
            product=product,
            marketplace="US",
            sku="TEST-001"
        )
        db.add_all([product, listing])
        db.commit()

        # Act
        db.delete(product)
        db.commit()

        # Assert
        assert db.query(Listing).count() == 0
```

---

## E2E 测试

### Playwright E2E 测试

```python
# tests/e2e/test_user_journeys.py
from playwright.async_api import async_playwright, Page
import pytest


class TestUserJourneys:
    """用户旅程 E2E 测试"""

    @pytest.mark.e2e
    async def test_complete_product_creation_flow(self):
        """测试: 完整的产品创建流程"""
        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            # 1. 登录
            await page.goto("http://localhost:3000/login")
            await page.fill("input[name='email']", "test@example.com")
            await page.fill("input[name='password']", "password123")
            await page.click("button[type='submit']")
            await page.wait_for_url("**/dashboard")

            # 2. 导航到产品页面
            await page.click("text=Products")
            await page.wait_for_url("**/products")

            # 3. 点击新建产品
            await page.click("button:has-text('New Product')")
            await page.wait_for_selector("form#create-product-form")

            # 4. 填写产品表单
            await page.fill("input[name='asin']", "B0BZYCJK89")
            await page.fill("input[name='title']", "Test Product")
            await page.fill("input[name='brand']", "Test Brand")
            await page.fill("input[name='price']", "29.99")

            # 5. 上传图片
            file_input = await page.query_selector("input[type='file']")
            await file_input.set_input_files("tests/fixtures/test_product.jpg")

            # 6. 提交表单
            await page.click("button[type='submit']")

            # 7. 验证成功
            await page.wait_for_selector("text=Product created successfully")
            success_msg = await page.text_content(".success-message")

            assert "Product created" in success_msg
            assert await page.url == "http://localhost:3000/products"

            # 清理
            await context.close()
            await browser.close()

    @pytest.mark.e2e
    async def test_ai_image_generation_flow(self):
        """测试: AI 图片生成流程"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # 1. 登录
            await page.goto("http://localhost:3000/login")
            # ... 登录代码 ...

            # 2. 导航到 AI 创作页面
            await page.click("text=AI Creative")
            await page.wait_for_selector(".ai-creative-upload")

            # 3. 上传产品图片
            await page.set_input_files(
                "input[type='file']",
                "tests/fixtures/test_product.jpg"
            )

            # 4. 选择场景
            await page.check("input[value='minimalist_white']")
            await page.check("input[value='modern_living']")

            # 5. 点击生成
            await page.click("button:has-text('Generate Images')")

            # 6. 等待生成完成
            await page.wait_for_selector(".generation-progress", state="hidden", timeout=60000)

            # 7. 验证结果
            generated_images = await page.query_selector_all(".generated-image")
            assert len(generated_images) >= 2

            # 8. 下载图片
            await page.click("button:has-text('Download All')")

            # 验证下载开始
            async with page.expect_download() as download_info:
                await page.click("button:has-text('Download All')")

            assert download_info

            await browser.close()

    @pytest.mark.e2e
    async def test_order_processing_workflow(self):
        """测试: 订单处理工作流"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # 1. 创建模拟订单 (通过 API)
            # 这通常在 setup 中完成

            # 2. 登录并导航到订单页面
            await page.goto("http://localhost:3000/orders")
            await page.wait_for_selector(".order-list")

            # 3. 找到新订单
            new_order = page.locator(".order-item").first
            await new_order.click()

            # 4. 处理订单
            await page.click("button:has-text('Process Order')")
            await page.wait_for_selector(".order-status:has-text('Processing')")

            # 5. 更新状态
            await page.select_option("#status-select", "Shipped")
            await page.fill("#tracking-input", "1Z999AA10123456784")
            await page.click("button:has-text('Update Status')")

            # 6. 验证状态更新
            status_badge = await page.text_content(".order-status")
            assert "Shipped" in status_badge

            await browser.close()
```

---

## 性能测试

### Locust 性能测试

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner
import time

class EcommerceUser(HttpUser):
    """电商系统用户模拟"""

    wait_time = between(1, 3)
    host = "http://localhost:8000"

    def on_start(self):
        """用户启动时的操作"""
        self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password"
        })

    @task(3)
    def view_products(self):
        """浏览产品 (权重 3)"""
        self.client.get("/api/v1/products?page=1&limit=20")

    @task(2)
    def view_product_detail(self):
        """查看产品详情 (权重 2)"""
        asin = "B0BZYCJK89"
        self.client.get(f"/api/v1/products/{asin}")

    @task(1)
    def search_products(self):
        """搜索产品 (权重 1)"""
        self.client.get("/api/v1/products?q=wireless+mouse")

    @task(1)
    def get_analytics(self):
        """获取分析数据 (权重 1)"""
        self.client.get("/api/v1/finance/revenue")


class APIStressTest(HttpUser):
    """API 压力测试"""

    wait_time = between(0.1, 0.5)
    host = "http://localhost:8000"

    @task
    def create_product(self):
        """创建产品 (写入操作)"""
        import random
        asin = f"B0{random.randint(100000, 999999)}"

        self.client.post("/api/v1/products", json={
            "asin": asin,
            "title": f"Test Product {asin}",
            "price": random.uniform(10, 100)
        })

    @task
    def get_products(self):
        """获取产品列表 (读取操作)"""
        self.client.get("/api/v1/products")
```

### 性能测试运行

```bash
# 单机运行
locust -f tests/performance/locustfile.py --headless -u 100 -r 10 -t 60s

# 分布式运行
# Master
locust -f tests/performance/locustfile.py --master --headless -u 100 -r 10

# Worker
locust -f tests/performance/locustfile.py --worker --master-host=master

# 生成 HTML 报告
locust -f tests/performance/locustfile.py --headless -u 100 -r 10 -t 60s --html report.html
```

---

## 测试工具

### Pytest 插件

```bash
# requirements-test.txt
pytest==7.4.0
pytest-asyncio==0.21.0
pytest-cov==4.1.0
pytest-mock==3.11.1
pytest-timeout==2.1.0
pytest-xdist==3.3.1  # 并行测试
pytest-html==3.2.0  # HTML 报告
pytest-json-report==1.5.0  # JSON 报告
playwright==1.40.0  # E2E 测试
```

### CI/CD 集成

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [master, develop]
  pull_request:
    branches: [master, develop]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt
          pip install -r requirements.txt

      - name: Run unit tests
        run: pytest tests/unit/ --cov=backend --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt
          pip install -r requirements.txt

      - name: Run integration tests
        run: pytest tests/integration/ --timeout=300

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright
        run: npx playwright install --with-deps

      - name: Run E2E tests
        run: npm run test:e2e

      - name: Upload test results
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
```

---

**下一步**: 查看 [modules/SELECTION_SYSTEM.md](../modules/SELECTION_SYSTEM.md)
