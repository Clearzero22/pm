# 亚马逊浏览器自动化登录技术详解

> **使用 Playwright 实现亚马逊卖家账号安全登录的完整指南**
>
> ⚠️ **重要声明**: 本文档仅供技术学习和合法业务使用。请确保你的操作符合亚马逊服务条款和当地法律法规。

---

## 目录

1. [登录流程分析](#1-登录流程分析)
2. [技术实现方案](#2-技术实现方案)
3. [风控机制解析](#3-风控机制解析)
4. [反检测策略](#4-反检测策略)
5. [完整代码实现](#5-完整代码实现)
6. [故障排查](#6-故障排查)

---

## 1. 登录流程分析

### 1.1 亚马逊登录页面流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        亚马逊登录流程图                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌───────────┐ │
│  │ 访问登录页  │────►│ 输入邮箱    │────►│ 输入密码    │────►│ 提交表单  │ │
│  │ /ap/signin  │     │             │     │             │     │           │ │
│  └─────────────┘     └─────────────┘     └─────────────┘     └─────┬─────┘ │
│                                                                    │       │
│                                                                    ▼       │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌───────────┐ │
│  │ 登录成功    │◄────│ 2FA 验证    │◄────│ CAPTCHA     │◄────│ 风险评估  │ │
│  │ 跳转后台    │     │ (可选)      │     │ (可选)      │     │           │ │
│  └─────────────┘     └─────────────┘     └─────────────┘     └───────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 关键页面和元素

| 页面 | URL | 关键元素 |
|------|-----|----------|
| 登录页 | `https://www.amazon.com/ap/signin` | 邮箱输入框、密码输入框、提交按钮 |
| 2FA 页 | `https://www.amazon.com/ap/oa` | OTP 输入框、提交按钮 |
| CAPTCHA 页 | `https://www.amazon.com/errors/validateCaptcha` | 验证码图片、输入框 |
| 卖家后台 | `https://sellercentral.amazon.com` | 导航菜单、仪表盘 |

### 1.3 登录请求分析

```http
# 登录 POST 请求示例
POST /ap/signin HTTP/1.1
Host: www.amazon.com
Content-Type: application/x-www-form-urlencoded

email=your_email@example.com
password=your_password
&metadata1=xxx
&metadata2=yyy
&openid.pape.max_auth_age=0
&openid.identity=http://specs.openid.net/auth/2.0/identifier_select
&language=en_US
&pageId=amzn_seller_central
&openid.return_to=https://sellercentral.amazon.com
&prevRID=xxx
&openid.assoc_handle=amzn_seller_central
&openid.mode=checkid_setup
&openid.ns.pape=http://specs.openid.net/extensions/pape/1.0
&prepopulatedLoginId=&rememberMe=true
&openid.oa2.scope=profile
&skipAjaxPasswordEncrypt=true
&openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select
&openid.ns=http://specs.openid.net/auth/2.0
```

---

## 2. 技术实现方案

### 2.1 技术选型对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **Playwright** | 现代、难检测、支持多浏览器 | 学习曲线中等 | ⭐⭐⭐⭐⭐ |
| **Selenium** | 成熟、文档多 | 容易被检测 | ⭐⭐⭐ |
| **Puppeteer** | 轻量、快速 | 仅支持 Chromium | ⭐⭐⭐⭐ |
| **纯 HTTP 请求** | 速度快 | 无法处理 JS、极易被检测 | ⭐ |

### 2.2 推荐架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        浏览器自动化架构                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      应用层 (Application)                            │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │  登录管理器  │  │  Cookie 管理  │  │  会话管理    │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                      │
│  ┌───────────────────────────────────┼───────────────────────────────────┐ │
│  │                      框架层 (Framework)                                │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │ │
│  │  │                    Playwright + Stealth                         │  │ │
│  │  │  ┌────────────┐  ┌────────────┐  ┌────────────┐                │  │ │
│  │  │  │  浏览器控制 │  │  反检测    │  │  等待机制  │                │  │ │
│  │  │  └────────────┘  └────────────┘  └────────────┘                │  │ │
│  │  └─────────────────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                      │                                      │
│  ┌───────────────────────────────────┼───────────────────────────────────┐ │
│  │                      浏览器层 (Browser)                                │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │ │
│  │  │  Chromium    │  │  Firefox     │  │  WebKit      │                │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 风控机制解析

### 3.1 亚马逊风控系统

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        亚马逊风控检测维度                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. 设备指纹 (Device Fingerprint)                                     │   │
│  │    - User-Agent                                                     │   │
│  │    - Canvas 指纹                                                    │   │
│  │    - WebGL 渲染器                                                   │   │
│  │    - 屏幕分辨率                                                     │   │
│  │    - 时区和语言                                                     │   │
│  │    - 字体列表                                                       │   │
│  │    - 浏览器插件                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 2. 行为分析 (Behavior Analysis)                                      │   │
│  │    - 鼠标移动轨迹                                                   │   │
│  │    - 键盘输入节奏                                                   │   │
│  │    - 点击模式                                                       │   │
│  │    - 页面停留时间                                                   │   │
│  │    - 滚动行为                                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 3. 网络特征 (Network Pattern)                                        │   │
│  │    - IP 地址信誉                                                     │   │
│  │    - IP 地理位置                                                     │   │
│  │    - 请求频率                                                       │   │
│  │    - TLS 指纹                                                        │   │
│  │    - DNS 解析                                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 4. 会话特征 (Session Pattern)                                        │   │
│  │    - Cookie 模式                                                    │   │
│  │    - LocalStorage 数据                                               │   │
│  │    - 浏览器历史记录                                                 │   │
│  │    - Referer 链                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 5. 自动化检测 (Automation Detection)                                 │   │
│  │    - navigator.webdriver 属性                                        │   │
│  │    - Selenium/Playwright 特征                                        │   │
│  │    - 异常 DOM 操作                                                    │   │
│  │    - JavaScript 执行环境                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 风控触发条件

| 风险因素 | 触发阈值 | 后果 |
|----------|----------|------|
| **异常 User-Agent** | 检测到自动化工具特征 | CAPTCHA |
| **IP 信誉低** | 数据中心 IP、代理 IP | 2FA 验证 |
| **登录频率高** | 同一 IP 短时间多次登录 | 临时锁定 |
| **地理位置异常** | 登录地点频繁变化 | 账号审核 |
| **设备指纹变化** | 设备特征频繁改变 | 要求验证 |
| **行为异常** | 鼠标/键盘模式异常 | CAPTCHA |

---

## 4. 反检测策略

### 4.1 浏览器指纹伪装

```python
# 完整的反检测配置
ANTI_DETECT_CONFIG = {
    # 1. User-Agent（模拟真实用户）
    "user_agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.6099.130 Safari/537.36"
    ),
    
    # 2. 视口大小（常见分辨率）
    "viewport": {"width": 1920, "height": 1080},
    
    # 3. 时区和语言
    "timezone_id": "America/New_York",
    "locale": "en-US",
    "languages": ["en-US", "en"],
    
    # 4. 地理位置（与 IP 匹配）
    "geolocation": {"latitude": 40.7128, "longitude": -74.0060},
    
    # 5. 设备特征
    "device_scale_factor": 1,
    "is_mobile": False,
    "has_touch": False,
    
    # 6. 颜色方案
    "color_scheme": "light",
}
```

### 4.2 JavaScript 注入隐藏自动化特征

```javascript
// 注入到页面初始化脚本
INIT_SCRIPT = """
// 隐藏 webdriver 属性
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined,
});

// 隐藏 automation 属性
Object.defineProperty(navigator, 'automation', {
    get: () => undefined,
});

// 模拟真实插件
Object.defineProperty(navigator, 'plugins', {
    get: () => [
        { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
        { name: 'Chrome PDF Viewer', filename: 'internal-pdf-viewer' },
        { name: 'Native Client', filename: 'internal-nacl-plugin' },
    ],
});

// 模拟真实语言
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en'],
});

// 隐藏 headless 特征
Object.defineProperty(navigator, 'headless', {
    get: () => false,
});

// Canvas 指纹噪声
const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
HTMLCanvasElement.prototype.toDataURL = function(type) {
    if (type === 'image/webp') {
        return originalToDataURL.call(this, type);
    }
    return originalToDataURL.call(this, 'image/png');
};

// WebGL 指纹伪装
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(parameter) {
    if (parameter === 37445) {
        return 'Intel Inc.';
    }
    if (parameter === 37446) {
        return 'Intel Iris OpenGL Engine';
    }
    return getParameter.call(this, parameter);
};
"""
```

### 4.3 人类行为模拟

```python
# src/utils/human_behavior.py
import asyncio
import random
from playwright.async_api import Page


class HumanBehaviorSimulator:
    """人类行为模拟器"""
    
    @staticmethod
    async def human_typing(page: Page, selector: str, text: str):
        """
        模拟人类打字
        
        - 随机输入速度
        - 随机暂停
        - 偶尔错误修正
        """
        element = await page.wait_for_selector(selector)
        await element.click()
        
        # 清空输入框
        await page.keyboard.press("Control+A")
        await page.keyboard.press("Delete")
        await asyncio.sleep(random.uniform(0.2, 0.5))
        
        # 逐字输入
        for i, char in enumerate(text):
            await page.keyboard.type(char)
            
            # 随机延迟（模拟思考）
            if random.random() < 0.1:  # 10% 概率暂停
                await asyncio.sleep(random.uniform(0.3, 1.0))
            elif random.random() < 0.05:  # 5% 概率模拟错误
                await page.keyboard.press("Backspace")
                await asyncio.sleep(random.uniform(0.1, 0.3))
                await page.keyboard.type(char)
            else:
                # 正常输入延迟
                await asyncio.sleep(random.uniform(0.05, 0.2))
    
    @staticmethod
    async def human_scroll(page: Page):
        """模拟人类滚动"""
        scroll_distances = [100, 200, 300, 400, 500]
        
        for _ in range(random.randint(3, 7)):
            distance = random.choice(scroll_distances)
            await page.evaluate(f"window.scrollBy(0, {distance})")
            await asyncio.sleep(random.uniform(0.5, 2.0))
    
    @staticmethod
    async def human_mouse_move(page: Page, x: int, y: int):
        """模拟人类鼠标移动（贝塞尔曲线）"""
        steps = random.randint(10, 30)
        
        for i in range(steps):
            progress = i / steps
            # 添加随机偏移
            offset_x = random.randint(-5, 5) * (1 - progress)
            offset_y = random.randint(-5, 5) * (1 - progress)
            
            current_x = int(x * progress + offset_x)
            current_y = int(y * progress + offset_y)
            
            await page.mouse.move(current_x, current_y)
            await asyncio.sleep(random.uniform(0.01, 0.05))
    
    @staticmethod
    async def random_delay(min_seconds: float = 0.5, max_seconds: float = 2.0):
        """随机延迟"""
        await asyncio.sleep(random.uniform(min_seconds, max_seconds))
```

### 4.4 IP 代理策略

```python
# 代理配置
PROXY_CONFIGS = {
    # 住宅代理（推荐）
    "residential": {
        "server": "http://residential-proxy.com:8080",
        "username": "user",
        "password": "pass",
    },
    
    # 移动代理（最佳）
    "mobile": {
        "server": "http://4g-proxy.com:8080",
        "username": "user",
        "password": "pass",
    },
    
    # 静态住宅代理
    "static_residential": {
        "server": "http://static-residential.com:8080",
        "username": "user",
        "password": "pass",
    },
}

# 代理选择策略
def select_proxy(location: str = "US") -> dict:
    """
    根据目标地区选择代理
    
    原则:
    - 选择与账号注册地匹配的 IP
    - 优先使用住宅代理
    - 避免使用数据中心 IP
    """
    # 实现代理选择逻辑
    return PROXY_CONFIGS["residential"]
```

### 4.5 Cookie 持久化策略

```python
# Cookie 管理策略
class CookieManager:
    """
    Cookie 管理器
    
    策略:
    1. 首次登录后保存 Cookie
    2. 后续使用 Cookie 直接访问
    3. Cookie 过期后重新登录
    4. 定期刷新 Cookie
    """
    
    def __init__(self, cookie_file: str = "cookies/amazon.json"):
        self.cookie_file = Path(cookie_file)
        self.cookies = []
    
    def save_cookies(self, cookies: list):
        """保存 Cookie"""
        self.cookie_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cookie_file, "w") as f:
            json.dump(cookies, f, indent=2)
    
    def load_cookies(self) -> list:
        """加载 Cookie"""
        if self.cookie_file.exists():
            with open(self.cookie_file, "r") as f:
                return json.load(f)
        return []
    
    def is_cookie_valid(self, cookies: list) -> bool:
        """检查 Cookie 是否有效"""
        if not cookies:
            return False
        
        # 检查过期时间
        for cookie in cookies:
            if cookie.get("expires", 0) < time.time():
                return False
        
        return True
```

---

## 5. 完整代码实现

### 5.1 亚马逊登录类

```python
# src/amazon/amazon_login.py
import asyncio
import json
import random
import time
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from playwright_stealth import stealth_async

from src.utils.human_behavior import HumanBehaviorSimulator


class AmazonLoginError(Exception):
    """登录异常基类"""
    pass


class CaptchaRequired(AmazonLoginError):
    """需要验证码"""
    pass


class TwoFactorRequired(AmazonLoginError):
    """需要双重验证"""
    def __init__(self, message: str, method: str = "unknown"):
        super().__init__(message)
        self.method = method


class AmazonLogin:
    """
    亚马逊登录自动化类
    
    功能:
    - 账号密码登录
    - Cookie 持久化
    - 2FA 支持
    - CAPTCHA 处理
    - 反检测配置
    """
    
    # 亚马逊登录 URL
    LOGIN_URL = "https://www.amazon.com/ap/signin"
    SELLER_CENTRAL_URL = "https://sellercentral.amazon.com"
    
    # CSS 选择器（可能需要根据实际页面调整）
    SELECTORS = {
        # 登录表单
        "email": "#ap_email",
        "password": "#ap_password",
        "submit": "#signInSubmit",
        
        # 错误信息
        "error_box": "#auth-error-message-box",
        "error_message": ".a-alert-content",
        
        # CAPTCHA
        "captcha_image": "#auth-captcha-image",
        "captcha_input": "#auth-captcha-guess",
        
        # 2FA
        "2fa_page": "#auth-otp-form",
        "2fa_input": "#auth-otp-enter-otp",
        "2fa_submit": "#auth-otp-submit-button",
        
        # 登录成功标志
        "account_menu": "#nav-link-accountList",
        "sign_out": "#nav-item-signout",
    }
    
    def __init__(
        self,
        email: str,
        password: str,
        headless: bool = False,
        proxy: Optional[Dict[str, str]] = None,
        cookie_path: str = "cookies/amazon.json",
        user_data_dir: Optional[str] = None,
    ):
        """
        初始化登录器
        
        Args:
            email: 亚马逊账号邮箱
            password: 密码
            headless: 是否无头模式
            proxy: 代理配置
            cookie_path: Cookie 存储路径
            user_data_dir: 浏览器用户数据目录（用于保持登录状态）
        """
        self.email = email
        self.password = password
        self.headless = headless
        self.proxy = proxy
        self.cookie_path = Path(cookie_path)
        self.user_data_dir = user_data_dir
        
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        self.human = HumanBehaviorSimulator()
    
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
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-features=TranslateUI",
                "--disable-ipc-flooding-protection",
            ],
        }
        
        # 代理配置
        if self.proxy:
            browser_args["proxy"] = self.proxy
        
        # 用户数据目录（保持登录状态）
        if self.user_data_dir:
            browser_args["user_data_dir"] = self.user_data_dir
        
        self.browser = await playwright.chromium.launch(**browser_args)
        
        # 创建浏览器上下文
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.6099.130 Safari/537.36"
            ),
            locale="en-US",
            timezone_id="America/New_York",
            permissions=["geolocation"],
            geolocation={"latitude": 40.7128, "longitude": -74.0060},
            color_scheme="light",
        )
        
        # 应用 Stealth 反检测
        await stealth_async(self.context)
        
        # 注入初始化脚本
        await self.context.add_init_script("""
            // 隐藏 webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // 隐藏 automation
            Object.defineProperty(navigator, 'automation', {
                get: () => undefined,
            });
            
            // 模拟插件
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // 模拟语言
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
        """)
        
        self.page = await self.context.new_page()
        
        return self.page
    
    async def load_cookies(self) -> bool:
        """加载 Cookie"""
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
        """保存 Cookie"""
        try:
            cookies = await self.context.cookies()
            self.cookie_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cookie_path, "w") as f:
                json.dump(cookies, f, indent=2)
            print(f"[INFO] 已保存 {len(cookies)} 个 Cookie")
        except Exception as e:
            print(f"[ERROR] 保存 Cookie 失败：{e}")
    
    async def is_logged_in(self) -> bool:
        """检查是否已登录"""
        try:
            await self.page.goto(self.SELLER_CENTRAL_URL, wait_until="domcontentloaded")
            await self.page.wait_for_timeout(3000)
            
            # 检查是否在卖家后台
            current_url = self.page.url
            if "sellercentral" in current_url:
                # 检查是否有登出按钮
                sign_out = await self.page.query_selector(self.SELECTORS["sign_out"])
                return sign_out is not None
            
            return False
        except Exception as e:
            print(f"[ERROR] 检查登录状态失败：{e}")
            return False
    
    async def handle_captcha(self):
        """处理验证码"""
        captcha_image = await self.page.query_selector(self.SELECTORS["captcha_image"])
        
        if captcha_image:
            print("[WARNING] 检测到 CAPTCHA，需要手动处理")
            
            # 等待用户手动完成（最长 5 分钟）
            try:
                await self.page.wait_for_selector(
                    self.SELECTORS["captcha_image"],
                    state="detached",
                    timeout=300000,
                )
                print("[INFO] CAPTCHA 已完成")
            except asyncio.TimeoutError:
                raise CaptchaRequired("CAPTCHA 处理超时")
    
    async def handle_2fa(self, otp_code: Optional[str] = None) -> bool:
        """
        处理双重验证
        
        Args:
            otp_code: 6 位验证码
            
        Returns:
            是否成功处理
        """
        2fa_form = await self.page.query_selector(self.SELECTORS["2fa_page"])
        
        if 2fa_form:
            if otp_code:
                # 自动输入验证码
                await self.human.human_typing(
                    self.page,
                    self.SELECTORS["2fa_input"],
                    otp_code
                )
                await self.page.click(self.SELECTORS["2fa_submit"])
                return True
            else:
                print("[WARNING] 需要 2FA 验证码，请在浏览器中手动输入")
                # 等待用户手动完成
                await self.page.wait_for_timeout(300000)
                return True
        
        return False
    
    async def login(self, otp_code: Optional[str] = None) -> bool:
        """
        执行登录流程
        
        Args:
            otp_code: 2FA 验证码（可选）
            
        Returns:
            是否登录成功
        """
        print("[INFO] 开始登录流程...")
        
        # 1. 初始化浏览器
        await self.init_browser()
        
        # 2. 尝试使用 Cookie 登录
        if await self.load_cookies():
            if await self.is_logged_in():
                print("[SUCCESS] Cookie 有效，已自动登录")
                return True
            print("[INFO] Cookie 已过期，重新登录")
        
        # 3. 访问登录页面
        print(f"[INFO] 访问登录页面：{self.LOGIN_URL}")
        await self.page.goto(self.LOGIN_URL, wait_until="domcontentloaded")
        await self.page.wait_for_timeout(random.randint(2000, 4000))
        
        # 4. 输入邮箱
        print("[INFO] 输入邮箱账号")
        await self.human.human_typing(self.page, self.SELECTORS["email"], self.email)
        await self.human.random_delay(0.5, 1.0)
        
        # 5. 输入密码
        print("[INFO] 输入密码")
        await self.human.human_typing(self.page, self.SELECTORS["password"], self.password)
        await self.human.random_delay(0.5, 1.0)
        
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
            error_box = await self.page.query_selector(self.SELECTORS["error_box"])
            if error_box:
                error_msg = await self.page.text_content(self.SELECTORS["error_message"])
                raise AmazonLoginError(f"登录失败：{error_msg.strip()}")
            
            raise AmazonLoginError("登录失败，无法进入卖家后台")
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
            print("[INFO] 浏览器已关闭")
```

### 5.2 使用示例

```python
# examples/amazon_login_example.py
import asyncio
import os
from src.amazon.amazon_login import AmazonLogin


async def main():
    # 从环境变量读取配置
    email = os.getenv("AMAZON_EMAIL")
    password = os.getenv("AMAZON_PASSWORD")
    otp_code = os.getenv("AMAZON_OTP")  # 可选：2FA 验证码
    
    # 创建登录器
    login = AmazonLogin(
        email=email,
        password=password,
        headless=False,  # 首次登录建议显示浏览器
        cookie_path="cookies/amazon_seller.json",
        user_data_dir="browser_data/amazon",  # 保持浏览器状态
    )
    
    try:
        # 执行登录
        success = await login.login(otp_code=otp_code)
        
        if success:
            print("✅ 登录成功！")
            
            # 在这里执行你的业务操作
            # await do_seller_tasks(login.page)
            
            # 保持浏览器打开
            await asyncio.sleep(60)
        else:
            print("❌ 登录失败")
    
    except Exception as e:
        print(f"❌ 发生错误：{e}")
    
    finally:
        await login.close()


if __name__ == "__main__":
    asyncio.run(main())
```

### 5.3 配置文件

```yaml
# config/amazon.yaml
# 亚马逊登录配置

accounts:
  - name: "主账号"
    email: "your_email@example.com"
    password_env: "AMAZON_PASSWORD"  # 从环境变量读取密码
    otp_env: "AMAZON_OTP"  # 2FA 验证码（可选）
    marketplace: "US"
    
  - name: "欧洲账号"
    email: "eu_email@example.com"
    password_env: "AMAZON_EU_PASSWORD"
    marketplace: "EU"

# 浏览器配置
browser:
  headless: false  # 首次登录建议设为 false
  user_data_dir: "browser_data/amazon"
  cookie_path: "cookies/amazon"
  
# 代理配置
proxy:
  enabled: true
  type: "residential"  # residential / mobile / static
  config:
    server: "http://proxy-server:8080"
    username: "your_username"
    password: "your_password"

# 反检测配置
anti_detect:
  random_delay_min: 0.5
  random_delay_max: 2.0
  human_typing: true
  human_scroll: true
  
# 重试配置
retry:
  max_attempts: 3
  delay_between_attempts: 60  # 秒
```

---

## 6. 故障排查

### 6.1 常见问题及解决方案

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| **CAPTCHA 频繁出现** | IP 信誉低、行为异常 | 更换住宅代理、增加人类行为模拟 |
| **2FA 无法跳过** | 新设备登录 | 使用 Cookie 持久化、保持浏览器数据 |
| **登录成功但无法访问后台** | Cookie 不完整 | 等待页面完全加载后再保存 Cookie |
| **选择器找不到** | 页面结构变化 | 更新 CSS 选择器、增加等待时间 |
| **浏览器被检测** | 反检测配置不足 | 加强 stealth 配置、使用真实用户数据目录 |

### 6.2 调试技巧

```python
# 启用调试日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 截图调试
await page.screenshot(path="debug_login.png", full_page=True)

# 录制视频
context = await browser.new_context(record_video_dir="videos/")

# 监控控制台日志
page.on("console", lambda msg: print(f"Console: {msg.text}"))

# 监控网络请求
page.on("request", lambda req: print(f"Request: {req.url}"))
page.on("response", lambda res: print(f"Response: {res.status} - {res.url}"))
```

### 6.3 选择器更新指南

```python
# 调试选择器工具
async def debug_selectors(page: Page):
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

## 附录：安全最佳实践

### A. 账号安全

```markdown
## 账号安全清单

- [ ] 使用强密码（16 位以上，包含大小写、数字、特殊字符）
- [ ] 启用 2FA 双重验证
- [ ] 定期更换密码（90 天周期）
- [ ] 不在代码中硬编码凭据
- [ ] 使用环境变量或密钥管理服务
- [ ] 定期审查账号活动日志
- [ ] 限制登录 IP 范围（如可能）
```

### B. 合规使用

```markdown
## 合规使用原则

1. **遵守服务条款**
   - 阅读并遵守亚马逊服务条款
   - 不使用于违规用途

2. **合理使用频率**
   - 避免高频访问
   - 加入适当延迟
   - 模拟真实用户行为

3. **数据保护**
   - 加密存储敏感数据
   - 定期清理日志
   - 不泄露账号信息
```

---

*文档版本：0.1.0 | 最后更新：2026-03-12*
