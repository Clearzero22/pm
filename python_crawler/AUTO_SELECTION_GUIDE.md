# 自动化选品实现指南

## 目录

1. [概述](#一概述)
2. [系统架构](#二系统架构)
3. [选品算法设计](#三选品算法设计)
4. [代码实现](#四代码实现)
5. [定时任务](#五定时任务)
6. [仪表盘集成](#六仪表盘集成)
7. [部署方案](#七部署方案)

---

## 一、概述

### 1.1 什么是自动化选品

自动化选品是指通过算法自动分析商品数据，根据多个维度（评分、价格、变体、评论等）计算综合得分，自动筛选出最有潜力的商品，减少人工判断的工作量。

### 1.2 核心价值

| 价值点 | 说明 |
|-------|------|
| ⏱️ **节省时间** | 自动筛选，无需人工逐一分析 |
| 📊 **数据驱动** | 基于多维度数据决策，更客观 |
| 🔄 **持续监控** | 定时执行，持续发现新机会 |
| ⚠️ **风险预警** | 自动识别高风险商品 |

### 1.3 实现层次

```
Level 1: 基础筛选     →  价格/评分过滤
Level 2: 智能评分     →  多维度加权打分
Level 3: 自动推荐     →  排序 + 风险评估
Level 4: 持续监控     →  定时任务 + 变化追踪
Level 5: 智能决策     →  AI 辅助决策（进阶）
```

---

## 二、系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        自动化选品系统                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐         │
│  │   数据采集层  │    │   分析处理层  │    │   输出展示层  │         │
│  │              │    │              │    │              │         │
│  │  - 爬虫引擎   │───▶│  - 选品算法   │───▶│  - 仪表盘    │         │
│  │  - 数据清洗   │    │  - 评分引擎   │    │  - 报告生成  │         │
│  │  - 去重存储   │    │  - 风险检测   │    │  - 飞书推送  │         │
│  └──────────────┘    └──────────────┘    └──────────────┘         │
│         │                   │                   │                  │
│         ▼                   ▼                   ▼                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐         │
│  │   CSV/DB     │    │   评分缓存    │    │   通知服务   │         │
│  └──────────────┘    └──────────────┘    └──────────────┘         │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                      调度层 (Scheduler)                        │  │
│  │                                                               │  │
│  │   定时任务: 每天 08:00 执行 → 爬取 → 分析 → 推送               │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流程

```
Amazon Best Sellers
        │
        ▼
   ┌─────────┐
   │ 爬虫抓取 │
   └────┬────┘
        │
        ▼
   ┌─────────┐     ┌─────────────────────────────────┐
   │ CSV存储 │────▶│ 字段: asin, title, price, rating │
   └────┬────┘     │ variants, images, description... │
        │          └─────────────────────────────────┘
        ▼
   ┌─────────┐
   │ 数据预处理│ ← 清洗、转换、计算派生字段
   └────┬────┘
        │
        ▼
   ┌─────────┐     ┌─────────────────────────────────┐
   │ 评分引擎 │────▶│ 计算每个商品的综合得分 (0-100)  │
   └────┬────┘     └─────────────────────────────────┘
        │
        ▼
   ┌─────────┐
   │ 风险评估 │ ← 识别高风险、中风险、低风险商品
   └────┬────┘
        │
        ▼
   ┌─────────┐
   │ 排序推荐 │ ← 按得分排序，输出 Top N
   └────┬────┘
        │
        ├──────────▶ 仪表盘展示
        │
        ├──────────▶ 飞书多维表格
        │
        └──────────▶ 选品报告 (TXT/JSON)
```

---

## 三、选品算法设计

### 3.1 评分维度

| 维度 | 权重 | 说明 | 计算方式 |
|------|------|------|----------|
| **评分 (rating)** | 30% | 用户评价质量 | 4.8+ = 100分, 4.5 = 80分 |
| **价格竞争力** | 20% | 与同类均价对比 | 低于均价70% = 100分 |
| **评论数量** | 15% | 销量验证程度 | 1000+评论 = 100分 |
| **变体多样性** | 15% | 商品选择丰富度 | 3-8个变体 = 100分 |
| **图片质量** | 10% | 商品展示完整度 | 5+张图 = 60分, 8+张 = 100分 |
| **利润空间** | 10% | 预估利润率 | 利润率50%+ = 100分 |

### 3.2 评分公式

```
综合得分 = Σ (维度得分 × 权重)

例如：
- 评分: 4.7 → 88分 × 30% = 26.4
- 价格: $25 (均价$30) → 80分 × 20% = 16.0
- 评论: 500 → 80分 × 15% = 12.0
- 变体: 5个 → 100分 × 15% = 15.0
- 图片: 8张 → 100分 × 10% = 10.0
- 利润: 40% → 80分 × 10% = 8.0

综合得分 = 26.4 + 16.0 + 12.0 + 15.0 + 10.0 + 8.0 = 87.4
```

### 3.3 风险评估规则

#### ✅ 积极信号（加分项）

```python
POSITIVE_SIGNALS = [
    ("rating >= 4.5", "高评分商品"),
    ("review_count >= 100", "评论充足，销量验证"),
    ("3 <= variants <= 8", "变体数量适中"),
    ("image_count >= 5", "图片丰富"),
    ("is_prime == True", "Prime 商品"),
    ("is_fba == True", "FBA 配送"),
]
```

#### ⚠️ 风险信号（警告项）

```python
RISK_SIGNALS = [
    ("rating < 4.0", "评分偏低", "HIGH"),
    ("review_count < 50", "评论较少，未验证", "MEDIUM"),
    ("variants > 15", "变体过多，管理复杂", "MEDIUM"),
    ("price > 50", "价格较高，竞争激烈", "LOW"),
    ("seller != 'Amazon'", "非自营商品", "LOW"),
]
```

#### 风险等级判定

```
风险等级 = 
    LOW    (绿色) : 无警告信号
    MEDIUM (黄色) : 1-2 个警告信号
    HIGH   (红色) : 3+ 个警告信号 或 有高风险信号
```

---

## 四、代码实现

### 4.1 项目结构

```
python_crawler/
├── src/
│   ├── crawler.py              # 爬虫（已有）
│   ├── product_detail_parser.py # 详情解析（已有）
│   ├── selection/              # 新增：选品模块
│   │   ├── __init__.py
│   │   ├── scorer.py           # 评分引擎
│   │   ├── risk_assessor.py    # 风险评估
│   │   ├── selector.py         # 选品器
│   │   └── config.py           # 配置参数
│   └── utils.py
├── scheduler.py                # 定时任务
├── output/
│   ├── amazon_products.csv
│   ├── recommendations.json    # 选品推荐结果
│   └── reports/                # 报告目录
└── dashboard/
    └── app.py                  # 仪表盘（扩展）
```

### 4.2 配置文件 (config.py)

```python
# src/selection/config.py

"""选品算法配置"""

# 维度权重配置
SCORING_WEIGHTS = {
    "rating": 0.30,
    "price_competitiveness": 0.20,
    "review_volume": 0.15,
    "variant_diversity": 0.15,
    "image_quality": 0.10,
    "profit_margin": 0.10,
}

# 评分阈值
RATING_THRESHOLDS = {
    "excellent": 4.8,    # 100分
    "good": 4.5,         # 80分
    "average": 4.0,      # 60分
    "poor": 3.5,         # 40分
}

# 价格竞争力阈值（相对均价的倍数）
PRICE_THRESHOLDS = {
    "very_competitive": 0.7,   # 低于均价30%
    "competitive": 1.0,        # 等于均价
    "average": 1.3,            # 高于均价30%
}

# 评论数量阈值
REVIEW_THRESHOLDS = {
    "excellent": 1000,
    "good": 500,
    "average": 100,
    "minimum": 50,
}

# 变体数量阈值
VARIANT_THRESHOLDS = {
    "optimal_min": 3,
    "optimal_max": 8,
    "too_many": 15,
}

# 图片数量阈值
IMAGE_THRESHOLDS = {
    "excellent": 8,
    "good": 5,
    "minimum": 3,
}

# 默认选品参数
DEFAULT_SELECTION_PARAMS = {
    "top_n": 10,
    "min_score": 60,
    "max_price": None,
    "min_rating": 4.0,
    "min_reviews": 50,
    "risk_levels": ["LOW", "MEDIUM"],  # 允许的风险等级
}
```

### 4.3 评分引擎 (scorer.py)

```python
# src/selection/scorer.py

"""商品评分引擎"""

import pandas as pd
from typing import Dict, Any
from dataclasses import dataclass

from .config import (
    SCORING_WEIGHTS,
    RATING_THRESHOLDS,
    PRICE_THRESHOLDS,
    REVIEW_THRESHOLDS,
    VARIANT_THRESHOLDS,
    IMAGE_THRESHOLDS,
)


@dataclass
class ScoreBreakdown:
    """评分明细"""
    rating: float
    price_competitiveness: float
    review_volume: float
    variant_diversity: float
    image_quality: float
    profit_margin: float
    total: float


class ProductScorer:
    """商品评分器"""
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        初始化评分器
        
        Args:
            weights: 自定义权重，默认使用配置文件中的权重
        """
        self.weights = weights or SCORING_WEIGHTS.copy()
    
    def calculate_score(self, product: Dict[str, Any]) -> ScoreBreakdown:
        """
        计算商品综合得分
        
        Args:
            product: 商品数据字典
        
        Returns:
            ScoreBreakdown: 各维度得分及总分
        """
        # 计算各维度得分
        rating_score = self._score_rating(product)
        price_score = self._score_price(product)
        review_score = self._score_reviews(product)
        variant_score = self._score_variants(product)
        image_score = self._score_images(product)
        profit_score = self._score_profit(product)
        
        # 计算加权总分
        total = (
            rating_score * self.weights["rating"] +
            price_score * self.weights["price_competitiveness"] +
            review_score * self.weights["review_volume"] +
            variant_score * self.weights["variant_diversity"] +
            image_score * self.weights["image_quality"] +
            profit_score * self.weights["profit_margin"]
        )
        
        return ScoreBreakdown(
            rating=round(rating_score, 2),
            price_competitiveness=round(price_score, 2),
            review_volume=round(review_score, 2),
            variant_diversity=round(variant_score, 2),
            image_quality=round(image_score, 2),
            profit_margin=round(profit_score, 2),
            total=round(total, 2)
        )
    
    def _score_rating(self, product: Dict) -> float:
        """
        评分得分
        
        规则:
        - 4.8+ : 100分
        - 4.5-4.8 : 80-100分 (线性)
        - 4.0-4.5 : 60-80分 (线性)
        - 3.5-4.0 : 40-60分 (线性)
        - <3.5 : 0-40分 (线性)
        """
        rating = self._extract_rating(product.get("rating", 0))
        
        if rating >= RATING_THRESHOLDS["excellent"]:
            return 100
        elif rating >= RATING_THRESHOLDS["good"]:
            return 80 + (rating - 4.5) * (100 - 80) / (4.8 - 4.5)
        elif rating >= RATING_THRESHOLDS["average"]:
            return 60 + (rating - 4.0) * (80 - 60) / (4.5 - 4.0)
        elif rating >= RATING_THRESHOLDS["poor"]:
            return 40 + (rating - 3.5) * (60 - 40) / (4.0 - 3.5)
        else:
            return max(0, rating * 10)
    
    def _score_price(self, product: Dict) -> float:
        """
        价格竞争力得分
        
        规则:
        - 低于均价30% : 100分 (非常有竞争力)
        - 等于均价 : 80分
        - 高于均价30% : 60分
        - 高于均价50%+ : 40分
        """
        price = self._extract_price(product.get("price", 0))
        avg_price = product.get("category_avg_price", 30)  # 默认均价$30
        
        if avg_price <= 0:
            avg_price = 30
        
        ratio = price / avg_price
        
        if ratio <= PRICE_THRESHOLDS["very_competitive"]:
            return 100
        elif ratio <= PRICE_THRESHOLDS["competitive"]:
            return 80 + (1 - ratio) * 20 / 0.3
        elif ratio <= PRICE_THRESHOLDS["average"]:
            return 60 + (1.3 - ratio) * 20 / 0.3
        else:
            return max(20, 60 - (ratio - 1.3) * 40)
    
    def _score_reviews(self, product: Dict) -> float:
        """
        评论数量得分
        
        规则:
        - 1000+ : 100分 (销量已验证)
        - 500-1000 : 80-100分
        - 100-500 : 60-80分
        - 50-100 : 40-60分
        - <50 : 0-40分
        """
        reviews = self._extract_review_count(product)
        
        if reviews >= REVIEW_THRESHOLDS["excellent"]:
            return 100
        elif reviews >= REVIEW_THRESHOLDS["good"]:
            return 80 + (reviews - 500) * 20 / 500
        elif reviews >= REVIEW_THRESHOLDS["average"]:
            return 60 + (reviews - 100) * 20 / 400
        elif reviews >= REVIEW_THRESHOLDS["minimum"]:
            return 40 + (reviews - 50) * 20 / 50
        else:
            return min(40, reviews * 0.8)
    
    def _score_variants(self, product: Dict) -> float:
        """
        变体多样性得分
        
        规则:
        - 3-8个 : 100分 (最佳范围)
        - 8-15个 : 80分 (略多)
        - 1-3个 : 60分 (偏少)
        - 15+个 : 50分 (过多，管理复杂)
        - 0个 : 30分 (无变体)
        """
        variants = int(product.get("total_variants", 0))
        
        if VARIANT_THRESHOLDS["optimal_min"] <= variants <= VARIANT_THRESHOLDS["optimal_max"]:
            return 100
        elif VARIANT_THRESHOLDS["optimal_max"] < variants <= VARIANT_THRESHOLDS["too_many"]:
            return 80
        elif 0 < variants < VARIANT_THRESHOLDS["optimal_min"]:
            return 60
        elif variants > VARIANT_THRESHOLDS["too_many"]:
            return 50
        else:
            return 30
    
    def _score_images(self, product: Dict) -> float:
        """
        图片质量得分
        
        规则:
        - 8+张 : 100分
        - 5-8张 : 80分
        - 3-5张 : 60分
        - 1-3张 : 40分
        - 0张 : 0分
        """
        image_count = int(product.get("image_count", 0))
        
        if image_count >= IMAGE_THRESHOLDS["excellent"]:
            return 100
        elif image_count >= IMAGE_THRESHOLDS["good"]:
            return 80
        elif image_count >= IMAGE_THRESHOLDS["minimum"]:
            return 60
        elif image_count > 0:
            return 40
        else:
            return 0
    
    def _score_profit(self, product: Dict) -> float:
        """
        预估利润空间得分
        
        规则:
        - 利润率 50%+ : 100分
        - 利润率 30-50% : 80分
        - 利润率 20-30% : 60分
        - 利润率 10-20% : 40分
        - 利润率 <10% : 20分
        
        注：利润率 = (售价 - 成本 - 运费 - 平台费) / 售价
        """
        price = self._extract_price(product.get("price", 0))
        
        if price <= 0:
            return 0
        
        # 预估成本结构
        # - 采购成本: 约40%售价
        # - 运费: 约$5-10
        # - Amazon平台费: 约15%
        estimated_cost = price * 0.4
        shipping = 7 if price < 30 else 10
        platform_fee = price * 0.15
        
        profit = price - estimated_cost - shipping - platform_fee
        profit_margin = (profit / price) * 100
        
        if profit_margin >= 50:
            return 100
        elif profit_margin >= 30:
            return 80
        elif profit_margin >= 20:
            return 60
        elif profit_margin >= 10:
            return 40
        else:
            return max(0, 20 + profit_margin)
    
    # ========== 辅助方法 ==========
    
    def _extract_rating(self, rating_value: Any) -> float:
        """从各种格式提取评分数值"""
        if isinstance(rating_value, (int, float)):
            return float(rating_value)
        
        # 处理字符串格式 "4.7 out of 5 stars"
        import re
        if isinstance(rating_value, str):
            match = re.search(r'([\d.]+)', rating_value)
            if match:
                return float(match.group(1))
        
        return 0.0
    
    def _extract_price(self, price_value: Any) -> float:
        """从各种格式提取价格数值"""
        if isinstance(price_value, (int, float)):
            return float(price_value)
        
        # 处理字符串格式 "$29.99"
        import re
        if isinstance(price_value, str):
            match = re.search(r'([\d.]+)', price_value.replace(',', ''))
            if match:
                return float(match.group(1))
        
        return 0.0
    
    def _extract_review_count(self, product: Dict) -> int:
        """提取评论数量"""
        # 尝试多个可能的字段
        for field in ["review_count", "total_reviews", "reviews"]:
            value = product.get(field)
            if value:
                if isinstance(value, (int, float)):
                    return int(value)
                if isinstance(value, str):
                    import re
                    match = re.search(r'([\d,]+)', value)
                    if match:
                        return int(match.group(1).replace(',', ''))
        
        return 0


def score_dataframe(df: pd.DataFrame, weights: Dict = None) -> pd.DataFrame:
    """
    为整个 DataFrame 计算评分
    
    Args:
        df: 商品数据 DataFrame
        weights: 自定义权重
    
    Returns:
        添加了评分列的 DataFrame
    """
    scorer = ProductScorer(weights)
    
    scores = []
    for _, row in df.iterrows():
        product = row.to_dict()
        breakdown = scorer.calculate_score(product)
        scores.append({
            "score_rating": breakdown.rating,
            "score_price": breakdown.price_competitiveness,
            "score_reviews": breakdown.review_volume,
            "score_variants": breakdown.variant_diversity,
            "score_images": breakdown.image_quality,
            "score_profit": breakdown.profit_margin,
            "total_score": breakdown.total,
        })
    
    scores_df = pd.DataFrame(scores)
    return pd.concat([df.reset_index(drop=True), scores_df], axis=1)
```

### 4.4 风险评估器 (risk_assessor.py)

```python
# src/selection/risk_assessor.py

"""商品风险评估器"""

from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    """风险等级"""
    LOW = "低风险"
    MEDIUM = "中风险"
    HIGH = "高风险"


@dataclass
class RiskAssessment:
    """风险评估结果"""
    level: RiskLevel
    score: int  # 风险分数 0-100，越高越危险
    positive_signals: List[str]  # 积极信号
    warnings: List[str]  # 警告信号
    recommendation: str  # 推荐建议


class RiskAssessor:
    """风险评估器"""
    
    # 积极信号规则: (条件函数, 信号描述, 加分)
    POSITIVE_RULES = [
        (lambda p: p.get("rating_num", 0) >= 4.5, "✅ 高评分 (≥4.5)", 10),
        (lambda p: p.get("rating_num", 0) >= 4.8, "✅ 优秀评分 (≥4.8)", 15),
        (lambda p: p.get("review_count", 0) >= 100, "✅ 评论充足 (≥100)", 10),
        (lambda p: p.get("review_count", 0) >= 500, "✅ 评论丰富 (≥500)", 15),
        (lambda p: 3 <= p.get("total_variants", 0) <= 8, "✅ 变体数量适中", 10),
        (lambda p: p.get("image_count", 0) >= 5, "✅ 图片丰富 (≥5张)", 5),
        (lambda p: p.get("is_prime", False), "✅ Prime 商品", 5),
        (lambda p: p.get("is_fba", False), "✅ FBA 配送", 5),
        (lambda p: p.get("amazons_choice", False), "✅ Amazon's Choice", 10),
        (lambda p: p.get("coupon", None), "✅ 有优惠券", 5),
    ]
    
    # 风险信号规则: (条件函数, 警告描述, 风险等级, 扣分)
    RISK_RULES = [
        (lambda p: p.get("rating_num", 0) < 4.0, "⚠️ 评分偏低 (<4.0)", "HIGH", 20),
        (lambda p: p.get("rating_num", 0) < 3.5, "⚠️ 评分过低 (<3.5)", "HIGH", 30),
        (lambda p: p.get("review_count", 0) < 50, "⚠️ 评论较少 (<50)", "MEDIUM", 15),
        (lambda p: p.get("review_count", 0) < 10, "⚠️ 评论极少 (<10)", "HIGH", 25),
        (lambda p: p.get("total_variants", 0) > 15, "⚠️ 变体过多 (>15)", "MEDIUM", 10),
        (lambda p: p.get("total_variants", 0) == 0, "⚠️ 无变体选项", "LOW", 5),
        (lambda p: p.get("price_num", 0) > 50, "⚠️ 价格较高 (>$50)", "LOW", 5),
        (lambda p: p.get("price_num", 0) > 100, "⚠️ 高价商品 (>$100)", "MEDIUM", 10),
        (lambda p: p.get("stock_status", "") == "Out of Stock", "⚠️ 缺货中", "HIGH", 25),
        (lambda p: "Only" in str(p.get("stock_status", "")), "⚠️ 库存紧张", "MEDIUM", 10),
    ]
    
    def assess(self, product: Dict[str, Any]) -> RiskAssessment:
        """
        评估商品风险
        
        Args:
            product: 商品数据字典
        
        Returns:
            RiskAssessment: 风险评估结果
        """
        positive_signals = []
        warnings = []
        positive_score = 0
        risk_score = 0
        high_risk_count = 0
        
        # 检查积极信号
        for condition, description, score in self.POSITIVE_RULES:
            try:
                if condition(product):
                    positive_signals.append(description)
                    positive_score += score
            except Exception:
                pass
        
        # 检查风险信号
        for condition, description, level, score in self.RISK_RULES:
            try:
                if condition(product):
                    warnings.append(description)
                    risk_score += score
                    if level == "HIGH":
                        high_risk_count += 1
            except Exception:
                pass
        
        # 计算最终风险分数 (0-100)
        final_risk_score = max(0, min(100, risk_score - positive_score // 2))
        
        # 确定风险等级
        if high_risk_count >= 2 or final_risk_score >= 50:
            level = RiskLevel.HIGH
            recommendation = "❌ 不推荐：存在多个高风险因素"
        elif high_risk_count >= 1 or final_risk_score >= 30:
            level = RiskLevel.MEDIUM
            recommendation = "⚡ 谨慎考虑：存在一定风险，建议进一步调研"
        else:
            level = RiskLevel.LOW
            recommendation = "✅ 推荐选择：风险较低，可优先考虑"
        
        return RiskAssessment(
            level=level,
            score=final_risk_score,
            positive_signals=positive_signals,
            warnings=warnings,
            recommendation=recommendation
        )


def assess_dataframe(df) -> Tuple:
    """
    为整个 DataFrame 评估风险
    
    Returns:
        (risk_levels, risk_scores, positive_signals, warnings)
    """
    assessor = RiskAssessor()
    
    results = []
    for _, row in df.iterrows():
        product = row.to_dict()
        assessment = assessor.assess(product)
        results.append({
            "risk_level": assessment.level.value,
            "risk_score": assessment.score,
            "positive_signals": " | ".join(assessment.positive_signals),
            "warnings": " | ".join(assessment.warnings),
            "recommendation": assessment.recommendation,
        })
    
    return pd.DataFrame(results)
```

### 4.5 选品器 (selector.py)

```python
# src/selection/selector.py

"""自动选品器"""

import json
import pandas as pd
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import os

from .scorer import ProductScorer, ScoreBreakdown
from .risk_assessor import RiskAssessor, RiskLevel
from .config import DEFAULT_SELECTION_PARAMS


@dataclass
class ProductRecommendation:
    """商品推荐结果"""
    # 基本信息
    asin: str
    title: str
    price: float
    rating: float
    review_count: int
    total_variants: int
    image_count: int
    url: str
    
    # 评分信息
    total_score: float
    score_breakdown: Dict[str, float]
    
    # 风险信息
    risk_level: str
    risk_score: int
    positive_signals: List[str]
    warnings: List[str]
    
    # 推荐信息
    recommendation: str
    rank: int


class AutoProductSelector:
    """自动选品器"""
    
    def __init__(self, csv_path: str):
        """
        初始化选品器
        
        Args:
            csv_path: 商品数据 CSV 文件路径
        """
        self.csv_path = csv_path
        self.df = self._load_and_preprocess()
        self.scorer = ProductScorer()
        self.assessor = RiskAssessor()
    
    def _load_and_preprocess(self) -> pd.DataFrame:
        """加载并预处理数据"""
        df = pd.read_csv(self.csv_path)
        
        # 提取数值型字段
        if "price" in df.columns:
            df["price_num"] = df["price"].astype(str).str.replace(r"[\$,]", "", regex=True)
            df["price_num"] = pd.to_numeric(df["price_num"], errors="coerce").fillna(0)
        
        if "rating" in df.columns:
            df["rating_num"] = df["rating"].astype(str).str.extract(r"([\d.]+)")[0]
            df["rating_num"] = pd.to_numeric(df["rating_num"], errors="coerce").fillna(0)
        
        for col in ["total_variants", "image_count", "review_count"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        
        return df
    
    def select(
        self,
        top_n: int = None,
        min_score: float = None,
        max_price: float = None,
        min_rating: float = None,
        min_reviews: int = None,
        allowed_risk_levels: List[str] = None,
    ) -> List[ProductRecommendation]:
        """
        执行选品
        
        Args:
            top_n: 返回前 N 个商品
            min_score: 最低综合得分
            max_price: 最高价格
            min_rating: 最低评分
            min_reviews: 最少评论数
            allowed_risk_levels: 允许的风险等级
        
        Returns:
            排序后的推荐列表
        """
        # 使用默认参数
        params = DEFAULT_SELECTION_PARAMS.copy()
        params.update({k: v for k, v in locals().items() if v is not None and k != 'self'})
        
        recommendations = []
        
        for _, row in self.df.iterrows():
            product = row.to_dict()
            
            # 1. 基础过滤
            if params.get("max_price") and product.get("price_num", 0) > params["max_price"]:
                continue
            if params.get("min_rating") and product.get("rating_num", 0) < params["min_rating"]:
                continue
            if params.get("min_reviews") and product.get("review_count", 0) < params["min_reviews"]:
                continue
            
            # 2. 计算评分
            score_breakdown = self.scorer.calculate_score(product)
            
            if score_breakdown.total < params.get("min_score", 0):
                continue
            
            # 3. 评估风险
            assessment = self.assessor.assess(product)
            
            if params.get("allowed_risk_levels"):
                if assessment.level.value not in params["allowed_risk_levels"]:
                    continue
            
            # 4. 构建推荐结果
            recommendation = ProductRecommendation(
                asin=product.get("asin", ""),
                title=product.get("title", ""),
                price=product.get("price_num", 0),
                rating=product.get("rating_num", 0),
                review_count=int(product.get("review_count", 0)),
                total_variants=int(product.get("total_variants", 0)),
                image_count=int(product.get("image_count", 0)),
                url=product.get("url", ""),
                total_score=score_breakdown.total,
                score_breakdown={
                    "rating": score_breakdown.rating,
                    "price": score_breakdown.price_competitiveness,
                    "reviews": score_breakdown.review_volume,
                    "variants": score_breakdown.variant_diversity,
                    "images": score_breakdown.image_quality,
                    "profit": score_breakdown.profit_margin,
                },
                risk_level=assessment.level.value,
                risk_score=assessment.score,
                positive_signals=assessment.positive_signals,
                warnings=assessment.warnings,
                recommendation=assessment.recommendation,
                rank=0,  # 稍后设置
            )
            
            recommendations.append(recommendation)
        
        # 5. 排序
        recommendations.sort(key=lambda x: x.total_score, reverse=True)
        
        # 6. 设置排名并截取
        for i, rec in enumerate(recommendations[:params.get("top_n", 10)], 1):
            rec.rank = i
        
        return recommendations[:params.get("top_n", 10)]
    
    def generate_report(
        self,
        recommendations: List[ProductRecommendation],
        output_format: str = "text"
    ) -> str:
        """
        生成选品报告
        
        Args:
            recommendations: 推荐列表
            output_format: 输出格式 (text/json)
        
        Returns:
            报告内容
        """
        if output_format == "json":
            return json.dumps(
                [asdict(rec) for rec in recommendations],
                ensure_ascii=False,
                indent=2
            )
        
        # 文本报告
        lines = []
        lines.append("=" * 70)
        lines.append("🎯 自动化选品报告")
        lines.append("=" * 70)
        lines.append(f"📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"📊 数据来源: {self.csv_path}")
        lines.append(f"🔢 商品总数: {len(self.df)}")
        lines.append(f"✅ 推荐数量: {len(recommendations)}")
        lines.append("")
        
        for rec in recommendations:
            lines.append("-" * 70)
            lines.append(f"🏆 #{rec.rank}  {rec.title[:60]}...")
            lines.append(f"   ASIN: {rec.asin}")
            lines.append(f"   💰 价格: ${rec.price:.2f}  ⭐ 评分: {rec.rating}  📝 评论: {rec.review_count}")
            lines.append(f"   🎨 变体: {rec.total_variants}个  🖼️ 图片: {rec.image_count}张")
            lines.append(f"   📊 综合得分: {rec.total_score:.1f}/100")
            lines.append(f"   🎯 风险等级: {rec.risk_level} (风险分: {rec.risk_score})")
            
            if rec.positive_signals:
                lines.append(f"   ✅ 优势:")
                for signal in rec.positive_signals[:3]:
                    lines.append(f"      {signal}")
            
            if rec.warnings:
                lines.append(f"   ⚠️ 注意:")
                for warning in rec.warnings[:3]:
                    lines.append(f"      {warning}")
            
            lines.append(f"   💡 建议: {rec.recommendation}")
        
        lines.append("")
        lines.append("=" * 70)
        lines.append("报告结束")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def save_report(
        self,
        recommendations: List[ProductRecommendation],
        output_dir: str = "output/reports",
        formats: List[str] = ["text", "json"]
    ) -> Dict[str, str]:
        """
        保存报告到文件
        
        Args:
            recommendations: 推荐列表
            output_dir: 输出目录
            formats: 输出格式列表
        
        Returns:
            保存的文件路径字典
        """
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files = {}
        
        if "text" in formats:
            text_path = os.path.join(output_dir, f"report_{timestamp}.txt")
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(self.generate_report(recommendations, "text"))
            saved_files["text"] = text_path
        
        if "json" in formats:
            json_path = os.path.join(output_dir, f"report_{timestamp}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                f.write(self.generate_report(recommendations, "json"))
            saved_files["json"] = json_path
        
        return saved_files


# ========== 便捷函数 ==========

def quick_select(csv_path: str, top_n: int = 10) -> List[ProductRecommendation]:
    """
    快速选品（使用默认参数）
    
    Args:
        csv_path: CSV 文件路径
        top_n: 返回前 N 个
    
    Returns:
        推荐列表
    """
    selector = AutoProductSelector(csv_path)
    return selector.select(top_n=top_n)


def print_recommendations(recommendations: List[ProductRecommendation]):
    """打印推荐结果"""
    for rec in recommendations:
        print(f"\n#{rec.rank} {rec.title[:50]}...")
        print(f"   得分: {rec.total_score:.1f} | 风险: {rec.risk_level}")
        print(f"   价格: ${rec.price:.2f} | 评分: {rec.rating}")
```

### 4.6 模块初始化 (__init__.py)

```python
# src/selection/__init__.py

"""自动化选品模块"""

from .scorer import ProductScorer, ScoreBreakdown, score_dataframe
from .risk_assessor import RiskAssessor, RiskLevel, RiskAssessment, assess_dataframe
from .selector import (
    AutoProductSelector,
    ProductRecommendation,
    quick_select,
    print_recommendations,
)
from .config import (
    SCORING_WEIGHTS,
    DEFAULT_SELECTION_PARAMS,
)

__all__ = [
    # 评分器
    "ProductScorer",
    "ScoreBreakdown",
    "score_dataframe",
    
    # 风险评估
    "RiskAssessor",
    "RiskLevel",
    "RiskAssessment",
    "assess_dataframe",
    
    # 选品器
    "AutoProductSelector",
    "ProductRecommendation",
    "quick_select",
    "print_recommendations",
    
    # 配置
    "SCORING_WEIGHTS",
    "DEFAULT_SELECTION_PARAMS",
]
```

---

## 五、定时任务

### 5.1 调度器 (scheduler.py)

```python
# scheduler.py

"""
自动化选品调度器
支持定时执行爬取和选品任务
"""

import schedule
import time
import logging
from datetime import datetime
from typing import Optional
import subprocess
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.selection import AutoProductSelector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("output/scheduler.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SelectionScheduler:
    """选品任务调度器"""
    
    def __init__(
        self,
        csv_path: str = "output/amazon_products.csv",
        pages: int = 2,
        products: int = 20,
        top_n: int = 10,
    ):
        self.csv_path = csv_path
        self.pages = pages
        self.products = products
        self.top_n = top_n
    
    def run_crawler(self):
        """运行爬虫"""
        logger.info(f"🕷️ 开始爬取数据: {self.pages} 页, 每页 {self.products} 个商品")
        
        try:
            result = subprocess.run(
                [
                    sys.executable, "main.py",
                    "--pages", str(self.pages),
                    "--products", str(self.products),
                    "--headless",
                ],
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )
            
            if result.returncode == 0:
                logger.info("✅ 爬取完成")
                return True
            else:
                logger.error(f"❌ 爬取失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ 爬取超时")
            return False
        except Exception as e:
            logger.error(f"❌ 爬取异常: {e}")
            return False
    
    def run_selection(self):
        """运行选品分析"""
        logger.info("🎯 开始选品分析...")
        
        try:
            selector = AutoProductSelector(self.csv_path)
            recommendations = selector.select(
                top_n=self.top_n,
                min_score=60,
                min_rating=4.0,
                allowed_risk_levels=["低风险", "中风险"]
            )
            
            # 保存报告
            saved_files = selector.save_report(recommendations)
            
            logger.info(f"✅ 选品完成: {len(recommendations)} 个推荐商品")
            
            # 打印简要结果
            for rec in recommendations[:5]:
                logger.info(f"   #{rec.rank} {rec.title[:40]}... - 得分: {rec.total_score:.1f}")
            
            return recommendations
            
        except FileNotFoundError:
            logger.error(f"❌ 数据文件不存在: {self.csv_path}")
            return []
        except Exception as e:
            logger.error(f"❌ 选品分析异常: {e}")
            return []
    
    def job(self):
        """定时任务：爬取 + 选品"""
        logger.info("=" * 60)
        logger.info(f"📅 开始执行定时任务: {datetime.now()}")
        logger.info("=" * 60)
        
        # 1. 运行爬虫
        if self.run_crawler():
            # 2. 运行选品
            self.run_selection()
        
        logger.info("=" * 60)
        logger.info("✅ 定时任务完成")
        logger.info("=" * 60)
    
    def start(self, schedule_time: str = "08:00", interval_hours: Optional[int] = None):
        """
        启动调度器
        
        Args:
            schedule_time: 每天执行时间 (如 "08:00")
            interval_hours: 间隔小时数 (如设置则忽略 schedule_time)
        """
        if interval_hours:
            schedule.every(interval_hours).hours.do(self.job)
            logger.info(f"🕐 调度器已启动: 每 {interval_hours} 小时执行一次")
        else:
            schedule.every().day.at(schedule_time).do(self.job)
            logger.info(f"🕐 调度器已启动: 每天 {schedule_time} 执行")
        
        logger.info("按 Ctrl+C 停止...")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("👋 调度器已停止")


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="自动化选品调度器")
    parser.add_argument("--time", default="08:00", help="每天执行时间 (默认: 08:00)")
    parser.add_argument("--interval", type=int, help="间隔小时数")
    parser.add_argument("--pages", type=int, default=2, help="爬取页数")
    parser.add_argument("--products", type=int, default=20, help="每页商品数")
    parser.add_argument("--top-n", type=int, default=10, help="推荐商品数")
    parser.add_argument("--run-now", action="store_true", help="立即执行一次")
    
    args = parser.parse_args()
    
    scheduler = SelectionScheduler(
        pages=args.pages,
        products=args.products,
        top_n=args.top_n
    )
    
    if args.run_now:
        # 立即执行一次
        scheduler.job()
    else:
        # 启动调度器
        scheduler.start(
            schedule_time=args.time,
            interval_hours=args.interval
        )


if __name__ == "__main__":
    main()
```

### 5.2 使用方法

```bash
# 立即执行一次
python scheduler.py --run-now

# 每天早上8点执行
python scheduler.py --time 08:00

# 每6小时执行一次
python scheduler.py --interval 6

# 自义参数
python scheduler.py --pages 3 --products 30 --top-n 15 --time 09:00
```

---

## 六、仪表盘集成

### 6.1 添加智能选品 Tab

在 `dashboard/app.py` 中添加新的 Tab：

```python
# 在 st.tabs 中添加新 Tab
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 价格分析",
    "⭐ 评分分析",
    "🎨 变体分析",
    "🎯 选品建议",
    "🤖 智能选品",  # 新增
    "🖼️ 图片展示",
    "📋 数据表格"
])

# 智能选品 Tab
with tab5:
    render_smart_selection(filtered_df)
```

### 6.2 智能选品组件

```python
def render_smart_selection(df):
    """渲染智能选品界面"""
    from src.selection import AutoProductSelector, ProductScorer
    
    st.subheader("🤖 AI 智能选品")
    
    # 参数配置
    with st.expander("⚙️ 选品参数配置", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            top_n = st.slider("推荐数量", 5, 20, 10)
            min_score = st.slider("最低得分", 0, 100, 60)
        
        with col2:
            max_price = st.number_input("最高价格 ($)", 0, 500, 50)
            min_rating = st.slider("最低评分", 0.0, 5.0, 4.0, 0.1)
        
        with col3:
            min_reviews = st.number_input("最少评论数", 0, 1000, 50)
            allow_medium_risk = st.checkbox("允许中风险商品", value=True)
    
    # 权重配置
    st.write("**📊 评分权重调整**")
    weights_col1, weights_col2, weights_col3 = st.columns(3)
    
    with weights_col1:
        w_rating = st.slider("评分权重", 0.0, 0.5, 0.30, 0.05)
        w_price = st.slider("价格权重", 0.0, 0.5, 0.20, 0.05)
    
    with weights_col2:
        w_reviews = st.slider("评论权重", 0.0, 0.5, 0.15, 0.05)
        w_variants = st.slider("变体权重", 0.0, 0.5, 0.15, 0.05)
    
    with weights_col3:
        w_images = st.slider("图片权重", 0.0, 0.5, 0.10, 0.05)
        w_profit = st.slider("利润权重", 0.0, 0.5, 0.10, 0.05)
    
    custom_weights = {
        "rating": w_rating,
        "price_competitiveness": w_price,
        "review_volume": w_reviews,
        "variant_diversity": w_variants,
        "image_quality": w_images,
        "profit_margin": w_profit,
    }
    
    # 执行选品
    if st.button("🚀 开始智能选品", type="primary"):
        with st.spinner("正在分析商品..."):
            # 保存临时 CSV
            temp_csv = "output/temp_for_selection.csv"
            df.to_csv(temp_csv, index=False)
            
            # 执行选品
            selector = AutoProductSelector(temp_csv)
            selector.scorer = ProductScorer(weights=custom_weights)
            
            risk_levels = ["低风险"]
            if allow_medium_risk:
                risk_levels.append("中风险")
            
            recommendations = selector.select(
                top_n=top_n,
                min_score=min_score,
                max_price=max_price if max_price > 0 else None,
                min_rating=min_rating,
                min_reviews=min_reviews,
                allowed_risk_levels=risk_levels
            )
        
        if recommendations:
            st.success(f"✅ 找到 {len(recommendations)} 个推荐商品")
            
            # 显示结果
            for rec in recommendations:
                with st.expander(
                    f"#{rec.rank} {rec.title[:50]}... | 得分: {rec.total_score:.1f} | {rec.risk_level}",
                    expanded=(rec.rank <= 3)
                ):
                    # 基本信息列
                    info_col1, info_col2, info_col3 = st.columns(3)
                    
                    with info_col1:
                        st.metric("💰 价格", f"${rec.price:.2f}")
                        st.metric("⭐ 评分", f"{rec.rating}")
                        st.metric("📝 评论", f"{rec.review_count}")
                    
                    with info_col2:
                        st.metric("🎨 变体", f"{rec.total_variants}个")
                        st.metric("🖼️ 图片", f"{rec.image_count}张")
                        st.metric("🎯 风险", rec.risk_level)
                    
                    with info_col3:
                        # 评分明细
                        st.write("**得分明细:**")
                        for key, value in rec.score_breakdown.items():
                            st.progress(int(value))
                            st.caption(f"{key}: {value:.1f}")
                    
                    # 信号显示
                    signal_col1, signal_col2 = st.columns(2)
                    
                    with signal_col1:
                        if rec.positive_signals:
                            st.write("**✅ 优势:**")
                            for signal in rec.positive_signals:
                                st.write(f"  {signal}")
                    
                    with signal_col2:
                        if rec.warnings:
                            st.write("**⚠️ 注意:**")
                            for warning in rec.warnings:
                                st.write(f"  {warning}")
                    
                    # 建议
                    st.info(f"💡 {rec.recommendation}")
                    
                    # 链接
                    st.markdown(f"[🔗 查看商品详情]({rec.url})")
            
            # 下载报告
            report_json = selector.generate_report(recommendations, "json")
            st.download_button(
                "📥 下载选品报告 (JSON)",
                report_json,
                file_name=f"selection_report_{datetime.now():%Y%m%d}.json",
                mime="application/json"
            )
        
        else:
            st.warning("⚠️ 未找到符合条件的商品，请调整筛选参数")
```

---

## 七、部署方案

### 7.1 本地运行

```bash
# 安装依赖
uv sync

# 启动调度器
python scheduler.py --time 08:00

# 或启动仪表盘
bash run_dashboard.sh
```

### 7.2 Docker 部署

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Playwright
RUN playwright install chromium
RUN playwright install-deps

# 复制代码
COPY . .

# 创建输出目录
RUN mkdir -p output/reports

# 启动命令
CMD ["python", "scheduler.py", "--time", "08:00"]
```

### 7.3 Systemd 服务 (Linux)

```ini
# /etc/systemd/system/amazon-selector.service

[Unit]
Description=Amazon Auto Product Selector
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/python_crawler
ExecStart=/usr/bin/python scheduler.py --time 08:00
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 启用服务
sudo systemctl enable amazon-selector
sudo systemctl start amazon-selector
```

---

## 八、总结

### 8.1 已实现功能

| 功能 | 状态 | 文件 |
|------|------|------|
| 多维度评分引擎 | ✅ | `src/selection/scorer.py` |
| 风险评估器 | ✅ | `src/selection/risk_assessor.py` |
| 自动选品器 | ✅ | `src/selection/selector.py` |
| 定时调度器 | ✅ | `scheduler.py` |
| 仪表盘集成 | 📝 | `dashboard/app.py` |

### 8.2 后续扩展方向

1. **机器学习模型** - 基于历史数据训练销量预测模型
2. **竞品监控** - 定时追踪竞品价格变化
3. **利润计算器** - 更精准的成本和利润估算
4. **多平台支持** - 支持 eBay、Walmart 等平台
5. **API 接口** - 提供 REST API 供其他系统调用

---

*文档版本: v1.0*
*创建时间: 2026-03-12*
