# 📊 Amazon 分析仪表盘

基于 Streamlit 的交互式数据可视化仪表盘，用于分析 Amazon Best Sellers 爬虫数据。

## 功能特性

- 📊 **价格分析** - 价格分布直方图、价格区间饼图
- ⭐ **评分分析** - 评分箱线图、评分区间统计
- 🎨 **变体分析** - 变体数量分布、变体TOP排行
- 🎯 **选品建议** - 高评分低价机会、风险商品提醒
- 🔍 **数据筛选** - 价格、评分、变体分类过滤
- 📋 **原始数据** - 完整数据表格查看

## 快速开始

### 1. 安装依赖

```bash
# 使用 uv
uv add --dev streamlit plotly

# 或使用 pip
pip install -r dashboard/requirements.txt
```

### 2. 运行仪表盘

```bash
# 方式1: 使用 uv run
uv run streamlit run dashboard/app.py

# 方式2: 直接运行
streamlit run dashboard/app.py

# 方式3: 指定端口
streamlit run dashboard/app.py --server.port 8501
```

### 3. 访问仪表盘

浏览器打开: http://localhost:8501

## 界面预览

```
┌────────────────────────────────────────────────────────────┐
│  📊 Amazon Best Sellers 数据分析                           │
├────────────────────────────────────────────────────────────┤
│  🔍 侧边栏过滤器                                            │
│  ├── 💰 价格范围: $0 - $100                                │
│  ├── ⭐ 评分范围: 4.0 - 5.0                                │
│  └── 🎨 变体分类: [多变体, 少变体]                          │
├────────────────────────────────────────────────────────────┤
│  KPI 指标                                                  │
│  ┌───────┬───────┬───────┬───────┬───────┐                │
│  │商品数 │均价   │评分   │变体数 │图片数 │                │
│  └───────┴───────┴───────┴───────┴───────┘                │
├────────────────────────────────────────────────────────────┤
│  [📊 价格分析] [⭐ 评分] [🎨 变体] [🎯 选品] [📋 表格] │
├────────────────────────────────────────────────────────────┤
│  │                                                         │
│  │  图表内容区域...                                        │
│  │                                                         │
│  └───────────────────────────────────────────────────────┘
└────────────────────────────────────────────────────────────┘
```

## 功能详解

### 📊 价格分析

- **价格分布直方图** - 查看商品价格分布情况
- **价格区间饼图** - 了解各价格区间占比

### ⭐ 评分分析

- **评分箱线图** - 评分的中位数、四分位数
- **评分区间柱状图** - 各评分区间的商品数量

### 🎨 变体分析

- **变体分类饼图** - 无变体/少变体/多变体/超多变体占比
- **变体TOP榜单** - 变体数量最多的商品
- **散点图** - 变体数与价格的关系

### 🎯 选品建议

- **机会商品** - 高评分(≥4.5) + 低价格(<$30)
- **风险商品** - 高价(>$50) + 低评分(<4.0)

### 📋 数据表格

- 完整的原始数据
- 支持列选择显示
- 可搜索、排序

## 数据更新

仪表盘会自动读取 `output/amazon_products.csv` 文件。

更新数据：

```bash
# 1. 运行爬虫抓取新数据
uv run python main.py --pages 2 --products 20

# 2. 刷新仪表盘页面（按 R 键或浏览器刷新）
```

## 配置选项

### Streamlit 配置

创建 `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#f5f5f5"
secondaryBackgroundColor = "#ffffff"
textColor = "#262730"
font = "sans serif"

[client]
showErrorDetails = false
maxUploadSize = 200

[logger]
level = "info"
```

## 部署

### Streamlit Cloud

```bash
# 1. 推送到 GitHub
git add .
git commit -m "Add dashboard"
git push

# 2. 访问 share.streamlit.io
# 3. 连接 GitHub 仓库
# 4. 选择 dashboard/app.py 作为主文件
# 5. 部署！
```

### Docker

```dockerfile
FROM python:3.14-slim

WORKDIR /app

COPY dashboard/requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

EXPOSE 8501

CMD streamlit run dashboard/app.py --server.port=8501 --server.address=0.0.0.0
```

```bash
# 构建并运行
docker build -t amazon-dashboard .
docker run -p 8501:8501 amazon-dashboard
```

## 故障排除

### 问题：无法加载CSV

**解决方案：**
```bash
# 确保已运行爬虫生成数据
uv run python main.py --pages 1 --products 5
```

### 问题：图表不显示

**解决方案：**
```bash
# 更新 plotly
pip install --upgrade plotly
```

### 问题：端口被占用

**解决方案：**
```bash
# 使用其他端口
streamlit run dashboard/app.py --server.port 8502
```

## 开发

### 添加新图表

```python
# 在 dashboard/app.py 中添加新的渲染函数

def render_custom_chart(df):
    st.subheader("自定义图表")
    fig = px.bar(df, x="field1", y="field2")
    st.plotly_chart(fig)

# 在 main() 函数中调用
with st.tabs(["自定义图表"]):
    render_custom_chart(df)
```

### 自定义样式

```python
# 修改 CSS 样式
st.markdown("""
<style>
    .custom-class {
        background: #your-color;
    }
</style>
""", unsafe_allow_html=True)
```

## 性能优化

- 使用 `@st.cache_data` 缓存数据加载
- 限制大数据集的显示行数
- 使用采样数据加快渲染

## 许可证

MIT
