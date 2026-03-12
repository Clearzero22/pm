# 开发流程规范

> **跨境电商全工作流系统** - 团队开发与代码规范

**版本**: v1.0.0
**更新时间**: 2026-03-12

---

## 目录

1. [开发流程](#开发流程)
2. [代码规范](#代码规范)
3. [Git 工作流](#git-工作流)
4. [代码审查](#代码审查)
5. [测试要求](#测试要求)
6. [文档规范](#文档规范)

---

## 开发流程

### 敏捷开发流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          敏捷开发流程                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Sprint 规划 (2周)                                                      │
│    │                                                                    │
│    ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  任务分配                                                          │   │
│  │  • 从 Project Board 选择任务                                      │   │
│  │  • 创建 Feature 分支                                              │   │
│  │  • 领取任务 (Assign)                                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│    │                                                                    │
│    ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  开发实施                                                          │   │
│  │  1. 编写代码                                                      │   │
│  │  2. 编写测试                                                      │   │
│  │  3. 本地验证                                                      │   │
│  │  4. 提交代码                                                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│    │                                                                    │
│    ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  代码审查                                                          │   │
│  │  • 创建 Pull Request                                            │   │
│  │  • 自动检查通过                                                   │   │
│  │  • 至少 1 人 Review                                               │   │
│  │  • 修改反馈                                                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│    │                                                                    │
│    ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  合并部署                                                          │   │
│  │  • Squash and merge                                             │   │
│  │  • 自动部署到 Staging                                            │   │
│  │  • 冒烟测试                                                       │   │
│  │  • 部署到 Production                                             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 任务状态流转

```
┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐
│ Backlog │────▶│  Todo  │────▶│In Prog.│────▶│ Review │────▶│  Done  │
│        │     │        │     │        │     │        │     │        │
│规划阶段 │     │待开发  │     │开发中  │     │审查中  │     │已完成  │
└────────┘     └────────┘     └────────┘     └────────┘     └────────┘
                    ▲                                    │
                    │                                    │
                    └────────────────────────────────────┘
                             需要修改
```

---

## 代码规范

### Python 代码规范

#### 命名规范

```python
# ========== 文件命名 ==========
# 小写，下划线分隔
# user_service.py
# product_model.py

# ========== 类命名 ==========
# 大驼峰 (PascalCase)
class UserService:
    pass

class OrderItem:
    pass

# ========== 函数命名 ==========
# 小写，下划线分隔
def get_user_by_id(user_id: str):
    pass

def calculate_profit_margin(revenue: float, cost: float):
    pass

# ========== 变量命名 ==========
# 小写，下划线分隔
user_name = "John"
order_count = 10
is_active = True

# 常量: 全大写
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 30
API_BASE_URL = "https://api.example.com"

# 私有变量: 前缀下划线
class UserService:
    def __init__(self):
        self._cache = {}  # 私有
        self.session = None  # 公共
```

#### 类型注解

```python
# ========== 函数类型注解 ==========
from typing import List, Dict, Optional, Union

def get_products(
    category: str,
    limit: int = 20,
    include_inactive: bool = False
) -> List[dict]:
    """获取产品列表"""
    pass

def calculate_profit(
    revenue: float,
    costs: Dict[str, float]
) -> Optional[float]:
    """计算利润"""
    pass

# ========== 类型别名 ==========
from typing import TypedDict, List

class Product(TypedDict):
    id: str
    title: str
    price: float

ProductList = List[Product]

def process_products(products: ProductList) -> int:
    """处理产品列表"""
    pass

# ========== 泛型 ==========
from typing import TypeVar, Generic

T = TypeVar('T')

class PaginatedResponse(Generic[T]):
    def __init__(self, data: List[T], total: int):
        self.data = data
        self.total = total
```

#### 文档字符串

```python
# ========== Google 风格 ==========
def get_user_orders(
    user_id: str,
    status: str = "all",
    limit: int = 20
) -> List[dict]:
    """获取用户订单列表.

    Args:
        user_id: 用户 ID
        status: 订单状态筛选 (all/pending/shipped/completed)
        limit: 返回数量限制

    Returns:
        订单列表，每个订单包含 id, status, total 等字段

    Raises:
        ValueError: 如果 user_id 为空
        UserNotFound: 如果用户不存在

    Examples:
        >>> get_user_orders("user123", limit=5)
        [{'id': 'order1', 'status': 'shipped', ...}]
    """
    pass

# ========== 类文档字符串 ==========
class UserService:
    """用户服务类.

    负责用户的 CRUD 操作和业务逻辑处理。

    Attributes:
        db: 数据库会话
        cache: 缓存客户端

    Examples:
        >>> service = UserService()
        >>> user = service.get_user("user123")
    """

    def __init__(self, db, cache):
        """初始化用户服务.

        Args:
            db: 数据库会话
            cache: 缓存客户端
        """
        self.db = db
        self.cache = cache
```

#### 代码组织

```python
# ========== 导入顺序 ==========
# 1. 标准库
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional

# 2. 第三方库
import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session

# 3. 本地模块
from api.models import User
from api.utils import validate_input

# ========== 模块组织 ==========
# 按功能分组，使用空行分隔

class UserService:
    """用户服务"""

    def __init__(self):
        pass

    # ========== CRUD ==========
    def create(self):
        pass

    def read(self):
        pass

    # ========== 业务逻辑 ==========
    def validate(self):
        pass

    def process(self):
        pass
```

### TypeScript/JavaScript 代码规范

```typescript
// ========== 命名规范 ==========
// 接口/类型: 大驼峰
interface UserService {
  getUserById(id: string): User;
}

// 类: 大驼峰
class OrderService {
  private cache: Map<string, any>;
}

// 函数/变量: 小驼峰
function getUserOrders(userId: string): Order[] {
  return [];
}

const maxRetryCount = 3;

// 常量: 全大写
const API_BASE_URL = "https://api.example.com";

// ========== 类型定义 ==========
interface User {
  id: string;
  name: string;
  email: string;
}

type OrderStatus = "pending" | "shipped" | "completed";

interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
}

// ========== 异步处理 ==========
async function fetchUserData(userId: string): Promise<User> {
  const response = await fetch(`/api/users/${userId}`);
  const data = await response.json();
  return data;
}

// ========== 错误处理 ==========
try {
  const user = await fetchUserData(userId);
} catch (error) {
  if (error instanceof NetworkError) {
    console.error("Network error:", error.message);
  } else {
    console.error("Unexpected error:", error);
  }
}
```

---

## Git 工作流

### 分支策略

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Git 分支模型                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  master (主分支)                                                        │
│  ├── 只有稳定的代码                                                     │
│  ├── 每次提交打标签                                                     │
│  └── 保护分支，禁止直接推送                                           │
│                                                                         │
│  develop (开发分支)                                                     │
│  ├── 开发集成分支                                                       │
│  ├── 每日集成                                                           │
│  └── 功能测试通过                                                     │
│                                                                         │
│  feature/* (功能分支)                                                  │
│  ├── feature/selection-system                                          │
│  ├── feature/ai-image-editing                                          │
│  └── 从 develop 分支，合并回 develop                                   │
│                                                                         │
│  bugfix/* (修复分支)                                                   │
│  ├── bugfix/login-error                                                │
│  ├── bugfix/payment-crash                                             │
│  └── 从 develop 分支，合并回 develop                                   │
│                                                                         │
│  hotfix/* (紧急修复)                                                   │
│  ├── hotfix/security-patch                                            │
│  ├── 从 master 分支，合并到 master 和 develop                          │
│  └── 用于生产环境紧急修复                                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 提交规范

```bash
# ========== Conventional Commits ==========
# 格式: <type>(<scope>): <subject>

# type 类型:
feat:     新功能
fix:      Bug 修复
docs:     文档变更
style:    代码格式 (不影响功能)
refactor: 重构
perf:     性能优化
test:     测试相关
chore:    构建/工具链相关
ci:       CI/CD 配置

# scope 范围:
(selection), (creative), (operations), (api), (db), etc.

# 示例:
git commit -m "feat(selection): add competitor analysis"
git commit -m "fix(api): resolve authentication token leak"
git commit -m "docs(readme): update installation instructions"
git commit -m "perf(image): optimize batch processing speed"
```

### 提交消息模板

```bash
# .gitmessage 模板
# 可以设置为 git commit 模板

# <type>(<scope>): <subject>
# |<----  Using a Maximum Of 50 Characters  ---->|

# Explain why this change is being made
# |<----   Try To Limit Each Line to a Maximum Of 72 Characters   ---->|

# Provide links or keys to any relevant tickets, articles or other resources
# Example: Fixes #234

# --- COMMIT END ---
# Type can be : [feat, fix, docs, style, refactor, test, chore]
# Remember to add Signed-off-by for DCO (Developer Certificate of Origin)
# Signed-off-by: Your Name <your.email@example.com>
```

### 分支操作示例

```bash
# ========== 创建功能分支 ==========
git checkout develop
git pull origin develop
git checkout -b feature/ai-image-editing

# ========== 开发并提交 ==========
git add .
git commit -m "feat(ai): implement background removal"

# ========== 推送到远程 ==========
git push -u origin feature/ai-image-editing

# ========== 创建 Pull Request ==========
# 通过 GitHub/GitLab UI 创建 PR

# ========== 代码审查通过后合并 ==========
git checkout develop
git pull origin develop
git branch -d feature/ai-image-editing

# ========== 紧急修复流程 ==========
git checkout master
git checkout -b hotfix/security-patch
# ... 修复 ...
git checkout master
git merge hotfix/security-patch
git checkout develop
git merge hotfix/security-patch
```

---

## 代码审查

### Pull Request 检查清单

```markdown
## PR 检查清单

### 代码质量
- [ ] 代码符合项目规范 (PEP 8 / ESLint)
- [ ] 没有硬编码的配置值
- [ ] 没有调试代码 (console.log / print)
- [ ] 没有注释掉的代码
- [ ] 适当的错误处理
- [ ] 类型注解完整

### 测试
- [ ] 单元测试覆盖率 > 80%
- [ ] 所有测试通过
- [ ] 新功能有对应测试
- [ ] Bug 修复有回归测试

### 文档
- [ ] README 已更新
- [ ] API 文档已更新
- [ ] 复杂逻辑有注释
- [ ] 变更日志已更新

### 性能
- [ ] 没有明显的性能问题
- [ ] 数据库查询已优化
- [ ] 没有内存泄漏
- [ ] API 响应时间合理

### 安全
- [ ] 没有安全漏洞
- [ ] 输入验证完整
- [ ] 敏感数据已加密
- [ ] 权限检查正确
```

### 审查流程

```
1. 自动检查
   ├── 代码格式检查 (Black / ESLint)
   ├── 类型检查 (mypy / TypeScript)
   ├── 单元测试
   ├── 集成测试
   └── 安全扫描

2. 人工审查
   ├── 功能正确性
   ├── 代码质量
   ├── 性能影响
   ├── 安全问题
   └── 文档完整性

3. 修改反馈
   └── 开发者修改

4. 审查通过
   └── Squash and merge
```

---

## 测试要求

### 测试金字塔

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          测试金字塔                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                        /E2E Tests\                                    │
│                       /-------------\                                   │
│                      /               \                                  │
│                     /    集成测试     \                                 │
│                    /-------------------\                                │
│                   /                       \                               │
│                  /      单元测试 (70%)      \                          │
│                 /                           \                         │
│                /_______________________________\                        │
│                                                                         │
│  E2E (10%): 端到端用户流程                                             │
│  集成 (20%): 模块间交互                                                 │
│  单元 (70%): 函数/类级别测试                                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 单元测试

```python
# tests/test_user_service.py
import pytest
from unittest.mock import Mock
from api.services.user_service import UserService

class TestUserService:
    """用户服务测试"""

    @pytest.fixture
    def service(self):
        """创建服务实例"""
        mock_db = Mock()
        mock_cache = Mock()
        return UserService(mock_db, mock_cache)

    @pytest.fixture
    def sample_user(self):
        """示例用户数据"""
        return {
            "id": "user123",
            "name": "John Doe",
            "email": "john@example.com"
        }

    def test_get_user_success(self, service, sample_user):
        """测试: 成功获取用户"""
        # Arrange
        service.db.query.return_value.filter.return_value.first.return_value = sample_user

        # Act
        result = service.get_user("user123")

        # Assert
        assert result == sample_user
        service.db.query.assert_called_once()

    def test_get_user_not_found(self, service):
        """测试: 用户不存在"""
        # Arrange
        service.db.query.return_value.filter.return_value.first.return_value = None

        # Act & Assert
        with pytest.raises(UserNotFound):
            service.get_user("nonexistent")

    @pytest.mark.parametrize("status,count", [
        ("active", 10),
        ("inactive", 5),
        ("all", 15)
    ])
    def test_get_users_by_status(self, service, status, count):
        """测试: 按状态获取用户"""
        # Arrange
        service.db.query.return_value.filter.return_value.count.return_value = count

        # Act
        result = service.get_user_count_by_status(status)

        # Assert
        assert result == count
```

### 集成测试

```python
# tests/integration/test_api_integration.py
import pytest
from fastapi.testclient import TestClient
from api.main import app

class TestProductAPI:
    """产品 API 集成测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self):
        """认证头"""
        return {"Authorization": "Bearer test_token"}

    def test_create_product_success(self, client, auth_headers):
        """测试: 创建产品成功"""
        response = client.post(
            "/api/v1/products",
            json={
                "asin": "B0BZYCJK89",
                "title": "Test Product",
                "price": 29.99
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["asin"] == "B0BZYCJK89"

    def test_get_products_pagination(self, client):
        """测试: 产品分页"""
        response = client.get("/api/v1/products?page=1&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert data["meta"]["page"] == 1
        assert data["meta"]["limit"] == 10
```

### E2E 测试

```python
# tests/e2e/test_user_flow.py
from playwright.async_api import async_playwright

class TestUserFlow:
    """用户流程 E2E 测试"""

    async def test_login_and_create_order(self):
        """测试: 登录并创建订单"""
        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch()
            page = await browser.new_page()

            # 打开登录页
            await page.goto("http://localhost:3000/login")

            # 填写登录表单
            await page.fill("input[name='email']", "test@example.com")
            await page.fill("input[name='password']", "password123")
            await page.click("button[type='submit']")

            # 等待跳转
            await page.wait_for_url("**/dashboard")

            # 创建订单
            await page.click("text=New Order")
            await page.fill("input[name='product_name']", "Test Product")
            await page.click("button[type='submit']")

            # 验证成功
            await page.wait_for_selector("text=Order created successfully")
            success_message = await page.text_content(".success-message")
            assert "Order created" in success_message

            await browser.close()
```

---

## 文档规范

### 代码注释原则

```python
# ========== 好的注释 ==========
# 计算利润率
# 公式: (收入 - 成本) / 收入 * 100
def calculate_profit_margin(revenue: float, cost: float) -> float:
    """计算利润率.

    Args:
        revenue: 总收入
        cost: 总成本

    Returns:
        利润率百分比

    Raises:
        ValueError: 如果收入为 0 或负数
    """
    if revenue <= 0:
        raise ValueError("Revenue must be positive")
    return ((revenue - cost) / revenue) * 100

# ========== 不好的注释 ==========
# 获取用户
def get_user(user_id):  # user_id 是字符串
    # 返回用户数据
    return db.query(user_id)
    # 这里的注释只是重复了代码，没有价值
```

### README 规范

```markdown
# 项目名称

简短描述 (一句话)

## 功能特性

- 特性 1
- 特性 2

## 安装

\`\`\`bash
pip install project-name
\`\`\`

## 使用

\`\`\`python
import project_name
\`\`\`

## 贡献指南

欢迎贡献！

## 许可证

MIT
```

### API 文档规范

```python
# FastAPI 自动生成文档
from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI(
    title="E-commerce API",
    description="Amazon E-commerce Automation System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get(
    "/api/v1/products",
    summary="获取产品列表",
    description="支持分页、过滤和排序的产品列表接口",
    response_description="产品列表和分页信息"
)
async def get_products(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词")
):
    """
    获取产品列表

    - **page**: 页码 (从 1 开始)
    - **limit**: 每页数量 (1-100)
    - **search**: 搜索关键词 (可选)

    返回产品列表和分页信息
    """
    pass
```

---

## 开发工具配置

### VSCode 配置

```json
// .vscode/settings.json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "python.testing.pytestEnabled": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true
  }
}

// .vscode/extensions.json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "eamodio.gitlens",
    "streetsidesoftware.code-spell-checker"
  ]
}
```

### Pre-commit 配置

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ["--max-line-length=88"]
```

---

**下一步**: 查看 [TESTING_GUIDE.md](./TESTING_GUIDE.md)
