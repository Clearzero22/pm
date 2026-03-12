# 选品系统模块

> **跨境电商全工作流系统** - Amazon 竞品分析与利润计算

**优先级**: ⭐⭐⭐⭐⭐
**预计工作量**: 2-3 周

---

## 目录

1. [模块概述](#模块概述)
2. [功能设计](#功能设计)
3. [数据采集](#数据采集)
4. [分析算法](#分析算法)
5. [API 设计](#api-设计)

---

## 模块概述

### 业务价值

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         选品系统业务价值                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  传统选品方式:                                                           │
│  • 手动搜索 Amazon 产品                                                │
│  • 手动记录竞品信息                                                    │
│  • Excel 计算利润                                                      │
│  • 凭经验判断机会                                                      │
│  • 时间成本: 2-4 小时/产品                                             │
│                                                                         │
│  AI 选品方式:                                                           │
│  • 自动爬取 Amazon 数据                                                │
│  • 实时竞品价格监控                                                    │
│  • 自动计算利润率                                                      │
│  • 数据驱动决策                                                        │
│  • 时间成本: 5 分钟/产品                                              │
│                                                                         │
│  效率提升: 20-30x                                                       │
│  准确率提升: 50%+                                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 核心功能

| 功能 | 说明 | 优先级 |
|------|------|--------|
| **竞品分析** | 分析竞品价格、评分、评论 | ⭐⭐⭐⭐⭐ |
| **趋势预测** | 基于历史数据预测销量 | ⭐⭐⭐⭐ |
| **利润计算** | 自动计算 FBA 费用、佣金、利润 | ⭐⭐⭐⭐⭐ |
| **机会评分** | 综合评估产品潜力 | ⭐⭐⭐⭐ |
| **供应商对接** | 1688/Alibaba 价格对比 | ⭐⭐⭐ |

---

## 功能设计

### 1. 竞品分析

#### 分析维度

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          竞品分析维度                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  市场维度:                                                               │
│  • 搜索量 (Search Volume)        - 月搜索量                          │
│  • 竞争度 (Competition Level)     - 卖家数量                          │
│  • 价格区间 (Price Range)          - 最低/最高/平均                   │
│  • 品牌集中度 (Brand Dominance)    - Top 品牌份额                     │
│                                                                         │
│  产品维度:                                                               │
│  • 平均评分 (Average Rating)      - 1-5 星                           │
│  • 评论数量 (Review Count)         - 总评论数                          │
│  • 变体数量 (Variation Count)      - 颜色/尺寸数量                    │
│  • 上架时长 (Listing Age)          - 上架时间                         │
│                                                                         │
│  销售维度:                                                               │
│  • 预估销量 (Estimated Sales)     - 月销量                          │
│  • 销售排名 (Best Sellers Rank)   - 类目排名                         │
│  • 季节性 (Seasonality)             - 季节波动                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 代码实现

```python
# backend/services/selection/competitor_analysis.py

from typing import Dict, List
from decimal import Decimal
import asyncio

class CompetitorAnalyzer:
    """竞品分析器"""

    def __init__(self, crawler, cache):
        self.crawler = crawler
        self.cache = cache

    async def analyze_competitor(
        self,
        asin: str,
        marketplace: str = "US"
    ) -> Dict:
        """
        分析竞品

        Returns:
            {
                "asin": "B0BZYCJK89",
                "title": "Wireless Mouse",
                "price": {
                    "current": 29.99,
                    "min": 24.99,
                    "max": 39.99,
                    "avg": 29.50
                },
                "rating": {
                    "average": 4.5,
                    "count": 1500,
                    "distribution": {...}
                },
                "competition": {
                    "total_sellers": 45,
                    "top_seller": {...}
                },
                "metrics": {
                    "bsr_rank": 1234,
                    "estimated_sales": 500,
                    "listing_age_days": 365
                },
                "opportunity_score": 75
            }
        """
        # 1. 获取产品基本信息
        product_info = await self.crawler.get_product_info(asin, marketplace)

        # 2. 获取价格信息
        price_data = await self._analyze_pricing(asin, marketplace)

        # 3. 获取评分信息
        rating_data = await self._analyze_ratings(asin)

        # 4. 分析竞争情况
        competition_data = await self._analyze_competition(asin, marketplace)

        # 5. 获取销售指标
        metrics_data = await self._get_sales_metrics(asin, marketplace)

        # 6. 计算机会评分
        opportunity_score = self._calculate_opportunity_score({
            "price": price_data,
            "rating": rating_data,
            "competition": competition_data,
            "metrics": metrics_data
        })

        return {
            "asin": asin,
            "title": product_info.get("title"),
            "price": price_data,
            "rating": rating_data,
            "competition": competition_data,
            "metrics": metrics_data,
            "opportunity_score": opportunity_score
        }

    async def _analyze_pricing(self, asin: str, marketplace: str) -> Dict:
        """分析价格"""
        # 获取所有卖家报价
        offers = await self.crawler.get_offers(asin, marketplace)

        prices = [Decimal(str(offer.get("price", "0"))) for offer in offers if offer.get("price")]

        if not prices:
            return {"current": 0, "min": 0, "max": 0, "avg": 0}

        return {
            "current": float(prices[0]),  # 最低价为当前价
            "min": float(min(prices)),
            "max": float(max(prices)),
            "avg": float(sum(prices) / len(prices)),
            "count": len(prices)
        }

    async def _analyze_ratings(self, asin: str) -> Dict:
        """分析评分"""
        reviews = await self.crawler.get_reviews(asin, limit=100)

        ratings = [float(review.get("rating", 0)) for review in reviews]

        if not ratings:
            return {"average": 0, "count": 0}

        # 评分分布
        distribution = {i: 0 for i in range(1, 6)}
        for r in ratings:
            distribution[int(r)] += 1

        return {
            "average": round(sum(ratings) / len(ratings), 2),
            "count": len(ratings),
            "distribution": distribution
        }

    async def _analyze_competition(self, asin: str, marketplace: str) -> Dict:
        """分析竞争情况"""
        # 搜索相似产品
        similar_products = await self.crawler.search_similar_products(asin, marketplace)

        # 按品牌分组
        brands = {}
        for product in similar_products:
            brand = product.get("brand", "Unknown")
            if brand not in brands:
                brands[brand] = []
            brands[brand].append(product)

        # 找出 Top 卖家
        sorted_brands = sorted(
            brands.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )

        return {
            "total_sellers": len(similar_products),
            "total_brands": len(brands),
            "top_seller": {
                "brand": sorted_brands[0][0],
                "count": len(sorted_brands[0][1]),
                "share": round(len(sorted_brands[0][1]) / len(similar_products) * 100, 2)
            }
        }

    def _calculate_opportunity_score(self, data: Dict) -> int:
        """计算机会评分 (0-100)"""
        score = 100

        # 价格竞争惩罚 (价格越接近，竞争越激烈)
        price_range = data["price"]["max"] - data["price"]["min"]
        if price_range < 10:
            score -= 20
        elif price_range > 50:
            score += 10

        # 评分奖励 (高分产品机会小)
        avg_rating = data["rating"]["average"]
        if avg_rating >= 4.5:
            score -= 15  # 高分产品竞争大
        elif avg_rating < 3.5:
            score -= 20  # 低分产品难做
        elif 3.5 <= avg_rating < 4.3:
            score += 10  # 适中评分最佳

        # 竞争度惩罚
        total_sellers = data["competition"]["total_sellers"]
        if total_sellers > 100:
            score -= 25
        elif total_sellers < 20:
            score += 15

        # 销量奖励
        estimated_sales = data["metrics"]["estimated_sales"]
        if estimated_sales > 1000:
            score += 20
        elif estimated_sales > 500:
            score += 10

        # 限制范围
        return max(0, min(100, score))
```

### 2. 利润计算

#### 费用结构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Amazon 费用结构                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  售价 (Selling Price): $30.00                                          │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  扣减项目                                                       │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │  • Amazon 佣金 (Referral Fee): 15% × $30 = $4.50            │   │
│  │  • FBA 配送费 (Fulfillment Fee): $3.00                        │   │
│  │  • FBA 仓储费 (Storage Fee): $0.15/月                         │   │
│  │  • FBA 订单处理费 (Order Handling): $1.00                    │   │
│  │  • 广告费 (PPC): $3.00 (10% ACOS)                             │   │
│  │  • 退货准备金: 2% × $30 = $0.60                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                          总计: $12.25                                │
│                                                                         │
│  净收入 (Net Proceed): $30.00 - $12.25 = $17.75                      │
│                                                                         │
│  成本 (COGS): $10.00                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  • 产品成本: $8.00                                               │   │
│  │  • 海运费: $1.50                                                 │   │
│  │  • 清关费: $0.30                                                 │   │
│  │  • 其他: $0.20                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  净利润 (Net Profit): $17.75 - $10.00 = $7.75                            │
│  利润率 (ROI): 7.75 / 30 = 25.8%                                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 代码实现

```python
# backend/services/selection/profit_calculator.py

from typing import Dict, Optional
from decimal import Decimal
from datetime import date, timedelta

class ProfitCalculator:
    """利润计算器"""

    # Amazon 费率表 (2024)
    REFERRAL_FEES = {
        "8": 15.0,    # 8% 以下
        "15": 15.0,   # 8.01%-15%
        "20": 15.0,   # 15.01%-20%
        "25": 15.0,   # 20.01%-25%
        "30": 15.0,   # 25.01%-30%
        "35": 7.0,    # 30.01%-35%
        "40": 7.0,    # 35.01%-40%
        "45": 6.0,    # 40.01%-45%
        "50": 6.0,    # 45.01%-50%
        "55": 5.5,    # 50.01%-55%
        "60": 5.5,    # 55.01%-60%
        "70": 5.25,   # 60.01%-70%
        "75": 5.25,   # 70.01%-75%
        "100": 5.0,   # 75.01%-100%
        "over": 5.0   # > 100
    }

    FBA_FEES = {
        "standard": Decimal("3.00"),      # 标准尺寸
        "oversize": Decimal("5.50"),      # 超大尺寸
        "small": Decimal("2.50")          # 小件标准
    }

    def __init__(self, category_fees: Optional[Dict] = None):
        """
        初始化计算器

        Args:
            category_fees: 特殊类目费率 (如服装 17%)
        """
        self.category_fees = category_fees or {}

    def calculate_profit(
        self,
        selling_price: Decimal,
        product_cost: Decimal,
        shipping_cost: Decimal,
        monthly_sales: int = 100,
        package_size: str = "standard",
        category: Optional[str] = None,
        advertising_acos: float = 0.10
    ) -> Dict:
        """
        计算利润

        Args:
            selling_price: 售价
            product_cost: 产品成本
            shipping_cost: 海运费 (单位)
            monthly_sales: 月销量 (影响仓储费)
            package_size: 包装尺寸
            category: 产品类目
            advertising_acos: 广告销售占比

        Returns:
            利润分析报告
        """
        # 1. 计算 Amazon 佣金
        referral_fee = self._calculate_referral_fee(selling_price, category)

        # 2. FBA 费用
        fulfillment_fee = self.FBA_FEES.get(package_size, Decimal("3.00"))
        storage_fee = self._calculate_storage_fee(package_size, monthly_sales)
        order_handling = Decimal("1.00")

        # 3. 总费用
        amazon_fees = referral_fee + fulfillment_fee + storage_fee + order_handling

        # 4. 广告费
        advertising_cost = Decimal(selling_price) * Decimal(str(advertising_acos))

        # 5. 其他费用
        return_reserve = Decimal(selling_price) * Decimal("0.02")

        # 6. 净收入
        net_proceed = selling_price - amazon_fees - advertising_cost - return_reserve

        # 7. 总成本
        total_cost = product_cost + shipping_cost

        # 8. 净利润
        net_profit = net_proceed - total_cost

        # 9. 利润率
        roi = (net_profit / selling_price * 100) if selling_price > 0 else Decimal("0")

        return {
            "revenue": {
                "selling_price": float(selling_price),
                "net_proceed": float(net_proceed)
            },
            "costs": {
                "product": float(product_cost),
                "shipping": float(shipping_cost),
                "amazon_fees": float(amazon_fees),
                "advertising": float(advertising_cost),
                "total": float(total_cost + amazon_fees + advertising_cost + return_reserve)
            },
            "profit": {
                "net": float(net_profit),
                "roi": float(roi),
                "margin": float(net_profit / total_cost * 100) if total_cost > 0 else 0
            },
            "breakdown": {
                "referral_fee": float(referral_fee),
                "fulfillment_fee": float(fulfillment_fee),
                "storage_fee": float(storage_fee),
                "order_handling": float(order_handling),
                "return_reserve": float(return_reserve)
            }
        }

    def _calculate_referral_fee(
        self,
        price: Decimal,
        category: Optional[str] = None
    ) -> Decimal:
        """计算推荐费"""
        # 检查特殊类目
        if category and category in self.category_fees:
            return price * Decimal(str(self.category_fees[category] / 100))

        # 标准费率
        fee_tier = self._get_price_tier(price)
        fee_rate = self.REFERRAL_FEES[fee_tier]

        return price * Decimal(str(fee_rate / 100))

    def _get_price_tier(self, price: Decimal) -> str:
        """获取价格区间"""
        price_value = float(price)

        if price_value <= 8:
            return "8"
        elif price_value <= 15:
            return "15"
        elif price_value <= 20:
            return "20"
        elif price_value <= 25:
            return "25"
        elif price_value <= 30:
            return "30"
        elif price_value <= 35:
            return "35"
        elif price_value <= 40:
            return "40"
        elif price_value <= 45:
            return "45"
        elif price_value <= 50:
            return "50"
        elif price_value <= 55:
            return "55"
        elif price_value <= 60:
            return "60"
        elif price_value <= 70:
            return "70"
        elif price_value <= 75:
            return "75"
        else:
            return "over"

    def _calculate_storage_fee(
        self,
        package_size: str,
        monthly_sales: int
    ) -> Decimal:
        """计算仓储费"""
        # 2024 年 1 月费率
        storage_rates = {
            "standard": Decimal("0.83"),   # 每立方英尺/月
            "oversize": Decimal("0.83"),
            "small": Decimal("0.83"),
            "special": Decimal("0.53")     # 小件特殊
        }

        # 假设平均体积 0.1 立方英尺
        volume = Decimal("0.1")
        monthly_rate = storage_rates.get(package_size, Decimal("0.83"))

        # 按天计算 (假设平均库存周转天数 30 天)
        daily_rate = monthly_rate / 30

        # 年度库存周转次数
        turns = max(1, monthly_sales / 100)

        # 存储天数
        storage_days = 30 / turns

        return daily_rate * volume * Decimal(str(storage_days))
```

### 3. 趋势预测

```python
# backend/services/selection/trend_analyzer.py

from typing import Dict, List
from datetime import datetime, timedelta
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

class TrendAnalyzer:
    """趋势分析器"""

    def __init__(self):
        """初始化"""
        self.model = LinearRegression()

    async def predict_sales_trend(
        self,
        asin: str,
        months: int = 6,
        marketplace: str = "US"
    ) -> Dict:
        """
        预测销售趋势

        Returns:
            {
                "asin": "B0BZYCJK89",
                "historical": [
                    {"month": "2024-01", "sales": 100},
                    ...
                ],
                "forecast": [
                    {"month": "2024-07", "sales": 150},
                    ...
                ],
                "trend": "up",
                "seasonality": {},
                "confidence": 0.85
            }
        """
        # 1. 获取历史数据
        historical_data = await self._get_historical_sales(asin, months, marketplace)

        # 2. 分析季节性
        seasonality = self._analyze_seasonality(historical_data)

        # 3. 训练预测模型
        forecast = self._train_and_predict(historical_data, months)

        # 4. 计算趋势
        trend = self._determine_trend(forecast)

        return {
            "asin": asin,
            "historical": historical_data,
            "forecast": forecast,
            "trend": trend,
            "seasonality": seasonality,
            "confidence": 0.85  # 简化
        }

    async def _get_historical_sales(
        self,
        asin: str,
        months: int,
        marketplace: str
    ) -> List[Dict]:
        """获取历史销售数据"""
        # 从 Amazon API 或爬虫获取
        # 这里简化为模拟数据
        data = []
        base_sales = 100

        for i in range(months):
            month = datetime.now() - timedelta(days=30 * (months - i))
            # 添加随机波动
            sales = base_sales + int(np.random.normal(0, 20))

            data.append({
                "month": month.strftime("%Y-%m"),
                "sales": max(0, sales)
            })

        return data

    def _analyze_seasonality(self, data: List[Dict]) -> Dict:
        """分析季节性"""
        df = pd.DataFrame(data)
        df["month"] = pd.to_datetime(df["month"])
        df["month_num"] = df["month"].dt.month

        # 按月平均
        monthly_avg = df.groupby("month_num")["sales"].mean().to_dict()

        # 计算季节性系数
        overall_avg = df["sales"].mean()
        seasonality = {
            k: round(v / overall_avg, 2) if overall_avg > 0 else 1
            for k, v in monthly_avg.items()
        }

        return seasonality

    def _train_and_predict(
        self,
        historical: List[Dict],
        forecast_months: int
    ) -> List[Dict]:
        """训练模型并预测"""
        # 准备数据
        df = pd.DataFrame(historical)
        df["x"] = range(len(df))

        # 训练
        X = df[["x"]].values
        y = df["sales"].values
        self.model.fit(X, y)

        # 预测
        last_x = len(df) - 1
        forecast = []

        for i in range(1, forecast_months + 1):
            pred_x = np.array([[last_x + i]])
            pred_sales = self.model.predict(pred_x)[0]
            pred_sales = max(0, int(pred_sales))  # 不允许负数

            future_month = datetime.now() + timedelta(days=30 * i)
            forecast.append({
                "month": future_month.strftime("%Y-%m"),
                "sales": pred_sales,
                "type": "forecast"
            })

        return forecast

    def _determine_trend(self, forecast: List[Dict]) -> str:
        """判断趋势"""
        if len(forecast) < 2:
            return "stable"

        first_avg = np.mean([f["sales"] for f in forecast[:len(forecast)//2]])
        second_avg = np.mean([f["sales"] for f in forecast[len(forecast)//2:]])

        if second_avg > first_avg * 1.1:
            return "up"
        elif second_avg < first_avg * 0.9:
            return "down"
        else:
            return "stable"
```

### 4. 供应商对接

```python
# backend/services/selection/supplier_integration.py

class SupplierService:
    """供应商服务"""

    async def search_suppliers(
        self,
        keyword: str,
        min_price: float = 0,
        max_price: float = 1000
    ) -> List[Dict]:
        """
        搜索 1688 供应商

        Returns:
            [
                {
                    "title": "Product Title",
                    "supplier": "Supplier Name",
                    "price": 50.0,
                    "moq": 100,
                    "location": "Shenzhen",
                    "rating": 4.8,
                    "url": "https://..."
                }
            ]
        """
        # 实际实现需要爬取 1688 或使用 API
        # 这里返回模拟数据
        return [
            {
                "title": f"{keyword} Sample",
                "supplier": "Guangdong Electronics",
                "price": 50.0,
                "moq": 100,
                "location": "Shenzhen, Guangdong",
                "rating": 4.8,
                "url": "https://1688.com/..."
            }
        ]

    async def compare_profitability(
        self,
        amazon_price: float,
        supplier_price: float,
        shipping_cost: float
    ) -> Dict:
        """对比盈利能力"""
        calculator = ProfitCalculator()

        result = calculator.calculate_profit(
            selling_price=Decimal(str(amazon_price)),
            product_cost=Decimal(str(supplier_price)),
            shipping_cost=Decimal(str(shipping_cost))
        )

        return result
```

---

## API 设计

### 端点定义

```python
# backend/api/routes/selection.py

from fastapi import APIRouter, Query, BackgroundTasks
from typing import List, Optional

router = APIRouter(prefix="/api/v1/selection", tags=["Selection"])

@router.post("/analyze")
async def analyze_competitor(
    asin: str = Query(..., min_length=10, max_length=10),
    marketplace: str = Query("US")
):
    """
    分析竞品

    返回竞品的完整分析数据，包括价格、评分、竞争情况等
    """
    analyzer = CompetitorAnalyzer(crawler, cache)
    result = await analyzer.analyze_competitor(asin, marketplace)
    return result

@router.post("/profit-calculate")
async def calculate_profit(
    asin: str = Query(...),
    selling_price: float = Query(...),
    product_cost: float = Query(...),
    shipping_cost: float = Query(5.0),
    monthly_sales: int = Query(100),
    advertising_acos: float = Query(0.10)
):
    """
    计算利润

    基于 Amazon 费率计算 FBA 净利润
    """
    calculator = ProfitCalculator()
    result = calculator.calculate_profit(
        selling_price=Decimal(str(selling_price)),
        product_cost=Decimal(str(product_cost)),
        shipping_cost=Decimal(str(shipping_cost)),
        monthly_sales=monthly_sales,
        advertising_acos=advertising_acos
    )
    return result

@router.get("/trends")
async def get_trends(
    asin: str = Query(...),
    months: int = Query(6)
):
    """
    获取趋势预测

    基于历史数据预测未来销量趋势
    """
    analyzer = TrendAnalyzer()
    result = await analyzer.predict_sales_trend(asin, months)
    return result

@router.get("/opportunities")
async def find_opportunities(
    category: str = Query(...),
    min_profit: float = Query(20.0),
    max_competition: int = Query(50)
):
    """
    发现机会产品

    基于筛选条件找到高潜力产品
    """
    # 实现筛选逻辑
    pass
```

---

**预计工作量**: 2-3 周

| 阶段 | 任务 | 时间 |
|------|------|------|
| Week 1 | 竞品分析 + 利润计算 | 5 天 |
| Week 2 | 趋势预测 + 供应商对接 | 5 天 |
| Week 3 | API 开发 + 测试 | 5 天 |

---

**下一步**: 查看 [CUSTOMER_SERVICE_MODULE.md](./CUSTOMER_SERVICE_MODULE.md)
