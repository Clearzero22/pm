# 财务系统模块

> **跨境电商全工作流系统** - 收入、成本、利润分析

**优先级**: ⭐⭐⭐⭐
**预计工作量**: 2 周

---

## 目录

1. [模块概述](#模块概述)
2. [功能设计](#功能设计)
3. [数据处理](#数据处理)
4. [报表生成](#报表生成)
5. [API 设计](#api-设计)

---

## 模块概述

### 业务价值

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         财务系统业务价值                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  传统财务方式:                                                           │
│  • 手动记录 Excel                                                      │
│  • 无法实时统计                                                        │
│  • 报表生成慢 (周/月)                                                  │
│  • 数据易出错                                                          │
│                                                                         │
│  自动化财务系统:                                                         │
│  • 实时数据同步                                                        │
│  • 自动分类统计                                                        │
│  • 多维度分析                                                          │
│  • 可视化报表                                                          │
│                                                                         │
│  时间节省: 90%+                                                          │
│  准确率提升: 95%+                                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 核心功能

| 功能 | 说明 | 优先级 |
|------|------|--------|
| **收入统计** | 实时收入、按产品/市场 | ⭐⭐⭐⭐⭐ |
| **成本追踪** | 采购/物流/广告/平台费 | ⭐⭐⭐⭐⭐ |
| **利润分析** | 按产品/时间/市场 | ⭐⭐⭐⭐⭐ |
| **现金流** | 应收/应付、预测 | ⭐⭐⭐ |
| **财务报表** | 日报/周报/月报 | ⭐⭐⭐⭐ |

---

## 功能设计

### 1. 收入统计

#### 收入来源

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          收入来源分类                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  销售收入:                                                               │
│  • 产品销售收入 (商品订单)                                            │
│  • 运费收入 (买家承担)                                                 │
│                                                                         │
│  其他收入:                                                               │
│  • 退款补差收入                                                        │
│  • 促销补偿                                                            │
│                                                                         │
│  扣减:                                                                   │
│  • 退款金额                                                            │
│  • 取消订单                                                            │
│  │                                                                     │
│                                                                         │
│  净收入 = 销售收入 - 退款金额                                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 代码实现

```python
# backend/services/finance/revenue_tracker.py

from typing import Dict, List, Optional
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import func

class RevenueTracker:
    """收入追踪器"""

    async def get_daily_revenue(
        self,
        date: date,
        marketplace: str = None
    ) -> Dict:
        """
        获取指定日期的收入

        Returns:
            {
                "date": "2024-01-01",
                "gross_revenue": 5000.00,
                "refund_amount": -200.00,
                "net_revenue": 4800.00,
                "order_count": 150,
                "by_marketplace": {...}
            }
        """
        # 查询当日订单
        query = self.db.query(
            func.sum(orders.total),
            func.count(orders.id)
        ).filter(
            func.date(orders.order_date) == date
        )

        if marketplace:
            query = query.filter(orders.marketplace == marketplace)

        result = query.first()
        gross_revenue = result[0] or Decimal("0")
        order_count = result[1] or 0

        # 查询退款金额
        refund_query = self.db.query(
            func.sum(refunds.amount)
        ).filter(
            func.date(refunds.created_at) == date
        )
        refund_amount = refund_query.first()[0] or Decimal("0")

        net_revenue = gross_revenue - refund_amount

        # 按市场分组
        by_marketplace = await self._get_revenue_by_marketplace(date)

        return {
            "date": date.isoformat(),
            "gross_revenue": float(gross_revenue),
            "refund_amount": float(refund_amount),
            "net_revenue": float(net_revenue),
            "order_count": order_count,
            "by_marketplace": by_marketplace
        }

    async def get_revenue_trend(
        self,
        start_date: date,
        end_date: date,
        group_by: str = "day"
    ) -> List[Dict]:
        """
        获取收入趋势

        Args:
            start_date: 开始日期
            end_date: 结束日期
            group_by: 分组方式 (day/week/month)

        Returns:
            [
                {"date": "2024-01-01", "revenue": 1000, "orders": 50},
                {"date": "2024-01-02", "revenue": 1200, "orders": 55},
                ...
            ]
        """
        # 按日期分组
        if group_by == "day":
            date_trunc = func.date(orders.order_date)
        elif group_by == "week":
            date_trunc = func.date_trunc("week", orders.order_date)
        elif group_by == "month":
            date_trunc = func.date_trunc("month", orders.order_date)

        query = self.db.query(
            date_trunc.label("date"),
            func.sum(orders.total).label("revenue"),
            func.count(orders.id).label("orders")
        ).filter(
            func.date(orders.order_date) >= start_date,
            func.date(orders.order_date) <= end_date
        ).group_by("date").order_by("date")

        results = query.all()

        return [
            {
                "date": str(r.date),
                "revenue": float(r.revenue),
                "orders": r.orders
            }
            for r in results
        ]

    async def get_product_revenue_ranking(
        self,
        start_date: date,
        end_date: date,
        limit: int = 10
    ) -> List[Dict]:
        """
        获取产品收入排名

        Returns:
            [
                {"asin": "B0XXX", "title": "...", "revenue": 5000, "orders": 100},
                ...
            ]
        """
        query = self.db.query(
            products.asin,
            products.title,
            func.sum(order_items.total * order_items.quantity).label("revenue"),
            func.sum(order_items.quantity).label("orders")
        ).join(
            order_items, order_items.order_id == orders.id
        ).join(
            orders, orders.id == order_items.order_id
        ).join(
            products, products.asin == order_items.asin
        ).filter(
            func.date(orders.order_date) >= start_date,
            func.date(orders.order_date) <= end_date
        ).group_by(
            products.asin, products.title
        ).order_by(
            func.sum(order_items.total * order_items.quantity).desc()
        ).limit(limit)

        results = query.all()

        return [
            {
                "asin": r.asin,
                "title": r.title,
                "revenue": float(r.revenue),
                "orders": r.orders
            }
            for r in results
        ]
```

### 2. 成本追踪

#### 成本分类

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          成本分类体系                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  直接成本 (COGS):                                                        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  • 产品采购成本 (Product Cost)                                    │   │
│  │  • 海运费 (Sea Freight)                                           │   │
│  │  • 清关费 (Customs Duty)                                           │   │
│  │  • 关税 (Import Tax)                                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  间接成本:                                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Amazon 平台费:                                                  │   │
│  │    - 佣金 (Referral Fee)                                          │   │
│  │    - FBA 费 (Fulfillment Fee)                                      │   │
│  │    - 仓储费 (Storage Fee)                                         │   │
│  │    - 订单处理费 (Order Handling)                                 │   │
│  │    - 退货准备金 (Return Reserve)                                 │   │
│  │                                                                 │   │
│  │  • 广告费 (Advertising):                                         │   │
│  │    - PPC 广告支出                                                 │   │
│  │    • DSP 广告支出                                                 │   │
│  │                                                                 │   │
│  │  • 运营成本:                                                    │   │
│  │    - 订阅软件费                                                   │   │
│  │    - 工具费                                                      │   │
│  │    - 办公用品                                                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 代码实现

```python
# backend/services/finance/cost_tracker.py

class CostTracker:
    """成本追踪器"""

    async def record_cost(
        self,
        order_id: str,
        cost_type: str,
        amount: float,
        description: str = None,
        invoice_number: str = None
    ):
        """记录成本"""
        cost = Cost(
            id=uuid.uuid4(),
            order_id=order_id,
            cost_type=cost_type,
            amount=Decimal(str(amount)),
            currency="CNY",
            description=description,
            invoice_number=invoice_number,
            incurred_at=datetime.utcnow()
        )

        self.db.add(cost)
        self.db.commit()

        return cost

    async def get_costs_breakdown(
        self,
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        获取成本分解

        Returns:
            {
                "total_cost": 10000.00,
                "by_type": {
                    "product": 6000.00,
                    "shipping": 1000.00,
                    "amazon_fees": 2000.00,
                    "advertising": 1000.00
                },
                "by_order": [...]
            }
        """
        # 按类型汇总
        query = self.db.query(
            costs.cost_type,
            func.sum(costs.amount).label("total")
        ).filter(
            func.date(costs.incurred_date) >= start_date,
            func.date(costs.incurred_date) <= end_date
        ).group_by(costs.cost_type)

        results = query.all()
        by_type = {r.cost_type: float(r.total) for r in results}
        total_cost = sum(by_type.values())

        # 按订单汇总
        by_order = await self._get_costs_by_order(start_date, end_date)

        return {
            "total_cost": float(total_cost),
            "by_type": by_type,
            "by_order": by_order
        }

    async def get_profitability_report(
        self,
        start_date: date,
        end_date: date,
        group_by: str = "product"
    ) -> List[Dict]:
        """
        获取盈利能力报告

        Args:
            group_by: 分组方式 (product/category/marketplace)

        Returns:
            [
                {
                    "asin": "B0XXX",
                    "title": "...",
                    "revenue": 5000.00,
                    "cost": 3000.00,
                    "profit": 2000.00,
                    "margin": 40.0,
                    "roi": 66.7
                },
                ...
            ]
        """
        if group_by == "product":
            # 按产品分组
            revenue_subq = self.db.query(
                order_items.asin,
                func.sum(order_items.total * order_items.quantity).label("revenue")
            ).join(
                orders, orders.id == order_items.order_id
            ).filter(
                func.date(orders.order_date) >= start_date,
                func.date(orders.order_date) <= end_date
            ).group_by(order_items.asin).subquery()

            cost_subq = self.db.query(
                costs.order_id,
                func.sum(costs.amount).label("cost")
            ).join(
                orders, orders.id == costs.order_id
            ).filter(
                func.date(orders.order_date) >= start_date,
                func.date(orders.order_date) <= end_date
            ).group_by(costs.order_id).subquery()

            # 关联数据
            query = self.db.query(
                order_items.asin,
                products.title,
                revenue_subq.c.revenue,
                func.coalesce(cost_subq.c.cost, 0).label("cost")
            ).join(
                products, products.asin == order_items.asin
            ).join(
                revenue_subq, revenue_subq.c.asin == order_items.asin
            ).join(
                cost_subq, cost_subq.c.order_id == revenue_subq.c.order_id
            )

            results = query.all()

            return [
                {
                    "asin": r.asin,
                    "title": r.title,
                    "revenue": float(r.revenue),
                    "cost": float(r.cost),
                    "profit": float(r.revenue - r.cost),
                    "margin": float((r.revenue - r.cost) / r.revenue * 100) if r.revenue > 0 else 0,
                    "roi": float((r.revenue - r.cost) / r.cost * 100) if r.cost > 0 else 0
                }
                for r in results
            ]
```

### 3. 财务报表生成

```python
# backend/services/finance/report_generator.py

from typing import Dict, List, Optional
from datetime import date
from decimal import Decimal

class FinancialReportGenerator:
    """财务报表生成器"""

    async def generate_daily_report(
        self,
        report_date: date
    ) -> Dict:
        """
        生成日报

        Returns:
            {
                "date": "2024-01-01",
                "summary": {
                    "revenue": 5000.00,
                    "cost": 3000.00,
                    "profit": 2000.00,
                    "orders": 150
                },
                "details": {...}
            }
        """
        # 获取收入
        revenue_data = await revenue_tracker.get_daily_revenue(report_date)

        # 获取成本
        cost_data = await cost_tracker.get_daily_costs(report_date)

        # 计算利润
        profit = revenue_data["net_revenue"] - cost_data["total_cost"]

        # 获取订单明细
        orders = await self._get_orders_by_date(report_date)

        return {
            "date": report_date.isoformat(),
            "summary": {
                "revenue": revenue_data["net_revenue"],
                "cost": cost_data["total_cost"],
                "profit": profit,
                "orders": revenue_data["order_count"],
                "average_order_value": revenue_data["net_revenue"] / revenue_data["order_count"]
            },
            "revenue_breakdown": revenue_data["by_marketplace"],
            "cost_breakdown": cost_data["by_type"],
            "top_products": await self._get_top_products(report_date, limit=5),
            "pending_actions": await self._get_pending_actions(report_date)
        }

    async def generate_profit_loss_statement(
        self,
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        生成损益表 (P&L)

        Returns:
            {
                "period": "2024-01-01 to 2024-01-31",
                "revenue": {...},
                "cogs": {...},
                "gross_profit": {...},
                "operating_expenses": {...},
                "net_profit": {...}
            }
        """
        # 收入
        total_revenue = await self._get_total_revenue(start_date, end_date)

        # 销货成本
        total_cogs = await self._get_total_cogs(start_date, end_date)

        # 毛利
        gross_profit = total_revenue - total_cogs

        # 运营费用
        operating_expenses = await self._get_operating_expenses(start_date, end_date)

        # 净利润
        net_profit = gross_profit - operating_expenses

        return {
            "period": f"{start_date} to {end_date}",
            "revenue": {
                "total": total_revenue,
                "breakdown": await self._get_revenue_breakdown(start_date, end_date)
            },
            "cogs": {
                "total": total_cogs,
                "products": total_cogs * 0.6,  # 假设 60%
                "shipping": total_cogs * 0.2,
                "duties": total_cogs * 0.1,
                "other": total_cogs * 0.1
            },
            "gross_profit": {
                "amount": gross_profit,
                "margin": (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
            },
            "operating_expenses": {
                "total": operating_expenses,
                "amazon_fees": operating_expenses * 0.5,
                "advertising": operating_expenses * 0.3,
                "other": operating_expenses * 0.2
            },
            "net_profit": {
                "amount": net_profit,
                "net_margin": (net_profit / total_revenue * 100) if total_revenue > 0 else 0
            }
        }

    async def export_report(
        self,
        report_type: str,
        start_date: date,
        end_date: date,
        format: str = "excel"
    ) -> bytes:
        """
        导出报表

        Args:
            report_type: daily/weekly/monthly/pnl
            format: excel/pdf/csv

        Returns:
            报告文件字节流
        """
        # 生成报表数据
        if report_type == "daily":
            data = await self.generate_daily_report(start_date)
        elif report_type == "pnl":
            data = await self.generate_profit_loss_statement(start_date, end_date)

        # 格式化输出
        if format == "excel":
            return await self._export_to_excel(data)
        elif format == "pdf":
            return await self._export_to_pdf(data)
        elif format == "csv":
            return await self._export_to_csv(data)
```

---

## API 设计

### 端点定义

```python
# backend/api/routes/finance.py

from fastapi import APIRouter, Query
from typing import List

router = APIRouter(prefix="/api/v1/finance", tags=["Finance"])

@router.get("/revenue")
async def get_revenue(
    period: str = Query("today"),  # today/week/month/custom
    start_date: date = Query(None),
    end_date: date = Query(None),
    marketplace: str = Query(None)
):
    """获取收入统计"""
    pass

@router.get("/costs")
async def get_costs(
    period: str = Query("month"),
    cost_type: str = Query(None),
    start_date: date = Query(None),
    end_date: date = Query(None)
):
    """获取成本统计"""
    pass

@router.get("/profit")
async def get_profit_analysis(
    start_date: date = Query(...),
    end_date: date = Query(...),
    group_by: str = Query("product")
):
    """获取利润分析"""
    pass

@router.get("/cashflow")
async def get_cashflow_forecast(
    forecast_days: int = Query(30)
):
    """现金流预测"""
    pass

@router.post("/reports/generate")
async def generate_report(
    report_type: str = Query(...),  # daily/weekly/monthly/pnl
    start_date: date = Body(...),
    end_date: date = Body(...),
    format: str = Query("excel")
):
    """生成财务报表"""
    pass

@router.get("/dashboards")
async def get_financial_dashboard():
    """获取财务仪表板数据"""
    return {
        "today_revenue": {"value": 1500, "change": 15.5},
        "mtd_revenue": {"value": 45000, "change": 8.3},
        "pending_payouts": 1234.56,
        "profit_margin": 25.8,
        "top_products": [...],
        "cash_balance": 50000.00
    }
```

---

## 数据可视化

### Dashboard 组件

```typescript
// frontend/components/finance/Dashboard.tsx

import React from 'react';
import { Line, Bar, Pie } from 'recharts';

const FinancialDashboard: React.FC = () => {
  const data = {
    revenue: [
      { date: '01-01', revenue: 5000, cost: 3000, profit: 2000 },
      { date: '01-02', revenue: 5500, cost: 3200, profit: 2300 },
      { date: '01-03', revenue: 4800, cost: 2900, profit: 1900 },
      // ...
    ],
    costsByType: [
      { type: '产品采购', value: 6000 },
      { type: 'Amazon费用', value: 2000 },
      { type: '广告费', value: 1000 },
      { type: '其他', value: 1000 }
    ],
    topProducts: [
      { asin: 'B0XXX', title: 'Product 1', revenue: 5000, profit: 2000 },
      { asin: 'B0YYY', title: 'Product 2', revenue: 4500, profit: 1800 }
    ]
  };

  return (
    <div className="financial-dashboard">
      {/* 收入趋势图 */}
      <div className="chart-container">
        <h3>收入趋势 (最近 30 天)</h3>
        <Line width={800} height={300} data={data.revenue}>
          <XAxis dataKey="date" />
          <YAxis />
          <CartesianGrid strokeDasharray="3 3" />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="revenue" stroke="#8884d8" strokeWidth={2} />
          <Line type="monotone" dataKey="cost" stroke="#82ca9d" strokeWidth={2} />
          <Line type="monotone" dataKey="profit" stroke="#ffc658" strokeWidth={2} />
        </Line>
      </div>

      {/* 成本分布饼图 */}
      <div className="chart-container">
        <h3>成本分布</h3>
        <Pie width={400} height={300} data={data.costsByType}>
          <Pie dataKey="value" name="cost" cx="50%" cy="50%" outerRadius={80} fill="#8884d8" label />
          <Tooltip />
        </Pie>
      </div>

      {/* 热销产品排行 */}
      <div className="table-container">
        <h3>热销产品排行</h3>
        <table>
          <thead>
            <tr>
              <th>ASIN</th>
              <th>产品</th>
              <th>收入</th>
              <th>利润</th>
              <th>ROI</th>
            </tr>
          </thead>
          <tbody>
            {data.topProducts.map(product => (
              <tr key={product.asin}>
                <td>{product.asin}</td>
                <td>{product.title}</td>
                <td>${product.revenue.toFixed(2)}</td>
                <td>${product.profit.toFixed(2)}</td>
                <td>{product.profit / product.revenue * 100:.1f}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
```

---

**预计工作量**: 2 周

| 阶段 | 任务 | 时间 |
|------|------|------|
| Week 1 | 收入/成本统计 | 5 天 |
| Week 2 | 利润分析 + 报表生成 | 5 天 |

---

**所有模块文档已完成！**

现在可以提交所有新创建的文档了。
