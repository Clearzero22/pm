# 个人信息保护与数据安全指南

> **保护账号凭据、Cookie、个人数据不被泄露的完整方案**
>
> ⚠️ **重要性**: 数据泄露可能导致账号被盗、财产损失、隐私曝光等严重后果

---

## 目录

1. [风险识别](#1-风险识别)
2. [凭据安全管理](#2-凭据安全管理)
3. [敏感数据加密](#3-敏感数据加密)
4. [日志脱敏处理](#4-日志脱敏处理)
5. [文件权限控制](#5-文件权限控制)
6. [网络安全防护](#6-网络安全防护)
7. [代码安全实践](#7-代码安全实践)
8. [应急响应方案](#8-应急响应方案)

---

## 1. 风险识别

### 1.1 敏感信息清单

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        需要保护的敏感信息                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  🔴 极高风险                                                                 │
│  ├── 账号密码 (email/password)                                              │
│  ├── Cookie/Session Token                                                   │
│  ├── 2FA 验证码                                                              │
│  └── API Keys (Anthropic/OpenAI/飞书等)                                     │
│                                                                             │
│  🟠 高风险                                                                   │
│  ├── 个人身份信息 (姓名、电话、地址)                                         │
│  ├── 支付信息 (信用卡、银行账户)                                             │
│  ├── 浏览器指纹数据                                                         │
│  └── IP 地址/代理信息                                                         │
│                                                                             │
│  🟡 中等风险                                                                 │
│  ├── 操作日志 (可能泄露行为模式)                                             │
│  ├── 数据库连接字符串                                                       │
│  └── 配置文件路径                                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 常见泄露途径

| 泄露途径 | 风险示例 | 防范措施 |
|----------|----------|----------|
| **代码仓库** | 密码硬编码提交到 Git | .gitignore、密钥扫描 |
| **日志文件** | 明文记录账号密码 | 日志脱敏 |
| **配置文件** | config.yaml 明文存储 | 加密存储、环境变量 |
| **数据库** | 未加密存储 Cookie | 字段加密 |
| **网络传输** | HTTP 明文传输 | HTTPS/TLS |
| **文件权限** | 644 权限所有人可读 | 设置 600 权限 |
| **内存转储** | 进程内存包含敏感数据 | 及时清理 |

---

## 2. 凭据安全管理

### 2.1 绝对不要这样做

```python
# ❌ 错误示例：硬编码密码

# 错误 1: 直接写在代码里
email = "myemail@example.com"
password = "MyPassword123!"

# 错误 2: 提交到 Git
# config.py 包含敏感信息
AMAZON_PASSWORD = "secret123"

# 错误 3: 明文日志
logger.info(f"登录账号：{email}, 密码：{password}")

# 错误 4: 不安全的配置文件
# config.yaml (未加密)
amazon:
  email: myemail@example.com
  password: MyPassword123!
```

### 2.2 正确做法：环境变量

```python
# ✅ 正确示例：使用环境变量

import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 从环境变量读取
AMAZON_EMAIL = os.getenv("AMAZON_EMAIL")
AMAZON_PASSWORD = os.getenv("AMAZON_PASSWORD")

# 验证是否设置
if not AMAZON_EMAIL or not AMAZON_PASSWORD:
    raise ValueError("请设置 AMAZON_EMAIL 和 AMAZON_PASSWORD 环境变量")
```

```bash
# .env 文件 (必须加入 .gitignore)
# 亚马逊账号配置
AMAZON_EMAIL=myemail@example.com
AMAZON_PASSWORD=MySecurePassword123!

# API Keys
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx

# 数据库配置
DATABASE_URL=postgresql://user:pass@localhost/db
```

```gitignore
# .gitignore
# 敏感配置文件
.env
.env.local
.env.production
*.pem
*.key
cookies/
browser_data/
logs/*.log
config/secrets.yaml
```

### 2.3 密钥管理服务

```python
# src/security/secret_manager.py
import os
from typing import Optional
from pathlib import Path


class SecretManager:
    """
    密钥管理器
    
    支持多种密钥存储后端:
    - 环境变量
    - HashiCorp Vault
    - AWS Secrets Manager
    - 本地加密文件
    """
    
    def __init__(self, backend: str = "env"):
        self.backend = backend
        
        if backend == "vault":
            self._init_vault()
        elif backend == "aws":
            self._init_aws()
        elif backend == "file":
            self._init_file()
    
    def _init_vault(self):
        """初始化 HashiCorp Vault"""
        import hvac
        
        vault_url = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
        vault_token = os.getenv("VAULT_TOKEN")
        
        self.client = hvac.Client(url=vault_url, token=vault_token)
    
    def _init_aws(self):
        """初始化 AWS Secrets Manager"""
        import boto3
        self.client = boto3.client("secretsmanager")
        self.secret_name = os.getenv("AWS_SECRET_NAME")
    
    def _init_file(self):
        """初始化本地加密文件"""
        from cryptography.fernet import Fernet
        
        key_file = Path.home() / ".secret_key"
        
        if not key_file.exists():
            # 生成新密钥
            key = Fernet.generate_key()
            key_file.write_bytes(key)
            key_file.chmod(0o600)
        
        self.cipher = Fernet(key_file.read_bytes())
        self.secrets_file = Path.home() / ".secrets.enc"
    
    def get_secret(self, key: str) -> Optional[str]:
        """获取密钥"""
        if self.backend == "env":
            return os.getenv(key)
        
        elif self.backend == "vault":
            response = self.client.secrets.kv.v2.read_secret_version(
                path=f"secret/{key}"
            )
            return response["data"]["data"].get("value")
        
        elif self.backend == "aws":
            import json
            response = self.client.get_secret_value(SecretId=self.secret_name)
            secrets = json.loads(response["SecretString"])
            return secrets.get(key)
        
        elif self.backend == "file":
            if not self.secrets_file.exists():
                return None
            
            encrypted = self.secrets_file.read_bytes()
            decrypted = self.cipher.decrypt(encrypted)
            import json
            secrets = json.loads(decrypted.decode())
            return secrets.get(key)
    
    def set_secret(self, key: str, value: str):
        """设置密钥"""
        if self.backend == "file":
            import json
            
            # 读取现有密钥
            secrets = {}
            if self.secrets_file.exists():
                encrypted = self.secrets_file.read_bytes()
                decrypted = self.cipher.decrypt(encrypted)
                secrets = json.loads(decrypted.decode())
            
            # 更新
            secrets[key] = value
            
            # 加密保存
            encrypted = self.cipher.encrypt(
                json.dumps(secrets).encode()
            )
            self.secrets_file.write_bytes(encrypted)
            self.secrets_file.chmod(0o600)


# 使用示例
secrets = SecretManager(backend="env")

# 获取密钥
amazon_password = secrets.get_secret("AMAZON_PASSWORD")
api_key = secrets.get_secret("ANTHROPIC_API_KEY")
```

---

## 3. 敏感数据加密

### 3.1 Cookie 加密存储

```python
# src/security/cookie_encrypt.py
import json
import base64
from pathlib import Path
from typing import List, Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptedCookieStorage:
    """
    加密 Cookie 存储
    
    使用 Fernet 对称加密
    """
    
    def __init__(
        self,
        storage_dir: str = "cookies",
        password: Optional[str] = None,
    ):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成或加载加密密钥
        self.key = self._load_or_create_key(password)
        self.cipher = Fernet(self.key)
    
    def _load_or_create_key(self, password: Optional[str] = None) -> bytes:
        """加载或生成加密密钥"""
        key_file = self.storage_dir / ".cookie_key"
        
        if key_file.exists():
            return key_file.read_bytes()
        
        # 生成新密钥
        if password:
            # 从密码派生密钥
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            # 保存盐值
            (self.storage_dir / ".salt").write_bytes(salt)
        else:
            # 随机生成密钥
            key = Fernet.generate_key()
        
        key_file.write_bytes(key)
        key_file.chmod(0o600)  # 仅所有者可读写
        
        return key
    
    def save(
        self,
        account_email: str,
        cookies: List[Dict[str, Any]],
    ) -> bool:
        """加密保存 Cookie"""
        try:
            # 序列化
            data = json.dumps({
                "email": account_email,
                "cookies": cookies,
                "timestamp": self._get_timestamp(),
            }, indent=2)
            
            # 加密
            encrypted = self.cipher.encrypt(data.encode())
            
            # 保存
            safe_name = account_email.replace("@", "_at_")
            cookie_file = self.storage_dir / f"cookies_{safe_name}.enc"
            cookie_file.write_bytes(encrypted)
            cookie_file.chmod(0o600)
            
            print(f"[INFO] Cookie 已加密保存：{cookie_file}")
            return True
            
        except Exception as e:
            print(f"[ERROR] 保存 Cookie 失败：{e}")
            return False
    
    def load(self, account_email: str) -> Optional[List[Dict[str, Any]]]:
        """解密加载 Cookie"""
        safe_name = account_email.replace("@", "_at_")
        cookie_file = self.storage_dir / f"cookies_{safe_name}.enc"
        
        if not cookie_file.exists():
            return None
        
        try:
            # 读取加密数据
            encrypted = cookie_file.read_bytes()
            
            # 解密
            decrypted = self.cipher.decrypt(encrypted)
            
            # 反序列化
            data = json.loads(decrypted.decode())
            
            # 验证邮箱匹配
            if data.get("email") != account_email:
                return None
            
            print(f"[INFO] Cookie 已解密加载")
            return data["cookies"]
            
        except Exception as e:
            print(f"[ERROR] 加载 Cookie 失败：{e}")
            return None
    
    def delete(self, account_email: str) -> bool:
        """删除 Cookie"""
        safe_name = account_email.replace("@", "_at_")
        cookie_file = self.storage_dir / f"cookies_{safe_name}.enc"
        
        if cookie_file.exists():
            # 安全删除（覆盖后删除）
            cookie_file.write_bytes(os.urandom(cookie_file.stat().st_size))
            cookie_file.unlink()
            print(f"[INFO] Cookie 已安全删除")
            return True
        
        return False
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
```

### 3.2 数据库字段加密

```python
# src/security/db_encrypt.py
from sqlalchemy import Column, String, LargeBinary, create_engine
from sqlalchemy.ext.declarative import declarative_base
from cryptography.fernet import Fernet
import base64
import json

Base = declarative_base()


class EncryptedCookie(Base):
    """加密 Cookie 模型"""
    __tablename__ = "encrypted_cookies"
    
    id = Column(String, primary_key=True)
    account_email = Column(String, nullable=False)
    encrypted_data = Column(LargeBinary, nullable=False)  # 加密数据
    
    def set_cookies(self, cookies: list, cipher: Fernet):
        """设置 Cookie（加密）"""
        data = json.dumps(cookies).encode()
        self.encrypted_data = cipher.encrypt(data)
    
    def get_cookies(self, cipher: Fernet) -> list:
        """获取 Cookie（解密）"""
        decrypted = cipher.decrypt(self.encrypted_data)
        return json.loads(decrypted.decode())


class EncryptedDatabase:
    """
    加密数据库管理器
    """
    
    def __init__(self, db_url: str, encryption_key: bytes):
        self.engine = create_engine(db_url)
        self.cipher = Fernet(encryption_key)
        Base.metadata.create_all(self.engine)
    
    def save_cookies(self, email: str, cookies: list):
        """保存加密 Cookie"""
        from sqlalchemy.orm import Session
        
        with Session(self.engine) as session:
            record = EncryptedCookie(id=email)
            record.account_email = email
            record.set_cookies(cookies, self.cipher)
            
            session.merge(record)
            session.commit()
    
    def load_cookies(self, email: str) -> list:
        """加载解密 Cookie"""
        from sqlalchemy.orm import Session
        
        with Session(self.engine) as session:
            record = session.get(EncryptedCookie, email)
            if record:
                return record.get_cookies(self.cipher)
            return None
```

---

## 4. 日志脱敏处理

### 4.1 敏感数据过滤器

```python
# src/security/log_sanitizer.py
import logging
import re
from typing import List, Tuple


class SensitiveDataFilter(logging.Filter):
    """
    敏感数据过滤器
    
    自动脱敏日志中的敏感信息
    """
    
    # 敏感数据模式
    PATTERNS: List[Tuple[str, str]] = [
        # 密码
        (r'password["\']?\s*[:=]\s*["\']?[\w@!#$%^&*]+["\']?', 'password=***'),
        (r'passwd["\']?\s*[:=]\s*["\']?[\w@!#$%^&*]+["\']?', 'passwd=***'),
        
        # 邮箱
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'email@***.***'),
        
        # 手机号
        (r'1[3-9]\d{9}', '1***-****-***'),
        (r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', '***-***-****'),
        
        # API Key
        (r'(sk-|key_|api_)[a-zA-Z0-9]{20,}', '\\1***'),
        (r'Bearer\s+[a-zA-Z0-9._-]+', 'Bearer ***'),
        
        # Cookie
        (r'cookie["\']?\s*[:=]\s*["\']?[^"\';]+["\']?', 'cookie=***'),
        (r'session[_-]?[a-z]*["\']?\s*[:=]\s*["\']?[\w.-]+["\']?', 'session=***'),
        
        # 信用卡
        (r'\b(?:\d{4}[- ]?){3}\d{4}\b', '****-****-****-****'),
        
        # 身份证号
        (r'[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]',
         'ID:***'),
    ]
    
    def __init__(self, custom_patterns: List[Tuple[str, str]] = None):
        super().__init__()
        self.patterns = self.PATTERNS + (custom_patterns or [])
        self.compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), replacement)
            for pattern, replacement in self.patterns
        ]
    
    def filter(self, record) -> bool:
        """过滤敏感数据"""
        # 处理消息
        if isinstance(record.msg, str):
            record.msg = self._sanitize(record.msg)
        
        # 处理参数
        if record.args:
            if isinstance(record.args, tuple):
                record.args = tuple(self._sanitize(str(arg)) for arg in record.args)
            elif isinstance(record.args, dict):
                record.args = {
                    k: self._sanitize(str(v)) for k, v in record.args.items()
                }
        
        return True
    
    def _sanitize(self, text: str) -> str:
        """脱敏文本"""
        if not text:
            return text
        
        for pattern, replacement in self.compiled_patterns:
            text = pattern.sub(replacement, text)
        
        return text


# 配置日志
def setup_secure_logging(level=logging.INFO):
    """设置安全日志"""
    # 创建过滤器
    sanitizer = SensitiveDataFilter()
    
    # 配置处理器
    handler = logging.FileHandler("logs/app.log")
    handler.addFilter(sanitizer)
    
    # 配置格式
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    
    # 配置根日志
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger
```

### 4.2 使用示例

```python
# 日志输出示例
logger = setup_secure_logging()

# 这些日志会被自动脱敏
logger.info(f"用户登录：email={email}, password={password}")
# 输出：用户登录：email=email@***.***, password=***

logger.info(f"API Key: {api_key}")
# 输出：API Key: ***

logger.info(f"Cookie: {cookie_value}")
# 输出：Cookie: ***
```

---

## 5. 文件权限控制

### 5.1 安全文件权限

```python
# src/security/file_permissions.py
import os
import stat
from pathlib import Path
from typing import Union


class SecureFilePermissions:
    """
    安全文件权限管理器
    """
    
    @staticmethod
    def set_secure(path: Union[str, Path]):
        """
        设置安全权限
        
        Linux/Mac: 600 (仅所有者读写)
        Windows: 限制为当前用户
        """
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在：{path}")
        
        if os.name == "nt":
            # Windows
            import win32security
            import ntsecuritycon as con
            
            sd = win32security.GetFileSecurity(
                str(path), win32security.DACL_SECURITY_INFORMATION
            )
            
            dacl = win32security.ACL()
            # 仅当前用户可访问
            user = win32security.GetTokenInformation(
                win32security.OpenProcessToken(
                    win32security.GetCurrentProcess(),
                    win32security.TOKEN_QUERY
                ),
                win32security.TokenUser
            )[0]
            
            dacl.AddAccessAllowedAce(
                win32security.ACL_REVISION,
                con.FILE_ALL_ACCESS,
                user
            )
            
            sd.SetSecurityDescriptorDacl(1, dacl, 0)
            win32security.SetFileSecurity(
                str(path), win32security.DACL_SECURITY_INFORMATION, sd
            )
        else:
            # Linux/Mac: 600
            path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    
    @staticmethod
    def verify_permissions(path: Union[str, Path]) -> bool:
        """验证文件权限是否安全"""
        path = Path(path)
        
        if not path.exists():
            return False
        
        mode = path.stat().st_mode
        
        # 检查是否有组或其他用户权限
        if mode & stat.S_IRGRP:  # 组可读
            return False
        if mode & stat.S_IWGRP:  # 组可写
            return False
        if mode & stat.S_IROTH:  # 其他用户可读
            return False
        if mode & stat.S_IWOTH:  # 其他用户可写
            return False
        
        return True
    
    @staticmethod
    def secure_create(path: Union[str, Path], content: bytes = None):
        """安全创建文件（先设置权限再写入）"""
        path = Path(path)
        
        # 创建空文件
        path.touch()
        
        # 设置权限
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)
        
        # 写入内容
        if content:
            path.write_bytes(content)


# 使用示例
SecureFilePermissions.set_secure("cookies/amazon.enc")
SecureFilePermissions.set_secure(".env")
SecureFilePermissions.set_secure("logs/app.log")
```

### 5.2 目录安全检查

```python
# scripts/security_check.py
#!/usr/bin/env python3
"""
安全检查脚本

检查项目中的敏感文件权限
"""

import os
import stat
from pathlib import Path


SENSITIVE_FILES = [
    ".env",
    ".env.local",
    ".env.production",
    "config/secrets.yaml",
    "cookies/",
    "browser_data/",
    "*.key",
    "*.pem",
    "*.enc",
]


def check_file_permissions():
    """检查文件权限"""
    print("=" * 60)
    print("文件权限安全检查")
    print("=" * 60)
    
    issues = []
    
    for root, dirs, files in os.walk("."):
        # 跳过某些目录
        if any(skip in root for skip in [".git", "node_modules", "__pycache__"]):
            continue
        
        for file in files:
            file_path = Path(root) / file
            
            # 检查是否是敏感文件
            is_sensitive = any(
                file.match(pattern) or str(file_path).startswith(pattern.rstrip("/"))
                for pattern in SENSITIVE_FILES
            )
            
            if is_sensitive:
                mode = file_path.stat().st_mode
                
                # 检查权限
                if mode & stat.S_IRGRP:
                    issues.append(f"⚠️  {file_path}: 组用户可读")
                if mode & stat.S_IWGRP:
                    issues.append(f"⚠️  {file_path}: 组用户可写")
                if mode & stat.S_IROTH:
                    issues.append(f"⚠️  {file_path}: 其他用户可读")
                if mode & stat.S_IWOTH:
                    issues.append(f"⚠️  {file_path}: 其他用户可写")
    
    if issues:
        print("\n发现以下安全问题:\n")
        for issue in issues:
            print(f"  {issue}")
        print(f"\n共发现 {len(issues)} 个问题")
        return False
    else:
        print("\n✅ 所有敏感文件权限安全")
        return True


def check_gitignore():
    """检查 .gitignore 配置"""
    print("\n" + "=" * 60)
    print(".gitignore 检查")
    print("=" * 60)
    
    gitignore_path = Path(".gitignore")
    
    if not gitignore_path.exists():
        print("❌ .gitignore 文件不存在")
        return False
    
    content = gitignore_path.read_text()
    
    required_entries = [
        ".env",
        ".env.*",
        "cookies/",
        "browser_data/",
        "*.key",
        "*.pem",
        "logs/",
    ]
    
    missing = []
    for entry in required_entries:
        if entry not in content:
            missing.append(entry)
    
    if missing:
        print(f"\n⚠️  .gitignore 缺少以下条目:\n")
        for entry in missing:
            print(f"  - {entry}")
        return False
    else:
        print("\n✅ .gitignore 配置完整")
        return True


if __name__ == "__main__":
    perm_ok = check_file_permissions()
    git_ok = check_gitignore()
    
    print("\n" + "=" * 60)
    print("安全检查总结")
    print("=" * 60)
    
    if perm_ok and git_ok:
        print("✅ 所有安全检查通过")
    else:
        print("❌ 发现安全问题，请及时修复")
        exit(1)
```

---

## 6. 网络安全防护

### 6.1 HTTPS 强制

```python
# src/security/https_config.py
import ssl
import aiohttp


def create_secure_session() -> aiohttp.ClientSession:
    """创建安全的 HTTP 会话"""
    # SSL 配置
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    
    # 禁用不安全的协议
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    
    # 创建会话
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    return aiohttp.ClientSession(connector=connector)


# 使用示例
async def fetch_data(url: str):
    """安全获取数据"""
    # 强制 HTTPS
    if not url.startswith("https://"):
        raise ValueError("必须使用 HTTPS 协议")
    
    session = create_secure_session()
    
    async with session.get(url) as response:
        return await response.text()
```

### 6.2 代理安全

```python
# src/security/proxy_config.py
from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class ProxyConfig:
    """代理配置"""
    server: str
    username: Optional[str] = None
    password: Optional[str] = None
    
    def to_dict(self) -> dict:
        """转换为字典（密码脱敏）"""
        return {
            "server": self.server,
            "username": self.username,
            "password": "***" if self.password else None,
        }
    
    def to_playwright(self) -> dict:
        """转换为 Playwright 格式"""
        config = {"server": self.server}
        if self.username and self.password:
            config["username"] = self.username
            config["password"] = self.password
        return config


def load_proxy_config() -> Optional[ProxyConfig]:
    """从环境变量加载代理配置"""
    server = os.getenv("PROXY_SERVER")
    
    if not server:
        return None
    
    return ProxyConfig(
        server=server,
        username=os.getenv("PROXY_USERNAME"),
        password=os.getenv("PROXY_PASSWORD"),
    )
```

---

## 7. 代码安全实践

### 7.1 Git 提交前检查

```python
# .git/hooks/pre-commit
#!/bin/bash
# Git 提交前检查钩子

echo "运行安全检查..."

# 检查是否有敏感文件被暂存
SENSITIVE_PATTERNS=(
    "\.env$"
    "\.pem$"
    "\.key$"
    "password.*\.py"
    "secret.*\.py"
)

for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    if git diff --cached --name-only | grep -q "$pattern"; then
        echo "❌ 错误：检测到敏感文件"
        echo "请确保以下文件已加入 .gitignore:"
        git diff --cached --name-only | grep "$pattern"
        exit 1
    fi
done

# 使用 gitleaks 扫描密钥
if command -v gitleaks &> /dev/null; then
    echo "扫描密钥泄露..."
    if ! gitleaks detect --staged --verbose; then
        echo "❌ 发现密钥泄露"
        exit 1
    fi
fi

echo "✅ 安全检查通过"
```

### 7.2 密钥扫描工具

```bash
# 安装 gitleaks
pip install gitleaks

# 扫描整个项目
gitleaks detect --source . --verbose

# 扫描暂存文件
gitleaks detect --staged --verbose

# 配置 gitleaks
# .gitleaks.toml
title = "gitleaks config"

[[rules]]
description = "Password in file"
id = "password-file"
regex = '''(?i)(password|passwd|pwd)\s*[:=]\s*['"][^'"]{8,}['"]'''
tags = ["password"]
```

---

## 8. 应急响应方案

### 8.1 泄露应急流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        数据泄露应急响应流程                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. 发现泄露                                                                │
│     │                                                                       │
│     ▼                                                                       │
│  2. 立即评估泄露范围                                                        │
│     │                                                                       │
│     ▼                                                                       │
│  3. 紧急措施                                                                │
│     ├── 修改泄露的密码                                                      │
│     ├── 撤销泄露的 API Key                                                  │
│     ├── 使泄露的 Cookie 失效                                                  │
│     └── 通知相关人员                                                        │
│     │                                                                       │
│     ▼                                                                       │
│  4. 调查原因                                                                │
│     │                                                                       │
│     ▼                                                                       │
│  5. 修复漏洞                                                                │
│     │                                                                       │
│     ▼                                                                       │
│  6. 加强防护                                                                │
│     │                                                                       │
│     ▼                                                                       │
│  7. 记录总结                                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 应急脚本

```python
# scripts/emergency_response.py
#!/usr/bin/env python3
"""
应急响应脚本

数据泄露时快速响应
"""

import asyncio
import os
from pathlib import Path


class EmergencyResponse:
    """应急响应处理器"""
    
    def __init__(self):
        self.email = os.getenv("AMAZON_EMAIL")
    
    async def revoke_all_sessions(self):
        """撤销所有会话（需要登录亚马逊后台操作）"""
        print("⚠️  请立即执行以下操作:")
        print("1. 登录亚马逊卖家后台")
        print("2. 进入账户设置")
        print("3. 点击'注销所有设备'")
        print("4. 修改登录密码")
    
    def rotate_api_keys(self):
        """轮换 API Keys"""
        print("\n⚠️  请轮换以下 API Keys:")
        print("- Anthropic API Key")
        print("- OpenAI API Key")
        print("- 飞书 API Key")
        print("\n操作步骤:")
        print("1. 登录对应平台")
        print("2. 撤销现有 Key")
        print("3. 生成新 Key")
        print("4. 更新 .env 文件")
    
    def invalidate_cookies(self):
        """使 Cookie 失效"""
        cookie_dir = Path("cookies")
        
        if cookie_dir.exists():
            # 删除所有 Cookie 文件
            for cookie_file in cookie_dir.glob("*.enc"):
                cookie_file.unlink()
            
            print(f"✅ 已删除 {cookie_dir} 下所有 Cookie 文件")
        
        browser_dir = Path("browser_data")
        
        if browser_dir.exists():
            print(f"\n⚠️  请手动删除浏览器数据目录：{browser_dir}")
    
    def notify_team(self):
        """通知团队"""
        print("\n⚠️  请立即通知以下人员:")
        print("- 项目负责人")
        print("- 安全团队")
        print("- 相关开发人员")
    
    async def full_response(self):
        """完整应急响应"""
        print("=" * 60)
        print("数据泄露应急响应")
        print("=" * 60)
        
        await self.revoke_all_sessions()
        self.rotate_api_keys()
        self.invalidate_cookies()
        self.notify_team()
        
        print("\n" + "=" * 60)
        print("应急响应完成")
        print("=" * 60)


if __name__ == "__main__":
    response = EmergencyResponse()
    asyncio.run(response.full_response())
```

### 8.3 安全检查清单

```markdown
# security/checklist.md

## 日常安全检查

### 每周检查
- [ ] 检查日志文件是否有敏感信息泄露
- [ ] 验证 .gitignore 配置
- [ ] 检查文件权限
- [ ] 审查访问日志

### 每月检查
- [ ] 轮换 API Keys
- [ ] 检查依赖包安全漏洞
- [ ] 审查代码中的硬编码密码
- [ ] 更新安全策略

### 每季度检查
- [ ] 修改登录密码
- [ ] 审查账户访问权限
- [ ] 安全培训
- [ ] 应急演练
```

---

## 附录：安全配置模板

### A. 完整 .env 示例

```bash
# .env.example (模板，不要填入真实值)

# 亚马逊账号
AMAZON_EMAIL=your_email@example.com
AMAZON_PASSWORD=  # 从密钥管理器获取

# API Keys
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
FEISHU_APP_ID=
FEISHU_APP_SECRET=

# 数据库
DATABASE_URL=postgresql://user:pass@localhost/db

# 加密密钥
ENCRYPTION_KEY=  # 使用 Python 生成：Fernet.generate_key()

# 代理配置
PROXY_SERVER=
PROXY_USERNAME=
PROXY_PASSWORD=

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### B. Docker 安全配置

```dockerfile
# Dockerfile
FROM python:3.11-slim

# 不运行 root 用户
RUN useradd -m -u 1000 appuser

WORKDIR /app

# 复制依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY --chown=appuser:appuser . .

# 设置权限
RUN chmod 600 .env* 2>/dev/null || true
RUN chmod -R 700 cookies/ browser_data/ 2>/dev/null || true

# 切换到普通用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health/live || exit 1

CMD ["python", "main.py"]
```

---

*文档版本：0.1.0 | 最后更新：2026-03-12*
