# Amazon 商品数据抓取需求文档

## 一、当前已抓取的数据 ✅

### 1.1 基础信息

| 字段 | 英文名 | 数据类型 | 示例 | 抓取状态 |
|------|--------|----------|------|----------|
| 商品ID | `asin` | String | `B0BZYCJK89` | ✅ 已实现 |
| 商品标题 | `title` | String | `Owala FreeSip Insulated...` | ✅ 已实现 |
| 商品链接 | `url` | String | `https://www.amazon.com/dp/...` | ✅ 已实现 |

### 1.2 价格与评价

| 字段 | 英文名 | 数据类型 | 示例 | 抓取状态 |
|------|--------|----------|------|----------|
| 价格 | `price` | String | `$29.99` | ✅ 已实现 |
| 评分 | `rating` | String | `4.7 out of 5 stars` | ✅ 已实现 |
| 评论数 | `review_count` | String | `12,345` | ⚠️ 部分实现 |

### 1.3 商品描述

| 字段 | 英文名 | 数据类型 | 示例 | 抓取状态 |
|------|--------|----------|------|----------|
| 商品描述 | `description` | String | `24-ounce insulated...` | ✅ 已实现 |
| 图片链接 | `images` | String | `https://...jpg | https://...jpg` | ✅ 已实现 |
| 图片数量 | `image_count` | Integer | `8` | ✅ 已实现 |

---

## 二、可扩展抓取的数据 📋

### 2.1 价格详细信息

| 字段 | 英文名 | 页面位置 | 优先级 |
|------|--------|----------|--------|
| 原价 | `list_price` | 价格上方，通常有删除线 | 中 |
| 折扣价 | `deal_price` | 显示为促销价 | 中 |
| 节省金额 | `you_save` | "You Save: $X.XX" | 低 |
| 价格历史 | `price_history` | 需要第三方API | 低 |

### 2.2 库存与配送

| 字段 | 英文名 | 页面位置 | 优先级 |
|------|--------|----------|--------|
| 库存状态 | `stock_status` | "In Stock" / "Only X left" | **高** |
| 配送信息 | `shipping_info` | "FREE Delivery" / 配送日期 | **高** |
| 卖家信息 | `seller_info` | "Sold by Amazon" / 第三方卖家 | 中 |
| FBA标识 | `is_fba` | "Fulfilled by Amazon" | 中 |

### 2.3 评价详细信息

| 字段 | 英文名 | 页面位置 | 优先级 |
|------|--------|----------|--------|
| 总评论数 | `total_reviews` | "X ratings" | **高** |
| 五星分布 | `rating_breakdown` | 5星到1星的百分比 | 中 |
| 最新评论 | `recent_reviews` | 需要进入评论页 | 低 |
| 图片评论 | `image_reviews` | 带图的评论数量 | 低 |

### 2.4 商品规格

| 字段 | 英文名 | 页面位置 | 优先级 |
|------|--------|----------|--------|
| 规格参数表 | `specifications` | "Product Details" / "Product Information" | **高** |
| 尺寸 | `dimensions` | 规格/包装尺寸 | **高** |
| 重量 | `weight` | 商品重量 | 中 |
| 颜色选项 | `color_variants` | 颜色选择器 | 中 |
| 尺码选项 | `size_variants` | 尺码选择器 | 中 |
| 款式总数 | `total_variants` | 所有变体数量 | 低 |

### 2.5 分类与标签

| 字段 | 英文名 | 页面位置 | 优先级 |
|------|--------|----------|--------|
| 一级分类 | `category_1` | 面包屑导航 | **高** |
| 二级分类 | `category_2` | 面包屑导航 | **高** |
| 三级分类 | `category_3` | 面包屑导航 | 中 |
| 最佳排名 | `best_seller_rank` | "#1 in XYZ Category" | 中 |
| 年龄段 | `age_range` | 儿童商品适用 | 低 |

### 2.6 营销信息

| 字段 | 英文名 | 页面位置 | 优先级 |
|------|--------|----------|--------|
| 优惠券 | `coupon` | "Coupon" / "Clip Coupon" | **高** |
| Prime标识 | `is_prime` | Prime 蓝色标识 | 中 |
| Add-on Item | `is_addon` | "Add-on Item" 标识 | 低 |
| Amazon's Choice | `amazons_choice` | "Amazon's Choice" 徽章 | 低 |

### 2.7 问答与相关

| 字段 | 英文名 | 页面位置 | 优先级 |
|------|--------|----------|--------|
| 问答数量 | `qa_count` | "X answered questions" | 低 |
| 相关商品 | `related_products` | "Customers who viewed..." | 低 |
| 购买此商品也买 | `bought_together` | "Frequently bought together" | 低 |

---

## 三、建议优先抓取的数据 🎯

### Phase 1: 核心电商数据（立即实现）

```
✅ 已实现:
- 商品ID、标题、价格、评分
- 商品描述、图片链接

🔨 建议新增:
- 库存状态 (stock_status)
- 配送信息 (shipping_info)
- 总评论数 (total_reviews)
- 规格参数表 (specifications)
- 一级/二级分类 (category_1, category_2)
```

### Phase 2: 决策支持数据（后续实现）

```
- 原价/折扣价 (list_price, deal_price)
- 优惠券信息 (coupon)
- 卖家信息 (seller_info)
- 颜色/尺码变体 (variants)
- 最佳排名 (best_seller_rank)
```

### Phase 3: 深度分析数据（可选）

```
- 五星评分分布 (rating_breakdown)
- 问答内容 (questions_answers)
- 相关商品推荐 (related_products)
- A/B 测试价格跟踪
```

---

## 四、页面元素定位参考

### 4.1 价格区域

```css
/* 当前价格 */
#priceblock_ourprice
.a-price .a-offscreen

/* 原价（如果有折扣） */
#priceblock_dealprice
.a-price.a-text-price span

/* 节省金额 */
#regularPriceSavings .a-color-price
```

### 4.2 库存区域

```css
/* 库存状态 */
#availability span
#availability-in-stock

/* 配送信息 */
#deliveryBlock
#price-shipping-message
```

### 4.3 规格参数表

```css
/* 产品详情表格 */
#productDetails_techSpec_section_1
#detailBullets_feature_div
.prodDetTable tr

/* 或者使用 */
#productDetails table tr
```

### 4.4 分类导航

```css
/* 面包屑导航 */
#wayfinding-breadcrumbs_feature_div
.a-breadcrumb a

/* 最佳排名 */
#productDetails_feature_div b:contains("Best Sellers Rank")
```

### 4.5 评价信息

```css
/* 总评论数 */
[data-hook="total-review-count"]
#acrCustomerReviewText

/* 评分分布 */
[data-hook="review-bar-metadata"]
```

---

## 五、数据优先级矩阵

| 数据字段 | 业务价值 | 实现难度 | 优先级 |
|----------|----------|----------|--------|
| 库存状态 | ⭐⭐⭐⭐⭐ | ⭐ | P0 |
| 配送信息 | ⭐⭐⭐⭐⭐ | ⭐ | P0 |
| 规格参数 | ⭐⭐⭐⭐ | ⭐⭐ | P0 |
| 总评论数 | ⭐⭐⭐⭐ | ⭐ | P0 |
| 分类导航 | ⭐⭐⭐ | ⭐ | P0 |
| 原价/折扣 | ⭐⭐⭐⭐ | ⭐⭐ | P1 |
| 优惠券 | ⭐⭐⭐⭐ | ⭐⭐ | P1 |
| 变体选项 | ⭐⭐⭐ | ⭐⭐⭐ | P1 |
| 卖家信息 | ⭐⭐⭐ | ⭐⭐ | P2 |
| 评分分布 | ⭐⭐ | ⭐⭐ | P2 |

---

## 六、实现建议

### 6.1 立即可实现（简单）

```python
# 库存状态
stock = page.locator("#availability span").text_content()

# 配送信息
shipping = page.locator("#deliveryBlock").text_content()

# 总评论数
reviews = page.locator("[data-hook='total-review-count']").text_content()

# 分类导航
categories = page.locator(".a-breadcrumb a").all_text_contents()
```

### 6.2 需要解析（中等）

```python
# 规格参数表 - 需要解析表格
specs_table = page.locator("#productDetails_techSpec_section_1 table")
rows = specs_table.locator("tr").all()
for row in rows:
    name = row.locator("th").text_content()
    value = row.locator("td").text_content()
```

### 6.3 复杂逻辑（高级）

```python
# 变体选项 - 需要处理下拉/点击
variant_dropdown = page.locator("#native_dropdown_selected_size_name")
options = variant_dropdown.locator("option").all()

# 优惠券 - 需要检查是否存在
coupon = page.locator("#promoPriceBlockMessage")
if coupon.count() > 0:
    coupon_text = coupon.text_content()
```

---

## 七、输出格式建议

### 7.1 当前 CSV 格式（扁平）

```csv
asin,title,price,rating,description,images,image_count,url
```

### 7.2 扩展 CSV 格式（更多字段）

```csv
asin,title,price,list_price,deal_price,savings,stock_status,
shipping_info,seller_info,total_reviews,rating,rating_5,
rating_4,rating_3,rating_2,rating_1,description,images,
image_count,category_1,category_2,category_3,specifications,
coupon,is_prime,is_addon,variants_count,url
```

### 7.3 JSON 格式（嵌套结构）

```json
{
  "asin": "B0BZYCJK89",
  "title": "Owala FreeSip...",
  "pricing": {
    "current": "$29.99",
    "list": "$35.99",
    "savings": "$6.00"
  },
  "inventory": {
    "stock": "In Stock",
    "shipping": "FREE Delivery"
  },
  "ratings": {
    "average": "4.7",
    "total": "12,345",
    "breakdown": {
      "5": "70%",
      "4": "15%",
      "3": "8%",
      "2": "4%",
      "1": "3%"
    }
  },
  "specifications": {
    "Brand": "Owala",
    "Capacity": "24 Oz",
    "Material": "Stainless Steel"
  }
}
```

---

## 八、下一步行动计划

1. **确认需求** - 确定优先抓取哪些字段
2. **更新代码** - 在 `product_detail_parser.py` 中添加新的提取函数
3. **测试验证** - 用少量商品测试新字段提取
4. **更新输出** - 调整 CSV 输出格式
5. **批量抓取** - 运行完整抓取任务

---

*文档创建时间: 2026-03-12*
*当前版本: v1.0*
