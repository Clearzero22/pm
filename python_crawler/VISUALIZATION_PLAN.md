# Amazon 数据可视化与决策支持方案

## 一、目标受众分析

| 受众 | 需求 | 推荐方案 |
|------|------|----------|
| **业务决策者** | 一眼看懂趋势、价格分析、竞品对比 | 仪表盘 + 每日报告 |
| **产品经理** | 选品决策、市场缺口分析 | 交互式图表 + 洞察报告 |
| **运营人员** | 库存监控、定价策略 | 实时警报 + 趋势线 |
| **AI智能体** | 结构化数据输入、API接口 | JSON API + 数据库 |

---

## 二、可视化方案架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Amazon 数据源                            │
│                   (CSV文件 / 数据库)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌─────────────┐ ┌─────────┐ ┌──────────┐
│  仪表盘Web   │ │ 报告PDF │ │ AI API   │
│  (Streamlit)│ │ (自动)  │ │ (FastAPI)│
└─────────────┘ └─────────┘ └──────────┘
        │            │            │
        ▼            ▼            ▼
  业务决策者      每日邮件      AI智能体
```

---

## 三、方案A：Web仪表盘（推荐）⭐

### 技术栈
- **Streamlit** - 快速构建交互式仪表盘
- **Plotly** - 交互式图表
- **Pandas** - 数据处理

### 功能模块

#### 1. 价格趋势分析
```python
# 价格分布图
# 价格 vs 评分散点图
# 各品类价格对比
```

#### 2. 竞品分析
```python
# 评分排名
# 评论数对比
# 图片数量分析
```

#### 3. 变体洞察
```python
# 颜色受欢迎程度
# 尺寸分布
# 变体数量与价格关系
```

#### 4. 选品建议
```python
# 高评分低价格商品（机会）
# 高价低评分商品（避免）
# 缺失变体机会
```

### 仪表盘预览

```
┌────────────────────────────────────────────────────────────┐
│  Amazon Best Sellers 分析仪表盘                            │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  📊 价格分布          🎯 评分分析                           │
│  [直方图]            [箱线图]                               │
│                                                              │
│  🏆 热门变体          💰 价格vs评分                          │
│  [条形图]            [散点图]                               │
│                                                              │
│  📈 品类对比          🔍 智能选品建议                        │
│  [分组柱状图]        [数据表格]                             │
│                                                              │
│  过滤器: [品类▼] [价格范围] [评分▼]                      │
└────────────────────────────────────────────────────────────┘
```

---

## 四、方案B：自动化报告系统

### 报告内容

#### 1. 每日市场报告（PDF）

```
📊 Amazon Best Sellers 每日报告
日期: 2026-03-12

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 市场概况
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 抓取商品数: 50 个
• 平均价格: $28.50
• 平均评分: 4.5 ⭐
• 有变体的商品: 35 个 (70%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 选品机会 Top 5
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Owala FreeSip水瓶 - $29.99, 4.7⭐, 10个变体
   💡 机会: 高评分、多变体、市场认可度高

2. Etekcity厨房秤 - $13.99, 4.6⭐, 3个变体
   💡 机会: 低价格、高评分、性价比高

...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ 风险提示
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 竞品价格战: 某品类价格低于 $15
• 饱和市场: 某品类变体数量 > 20
```

#### 2. 每周趋势报告

```
• 价格趋势（涨跌分析）
• 新品进入数量
• 评分变化监控
• 热门变体变化
```

---

## 五、方案C：AI智能体集成

### 为AI提供结构化数据

#### 1. REST API接口

```python
# FastAPI 后端
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Product(BaseModel):
    asin: str
    title: str
    price: float
    rating: float
    variants: list
    # ... 其他字段

@app.get("/api/products")
async def get_products(
    min_price: float = None,
    max_price: float = None,
    min_rating: float = None
):
    """查询商品数据"""
    return filter_products(min_price, max_price, min_rating)

@app.get("/api/products/{asin}")
async def get_product(asin: str):
    """获取单个商品详情"""
    return get_product_by_asin(asin)

@app.get("/api/insights")
async def get_insights():
    """获取AI分析洞察"""
    return {
        "opportunities": find_high_rating_low_price(),
        "risks": find_market_saturation(),
        "trends": analyze_pricing_trends()
    }
```

#### 2. AI智能体使用示例

```python
# AI 智能体调用API
import requests

# 获取选品机会
response = requests.get("http://api:8000/api/insights")
insights = response.json()

# AI 做决策
for product in insights["opportunities"]:
    if product["price"] < 30 and product["rating"] >= 4.5:
        print(f"🎯 建议选品: {product['title']}")
        print(f"   理由: 高评分({product['rating']})+ 低价格({product['price']})")
```

---

## 六、实现代码

### 6.1 Streamlit 仪表盘

```python
# dashboard/app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 页面配置
st.set_page_config(
    page_title="Amazon 分析仪表盘",
    page_icon="📊",
    layout="wide"
)

# 加载数据
@st.cache_data
def load_data():
    df = pd.read_csv("output/amazon_products.csv")
    return df

df = load_data()

# 侧边栏过滤器
st.sidebar.header("🔍 数据筛选")
category_filter = st.sidebar.multiselect("选择品类", df["category"].unique())
price_range = st.sidebar.slider("价格范围", 0, 100, (0, 100))
rating_filter = st.sidebar.slider("最低评分", 0.0, 5.0, 4.0)

# 主标题
st.title("📊 Amazon Best Sellers 数据分析")
st.markdown(f"**当前数据:** {len(df)} 个商品")

# KPI指标
col1, col2, col3, col4 = st.columns(4)
col1.metric("平均价格", f"${df['price'].mean():.2f}")
col2.metric("平均评分", f"{df['rating'].mean():.1f}⭐")
col3.metric("有变体商品", f"{df[df['total_variants']>0].shape[0]}个")
col4.metric("总变体数", f"{df['total_variants'].sum()}个")

# 价格分布图
col1, col2 = st.columns(2)
with col1:
    st.subheader("💰 价格分布")
    fig1 = px.histogram(df, x="price", nbins=20, title="价格区间分布")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("⭐ 评分分布")
    fig2 = px.box(df, y="rating", title="评分箱线图")
    st.plotly_chart(fig2, use_container_width=True)

# 价格 vs 评分散点图
st.subheader("💰 价格 vs 评分关系")
fig3 = px.scatter(
    df, x="price", y="rating",
    color="total_variants",
    size="image_count",
    hover_data=["title"],
    title="商品价格与评分关系（气泡大小=图片数量）"
)
st.plotly_chart(fig3, use_container_width=True)

# 变体分析
st.subheader("🎨 变体分析")
col1, col2 = st.columns(2)
with col1:
    st.write("**颜色变体最多的商品**")
    top_colors = df.nlargest(5, "color_variants_count")[["title", "color_variants"]]
    st.dataframe(top_colors)

with col2:
    st.write("**尺码变体最多的商品**")
    top_sizes = df.nlargest(5, "size_variants_count")[["title", "size_variants"]]
    st.dataframe(top_sizes)

# 智能选品建议
st.subheader("🎯 智能选品建议")
opportunities = df[
    (df["price"] < 30) &
    (df["rating"] >= 4.5) &
    (df["total_variants"] > 0)
].nlargest(10, "rating")

st.write("💡 高评分 + 低价格 + 有变体 = 市场机会")
st.dataframe(
    opportunities[["title", "price", "rating", "total_variants", "color_variants", "size_variants"]]
)
```

### 6.2 自动化报告生成

```python
# reports/generate_report.py
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import pandas as pd

class AmazonReportGenerator:
    """Amazon数据报告生成器"""

    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)
        self.width, self.height = letter

    def generate_pdf(self, output_path):
        """生成PDF报告"""
        c = canvas.Canvas(output_path, pagesize=letter)
        styles = getSampleStyleSheet()

        # 标题
        c.setFont("Helvetica-Bold", 24)
        c.drawString(50, 750, "Amazon Best Sellers 数据报告")

        # 日期
        from datetime import datetime
        c.setFont("Helvetica", 12)
        c.drawString(50, 720, f"报告日期: {datetime.now().strftime('%Y-%m-%d')}")

        # 概况统计
        y_pos = 680
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_pos, "📊 市场概况")
        y_pos -= 30

        stats = [
            f"• 抓取商品数: {len(self.df)} 个",
            f"• 平均价格: ${self.df['price'].mean():.2f}",
            f"• 平均评分: {self.df['rating'].mean():.1f}⭐",
            f"• 有变体商品: {self.df[self.df['total_variants']>0].shape[0]} 个"
        ]

        c.setFont("Helvetica", 12)
        for stat in stats:
            c.drawString(70, y_pos, stat)
            y_pos -= 20

        # 选品机会表格
        y_pos -= 30
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_pos, "🎯 选品机会 Top 5")
        y_pos -= 30

        opportunities = self.df[
            (self.df["price"] < 30) &
            (self.df["rating"] >= 4.5)
        ].nlargest(5, "rating")

        # 创建表格
        table_data = [["商品名称", "价格", "评分", "变体数"]]
        for _, row in opportunities.iterrows():
            table_data.append([
                row["title"][:30] + "...",
                f"${row['price']:.2f}",
                f"{row['rating']}",
                row["total_variants"]
            ])

        table = Table(table_data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        table.wrapOn(c, self.width, self.height)
        table.drawOn(c, 50, y_pos - 200)

        c.save()
        return output_path
```

### 6.3 FastAPI后端

```python
# api/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from typing import List, Optional

app = FastAPI(title="Amazon Data API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# 数据模型
class Product(BaseModel):
    asin: str
    title: str
    price: float
    rating: float
    color_variants: str
    size_variants: str
    total_variants: int

class Insight(BaseModel):
    message: str
    products: List[Product]

# 加载数据
@startup
def load_data():
    global df
    df = pd.read_csv("output/amazon_products.csv")

@app.get("/api/products", response_model=List[Product])
async def get_products(
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None
):
    """获取商品列表"""
    filtered_df = df.copy()

    if min_price:
        filtered_df = filtered_df[filtered_df["price"] >= min_price]
    if max_price:
        filtered_df = filtered_df[filtered_df["price"] <= max_price]
    if min_rating:
        filtered_df = filtered_df[filtered_df["rating"] >= min_rating]

    return filtered_df.to_dict("records")

@app.get("/api/products/{asin}")
async def get_product(asin: str):
    """获取单个商品详情"""
    product = df[df["asin"] == asin]
    if product.empty:
        raise HTTPException(status_code=404, detail="Product not found")
    return product.to_dict("records")[0]

@app.get("/api/insights/opportunities")
async def get_opportunities():
    """获取选品机会"""
    opportunities = df[
        (df["price"] < 30) &
        (df["rating"] >= 4.5) &
        (df["total_variants"] > 0)
    ].nlargest(10, "rating")

    return {
        "count": len(opportunities),
        "message": f"发现 {len(opportunities)} 个高评分低价机会",
        "products": opportunities.to_dict("records")
    }

@app.get("/api/insights/risk")
async def get_risks():
    """获取市场风险"""
    risks = df[df["rating"] < 4.0]

    return {
        "count": len(risks),
        "message": f"发现 {len(risks)} 个低评分商品（风险）",
        "products": risks.to_dict("records")
    }

@app.get("/api/summary")
async def get_summary():
    """获取数据摘要"""
    return {
        "total_products": len(df),
        "avg_price": float(df["price"].mean()),
        "avg_rating": float(df["rating"].mean()),
        "products_with_variants": int(df[df["total_variants"] > 0].shape[0]),
        "price_range": {
            "min": float(df["price"].min()),
            "max": float(df["price"].max())
        },
        "rating_range": {
            "min": float(df["rating"].min()),
            "max": float(df["rating"].max())
        }
    }
```

---

## 七、部署方案

### 方案A：本地运行

```bash
# 安装依赖
pip install streamlit plotly pandas

# 运行仪表盘
streamlit run dashboard/app.py

# 访问 http://localhost:8501
```

### 方案B：Docker部署

```dockerfile
# Dockerfile
FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  dashboard:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./output:/app/output

  api:
    build: .
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
```

### 方案C：云端部署

| 平台 | 优点 | 缺点 |
|------|------|------|
| **Streamlit Cloud** | 免费托管，一键部署 | 有访问限制 |
| **Heroku** | 灵活，可扩展 | 需付费 |
| **AWS EC2** | 完全控制 | 需要运维 |
| **Azure Web Apps** | 企业级 | 价格较高 |

---

## 八、推荐实施步骤

### Phase 1: 快速原型（1天）
1. ✅ 创建 Streamlit 仪表盘
2. ✅ 添加基础图表
3. ✅ 连接CSV数据

### Phase 2: 功能完善（3天）
4. ⬜ 添加交互式过滤器
5. ⬜ 实现智能选品算法
6. ⬜ PDF自动报告生成

### Phase 3: 集成部署（2天）
7. ⬜ Docker容器化
8. ⬜ API接口开发
9. ⬜ 云端部署

---

## 九、效果预览

### 决策者看到的内容

```
┌─────────────────────────────────────┐
│  📊 每日市场摘要                    │
│  ───────────────────────────────   │
│  今日新增: 50 个商品               │
│  平均价格: $28.50 ↑ 2%            │
│  高评分机会: 8 个                 │
│  ⚠️ 价格竞争风险: 3 个品类        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  🎯 今日选品推荐                   │
│  ───────────────────────────────   │
│  1. Owala 水瓶                    │
│     价格: $29.99 | 评分: 4.7⭐    │
│     理由: 高评分+多变体+价格合理  │
│                                    │
│  2. Etekcity 厨房秤               │
│     价格: $13.99 | 评分: 4.6⭐    │
│     理由: 低价格+高性价比         │
└─────────────────────────────────────┘
```

### AI智能体获取的数据

```json
{
  "api_summary": {
    "total_products": 50,
    "avg_price": 28.50,
    "avg_rating": 4.5
  },
  "opportunities": [
    {
      "asin": "B0BZYCJK89",
      "title": "Owala Water Bottle",
      "price": 29.99,
      "rating": 4.7,
      "total_variants": 10,
      "recommendation": "strong_buy"
    }
  ],
  "risks": [
    {
      "category": "Water Bottles",
      "avg_price": 15.50,
      "risk_level": "high",
      "reason": "价格战激烈"
    }
  ]
}
```

---

*文档创建时间: 2026-03-12*
