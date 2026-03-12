# 亚马逊登录状态持久化指南

> **一次登录，多次使用 - Cookie 和浏览器数据持久化完整方案**

---

## 目录

1. [持久化方案对比](#1-持久化方案对比)
2. [方案一：Cookie 持久化](#2-方案一-cookie-持久化)
3. [方案二：浏览器用户数据目录](#3-方案二 - 浏览器用户数据目录)
4. [方案三：混合模式（推荐）](#4-方案三 - 混合模式推荐)
5. [完整代码实现](#5-完整代码实现)
6. [常见问题排查](#6-常见问题排查)

---

## 1. 持久化方案对比

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           持久化方案对比                                     │
├──────────────────┬──────────────────┬──────────────────┬────────────────────┤
│       特性        │   Cookie 持久化  │  用户数据目录    │    混合模式        │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ 实现难度         │ 简单             │ 简单             │ 中等              │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ 持久化效果       │ 7-30 天          │ 长期（数月）      │ 长期              │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ 安全性           │ 中等             │ 高               │ 高                │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ 跨设备支持       │ ✅ 支持          │ ❌ 不支持         │ ⚠️ 部分支持        │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ 防检测能力       │ 中等             │ 高（真实浏览器）  │ 高                │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ 推荐指数         │ ⭐⭐⭐            │ ⭐⭐⭐⭐           │ ⭐⭐⭐⭐⭐          │
└──────────────────┴──────────────────┴──────────────────┴────────────────────┘
```

---

## 2. 方案一：Cookie 持久化

### 2.1 原理

```
首次登录                         后续启动
┌─────────────┐                 ┌─────────────┐
│  输入账号   │                 │  读取 Cookie │
│  输入密码   │                 │  注入浏览器  │
│  完成登录   │────► 保存 Cookie │  验证状态   │
│             │                 │  ✓ 有效：直接使用
│             │                 │  ✗ 过期：重新登录
└─────────────┘                 └─────────────┘
```

### 2.2 Cookie 管理器实现

```python
# src/utils/cookie_manager.py
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CookieData:
    """Cookie 数据结构"""
    cookies: List[Dict[str, Any]]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: Optional[str] = None
    account_email: str = ""
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if not self.expires_at:
            return False
        
        expire_time = datetime.fromisoformat(self.expires_at)
        return datetime.now() > expire_time
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "cookies": self.cookies,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "account_email": self.account_email,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CookieData":
        """从字典创建"""
        return cls(
            cookies=data.get("cookies", []),
            created_at=data.get("created_at", ""),
            expires_at=data.get("expires_at"),
            account_email=data.get("account_email", ""),
        )


class CookieManager:
    """
    Cookie 管理器
    
    功能:
    - Cookie 保存/加载
    - 过期检测
    - 加密存储（可选）
    - 多账号管理
    """
    
    def __init__(
        self,
        storage_dir: str = "cookies",
        encryption: bool = False,
        encryption_key: Optional[bytes] = None,
    ):
        """
        初始化 Cookie 管理器
        
        Args:
            storage_dir: Cookie 存储目录
            encryption: 是否加密存储
            encryption_key: 加密密钥（None 则自动生成）
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.encryption = encryption
        if encryption:
            from cryptography.fernet import Fernet
            self.encryption_key = encryption_key or self._load_or_create_key()
            self.cipher = Fernet(self.encryption_key)
    
    def _load_or_create_key(self) -> bytes:
        """加载或生成加密密钥"""
        key_file = self.storage_dir / ".cookie_key"
        
        if key_file.exists():
            with open(key_file, "rb") as f:
                return f.read()
        else:
            from cryptography.fernet import Fernet
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            # 设置权限：仅所有者可读写
            key_file.chmod(0o600)
            return key
    
    def _get_cookie_file(self, account_email: str, suffix: str = "") -> Path:
        """获取 Cookie 文件路径"""
        # 将邮箱转换为安全文件名
        safe_name = account_email.replace("@", "_at_").replace(".", "_")
        filename = f"cookies_{safe_name}{suffix}.json"
        return self.storage_dir / filename
    
    def save_cookies(
        self,
        account_email: str,
        cookies: List[Dict[str, Any]],
        valid_days: int = 30,
    ) -> bool:
        """
        保存 Cookie
        
        Args:
            account_email: 账号邮箱
            cookies: Cookie 列表
            valid_days: 有效期（天）
            
        Returns:
            是否保存成功
        """
        try:
            from datetime import timedelta
            
            # 计算过期时间
            expires_at = datetime.now() + timedelta(days=valid_days)
            
            # 创建 Cookie 数据
            cookie_data = CookieData(
                cookies=cookies,
                account_email=account_email,
                expires_at=expires_at.isoformat(),
            )
            
            # 序列化
            data = json.dumps(cookie_data.to_dict(), indent=2)
            
            # 加密（可选）
            if self.encryption:
                data = self.cipher.encrypt(data.encode())
            
            # 保存
            cookie_file = self._get_cookie_file(account_email)
            with open(cookie_file, "wb" if self.encryption else "w") as f:
                if self.encryption:
                    f.write(data)
                else:
                    f.write(data)
            
            # 设置权限
            cookie_file.chmod(0o600)
            
            print(f"[INFO] Cookie 已保存：{cookie_file}")
            print(f"[INFO] 有效期至：{expires_at}")
            return True
            
        except Exception as e:
            print(f"[ERROR] 保存 Cookie 失败：{e}")
            return False
    
    def load_cookies(self, account_email: str) -> Optional[List[Dict[str, Any]]]:
        """
        加载 Cookie
        
        Args:
            account_email: 账号邮箱
            
        Returns:
            Cookie 列表，如果不存在或过期则返回 None
        """
        cookie_file = self._get_cookie_file(account_email)
        
        if not cookie_file.exists():
            print(f"[INFO] Cookie 文件不存在：{cookie_file}")
            return None
        
        try:
            # 读取
            with open(cookie_file, "rb" if self.encryption else "r") as f:
                data = f.read()
            
            # 解密（可选）
            if self.encryption:
                data = self.cipher.decrypt(data).decode()
            
            # 反序列化
            cookie_data = CookieData.from_dict(json.loads(data))
            
            # 检查过期
            if cookie_data.is_expired():
                print(f"[INFO] Cookie 已过期，删除旧文件")
                cookie_file.unlink()
                return None
            
            # 验证账号匹配
            if cookie_data.account_email != account_email:
                print(f"[WARNING] Cookie 账号不匹配")
                return None
            
            print(f"[INFO] Cookie 加载成功，有效期到：{cookie_data.expires_at}")
            return cookie_data.cookies
            
        except Exception as e:
            print(f"[ERROR] 加载 Cookie 失败：{e}")
            return None
    
    def delete_cookies(self, account_email: str) -> bool:
        """删除 Cookie"""
        cookie_file = self._get_cookie_file(account_email)
        
        if cookie_file.exists():
            cookie_file.unlink()
            print(f"[INFO] Cookie 已删除：{cookie_file}")
            return True
        
        return False
    
    def list_accounts(self) -> List[str]:
        """列出所有已保存的账号"""
        accounts = []
        
        for cookie_file in self.storage_dir.glob("cookies_*.json"):
            # 从文件名提取邮箱
            name = cookie_file.stem.replace("cookies_", "")
            email = name.replace("_at_", "@").replace("_", ".")
            accounts.append(email)
        
        return accounts
    
    def get_cookie_stats(self, account_email: str) -> Dict[str, Any]:
        """获取 Cookie 统计信息"""
        cookie_file = self._get_cookie_file(account_email)
        
        if not cookie_file.exists():
            return {"exists": False}
        
        try:
            with open(cookie_file, "rb" if self.encryption else "r") as f:
                data = f.read()
            
            if self.encryption:
                data = self.cipher.decrypt(data).decode()
            
            cookie_data = CookieData.from_dict(json.loads(data))
            
            return {
                "exists": True,
                "account_email": cookie_data.account_email,
                "created_at": cookie_data.created_at,
                "expires_at": cookie_data.expires_at,
                "is_expired": cookie_data.is_expired(),
                "cookie_count": len(cookie_data.cookies),
            }
        except Exception as e:
            return {"exists": False, "error": str(e)}
```

### 2.3 集成到登录类

```python
# src/amazon/amazon_login.py (修改版)
from src.utils.cookie_manager import CookieManager


class AmazonLogin:
    def __init__(
        self,
        email: str,
        password: str,
        headless: bool = False,
        proxy: Optional[Dict[str, str]] = None,
        cookie_storage: str = "cookies/amazon",
        cookie_encryption: bool = True,
    ):
        self.email = email
        self.password = password
        self.headless = headless
        self.proxy = proxy
        
        # 初始化 Cookie 管理器
        self.cookie_manager = CookieManager(
            storage_dir=cookie_storage,
            encryption=cookie_encryption,
        )
        
        self.browser = None
        self.context = None
        self.page = None
    
    async def login(self, otp_code: Optional[str] = None, force_relogin: bool = False) -> bool:
        """
        登录（带 Cookie 缓存）
        
        Args:
            otp_code: 2FA 验证码
            force_relogin: 是否强制重新登录
            
        Returns:
            是否成功
        """
        # 1. 初始化浏览器
        await self.init_browser()
        
        # 2. 尝试使用 Cookie 登录（除非强制重新登录）
        if not force_relogin:
            cookies = self.cookie_manager.load_cookies(self.email)
            
            if cookies:
                await self.context.add_cookies(cookies)
                print("[INFO] 已加载 Cookie，尝试直接访问...")
                
                # 验证 Cookie 是否有效
                if await self.is_logged_in():
                    print("[SUCCESS] Cookie 有效，已自动登录")
                    return True
                else:
                    print("[INFO] Cookie 已过期，需要重新登录")
        
        # 3. 执行登录流程
        print("[INFO] 开始登录流程...")
        success = await self._do_login(otp_code)
        
        # 4. 保存 Cookie
        if success:
            cookies = await self.context.cookies()
            self.cookie_manager.save_cookies(self.email, cookies, valid_days=30)
        
        return success
    
    async def logout(self):
        """登出并清除 Cookie"""
        self.cookie_manager.delete_cookies(self.email)
        await self.close()
```

---

## 3. 方案二：浏览器用户数据目录

### 3.1 原理

```
使用真实浏览器的用户数据目录，保存完整的浏览器状态：
- Cookie
- LocalStorage
- IndexedDB
- 浏览器历史
- 保存的密码
- 会话数据

优势：最接近真实用户行为，最难被检测
```

### 3.2 实现方式

```python
# src/amazon/persistent_browser.py
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, Browser


class PersistentBrowser:
    """
    持久化浏览器
    
    使用用户数据目录保持浏览器状态
    """
    
    def __init__(
        self,
        user_data_dir: str = "browser_data/amazon",
        headless: bool = False,
        proxy: Optional[Dict[str, str]] = None,
    ):
        self.user_data_dir = Path(user_data_dir)
        self.user_data_dir.mkdir(parents=True, exist_ok=True)
        
        self.headless = headless
        self.proxy = proxy
        self.browser: Optional[Browser] = None
        self.page = None
        self.context = None
    
    async def launch(self):
        """启动浏览器（带用户数据目录）"""
        playwright = await async_playwright().start()
        
        # 浏览器参数
        browser_args = {
            "headless": self.headless,
            "user_data_dir": str(self.user_data_dir),  # 关键：用户数据目录
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                # 更多优化参数
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
            ],
        }
        
        # 代理配置
        if self.proxy:
            browser_args["proxy"] = self.proxy
        
        self.browser = await playwright.chromium.launch(**browser_args)
        
        # 创建上下文（不再需要手动设置 Cookie）
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/New_York",
        )
        
        self.page = await self.context.new_page()
        
        print(f"[INFO] 浏览器已启动，用户数据目录：{self.user_data_dir}")
        return self.page
    
    async def is_logged_in(self) -> bool:
        """检查登录状态"""
        await self.page.goto("https://sellercentral.amazon.com", wait_until="domcontentloaded")
        await self.page.wait_for_timeout(3000)
        
        # 检查是否有登出按钮
        sign_out = await self.page.query_selector("#nav-item-signout")
        return sign_out is not None
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
            print("[INFO] 浏览器已关闭，数据已保存到用户目录")
```

### 3.3 使用示例

```python
# examples/persistent_login_example.py
import asyncio
from src.amazon.persistent_browser import PersistentBrowser


async def main():
    # 创建持久化浏览器
    browser = PersistentBrowser(
        user_data_dir="browser_data/amazon_main账号",
        headless=False,  # 首次登录建议显示浏览器
    )
    
    try:
        # 启动浏览器
        await browser.launch()
        
        # 检查是否已登录
        if await browser.is_logged_in():
            print("✅ 已登录状态，直接使用！")
        else:
            print("❌ 未登录，请手动登录...")
            # 等待用户手动登录
            input("登录完成后按回车继续...")
        
        # 执行业务操作
        # await do_seller_tasks(browser.page)
        
        # 保持运行
        await asyncio.sleep(60)
        
    finally:
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 4. 方案三：混合模式（推荐）

### 4.1 原理

```
结合 Cookie 持久化 + 用户数据目录的优势：

1. 首次登录：使用用户数据目录，手动登录
2. 后续启动：优先使用 Cookie，失败则使用用户数据目录
3. 定期刷新：Cookie 快过期时，使用用户数据目录自动刷新
```

### 4.2 完整实现

```python
# src/amazon/smart_login.py
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta

from src.utils.cookie_manager import CookieManager
from src.amazon.persistent_browser import PersistentBrowser


class SmartAmazonLogin:
    """
    智能登录管理器
    
    混合模式：Cookie + 用户数据目录
    """
    
    def __init__(
        self,
        email: str,
        password: str,
        headless: bool = False,
        proxy: Optional[Dict[str, str]] = None,
        cookie_storage: str = "cookies/amazon",
        user_data_dir: str = "browser_data/amazon",
    ):
        self.email = email
        self.password = password
        self.headless = headless
        self.proxy = proxy
        
        # Cookie 管理器
        self.cookie_manager = CookieManager(
            storage_dir=cookie_storage,
            encryption=True,
        )
        
        # 持久化浏览器
        self.browser_manager = PersistentBrowser(
            user_data_dir=user_data_dir,
            headless=headless,
            proxy=proxy,
        )
        
        self.page = None
    
    async def login(
        self,
        otp_code: Optional[str] = None,
        auto_refresh: bool = True,
    ) -> bool:
        """
        智能登录
        
        策略:
        1. 优先尝试 Cookie 登录
        2. Cookie 失效则使用用户数据目录
        3. 都失败则执行完整登录流程
        
        Args:
            otp_code: 2FA 验证码
            auto_refresh: 是否自动刷新 Cookie
            
        Returns:
            是否成功
        """
        print(f"\n{'='*60}")
        print(f"智能登录：{self.email}")
        print(f"{'='*60}\n")
        
        # 1. 尝试 Cookie 登录
        print("[策略 1/3] 尝试 Cookie 登录...")
        if await self._login_with_cookie():
            print("✅ Cookie 登录成功\n")
            
            # 检查是否需要刷新
            if auto_refresh and self._cookie_expiring_soon():
                print("[INFO] Cookie 即将过期，自动刷新...")
                await self._refresh_cookie()
            
            return True
        
        # 2. 尝试用户数据目录
        print("[策略 2/3] 尝试用户数据目录登录...")
        if await self._login_with_user_data():
            print("✅ 用户数据目录登录成功\n")
            
            # 刷新 Cookie
            await self._refresh_cookie()
            return True
        
        # 3. 完整登录流程
        print("[策略 3/3] 执行完整登录流程...")
        if await self._full_login(otp_code):
            print("✅ 完整登录成功\n")
            return True
        
        print("❌ 所有登录方式都失败了\n")
        return False
    
    async def _login_with_cookie(self) -> bool:
        """使用 Cookie 登录"""
        # 加载 Cookie
        cookies = self.cookie_manager.load_cookies(self.email)
        if not cookies:
            print("[INFO] 没有可用的 Cookie")
            return False
        
        # 启动浏览器
        await self.browser_manager.launch()
        await self.browser_manager.context.add_cookies(cookies)
        
        self.page = self.browser_manager.page
        
        # 验证登录状态
        if await self.browser_manager.is_logged_in():
            return True
        
        print("[INFO] Cookie 已失效")
        await self.close()
        return False
    
    async def _login_with_user_data(self) -> bool:
        """使用用户数据目录登录"""
        await self.browser_manager.launch()
        self.page = self.browser_manager.page
        
        if await self.browser_manager.is_logged_in():
            return True
        
        print("[INFO] 用户数据目录中无有效登录")
        await self.close()
        return False
    
    async def _full_login(self, otp_code: Optional[str] = None) -> bool:
        """完整登录流程"""
        await self.browser_manager.launch()
        self.page = self.browser_manager.page
        
        # 访问登录页
        await self.page.goto("https://www.amazon.com/ap/signin")
        await self.page.wait_for_timeout(2000)
        
        # 输入邮箱
        await self.page.fill("#ap_email", self.email)
        await self.page.wait_for_timeout(500)
        
        # 输入密码
        await self.page.fill("#ap_password", self.password)
        await self.page.wait_for_timeout(500)
        
        # 提交
        await self.page.click("#signInSubmit")
        await self.page.wait_for_timeout(3000)
        
        # 处理 2FA
        if otp_code:
            2fa_input = await self.page.query_selector("#auth-otp-enter-otp")
            if 2fa_input:
                await 2fa_input.fill(otp_code)
                await self.page.click("#auth-otp-submit-button")
                await self.page.wait_for_timeout(3000)
        
        # 验证结果
        if await self.browser_manager.is_logged_in():
            # 保存 Cookie
            cookies = await self.browser_manager.context.cookies()
            self.cookie_manager.save_cookies(self.email, cookies, valid_days=30)
            return True
        
        return False
    
    async def _refresh_cookie(self):
        """刷新 Cookie"""
        cookies = await self.browser_manager.context.cookies()
        self.cookie_manager.save_cookies(self.email, cookies, valid_days=30)
        print("[INFO] Cookie 已刷新")
    
    def _cookie_expiring_soon(self, days_threshold: int = 7) -> bool:
        """检查 Cookie 是否即将过期"""
        stats = self.cookie_manager.get_cookie_stats(self.email)
        
        if not stats.get("exists"):
            return False
        
        expires_at = stats.get("expires_at")
        if not expires_at:
            return False
        
        expire_time = datetime.fromisoformat(expires_at)
        return datetime.now() + timedelta(days=days_threshold) > expire_time
    
    async def close(self):
        """关闭"""
        await self.browser_manager.close()
    
    def get_status(self) -> Dict[str, Any]:
        """获取登录状态"""
        cookie_stats = self.cookie_manager.get_cookie_stats(self.email)
        
        return {
            "email": self.email,
            "cookie_exists": cookie_stats.get("exists", False),
            "cookie_expired": not cookie_stats.get("is_expired", True),
            "cookie_expires_at": cookie_stats.get("expires_at"),
            "user_data_dir": self.browser_manager.user_data_dir,
        }
```

---

## 5. 完整代码实现

### 5.1 配置文件

```yaml
# config/login_config.yaml
# 登录配置

# 账号配置
accounts:
  - name: "主账号"
    email: "your_email@example.com"
    password_env: "AMAZON_PASSWORD"
    otp_env: "AMAZON_OTP"
    marketplace: "US"
    enabled: true

# 持久化配置
persistence:
  # Cookie 配置
  cookie:
    enabled: true
    storage_dir: "cookies/amazon"
    encryption: true
    valid_days: 30
    auto_refresh: true
    refresh_threshold_days: 7
  
  # 用户数据目录配置
  user_data:
    enabled: true
    base_dir: "browser_data"
    per_account: true  # 每个账号独立目录
  
  # 登录策略
  login_strategy: "hybrid"  # cookie_only / user_data_only / hybrid
  
# 浏览器配置
browser:
  headless: false  # 首次登录建议 false
  proxy:
    enabled: false
    server: "http://proxy:port"
    username: "user"
    password: "pass"

# 自动刷新配置
auto_refresh:
  enabled: true
  # 每天检查一次
  check_interval_hours: 24
  # Cookie 7 天内过期时刷新
  threshold_days: 7
```

### 5.2 自动刷新服务

```python
# src/services/cookie_refresh_service.py
import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

from src.amazon.smart_login import SmartAmazonLogin


logger = logging.getLogger(__name__)


class CookieRefreshService:
    """
    Cookie 自动刷新服务
    
    定期检查和刷新即将过期的 Cookie
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.accounts = config.get("accounts", [])
        self.running = False
    
    async def start(self):
        """启动服务"""
        self.running = True
        check_interval = self.config.get("check_interval_hours", 24) * 3600
        
        logger.info(f"Cookie 刷新服务已启动，检查间隔：{check_interval/3600}小时")
        
        while self.running:
            try:
                await self._check_and_refresh()
            except Exception as e:
                logger.error(f"刷新服务异常：{e}")
            
            await asyncio.sleep(check_interval)
    
    async def stop(self):
        """停止服务"""
        self.running = False
        logger.info("Cookie 刷新服务已停止")
    
    async def _check_and_refresh(self):
        """检查并刷新"""
        logger.info("开始检查 Cookie 状态...")
        
        for account in self.accounts:
            if not account.get("enabled", True):
                continue
            
            email = account["email"]
            threshold_days = self.config.get("threshold_days", 7)
            
            # 检查 Cookie 状态
            login = SmartAmazonLogin(
                email=email,
                password="",  # 不需要密码
                headless=True,
            )
            
            status = login.get_status()
            
            if status["cookie_exists"] and not status["cookie_expired"]:
                # 检查是否即将过期
                expires_at = datetime.fromisoformat(status["cookie_expires_at"])
                days_until_expire = (expires_at - datetime.now()).days
                
                if days_until_expire <= threshold_days:
                    logger.info(f"账号 {email} Cookie 将在 {days_until_expire} 天后过期，开始刷新...")
                    
                    # 执行刷新
                    success = await login.login(
                        otp_code=account.get("otp"),
                        auto_refresh=True,
                    )
                    
                    if success:
                        logger.info(f"✅ 账号 {email} Cookie 刷新成功")
                    else:
                        logger.error(f"❌ 账号 {email} Cookie 刷新失败")
            
            await login.close()
        
        logger.info("Cookie 检查完成")


# 使用示例
async def main():
    config = {
        "accounts": [
            {
                "email": "your_email@example.com",
                "password_env": "AMAZON_PASSWORD",
                "enabled": True,
            }
        ],
        "check_interval_hours": 24,
        "threshold_days": 7,
    }
    
    service = CookieRefreshService(config)
    
    try:
        await service.start()
    except KeyboardInterrupt:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())
```

### 5.3 CLI 工具

```python
# tools/cookie_manager_cli.py
import click
import json
from src.utils.cookie_manager import CookieManager


@click.group()
def cli():
    """Cookie 管理工具"""
    pass


@cli.command()
@click.option("--email", required=True, help="账号邮箱")
@click.option("--storage", default="cookies/amazon", help="Cookie 存储目录")
def status(email, storage):
    """查看 Cookie 状态"""
    manager = CookieManager(storage_dir=storage, encryption=True)
    stats = manager.get_cookie_stats(email)
    
    click.echo(f"\nCookie 状态：{email}")
    click.echo(f"{'='*40}")
    click.echo(f"存在：{stats.get('exists', False)}")
    
    if stats.get('exists'):
        click.echo(f"创建时间：{stats.get('created_at')}")
        click.echo(f"过期时间：{stats.get('expires_at')}")
        click.echo(f"已过期：{stats.get('is_expired', False)}")
        click.echo(f"Cookie 数量：{stats.get('cookie_count', 0)}")


@cli.command()
@click.option("--email", required=True, help="账号邮箱")
@click.option("--storage", default="cookies/amazon", help="Cookie 存储目录")
def delete(email, storage):
    """删除 Cookie"""
    manager = CookieManager(storage_dir=storage, encryption=True)
    
    if manager.delete_cookies(email):
        click.echo(f"✅ Cookie 已删除：{email}")
    else:
        click.echo(f"❌ Cookie 不存在：{email}")


@cli.command()
@click.option("--storage", default="cookies/amazon", help="Cookie 存储目录")
def list_accounts(storage):
    """列出所有账号"""
    manager = CookieManager(storage_dir=storage, encryption=True)
    accounts = manager.list_accounts()
    
    click.echo(f"\n已保存的账号 ({len(accounts)}):")
    click.echo(f"{'='*40}")
    
    for email in accounts:
        stats = manager.get_cookie_stats(email)
        status = "✅ 有效" if not stats.get('is_expired', True) else "❌ 过期"
        click.echo(f"  {email} - {status}")


@cli.command()
@click.option("--email", required=True, help="账号邮箱")
@click.option("--storage", default="cookies/amazon", help="Cookie 存储目录")
@click.option("--output", help="导出文件路径")
def export(email, storage, output):
    """导出 Cookie"""
    manager = CookieManager(storage_dir=storage, encryption=False)
    cookies = manager.load_cookies(email)
    
    if cookies:
        output_file = output or f"cookies_{email}.json"
        with open(output_file, "w") as f:
            json.dump(cookies, f, indent=2)
        click.echo(f"✅ Cookie 已导出：{output_file}")
    else:
        click.echo(f"❌ Cookie 不存在或已过期")


if __name__ == "__main__":
    cli()
```

---

## 6. 常见问题排查

### 6.1 Cookie 快速失效

| 原因 | 解决方案 |
|------|----------|
| 亚马逊强制登出 | 使用用户数据目录模式 |
| IP 地址变化 | 固定 IP 或使用相同地区代理 |
| 设备指纹变化 | 保持浏览器配置一致 |
| Cookie 被清除 | 启用加密存储，避免手动清理 |

### 6.2 登录状态检查

```python
# 调试脚本
async def debug_login_state(page):
    """调试登录状态"""
    # 获取所有 Cookie
    cookies = await page.context.cookies()
    print(f"Cookie 数量：{len(cookies)}")
    
    # 检查关键 Cookie
    key_cookies = ["session-token", "ubid-main", "x-main"]
    for name in key_cookies:
        cookie = next((c for c in cookies if c["name"] == name), None)
        if cookie:
            print(f"✅ {name}: 存在")
        else:
            print(f"❌ {name}: 缺失")
    
    # 检查 LocalStorage
    storage = await page.evaluate("() => localStorage")
    print(f"LocalStorage 项数：{len(storage)}")
    
    # 截图
    await page.screenshot(path="debug_login_state.png")
```

### 6.3 最佳实践总结

```markdown
## Cookie 持久化最佳实践

1. **首次登录**
   - 使用真实 IP 或固定代理
   - 显示浏览器界面（headless=false）
   - 手动完成可能的 2FA/CAPTCHA

2. **日常使用**
   - 优先使用 Cookie 登录
   - 设置 7 天提前刷新阈值
   - 定期（24 小时）检查状态

3. **安全存储**
   - 启用加密存储
   - 设置文件权限 0600
   - 定期备份 Cookie 文件

4. **多账号管理**
   - 每个账号独立 Cookie 文件
   - 每个账号独立用户数据目录
   - 避免同时登录多个账号

5. **异常处理**
   - Cookie 失效自动降级到完整登录
   - 登录失败记录详细日志
   - 连续失败发送告警
```

---

*文档版本：0.1.0 | 最后更新：2026-03-12*
