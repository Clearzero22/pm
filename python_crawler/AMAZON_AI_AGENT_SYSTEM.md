# 电商AI智能体系统 - 完整技术方案

> 基于AI智能体的亚马逊电商运营自动化解决方案

---

## 目录

1. [系统整体架构](#1-系统整体架构)
2. [SOP 1: 市场调研智能体详解](#2-sop-1-市场调研智能体详解)
3. [SOP 2: 关键词挖掘智能体详解](#3-sop-2-关键词挖掘智能体详解)
4. [SOP 3: Listing优化智能体详解](#4-sop-3-listing优化智能体详解)
5. [技术栈与部署方案](#5-技术栈与部署方案)
6. [成本与ROI分析](#6-成本与roi分析)

---

## 1. 系统整体架构

### 1.1 分层架构设计

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              用户交互层                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Web Dashboard│  │ Slack Bot    │  │ API Gateway  │  │ 定时任务     │ │
│  │ (Streamlit)  │  │ 通知         │  │ REST/GraphQL │  │ (Celery Beat)│ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────┼─────────────────────────────────────┐
│                               业务编排层                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    Agent Orchestrator (编排器)                        │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │  │
│  │  │ Task Dispatcher │→│ State Manager   │→│ Result Aggregator│       │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘       │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────┼─────────────────────────────────────┘
                                      │
┌─────────────────────────────────────┼─────────────────────────────────────┐
│                               智能体层                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐         │
│  │ Market Research  │  │  Keyword Miner   │  │  Listing         │         │
│  │      Agent       │  │      Agent       │  │  Optimizer       │         │
│  │  ┌────────────┐  │  │  ┌────────────┐  │  │  ┌────────────┐  │         │
│  │  │Data Collector│  │  │  Keyword    │  │  │  Copywriter │  │         │
│  │  │Competitor   │  │  │  Expander   │  │  │  Sub-agent  │  │         │
│  │  │Analyzer     │  │  │  Filter     │  │  │  Image      │  │         │
│  │  └────────────┘  │  │  Scorer     │  │  │  Generator  │  │         │
│  └──────────────────┘  │  └────────────┘  │  │  QA Checker │  │         │
│                        └──────────────────┘  │  └────────────┘  │         │
│                                             └──────────────────┘         │
└───────────────────────────────────────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────┼─────────────────────────────────────┐
│                               工具与数据层                                    │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │Jungle   │ │卖家精灵 │ │Amazon   │ │Google   │ │OpenAI   │ │Claude   │  │
│  │Scout API│ │  API    │ │Scrape   │ │Trends   │ │  API    │ │  API    │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
└───────────────────────────────────────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────┼─────────────────────────────────────┐
│                               数据持久层                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │   PostgreSQL    │  │    Redis        │  │    Qdrant       │             │
│  │  (结构化数据)    │  │   (缓存/队列)    │  │  (向量数据库)    │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
└───────────────────────────────────────────────────────────────────────────┘
```

### 1.2 核心组件说明

```yaml
# 智能体编排器
Agent Orchestrator:
  职责:
    - 任务分解与分发
    - 智能体间协调
    - 状态管理与容错
    - 结果聚合与输出

  技术选型:
    - LangChain Agents / CrewAI
    - Redis作为消息队列
    - PostgreSQL存储工作流状态

# 数据收集器
Data Collector:
  职责:
    - 统一封装第三方API
    - 处理反爬与限流
    - 数据清洗与标准化
    - 本地缓存策略

  技术选型:
    - httpx (异步HTTP)
    - Playwright (动态渲染)
    - rate-limiter (限流)
```

---

## 2. SOP 1: 市场调研智能体详解

### 2.1 智能体内部架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     MarketResearchAgent                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐      ┌─────────────────┐                   │
│  │  Input Handler  │─────▶│ Task Scheduler  │                   │
│  │  输入处理器       │      │  任务调度器       │                   │
│  └─────────────────┘      └────────┬────────┘                   │
│                                    │                             │
│           ┌────────────────────────┼────────────────────────┐   │
│           │                        │                        │   │
│   ┌───────▼────────┐     ┌─────────▼────────┐    ┌────────▼─────┐  │
│   │Competitor      │     │   Market         │    │  Trend       │  │
│   │Scanner         │     │   Analyzer       │    │  Analyzer    │  │
│   │竞品扫描器       │     │   市场分析器       │    │  趋势分析器   │  │
│   ├───────────────┤     ├─────────────────┤    ├─────────────┤  │
│   │• Jungle Scout │     │• 价格分布分析    │    │• Google      │  │
│   │• Amazon BSR   │     │• 评分集中度     │    │  Trends      │  │
│   │• Keepa API    │     │• 销量估算       │    │• 季节性波动  │  │
│   │• 爬虫补充      │     │• 品牌占有率     │    │• 上升关键词  │  │
│   └───────┬────────┘     └────────┬────────┘    └──────┬───────┘  │
│           │                       │                     │          │
│           └───────────────────────┼─────────────────────┘          │
│                                   │                                │
│                          ┌────────▼────────┐                       │
│                          │  AI Analyst     │                       │
│                          │  AI分析引擎      │                       │
│                          ├─────────────────┤                       │
│                          │• 评论情感分析    │                       │
│                          │• 卖点提取       │                       │
│                          │• 痛点聚类       │                       │
│                          │• 差异化建议     │                       │
│                          └────────┬────────┘                       │
│                                   │                                │
│                          ┌────────▼────────┐                       │
│                          │ Report Builder  │                       │
│                          │  报告生成器      │                       │
│                          ├─────────────────┤                       │
│                          │• Excel导出      │                       │
│                          │• PDF报告        │                       │
│                          │• 可视化图表     │                       │
│                          └─────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 详细工作流程

```python
# 伪代码展示完整流程

class MarketResearchAgent:
    """
    市场调研智能体
    """

    async def execute(self, product_keyword: str, market: str):
        """
        执行市场调研任务
        """
        # ========== 阶段1: 竞品数据采集 ==========
        competitors = await self._scan_competitors(product_keyword, market)

        # ========== 阶段2: 深度数据挖掘 ==========
        enriched_data = []
        for competitor in competitors[:50]:  # 取Top 50
            data = {
                "基础信息": await self._get_basic_info(competitor),
                "价格历史": await self._get_price_history(competitor),
                "评论数据": await self._scrape_reviews(competitor, limit=500),
                "QA数据": await self._scrape_qa(competitor),
                "图片分析": await self._analyze_images(competitor),
            }
            enriched_data.append(data)

        # ========== 阶段3: AI智能分析 ==========
        analysis_results = await self._ai_analyze(enriched_data)

        # ========== 阶段4: 报告生成 ==========
        report = self._generate_report(analysis_results)

        return report

    async def _scan_competitors(self, keyword: str, market: str):
        """
        多源竞品扫描
        """
        sources = {
            "jungle_scout": self._js_search,
            "amazon_bsr": self._bsr_search,
            "amazon_search": self._organic_search,
            "ad_spies": self._ad_search,
        }

        all_results = []
        for source_name, search_func in sources.items():
            results = await search_func(keyword, market)
            all_results.extend(results)

        # 去重并排序
        unique_products = self._deduplicate(all_results)
        return sorted(unique_products, key=lambda x: x['sales_rank'])

    async def _ai_analyze(self, products: List[Dict]):
        """
        AI分析引擎
        """
        results = {
            "卖点分析": await self._extract_selling_points(products),
            "痛点分析": await self._extract_pain_points(products),
            "价格分析": self._analyze_pricing(products),
            "市场机会": await self._identify_opportunities(products),
        }
        return results

    async def _extract_selling_points(self, products):
        """
        提取核心卖点
        方法: 聚合所有好评，用NLP提取高频短语
        """
        all_positive_reviews = []
        for product in products:
            all_positive_reviews.extend(
                [r for r in product['reviews'] if r['rating'] >= 4]
            )

        prompt = f"""
        你是一位产品分析专家。请分析以下{len(all_positive_reviews)}条好评，
        提取客户最常提到的卖点。

        要求:
        1. 按提及频率排序
        2. 每个卖点附上典型原话
        3. 识别隐性需求（客户没直接说但重视的）
        4. 标注竞品差异化程度

        评论样本:
        {self._sample_reviews(all_positive_reviews, 100)}
        """

        return await self._call_llm(prompt)

    async def _extract_pain_points(self, products):
        """
        提取痛点
        方法: 聚合差评，情感分析+主题聚类
        """
        all_negative_reviews = []
        for product in products:
            all_negative_reviews.extend(
                [r for r in product['reviews'] if r['rating'] <= 2]
            )

        # 第一步: 痛点分类
        classify_prompt = f"""
        分析以下差评，将问题归类到以下类别：
        - 质量问题
        - 设计缺陷
        - 功能缺失
        - 物流问题
        - 客服问题
        - 性价比问题

        输出格式: JSON，每个问题包含类别、描述、严重度(1-10)

        差评样本:
        {self._sample_reviews(all_negative_reviews, 100)}
        """

        classified = await self._call_llm(classify_prompt)

        # 第二步: 聚类与优先级
        cluster_prompt = f"""
        对以下分类后的痛点进行聚类分析：
        1. 合并相似问题
        2. 按影响范围排序
        3. 标注哪些痛点是行业通病（难以解决），
           哪些是机会点（竞品都没解决好）

        {classified}
        """

        return await self._call_llm(cluster_prompt)
```

### 2.3 Prompt工程模板库

#### 模板1: 竞品分析综合Prompt

```
SYSTEM ROLE:
你是一位拥有10年经验的亚马逊资深运营专家，精通市场分析和产品策略。

INPUT DATA:
{product_data}

ANALYSIS TASK:

【第一部分：市场格局分析】
1. 计算市场集中度（Top5品牌市占率）
2. 判断市场阶段（成长期/成熟期/衰退期）
3. 评估进入壁垒（资金/技术/认证/品牌）

【第二部分：竞品深度剖析】
对Top5竞品逐一分析：
产品维度：
- 核心功能配置
- 材质与工艺
- 包装与配件
- 认证与专利

运营维度：
- Listing质量评分（标题/图片/A+）
- 评价策略（Vine/测评）
- 广告投放强度
- 价格策略

【第三部分：客户洞察】
基于{review_count}条评论：
- 目标用户画像（年龄/性别/使用场景）
- 购买决策因素（按重要性排序）
- 使用频率与更换周期
- 期望vs现实的gap

【第四部分：差异化机会】
输出3-5个差异化方向，每个包含：
- 机会描述
- 目标痛点
- 实现难度
- 预期溢价空间
- 竞品跟进壁垒

OUTPUT FORMAT:
Markdown表格 + 可视化建议图表类型
```

#### 模板2: 评论情感分析Prompt

```
TASK: 评论情感分析

REVIEW DATA:
{reviews_json}

INSTRUCTIONS:

1. 情感分类
   - 正面: 4-5星
   - 中性: 3星
   - 负面: 1-2星

2. 维度分析（对每条评论打分0-10）
   - 功能满意度
   - 质量满意度
   - 价格满意度
   - 服务满意度

3. 关键词提取
   - 提取具象描述词（如"电池续航8小时"）
   - 提取情感形容词（如"失望""惊艳"）
   - 标注词频和情感倾向

4. 时间趋势
   - 按月份统计平均分
   - 识别质量下降/改进信号

OUTPUT:
```json
{
  "summary": {
    "total_reviews": 1234,
    "avg_rating": 4.2,
    "sentiment_distribution": {"positive": 0.75, "neutral": 0.15, "negative": 0.10}
  },
  "dimension_scores": {
    "功能": 8.5,
    "质量": 7.2,
    "价格": 6.8,
    "服务": 9.1
  },
  "top_keywords": [
    {"word": "续航", "frequency": 156, "sentiment": "positive"},
    {"word": "充电口松动", "frequency": 89, "sentiment": "negative"}
  ],
  "monthly_trend": [
    {"month": "2024-01", "avg_rating": 4.3},
    {"month": "2024-02", "avg_rating": 4.1}
  ]
}
```
```

### 2.4 数据输出格式

#### 《产品差异化分析表》结构

```excel
| 列名 | 说明 | 数据来源 |
|------|------|----------|
| ASIN | 亚马逊标准识别码 | Jungle Scout |
| 品牌 | 品牌名称 | 亚马逊Listing |
| 价格 | 当前价格 | 实时抓取 |
| BSR排名 | 类目排名 | 亚马逊API |
| 月销量估算 | 预估月销量 | Jungle Scout算法 |
| 评分数 | 总评论数 | 亚马逊API |
| 平均评分 | 加权平均分 | 计算 |
| 核心卖点1 | 提取的卖点 | AI分析 |
| 核心卖点2 | 提取的卖点 | AI分析 |
| 核心卖点3 | 提取的卖点 | AI分析 |
| 主要差评1 | 提取的痛点 | AI分析 |
| 主要差评2 | 提取的痛点 | AI分析 |
| 主要差评3 | 提取的痛点 | AI分析 |
| 价格带 | 价格区间 | 分类 |
| 功能配置 | 关键参数 | 规格表 |
| 目标场景 | 使用场景 | 评论分析 |
| 差异化机会 | 机会点 | AI生成 |
| 进入难度 | 评估分 | AI评估 |
```

---

## 3. SOP 2: 关键词挖掘智能体详解

### 3.1 智能体架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                        KeywordMinerAgent                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│    输入                处理流程                    输出             │
│  ┌────────┐         ┌─────────────────┐          ┌──────────────┐   │
│  │产品类目 │────────▶│  Phase 1: 种子  │─────────▶│种子关键词库   │   │
│  │竞品ASIN│         │  关键词获取      │          │(50-100个)    │   │
│  └────────┘         └────────┬────────┘          └──────────────┘   │
│                               │                                   │
│                      ┌────────▼────────┐                          │
│                      │ Phase 2: 关键词  │                          │
│                      │   扩展 (1000+)   │                          │
│                      └────────┬────────┘                          │
│                               │                                   │
│      ┌────────────────────────┼────────────────────────┐          │
│      │                        │                        │          │
│ ┌────▼────┐            ┌──────▼──────┐         ┌───────▼──────┐    │
│ │ 卖家精灵 │            │ Amazon搜索   │         │ Google相关   │    │
│ │ API扩展 │            │ 建议词挖掘   │         │ 搜索词       │    │
│ └────┬────┘            └──────┬──────┘         └───────┬──────┘    │
│      │                        │                        │          │
│      └────────────────────────┼────────────────────────┘          │
│                               │                                   │
│                      ┌────────▼────────┐                          │
│                      │ Phase 3: 去重     │                          │
│                      │   (Levenshtein   │                          │
│                      │   + Embedding)   │                          │
│                      └────────┬────────┘                          │
│                               │                                   │
│                      ┌────────▼────────┐                          │
│                      │ Phase 4: 数据     │                          │
│                      │   丰富化         │                          │
│                      ├─────────────────┤                          │
│                      │ • 搜索量        │                          │
│                      │ • 竞争度(CPR)   │                          │
│                      │ • CPC价格       │                          │
│                      │ • 相关性评分     │                          │
│                      └────────┬────────┘                          │
│                               │                                   │
│                      ┌────────▼────────┐                          │
│                      │ Phase 5: 智能     │                          │
│                      │   过滤与分级     │                          │
│                      ├─────────────────┤                          │
│                      │ • 否定词识别     │                          │
│                      │ • 意图分类       │                          │
│                      │ • 机会评分       │                          │
│                      └────────┬────────┘                          │
│                               │                                   │
│                      ┌────────▼────────┐                          │
│                      │ Phase 6: 输出     │                          │
│                      ├─────────────────┤                          │
│                      │ • Excel词库     │                          │
│                      │ • 分级报告       │                          │
│                      │ • 否定库         │                          │
│                      └─────────────────┘                          │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 关键词扩展算法

```python
class KeywordExpander:
    """
    关键词扩展引擎
    """

    def __init__(self):
        self.mjs_api = MaiJiaLingAPI()
        self.helium10 = Helium10API()
        self.amazon_scraper = AmazonScraper()

    async def expand(self, seed_keywords: List[str]) -> Dict[str, KeywordData]:
        """
        从种子词扩展到完整词库
        """
        # ========== 策略1: API直接获取 ==========
        api_keywords = await self._fetch_from_apis(seed_keywords)

        # ========== 策略2: Amazon搜索建议递归挖掘 ==========
        suggestion_keywords = await self._recursive_suggestions(seed_keywords)

        # ========== 策略3: 竞品词库挖掘 ==========
        competitor_keywords = await self._mine_competitor_keywords()

        # ========== 策略4: 语义扩展（Embedding相似词）==========
        semantic_keywords = await self._semantic_expansion(seed_keywords)

        # ========== 合并与去重 ==========
        all_keywords = self._merge_and_deduplicate([
            api_keywords,
            suggestion_keywords,
            competitor_keywords,
            semantic_keywords
        ])

        return all_keywords

    async def _recursive_suggestions(self, keywords: List[str]) -> Set[str]:
        """
        Amazon搜索建议递归挖掘

        算法:
        1. 对每个关键词，获取Amazon下拉建议
        2. 对建议词再次获取建议（递归深度2-3）
        3. 提取其中的变体词

        示例:
        输入: "cat water fountain"
        → Amazon建议: "cat water fountain for multiple cats"
        → 再次挖掘: "cat water fountain for multiple cats large"
        """
        results = set()

        async def scrape_suggestions(keyword: str, depth: int = 0):
            if depth > 2:  # 限制递归深度
                return

            # 获取Amazon搜索建议
            suggestions = await self.amazon_scraper.get_search_suggestions(keyword)

            for suggestion in suggestions:
                # 清理和规范化
                clean_kw = self._normalize_keyword(suggestion)
                results.add(clean_kw)

                # 递归获取
                await scrape_suggestions(clean_kw, depth + 1)

        tasks = [scrape_suggestions(kw) for kw in keywords]
        await asyncio.gather(*tasks)

        return results

    async def _semantic_expansion(self, keywords: List[str]) -> Set[str]:
        """
        基于语义相似度的关键词扩展

        方法:
        1. 使用Embedding模型计算词向量
        2. 从历史词库中找出相似词
        3. 使用LLM生成同义表述
        """
        # 方案A: 向量检索（需要已有词库）
        similar_keywords = await self._vector_search(keywords, top_k=50)

        # 方案B: LLM生成同义词
        llm_variants = await self._llm_generate_variants(keywords)

        return similar_keywords | llm_variants

    async def _llm_generate_variants(self, keywords: List[str]) -> Set[str]:
        """
        使用LLM生成关键词变体
        """
        prompt = f"""
        你是一位SEO专家。请为以下产品关键词生成变体词。

        规则:
        1. 保持搜索意图不变
        2. 包含同义词替换
        3. 添加常用修饰词
        4. 改变语序
        5. 生成至少30个变体

        关键词: {", ".join(keywords)}

        输出格式: 每行一个关键词
        """

        response = await self._call_llm(prompt)
        return set(response.strip().split("\n"))
```

### 3.3 智能过滤与评分系统

```python
class KeywordScorer:
    """
    关键词评分与过滤系统
    """

    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.relevance_model = RelevanceModel()

    async def score_and_filter(
        self,
        keywords: List[KeywordData],
        criteria: FilterCriteria
    ) -> List[KeywordData]:
        """
        对关键词进行评分和过滤
        """
        filtered_keywords = []

        for kw in keywords:
            # ========== 步骤1: 硬性过滤 ==========
            if not self._passes_hard_filters(kw, criteria):
                continue

            # ========== 步骤2: 意图分类 ==========
            intent = await self._classify_intent(kw.text)
            if intent not in ["购买意向", "信息搜索"]:
                continue  # 过滤掉无关意图

            # ========== 步骤3: 相关性评分 ==========
            relevance = await self._score_relevance(
                kw.text,
                criteria.product_context
            )
            if relevance < criteria.min_relevance:
                continue

            # ========== 步骤4: 机会评分 ==========
            opportunity_score = self._calculate_opportunity(kw)

            # ========== 步骤5: 分级 ==========
            tier = self._assign_tier(kw, opportunity_score)

            kw.score = {
                "opportunity": opportunity_score,
                "relevance": relevance,
                "tier": tier
            }

            filtered_keywords.append(kw)

        # 按机会分排序
        return sorted(
            filtered_keywords,
            key=lambda x: x.score["opportunity"],
            reverse=True
        )

    def _calculate_opportunity(self, kw: KeywordData) -> float:
        """
        计算机会分

        公式:
        机会分 = (搜索量 ^ 0.5) * (相关性) / (竞争度 + 1)

        说明:
        - 搜索量取平方根，避免大词垄断
        - 相关性作为乘数，确保不相关词得分低
        - 竞争度作为除数，竞争越高分越低
        """
        import math

        search_volume = kw.search_volume or 0
        competition = kw.competition or 50
        relevance = kw.relevance or 0.5

        # 归一化处理
        norm_sv = math.sqrt(search_volume) / 100  # 假设最大10000/月
        norm_comp = competition / 100

        opportunity = (norm_sv * relevance) / (norm_comp + 0.1) * 100

        return round(opportunity, 2)

    async def _classify_intent(self, keyword: str) -> str:
        """
        关键词意图分类

        类别:
        - 购买意向: "buy", "cheap", "best", "deal"
        - 信息搜索: "how to", "what is", "review"
        - 品牌搜索: "apple", "anker", "sony"
        - 无关: "free", "diy", "repair"
        """
        prompt = f"""
        分析以下关键词的搜索意图：

        关键词: "{keyword}"

        请选择最符合的意图类别：
        A. 购买意向 - 用户准备购买
        B. 信息搜索 - 用户在了解产品
        C. 品牌搜索 - 用户搜索特定品牌
        D. 无关 - 不适合投放广告

        只返回类别字母(A/B/C/D)即可。
        """

        response = await self._call_llm(prompt)

        intent_map = {
            "A": "购买意向",
            "B": "信息搜索",
            "C": "品牌搜索",
            "D": "无关"
        }

        return intent_map.get(response.strip().upper(), "未知")

    async def _score_relevance(
        self,
        keyword: str,
        product_context: Dict
    ) -> float:
        """
        相关性评分

        方法:
        1. 使用Embedding计算语义相似度
        2. 结合产品特征匹配度
        3. LLM辅助判断
        """
        # 方法1: Embedding相似度
        similarity = await self._embedding_similarity(
            keyword,
            product_context["description"]
        )

        # 方法2: 关键词特征匹配
        feature_match = self._check_feature_match(
            keyword,
            product_context["features"]
        )

        # 方法3: LLM判断
        llm_score = await self._llm_relevance_check(
            keyword,
            product_context
        )

        # 加权平均
        relevance = (
            similarity * 0.4 +
            feature_match * 0.3 +
            llm_score * 0.3
        )

        return relevance

    def _assign_tier(self, kw: KeywordData, score: float) -> str:
        """
        关键词分级

        Tier 1 (蓝海词): 高搜索+低竞争+高相关性
        Tier 2 (成长词): 中等搜索+中等竞争
        Tier 3 (红海词): 高搜索+高竞争（大词）
        Tier 4 (长尾词): 低搜索+低竞争
        """
        sv = kw.search_volume or 0
        comp = kw.competition or 50

        if sv >= 1000 and comp <= 30:
            return "Tier 1"
        elif sv >= 500 and comp <= 50:
            return "Tier 2"
        elif sv >= 2000:
            return "Tier 3"
        else:
            return "Tier 4"
```

### 3.4 否定词自动识别

```python
class NegativeKeywordDetector:
    """
    否定词自动识别器
    """

    async def detect_negatives(
        self,
        keywords: List[str],
        product_context: Dict
    ) -> Set[str]:
        """
        检测应该加入否定列表的关键词
        """
        negatives = set()

        # 规则1: 明确的不相关词
        rule1_negatives = self._rule_based_negative(keywords)
        negatives.update(rule1_negatives)

        # 规则2: LLM判断
        llm_negatives = await self._llm_detect_negatives(
            keywords,
            product_context
        )
        negatives.update(llm_negatives)

        # 规则3: 竞品品牌词
        brand_negatives = await self._extract_competitor_brands(keywords)
        negatives.update(brand_negatives)

        return negatives

    def _rule_based_negative(self, keywords: List[str]) -> Set[str]:
        """
        基于规则的否定词检测
        """
        negative_patterns = [
            "免费", "破解", "盗版",  # 法律风险
            "二手", "旧", "维修",     # 非新品买家
            "教程", "怎么做",         # 信息搜索
            "配件", "零件",           # 非整机买家
        ]

        negatives = set()
        for kw in keywords:
            for pattern in negative_patterns:
                if pattern in kw:
                    negatives.add(kw)
                    break

        return negatives

    async def _llm_detect_negatives(
        self,
        keywords: List[str],
        product_context: Dict
    ) -> Set[str]:
        """
        使用LLM识别否定词
        """
        prompt = f"""
        你是一位亚马逊广告专家。请分析以下关键词，
        标记出应该加入否定列表的关键词。

        产品信息:
        - 类目: {product_context['category']}
        - 产品: {product_context['product_name']}
        - 目标客户: {product_context['target_audience']}

        待分析关键词:
        {chr(10).join(keywords[:100])}

        否定标准:
        1. 与产品功能无关
        2. 搜索者不是目标客户
        3. 带来无效流量（如信息搜索）

        输出格式: 每行一个否定词
        """

        response = await self._call_llm(prompt)
        return set(response.strip().split("\n"))
```

### 3.5 输出格式

#### 《产品关键词词库表》结构

```python
KEYWORD_EXCEL_SCHEMA = {
    "工作表": {
        "总览": [
            "关键词",
            "搜索量",
            "竞争度",
            "CPC",
            "相关性评分",
            "机会分",
            "分级",
            "意图",
            "推荐",
        ],
        "Tier1_蓝海词": ["关键词", "搜索量", "竞争度", "机会分"],
        "Tier2_成长词": ["关键词", "搜索量", "竞争度", "机会分"],
        "长尾词库": ["关键词", "搜索量", "相关性"],
        "否定词库": ["关键词", "否定原因"],
    }
}
```

---

## 4. SOP 3: Listing优化智能体详解

### 4.1 多智能体协作架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ListingOptimizerAgent                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                              输入层                                       │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ 输入: 产品信息 + 关键词库 + 目标市场 + 品牌调性                     │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                   │                                      │
│                                   ▼                                      │
│                              编排层                                       │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                    Listing Orchestrator                             │ │
│  │  • 分配任务给子智能体                                                │ │
│  │  • 管理依赖关系（标题→五点→描述）                                    │ │
│  │  • 收集结果并整合                                                    │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                   │                                      │
│            ┌──────────────────────┼──────────────────────┐              │
│            │                      │                      │              │
│            ▼                      ▼                      ▼              │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐        │
│  │  Copywriter     │   │  Image          │   │  QA Checker     │        │
│  │  Sub-agent      │   │  Generator      │   │  Sub-agent      │        │
│  │                 │   │                 │   │                 │        │
│  │  ┌───────────┐  │   │  ┌───────────┐  │   │  ┌───────────┐  │        │
│  │  │Title      │  │   │  │Main       │  │   │  │SEO Check  │  │        │
│  │  │Generator  │  │   │  │Image      │  │   │  │Compliance │  │        │
│  │  ├───────────┤  │   │  │Prompt     │  │   │  ├───────────┤  │        │
│  │  │Bullet     │  │   │  │Generator  │  │   │  │Spell      │  │        │
│  │  │Generator  │  │   │  ├───────────┤  │   │  │Check      │  │        │
│  │  ├───────────┤  │   │  │Lifestyle  │  │   │  ├───────────┤  │        │
│  │  │Description│  │   │  │Image      │  │   │  │Policy     │  │        │
│  │  │Generator  │  │   │  │Prompt     │  │   │  │Check      │  │        │
│  │  ├───────────┤  │   │  │Generator  │  │   │  │           │  │        │
│  │  │A+ Page    │  │   │  ├───────────┤  │   │  │           │  │        │
│  │  │Generator  │  │   │  │Infographic│  │   │  │           │  │        │
│  │  └───────────┘  │   │  │Prompt     │  │   │  └───────────┘  │        │
│  └─────────────────┘   │  │Generator  │  │   └─────────────────┘        │
│                       │  └───────────┘  │                              │
│                       └─────────────────┘                              │
│                                   │                                      │
│                                   ▼                                      │
│                              输出层                                       │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  • 完整Listing (标题/五点/描述/A+)                                  │ │
│  │  • 图片生成Prompt库                                                │ │
│  │  • QA检查报告                                                      │ │
│  │  • 埋词检查报告                                                    │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 标题生成子智能体

```python
class TitleGenerator:
    """
    标题生成子智能体
    """

    def __init__(self):
        self.llm = OpenAI()  # 或 Claude

    async def generate(
        self,
        product_info: Dict,
        keyword_library: List[KeywordData],
        market: str = "US",
        style: str = "professional"  # professional / friendly / luxury
    ) -> List[str]:
        """
        生成标题候选
        返回5个按SEO效果排序的标题
        """

        # ========== 步骤1: 准备核心元素 ==========
        core_elements = self._prepare_core_elements(
            product_info,
            keyword_library
        )

        # ========== 步骤2: 选择主关键词 ==========
        primary_keyword = self._select_primary_keyword(keyword_library)

        # ========== 步骤3: 生成多个候选 ==========
        candidates = await self._generate_candidates(
            core_elements,
            primary_keyword,
            style
        )

        # ========== 步骤4: SEO评分 ==========
        scored_candidates = await self._score_candidates(
            candidates,
            keyword_library
        )

        # ========== 步骤5: 返回Top 5 ==========
        return sorted(
            scored_candidates,
            key=lambda x: x["score"],
            reverse=True
        )[:5]

    def _prepare_core_elements(
        self,
        product_info: Dict,
        keyword_library: List[KeywordData]
    ) -> Dict:
        """
        准备标题核心元素
        """
        return {
            "brand": product_info.get("brand", ""),
            "model": product_info.get("model", ""),
            "core_feature": product_info.get("core_feature", ""),
            "material": product_info.get("material", ""),
            "color": product_info.get("color", ""),
            "size": product_info.get("size", ""),
            "quantity": product_info.get("quantity", ""),
            "target_audience": product_info.get("target_audience", ""),
            "use_case": product_info.get("use_case", ""),
            "top_keywords": [
                kw.text for kw in keyword_library[:20]
                if kw.score["tier"] in ["Tier 1", "Tier 2"]
            ]
        }

    def _select_primary_keyword(
        self,
        keyword_library: List[KeywordData]
    ) -> str:
        """
        选择主关键词

        策略:
        1. 优先Tier 1（蓝海词）
        2. 如果没有，选搜索量最高的Tier 2
        3. 必须包含产品核心词
        """
        tier1_keywords = [
            kw for kw in keyword_library
            if kw.score.get("tier") == "Tier 1"
        ]

        if tier1_keywords:
            # 选机会分最高的
            return max(tier1_keywords, key=lambda x: x.score["opportunity"]).text

        # 选Tier 2中搜索量最高的
        tier2_keywords = [
            kw for kw in keyword_library
            if kw.score.get("tier") == "Tier 2"
        ]

        if tier2_keywords:
            return max(tier2_keywords, key=lambda x: x.search_volume).text

        return keyword_library[0].text

    async def _generate_candidates(
        self,
        elements: Dict,
        primary_keyword: str,
        style: str
    ) -> List[Dict]:
        """
        生成候选标题
        """

        # 构建Prompt
        prompt = self._build_title_prompt(
            elements,
            primary_keyword,
            style
        )

        # 调用LLM生成
        response = await self._call_llm(prompt)

        # 解析结果
        candidates = self._parse_titles(response)

        return candidates

    def _build_title_prompt(
        self,
        elements: Dict,
        primary_keyword: str,
        style: str
    ) -> str:
        """
        构建标题生成Prompt
        """

        style_instructions = {
            "professional": "专业、正式、突出参数和认证",
            "friendly": "亲切、生活化、强调使用场景",
            "luxury": "高端、优雅、突出品质和体验"
        }

        prompt = f"""
你是一位亚马逊Listing专家。请根据以下信息生成5个产品标题。

【产品信息】
品牌: {elements['brand']}
核心功能: {elements['core_feature']}
材质: {elements['material']}
目标用户: {elements['target_audience']}
使用场景: {elements['use_case']}

【关键词要求】
主关键词（必须包含）: {primary_keyword}
可嵌入的次要关键词: {", ".join(elements['top_keywords'][:10])}

【风格要求】
{style_instructions.get(style, "专业、清晰")}

【Amazon标题规则】
1. 字符限制: 200字符以内（包含空格）
2. 每个单词首字母大写（介词除外）
3. 不包含促销信息（best, amazing, #1等）
4. 不使用主观评价
5. 数字用阿拉伯数字（2 not Two）
6. 尺寸用缩写（inch not inches）
7. 结构建议: 品牌 + 型号 + 核心词 + 材质 + 功能 + 场景

【输出要求】
请生成5个标题候选，每个标题一行，格式：
标题文本 | 预计字符数 | 主要卖点

示例格式：
ABC Premium Dog Water Fountain - 2L/67oz Automatic Water Dispenser with Ultra-Quiet Pump, Stainless Steel, Pet Water Bowl for Cats & Dogs - Filter Included | 178 | 大容量+静音+不锈钢
"""
        return prompt

    async def _score_candidates(
        self,
        candidates: List[str],
        keyword_library: List[KeywordData]
    ) -> List[Dict]:
        """
        对候选标题进行SEO评分
        """
        scored = []

        for title in candidates:
            score = {
                "title": title,
                "seo_score": await self._calculate_seo_score(
                    title,
                    keyword_library
                ),
                "readability_score": self._calculate_readability(title),
                "length_check": self._check_length(title),
                "compliance_check": await self._check_compliance(title)
            }
            score["total_score"] = (
                score["seo_score"] * 0.5 +
                score["readability_score"] * 0.2 +
                score["length_check"] * 0.15 +
                score["compliance_check"] * 0.15
            )
            scored.append(score)

        return scored

    async def _calculate_seo_score(
        self,
        title: str,
        keyword_library: List[KeywordData]
    ) -> float:
        """
        计算SEO得分
        """
        score = 0

        # 检查关键词覆盖
        title_lower = title.lower()

        # Tier 1关键词权重最高
        tier1_keywords = [
            kw.text.lower() for kw in keyword_library
            if kw.score.get("tier") == "Tier 1"
        ]

        for kw in tier1_keywords[:5]:
            if kw in title_lower:
                score += 20

        # Tier 2关键词
        tier2_keywords = [
            kw.text.lower() for kw in keyword_library
            if kw.score.get("tier") == "Tier 2"
        ]

        for kw in tier2_keywords[:10]:
            if kw in title_lower:
                score += 10

        # 关键词位置（越靠前越好）
        primary_keyword = keyword_library[0].text.lower()
        if primary_keyword in title_lower:
            position = title_lower.find(primary_keyword)
            if position < 50:
                score += 30
            elif position < 100:
                score += 20

        return min(score, 100)
```

### 4.3 五点描述生成子智能体

```python
class BulletGenerator:
    """
    五点描述生成子智能体
    """

    async def generate(
        self,
        product_info: Dict,
        keyword_library: List[KeywordData],
        pain_points: List[str],  # 来自SOP 1的痛点分析
        selling_points: List[str]  # 来自SOP 1的卖点分析
    ) -> List[Dict]:
        """
        生成五点描述

        每个要点包含:
        - 大标题（全大写，吸引眼球）
        - 详细描述
        - 埋入的关键词
        """

        # ========== 步骤1: 确定要点主题 ==========
        themes = await self._determine_themes(
            product_info,
            pain_points,
            selling_points
        )

        # ========== 步骤2: 为每个主题生成要点 ==========
        bullets = []
        for i, theme in enumerate(themes, 1):
            bullet = await self._generate_bullet(
                theme=theme,
                product_info=product_info,
                keyword_library=keyword_library,
                index=i
            )
            bullets.append(bullet)

        # ========== 步骤3: QA检查 ==========
        checked_bullets = await self._qa_check(bullets)

        return checked_bullets

    async def _determine_themes(
        self,
        product_info: Dict,
        pain_points: List[str],
        selling_points: List[str]
    ) -> List[Dict]:
        """
        确定五个要点的主题

        策略:
        1. 至少1个要点解决Top痛点
        2. 至少1个要点突出核心卖点
        3. 包含使用场景
        4. 包含规格/参数
        5. 包含品质保证
        """

        prompt = f"""
根据以下信息，确定产品五点描述的5个主题。

【产品】
{product_info}

【客户痛点】
{chr(10).join(f"- {p}" for p in pain_points[:5])}

【产品卖点】
{chr(10).join(f"- {s}" for s in selling_points[:5])}

要求:
1. 每个主题对应一个客户利益点
2. 必须覆盖以下维度:
   - 核心功能解决什么问题
   - 与竞品的差异化
   - 使用场景
   - 规格参数
   - 品质/服务保证

输出格式:
1. [主题名称] | [要解决的痛点] | [关键词方向]
2. ...
"""

        response = await self._call_llm(prompt)

        # 解析主题
        themes = self._parse_themes(response)
        return themes

    async def _generate_bullet(
        self,
        theme: Dict,
        product_info: Dict,
        keyword_library: List[KeywordData],
        index: int
    ) -> Dict:
        """
        生成单个要点
        """

        # 选择要嵌入的关键词
        target_keywords = self._select_keywords_for_bullet(
            theme["关键词方向"],
            keyword_library
        )

        # 构建Prompt
        prompt = f"""
你是一位亚马逊文案专家。请撰写第{index}个五点描述。

【主题】
{theme['主题名称']}

【要解决的痛点】
{theme['要解决的痛点']}

【产品信息】
{product_info}

【关键词要求】
必须自然嵌入以下关键词（至少2个）:
{chr(10).join(f"- {kw}" for kw in target_keywords[:5])}

【写作要求】
1. 大标题: 全大写，简洁有力，概括利益点
2. 详细描述:
   - 开头直击痛点或利益
   - 中间阐述如何实现
   - 结尾强化价值
3. 自然融入关键词，不生硬
4. 控制在1000字符以内（亚马逊限制）
5. 使用感性语言，让客户有代入感

【输出格式】
大标题: [全大写标题]
详细描述: [具体描述]
嵌入关键词: [列出的关键词]
"""

        response = await self._call_llm(prompt)

        # 解析结果
        bullet = self._parse_bullet(response)

        return {
            "index": index,
            "headline": bullet["headline"],
            "description": bullet["description"],
            "embedded_keywords": bullet["embedded_keywords"],
            "character_count": len(bullet["headline"]) + len(bullet["description"])
        }
```

### 4.4 图片生成Prompt子智能体

```python
class ImagePromptGenerator:
    """
    图片生成Prompt子智能体
    为DALL-E、Midjourney、Stable Diffusion等生成Prompt
    """

    async def generate_prompts(
        self,
        product_info: Dict,
        selling_points: List[str],
        target_style: str = "amazon_white_background"
    ) -> Dict[str, List[str]]:
        """
        为每种图片类型生成Prompt
        """

        image_types = {
            "main_image": {
                "count": 1,
                "requirement": "白底，产品正面，纯色背景(#FFFFFF)，专业产品摄影"
            },
            "lifestyle": {
                "count": 3,
                "requirement": "真实使用场景，真人模特，生活化"
            },
            "feature_highlight": {
                "count": 3,
                "requirement": "突出单个核心功能，特写镜头，标注说明"
            },
            "comparison": {
                "count": 1,
                "requirement": "与竞品或传统方案对比，突出优势"
            },
            "infographic": {
                "count": 2,
                "requirement": "信息图表，参数对比，使用步骤"
            }
        }

        prompts = {}

        for image_type, config in image_types.items():
            type_prompts = []
            for i in range(config["count"]):
                prompt = await self._generate_single_prompt(
                    image_type=image_type,
                    index=i,
                    product_info=product_info,
                    selling_points=selling_points,
                    requirement=config["requirement"]
                )
                type_prompts.append(prompt)

            prompts[image_type] = type_prompts

        return prompts

    async def _generate_single_prompt(
        self,
        image_type: str,
        index: int,
        product_info: Dict,
        selling_points: List[str],
        requirement: str
    ) -> Dict:
        """
        生成单个图片Prompt
        """

        # 基础产品描述
        base_description = self._build_base_description(product_info)

        # 根据图片类型定制
        if image_type == "main_image":
            prompt = self._build_main_image_prompt(
                base_description,
                product_info
            )
        elif image_type == "lifestyle":
            prompt = await self._build_lifestyle_prompt(
                base_description,
                product_info,
                selling_points,
                index
            )
        elif image_type == "feature_highlight":
            prompt = self._build_feature_prompt(
                base_description,
                selling_points[index] if index < len(selling_points) else selling_points[0]
            )
        # ... 其他类型

        return {
            "prompt": prompt,
            "negative_prompt": self._get_negative_prompt(image_type),
            "parameters": self._get_image_parameters(image_type),
            "usage_tip": self._get_usage_tip(image_type)
        }

    def _build_main_image_prompt(
        self,
        base_description: str,
        product_info: Dict
    ) -> str:
        """
        构建主图Prompt

        要求:
        - 纯白背景 (#FFFFFF)
        - 专业产品摄影
        - 柔和光线
        - 高细节
        - 亚马逊合规
        """

        prompt = f"""
Professional product photography, {base_description},

Composition:
- Centered product, 45-degree angle showing main features
- Clean white background (#FFFFFF pure white)
- Soft, even studio lighting
- No shadows or harsh highlights
- High resolution, sharp details

Style:
- Commercial product photography
- Amazon marketplace standard
- Minimal and clean
- Professional color grading

Technical:
- 8K resolution
- Photorealistic
- HDR lighting
- Product photography style
- Canon EOS R5, 100mm macro lens

Negative prompts:
- No background elements
- No text or logos
- No watermarks
- No people
- No props (unless part of product)
- No shadows
"""
        return prompt.strip()

    async def _build_lifestyle_prompt(
        self,
        base_description: str,
        product_info: Dict,
        selling_points: List[str],
        index: int
    ) -> str:
        """
        构建场景图Prompt
        """

        # 获取使用场景
        use_case = product_info.get("use_cases", [])[index] if index < len(product_info.get("use_cases", [])) else product_info.get("use_case", "")

        # 获取目标用户
        target_audience = product_info.get("target_audience", "adults")

        prompt = f"""
Lifestyle photography showing {base_description} in real use:

Scene:
{use_case}

People:
- {target_audience} using the product naturally
- Authentic interaction, not posed
- Diverse representation if applicable

Composition:
- Product is the hero, clearly visible
- Context shows scale and usage
- Natural indoor/outdoor lighting
- Depth of field with product in focus

Style:
- Warm, inviting atmosphere
- Real-life moment, not studio
- Editorial photography style
- High-end lifestyle catalog

Technical:
- Natural lighting with soft fill
- Environmental context
- Authentic moment capture
- Nikon D850, 35mm lens

Negative prompts:
- No studio lighting
- No white background
- No stock photo appearance
- No artificial poses
"""
        return prompt.strip()
```

### 4.5 QA检查子智能体

```python
class ListingQAChecker:
    """
    Listing质量检查子智能体
    """

    async def comprehensive_check(
        self,
        listing: Dict,  # 包含 title, bullets, description
        keyword_library: List[KeywordData],
        market: str
    ) -> Dict:
        """
        执行全面QA检查
        """

        results = {
            "overall_score": 0,
            "checks": {},
            "issues": [],
            "recommendations": []
        }

        # ========== 检查1: 埋词检查 ==========
        keyword_check = await self._check_keyword_embedding(
            listing,
            keyword_library
        )
        results["checks"]["keyword_embedding"] = keyword_check

        # ========== 检查2: 字符限制 ==========
        length_check = self._check_character_limits(listing, market)
        results["checks"]["character_limits"] = length_check

        # ========== 检查3: 违禁词检查 ==========
        compliance_check = await self._check_prohibited_terms(listing, market)
        results["checks"]["compliance"] = compliance_check

        # ========== 检查4: 拼写和语法 ==========
        spell_check = await self._check_spelling_grammar(listing)
        results["checks"]["spelling_grammar"] = spell_check

        # ========== 检查5: SEO评分 ==========
        seo_check = await self._seo_score(listing, keyword_library)
        results["checks"]["seo_score"] = seo_check

        # ========== 检查6: 可读性 ==========
        readability_check = self._check_readability(listing)
        results["checks"]["readability"] = readability_check

        # ========== 计算总分 ==========
        results["overall_score"] = self._calculate_total_score(results["checks"])

        # ========== 生成建议 ==========
        results["recommendations"] = self._generate_recommendations(results)

        return results

    async def _check_keyword_embedding(
        self,
        listing: Dict,
        keyword_library: List[KeywordData]
    ) -> Dict:
        """
        检查关键词埋入情况
        """

        result = {
            "score": 0,
            "covered_keywords": [],
            "missing_keywords": [],
            "details": {}
        }

        full_text = (
            listing.get("title", "") + " " +
            " ".join(b.get("description", "") for b in listing.get("bullets", [])) + " " +
            listing.get("description", "")
        ).lower()

        # 检查Tier 1关键词（必须全部覆盖）
        tier1_keywords = [
            kw for kw in keyword_library
            if kw.score.get("tier") == "Tier 1"
        ]

        for kw in tier1_keywords:
            if kw.text.lower() in full_text:
                result["covered_keywords"].append({
                    "keyword": kw.text,
                    "tier": "Tier 1",
                    "location": self._find_keyword_location(kw.text, listing)
                })
            else:
                result["missing_keywords"].append({
                    "keyword": kw.text,
                    "tier": "Tier 1",
                    "importance": "high"
                })

        # 检查Tier 2关键词（至少覆盖50%）
        tier2_keywords = [
            kw for kw in keyword_library
            if kw.score.get("tier") == "Tier 2"
        ]

        tier2_covered = 0
        for kw in tier2_keywords:
            if kw.text.lower() in full_text:
                tier2_covered += 1
                result["covered_keywords"].append({
                    "keyword": kw.text,
                    "tier": "Tier 2"
                })

        # 计算得分
        tier1_score = len(result["covered_keywords"]) / max(len(tier1_keywords), 1) * 50
        tier2_score = (tier2_covered / max(len(tier2_keywords), 1)) * 50

        result["score"] = tier1_score + tier2_score

        # 详细报告
        result["details"] = {
            "tier1_coverage": f"{len([k for k in result['covered_keywords'] if k['tier']=='Tier 1'])}/{len(tier1_keywords)}",
            "tier2_coverage": f"{tier2_covered}/{len(tier2_keywords)}",
            "total_keywords_embedded": len(result["covered_keywords"]),
            "critical_missing": len([k for k in result["missing_keywords"] if k["importance"]=="high"])
        }

        return result

    def _find_keyword_location(
        self,
        keyword: str,
        listing: Dict
    ) -> str:
        """
        找出关键词在Listing中的位置
        """
        locations = []

        if keyword.lower() in listing.get("title", "").lower():
            locations.append("标题")

        for i, bullet in enumerate(listing.get("bullets", []), 1):
            if keyword.lower() in bullet.get("description", "").lower():
                locations.append(f"要点{i}")

        if keyword.lower() in listing.get("description", "").lower():
            locations.append("描述")

        return ", ".join(locations) if locations else "未找到"

    async def _check_prohibited_terms(
        self,
        listing: Dict,
        market: str
    ) -> Dict:
        """
        检查违禁词和敏感词

        包括:
        - 亚马逊禁止的词汇
        - 过度承诺的词汇
        - 竞品品牌名
        - 法律风险词汇
        """

        # 违禁词库（示例）
        prohibited_terms = {
            "absolute": ["best", "worst", "#1", "top rated", "perfect"],
            "subjective": ["amazing", "incredible", "unbelievable"],
            "claims": ["cure", "heal", "prevent", "treat"],  # 医疗声明
            "competitors": await self._get_competitor_brands(market),
        }

        result = {
            "score": 100,
            "found_terms": [],
            "severity": "none"
        }

        full_text = (
            listing.get("title", "") + " " +
            " ".join(b.get("description", "") for b in listing.get("bullets", [])) + " " +
            listing.get("description", "")
        ).lower()

        for category, terms in prohibited_terms.items():
            for term in terms:
                if term.lower() in full_text:
                    severity = self._get_term_severity(category)
                    result["found_terms"].append({
                        "term": term,
                        "category": category,
                        "severity": severity,
                        "location": self._find_term_location(term, listing)
                    })

                    # 扣分
                    if severity == "critical":
                        result["score"] -= 20
                    elif severity == "high":
                        result["score"] -= 10
                    else:
                        result["score"] -= 5

        result["score"] = max(result["score"], 0)

        if result["score"] < 70:
            result["severity"] = "high"
        elif result["score"] < 90:
            result["severity"] = "medium"

        return result
```

---

## 5. 技术栈与部署方案

### 5.1 推荐技术栈

```yaml
# 后端框架
Backend:
  Framework: FastAPI
  原因:
    - 异步支持（调用多个API）
    - 自动API文档
    - 类型提示友好
    - 高性能

# 任务队列
Task Queue:
  Framework: Celery + Redis
  用途:
    - 长时间运行的任务
    - 定时任务（每日市场调研）
    - 任务重试机制

# 数据库
Databases:
  主库: PostgreSQL
    - 存储结构化数据
    - 支持JSON字段
    - 全文搜索

  向量库: Qdrant / Weaviate
    - 存储关键词Embedding
    - 语义搜索
    - 相似词推荐

  缓存: Redis
    - API响应缓存
    - 任务队列
    - 限流

# LLM集成
LLM:
  主要: OpenAI GPT-4
    - 复杂分析任务
    - Prompt工程友好

  备用: Anthropic Claude
    - 长文本分析
    - 更稳定的输出

  本地: Ollama (可选)
    - 降低成本
    - 数据隐私

# Web爬虫
Scraping:
  Framework: Playwright
    - 动态渲染
    - 反爬虫能力强

  辅助: httpx
    - 高性能异步HTTP
    - API调用

# 前端
Frontend:
  Framework: Streamlit
    - 快速原型
    - Python原生
    - 数据可视化友好

  生产: Next.js + shadcn/ui
    - 更好的用户体验
    - 可部署为独立服务
```

### 5.2 项目结构

```
amazon-ai-agent/
├── backend/
│   ├── api/                    # API层
│   │   ├── routes/
│   │   │   ├── market_research.py
│   │   │   ├── keyword_miner.py
│   │   │   └── listing_optimizer.py
│   │   └── main.py
│   │
│   ├── agents/                 # 智能体核心
│   │   ├── base.py            # 基础Agent类
│   │   ├── orchestrator.py    # 编排器
│   │   ├── market_research/
│   │   │   ├── agent.py
│   │   │   ├── scanner.py
│   │   │   ├── analyzer.py
│   │   │   └── reporter.py
│   │   ├── keyword_miner/
│   │   │   ├── agent.py
│   │   │   ├── expander.py
│   │   │   ├── scorer.py
│   │   │   └── filter.py
│   │   └── listing_optimizer/
│   │       ├── agent.py
│   │       ├── title_gen.py
│   │       ├── bullet_gen.py
│   │       ├── image_prompt.py
│   │       └── qa_checker.py
│   │
│   ├── tools/                  # 工具层
│   │   ├── scrapers/          # 爬虫
│   │   ├── apis/              # 第三方API封装
│   │   ├── llm/               # LLM封装
│   │   └── database/          # 数据库操作
│   │
│   ├── models/                 # 数据模型
│   │   ├── keyword.py
│   │   ├── product.py
│   │   └── listing.py
│   │
│   ├── prompts/                # Prompt模板
│   │   ├── market_research/
│   │   ├── keyword_miner/
│   │   └── listing_optimizer/
│   │
│   ├── tasks/                  # Celery任务
│   │   └── worker.py
│   │
│   └── utils/                  # 工具函数
│       ├── text_processing.py
│       ├── similarity.py
│       └── validators.py
│
├── frontend/                   # Streamlit前端
│   ├── pages/
│   │   ├── 1_Market_Research.py
│   │   ├── 2_Keyword_Miner.py
│   │   └── 3_Listing_Optimizer.py
│   └── utils.py
│
├── database/                   # 数据库
│   ├── migrations/
│   └── seeds/
│
├── config/
│   ├── settings.py            # 配置管理
│   ├── prompts.yaml           # Prompt配置
│   └── api_keys.yaml          # API密钥
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── prompts/
│
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
│
├── scripts/
│   ├── setup.sh
│   └── deploy.sh
│
└── docs/
    ├── ARCHITECTURE.md
    ├── API.md
    └── PROMPTS.md
```

### 5.3 核心代码示例

#### 基础Agent类

```python
# backend/agents/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    智能体基类
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.llm = self._init_llm()
        self.tools = self._init_tools()

    def _init_llm(self):
        """初始化LLM"""
        from backend.tools.llm.factory import LLMFactory
        return LLMFactory.create(
            provider=self.config.get("llm_provider", "openai"),
            model=self.config.get("llm_model", "gpt-4")
        )

    def _init_tools(self) -> Dict[str, Any]:
        """初始化工具集"""
        return {}

    @abstractmethod
    async def execute(self, input_data: Dict) -> Dict:
        """
        执行智能体任务

        Args:
            input_data: 输入数据

        Returns:
            执行结果
        """
        pass

    async def _call_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        调用LLM
        """
        return await self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            **kwargs
        )

    def _log_progress(self, message: str, level: str = "info"):
        """
        记录进度
        """
        log_func = getattr(logger, level, logger.info)
        log_func(f"[{self.__class__.__name__}] {message}")
```

#### 编排器实现

```python
# backend/agents/orchestrator.py

from typing import Dict, List, Any
import asyncio

from backend.agents.base import BaseAgent
from backend.agents.market_research.agent import MarketResearchAgent
from backend.agents.keyword_miner.agent import KeywordMinerAgent
from backend.agents.listing_optimizer.agent import ListingOptimizerAgent


class AgentOrchestrator:
    """
    智能体编排器

    负责协调多个智能体执行完整工作流
    """

    def __init__(self, config: Dict):
        self.config = config
        self.agents = self._init_agents()

    def _init_agents(self) -> Dict[str, BaseAgent]:
        """初始化所有智能体"""
        return {
            "market_research": MarketResearchAgent(
                self.config.get("market_research", {})
            ),
            "keyword_miner": KeywordMinerAgent(
                self.config.get("keyword_miner", {})
            ),
            "listing_optimizer": ListingOptimizerAgent(
                self.config.get("listing_optimizer", {})
            )
        }

    async def execute_workflow(
        self,
        workflow: str,
        input_data: Dict
    ) -> Dict:
        """
        执行完整工作流

        Args:
            workflow: 工作流名称 ("full_pipeline", "research_only", etc.)
            input_data: 输入数据

        Returns:
            工作流执行结果
        """

        if workflow == "full_pipeline":
            return await self._full_pipeline(input_data)

        elif workflow == "research_only":
            return await self._research_only(input_data)

        elif workflow == "keywords_only":
            return await self._keywords_only(input_data)

        elif workflow == "listing_only":
            return await self._listing_only(input_data)

        else:
            raise ValueError(f"Unknown workflow: {workflow}")

    async def _full_pipeline(self, input_data: Dict) -> Dict:
        """
        完整流水线: 市场调研 → 关键词挖掘 → Listing优化
        """

        results = {
            "workflow": "full_pipeline",
            "stages": {}
        }

        # ========== 阶段1: 市场调研 ==========
        self._log("开始市场调研...")
        research_result = await self.agents["market_research"].execute(
            product_keyword=input_data["product_keyword"],
            market=input_data.get("market", "US")
        )
        results["stages"]["market_research"] = research_result

        # ========== 阶段2: 关键词挖掘 ==========
        self._log("开始关键词挖掘...")
        keyword_result = await self.agents["keyword_miner"].execute(
            product_keyword=input_data["product_keyword"],
            research_data=research_result
        )
        results["stages"]["keyword_miner"] = keyword_result

        # ========== 阶段3: Listing优化 ==========
        self._log("开始Listing优化...")
        listing_result = await self.agents["listing_optimizer"].execute(
            product_info=input_data.get("product_info", {}),
            keyword_library=keyword_result["keywords"],
            market_research=research_result
        )
        results["stages"]["listing_optimizer"] = listing_result

        # ========== 整合结果 ==========
        results["summary"] = self._generate_summary(results)

        return results

    async def _parallel_research_and_keywords(
        self,
        input_data: Dict
    ) -> Dict:
        """
        并行执行市场调研和关键词挖掘

        适用场景: 当市场调研结果不影响关键词挖掘时
        """

        # 并行执行
        research_task = self.agents["market_research"].execute(
            product_keyword=input_data["product_keyword"],
            market=input_data.get("market", "US")
        )

        keyword_task = self.agents["keyword_miner"].execute(
            product_keyword=input_data["product_keyword"]
        )

        research_result, keyword_result = await asyncio.gather(
            research_task,
            keyword_task
        )

        return {
            "market_research": research_result,
            "keyword_miner": keyword_result
        }

    def _log(self, message: str):
        """记录日志"""
        print(f"[Orchestrator] {message}")

    def _generate_summary(self, results: Dict) -> Dict:
        """生成执行摘要"""
        return {
            "total_stages": len(results["stages"]),
            "keywords_found": len(
                results["stages"]
                .get("keyword_miner", {})
                .get("keywords", [])
            ),
            "listing_generated": bool(
                results["stages"]
                .get("listing_optimizer", {})
                .get("title")
            )
        }
```

#### API路由

```python
# backend/api/routes/market_research.py

from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from backend.agents.orchestrator import AgentOrchestrator
from backend.config import settings


router = APIRouter(prefix="/api/market-research", tags=["市场调研"])


class MarketResearchRequest(BaseModel):
    product_keyword: str
    market: str = "US"
    depth: str = "standard"  # quick / standard / deep


class KeywordMiningRequest(BaseModel):
    product_keyword: str
    seed_keywords: Optional[list] = None
    max_keywords: int = 1000


class ListingOptimizerRequest(BaseModel):
    product_keyword: str
    product_info: dict
    use_previous_research: bool = True


# 依赖注入
async def get_orchestrator():
    return AgentOrchestrator(settings.AGENT_CONFIG)


@router.post("/analyze")
async def analyze_market(
    request: MarketResearchRequest,
    background_tasks: BackgroundTasks,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    执行市场调研

    可同步或异步执行（后台任务）
    """

    # 同步执行（快速模式）
    if request.depth == "quick":
        result = await orchestrator.agents["market_research"].execute(
            product_keyword=request.product_keyword,
            market=request.market
        )
        return {"status": "completed", "data": result}

    # 异步执行（标准/深度模式）
    task_id = f"research_{request.product_keyword}_{request.market}"

    background_tasks.add_task(
        orchestrator.agents["market_research"].execute,
        product_keyword=request.product_keyword,
        market=request.market
    )

    return {
        "status": "processing",
        "task_id": task_id,
        "message": "调研任务已开始，请稍后查询结果"
    }


@router.post("/keywords")
async def mine_keywords(
    request: KeywordMiningRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    执行关键词挖掘
    """
    result = await orchestrator.agents["keyword_miner"].execute(
        product_keyword=request.product_keyword,
        seed_keywords=request.seed_keywords
    )

    return {
        "status": "success",
        "keywords_count": len(result["keywords"]),
        "data": result
    }


@router.post("/listing/generate")
async def generate_listing(
    request: ListingOptimizerRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    生成Listing
    """
    result = await orchestrator.agents["listing_optimizer"].execute(
        product_info=request.product_info,
        use_previous_research=request.use_previous_research
    )

    return {
        "status": "success",
        "listing": result
    }


@router.post("/workflow/full")
async def full_workflow(
    request: dict,
    background_tasks: BackgroundTasks,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    执行完整工作流
    """
    result = await orchestrator.execute_workflow(
        workflow="full_pipeline",
        input_data=request
    )

    return result
```

---

## 6. 成本与ROI分析

### 6.1 月度运营成本（中等规模）

| 项目 | 月成本 | 说明 |
|------|--------|------|
| **API费用** | | |
| OpenAI GPT-4 | $300 | 约300万tokens/月 |
| Claude API | $100 | 长文本分析 |
| Jungle Scout | $100 | 基础订阅 |
| 卖家精灵 | $100 | 基础订阅 |
| **服务器** | | |
| 云服务器(4核8G) | $50 | 阿里云/腾讯云 |
| PostgreSQL托管 | $30 | 云数据库 |
| Redis托管 | $20 | 缓存服务 |
| Qdrant向量库 | $0 | 自托管 |
| **域名与SSL** | $15 | |
| **监控与日志** | $10 | Sentry等 |
| **总计** | **$725/月** | |

### 6.2 ROI计算

```
假设场景:
- 团队规模: 5人运营团队
- 产品数量: 50个SKU
- 原人工成本: $8000/月（1人专职市场调研）
- 效率提升: 80%

节省成本:
- 人力节省: $6400/月
- 时间节省: 每个产品调研从2天 → 2小时

ROI = (节省成本 - 系统成本) / 系统成本
    = ($6400 - $725) / $725
    = 7.8倍

投资回收期: < 1个月
```

### 6.3 分阶段实施路线

```
阶段1: MVP (1个月)
├─ 核心功能: 基础市场调研
├─ 成本: $200/月
├─ 效果: 节省40%调研时间
└─ 下一步: 添加关键词挖掘

阶段2: 完整系统 (3个月)
├─ 核心功能: 完整SOP 1+2+3
├─ 成本: $500/月
├─ 效果: 节省70%运营时间
└─ 下一步: 优化与扩展

阶段3: 智能化平台 (6个月)
├─ 核心功能: 自动化决策
├─ 成本: $725/月
├─ 效果: 节省85%运营时间
└─ 下一步: 团队协作功能

阶段4: 企业级 (12个月)
├─ 核心功能: 多账号管理、数据分析
├─ 成本: $1200/月
├─ 效果: 支持百人团队
└─ 持续优化
```

---

## 附录: 快速启动命令

```bash
# 1. 克隆项目
git clone https://github.com/your-org/amazon-ai-agent.git
cd amazon-ai-agent

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑.env，填入API密钥

# 4. 初始化数据库
python scripts/init_db.py

# 5. 启动后端服务
uvicorn backend.api.main:app --reload

# 6. 启动前端（新终端）
streamlit run frontend/Home.py

# 7. 启动Celery Worker（新终端）
celery -A backend.tasks.worker worker --loglevel=info

# 8. 访问应用
# 打开浏览器: http://localhost:8501
```

---

## 系统流程图

### 完整工作流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          用户输入产品信息                                 │
│                         产品类目/关键词/目标市场                           │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        SOP 1: 市场调研智能体                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐         │
│  │竞品扫描  │ →  │价格分析  │ →  │评论挖掘  │ →  │痛点提取  │         │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘         │
│                                       │                                   │
│                        产出: 《产品差异化分析表》                        │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        SOP 2: 关键词挖掘智能体                            │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐         │
│  │词源扩展  │ →  │去重合并  │ →  │意图分类  │ →  │机会评分  │         │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘         │
│                                       │                                   │
│                        产出: 《产品关键词词库表》                         │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        SOP 3: Listing优化智能体                           │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐         │
│  │标题生成  │ →  │五点撰写  │ →  │图片Prompt│ →  │QA检查   │         │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘         │
│                                       │                                   │
│                        产出: 完整Listing + 图片Prompt                    │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              输出结果                                     │
│  • 市场调研报告（Excel/PDF）                                             │
│  • 关键词词库（Excel）                                                   │
│  • 完整Listing（标题/五点/描述/A+）                                      │
│  • 图片生成Prompt库                                                      │
│  • QA检查报告                                                            │
└─────────────────────────────────────────────────────────────────────────┘
```

---

**文档版本:** v1.0
**最后更新:** 2026-03-12
**维护者:** AI Systems Team
