# AI 超级智能体集成技术文档

> **将电商数据迁移系统与 AI 智能体框架（OpenHands/LangChain/AutoGen）深度集成，实现企业级自动化提效**
>
> 本文档详细分析如何将现有的爬虫、数据迁移、飞书集成系统与 AI 智能体框架结合，构建企业级自动化工作流。

---

## 目录

1. [AI 智能体框架概述](#1-ai-智能体框架概述)
2. [系统集成架构](#2-系统集成架构)
3. [智能体工具设计](#3-智能体工具设计)
4. [企业提效场景](#4-企业提效场景)
5. [核心模块实现](#5-核心模块实现)
6. [部署与配置](#6-部署与配置)

---

## 1. AI 智能体框架概述

### 1.1 主流 AI 智能体框架对比

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AI 智能体框架对比矩阵                                  │
├──────────────────┬──────────────────┬──────────────────┬────────────────────┤
│       特性        │    OpenHands    │   LangChain      │     AutoGen        │
│                  │   (OpenClaw)    │   Agents         │   (Microsoft)      │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ 核心定位         │ 通用任务智能体   │ LLM 应用开发框架  │ 多智能体协作       │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ 工具调用         │ ✅ 内置工具库    │ ✅ 可自定义      │ ✅ 可自定义        │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ 代码执行         │ ✅ 沙箱环境      │ ⚠️ 需配置        │ ⚠️ 需配置          │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ 多模态支持       │ ✅ 视觉 + 文本   │ ✅ 扩展支持      │ ⚠️ 有限支持        │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ 多智能体协作     │ ⚠️ 基础支持      │ ⚠️ 需扩展        │ ✅ 核心特性        │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ 企业级部署       │ ✅ Docker 支持    │ ✅ 灵活部署      │ ✅ 灵活部署        │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ 学习曲线         │ 低               │ 中等             │ 中等              │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ 适合场景         │ 通用任务自动化   │ LLM 应用开发     │ 复杂协作任务      │
└──────────────────┴──────────────────┴──────────────────┴────────────────────┘
```

### 1.2 OpenHands (OpenClaw) 架构分析

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        OpenHands 智能体架构                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      用户交互层 (User Interface)                     │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │   Web UI     │  │   CLI        │  │   API        │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                      │
│  ┌───────────────────────────────────┼───────────────────────────────────┐ │
│  │                      智能体核心层 (Agent Core)                         │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │ │
│  │  │                    Agent Controller                             │  │ │
│  │  │  ┌────────────┐  ┌────────────┐  ┌────────────┐                │  │ │
│  │  │  │  规划器    │  │  记忆管理  │  │  决策引擎  │                │  │ │
│  │  │  │  Planner   │  │  Memory    │  │  Decision  │                │  │ │
│  │  │  └────────────┘  └────────────┘  └────────────┘                │  │ │
│  │  └─────────────────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                      │                                      │
│  ┌───────────────────────────────────┼───────────────────────────────────┐ │
│  │                      工具执行层 (Tool Execution)                       │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │ │
│  │  │  Bash 工具   │  │  Python 工具  │  │  浏览器工具  │  │  自定义   │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘ │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                      │                                      │
│  ┌───────────────────────────────────┼───────────────────────────────────┐ │
│  │                      LLM 服务层 (LLM Providers)                        │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │ │
│  │  │   Claude     │  │   GPT-4      │  │  本地模型    │                │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 为什么需要集成 AI 智能体

| 传统自动化 | AI 智能体增强后 |
|------------|-----------------|
| ❌ 固定流程，无法处理异常 | ✅ 自主决策，灵活应对 |
| ❌ 需要人工配置每个步骤 | ✅ 自然语言指令驱动 |
| ❌ 错误处理复杂 | ✅ 自我修复和重试 |
| ❌ 无法理解业务上下文 | ✅ 理解语义和意图 |
| ❌ 扩展性差 | ✅ 可组合新工具和能力 |

---

## 2. 系统集成架构

### 2.1 整体集成架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           企业级 AI 智能体集成架构                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      业务应用层 (Business Apps)                      │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │  飞书多维表格 │  │  亚马逊后台  │  │  电商平台    │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│           ▲                    ▲                    ▲                       │
│           │                    │                    │                       │
│  ┌────────┴────────────────────┴────────────────────┴───────────────────┐  │
│  │                      智能体工具层 (Agent Tools)                       │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │  │
│  │  │  爬虫工具    │  │  数据同步工具│  │  AI 优化工具  │  │ 审核工具 │ │  │
│  │  │  CrawlerTool │  │  SyncTool    │  │  Optimizer   │  │ Review   │ │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────┘ │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                      │                                      │
│  ┌───────────────────────────────────┼───────────────────────────────────┐ │
│  │                      AI 智能体框架 (Agent Framework)                   │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │ │
│  │  │                   OpenHands / LangChain / AutoGen               │  │ │
│  │  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐ │  │ │
│  │  │  │  任务规划  │  │  工具调用  │  │  记忆管理  │  │  结果生成 │ │  │ │
│  │  │  └────────────┘  └────────────┘  └────────────┘  └───────────┘ │  │ │
│  │  └─────────────────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                      │                                      │
│  ┌───────────────────────────────────┼───────────────────────────────────┐ │
│  │                      用户交互层 (User Interface)                       │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │ │
│  │  │  自然语言    │  │  飞书机器人  │  │  Web 控制台   │                │ │
│  │  │  "采集这个商品"│  │  "@机器人同步"│  │  任务监控   │                │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流与交互流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   用户指令   │────►│  AI 智能体   │────►│  工具调用   │────►│  执行动作   │
│  自然语言   │     │  理解意图   │     │  选择工具   │     │  爬虫/API  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       ▲                                                           │
       │                                                           │
       │              ┌─────────────┐     ┌─────────────┐          │
       └──────────────│  结果反馈   │◄────│  数据写入   │◄─────────┘
                      │  飞书/邮件  │     │  数据库    │
                      └─────────────┘     └─────────────┘
```

### 2.3 工具注册机制

```python
# 智能体工具注册表
AGENT_TOOL_REGISTRY = {
    "crawler": {
        "taobao": TaobaoCrawlerTool,
        "1688": AlibabaCrawlerTool,
        "amazon": AmazonCrawlerTool,
    },
    "optimizer": {
        "keyword": KeywordOptimizerTool,
        "copywriter": CopywriterTool,
        "image": ImageProcessorTool,
    },
    "sync": {
        "feishu": FeishuSyncTool,
        "amazon_upload": AmazonUploadTool,
    },
    "review": {
        "approve": ReviewApproveTool,
        "reject": ReviewRejectTool,
    }
}
```

---

## 3. 智能体工具设计

### 3.1 工具基类设计

```python
# src/agents/base_tool.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class ToolResult:
    """工具执行结果"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "message": self.message,
            "metadata": self.metadata,
        }


@dataclass
class ToolDefinition:
    """工具定义（用于 LLM 理解）"""
    name: str
    description: str
    parameters: Dict[str, Any]
    returns: str
    
    def to_openai_format(self) -> Dict[str, Any]:
        """转换为 OpenAI Function Calling 格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": [
                        k for k, v in self.parameters.items()
                        if v.get("required", False)
                    ]
                }
            }
        }
    
    def to_anthropic_format(self) -> Dict[str, Any]:
        """转换为 Anthropic Tool Use 格式"""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": self.parameters,
                "required": [
                    k for k, v in self.parameters.items()
                    if v.get("required", False)
                ]
            }
        }


class BaseAgentTool(ABC):
    """
    智能体工具基类
    
    所有工具都需要继承此类并实现相应方法
    """
    
    name: str = "base_tool"
    description: str = "基础工具"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._initialize()
    
    def _initialize(self):
        """初始化钩子（子类可重写）"""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        执行工具
        
        Args:
            **kwargs: 工具参数
            
        Returns:
            ToolResult: 执行结果
        """
        pass
    
    def get_definition(self) -> ToolDefinition:
        """获取工具定义（供 LLM 使用）"""
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters=self._get_parameters(),
            returns=self._get_returns(),
        )
    
    def _get_parameters(self) -> Dict[str, Any]:
        """获取参数定义（子类可重写）"""
        return {}
    
    def _get_returns(self) -> str:
        """获取返回值描述"""
        return "执行结果"
    
    def _log(self, message: str, level: str = "info"):
        """日志记录"""
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] [{level.upper()}] [{self.name}] {message}")
```

### 3.2 爬虫工具实现

```python
# src/agents/tools/crawler_tools.py
from typing import List, Dict, Any, Optional
import asyncio

from src.agents.base_tool import BaseAgentTool, ToolResult
from src.crawler.taobao_crawler import TaobaoCrawler
from src.crawler.amazon_crawler import AmazonCrawler


class TaobaoCrawlerTool(BaseAgentTool):
    """
    淘宝商品爬取工具
    
    用法示例:
    ```
    请帮我采集这个淘宝商品：https://item.taobao.com/xxx.htm
    ```
    """
    
    name = "crawl_taobao"
    description = "从淘宝网站采集商品信息，包括标题、价格、图片、描述等"
    
    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "url": {
                "type": "string",
                "description": "淘宝商品 URL 地址",
            },
            "download_images": {
                "type": "boolean",
                "description": "是否下载商品图片",
                "default": True,
            },
            "max_images": {
                "type": "integer",
                "description": "最大下载图片数量",
                "default": 10,
            },
        }
    
    def _get_returns(self) -> str:
        return "包含商品信息的 JSON 对象，包括 title, price, images, description 等字段"
    
    async def execute(
        self,
        url: str,
        download_images: bool = True,
        max_images: int = 10,
    ) -> ToolResult:
        """执行爬取"""
        try:
            self._log(f"开始爬取淘宝商品：{url}")
            
            crawler = TaobaoCrawler(headless=True)
            product = await crawler.fetch_product(url)
            
            result_data = {
                "title": product.title,
                "price": product.price,
                "original_price": product.original_price,
                "sales": product.sales_count,
                "rating": product.rating,
                "images": product.images[:max_images] if download_images else [],
                "description": product.description[:500] + "..." if len(product.description) > 500 else product.description,
                "features": product.features,
                "specifications": product.specifications,
                "url": url,
            }
            
            await crawler.close()
            
            self._log(f"爬取成功：{product.title}")
            
            return ToolResult(
                success=True,
                data=result_data,
                message=f"成功采集商品：{product.title}",
                metadata={"product_id": product.product_id}
            )
            
        except Exception as e:
            self._log(f"爬取失败：{e}", level="error")
            return ToolResult(
                success=False,
                error=str(e),
                message="爬取失败，请检查 URL 是否正确"
            )


class AmazonCrawlerTool(BaseAgentTool):
    """
    亚马逊商品爬取工具
    """
    
    name = "crawl_amazon"
    description = "从亚马逊网站采集商品信息，包括 ASIN、价格、评论、排名等"
    
    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "url": {
                "type": "string",
                "description": "亚马逊商品 URL 地址或 ASIN",
            },
            "marketplace": {
                "type": "string",
                "description": "亚马逊站点：US/EU/JP/CN",
                "default": "US",
            },
            "include_reviews": {
                "type": "boolean",
                "description": "是否获取评论数据",
                "default": False,
            },
        }
    
    async def execute(
        self,
        url: str,
        marketplace: str = "US",
        include_reviews: bool = False,
    ) -> ToolResult:
        """执行爬取"""
        try:
            self._log(f"开始爬取亚马逊商品：{url}")
            
            # 实现亚马逊爬取逻辑
            # ...
            
            return ToolResult(
                success=True,
                data={"title": "商品标题", "price": "$99.99"},
                message="爬取成功"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                message="爬取失败"
            )


class MultiPlatformCrawlerTool(BaseAgentTool):
    """
    多平台智能爬取工具
    
    自动识别 URL 来源平台并调用相应爬虫
    """
    
    name = "crawl_smart"
    description = "智能识别电商平台 URL，自动调用对应的爬虫工具采集数据"
    
    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "url": {
                "type": "string",
                "description": "电商平台商品 URL",
            },
            "platform": {
                "type": "string",
                "description": "可选：指定平台（taobao/amazon/1688/aliexpress）",
                "enum": ["taobao", "amazon", "1688", "aliexpress", "auto"],
                "default": "auto",
            },
        }
    
    async def execute(
        self,
        url: str,
        platform: str = "auto",
    ) -> ToolResult:
        """智能爬取"""
        # 自动识别平台
        if platform == "auto":
            if "taobao.com" in url or "tb.cn" in url:
                platform = "taobao"
            elif "amazon.com" in url or "amazon." in url:
                platform = "amazon"
            elif "1688.com" in url:
                platform = "1688"
            elif "aliexpress.com" in url:
                platform = "aliexpress"
            else:
                return ToolResult(
                    success=False,
                    error="无法识别平台，请指定 platform 参数",
                )
        
        # 调用对应爬虫
        if platform == "taobao":
            tool = TaobaoCrawlerTool()
        elif platform == "amazon":
            tool = AmazonCrawlerTool()
        else:
            return ToolResult(
                success=False,
                error=f"暂不支持该平台：{platform}",
            )
        
        return await tool.execute(url=url)
```

### 3.3 AI 优化工具实现

```python
# src/agents/tools/optimizer_tools.py
from typing import List, Dict, Any
from src.agents.base_tool import BaseAgentTool, ToolResult
from src.optimizer.llm_client import LLMClient
from src.optimizer.keyword_optimizer import KeywordOptimizer
from src.optimizer.copywriter import Copywriter


class ProductOptimizerTool(BaseAgentTool):
    """
    商品 AI 优化工具
    
    用法示例:
    ```
    请优化这个商品信息，目标市场是美国，分类是家居用品
    ```
    """
    
    name = "optimize_product"
    description = "使用 AI 优化商品信息，生成符合亚马逊标准的标题、描述、关键词等"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.llm_client = LLMClient()
        self.keyword_optimizer = KeywordOptimizer()
        self.copywriter = Copywriter()
    
    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "product_data": {
                "type": "object",
                "description": "原始商品数据（JSON 对象）",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "features": {"type": "array", "items": {"type": "string"}},
                    "price": {"type": "string"},
                },
            },
            "target_market": {
                "type": "string",
                "description": "目标市场：US/EU/JP/CN",
                "default": "US",
            },
            "category": {
                "type": "string",
                "description": "商品分类",
            },
            "brand_name": {
                "type": "string",
                "description": "品牌名称",
            },
        }
    
    async def execute(
        self,
        product_data: Dict[str, Any],
        target_market: str = "US",
        category: str = "",
        brand_name: str = "",
    ) -> ToolResult:
        """执行优化"""
        try:
            self._log(f"开始优化商品：{product_data.get('title', 'N/A')[:50]}")
            
            # 调用 LLM 优化
            result = await self.llm_client.optimize_product(
                source_data=product_data,
                target_market=target_market,
                category=category,
            )
            
            if not result.success:
                return ToolResult(
                    success=False,
                    error=result.error_message,
                )
            
            # 提取关键词
            keywords = self.keyword_optimizer.extract_keywords(
                result.title + " " + result.description
            )
            
            optimized_data = {
                "title": result.title,
                "bullet_points": result.bullet_points,
                "description": result.description,
                "keywords": keywords[:20],
                "search_terms": result.search_terms,
            }
            
            self._log("优化完成")
            
            return ToolResult(
                success=True,
                data=optimized_data,
                message="商品优化完成",
                metadata={
                    "original_title": product_data.get("title", ""),
                    "optimized_title": result.title,
                }
            )
            
        except Exception as e:
            self._log(f"优化失败：{e}", level="error")
            return ToolResult(
                success=False,
                error=str(e),
                message="优化失败"
            )


class KeywordResearchTool(BaseAgentTool):
    """
    关键词研究工具
    """
    
    name = "research_keywords"
    description = "基于商品信息和目标市场，研究和生成 SEO 关键词"
    
    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "product_name": {
                "type": "string",
                "description": "商品名称",
            },
            "category": {
                "type": "string",
                "description": "商品分类",
            },
            "target_market": {
                "type": "string",
                "description": "目标市场",
                "default": "US",
            },
            "competitor_keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "竞品关键词（可选）",
            },
        }
    
    async def execute(
        self,
        product_name: str,
        category: str,
        target_market: str = "US",
        competitor_keywords: List[str] = None,
    ) -> ToolResult:
        """关键词研究"""
        try:
            optimizer = KeywordOptimizer()
            
            # 基础关键词提取
            core_keywords = optimizer.extract_keywords(product_name)
            
            # 生成长尾词
            long_tail = optimizer.generate_long_tail_keywords(
                core_keywords,
                category
            )
            
            # 验证和过滤
            valid_keywords = optimizer.validate_amazon_keywords(
                core_keywords + long_tail
            )
            
            return ToolResult(
                success=True,
                data={
                    "core_keywords": core_keywords[:10],
                    "long_tail_keywords": long_tail[:20],
                    "all_keywords": valid_keywords[:50],
                },
                message=f"生成 {len(valid_keywords)} 个有效关键词"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
            )
```

### 3.4 数据同步工具实现

```python
# src/agents/tools/sync_tools.py
from typing import Dict, Any, List, Optional
from src.agents.base_tool import BaseAgentTool, ToolResult
from src.feishu.bitable_client import FeishuBitableClient
from src.feishu.sync_service import DataSyncService
from src.models.feishu_models import ProductRecord, PlatformType


class FeishuSyncTool(BaseAgentTool):
    """
    飞书数据同步工具
    
    用法示例:
    ```
    请把采集的商品数据同步到飞书表格
    ```
    """
    
    name = "sync_to_feishu"
    description = "将商品数据同步到飞书多维表格，支持批量同步和增量更新"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.client: Optional[FeishuBitableClient] = None
        self.sync_service: Optional[DataSyncService] = None
    
    def _initialize(self):
        """初始化工具"""
        feishu_config = self.config.get("feishu", {})
        if feishu_config:
            self.client = FeishuBitableClient(
                app_id=feishu_config.get("app_id"),
                app_secret=feishu_config.get("app_secret"),
                app_token=feishu_config.get("app_token"),
            )
            self.sync_service = DataSyncService(
                client=self.client,
                table_config=feishu_config.get("tables", {}),
            )
    
    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "product_data": {
                "type": "object",
                "description": "商品数据（JSON 对象或数组）",
            },
            "table_name": {
                "type": "string",
                "description": "目标表名：products/reviews/tasks",
                "default": "products",
            },
            "batch_mode": {
                "type": "boolean",
                "description": "是否使用批量模式",
                "default": False,
            },
            "update_if_exists": {
                "type": "boolean",
                "description": "如果记录已存在是否更新",
                "default": True,
            },
        }
    
    async def execute(
        self,
        product_data: Dict[str, Any] | List[Dict[str, Any]],
        table_name: str = "products",
        batch_mode: bool = False,
        update_if_exists: bool = True,
    ) -> ToolResult:
        """执行同步"""
        if not self.sync_service:
            return ToolResult(
                success=False,
                error="飞书配置未初始化",
            )
        
        try:
            # 转换为数据模型
            if isinstance(product_data, list):
                products = [self._to_product_record(d) for d in product_data]
            else:
                products = [self._to_product_record(product_data)]
            
            self._log(f"准备同步 {len(products)} 个商品到飞书")
            
            if batch_mode:
                # 批量同步
                stats = await self.sync_service.sync_products_batch(products)
                message = f"批量同步完成：新增{stats['created']}, 更新{stats['updated']}, 失败{stats['failed']}"
            else:
                # 单条同步
                for product in products:
                    await self.sync_service.sync_product(
                        product,
                        update_if_exists=update_if_exists
                    )
                stats = self.sync_service.get_stats()
                message = f"同步完成：{stats}"
            
            return ToolResult(
                success=True,
                data=stats,
                message=message,
                metadata={"table_name": table_name}
            )
            
        except Exception as e:
            self._log(f"同步失败：{e}", level="error")
            return ToolResult(
                success=False,
                error=str(e),
                message="同步失败"
            )
    
    def _to_product_record(self, data: Dict[str, Any]) -> ProductRecord:
        """转换为商品记录"""
        return ProductRecord(
            product_name=data.get("title", "") or data.get("product_name", ""),
            product_id=data.get("asin", "") or data.get("product_id", ""),
            platform=PlatformType(data.get("platform", "淘宝")),
            source_url=data.get("url", ""),
            price=float(data.get("price", 0)),
            original_price=data.get("original_price"),
            currency=data.get("currency", "CNY"),
            sales_count=data.get("sales_count"),
            rating=data.get("rating"),
            review_count=data.get("review_count"),
            brand=data.get("brand"),
            shop_name=data.get("shop_name"),
            category=data.get("category"),
            main_image_url=data.get("main_image"),
            image_urls=data.get("images", []),
            description=data.get("description"),
            features=data.get("features", []),
            keywords=data.get("keywords", []),
        )


class AmazonUploadTool(BaseAgentTool):
    """
    亚马逊上传工具
    """
    
    name = "upload_to_amazon"
    description = "将审核通过的商品数据上传到亚马逊卖家后台"
    
    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "product_data": {
                "type": "object",
                "description": "审核通过的商品数据",
            },
            "marketplace": {
                "type": "string",
                "description": "目标站点：US/EU/JP",
                "default": "US",
            },
            "auto_submit": {
                "type": "boolean",
                "description": "是否自动提交审核",
                "default": False,
            },
        }
    
    async def execute(
        self,
        product_data: Dict[str, Any],
        marketplace: str = "US",
        auto_submit: bool = False,
    ) -> ToolResult:
        """执行上传"""
        try:
            self._log(f"准备上传商品到亚马逊 {marketplace}")
            
            # 实现亚马逊上传逻辑
            # ...
            
            return ToolResult(
                success=True,
                data={"upload_id": "xxx", "status": "pending"},
                message="上传成功，等待亚马逊审核"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
            )
```

### 3.5 审核工具实现

```python
# src/agents/tools/review_tools.py
from typing import Dict, Any, Optional
from src.agents.base_tool import BaseAgentTool, ToolResult
from src.reviewer.review_manager import ReviewManager, ReviewStatus


class ReviewApproveTool(BaseAgentTool):
    """
    审核通过工具
    """
    
    name = "review_approve"
    description = "审核通过商品数据，标记为可上传状态"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.review_manager = ReviewManager()
    
    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "product_id": {
                "type": "string",
                "description": "商品 ID 或审核单号",
            },
            "final_title": {
                "type": "string",
                "description": "最终确认的标题（可选修改）",
            },
            "final_description": {
                "type": "string",
                "description": "最终确认的描述（可选修改）",
            },
            "comments": {
                "type": "string",
                "description": "审核备注",
            },
        }
    
    async def execute(
        self,
        product_id: str,
        final_title: Optional[str] = None,
        final_description: Optional[str] = None,
        comments: str = "",
    ) -> ToolResult:
        """执行审核通过"""
        try:
            # 查找审核记录
            reviews = [r for r in self.review_manager.reviews if r.product_id == product_id]
            
            if not reviews:
                return ToolResult(
                    success=False,
                    error=f"未找到商品 {product_id} 的审核记录",
                )
            
            review = reviews[0]
            
            # 更新审核状态
            reviewed_data = review.optimized_data.copy()
            if final_title:
                reviewed_data["title"] = final_title
            if final_description:
                reviewed_data["description"] = final_description
            
            self.review_manager.update_review(
                product_id=product_id,
                reviewed_data=reviewed_data,
                status=ReviewStatus.APPROVED,
                reviewer_notes=comments,
                reviewer="AI Agent",
            )
            
            self._log(f"审核通过：{product_id}")
            
            return ToolResult(
                success=True,
                message=f"商品 {product_id} 已审核通过",
                metadata={"status": "approved"}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
            )


class ReviewQueryTool(BaseAgentTool):
    """
    审核查询工具
    """
    
    name = "review_query"
    description = "查询审核状态和待审核商品列表"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.review_manager = ReviewManager()
    
    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "status": {
                "type": "string",
                "description": "审核状态：pending/approved/rejected",
                "enum": ["pending", "approved", "rejected", "all"],
                "default": "pending",
            },
            "limit": {
                "type": "integer",
                "description": "返回数量限制",
                "default": 10,
            },
        }
    
    async def execute(
        self,
        status: str = "pending",
        limit: int = 10,
    ) -> ToolResult:
        """查询审核状态"""
        try:
            if status == "all":
                reviews = self.review_manager.reviews[:limit]
            elif status == "pending":
                reviews = self.review_manager.get_pending_reviews()[:limit]
            elif status == "approved":
                reviews = self.review_manager.get_approved_products()[:limit]
            else:
                reviews = []
            
            result_data = [
                {
                    "product_id": r.product_id,
                    "title": r.source_data.get("title", "")[:50],
                    "status": r.status.value,
                    "created_at": r.created_at,
                }
                for r in reviews
            ]
            
            return ToolResult(
                success=True,
                data=result_data,
                message=f"查询到 {len(result_data)} 条记录"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
            )
```

---

## 4. 企业提效场景

### 4.1 场景一：智能商品采集工作流

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      场景一：智能商品采集工作流                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  用户指令（飞书/微信/Web）:                                                  │
│  "帮我采集这 10 个淘宝爆款商品，优化后同步到飞书表格"                          │
│                                                                             │
│  ▼                                                                          │
│                                                                             │
│  AI 智能体自动执行:                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. 解析指令，提取 URL 列表                                            │   │
│  │ 2. 调用 crawl_taobao 工具批量爬取                                    │   │
│  │ 3. 调用 optimize_product 工具 AI 优化每个商品                           │   │
│  │ 4. 调用 sync_to_feishu 工具同步到飞书                                 │   │
│  │ 5. 发送完成通知到飞书群聊                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  预期效果:                                                                  │
│  - 人工操作：10 个商品 × 15 分钟 = 150 分钟                                    │
│  - AI 智能体：10 个商品 × 2 分钟 = 20 分钟（无人值守）                          │
│  - 效率提升：87%                                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 场景二：竞品监控与定价建议

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      场景二：竞品监控与定价建议                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  定时任务（每天上午 9 点）:                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. 自动爬取竞品价格和销量数据                                         │   │
│  │ 2. 分析价格趋势和市场份额变化                                         │   │
│  │ 3. 生成定价建议和促销策略                                             │   │
│  │ 4. 将分析报告发送到飞书管理群                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  飞书消息示例:                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 📊 竞品监控日报 - 2024-01-15                                        │   │
│  │                                                                      │   │
│  │ 🔴 价格预警：竞品 A 降价 15%，建议关注                                 │   │
│  │ 🟡 销量变化：竞品 B 销量上升 30%                                      │   │
│  │ 🟢 机会发现：细分关键词搜索量增长 50%                                 │   │
│  │                                                                      │   │
│  │ 💡 建议行动:                                                         │   │
│  │ 1. 调整 SKU-12345 价格至 $29.99                                      │   │
│  │ 2. 增加关键词"XXX"的广告投放                                         │   │
│  │ 3. 联系供应链确认库存                                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 场景三：智能审核工作流

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      场景三：智能审核工作流                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  审核流程:                                                                  │
│                                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌───────────┐ │
│  │  AI 初审    │────►│  人工复审   │────►│  确认修改   │────►│  自动上传 │ │
│  └─────────────┘     └─────────────┘     └─────────────┘     └───────────┘ │
│       │                   │                   │                  │          │
│       ▼                   ▼                   ▼                  ▼          │
│  自动检查：          飞书审核界面：      一键修改：        亚马逊后台：      │
│  - 违禁词检测        - 显示 AI 优化结果     - 标题调整        - 生成上传模板   │
│  - 格式合规性        - 人工确认/修改      - 描述润色        - 自动填写表单   │
│  - 图片质量          - 批量审批          - 关键词优化      - 提交审核      │
│  - 完整性检查        - 评论和批注        - 快速驳回        - 跟踪状态      │
│                                                                             │
│  审核效率对比:                                                              │
│  - 传统人工审核：5 分钟/商品                                                  │
│  - AI 辅助审核：1 分钟/商品（人工只需确认）                                   │
│  - 效率提升：80%                                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.4 场景四：自然语言数据查询

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      场景四：自然语言数据查询                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  用户提问（飞书机器人）:                                                      │
│                                                                             │
│  "上个月哪些商品销量最好？"                                                   │
│  "帮我找出价格低于$20 且评分高于 4.5 的商品"                                  │
│  "对比一下淘宝和亚马逊的同款商品价格"                                         │
│                                                                             │
│  ▼                                                                          │
│                                                                             │
│  AI 智能体处理:                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. 理解自然语言查询意图                                              │   │
│  │ 2. 转换为数据库查询或飞书 API 调用                                     │   │
│  │ 3. 执行查询并分析结果                                                │   │
│  │ 4. 生成可视化图表和文字总结                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  回复示例:                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 📈 上月销量 TOP5 商品（2024-01）                                      │   │
│  │                                                                      │   │
│  │ 1. Owala 水瓶 - 1,234 件 - $29.99 - ⭐4.7                            │   │
│  │ 2. 瑜伽垫 - 987 件 - $24.99 - ⭐4.5                                   │   │
│  │ 3. 保温杯 - 856 件 - $19.99 - ⭐4.6                                   │   │
│  │ ...                                                                  │   │
│  │                                                                      │   │
│  │ [查看完整报表] [导出 Excel] [设置监控]                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.5 场景五：多智能体协作

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      场景五：多智能体协作（AutoGen 模式）                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  用户指令: "开发一个新的商品上架流程，从采集到上传全自动"                      │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                        智能体协作流程                                   │ │
│  │                                                                       │ │
│  │  ┌─────────────┐                                                     │ │
│  │  │  管理员智能体 │  (协调和决策)                                       │ │
│  │  │  Admin Agent │                                                     │ │
│  │  └──────┬──────┘                                                     │ │
│  │         │ 分配任务                                                     │ │
│  │         ▼                                                            │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │ │
│  │  │                     执行智能体组                                  │ │ │
│  │  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────────┐ │ │ │
│  │  │  │ 采集智能体 │  │ 优化智能体 │  │ 审核智能体 │  │ 上传智能体    │ │ │ │
│  │  │  │ Crawler   │  │ Optimizer │  │ Reviewer  │  │ Uploader      │ │ │ │
│  │  │  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └───────┬───────┘ │ │ │
│  │  │        │              │              │                │         │ │ │
│  │  │        └──────────────┴──────────────┴────────────────┘         │ │ │
│  │  │                            │                                      │ │ │
│  │  │                            ▼                                      │ │ │
│  │  │                    共享数据总线                                    │ │ │
│  │  │                    (飞书多维表格)                                  │ │ │
│  │  └─────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                       │ │
│  │  协作过程:                                                            │ │
│  │  1. 管理员智能体分解任务为 4 个子任务                                    │ │
│  │  2. 各智能体并行执行各自任务                                          │ │
│  │  3. 通过共享数据总线交换信息                                          │ │
│  │  4. 管理员智能体汇总结果并报告用户                                    │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. 核心模块实现

### 5.1 智能体编排器

```python
# src/agents/orchestrator.py
from typing import Dict, Any, List, Optional
import asyncio
import json
from dataclasses import dataclass

from src.agents.base_tool import BaseAgentTool, ToolResult
from src.agents.tools.crawler_tools import (
    TaobaoCrawlerTool,
    AmazonCrawlerTool,
    MultiPlatformCrawlerTool,
)
from src.agents.tools.optimizer_tools import (
    ProductOptimizerTool,
    KeywordResearchTool,
)
from src.agents.tools.sync_tools import (
    FeishuSyncTool,
    AmazonUploadTool,
)
from src.agents.tools.review_tools import (
    ReviewApproveTool,
    ReviewQueryTool,
)


@dataclass
class TaskContext:
    """任务上下文"""
    task_id: str
    user_instruction: str
    parameters: Dict[str, Any]
    results: List[ToolResult]
    status: str = "pending"  # pending/running/completed/failed
    error: Optional[str] = None


class AgentOrchestrator:
    """
    智能体编排器
    
    负责:
    - 工具注册和管理
    - 任务解析和执行
    - 多步骤工作流编排
    - 错误处理和重试
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.tools: Dict[str, BaseAgentTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """注册默认工具"""
        # 爬虫工具
        self.register_tool("crawl_taobao", TaobaoCrawlerTool())
        self.register_tool("crawl_amazon", AmazonCrawlerTool())
        self.register_tool("crawl_smart", MultiPlatformCrawlerTool())
        
        # 优化工具
        self.register_tool("optimize_product", ProductOptimizerTool(self.config))
        self.register_tool("research_keywords", KeywordResearchTool())
        
        # 同步工具
        self.register_tool("sync_to_feishu", FeishuSyncTool(self.config))
        self.register_tool("upload_to_amazon", AmazonUploadTool())
        
        # 审核工具
        self.register_tool("review_approve", ReviewApproveTool())
        self.register_tool("review_query", ReviewQueryTool())
    
    def register_tool(self, name: str, tool: BaseAgentTool):
        """注册工具"""
        self.tools[name] = tool
        print(f"已注册工具：{name}")
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """获取所有工具定义（供 LLM 使用）"""
        return [
            tool.get_definition().to_anthropic_format()
            for tool in self.tools.values()
        ]
    
    async def execute_task(
        self,
        instruction: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> TaskContext:
        """
        执行任务
        
        Args:
            instruction: 用户指令
            parameters: 参数
            
        Returns:
            TaskContext: 任务上下文
        """
        import uuid
        
        context = TaskContext(
            task_id=str(uuid.uuid4()),
            user_instruction=instruction,
            parameters=parameters or {},
            results=[],
        )
        
        try:
            context.status = "running"
            
            # 解析指令，确定要调用的工具
            # 这里可以使用 LLM 来解析，也可以基于规则
            tool_calls = await self._parse_instruction(instruction, parameters)
            
            # 执行工具调用
            for tool_call in tool_calls:
                tool_name = tool_call["tool"]
                tool_params = tool_call.get("parameters", {})
                
                if tool_name not in self.tools:
                    raise ValueError(f"未知工具：{tool_name}")
                
                tool = self.tools[tool_name]
                result = await tool.execute(**tool_params)
                context.results.append(result)
                
                if not result.success:
                    context.error = result.error
                    context.status = "failed"
                    break
            
            if context.status != "failed":
                context.status = "completed"
            
        except Exception as e:
            context.status = "failed"
            context.error = str(e)
        
        return context
    
    async def _parse_instruction(
        self,
        instruction: str,
        parameters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        解析指令，生成工具调用序列
        
        实际实现中应该调用 LLM 来解析
        这里使用简单的规则匹配作为示例
        """
        tool_calls = []
        
        # 规则匹配示例
        instruction_lower = instruction.lower()
        
        if "采集" in instruction or "爬取" in instruction:
            if "taobao" in instruction_lower or "淘宝" in instruction:
                tool_calls.append({
                    "tool": "crawl_taobao",
                    "parameters": {"url": parameters.get("url")},
                })
            elif "amazon" in instruction_lower or "亚马逊" in instruction:
                tool_calls.append({
                    "tool": "crawl_amazon",
                    "parameters": {"url": parameters.get("url")},
                })
            else:
                tool_calls.append({
                    "tool": "crawl_smart",
                    "parameters": {"url": parameters.get("url")},
                })
        
        if "优化" in instruction:
            tool_calls.append({
                "tool": "optimize_product",
                "parameters": {
                    "product_data": parameters.get("product_data"),
                    "target_market": parameters.get("target_market", "US"),
                },
            })
        
        if "同步" in instruction or "飞书" in instruction:
            tool_calls.append({
                "tool": "sync_to_feishu",
                "parameters": {
                    "product_data": parameters.get("product_data"),
                    "batch_mode": True,
                },
            })
        
        if "上传" in instruction:
            tool_calls.append({
                "tool": "upload_to_amazon",
                "parameters": parameters,
            })
        
        return tool_calls
    
    async def run_workflow(
        self,
        workflow_name: str,
        input_data: Dict[str, Any],
    ) -> List[ToolResult]:
        """
        运行预定义工作流
        
        Args:
            workflow_name: 工作流名称
            input_data: 输入数据
            
        Returns:
            工具执行结果列表
        """
        workflows = {
            "full_pipeline": self._workflow_full_pipeline,
            "batch_crawl": self._workflow_batch_crawl,
            "smart_sync": self._workflow_smart_sync,
        }
        
        if workflow_name not in workflows:
            raise ValueError(f"未知工作流：{workflow_name}")
        
        return await workflows[workflow_name](input_data)
    
    async def _workflow_full_pipeline(
        self,
        input_data: Dict[str, Any],
    ) -> List[ToolResult]:
        """
        完整工作流：采集 → 优化 → 同步 → 上传
        """
        results = []
        
        # 1. 采集
        crawl_tool = self.tools.get("crawl_smart")
        if crawl_tool:
            result = await crawl_tool.execute(url=input_data.get("url"))
            results.append(result)
            if result.success:
                input_data["product_data"] = result.data
        
        # 2. 优化
        optimize_tool = self.tools.get("optimize_product")
        if optimize_tool and input_data.get("product_data"):
            result = await optimize_tool.execute(
                product_data=input_data["product_data"],
                target_market=input_data.get("target_market", "US"),
            )
            results.append(result)
            if result.success:
                input_data["product_data"] = result.data
        
        # 3. 同步
        sync_tool = self.tools.get("sync_to_feishu")
        if sync_tool and input_data.get("product_data"):
            result = await sync_tool.execute(
                product_data=input_data["product_data"],
                batch_mode=True,
            )
            results.append(result)
        
        return results
    
    async def _workflow_batch_crawl(
        self,
        input_data: Dict[str, Any],
    ) -> List[ToolResult]:
        """批量爬取工作流"""
        # 实现批量爬取逻辑
        pass
    
    async def _workflow_smart_sync(
        self,
        input_data: Dict[str, Any],
    ) -> List[ToolResult]:
        """智能同步工作流"""
        # 实现智能同步逻辑
        pass
```

### 5.2 LLM 集成模块

```python
# src/agents/llm_integration.py
from typing import Dict, Any, List, Optional, Callable
import json
from anthropic import AsyncAnthropic


class LLMIntegration:
    """
    LLM 集成模块
    
    支持:
    - Claude (Anthropic)
    - GPT-4 (OpenAI)
    - 本地模型
    """
    
    def __init__(
        self,
        provider: str = "anthropic",
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
    ):
        self.provider = provider
        self.model = model
        
        if provider == "anthropic":
            self.client = AsyncAnthropic(api_key=api_key)
        elif provider == "openai":
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=api_key)
        else:
            raise ValueError(f"不支持的提供商：{provider}")
    
    async def chat_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        system_prompt: str = "",
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """
        与 LLM 对话，支持工具调用
        
        Args:
            messages: 对话历史
            tools: 工具定义列表
            system_prompt: 系统提示词
            max_tokens: 最大 token 数
            
        Returns:
            LLM 响应
        """
        if self.provider == "anthropic":
            return await self._chat_anthropic(
                messages=messages,
                tools=tools,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
            )
        elif self.provider == "openai":
            return await self._chat_openai(
                messages=messages,
                tools=tools,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
            )
    
    async def _chat_anthropic(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        system_prompt: str,
        max_tokens: int,
    ) -> Dict[str, Any]:
        """Claude API 调用"""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            tools=tools,
            messages=messages,
        )
        
        # 处理响应
        content = response.content
        
        # 检查是否有工具调用
        for block in content:
            if block.type == "tool_use":
                return {
                    "type": "tool_call",
                    "tool_name": block.name,
                    "tool_input": block.input,
                    "tool_call_id": block.id,
                }
        
        # 普通文本响应
        text_content = "\n".join(
            block.text for block in content if hasattr(block, "text")
        )
        
        return {
            "type": "text",
            "content": text_content,
        }
    
    async def _chat_openai(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        system_prompt: str,
        max_tokens: int,
    ) -> Dict[str, Any]:
        """OpenAI API 调用"""
        # 添加系统消息
        all_messages = [{"role": "system", "content": system_prompt}] + messages
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=all_messages,
            tools=tools,
            max_tokens=max_tokens,
        )
        
        choice = response.choices[0]
        message = choice.message
        
        # 检查是否有工具调用
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            return {
                "type": "tool_call",
                "tool_name": tool_call.function.name,
                "tool_input": json.loads(tool_call.function.arguments),
                "tool_call_id": tool_call.id,
            }
        
        return {
            "type": "text",
            "content": message.content,
        }
    
    async def execute_tool_and_continue(
        self,
        initial_response: Dict[str, Any],
        tool_executor: Callable,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
    ) -> str:
        """
        执行工具调用并继续对话
        
        Args:
            initial_response: LLM 初始响应
            tool_executor: 工具执行函数
            messages: 对话历史
            tools: 工具定义
            
        Returns:
            最终响应文本
        """
        if initial_response["type"] != "tool_call":
            return initial_response.get("content", "")
        
        # 执行工具
        tool_result = await tool_executor(
            initial_response["tool_name"],
            initial_response["tool_input"],
        )
        
        # 添加工具结果到对话
        messages.append({
            "role": "assistant",
            "content": [
                {
                    "type": "tool_use",
                    "id": initial_response["tool_call_id"],
                    "name": initial_response["tool_name"],
                    "input": initial_response["tool_input"],
                }
            ],
        })
        
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": initial_response["tool_call_id"],
                    "content": json.dumps(tool_result.to_dict()),
                }
            ],
        })
        
        # 继续对话
        next_response = await self.chat_with_tools(
            messages=messages,
            tools=tools,
        )
        
        return next_response.get("content", "")
```

### 5.3 飞书机器人集成

```python
# src/agents/feishu_bot.py
import asyncio
import logging
from typing import Dict, Any, Optional
from aiohttp import web
import json

from src.agents.orchestrator import AgentOrchestrator
from src.feishu.bot_notifier import FeishuBotNotifier


logger = logging.getLogger(__name__)


class FeishuAgentBot:
    """
    飞书智能体机器人
    
    将 AI 智能体能力通过飞书机器人暴露给用户
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        orchestrator: AgentOrchestrator,
    ):
        self.config = config
        self.orchestrator = orchestrator
        self.notifier = FeishuBotNotifier(config.get("webhook_url"))
        
        self.app = web.Application()
        self.app.router.add_post("/webhook", self.handle_webhook)
    
    async def handle_webhook(self, request: web.Request) -> web.Response:
        """处理飞书 Webhook 请求"""
        try:
            data = await request.json()
            
            # 解析飞书消息
            message_type = data.get("msg_type")
            content = json.loads(data.get("content", "{}"))
            text = content.get("text", "")
            
            # 提取用户 ID 和会话信息
            user_id = data.get("sender_id", {}).get("user_id", "")
            conversation_id = data.get("chat_id", "")
            
            logger.info(f"收到飞书消息：{text[:100]} from user {user_id}")
            
            # 调用智能体处理
            response_text = await self.process_message(text, user_id)
            
            # 回复消息
            await self.notifier.send_text_message(
                content=response_text,
                mention_users=[user_id] if user_id else None,
            )
            
            return web.json_response({"status": "ok"})
            
        except Exception as e:
            logger.error(f"处理飞书消息失败：{e}", exc_info=True)
            return web.json_response({"status": "error", "message": str(e)})
    
    async def process_message(
        self,
        message: str,
        user_id: str,
    ) -> str:
        """
        处理用户消息
        
        Args:
            message: 用户消息
            user_id: 用户 ID
            
        Returns:
            回复文本
        """
        try:
            # 调用智能体编排器
            context = await self.orchestrator.execute_task(
                instruction=message,
                parameters={"user_id": user_id},
            )
            
            # 生成回复
            if context.status == "completed":
                return self._format_success_response(context)
            elif context.status == "failed":
                return self._format_error_response(context)
            else:
                return f"任务状态：{context.status}"
                
        except Exception as e:
            return f"处理失败：{e}"
    
    def _format_success_response(self, context) -> str:
        """格式化成功响应"""
        lines = ["✅ 任务完成"]
        lines.append("")
        
        for i, result in enumerate(context.results, 1):
            lines.append(f"{i}. {result.message}")
            if result.data:
                if isinstance(result.data, dict):
                    stats = result.data
                    if "created" in stats:
                        lines.append(
                            f"   新增：{stats.get('created', 0)}, "
                            f"更新：{stats.get('updated', 0)}"
                        )
        
        return "\n".join(lines)
    
    def _format_error_response(self, context) -> str:
        """格式化错误响应"""
        return f"❌ 任务失败\n\n错误信息：{context.error}"
    
    async def run(self, host: str = "0.0.0.0", port: int = 8080):
        """启动机器人服务"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        logger.info(f"飞书机器人服务已启动：http://{host}:{port}")
        
        # 保持运行
        while True:
            await asyncio.sleep(3600)
```

---

## 6. 部署与配置

### 6.1 完整配置文件

```yaml
# config/agent_config.yaml
# AI 智能体配置

# LLM 配置
llm:
  provider: anthropic  # anthropic / openai
  api_key_env: ANTHROPIC_API_KEY
  model: claude-sonnet-4-20250514
  max_tokens: 4096

# 飞书配置
feishu:
  app_id: "cli_xxxxxxxxxxxxx"
  app_secret: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  app_token: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  tables:
    products: "tblxxxxxxxxxxxxxx"
    reviews: "tblyyyyyyyyyyyy"
    tasks: "tblzzzzzzzzzzzzzz"
  bot:
    webhook_url: "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx"
    verification_token: "xxxxxxxxxx"

# 亚马逊配置
amazon:
  seller_email: "your_seller_email"
  seller_password: "your_password"
  marketplace: "US"

# 代理配置（可选）
proxy:
  enabled: false
  server: "http://proxy-server:port"
  username: "username"
  password: "password"

# 工具配置
tools:
  crawler:
    headless: true
    timeout: 30000
    max_retries: 3
  optimizer:
    auto_approve: false  # 是否自动审核通过
    min_confidence: 0.8  # 最小置信度
  sync:
    batch_size: 100
    retry_on_failure: true

# 日志配置
logging:
  level: INFO
  file: logs/agent.log
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### 6.2 Docker 部署

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# 安装 Playwright
RUN pip install playwright
RUN playwright install chromium
RUN playwright install-deps chromium

# 复制项目文件
COPY pyproject.toml .
COPY src/ ./src/
COPY config/ ./config/

# 安装 Python 依赖
RUN pip install uv
RUN uv sync --frozen

# 设置环境变量
ENV PYTHONPATH=/app
ENV HEADLESS=true

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["uv", "run", "python", "-m", "src.agents.feishu_bot"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  agent-bot:
    build: .
    ports:
      - "8080:8080"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - FEISHU_APP_ID=${FEISHU_APP_ID}
      - FEISHU_APP_SECRET=${FEISHU_APP_SECRET}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
  
  # 可选：Redis 用于缓存和队列
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
  
  # 可选：PostgreSQL 用于持久化
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: agent_db
      POSTGRES_USER: agent
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  redis_data:
  postgres_data:
```

### 6.3 快速启动

```bash
# 1. 克隆项目
git clone <repository>
cd python_crawler

# 2. 安装依赖
uv sync

# 3. 配置环境变量
cp .env.example .env
vim .env  # 填入 API Key 和配置

# 4. 安装浏览器
uv run playwright install chromium

# 5. 测试智能体
uv run python -m src.agents.test_agent \
  --instruction "采集这个商品：https://item.taobao.com/xxx.htm"

# 6. 启动飞书机器人
uv run python -m src.agents.feishu_bot

# 7. 或使用 Docker
docker-compose up -d
```

---

## 附录：企业提效指标

### 预期效果

| 指标 | 传统方式 | AI 智能体增强 | 提升幅度 |
|------|----------|---------------|----------|
| 商品采集效率 | 15 分钟/个 | 2 分钟/个 | 87% |
| 文案撰写时间 | 30 分钟/个 | 5 分钟/个 | 83% |
| 审核通过率 | 60% | 85%（AI 预审） | 42% |
| 数据同步延迟 | 1-2 天 | 实时 | 99% |
| 人力成本 | 5 人/天 | 1 人/天 | 80% |

### ROI 分析

```
假设场景：中型电商公司，每日处理 50 个商品

传统方式:
- 采集：50 × 15 分钟 = 750 分钟 = 12.5 小时
- 优化：50 × 30 分钟 = 1500 分钟 = 25 小时
- 审核：50 × 5 分钟 = 250 分钟 = 4.2 小时
- 同步：50 × 2 分钟 = 100 分钟 = 1.7 小时
- 总计：43.4 小时/天 ≈ 5.4 人/天

AI 智能体增强:
- 采集：50 × 2 分钟 = 100 分钟 = 1.7 小时
- 优化：50 × 5 分钟 = 250 分钟 = 4.2 小时
- 审核：50 × 1 分钟 = 50 分钟 = 0.8 小时
- 同步：自动完成 = 0.5 小时
- 总计：7.2 小时/天 ≈ 0.9 人/天

年度节省：(5.4 - 0.9) × 250 天 × 人力成本
假设人力成本 500 元/天，年度节省：4.5 × 250 × 500 = 562,500 元
```

---

*文档版本：0.1.0 | 最后更新：2026-03-12*
