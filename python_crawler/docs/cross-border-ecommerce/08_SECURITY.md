# 安全设计文档

> **跨境电商全工作流系统** - 全方位安全防护方案

**版本**: v1.0.0
**更新时间**: 2026-03-12

---

## 目录

1. [安全架构](#安全架构)
2. [认证授权](#认证授权)
3. [数据保护](#数据保护)
4. [API 安全](#api-安全)
5. [基础设施安全](#基础设施安全)
6. [合规要求](#合规要求)

---

## 安全架构

### 纵深防御模型

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         纵深防御安全模型                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Layer 1: 网络安全                                                      │
│  • 防火墙规则  • DDoS 防护  • 网络隔离                                  │
│                                                                         │
│  Layer 2: 应用安全                                                      │
│  • 认证授权  • 输入验证  • 输出编码  • CSRF 防护                         │
│                                                                         │
│  Layer 3: 数据安全                                                      │
│  • 加密存储  • 传输加密  • 密钥管理  • 数据脱敏                          │
│                                                                         │
│  Layer 4: 基础设施安全                                                  │
│  • 主机加固  • 容器安全  • 日志审计  • 入侵检测                          │
│                                                                         │
│  Layer 5: 合规与审计                                                    │
│  • 访问日志  • 操作审计  • 合规报告  • 安全培训                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 威胁模型

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          威胁模型分析                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  外部威胁:                                                               │
│  • SQL 注入  • XSS 攻击  • CSRF 攻击  • DDoS 攻击                      │
│  • 暴力破解  • 中间人攻击  • API 滥用                                   │
│                                                                         │
│  内部威胁:                                                               │
│  • 权限滥用  • 数据泄露  • 误操作  • 恶意内部人员                       │
│                                                                         │
│  系统威胁:                                                               │
│  • 0-day 漏洞  • 依赖库漏洞  • 配置错误  • 人为错误                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 认证授权

### JWT 认证实现

```python
# backend/core/security/jwt.py

from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext

class JWTAuthManager:
    """JWT 认证管理器"""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 60,
        refresh_token_expire_days: int = 7
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire = access_token_expire_minutes
        self.refresh_token_expire = refresh_token_expire_days
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """哈希密码"""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(
        self,
        user_id: str,
        scopes: list[str] = None
    ) -> str:
        """创建访问令牌"""
        now = datetime.utcnow()
        expire = now + timedelta(minutes=self.access_token_expire)

        payload = {
            "sub": user_id,
            "scopes": scopes or [],
            "iat": now.timestamp(),
            "exp": expire.timestamp(),
            "type": "access"
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: str) -> str:
        """创建刷新令牌"""
        now = datetime.utcnow()
        expire = now + timedelta(days=self.refresh_token_expire)

        payload = {
            "sub": user_id,
            "iat": now.timestamp(),
            "exp": expire.timestamp(),
            "type": "refresh"
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict:
        """解码令牌"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    def verify_access_token(
        self,
        token: str,
        required_scope: str = None
    ) -> dict:
        """验证访问令牌"""
        payload = self.decode_token(token)

        if payload.get("type") != "access":
            raise ValueError("Invalid token type")

        if required_scope:
            scopes = payload.get("scopes", [])
            if required_scope not in scopes and "*" not in scopes:
                raise ValueError("Insufficient permissions")

        return payload
```

### RBAC 权限模型

```python
# backend/core/security/rbac.py

from enum import Enum
from typing import List, Dict

class Permission(Enum):
    """权限枚举"""
    # 产品权限
    PRODUCTS_READ = "products:read"
    PRODUCTS_WRITE = "products:write"
    PRODUCTS_DELETE = "products:delete"

    # 订单权限
    ORDERS_READ = "orders:read"
    ORDERS_WRITE = "orders:write"

    # 客服权限
    MESSAGES_READ = "messages:read"
    MESSAGES_WRITE = "messages:write"

    # 财务权限
    FINANCE_READ = "finance:read"
    FINANCE_WRITE = "finance:write"

    # AI 功能
    AI_IMAGE = "ai:image"
    AI_COPY = "ai:copy"
    AI_CHAT = "ai:chat"

    # 管理员
    ADMIN = "admin:*"

class Role(Enum):
    """角色枚举"""
    ADMIN = "admin"
    OPERATOR = "operator"
    CUSTOMER_SERVICE = "customer_service"
    VIEWER = "viewer"

ROLE_PERMISSIONS: Dict[Role, List[Permission]] = {
    Role.ADMIN: [
        Permission.ADMIN  # 覆盖所有权限
    ],
    Role.OPERATOR: [
        Permission.PRODUCTS_READ,
        Permission.PRODUCTS_WRITE,
        Permission.ORDERS_READ,
        Permission.AI_IMAGE,
        Permission.AI_COPY
    ],
    Role.CUSTOMER_SERVICE: [
        Permission.MESSAGES_READ,
        Permission.MESSAGES_WRITE,
        Permission.ORDERS_READ,
        Permission.AI_CHAT
    ],
    Role.VIEWER: [
        Permission.PRODUCTS_READ,
        Permission.ORDERS_READ,
        Permission.FINANCE_READ
    ]
}

class RBACManager:
    """RBAC 权限管理器"""

    @staticmethod
    def get_role_permissions(role: Role) -> List[Permission]:
        """获取角色权限"""
        return ROLE_PERMISSIONS.get(role, [])

    @staticmethod
    def has_permission(
        user_permissions: List[str],
        required_permission: Permission
    ) -> bool:
        """检查是否有权限"""
        # 管理员通配符
        if "*:*" in user_permissions or "admin:*" in user_permissions:
            return True

        # 检查具体权限
        resource = required_permission.value.split(":")[0]
        wildcard = f"{resource}:*"

        return (
            required_permission.value in user_permissions or
            wildcard in user_permissions
        )

    @staticmethod
    def require_permission(permission: Permission):
        """权限装饰器"""
        def decorator(func):
            async def wrapper(*args, current_user: dict = None, **kwargs):
                if not current_user:
                    raise HTTPException(status_code=401, detail="Not authenticated")

                user_permissions = current_user.get("permissions", [])

                if not RBACManager.has_permission(user_permissions, permission):
                    raise HTTPException(status_code=403, detail="Insufficient permissions")

                return await func(*args, current_user=current_user, **kwargs)
            return wrapper
        return decorator

# FastAPI 依赖注入
from fastapi import Depends, HTTPException, status

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt_manager.decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    # 从数据库获取用户信息
    user = await get_user_by_id(user_id)
    if user is None:
        raise credentials_exception

    return user

async def require_permission(permission: Permission):
    """权限检查依赖"""
    def permission_checker(current_user: dict = Depends(get_current_user)):
        user_permissions = current_user.get("permissions", [])

        if not RBACManager.has_permission(user_permissions, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return current_user

    return Depends(permission_checker)
```

---

## 数据保护

### 加密配置

```python
# backend/core/security/encryption.py

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import os

class EncryptionManager:
    """加密管理器"""

    def __init__(self, master_key: bytes = None):
        """
        初始化加密管理器

        Args:
            master_key: 主密钥 (如果不提供，从环境变量读取)
        """
        if master_key is None:
            master_key = os.getenv("ENCRYPTION_MASTER_KEY").encode()

        # 派生加密密钥
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"ecommerce_system_salt",  # 生产环境应使用随机 salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key))
        self.cipher = Fernet(key)

    def encrypt(self, data: str) -> str:
        """加密数据"""
        encrypted = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """解密数据"""
        encrypted = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = self.cipher.decrypt(encrypted)
        return decrypted.decode()

    def encrypt_dict(self, data: dict, fields: list[str]) -> dict:
        """加密字典中的特定字段"""
        result = data.copy()
        for field in fields:
            if field in result and result[field]:
                result[field] = self.encrypt(str(result[field]))
        return result

    def decrypt_dict(self, data: dict, fields: list[str]) -> dict:
        """解密字典中的特定字段"""
        result = data.copy()
        for field in fields:
            if field in result and result[field]:
                result[field] = self.decrypt(result[field])
        return result

# 敏感字段配置
SENSITIVE_FIELDS = {
    "users": ["password", "api_key", "secret_key"],
    "suppliers": ["bank_account", "contact_person"],
    "orders": ["ship_address"],
    "costs": ["invoice_number"]
}

# 数据库模型钩子
from sqlalchemy import event
from sqlalchemy.orm import Mapper

def register_encryption_hooks(mapper: Mapper, cls):
    """注册加密钩子"""

    @event.listens_for(cls, "before_insert")
    def before_insert(mapper, connection, target):
        """插入前加密"""
        encryption_manager = EncryptionManager()
        table_name = cls.__tablename__

        if table_name in SENSITIVE_FIELDS:
            fields = SENSITIVE_FIELDS[table_name]
            for field in fields:
                if hasattr(target, field):
                    value = getattr(target, field)
                    if value:
                        setattr(target, field, encryption_manager.encrypt(value))

    @event.listens_for(cls, "load")
def on_load(target, context):
        """加载后解密"""
        encryption_manager = EncryptionManager()
        table_name = target.__class__.__tablename__

        if table_name in SENSITIVE_FIELDS:
            fields = SENSITIVE_FIELDS[table_name]
            for field in fields:
                if hasattr(target, field):
                    value = getattr(target, field)
                    if value:
                        setattr(target, field, encryption_manager.decrypt(value))
```

### 数据脱敏

```python
# backend/core/security/masking.py

import re
from typing import Any

class DataMasker:
    """数据脱敏器"""

    @staticmethod
    def mask_email(email: str) -> str:
        """脱敏邮箱"""
        if not email:
            return email

        local, domain = email.split("@")
        masked_local = local[0] + "***" if len(local) > 1 else "***"
        return f"{masked_local}@{domain}"

    @staticmethod
    def mask_phone(phone: str) -> str:
        """脱敏手机号"""
        if not phone:
            return phone

        return re.sub(r"(\d{3})\d{4}(\d{4})", r"\1****\2", phone)

    @staticmethod
    def mask_card(card: str) -> str:
        """脱敏银行卡号"""
        if not card:
            return card

        card_clean = re.sub(r"\s", "", card)
        if len(card_clean) < 8:
            return card

        return card_clean[:4] + "*" * (len(card_clean) - 8) + card_clean[-4:]

    @staticmethod
    def mask_address(address: str) -> str:
        """脱敏地址"""
        if not address:
            return address

        # 保留前几个字符和城市信息
        parts = address.split(",")
        if len(parts) > 1:
            return parts[0][:10] + "***" + "," + ",".join(parts[1:])
        return address[:10] + "***"

    @staticmethod
    def mask_data(data: Any, mask_type: str = None) -> Any:
        """根据类型脱敏数据"""
        if isinstance(data, dict):
            return {k: DataMasker.mask_data(v, k) for k, v in data.items()}
        elif isinstance(data, list):
            return [DataMasker.mask_data(item, mask_type) for item in data]
        elif isinstance(data, str):
            if mask_type == "email":
                return DataMasker.mask_email(data)
            elif mask_type == "phone":
                return DataMasker.mask_phone(data)
            elif mask_type in ["card", "bank_account"]:
                return DataMasker.mask_card(data)
            elif mask_type == "address":
                return DataMasker.mask_address(data)
        return data

# API 响应中间件
from fastapi import Response
import json

class MaskingMiddleware:
    """脱敏中间件"""

    async def __call__(self, request, call_next):
        response = await call_next(request)

        # 只处理 JSON 响应
        if response.headers.get("content-type") == "application/json":
            body = response.body.decode()
            data = json.loads(body)

            # 脱敏敏感字段
            masked_data = DataMasker.mask_data(data)

            # 重建响应
            masked_body = json.dumps(masked_data).encode()
            response = Response(
                content=masked_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type="application/json"
            )

        return response
```

---

## API 安全

### 输入验证

```python
# backend/core/security/validation.py

from pydantic import BaseModel, validator, Field
from typing import Optional
import re

class ProductCreateSchema(BaseModel):
    """产品创建验证"""

    asin: str = Field(..., min_length=10, max_length=10, regex=r"^[A-Z0-9]+$")
    title: str = Field(..., min_length=5, max_length=200)
    brand: Optional[str] = Field(None, max_length=100)
    price: Optional[float] = Field(None, gt=0, le=10000)

    @validator("asin")
    def validate_asin(cls, v):
        """验证 ASIN 格式"""
        if not re.match(r"^[A-Z0-9]{10}$", v):
            raise ValueError("Invalid ASIN format")
        return v

    @validator("title")
    def validate_title(cls, v):
        """验证标题"""
        # 检查 SQL 注入特征
        sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "UNION"]
        v_upper = v.upper()
        for keyword in sql_keywords:
            if keyword in v_upper:
                raise ValueError(f"Invalid characters in title")
        return v

class OrderUpdateSchema(BaseModel):
    """订单更新验证"""

    status: str = Field(..., regex=r"^(pending|shipped|delivered|cancelled)$")
    tracking_number: Optional[str] = Field(None, regex=r"^[A-Za-z0-9]+$")

    @validator("status")
    def validate_status_transition(cls, v, values):
        """验证状态转换"""
        # 这里可以添加状态转换逻辑
        return v
```

### SQL 注入防护

```python
# backend/core/security/sql_injection.py

import re
from typing import List, Tuple

SQL_INJECTION_PATTERNS = [
    r"(\bunion\b.*\bselect\b)",
    r"(\bselect\b.*\bfrom\b)",
    r"(\binsert\b.*\binto\b)",
    r"(\bupdate\b.*\bset\b)",
    r"(\bdelete\b.*\bfrom\b)",
    r"(\bdrop\b.*\btable\b)",
    r"(--|;|/\*|\*/|xp_|sp_)",
    r"(\bexec\b|\bexecute\b)",
    r"(\bcast\b|\bconvert\b)",
    r"(0x[0-9a-f]+)",
]

SQL_INJECTION_REGEX = re.compile(
    "|".join(SQL_INJECTION_PATTERNS),
    re.IGNORECASE | re.MULTILINE
)

class SQLInjectionChecker:
    """SQL 注入检测器"""

    @staticmethod
    def check_input(value: str) -> bool:
        """检查输入是否包含 SQL 注入特征"""
        if not isinstance(value, str):
            return False

        return SQL_INJECTION_REGEX.search(value) is not None

    @staticmethod
    def sanitize_input(value: str) -> str:
        """清理输入"""
        # 移除危险字符
        dangerous_chars = ["'", ";", "--", "/*", "*/", "xp_", "sp_"]
        result = value

        for char in dangerous_chars:
            result = result.replace(char, "")

        return result

    @staticmethod
    def check_dict(data: dict) -> List[str]:
        """检查字典中的所有字段"""
        suspicious_fields = []

        for key, value in data.items():
            if isinstance(value, str):
                if SQLInjectionChecker.check_input(value):
                    suspicious_fields.append(key)
            elif isinstance(value, dict):
                suspicious_fields.extend(
                    f"{key}.{k}" for k in SQLInjectionChecker.check_dict(value)
                )
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        suspicious_fields.extend(
                            f"{key}.{i}.{k}" for k in SQLInjectionChecker.check_dict(item)
                        )

        return suspicious_fields

# FastAPI 依赖注入
from fastapi import HTTPException

async def validate_sql_injection(data: dict = Body(...)):
    """验证 SQL 注入"""
    suspicious_fields = SQLInjectionChecker.check_dict(data)

    if suspicious_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Suspicious input detected in fields: {', '.join(suspicious_fields)}"
        )

    return data
```

### XSS 防护

```python
# backend/core/security/xss.py

import html
import re

XSS_PATTERNS = [
    r"<script[^>]*>.*?</script>",
    r"javascript:",
    r"on\w+\s*=",
    r"<iframe[^>]*>.*?</iframe>",
    r"<embed[^>]*>.*?</embed>",
    r"<object[^>]*>.*?</object>",
]

XSS_REGEX = re.compile("|".join(XSS_PATTERNS), re.IGNORECASE | re.DOTALL)

class XSSChecker:
    """XSS 攻击检测器"""

    @staticmethod
    def check_input(value: str) -> bool:
        """检查输入是否包含 XSS 特征"""
        if not isinstance(value, str):
            return False

        return XSS_REGEX.search(value) is not None

    @staticmethod
    def sanitize_input(value: str) -> str:
        """清理 HTML 输入"""
        # 转义 HTML 特殊字符
        return html.escape(value, quote=True)

    @staticmethod
    def strip_tags(value: str) -> str:
        """移除所有 HTML 标签"""
        return re.sub(r"<[^>]+>", "", value)

# HTML 响应头
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
}
```

### CSRF 防护

```python
# backend/core/security/csrf.py

import secrets
from fastapi import Request, HTTPException

class CSRFProtection:
    """CSRF 保护"""

    def __init__(self):
        self.tokens = {}

    def generate_token(self) -> str:
        """生成 CSRF Token"""
        return secrets.token_urlsafe(32)

    def validate_token(self, request: Request, token: str) -> bool:
        """验证 CSRF Token"""
        # 从 session 获取预期 token
        expected_token = request.session.get("csrf_token")

        if not expected_token or not token:
            return False

        return secrets.compare_digest(expected_token, token)

# FastAPI 中间件
from starlette.middleware.base import BaseHTTPMiddleware

class CSRFMiddleware(BaseHTTPMiddleware):
    """CSRF 中间件"""

    async def dispatch(self, request: Request, call_next):
        # 对于修改操作，验证 CSRF Token
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            csrf_token = request.headers.get("X-CSRF-Token")

            if not csrf_token or not csrf_manager.validate_token(request, csrf_token):
                raise HTTPException(status_code=403, detail="Invalid CSRF token")

        # 为 GET 请求生成新 token
        if request.method == "GET":
            new_token = csrf_manager.generate_token()
            request.session["csrf_token"] = new_token

        response = await call_next(request)

        # 添加 CSRF Token 到响应头
        if request.method == "GET":
            response.headers["X-CSRF-Token"] = new_token

        return response
```

---

## 基础设施安全

### Docker 安全

```dockerfile
# Dockerfile.security

# 使用最小化基础镜像
FROM python:3.11-slim as builder

# 非root 用户运行
RUN adduser --disabled-password --gecos '' appuser

# 只安装必要的依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

# 复制依赖
COPY --from=builder /root/.local /root/.local

# 复制应用代码
COPY --chown=appuser:appuser . /app

# 切换到非root 用户
USER appuser
WORKDIR /app

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# 只暴露必要端口
EXPOSE 8000

# 安全选项
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 网络隔离

```yaml
# docker-compose.security.yml
version: '3.8'

services:
  # 公共服务 (可访问外部)
  nginx:
    networks:
      - public
      - private

  # API 服务 (只在内网)
  api:
    networks:
      - private
    expose:
      - "8000"
    # 不映射端口到宿主机

  # 数据库 (只在内网)
  postgres:
    networks:
      - private
    expose:
      - "5432"
    environment:
      - POSTGRES_HOST_AUTH_METHOD=scram-sha-256

networks:
  public:
    driver: bridge
  private:
    driver: bridge
    internal: true  # 完全隔离
```

---

## 合规要求

### GDPR 合规

```python
# backend/core/security/gdpr.py

class GDPRManager:
    """GDPR 合规管理器"""

    @staticmethod
    async def export_user_data(user_id: str) -> dict:
        """导出用户数据 (数据可携权)"""
        user_data = {
            "profile": await get_user_profile(user_id),
            "orders": await get_user_orders(user_id),
            "messages": await get_user_messages(user_id),
            "activities": await get_user_activities(user_id)
        }

        return user_data

    @staticmethod
    async def delete_user_data(user_id: str) -> bool:
        """删除用户数据 (被遗忘权)"""
        # 匿名化而不是删除 (保留审计记录)
        await anonymize_user_profile(user_id)
        await anonymize_user_orders(user_id)

        return True

    @staticmethod
    async def get_consent_status(user_id: str) -> dict:
        """获取用户同意状态"""
        return {
            "analytics": True,
            "marketing": False,
            "data_processing": True,
            "updated_at": "2024-01-01T00:00:00Z"
        }
```

### 审计日志

```python
# backend/core/security/audit.py

from datetime import datetime
from enum import Enum

class AuditAction(Enum):
    """审计动作"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"

class AuditLogger:
    """审计日志记录器"""

    async def log(
        self,
        user_id: str,
        action: AuditAction,
        resource: str,
        resource_id: str = None,
        details: dict = None,
        ip_address: str = None,
        user_agent: str = None
    ):
        """记录审计日志"""

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action.value,
            "resource": resource,
            "resource_id": resource_id,
            "details": details,
            "ip_address": ip_address,
            "user_agent": user_agent
        }

        # 写入审计日志表
        await save_audit_log(log_entry)

        # 关键操作发送到 SIEM
        if action in [AuditAction.DELETE, AuditAction.EXPORT]:
            await send_to_siem(log_entry)
```

---

**下一步**: 开始实施 Phase 1 - 基础框架搭建
