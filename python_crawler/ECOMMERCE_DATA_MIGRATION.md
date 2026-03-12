# 电商商品数据自动迁移系统技术文档

> **自动化数据采集 → AI 智能优化 → 人工审核 → 亚马逊上架**
>
> 本文档详细描述如何构建一个完整的电商商品数据迁移系统，支持从其他电商平台（如淘宝、1688、速卖通等）采集商品数据，经过 AI 优化重构后，通过人工审核，最终自动填写到亚马逊卖家后台。

---

## 目录

1. [系统概述](#1-系统概述)
2. [技术架构](#2-技术架构)
3. [核心模块设计](#3-核心模块设计)
4. [工作流程详解](#4-工作流程详解)
5. [人机交互审核系统](#5-人机交互审核系统)
6. [完整代码实现](#6-完整代码实现)
7. [部署与配置](#7-部署与配置)

---

## 1. 系统概述

### 1.1 业务场景

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           商品数据迁移流程图                                 │
│                                                                             │
│   源电商平台          数据采集          AI 处理引擎           人工审核       │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐       │
│  │          │      │          │      │          │      │          │       │
│  │  淘宝    │─────►│  爬虫    │─────►│  关键词  │─────►│  Web      │       │
│  │  1688    │      │  模块    │      │  文案    │      │  审核    │       │
│  │  速卖通  │      │          │      │  图片    │      │  界面    │       │
│  │          │      │          │      │          │      │          │       │
│  └──────────┘      └──────────┘      └──────────┘      └────┬─────┘       │
│                                                              │              │
│                                                              ▼              │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐       │
│  │          │      │          │      │          │      │          │       │
│  │  亚马逊  │◄─────│  自动    │◄─────│  数据    │◄─────│  审核    │       │
│  │  Seller  │      │  填写    │      │  导出    │      │  通过    │       │
│  │  Central │      │  模块    │      │  格式    │      │          │       │
│  │          │      │          │      │          │      │          │       │
│  └──────────┘      └──────────┘      └──────────┘      └──────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 核心功能

| 功能模块 | 描述 | 技术栈 |
|----------|------|--------|
| **数据采集** | 从源电商平台抓取商品数据 | Playwright + BeautifulSoup |
| **关键词优化** | AI 生成亚马逊 SEO 关键词 | LLM API (Claude/GPT) |
| **文案重构** | 重写商品描述、五点描述 | LLM + 规则引擎 |
| **图片处理** | 下载、优化、生成主图 | Pillow + SD API |
| **人工审核** | Web 界面审核优化内容 | Streamlit/Flask |
| **自动填写** | 登录亚马逊并填写表单 | Playwright |

### 1.3 数据处理流程

```
原始数据 ──────► 清洗 ──────► AI 优化 ──────► 格式化 ──────► 审核 ──────► 导出
   │              │              │              │              │             │
   ▼              ▼              ▼              ▼              ▼             ▼
HTML 解析      去重/去噪     关键词提取     亚马逊模板    人工确认    CSV/直接上传
```

---

## 2. 技术架构

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              系统架构分层                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         表现层 (Presentation)                        │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │   CLI 工具   │  │  Web 审核界面 │  │  配置文件    │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      ▲                                      │
│  ┌───────────────────────────────────┼───────────────────────────────────┐ │
│  │                         业务逻辑层 (Business Logic)                    │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │ │
│  │  │  数据采集器  │  │  AI 优化引擎  │  │  审核管理器  │  │  填写器   │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘ │ │
│  └───────────────────────────────────┼───────────────────────────────────┘ │
│                                      ▲                                      │
│  ┌───────────────────────────────────┼───────────────────────────────────┐ │
│  │                         数据访问层 (Data Access)                       │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │ │
│  │  │  SQLite DB   │  │  JSON 存储   │  │  Cookie 管理  │  │  文件 IO  │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘ │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         外部服务层 (External Services)               │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │ │
│  │  │  LLM API     │  │  图片 API    │  │  翻译 API    │  │  代理池   │ │ │
│  │  │ (Claude/GPT) │  │  (StableDiff)│  │  (DeepL)     │  │           │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘ │ │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 技术选型

| 层级 | 技术 | 选择理由 |
|------|------|----------|
| **爬虫框架** | Playwright | 支持动态页面、反检测能力强 |
| **AI 引擎** | Claude API / GPT-4 | 文案质量高、支持中文 |
| **Web 框架** | Streamlit | 快速构建审核界面 |
| **数据存储** | SQLite + JSON | 轻量、易迁移 |
| **图片处理** | Pillow + requests | 功能完善、性能好 |
| **任务队列** | asyncio | 异步并发、高效 |

### 2.3 项目结构

```
python_crawler/
├── main.py                          # CLI 入口
├── migration_app.py                 # Web 审核应用入口
├── src/
│   ├── __init__.py
│   ├── crawler/
│   │   ├── __init__.py
│   │   ├── base_crawler.py          # 爬虫基类
│   │   ├── taobao_crawler.py        # 淘宝爬虫
│   │   ├── 1688_crawler.py          # 1688 爬虫
│   │   └── aliexpress_crawler.py    # 速卖通爬虫
│   ├── optimizer/
│   │   ├── __init__.py
│   │   ├── keyword_optimizer.py     # 关键词优化
│   │   ├── copywriter.py            # 文案重构
│   │   ├── image_processor.py       # 图片处理
│   │   └── llm_client.py            # LLM 客户端
│   ├── reviewer/
│   │   ├── __init__.py
│   │   ├── review_manager.py        # 审核管理
│   │   └── web_interface.py         # Web 界面
│   ├── uploader/
│   │   ├── __init__.py
│   │   ├── amazon_form_filler.py    # 亚马逊表单填写
│   │   └── inventory_template.py    # 库存模板生成
│   └── utils/
│       ├── __init__.py
│       ├── database.py              # 数据库操作
│       ├── config.py                # 配置管理
│       └── logger.py                # 日志配置
├── config/
│   ├── settings.yaml                # 主配置
│   ├── keywords.yaml                # 关键词配置
│   └── templates/                   # 模板文件
├── data/
│   ├── raw/                         # 原始采集数据
│   ├── processed/                   # 处理后数据
│   ├── reviewed/                    # 审核通过数据
│   ├── images/                      # 下载的图片
│   └── database.db                  # SQLite 数据库
├── output/
│   ├── amazon_upload.csv            # 亚马逊上传模板
│   └── reports/                     # 报告文件
└── .env                             # 环境变量
```

---

## 3. 核心模块设计

### 3.1 数据采集模块

#### 3.1.1 爬虫基类设计

```python
# src/crawler/base_crawler.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page
import asyncio


@dataclass
class ProductData:
    """商品数据结构"""
    # 基本信息
    title: str
    price: str
    original_price: str
    currency: str
    sales_count: str  # 销量
    
    # 详细描述
    description: str
    features: List[str]  # 商品特点
    specifications: Dict[str, str]  # 规格参数
    
    # 媒体资源
    images: List[str]  # 图片 URL 列表
    video_urls: List[str]  # 视频 URL 列表
    
    # 分类信息
    category: str
    brand: str
    shop_name: str
    
    # 评价信息
    rating: float
    review_count: int
    reviews: List[Dict[str, Any]]  # 评价列表
    
    # 元数据
    source_url: str
    source_platform: str
    crawl_time: str
    product_id: str
    
    # 扩展字段
    extra: Dict[str, Any]


class BaseCrawler(ABC):
    """爬虫基类"""
    
    def __init__(
        self,
        headless: bool = False,
        proxy: Optional[str] = None,
        timeout: int = 30000,
    ):
        self.headless = headless
        self.proxy = proxy
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def init_browser(self):
        """初始化浏览器"""
        playwright = await async_playwright().start()
        
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ]
        )
        
        self.page = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        return self.page
    
    @abstractmethod
    async def fetch_product(self, url: str) -> ProductData:
        """获取商品数据（子类实现）"""
        pass
    
    @abstractmethod
    async def parse_page(self) -> ProductData:
        """解析页面（子类实现）"""
        pass
    
    async def download_images(self, image_urls: List[str], save_dir: str) -> List[str]:
        """下载图片"""
        import aiohttp
        from pathlib import Path
        
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        saved_paths = []
        
        async with aiohttp.ClientSession() as session:
            for i, url in enumerate(image_urls[:10]):  # 最多下载 10 张
                try:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            image_data = await resp.read()
                            ext = url.split(".")[-1].split("?")[0] or "jpg"
                            save_path = Path(save_dir) / f"image_{i}.{ext}"
                            
                            with open(save_path, "wb") as f:
                                f.write(image_data)
                            
                            saved_paths.append(str(save_path))
                except Exception as e:
                    print(f"下载图片失败 {url}: {e}")
        
        return saved_paths
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
```

#### 3.1.2 淘宝爬虫示例

```python
# src/crawler/taobao_crawler.py
from .base_crawler import BaseCrawler, ProductData
from typing import List, Dict, Any
import json


class TaobaoCrawler(BaseCrawler):
    """淘宝商品爬虫"""
    
    PLATFORM = "taobao"
    
    async def fetch_product(self, url: str) -> ProductData:
        """获取淘宝商品数据"""
        await self.init_browser()
        
        try:
            # 访问商品页面
            await self.page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)
            await self.page.wait_for_timeout(3000)  # 等待动态加载
            
            # 滚动页面加载更多内容
            await self._scroll_page()
            
            # 解析数据
            product = await self.parse_page()
            product.source_url = url
            product.source_platform = self.PLATFORM
            
            return product
        finally:
            await self.close()
    
    async def _scroll_page(self):
        """模拟滚动加载"""
        for _ in range(3):
            await self.page.evaluate("window.scrollBy(0, 800)")
            await self.page.wait_for_timeout(1000)
    
    async def parse_page(self) -> ProductData:
        """解析淘宝商品页面"""
        # 标题
        title = await self._safe_text("#MainInfo h1")
        
        # 价格
        price = await self._safe_text(".price-current")
        original_price = await self._safe_text(".price-original", "N/A")
        
        # 销量
        sales = await self._safe_text(".sales-count", "0")
        
        # 图片
        images = await self._extract_images()
        
        # 商品详情
        description = await self._extract_description()
        features = await self._extract_features()
        specifications = await self._extract_specifications()
        
        # 评价
        rating = await self._extract_rating()
        reviews = await self._extract_reviews()
        
        # 店铺信息
        shop_name = await self._safe_text(".shop-name", "N/A")
        brand = await self._safe_text(".brand-name", "N/A")
        category = await self._safe_text(".category", "N/A")
        
        return ProductData(
            title=title or "N/A",
            price=price or "0",
            original_price=original_price,
            currency="CNY",
            sales_count=sales,
            description=description,
            features=features,
            specifications=specifications,
            images=images,
            video_urls=[],
            category=category,
            brand=brand,
            shop_name=shop_name,
            rating=rating,
            review_count=len(reviews),
            reviews=reviews,
            source_url="",
            source_platform=self.PLATFORM,
            crawl_time="",
            product_id="",
            extra={}
        )
    
    async def _safe_text(self, selector: str, default: str = "") -> str:
        """安全获取文本"""
        try:
            el = await self.page.wait_for_selector(selector, timeout=5000)
            return (await el.text_content()).strip()
        except:
            return default
    
    async def _extract_images(self) -> List[str]:
        """提取图片 URL"""
        images = []
        try:
            # 主图
            main_imgs = await self.page.query_selector_all(".main-image img")
            for img in main_imgs:
                src = await img.get_attribute("data-src") or await img.get_attribute("src")
                if src:
                    images.append(src)
            
            # 详情图
            detail_imgs = await self.page.query_selector_all(".detail-image img")
            for img in detail_imgs:
                src = await img.get_attribute("src")
                if src and src.startswith("http"):
                    images.append(src)
        except Exception as e:
            print(f"提取图片失败：{e}")
        
        return images[:10]  # 限制数量
    
    async def _extract_description(self) -> str:
        """提取商品描述"""
        try:
            desc_el = await self.page.wait_for_selector("#detail-hoz", timeout=5000)
            return (await desc_el.text_content()).strip()
        except:
            return ""
    
    async def _extract_features(self) -> List[str]:
        """提取商品特点（卖点）"""
        features = []
        try:
            feature_els = await self.page.query_selector_all(".feature-item")
            for el in feature_els:
                text = await el.text_content()
                if text.strip():
                    features.append(text.strip())
        except:
            pass
        return features[:5]
    
    async def _extract_specifications(self) -> Dict[str, str]:
        """提取规格参数"""
        specs = {}
        try:
            rows = await self.page.query_selector_all(".spec-table tr")
            for row in rows:
                cells = await row.query_selector_all("td")
                if len(cells) >= 2:
                    key = await cells[0].text_content()
                    value = await cells[1].text_content()
                    specs[key.strip()] = value.strip()
        except:
            pass
        return specs
    
    async def _extract_rating(self) -> float:
        """提取评分"""
        try:
            rating_text = await self._safe_text(".rating-score", "0")
            return float(rating_text.replace("分", ""))
        except:
            return 0.0
    
    async def _extract_reviews(self) -> List[Dict[str, Any]]:
        """提取评价"""
        reviews = []
        try:
            review_els = await self.page.query_selector_all(".review-item")
            for el in review_els[:10]:  # 最多 10 条
                content = await el.query_selector(".review-content")
                content_text = await content.text_content() if content else ""
                
                reviews.append({
                    "content": content_text.strip(),
                    "rating": 5,  # 简化处理
                    "date": "",
                })
        except:
            pass
        return reviews
```

---

### 3.2 AI 优化引擎

#### 3.2.1 LLM 客户端

```python
# src/optimizer/llm_client.py
import os
from typing import List, Dict, Any, Optional
from anthropic import AsyncAnthropic
from dataclasses import dataclass


@dataclass
class OptimizationResult:
    """优化结果"""
    keywords: List[str]  # 关键词列表
    title: str  # 优化后的标题
    bullet_points: List[str]  # 五点描述
    description: str  # 商品描述
    search_terms: List[str]  # 搜索词
    success: bool
    error_message: str = ""


class LLMClient:
    """LLM API 客户端"""
    
    def __init__(self, api_key: Optional[str] = None, provider: str = "anthropic"):
        self.provider = provider
        
        if provider == "anthropic":
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            self.client = AsyncAnthropic(api_key=self.api_key)
        elif provider == "openai":
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            # 初始化 OpenAI 客户端
        else:
            raise ValueError(f"不支持的提供商：{provider}")
    
    async def optimize_product(
        self,
        source_data: Dict[str, Any],
        target_market: str = "US",
        category: str = "",
    ) -> OptimizationResult:
        """
        优化商品信息
        
        Args:
            source_data: 源商品数据
            target_market: 目标市场 (US/EU/JP 等)
            category: 亚马逊分类
        
        Returns:
            OptimizationResult: 优化结果
        """
        prompt = self._build_optimization_prompt(source_data, target_market, category)
        
        try:
            if self.provider == "anthropic":
                response = await self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4096,
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        {"role": "user", "content": prompt}
                    ]
                )
                result_text = response.content[0].text
            else:
                # OpenAI 实现
                pass
            
            return self._parse_result(result_text)
        except Exception as e:
            return OptimizationResult(
                keywords=[],
                title="",
                bullet_points=[],
                description="",
                search_terms=[],
                success=False,
                error_message=str(e)
            )
    
    def _get_system_prompt(self) -> str:
        """系统提示词"""
        return """你是一位专业的亚马逊电商优化专家，擅长：
1. 关键词研究和 SEO 优化
2. 撰写高转化率的商品文案
3. 符合亚马逊政策的 Listing 优化

请根据提供的商品信息，生成符合亚马逊标准的优化内容。"""
    
    def _build_optimization_prompt(
        self,
        source_data: Dict[str, Any],
        target_market: str,
        category: str,
    ) -> str:
        """构建优化提示词"""
        return f"""
请优化以下商品信息，目标市场：{target_market}，分类：{category}

【原始商品信息】
- 标题：{source_data.get('title', '')}
- 价格：{source_data.get('price', '')}
- 特点：{chr(10).join(source_data.get('features', []))}
- 描述：{source_data.get('description', '')[:500]}

【输出要求】
请按以下 JSON 格式输出：
{{
    "keywords": ["核心关键词 1", "核心关键词 2", ...],
    "title": "优化后的标题（200 字符以内）",
    "bullet_points": [
        "五点描述 1（突出卖点）",
        "五点描述 2",
        "五点描述 3",
        "五点描述 4",
        "五点描述 5"
    ],
    "description": "详细的商品描述（2000 字符以内）",
    "search_terms": ["后台搜索词 1", "搜索词 2", ...]
}}

【优化原则】
1. 标题包含核心关键词，品牌名在前
2. 五点描述突出产品优势和差异化
3. 描述详细且有吸引力
4. 搜索词覆盖长尾关键词
5. 符合目标市场的语言习惯
"""
    
    def _parse_result(self, result_text: str) -> OptimizationResult:
        """解析结果"""
        import json
        try:
            # 提取 JSON 部分
            start = result_text.find("{")
            end = result_text.rfind("}") + 1
            json_str = result_text[start:end]
            
            data = json.loads(json_str)
            
            return OptimizationResult(
                keywords=data.get("keywords", []),
                title=data.get("title", ""),
                bullet_points=data.get("bullet_points", []),
                description=data.get("description", ""),
                search_terms=data.get("search_terms", []),
                success=True
            )
        except Exception as e:
            return OptimizationResult(
                keywords=[],
                title="",
                bullet_points=[],
                description="",
                search_terms=[],
                success=False,
                error_message=f"解析失败：{e}"
            )
```

#### 3.2.2 关键词优化器

```python
# src/optimizer/keyword_optimizer.py
from typing import List, Dict, Set
from dataclasses import dataclass
import re


@dataclass
class KeywordData:
    """关键词数据"""
    keyword: str
    search_volume: int  # 搜索量（估计）
    competition: str  # 竞争程度：low/medium/high
    relevance: float  # 相关性评分 0-1
    category: str  # 关键词分类


class KeywordOptimizer:
    """关键词优化器"""
    
    # 亚马逊关键词规则
    MAX_TITLE_LENGTH = 200
    MAX_BULLET_LENGTH = 250
    MAX_SEARCH_TERMS = 250  # 字节
    
    def __init__(self):
        self.stop_words = {
            "a", "an", "and", "the", "for", "with", "by", "in", "on",
            "at", "to", "from", "of", "or", "is", "are", "was", "were"
        }
    
    def extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 移除特殊字符
        text = re.sub(r"[^\w\s]", " ", text.lower())
        
        # 分词
        words = text.split()
        
        # 过滤停用词
        keywords = [w for w in words if w not in self.stop_words and len(w) > 2]
        
        # 统计词频
        from collections import Counter
        word_count = Counter(keywords)
        
        # 返回高频词
        return [word for word, count in word_count.most_common(20)]
    
    def generate_long_tail_keywords(
        self,
        core_keywords: List[str],
        product_type: str,
    ) -> List[str]:
        """生成长尾关键词"""
        long_tail = []
        
        # 组合模式
        patterns = [
            "{keyword} for {product_type}",
            "{product_type} with {keyword}",
            "best {keyword} {product_type}",
            "{keyword} {product_type} set",
        ]
        
        for keyword in core_keywords[:5]:
            for pattern in patterns:
                long_tail.append(pattern.format(keyword=keyword, product_type=product_type))
        
        return long_tail
    
    def validate_amazon_keywords(self, keywords: List[str]) -> List[str]:
        """验证关键词是否符合亚马逊政策"""
        # 禁止的词
        banned_words = {
            "best", "cheapest", "guaranteed", "100%", "free",
            "sale", "discount", "offer", "limited"
        }
        
        valid_keywords = []
        for kw in keywords:
            # 检查是否包含禁止词
            if any(banned in kw.lower() for banned in banned_words):
                continue
            
            # 检查长度
            if len(kw) > 50:
                continue
            
            valid_keywords.append(kw)
        
        return valid_keywords
    
    def optimize_for_amazon(
        self,
        title: str,
        keywords: List[str],
        category: str,
    ) -> str:
        """优化标题以符合亚马逊 SEO"""
        # 亚马逊标题公式：品牌 + 核心关键词 + 产品特性 + 规格/颜色
        
        words = title.split()
        
        # 确保核心关键词在前 80 个字符
        core_kw = keywords[0] if keywords else ""
        if core_kw and core_kw not in title[:80]:
            title = f"{core_kw} - {title}"
        
        # 截断到最大长度
        if len(title) > self.MAX_TITLE_LENGTH:
            title = title[:self.MAX_TITLE_LENGTH - 3] + "..."
        
        return title
```

#### 3.2.3 文案重构器

```python
# src/optimizer/copywriter.py
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class BulletPoint:
    """五点描述项"""
    title: str  # 小标题
    content: str  # 内容
    highlight: str  # 强调的卖点


class Copywriter:
    """文案重构器"""
    
    # 亚马逊五点描述最佳实践
    BULLET_STRUCTURE = [
        "核心卖点/独特功能",
        "产品质量/材料",
        "使用场景/适用人群",
        "规格参数/包装内容",
        "售后服务/品牌承诺"
    ]
    
    def generate_bullet_points(
        self,
        features: List[str],
        specifications: Dict[str, str],
        target_audience: str = "",
    ) -> List[BulletPoint]:
        """生成五点描述"""
        bullets = []
        
        for i, structure in enumerate(self.BULLET_STRUCTURE):
            bullet = self._create_bullet_point(
                structure=structure,
                features=features,
                specifications=specifications,
                index=i
            )
            bullets.append(bullet)
        
        return bullets
    
    def _create_bullet_point(
        self,
        structure: str,
        features: List[str],
        specifications: Dict[str, str],
        index: int,
    ) -> BulletPoint:
        """创建单个五点描述"""
        # 根据结构类型选择内容
        if "核心卖点" in structure:
            content = features[0] if features else ""
            highlight = "独特功能"
        elif "质量" in structure:
            material = specifications.get("材质", specifications.get("材料", ""))
            content = f"优质材料：{material}" if material else "高品质材料制造"
            highlight = "质量保证"
        elif "使用场景" in structure:
            content = f"适合{specifications.get('适用场景', '多种场合')}使用"
            highlight = "多功能"
        elif "规格" in structure:
            content = self._format_specifications(specifications)
            highlight = "详细规格"
        else:
            content = "30 天无理由退换，1 年质保"
            highlight = "售后保障"
        
        return BulletPoint(
            title=structure.split("/")[0],
            content=content,
            highlight=highlight
        )
    
    def _format_specifications(self, specs: Dict[str, str]) -> str:
        """格式化规格参数"""
        parts = []
        for key, value in list(specs.items())[:3]:
            parts.append(f"{key}: {value}")
        return " | ".join(parts)
    
    def optimize_description(
        self,
        original: str,
        bullet_points: List[BulletPoint],
        brand_story: str = "",
    ) -> str:
        """优化商品描述"""
        # 亚马逊描述结构
        description_parts = []
        
        # 1. 品牌介绍（可选）
        if brand_story:
            description_parts.append(f"<h3>关于品牌</h3><p>{brand_story}</p>")
        
        # 2. 产品亮点
        description_parts.append("<h3>产品亮点</h3><ul>")
        for bullet in bullet_points:
            description_parts.append(f"<li><b>{bullet.highlight}:</b> {bullet.content}</li>")
        description_parts.append("</ul>")
        
        # 3. 详细描述
        description_parts.append(f"<h3>产品描述</h3><p>{original}</p>")
        
        # 4. 规格参数
        description_parts.append("<h3>规格参数</h3>")
        description_parts.append("<p>请参阅商品图片中的详细信息图表</p>")
        
        return "".join(description_parts)
```

---

### 3.3 图片处理模块

```python
# src/optimizer/image_processor.py
from PIL import Image, ImageEnhance, ImageFilter
from pathlib import Path
from typing import List, Tuple
import requests


class ImageProcessor:
    """图片处理器"""
    
    # 亚马逊图片要求
    AMAZON_MAIN_IMAGE_SIZE = (1600, 1600)  # 推荐尺寸
    MIN_IMAGE_SIZE = (1000, 1000)  # 最小尺寸
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self, output_dir: str = "data/images"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def download_and_process(
        self,
        image_url: str,
        save_name: str,
        is_main_image: bool = False,
    ) -> str:
        """下载并处理图片"""
        # 下载
        response = requests.get(image_url)
        temp_path = self.output_dir / f"temp_{save_name}"
        
        with open(temp_path, "wb") as f:
            f.write(response.content)
        
        # 处理
        img = Image.open(temp_path)
        
        if is_main_image:
            img = self._process_main_image(img)
        else:
            img = self._process_secondary_image(img)
        
        # 保存
        final_path = self.output_dir / save_name
        img.save(final_path, "JPEG", quality=95)
        
        # 清理临时文件
        temp_path.unlink()
        
        return str(final_path)
    
    def _process_main_image(self, img: Image.Image) -> Image.Image:
        """处理主图（白底要求）"""
        # 调整尺寸
        img = img.resize(self.AMAZON_MAIN_IMAGE_SIZE, Image.Resampling.LANCZOS)
        
        # 增强对比度
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        
        # 增强亮度
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.1)
        
        # 锐化
        img = img.filter(ImageFilter.SHARPEN)
        
        return img
    
    def _process_secondary_image(self, img: Image.Image) -> Image.Image:
        """处理辅图"""
        # 确保最小尺寸
        if min(img.size) < self.MIN_IMAGE_SIZE[0]:
            scale = self.MIN_IMAGE_SIZE[0] / min(img.size)
            new_size = (int(img.size[0] * scale), int(img.size[1] * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        return img
    
    def create_image_grid(
        self,
        image_paths: List[str],
        output_name: str,
        grid_size: Tuple[int, int] = (2, 2),
    ) -> str:
        """创建图片拼图"""
        images = [Image.open(p) for p in image_paths[:4]]
        
        # 统一尺寸
        target_size = (800, 800)
        images = [img.resize(target_size, Image.Resampling.LANCZOS) for img in images]
        
        # 创建拼图
        grid_width = target_size[0] * grid_size[0]
        grid_height = target_size[1] * grid_size[1]
        
        grid_image = Image.new("RGB", (grid_width, grid_height), "white")
        
        for i, img in enumerate(images):
            x = (i % grid_size[0]) * target_size[0]
            y = (i // grid_size[0]) * target_size[1]
            grid_image.paste(img, (x, y))
        
        output_path = self.output_dir / output_name
        grid_image.save(output_path, "JPEG", quality=90)
        
        return str(output_path)
    
    def add_text_overlay(
        self,
        image_path: str,
        text: str,
        position: Tuple[int, int] = (50, 50),
    ) -> str:
        """添加文字覆盖（用于功能说明图）"""
        from PIL import ImageDraw, ImageFont
        
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        # 尝试加载字体
        try:
            font = ImageFont.truetype("arial.ttf", 48)
        except:
            font = ImageFont.load_default()
        
        # 添加半透明背景
        draw.rectangle(
            [position[0] - 10, position[1] - 10, position[0] + 500, position[1] + 60],
            fill=(0, 0, 0, 128)
        )
        
        # 添加文字
        draw.text(position, text, fill=(255, 255, 255), font=font)
        
        output_path = self.output_dir / f"overlay_{Path(image_path).name}"
        img.save(output_path, "JPEG", quality=90)
        
        return str(output_path)
```

---

## 4. 工作流程详解

### 4.1 完整工作流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           完整工作流程图                                     │
└─────────────────────────────────────────────────────────────────────────────┘

Step 1: 数据采集
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  用户输入商品 URL ──► 选择源平台 ──► 启动爬虫 ──► 提取数据 ──► 保存图片    │
│                                                                              │
│  输出：raw_product_data.json + images/                                      │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
Step 2: AI 优化
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  读取原始数据 ──► 调用 LLM API ──► 生成关键词 ──► 重写文案 ──► 处理图片   │
│                                                                              │
│  输出：optimized_product_data.json                                          │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
Step 3: 人工审核
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  启动 Web 界面 ──► 显示优化结果 ──► 人工编辑 ──► 确认通过 ──► 保存数据   │
│                                                                              │
│  输出：reviewed_product_data.json                                           │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
Step 4: 上传亚马逊
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  生成上传模板 ──► 登录亚马逊 ──► 自动填写表单 ──► 上传图片 ──► 提交审核  │
│                                                                              │
│  输出：upload_report.json                                                   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 状态机设计

```python
# src/reviewer/review_manager.py
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
from pathlib import Path


class ReviewStatus(Enum):
    """审核状态"""
    PENDING = "pending"  # 待审核
    IN_REVIEW = "in_review"  # 审核中
    APPROVED = "approved"  # 已通过
    REJECTED = "rejected"  # 已拒绝
    NEEDS_EDIT = "needs_edit"  # 需要修改


@dataclass
class ProductReview:
    """商品审核记录"""
    product_id: str
    source_data: Dict[str, Any]
    optimized_data: Dict[str, Any]
    reviewed_data: Optional[Dict[str, Any]] = None
    
    status: ReviewStatus = ReviewStatus.PENDING
    reviewer_notes: str = ""
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    reviewed_at: Optional[str] = None
    reviewed_by: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "product_id": self.product_id,
            "source_data": self.source_data,
            "optimized_data": self.optimized_data,
            "reviewed_data": self.reviewed_data,
            "status": self.status.value,
            "reviewer_notes": self.reviewer_notes,
            "created_at": self.created_at,
            "reviewed_at": self.reviewed_at,
            "reviewed_by": self.reviewed_by,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProductReview":
        """从字典创建"""
        data["status"] = ReviewStatus(data["status"])
        return cls(**data)


class ReviewManager:
    """审核管理器"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.reviews_file = self.data_dir / "reviews.json"
        self.reviews: List[ProductReview] = []
        self._load_reviews()
    
    def _load_reviews(self):
        """加载审核记录"""
        if self.reviews_file.exists():
            with open(self.reviews_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.reviews = [ProductReview.from_dict(d) for d in data]
    
    def _save_reviews(self):
        """保存审核记录"""
        with open(self.reviews_file, "w", encoding="utf-8") as f:
            json.dump([r.to_dict() for r in self.reviews], f, indent=2, ensure_ascii=False)
    
    def add_product(
        self,
        product_id: str,
        source_data: Dict[str, Any],
        optimized_data: Dict[str, Any],
    ) -> ProductReview:
        """添加待审核商品"""
        review = ProductReview(
            product_id=product_id,
            source_data=source_data,
            optimized_data=optimized_data,
        )
        self.reviews.append(review)
        self._save_reviews()
        return review
    
    def get_pending_reviews(self) -> List[ProductReview]:
        """获取待审核列表"""
        return [r for r in self.reviews if r.status == ReviewStatus.PENDING]
    
    def update_review(
        self,
        product_id: str,
        reviewed_data: Dict[str, Any],
        status: ReviewStatus,
        reviewer_notes: str = "",
        reviewer: str = "",
    ) -> bool:
        """更新审核结果"""
        for review in self.reviews:
            if review.product_id == product_id:
                review.reviewed_data = reviewed_data
                review.status = status
                review.reviewer_notes = reviewer_notes
                review.reviewed_at = datetime.now().isoformat()
                review.reviewed_by = reviewer
                self._save_reviews()
                return True
        return False
    
    def get_approved_products(self) -> List[ProductReview]:
        """获取已通过的商品"""
        return [r for r in self.reviews if r.status == ReviewStatus.APPROVED]
```

---

## 5. 人机交互审核系统

### 5.1 Streamlit Web 界面

```python
# migration_app.py
import streamlit as st
from pathlib import Path
import json
from src.reviewer.review_manager import ReviewManager, ReviewStatus
from src.optimizer.llm_client import LLMClient
from src.crawler.taobao_crawler import TaobaoCrawler


st.set_page_config(
    page_title="商品数据迁移系统",
    page_icon="🛒",
    layout="wide"
)


def init_session():
    """初始化会话状态"""
    if "review_manager" not in st.session_state:
        st.session_state.review_manager = ReviewManager()
    if "current_product" not in st.session_state:
        st.session_state.current_product = None


def sidebar_navigation():
    """侧边栏导航"""
    st.sidebar.title("导航")
    
    page = st.sidebar.radio(
        "选择页面",
        ["数据采集", "AI 优化", "人工审核", "上传管理"]
    )
    
    return page


def page_data_collection():
    """数据采集页面"""
    st.title("📥 数据采集")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        url = st.text_input("商品 URL", placeholder="粘贴商品链接...")
        platform = st.selectbox(
            "源平台",
            ["淘宝", "1688", "速卖通", "其他"],
        )
    
    with col2:
        st.markdown("### 采集统计")
        review_manager = st.session_state.review_manager
        st.metric("已采集商品", len(review_manager.reviews))
        st.metric("待审核", len(review_manager.get_pending_reviews()))
    
    if st.button("开始采集", type="primary"):
        if url:
            with st.spinner("正在采集商品数据..."):
                try:
                    crawler = TaobaoCrawler(headless=True)
                    product_data = crawler.fetch_product(url)
                    
                    # 保存原始数据
                    st.session_state.current_product = product_data
                    st.success("采集成功！")
                    
                    # 显示预览
                    st.json(product_data.__dict__)
                    
                except Exception as e:
                    st.error(f"采集失败：{e}")
        else:
            st.warning("请输入商品 URL")


def page_ai_optimization():
    """AI 优化页面"""
    st.title("🤖 AI 优化")
    
    if st.session_state.current_product is None:
        st.info("请先在「数据采集」页面采集商品数据")
        return
    
    product = st.session_state.current_product
    
    # 显示原始数据预览
    st.markdown("### 原始数据")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("原始标题", product.title, disabled=True)
        st.text_area("原始描述", product.description, height=200, disabled=True)
    with col2:
        st.multiselect("原始特点", product.features, disabled=True)
    
    # 优化配置
    st.markdown("### 优化配置")
    col1, col2 = st.columns(2)
    with col1:
        target_market = st.selectbox("目标市场", ["美国", "欧洲", "日本", "其他"])
        category = st.text_input("亚马逊分类")
    with col2:
        brand_name = st.text_input("品牌名")
        brand_story = st.text_area("品牌故事", height=100)
    
    if st.button("开始优化", type="primary"):
        with st.spinner("AI 正在优化商品信息..."):
            try:
                llm = LLMClient()
                result = llm.optimize_product(
                    source_data=product.__dict__,
                    target_market=target_market,
                    category=category,
                )
                
                if result.success:
                    st.success("优化成功！")
                    
                    # 存储优化结果
                    optimized_data = {
                        "title": result.title,
                        "bullet_points": result.bullet_points,
                        "description": result.description,
                        "keywords": result.keywords,
                        "search_terms": result.search_terms,
                    }
                    st.session_state.optimized_data = optimized_data
                    
                    # 显示优化结果
                    st.markdown("### 优化结果")
                    st.text_input("优化后标题", result.title)
                    st.text_area("优化后描述", result.description, height=200)
                    
                    st.markdown("### 五点描述")
                    for i, bullet in enumerate(result.bullet_points, 1):
                        st.text_area(f"要点 {i}", bullet, height=100)
                    
                    st.markdown("### 关键词")
                    st.write(", ".join(result.keywords))
                    
                else:
                    st.error(f"优化失败：{result.error_message}")
                    
            except Exception as e:
                st.error(f"优化过程出错：{e}")


def page_manual_review():
    """人工审核页面"""
    st.title("✍️ 人工审核")
    
    review_manager = st.session_state.review_manager
    
    # 获取待审核列表
    pending = review_manager.get_pending_reviews()
    
    if not pending:
        st.info("暂无待审核商品")
        return
    
    # 选择商品
    product_options = {p.product_id: p.source_data.get("title", "")[:50] for p in pending}
    selected_id = st.selectbox("选择商品", list(product_options.keys()), format_func=lambda x: product_options[x])
    
    if selected_id:
        review = next(r for r in pending if r.product_id == selected_id)
        
        # 显示优化结果供审核
        st.markdown("### 审核内容")
        
        # 标题编辑
        optimized = st.session_state.get("optimized_data", {})
        reviewed_title = st.text_input(
            "标题",
            optimized.get("title", review.source_data.get("title", "")),
            help="建议长度：150-200 字符"
        )
        
        # 五点描述编辑
        st.markdown("#### 五点描述")
        reviewed_bullets = []
        for i in range(5):
            bullet = st.text_area(
                f"要点 {i+1}",
                optimized.get("bullet_points", [""]*5)[i] if i < len(optimized.get("bullet_points", [])) else "",
                height=80,
                key=f"bullet_{i}"
            )
            reviewed_bullets.append(bullet)
        
        # 描述编辑
        reviewed_description = st.text_area(
            "商品描述",
            optimized.get("description", ""),
            height=300,
            help="支持 HTML 格式"
        )
        
        # 关键词编辑
        reviewed_keywords = st.text_input(
            "关键词",
            ", ".join(optimized.get("keywords", [])),
            help="用逗号分隔"
        )
        
        # 审核操作
        st.markdown("### 审核操作")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ 通过", type="primary", use_container_width=True):
                reviewed_data = {
                    "title": reviewed_title,
                    "bullet_points": reviewed_bullets,
                    "description": reviewed_description,
                    "keywords": [k.strip() for k in reviewed_keywords.split(",")],
                }
                review_manager.update_review(
                    product_id=selected_id,
                    reviewed_data=reviewed_data,
                    status=ReviewStatus.APPROVED,
                    reviewer="当前用户"
                )
                st.success("审核通过！")
                st.rerun()
        
        with col2:
            if st.button("✏️ 需要修改", use_container_width=True):
                review_manager.update_review(
                    product_id=selected_id,
                    reviewed_data={},
                    status=ReviewStatus.NEEDS_EDIT,
                    reviewer_notes=st.text_area("修改意见"),
                    reviewer="当前用户"
                )
                st.warning("已标记为需要修改")
                st.rerun()
        
        with col3:
            if st.button("❌ 拒绝", use_container_width=True):
                review_manager.update_review(
                    product_id=selected_id,
                    reviewed_data={},
                    status=ReviewStatus.REJECTED,
                    reviewer_notes=st.text_area("拒绝原因"),
                    reviewer="当前用户"
                )
                st.error("已拒绝")
                st.rerun()


def page_upload_management():
    """上传管理页面"""
    st.title("📤 上传管理")
    
    review_manager = st.session_state.review_manager
    approved = review_manager.get_approved_products()
    
    if not approved:
        st.info("暂无已通过的商品")
        return
    
    st.markdown(f"### 已通过商品 ({len(approved)})")
    
    for product in approved:
        with st.expander(product.reviewed_data.get("title", "未知商品")):
            st.json(product.reviewed_data)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("生成上传模板"):
                    # 生成 CSV 模板
                    generate_amazon_csv(product.reviewed_data)
                    st.success("模板已生成")
            
            with col2:
                if st.button("自动上传"):
                    st.info("正在启动自动上传流程...")
                    # 调用自动上传模块
                    # auto_upload(product.reviewed_data)


def generate_amazon_csv(product_data: dict):
    """生成亚马逊上传 CSV"""
    import csv
    from pathlib import Path
    
    output_path = Path("output/amazon_upload.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # 写入表头
        writer.writerow([
            "item_sku", "item_name", "item_description",
            "bullet_point1", "bullet_point2", "bullet_point3",
            "bullet_point4", "bullet_point5", "search_terms"
        ])
        
        # 写入数据
        writer.writerow([
            f"SKU-{product_data.get('asin', '001')}",
            product_data.get("title", ""),
            product_data.get("description", ""),
            product_data.get("bullet_points", [""]*5)[0] if len(product_data.get("bullet_points", [])) > 0 else "",
            product_data.get("bullet_points", [""]*5)[1] if len(product_data.get("bullet_points", [])) > 1 else "",
            product_data.get("bullet_points", [""]*5)[2] if len(product_data.get("bullet_points", [])) > 2 else "",
            product_data.get("bullet_points", [""]*5)[3] if len(product_data.get("bullet_points", [])) > 3 else "",
            product_data.get("bullet_points", [""]*5)[4] if len(product_data.get("bullet_points", [])) > 4 else "",
            " ".join(product_data.get("keywords", []))
        ])
    
    return str(output_path)


def main():
    """主函数"""
    init_session()
    
    page = sidebar_navigation()
    
    if page == "数据采集":
        page_data_collection()
    elif page == "AI 优化":
        page_ai_optimization()
    elif page == "人工审核":
        page_manual_review()
    elif page == "上传管理":
        page_upload_management()


if __name__ == "__main__":
    main()
```

### 5.2 审核界面截图示意

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🛒 商品数据迁移系统                    导航：数据采集 | AI 优化 | 人工审核 | 上传管理  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✍️ 人工审核                                                                 │
│                                                                             │
│  选择商品：[ Owala FreeSip 不锈钢水瓶... ▼ ]                                │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 审核内容                                                             │   │
│  │                                                                      │   │
│  │ 标题：[Owala FreeSip Insulated Stainless Steel Water Bottle...    ] │   │
│  │        建议长度：150-200 字符                                         │   │
│  │                                                                      │   │
│  │ 五点描述：                                                           │   │
│  │ ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │ │ 要点 1: [🔥 UNIQUE FREE SIP TECHNOLOGY - Designed with a...   ] │ │   │
│  │ │          [80 chars]                                              │ │   │
│  │ └─────────────────────────────────────────────────────────────────┘ │   │
│  │ ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │ │ 要点 2: [💧 PREMIUM QUALITY - Made with food-grade stainless..] │ │   │
│  │ │          [80 chars]                                              │ │   │
│  │ └─────────────────────────────────────────────────────────────────┘ │   │
│  │ ... (要点 3-5)                                                       │   │
│  │                                                                      │   │
│  │ 商品描述：                                                           │   │
│  │ ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │ │ [<h3>Product Highlights</h3>                                   ] │ │   │
│  │ │  [Stay hydrated in style with the Owala FreeSip...]            ] │ │   │
│  │ │  ...                                                             │ │   │
│  │ └─────────────────────────────────────────────────────────────────┘ │   │
│  │                                                                      │   │
│  │ 关键词：[water bottle, insulated, stainless steel, free sip, ...]  │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 审核操作                                                             │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │   ✅ 通过    │  │  ✏️ 需要修改  │  │   ❌ 拒绝    │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. 完整代码实现

### 6.1 主程序入口

```python
# main.py
import asyncio
import click
import logging
from pathlib import Path
from src.crawler.taobao_crawler import TaobaoCrawler
from src.optimizer.llm_client import LLMClient
from src.optimizer.image_processor import ImageProcessor
from src.reviewer.review_manager import ReviewManager


@click.group()
def cli():
    """电商商品数据迁移工具"""
    pass


@cli.command()
@click.option("--url", required=True, help="商品 URL")
@click.option("--platform", default="taobao", help="源平台")
@click.option("--output", default="data/raw", help="输出目录")
@click.option("--headless", is_flag=True, help="无头模式")
def collect(url, platform, output, headless):
    """采集商品数据"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    async def run():
        if platform == "taobao":
            crawler = TaobaoCrawler(headless=headless)
        else:
            logger.error(f"不支持的平台：{platform}")
            return
        
        try:
            logger.info(f"开始采集：{url}")
            product = await crawler.fetch_product(url)
            
            # 保存数据
            output_path = Path(output)
            output_path.mkdir(parents=True, exist_ok=True)
            
            import json
            with open(output_path / "product.json", "w", encoding="utf-8") as f:
                json.dump(product.__dict__, f, indent=2, ensure_ascii=False)
            
            # 下载图片
            if product.images:
                img_processor = ImageProcessor(str(output_path / "images"))
                for i, img_url in enumerate(product.images[:10]):
                    img_processor.download_and_process(
                        img_url,
                        f"image_{i}.jpg",
                        is_main_image=(i == 0)
                    )
            
            logger.info(f"采集完成，数据已保存到：{output_path}")
            
        except Exception as e:
            logger.error(f"采集失败：{e}")
        finally:
            await crawler.close()
    
    asyncio.run(run())


@cli.command()
@click.option("--input", "input_file", required=True, help="输入商品数据文件")
@click.option("--output", default="data/processed", help="输出目录")
@click.option("--market", default="US", help="目标市场")
@click.option("--api-key", help="LLM API Key")
def optimize(input_file, output, market, api_key):
    """优化商品信息"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    async def run():
        # 加载数据
        with open(input_file, "r", encoding="utf-8") as f:
            product_data = json.load(f)
        
        # 初始化优化器
        llm = LLMClient(api_key=api_key)
        
        try:
            logger.info("开始 AI 优化...")
            result = await llm.optimize_product(
                source_data=product_data,
                target_market=market
            )
            
            if result.success:
                # 保存优化结果
                output_path = Path(output)
                output_path.mkdir(parents=True, exist_ok=True)
                
                import json
                with open(output_path / "optimized.json", "w", encoding="utf-8") as f:
                    json.dump({
                        "title": result.title,
                        "bullet_points": result.bullet_points,
                        "description": result.description,
                        "keywords": result.keywords,
                        "search_terms": result.search_terms,
                    }, f, indent=2, ensure_ascii=False)
                
                logger.info(f"优化完成，结果已保存到：{output_path}")
            else:
                logger.error(f"优化失败：{result.error_message}")
                
        except Exception as e:
            logger.error(f"优化过程出错：{e}")
    
    asyncio.run(run())


@cli.command()
@click.option("--input", "input_file", required=True, help="审核通过的数据文件")
@click.option("--output", default="output/amazon_upload.csv", help="输出 CSV 文件")
def generate_template(input_file, output):
    """生成亚马逊上传模板"""
    import json
    import csv
    from pathlib import Path
    
    # 加载数据
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # 表头
        writer.writerow([
            "item_sku", "item_name", "item_description",
            "bullet_point1", "bullet_point2", "bullet_point3",
            "bullet_point4", "bullet_point5", "search_terms",
            "main_image_url", "other_image_urls"
        ])
        
        # 数据行
        writer.writerow([
            f"SKU-{data.get('asin', '001')}",
            data.get("title", ""),
            data.get("description", ""),
            data.get("bullet_points", [""]*5)[0],
            data.get("bullet_points", [""]*5)[1],
            data.get("bullet_points", [""]*5)[2],
            data.get("bullet_points", [""]*5)[3],
            data.get("bullet_points", [""]*5)[4],
            " ".join(data.get("keywords", [])),
            data.get("images", [""])[0],
            " | ".join(data.get("images", [""])[1:5])
        ])
    
    click.echo(f"模板已生成：{output_path}")


@cli.command()
@click.option("--data", "data_file", required=True, help="审核通过的数据文件")
@click.option("--headless", is_flag=True, help="无头模式")
def upload(data_file, headless):
    """自动上传到亚马逊"""
    import json
    from src.amazon_login import AmazonLogin
    from src.uploader.amazon_form_filler import AmazonFormFiller
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    async def run():
        # 加载数据
        with open(data_file, "r", encoding="utf-8") as f:
            product_data = json.load(f)
        
        # 登录亚马逊
        login = AmazonLogin(
            email="your_seller_email",
            password="your_password",
            headless=headless
        )
        
        try:
            # 登录
            if not await login.login():
                logger.error("登录失败")
                return
            
            # 填写表单
            filler = AmazonFormFiller(login.page)
            await filler.fill_product_form(product_data)
            
            logger.info("上传完成")
            
        except Exception as e:
            logger.error(f"上传失败：{e}")
        finally:
            await login.close()
    
    asyncio.run(run())


if __name__ == "__main__":
    cli()
```

### 6.2 亚马逊表单填写器

```python
# src/uploader/amazon_form_filler.py
from playwright.async_api import Page
from typing import Dict, List, Any
import asyncio
import random


class AmazonFormFiller:
    """亚马逊表单填写器"""
    
    # 卖家后台表单选择器
    SELECTORS = {
        # 添加商品入口
        "add_product_btn": "#addProductButton",
        "add_new_product": "a[href*='create-new-asin']",
        
        # 基本信息
        "product_name": "#productTitle",
        "brand": "#brand",
        "manufacturer": "#manufacturer",
        
        # 分类
        "category_tree": "#categoryTree",
        
        # 价格库存
        "standard_price": "#standardPrice",
        "quantity": "#quantity",
        "sku": "#sku",
        
        # 描述
        "description": "#productDescription",
        "bullet_points": ".bullet-point-input",
        
        # 关键词
        "search_terms": "#searchTerms",
        "subject_matter": "#subjectMatter",
        
        # 图片
        "image_upload": "#imageUpload",
        "image_url_input": ".image-url-input",
        
        # 提交
        "save_finish": "#saveAndFinishButton",
    }
    
    def __init__(self, page: Page):
        self.page = page
    
    async def fill_product_form(self, product_data: Dict[str, Any]):
        """填写商品表单"""
        # 1. 进入添加商品页面
        await self._navigate_to_add_product()
        
        # 2. 填写基本信息
        await self._fill_basic_info(product_data)
        
        # 3. 填写价格库存
        await self._fill_price_inventory(product_data)
        
        # 4. 填写商品描述
        await self._fill_description(product_data)
        
        # 5. 上传图片
        await self._upload_images(product_data)
        
        # 6. 保存并提交
        await self._submit_form()
    
    async def _navigate_to_add_product(self):
        """导航到添加商品页面"""
        await self.page.goto("https://sellercentral.amazon.com/product/add")
        await self.page.wait_for_timeout(3000)
    
    async def _fill_basic_info(self, data: Dict[str, Any]):
        """填写基本信息"""
        # 商品名称
        await self._safe_fill(self.SELECTORS["product_name"], data.get("title", ""))
        
        # 品牌
        await self._safe_fill(self.SELECTORS["brand"], data.get("brand", ""))
        
        # 分类（需要选择）
        if data.get("category"):
            await self._select_category(data["category"])
    
    async def _fill_price_inventory(self, data: Dict[str, Any]):
        """填写价格和库存"""
        # SKU
        await self._safe_fill(self.SELECTORS["sku"], data.get("sku", ""))
        
        # 价格
        price = self._parse_price(data.get("price", "0"))
        await self._safe_fill(self.SELECTORS["standard_price"], str(price))
        
        # 库存
        await self._safe_fill(self.SELECTORS["quantity"], str(data.get("quantity", "100")))
    
    async def _fill_description(self, data: Dict[str, Any]):
        """填写商品描述"""
        # 五点描述
        bullets = data.get("bullet_points", [])
        bullet_els = await self.page.query_selector_all(self.SELECTORS["bullet_points"])
        
        for i, bullet_el in enumerate(bullet_els[:5]):
            if i < len(bullets):
                await bullet_el.fill(bullets[i])
                await asyncio.sleep(random.uniform(0.3, 0.8))  # 模拟人类输入
        
        # 商品描述
        await self._safe_fill(self.SELECTORS["description"], data.get("description", ""))
        
        # 搜索关键词
        await self._safe_fill(
            self.SELECTORS["search_terms"],
            " ".join(data.get("keywords", [])[:10])
        )
    
    async def _upload_images(self, data: Dict[str, Any]):
        """上传图片"""
        images = data.get("images", [])
        
        if not images:
            return
        
        # 点击上传按钮
        await self.page.click(self.SELECTORS["image_upload"])
        
        # 输入图片 URL（或上传本地文件）
        for i, img_url in enumerate(images[:9]):
            url_input = await self.page.query_selector(
                f"{self.SELECTORS['image_url_input']}:nth-of-type({i+1})"
            )
            if url_input:
                await url_input.fill(img_url)
    
    async def _submit_form(self):
        """提交表单"""
        # 滚动到页面底部
        await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1000)
        
        # 点击保存
        await self.page.click(self.SELECTORS["save_finish"])
        
        # 等待提交完成
        await self.page.wait_for_timeout(5000)
    
    async def _safe_fill(self, selector: str, value: str):
        """安全填充输入框"""
        try:
            el = await self.page.wait_for_selector(selector, timeout=5000)
            if el and value:
                await el.fill(value)
                await asyncio.sleep(random.uniform(0.2, 0.5))
        except Exception as e:
            print(f"填充失败 {selector}: {e}")
    
    async def _select_category(self, category: str):
        """选择分类"""
        try:
            category_el = await self.page.wait_for_selector(self.SELECTORS["category_tree"])
            await category_el.click()
            
            # 输入分类名称
            await self.page.keyboard.type(category)
            await asyncio.sleep(500)
            
            # 选择第一个匹配项
            await self.page.keyboard.press("Enter")
        except Exception as e:
            print(f"选择分类失败：{e}")
    
    def _parse_price(self, price_str: str) -> float:
        """解析价格字符串"""
        import re
        match = re.search(r"[\d.]+", price_str.replace(",", ""))
        return float(match.group()) if match else 0.0
```

---

## 7. 部署与配置

### 7.1 环境配置

```yaml
# config/settings.yaml
# 系统配置

# LLM 配置
llm:
  provider: anthropic  # anthropic / openai
  api_key_env: ANTHROPIC_API_KEY
  model: claude-sonnet-4-20250514
  max_tokens: 4096

# 爬虫配置
crawler:
  headless: false
  timeout: 30000
  proxy: null
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."

# 亚马逊账号配置
amazon:
  seller_email: ${AMAZON_SELLER_EMAIL}
  seller_password: ${AMAZON_SELLER_PASSWORD}
  marketplace: US  # US / EU / JP

# 图片配置
image:
  download_enabled: true
  max_images: 10
  output_dir: data/images
  compress: true

# 日志配置
logging:
  level: INFO
  file: logs/migration.log
```

### 7.2 环境变量

```bash
# .env
# LLM API Keys
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx

# 亚马逊账号
AMAZON_SELLER_EMAIL=your@email.com
AMAZON_SELLER_PASSWORD=your_password

# 代理配置（可选）
PROXY_SERVER=http://proxy:port
PROXY_USERNAME=username
PROXY_PASSWORD=password
```

### 7.3 依赖安装

```toml
# pyproject.toml
[project]
name = "ecommerce-data-migration"
version = "0.1.0"
requires-python = ">=3.10"

dependencies = [
    "playwright>=1.40.0",
    "playwright-stealth>=1.0.6",
    "anthropic>=0.18.0",
    "openai>=1.0.0",
    "streamlit>=1.30.0",
    "click>=8.0.0",
    "pillow>=10.0.0",
    "aiohttp>=3.9.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.0.0",
    "beautifulsoup4>=4.12.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
]
```

### 7.4 快速启动

```bash
# 1. 安装依赖
uv sync

# 2. 安装浏览器
uv run playwright install chromium

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Key 和账号

# 4. 启动 Web 审核界面
uv run streamlit run migration_app.py

# 5. 或使用 CLI 工具
uv run python main.py collect --url "https://item.taobao.com/xxx"
uv run python main.py optimize --input data/raw/product.json
uv run python main.py generate-template --input data/reviewed/product.json
uv run python main.py upload --data data/reviewed/product.json
```

---

## 附录

### A. 亚马逊 Listing 政策要点

| 字段 | 要求 | 最佳实践 |
|------|------|----------|
| 标题 | ≤200 字符 | 品牌 + 核心词 + 特性 + 规格 |
| 五点描述 | 每点≤250 字符 | 突出卖点，包含关键词 |
| 商品描述 | ≤2000 字符 | 使用 HTML 格式化 |
| 搜索词 | ≤250 字节 | 不重复，包含长尾词 |
| 主图 | 纯白背景 | 1600x1600px 以上 |

### B. 常见问题

| 问题 | 解决方案 |
|------|----------|
| LLM 输出格式错误 | 添加 JSON Schema 验证 |
| 亚马逊表单选择器变化 | 定期更新 SELECTORS 字典 |
| 图片上传失败 | 检查图片尺寸和格式 |
| 验证码拦截 | 接入打码平台或人工处理 |

### C. 扩展功能建议

1. **批量处理** - 支持 Excel 批量导入 URL
2. **竞品分析** - 自动分析竞品 Listing
3. **A/B 测试** - 生成多个版本文案测试
4. **价格监控** - 跟踪竞品价格变化
5. **库存同步** - 与 ERP 系统集成

---

*文档版本：0.1.0 | 最后更新：2026-03-12*
