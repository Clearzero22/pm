"""
Amazon Best Sellers 数据分析仪表盘
使用 Streamlit 构建交互式数据可视化
"""
import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 页面配置
st.set_page_config(
    page_title="Amazon 分析仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data(ttl=300)  # 缓存5分钟
def load_data():
    """加载并处理CSV数据"""
    csv_path = "output/amazon_products.csv"

    if not os.path.exists(csv_path):
        st.error(f"❌ 数据文件不存在: {csv_path}")
        st.info("💡 请先运行爬虫: `uv run python main.py`")
        return pd.DataFrame()

    try:
        # 读取CSV
        df = pd.read_csv(csv_path)

        # 显示原始列名用于调试
        with st.expander("📋 原始数据列", expanded=False):
            st.write("CSV 文件中的列:")
            st.code(", ".join(df.columns.tolist()))

        # 数据清洗和转换
        # 处理价格
        if "price" in df.columns:
            df["price_num"] = df["price"].astype(str).str.replace(r"[\$]", "", regex=True)
            df["price_num"] = pd.to_numeric(df["price_num"], errors="coerce")
        else:
            df["price_num"] = None

        # 处理评分
        if "rating" in df.columns:
            df["rating_num"] = df["rating"].astype(str).str.extract(r"([\d.]+)")
            df["rating_num"] = pd.to_numeric(df["rating_num"], errors="coerce")
        else:
            df["rating_num"] = None

        # 处理数量字段
        for col in ["total_variants", "image_count"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # 处理图片URL列表（CSV中用两个空格分隔）
        if "images" in df.columns:
            df["image_urls"] = df["images"].astype(str).apply(
                lambda x: [url.strip() for url in x.split() if url.strip() and url.startswith("http")] if x != "nan" else []
            )
        else:
            df["image_urls"] = [[] for _ in range(len(df))]

        # 处理变体类型
        if "variant_types" in df.columns:
            df["variant_types_list"] = df["variant_types"].astype(str).apply(
                lambda x: [t.strip() for t in x.split("|") if t.strip()]
            )
        else:
            df["variant_types_list"] = [[] for _ in range(len(df))]

        return df

    except Exception as e:
        st.error(f"❌ 读取数据文件时出错: {str(e)}")
        st.info("💡 请检查 CSV 文件格式是否正确")
        return pd.DataFrame()


def render_kpi_metrics(df):
    """渲染KPI指标卡片"""
    if df.empty:
        return

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("📦 商品总数", f"{len(df)}")

    with col2:
        if "price_num" in df.columns and not df["price_num"].isna().all():
            avg_price = df["price_num"].mean()
            st.metric("💰 平均价格", f"${avg_price:.2f}")
        else:
            st.metric("💰 平均价格", "N/A")

    with col3:
        if "rating_num" in df.columns and not df["rating_num"].isna().all():
            avg_rating = df["rating_num"].mean()
            st.metric("⭐ 平均评分", f"{avg_rating:.1f}")
        else:
            st.metric("⭐ 平均评分", "N/A")

    with col4:
        if "total_variants" in df.columns:
            has_variants = (df["total_variants"] > 0).sum()
            st.metric("🎨 有变体商品", f"{int(has_variants)}")
        else:
            st.metric("🎨 有变体商品", "N/A")

    with col5:
        if "image_count" in df.columns:
            total_images = df["image_count"].sum()
            st.metric("🖼️ 总图片数", f"{int(total_images)}")
        else:
            st.metric("🖼️ 总图片数", "N/A")


def render_price_analysis(df):
    """价格分析图表"""
    if "price_num" not in df.columns:
        st.warning("⚠️ 缺少价格数据")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💰 价格分布")
        valid_prices = df[df["price_num"].notna()]
        if len(valid_prices) > 0:
            fig1 = px.histogram(
                valid_prices,
                x="price_num",
                nbins=20,
                title="商品价格分布",
                labels={"price_num": " price ($)"},
                color_discrete_sequence=["#667eea"]
            )
            fig1.update_layout(
                bargap=0.1,
                xaxis_title="price ($)",
                yaxis_title="商品数量",
                height=350
            )
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("📊 价格区间占比")
        valid_prices = df[df["price_num"].notna()]
        if len(valid_prices) > 0:
            price_bins = pd.cut(
                valid_prices["price_num"],
                bins=[0, 15, 30, 50, 100, 1000],
                labels=["<$15", "$15-30", "$30-50", "$50-100", ">$100"]
            )
            price_dist = price_bins.value_counts().sort_index()

            fig2 = px.pie(
                values=price_dist.values,
                names=price_dist.index,
                title="价格区间分布",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Viridis
            )
            fig2.update_layout(height=350)
            st.plotly_chart(fig2, use_container_width=True)


def render_rating_analysis(df):
    """评分分析图表"""
    if "rating_num" not in df.columns:
        st.warning("⚠️ 缺少评分数据")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("⭐ 评分分布")
        valid_ratings = df[df["rating_num"].notna()]
        if len(valid_ratings) > 0:
            fig1 = px.box(
                valid_ratings,
                y="rating_num",
                title="评分箱线图",
                labels={"rating_num": "评分"},
                color_discrete_sequence=["#00d4aa"]
            )
            fig1.update_layout(
                yaxis_title="评分 (⭐)",
                height=350,
                showlegend=False
            )
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("📈 评分区间统计")
        valid_ratings = df[df["rating_num"].notna()]
        if len(valid_ratings) > 0:
            rating_bins = pd.cut(
                valid_ratings["rating_num"],
                bins=[0, 3.5, 4.0, 4.5, 5.0],
                labels=["<3.5⭐", "3.5-4.0⭐", "4.0-4.5⭐", "4.5-5.0⭐"]
            )
            rating_dist = rating_bins.value_counts().sort_index()

            fig2 = px.bar(
                x=rating_dist.index,
                y=rating_dist.values,
                title="各评分区间商品数量",
                labels={"x": "评分区间", "y": "商品数量"},
                text=rating_dist.values,
                color=rating_dist.values,
                color_continuous_scale=px.colors.sequential.Viridis
            )
            fig2.update_traces(texttemplate='%{y}', textposition='outside')
            fig2.update_layout(
                xaxis_title="评分区间",
                yaxis_title="商品数量",
                height=350,
                showlegend=False
            )
            st.plotly_chart(fig2, use_container_width=True)


def render_variant_analysis(df):
    """变体分析"""
    if "total_variants" not in df.columns:
        st.warning("⚠️ 缺少变体数据")
        return

    has_variants = df[df["total_variants"] > 0]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**📊 变体数量分布**")

        # 创建变体分类
        df["variant_category"] = df["total_variants"].apply(
            lambda x: (
                "无变体" if x == 0 else
                "1个变体" if x == 1 else
                "2-5个变体" if 2 <= x <= 5 else
                "6-10个变体" if 6 <= x <= 10 else
                "超多变体(10+)"
            )
        )

        variant_dist = df["variant_category"].value_counts()

        fig1 = px.pie(
            values=variant_dist.values,
            names=variant_dist.index,
            hole=0.5,
            color_discrete_sequence=px.colors.sequential.Tealgrn
        )
        fig1.update_layout(height=300)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.write("**🏆 变体数量 Top 10**")
        top_variants = has_variants.nlargest(10, "total_variants")[
            ["title", "total_variants", "price_num", "rating_num"]
        ] if len(has_variants) > 0 else pd.DataFrame()

        if not top_variants.empty:
            # 格式化显示
            display_df = top_variants.copy()
            display_df["price_num"] = display_df["price_num"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
            display_df["rating_num"] = display_df["rating_num"].apply(lambda x: f"{x:.1f}⭐" if pd.notna(x) else "N/A")
            display_df.columns = ["商品名称", "变体数", "价格", "评分"]
            st.dataframe(display_df, hide_index=True, use_container_width=True, height=300)
        else:
            st.info("暂无变体数据")

    with col3:
        st.write("**📈 价格与变体关系**")
        if len(has_variants) > 0:
            fig3 = px.scatter(
                has_variants,
                x="total_variants",
                y="price_num",
                color="rating_num",
                size="image_count",
                hover_data=["title"],
                title="变体数 vs 价格",
                labels={
                    "total_variants": "变体数量",
                    "price_num": "价格 ($)",
                    "rating_num": "评分"
                },
                height=300
            )
            fig3.update_layout(
                xaxis_title="变体数量",
                yaxis_title="价格 ($)"
            )
            st.plotly_chart(fig3, use_container_width=True)


def render_opportunity_analysis(df):
    """选品机会分析"""
    st.subheader("🎯 智能选品建议")

    col1, col2 = st.columns(2)

    with col1:
        st.write("💡 **高评分 + 低价格 = 机会**")

        # 筛选条件
        mask = pd.Series([True] * len(df), index=df.index)
        if "price_num" in df.columns:
            mask &= df["price_num"] < 30
        if "rating_num" in df.columns:
            mask &= (df["rating_num"] >= 4.5) & (df["rating_num"].notna())

        opportunities = df[mask].nlargest(10, "rating_num") if mask.any() else pd.DataFrame()

        if not opportunities.empty:
            for idx, row in opportunities.iterrows():
                with st.expander(f"⭐ {row['title'][:60]}..."):
                    cols = st.columns(4)
                    cols[0].metric("价格", f"${row.get('price_num', 0):.2f}" if pd.notna(row.get('price_num')) else "N/A")
                    cols[1].metric("评分", f"{row.get('rating_num', 0):.1f}⭐" if pd.notna(row.get('rating_num')) else "N/A")
                    cols[2].metric("变体", f"{int(row.get('total_variants', 0))}个")
                    cols[3].metric("图片", f"{int(row.get('image_count', 0))}张")
        else:
            st.info("当前筛选条件下暂无机会商品")

    with col2:
        st.write("⚠️ **需要关注的商品**")

        # 高价低评分
        mask = pd.Series([True] * len(df), index=df.index)
        if "price_num" in df.columns:
            mask &= df["price_num"] > 50
        if "rating_num" in df.columns:
            mask &= (df["rating_num"] < 4.0) & (df["rating_num"].notna())

        risks = df[mask].nsmallest(5, "rating_num") if mask.any() else pd.DataFrame()

        if not risks.empty:
            for idx, row in risks.iterrows():
                with st.expander(f"⚠️ {row['title'][:60]}..."):
                    cols = st.columns(3)
                    cols[0].metric("价格", f"${row.get('price_num', 0):.2f}" if pd.notna(row.get('price_num')) else "N/A")
                    cols[1].metric("评分", f"{row.get('rating_num', 0):.1f}⭐" if pd.notna(row.get('rating_num')) else "N/A")
                    cols[2].metric("建议", "谨慎选择")
        else:
            st.info("当前数据中没有明显风险商品")


def render_image_gallery(df):
    """图片画廊展示"""
    st.subheader("🖼️ 商品图片展示")

    # 选择要显示的商品数量
    num_products = st.slider("显示商品数量", 1, min(len(df), 10), 5)

    for idx, row in df.head(num_products).iterrows():
        with st.expander(f"📦 {row.get('title', 'N/A')[:80]}"):
            col1, col2 = st.columns([1, 2])

            with col1:
                # 基本信息
                st.write("**基本信息**")
                if "price" in df.columns:
                    st.write(f"💰 价格: {row.get('price', 'N/A')}")
                if "rating" in df.columns:
                    st.write(f"⭐ 评分: {row.get('rating', 'N/A')}")
                if "total_variants" in df.columns:
                    st.write(f"🎨 变体数: {int(row.get('total_variants', 0))}个")
                if "color_variants" in df.columns and pd.notna(row.get('color_variants')):
                    st.write(f"🎨 颜色: {row.get('color_variants', 'N/A')}")
                if "size_variants" in df.columns and pd.notna(row.get('size_variants')):
                    st.write(f"📏 尺寸: {row.get('size_variants', 'N/A')}")

            with col2:
                # 图片展示
                images = row.get('image_urls', [])
                if images and len(images) > 0:
                    st.write(f"**图片 ({len(images)}张)**")
                    # 分列显示图片
                    cols_per_row = 4
                    for i in range(0, len(images), cols_per_row):
                        cols = st.columns(cols_per_row)
                        for j in range(cols_per_row):
                            if i + j < len(images):
                                with cols[j]:
                                    st.image(images[i + j], use_container_width=True)
                else:
                    st.info("暂无图片")


def render_data_table(df):
    """数据表格"""
    st.subheader("📋 原始数据")

    # 显示所有列
    all_columns = df.columns.tolist()
    default_columns = ["title", "price", "rating", "total_variants", "color_variants", "size_variants", "image_count"]

    selected_columns = st.multiselect(
        "选择要显示的列 (默认全选)",
        all_columns,
        default=all_columns
    )

    if selected_columns:
        # 格式化显示
        display_df = df[selected_columns].copy()

        # 格式化价格
        if "price_num" in display_df.columns:
            display_df["price_num"] = display_df["price_num"].apply(
                lambda x: f"${x:.2f}" if pd.notna(x) else "N/A"
            )

        # 格式化评分
        if "rating_num" in display_df.columns:
            display_df["rating_num"] = display_df["rating_num"].apply(
                lambda x: f"{x:.1f}⭐" if pd.notna(x) else "N/A"
            )

        st.dataframe(
            display_df,
            column_config={col: col for col in selected_columns},
            hide_index=True,
            use_container_width=True,
            height=400
        )


def main():
    """主函数"""
    # 标题
    st.markdown('<p class="main-header">📊 Amazon Best Sellers 数据分析</p>', unsafe_allow_html=True)

    # 加载数据
    df = load_data()

    if df.empty:
        st.stop()

    # 显示数据概览
    with st.expander("📊 数据概览", expanded=True):
        col1, col2, col3 = st.columns(3)
        col1.write(f"**总行数:** {len(df)}")
        col2.write(f"**总列数:** {len(df.columns)}")
        col3.write(f"**文件大小:** {os.path.getsize('output/amazon_products.csv') / 1024:.1f} KB")

        st.write("**所有列名:**")
        st.code(", ".join(df.columns.tolist()))

    # 侧边栏过滤器
    st.sidebar.header("🔍 数据筛选")

    # 价格范围
    if "price_num" in df.columns:
        min_price = float(df["price_num"].min())
        max_price = float(df["price_num"].max())
        price_range = st.sidebar.slider(
            "💰 价格范围",
            min_price,
            max_price,
            (min_price, max_price)
        )
    else:
        price_range = None

    # 评分范围
    if "rating_num" in df.columns:
        min_rating = float(df["rating_num"].min())
        max_rating = float(df["rating_num"].max())
        rating_range = st.sidebar.slider(
            "⭐ 评分范围",
            min_rating,
            max_rating,
            (min_rating, max_rating)
        )
    else:
        rating_range = None

    # 应用过滤
    filtered_df = df.copy()

    if price_range is not None:
        filtered_df = filtered_df[
            (filtered_df["price_num"] >= price_range[0]) &
            (filtered_df["price_num"] <= price_range[1])
        ]

    if rating_range is not None:
        filtered_df = filtered_df[
            (filtered_df["rating_num"] >= rating_range[0]) &
            (filtered_df["rating_num"] <= rating_range[1])
        ]

    # 显示过滤结果数量
    st.info(f"📊 当前显示: **{len(filtered_df)}** 个商品 (共 {len(df)} 个)")

    # KPI指标
    st.markdown("---")
    render_kpi_metrics(filtered_df)

    # 图表区域
    st.markdown("---")

    # Tab 布局
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 价格分析",
        "⭐ 评分分析",
        "🎨 变体分析",
        "🎯 选品建议",
        "🖼️ 图片展示",
        "📋 数据表格"
    ])

    with tab1:
        render_price_analysis(filtered_df)

    with tab2:
        render_rating_analysis(filtered_df)

    with tab3:
        render_variant_analysis(filtered_df)

    with tab4:
        render_opportunity_analysis(filtered_df)

    with tab5:
        render_image_gallery(filtered_df)

    with tab6:
        render_data_table(filtered_df)


if __name__ == "__main__":
    main()
