# 亚马逊店铺自动化登录技术文档

> ⚠️ **重要声明**
> 
> 本文档仅供学习和技术研究使用。自动化登录亚马逊店铺可能违反亚马逊服务条款。
> 请确保你的使用场景符合：
> - 亚马逊卖家平台服务条款
> - 当地法律法规
> - 公司合规要求
> 
> **推荐方案：优先使用亚马逊官方 SP-API（Selling Partner API）**

---

## 目录

1. [技术原理概述](#1-技术原理概述)
2. [方案对比](#2-方案对比)
3. [Playwright 实现方案](#3-playwright-实现方案)
4. [反检测策略](#4-反检测策略)
5. [安全实践](#5-安全实践)
6. [完整代码实现](#6-完整代码实现)
7. [故障排查](#7-故障排查)

---

## 1. 技术原理概述

### 1.1 亚马逊登录流程分析

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  访问登录页  │ ──► │  获取 CSRF   │ ──► │  提交表单   │ ──► │  验证跳转   │
│  /ap/signin │     │   Token     │     │  + 加密参数  │     │  /sellercentral │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
                                                                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  登录成功    │ ◄── │  设置 Cookie │ ◄── │  2FA 验证   │ ◄── │  风险评估   │
│  进入后台    │     │   Session   │     │  (可选)     │     │  CAPTCHA   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### 1.2 关键技术点

| 技术点 | 说明 | 难度 |
|--------|------|------|
| **Cookie 管理** | 维持登录状态的 Session Cookie | ⭐⭐ |
| **CSRF Token** | 表单提交时的安全令牌 | ⭐⭐⭐ |
| **设备指纹** | 浏览器特征、Canvas 指纹等 | ⭐⭐⭐⭐ |
| **行为分析** | 鼠标轨迹、输入节奏检测 | ⭐⭐⭐⭐ |
| **CAPTCHA** | 人机验证（滑块/图片） | ⭐⭐⭐⭐⭐ |
| **2FA** | 短信/认证器双重验证 | ⭐⭐⭐ |

---

## 2. 方案对比

### 2.1 三种主流方案

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           方案对比矩阵                                   │
├──────────────────┬──────────────────┬──────────────────┬────────────────┤
│       特性        │     Selenium     │    Playwright    │   纯 HTTP 请求   │
├──────────────────┼──────────────────┼──────────────────┼────────────────┤
│ 执行速度         │ 慢               │ 中等             │ 快             │
│ 检测风险         │ 高               │ 中               │ 极高           │
│ 实现难度         │ 低               │ 中等             │ 高             │
│ 支持 2FA         │ ✅               │ ✅               │ ❌             │
│ 支持 CAPTCHA     │ 手动处理         │ 手动处理         │ ❌             │
│ 维护成本         │ 高               │ 中等             │ 高             │
│ 推荐指数         │ ⭐⭐              │ ⭐⭐⭐⭐            │ ⭐              │
└──────────────────┴──────────────────┴──────────────────┴────────────────┘
```

### 2.2 推荐方案：Playwright

**选择理由：**
1. **更现代的架构** - 比 Selenium 更难被检测
2. **自动等待** - 内置智能等待机制
3. **多浏览器支持** - Chromium/Firefox/WebKit
4. **上下文隔离** - 可创建多个独立的浏览器上下文
5. **网络拦截** - 可拦截和修改网络请求

---

## 3. Playwright 实现方案

### 3.1 环境准备

```bash
# 1. 创建虚拟环境（如已存在可跳过）
uv venv .venv-login

# 2. 激活环境
source .venv-login/bin/activate

# 3. 安装 Playwright
uv add playwright

# 4. 安装浏览器
uv run playwright install chromium

# 5. 安装可选依赖（用于 Stealth 模式）
uv add playwright-stealth
```

### 3.2 项目结构

```
python_crawler/
├── src/
│   ├── __init__.py
│   ├── crawler.py
│   ├── amazon_login.py          # 新增：登录模块
│   ├── amazon_seller.py         # 新增：卖家后台操作
│   └── utils.py
├── config/
│   ├── __init__.py
│   └── settings.py              # 新增：配置文件
├── data/
│   └── cookies/                 # 新增：Cookie 存储目录
│       └── seller_cookies.json
├── .env                         # 新增：环境变量（敏感信息）
└── pyproject.toml
```

### 3.3 核心登录类设计

```python
# src/amazon_login.py
import asyncio
import json
import random
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from playwright_stealth import stealth_async


class AmazonLoginError(Exception):
    """登录异常基类"""
    pass


class CaptchaRequired(AmazonLoginError):
    """需要验证码"""
    pass


class TwoFactorRequired(AmazonLoginError):
    """需要双重验证"""
    pass


class AmazonLogin:
    """
    亚马逊登录自动化类
    
    支持功能:
    - 账号密码登录
    - Cookie 持久化（避免重复登录）
    - 2FA 验证码支持
    - 反检测配置
    """
    
    # 亚马逊卖家登录 URL
    LOGIN_URL = "https://sellercentral.amazon.com"
    SIGNIN_URL = "https://www.amazon.com/ap/signin"
    
    # CSS 选择器（可能需要根据实际页面调整）
    SELECTORS = {
        "email": "#ap_email",
        "password": "#ap_password",
        "submit": "#signInSubmit",
        "captcha": "#auth-captcha-image",
        "2fa_input": "#auth-otp-enter-otp",
        "2fa_submit": "#auth-otp-submit-button",
        "error_msg": ".a-alert-content",
    }
    
    def __init__(
        self,
        email: str,
        password: str,
        headless: bool = False,
        cookie_path: str = "data/cookies/seller_cookies.json",
        proxy: Optional[str] = None,
    ):
        self.email = email
        self.password = password
        self.headless = headless
        self.cookie_path = Path(cookie_path)
        self.proxy = proxy
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def init_browser(self):
        """初始化浏览器（带反检测配置）"""
        playwright = await async_playwright().start()
        
        # 浏览器启动参数
        browser_args = {
            "headless": self.headless,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ],
        }
        
        # 代理配置
        if self.proxy:
            browser_args["proxy"] = {"server": self.proxy}
        
        self.browser = await playwright.chromium.launch(**browser_args)
        
        # 创建浏览器上下文（模拟真实用户）
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="America/New_York",
            permissions=["geolocation"],
            geolocation={"latitude": 40.7128, "longitude": -74.0060},  # 纽约
            color_scheme="light",
        )
        
        # 应用 Stealth 反检测
        await stealth_async(self.context)
        
        self.page = await self.context.new_page()
        
        # 注入 JavaScript 隐藏自动化特征
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
        """)
        
        return self.page
    
    async def load_cookies(self) -> bool:
        """
        从文件加载 Cookie
        
        Returns:
            bool: 是否成功加载
        """
        if not self.cookie_path.exists():
            return False
        
        try:
            with open(self.cookie_path, "r") as f:
                cookies = json.load(f)
            
            await self.context.add_cookies(cookies)
            print(f"[INFO] 已加载 {len(cookies)} 个 Cookie")
            return True
        except Exception as e:
            print(f"[ERROR] 加载 Cookie 失败：{e}")
            return False
    
    async def save_cookies(self):
        """保存 Cookie 到文件"""
        try:
            cookies = await self.context.cookies()
            self.cookie_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cookie_path, "w") as f:
                json.dump(cookies, f, indent=2)
            print(f"[INFO] 已保存 {len(cookies)} 个 Cookie 到 {self.cookie_path}")
        except Exception as e:
            print(f"[ERROR] 保存 Cookie 失败：{e}")
    
    async def is_logged_in(self) -> bool:
        """
        检查是否已登录
        
        Returns:
            bool: 登录状态
        """
        await self.page.goto(self.LOGIN_URL, wait_until="domcontentloaded")
        await self.page.wait_for_timeout(3000)
        
        # 检查是否在卖家后台页面
        current_url = self.page.url
        if "sellercentral" in current_url:
            return True
        
        # 检查是否有登出按钮
        try:
            logout_btn = self.page.locator('a[href*="sign-out"]')
            return await logout_btn.count() > 0
        except:
            return False
    
    async def human_typing(self, selector: str, text: str):
        """
        模拟人类打字（随机延迟）
        
        Args:
            selector: CSS 选择器
            text: 要输入的文本
        """
        element = await self.page.wait_for_selector(selector)
        await element.click()
        
        # 清空输入框
        await self.page.keyboard.press("Control+A")
        await self.page.keyboard.press("Delete")
        
        # 逐字输入，模拟人类打字
        for char in text:
            await self.page.keyboard.type(char, delay=random.randint(50, 200))
            # 随机暂停
            if random.random() < 0.1:
                await self.page.wait_for_timeout(random.randint(100, 500))
    
    async def handle_captcha(self):
        """
        处理验证码（需要人工介入）
        
        Raises:
            CaptchaRequired: 当检测到验证码时抛出
        """
        captcha = self.page.locator(self.SELECTORS["captcha"])
        if await captcha.count() > 0:
            print("[WARNING] 检测到验证码，请在浏览器中手动完成")
            # 等待用户手动完成（最长 5 分钟）
            try:
                await self.page.wait_for_selector(
                    self.SELECTORS["captcha"],
                    state="detached",
                    timeout=300000,
                )
                print("[INFO] 验证码已完成")
            except:
                raise CaptchaRequired("验证码处理超时")
    
    async def handle_2fa(self, otp_code: Optional[str] = None):
        """
        处理双重验证
        
        Args:
            otp_code: 6 位验证码（如不提供则等待手动输入）
        """
        2fa_input = self.page.locator(self.SELECTORS["2fa_input"])
        if await 2fa_input.count() > 0:
            if otp_code:
                await self.human_typing(self.SELECTORS["2fa_input"], otp_code)
                await self.page.click(self.SELECTORS["2fa_submit"])
            else:
                print("[WARNING] 需要 2FA 验证码，请在浏览器中手动输入")
                # 等待用户手动完成
                await self.page.wait_for_timeout(300000)
    
    async def login(self, otp_code: Optional[str] = None) -> bool:
        """
        执行登录流程
        
        Args:
            otp_code: 2FA 验证码（可选）
            
        Returns:
            bool: 登录是否成功
            
        Raises:
            AmazonLoginError: 登录失败时抛出
        """
        # 1. 初始化浏览器
        await self.init_browser()
        
        # 2. 尝试加载 Cookie
        if await self.load_cookies():
            if await self.is_logged_in():
                print("[INFO] Cookie 有效，已自动登录")
                return True
            print("[INFO] Cookie 已过期，重新登录")
        
        # 3. 访问登录页面
        print(f"[INFO] 访问登录页面：{self.SIGNIN_URL}")
        await self.page.goto(self.SIGNIN_URL, wait_until="domcontentloaded")
        await self.page.wait_for_timeout(random.randint(2000, 4000))
        
        # 4. 输入邮箱
        print("[INFO] 输入邮箱账号")
        await self.human_typing(self.SELECTORS["email"], self.email)
        await self.page.wait_for_timeout(random.randint(500, 1000))
        
        # 5. 输入密码
        print("[INFO] 输入密码")
        await self.human_typing(self.SELECTORS["password"], self.password)
        await self.page.wait_for_timeout(random.randint(500, 1000))
        
        # 6. 点击登录按钮
        print("[INFO] 提交登录表单")
        await self.page.click(self.SELECTORS["submit"])
        await self.page.wait_for_timeout(3000)
        
        # 7. 检查是否需要验证码
        try:
            await self.handle_captcha()
        except CaptchaRequired:
            # 等待手动处理
            pass
        
        # 8. 检查是否需要 2FA
        await self.handle_2fa(otp_code)
        
        # 9. 等待跳转
        await self.page.wait_for_timeout(5000)
        
        # 10. 验证登录结果
        if await self.is_logged_in():
            print("[SUCCESS] 登录成功！")
            await self.save_cookies()
            return True
        else:
            # 检查错误信息
            try:
                error = await self.page.text_content(self.SELECTORS["error_msg"])
                if error and error.strip():
                    raise AmazonLoginError(f"登录失败：{error.strip()}")
            except:
                pass
            raise AmazonLoginError("登录失败，无法进入卖家后台")
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
```

---

## 4. 反检测策略

### 4.1 浏览器指纹伪装

```python
# 完整的反检测配置
ANTI_DETECT_CONFIG = {
    # 1. User-Agent（模拟真实浏览器）
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    
    # 2. 视口大小（常见分辨率）
    "viewport": {"width": 1920, "height": 1080},
    
    # 3. 时区和语言
    "timezone_id": "America/New_York",
    "locale": "en-US",
    "languages": ["en-US", "en"],
    
    # 4. 地理位置（可选）
    "geolocation": {"latitude": 40.7128, "longitude": -74.0060},
    
    # 5. 浏览器插件模拟
    "plugins": [1, 2, 3, 4, 5],
    
    # 6. Canvas 指纹噪声
    "canvas_noise": True,
    
    # 7. WebGL 供应商
    "webgl_vendor": "Intel Inc.",
    "webgl_renderer": "Intel Iris OpenGL Engine",
}
```

### 4.2 行为模拟

```python
class HumanBehaviorSimulator:
    """人类行为模拟器"""
    
    @staticmethod
    async def random_scroll(page):
        """随机滚动"""
        scroll_distance = random.randint(300, 800)
        scroll_delay = random.randint(100, 300)
        
        for _ in range(random.randint(2, 5)):
            await page.evaluate(f"window.scrollBy(0, {scroll_distance})")
            await page.wait_for_timeout(scroll_delay)
    
    @staticmethod
    async def random_mouse_move(page):
        """随机鼠标移动"""
        viewport = page.viewport_size
        x = random.randint(100, viewport["width"] - 100)
        y = random.randint(100, viewport["height"] - 100)
        
        # 贝塞尔曲线移动（更自然）
        await page.mouse.move(x, y, steps=random.randint(10, 30))
    
    @staticmethod
    async def random_delay():
        """随机延迟（人类思考时间）"""
        await asyncio.sleep(random.uniform(0.5, 2.0))
```

### 4.3 IP 代理策略

| 代理类型 | 推荐度 | 说明 |
|----------|--------|------|
| **住宅代理** | ⭐⭐⭐⭐⭐ | 最安全，来自真实 ISP |
| **移动代理** | ⭐⭐⭐⭐ | 来自移动网络，更难检测 |
| **数据中心代理** | ⭐⭐ | 容易被识别和封锁 |
| **免费代理** | ❌ | 绝对不要使用 |

```python
# 代理配置示例
PROXY_CONFIG = {
    "server": "http://proxy-server.com:8080",
    "username": "your_username",
    "password": "your_password",
}

# 使用代理创建浏览器上下文
context = await browser.new_context(proxy=PROXY_CONFIG)
```

---

## 5. 安全实践

### 5.1 凭据管理

**❌ 错误做法（硬编码）：**
```python
email = "myemail@example.com"
password = "MySecretPassword123"
```

**✅ 正确做法（环境变量）：**
```bash
# .env 文件（加入 .gitignore）
AMAZON_EMAIL=myemail@example.com
AMAZON_PASSWORD=MySecretPassword123
AMAZON_2FA_SECRET=JBSWY3DPEHPK3PXP
```

```python
# config/settings.py
from dotenv import load_dotenv
import os

load_dotenv()

AMAZON_EMAIL = os.getenv("AMAZON_EMAIL")
AMAZON_PASSWORD = os.getenv("AMAZON_PASSWORD")
AMAZON_2FA_SECRET = os.getenv("AMAZON_2FA_SECRET")
```

### 5.2 Cookie 加密存储

```python
from cryptography.fernet import Fernet

class SecureCookieStorage:
    """加密 Cookie 存储"""
    
    def __init__(self, key_file: str = ".cookie_key"):
        self.key_file = Path(key_file)
        self.key = self._load_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _load_or_create_key(self):
        if self.key_file.exists():
            with open(self.key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
            self.key_file.chmod(0o600)  # 仅所有者可读写
            return key
    
    def save(self, cookies: list, path: str):
        """加密保存"""
        encrypted = self.cipher.encrypt(json.dumps(cookies).encode())
        with open(path, "wb") as f:
            f.write(encrypted)
    
    def load(self, path: str) -> list:
        """解密加载"""
        with open(path, "rb") as f:
            decrypted = self.cipher.decrypt(f.read())
        return json.loads(decrypted.decode())
```

### 5.3 日志脱敏

```python
import logging
import re

class SensitiveDataFilter(logging.Filter):
    """敏感数据过滤器"""
    
    PATTERNS = [
        (r'password[=:]\s*["\']?[\w@!#$%^&*]+["\']?', 'password=***'),
        (r'email[=:]\s*["\']?[\w.]+@[\w.]+["\']?', 'email=***'),
        (r'otp[=:]\s*["\']?\d{6}["\']?', 'otp=***'),
    ]
    
    def filter(self, record):
        record.msg = str(record.msg)
        for pattern, replacement in self.PATTERNS:
            record.msg = re.sub(pattern, replacement, record.msg, flags=re.IGNORECASE)
        return True

# 配置日志
logger = logging.getLogger("amazon_login")
logger.addFilter(SensitiveDataFilter())
```

---

## 6. 完整代码实现

### 6.1 配置文件

```python
# config/settings.py
from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 亚马逊账号
    amazon_email: str
    amazon_password: str
    amazon_2fa_secret: Optional[str] = None
    
    # 浏览器配置
    headless: bool = False
    proxy: Optional[str] = None
    
    # Cookie 配置
    cookie_path: str = "data/cookies/seller_cookies.json"
    cookie_encryption: bool = True
    
    # 反检测配置
    random_delay_min: float = 0.5
    random_delay_max: float = 2.0
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
```

### 6.2 主程序入口

```python
# main_login.py
import asyncio
import logging
from src.amazon_login import AmazonLogin
from config.settings import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """主函数"""
    login = AmazonLogin(
        email=settings.amazon_email,
        password=settings.amazon_password,
        headless=settings.headless,
        cookie_path=settings.cookie_path,
        proxy=settings.proxy,
    )
    
    try:
        # 执行登录
        success = await login.login()
        
        if success:
            logger.info("登录成功！可以开始执行卖家后台操作")
            
            # 在这里添加你的业务逻辑
            # await do_seller_tasks(login.page)
            
            # 保持浏览器打开一段时间
            await asyncio.sleep(60)
        else:
            logger.error("登录失败")
    
    except Exception as e:
        logger.error(f"发生错误：{e}", exc_info=True)
    
    finally:
        await login.close()


if __name__ == "__main__":
    asyncio.run(main())
```

### 6.3 卖家后台操作示例

```python
# src/amazon_seller.py
from playwright.async_api import Page


class AmazonSellerCentral:
    """亚马逊卖家后台操作类"""
    
    def __init__(self, page: Page):
        self.page = page
    
    async def get_dashboard_data(self):
        """获取仪表盘数据"""
        await self.page.goto("https://sellercentral.amazon.com")
        
        # 提取销售数据
        sales_data = await self.page.locator(".sales-metric").all_text_contents()
        orders_data = await self.page.locator(".order-metric").all_text_contents()
        
        return {
            "sales": sales_data,
            "orders": orders_data,
        }
    
    async def get_inventory_status(self):
        """获取库存状态"""
        await self.page.goto("https://sellercentral.amazon.com/inventory")
        
        # 提取库存列表
        inventory_rows = await self.page.locator("table.inventory-table tbody tr").all()
        
        inventory = []
        for row in inventory_rows:
            cells = await row.locator("td").all()
            if len(cells) >= 5:
                inventory.append({
                    "sku": await cells[0].text_content(),
                    "name": await cells[1].text_content(),
                    "quantity": await cells[2].text_content(),
                    "status": await cells[3].text_content(),
                })
        
        return inventory
    
    async def create_shipping_plan(self, sku: str, quantity: int):
        """创建发货计划"""
        await self.page.goto("https://sellercentral.amazon.com/shipping")
        
        # 点击创建新计划
        await self.page.click('button:has-text("Create Shipping Plan")')
        
        # 填写 SKU 和数量
        await self.page.fill('input[name="sku"]', sku)
        await self.page.fill('input[name="quantity"]', str(quantity))
        
        # 提交
        await self.page.click('button[type="submit"]')
```

---

## 7. 故障排查

### 7.1 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 登录后仍显示登录页 | Cookie 域不匹配 | 检查 Cookie 的 domain 字段 |
| 检测到自动化软件 | 指纹暴露 | 使用 stealth 模式 |
| CAPTCHA 频繁出现 | IP 被标记 | 更换住宅代理 |
| 2FA 无法通过 | 时间不同步 | 同步系统时间 |
| 选择器找不到 | 页面结构变化 | 更新 CSS 选择器 |

### 7.2 调试技巧

```python
# 1. 截图调试
await page.screenshot(path="debug_login.png", full_page=True)

# 2. 录制视频
context = await browser.new_context(record_video_dir="videos/")

# 3. 控制台日志
page.on("console", lambda msg: print(f"Console: {msg.text}"))

# 4. 网络请求监控
page.on("request", lambda req: print(f"Request: {req.url}"))
page.on("response", lambda res: print(f"Response: {res.url} - {res.status}"))
```

### 7.3 选择器更新指南

亚马逊页面结构会不定期更新，需要定期检查：

```python
# 调试选择器
async def debug_selectors(page):
    """调试并验证选择器"""
    selectors = {
        "email": "#ap_email",
        "password": "#ap_password",
        "submit": "#signInSubmit",
    }
    
    for name, selector in selectors.items():
        count = await page.locator(selector).count()
        print(f"{name}: {count} elements found")
        if count == 0:
            print(f"  ⚠️ 选择器可能已过时：{selector}")
```

---

## 附录 A：依赖安装

```toml
# pyproject.toml
[project]
name = "amazon-login-crawler"
version = "0.1.0"
dependencies = [
    "playwright>=1.40.0",
    "playwright-stealth>=1.0.6",
    "python-dotenv>=1.0.0",
    "pydantic>=2.0.0",
    "cryptography>=41.0.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
]
```

---

## 附录 B：推荐资源

- [Playwright 官方文档](https://playwright.dev/python/)
- [Playwright Stealth](https://github.com/berstend/playwright-stealth)
- [亚马逊 SP-API 文档](https://developer-docs.amazon.com/sp-api)
- [反检测最佳实践](https://antoinevastel.com/blogs/blog/overview)

---

## 更新日志

| 版本 | 日期 | 说明 |
|------|------|------|
| 0.1.0 | 2026-03-12 | 初始版本 |

---

*文档结束*
