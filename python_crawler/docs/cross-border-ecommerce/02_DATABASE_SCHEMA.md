# 数据库设计详解

> **跨境电商全工作流系统** - 数据模型与关系设计

**版本**: v1.0.0
**更新时间**: 2026-03-12

---

## 目录

1. [设计原则](#设计原则)
2. [ER 图](#er-图)
3. [核心表结构](#核心表结构)
4. [索引优化](#索引优化)
5. [数据迁移](#数据迁移)

---

## 设计原则

### 规范化原则

```
┌─────────────────────────────────────────────────────────────────┐
│                     数据库设计范式                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1NF │ 每个字段都是不可分割的最小单位                            │
│  2NF │ 消除部分依赖 (非主键字段完全依赖于主键)                   │
│  3NF │ 消除传递依赖 (非主键字段不依赖于其他非主键字段)            │
│  BCNF│ 消除主键内部的依赖关系                                    │
│                                                                 │
│  反规范化 │ 在性能要求高的场景适当违反范式                        │
│            (如添加冗余字段、汇总表等)                            │
└─────────────────────────────────────────────────────────────────┘
```

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| **表名** | 小写复数名词，下划线分隔 | `products`, `order_items` |
| **字段名** | 小写，下划线分隔 | `created_at`, `is_active` |
| **主键** | `id` 或 `{table}_id` | `id`, `product_id` |
| **外键** | `{referenced_table}_id` | `customer_id`, `listing_id` |
| **索引** | `idx_{table}_{column}` | `idx_products_asin` |
| **唯一键** | `uk_{table}_{column}` | `uk_products_asin` |

---

## ER 图

### 核心实体关系

```
                                    ┌──────────────────┐
                                    │     Category     │
                                    │     (类目)       │
                                    ├──────────────────┤
                                    │ id (PK)          │
                                    │ name             │
                                    │ path             │
                                    │ parent_id (FK)   │
                                    └─────────┬────────┘
                                              │ 1
                                              │
                                              │ N
┌─────────────┐              ┌─────────────┐  │
│  Supplier   │             │   Product   │◄─┘
│  (供应商)   │              │   (产品)    │
├─────────────┤              ├─────────────┤
│ id (PK)     │     N     1  │ id (PK)     │
│ name        │◄────────────│ asin (UK)   │
│ contact     │              │ title       │
│ website     │              │ category_id │
└─────────────┘              │            │
                             └──────┬──────┘
                                    │ 1
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    │ 1             │ 1             │ 1
                    │               │               │
                    │ N             │ N             │ N
            ┌───────┴──────┐ ┌─────┴─────┐ ┌──────┴──────┐
            │   Listing    │ │   Asset   │ │  Supplier   │
            │   (上架)     │ │  (素材)   │ │  Product    │
            ├──────────────┤ ├───────────┤ ├─────────────┤
            │ id (PK)      │ │ id (PK)   │ │ id (PK)     │
            │ product_id   │ │ product_id│ │ product_id  │
            │ marketplace  │ │ type      │ │ supplier_id │
            │ sku          │ │ url       │ │ price       │
            │ price        │ │ metadata  │ │ moq         │
            └──────┬───────┘ └───────────┘ └─────────────┘
                   │
                   │ 1
                   │
                   │ N
            ┌──────┴──────┐
            │    Order    │
            │   (订单)    │
            ├─────────────┤
            │ id (PK)     │
            │ listing_id  │
            │ amazon_id   │
            │ status      │
            │ total       │
            └──────┬──────┘
                   │
                   │ 1
                   │
                   │ N
            ┌──────┴─────────┐
            │  OrderItem     │
            │  (订单明细)    │
            ├────────────────┤
            │ id (PK)        │
            │ order_id       │
            │ quantity       │
            │ price          │
            └────────────────┘

            ┌─────────────┐              ┌─────────────┐
            │  Customer   │              │   Message   │
            │  (客户)     │              │   (消息)    │
            ├─────────────┤              ├─────────────┤
            │ id (PK)     │      N     1  │ id (PK)     │
            │ amazon_id   │◄────────────│ customer_id │
            │ name        │              │ channel     │
            │ email       │              │ content     │
            │ messages[]  │              │ status      │
            └─────────────┘              └─────────────┘
```

---

## 核心表结构

### 1. 产品相关表

#### 1.1 产品表 (products)

```sql
CREATE TABLE products (
    -- 主键
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Amazon 标识
    asin VARCHAR(20) UNIQUE NOT NULL,
    amazon_parent_asin VARCHAR(20),

    -- 基本信息
    title TEXT NOT NULL,
    brand VARCHAR(255),
    manufacturer VARCHAR(255),
    model_number VARCHAR(100),

    -- 类目
    category_id UUID REFERENCES categories(id),
    amazon_category_id VARCHAR(50),

    -- 尺寸重量
    package_dimensions JSONB,
    item_weight DECIMAL(10, 2),
    package_weight DECIMAL(10, 2),

    -- 元数据
    images JSONB DEFAULT '[]'::jsonb,
    attributes JSONB DEFAULT '{}'::jsonb,

    -- 时间戳
    amazon_created_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- 索引
    CONSTRAINT title_not_empty CHECK (length(trim(title)) > 0)
);

-- 索引
CREATE INDEX idx_products_asin ON products(asin);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_created ON products(created_at DESC);

-- 全文搜索索引
CREATE INDEX idx_products_title_search ON products USING gin(to_tsvector('english', title));
CREATE INDEX idx_products_attributes ON products USING gin(attributes);

-- 触发器：自动更新 updated_at
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

#### 1.2 类目表 (categories)

```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    path VARCHAR(500) NOT NULL, -- Electronics > Computers > Laptops
    amazon_id VARCHAR(50) UNIQUE,
    parent_id UUID REFERENCES categories(id),
    level INTEGER NOT NULL DEFAULT 0,
    is_leaf BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_categories_path ON categories(path);
CREATE INDEX idx_categories_parent ON categories(parent_id);
CREATE INDEX idx_categories_amazon ON categories(amazon_id);
```

#### 1.3 上架表 (listings)

```sql
CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 关联
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    marketplace VARCHAR(10) NOT NULL, -- US, UK, DE, FR, IT, ES, JP, CA, AU

    -- Amazon 信息
    seller_sku VARCHAR(50),
    amazon_product_id VARCHAR(50),
    item_name TEXT,
    item_description TEXT,

    -- 定价
    standard_price DECIMAL(10, 2),
    sale_price DECIMAL(10, 2),
    sale_start_date TIMESTAMPTZ,
    sale_end_date TIMESTAMPTZ,
    currency VARCHAR(3) DEFAULT 'USD',

    -- 库存
    quantity INTEGER DEFAULT 0,
    fulfillment_type VARCHAR(20) DEFAULT 'FBA', -- FBA, FBM

    -- 状态
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, deleted
    listing_status VARCHAR(50), -- Amazon 返回的状态

    -- SEO
    search_terms VARCHAR(500),
    keywords JSONB DEFAULT '[]'::jsonb,

    -- 时间戳
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- 约束
    CONSTRAINT marketplace_valid CHECK (marketplace IN ('US', 'UK', 'DE', 'FR', 'IT', 'ES', 'JP', 'CA', 'AU')),
    CONSTRAINT fulfillment_type_valid CHECK (fulfillment_type IN ('FBA', 'FBM')),
    CONSTRAINT unique_listing UNIQUE(product_id, marketplace)
);

-- 索引
CREATE INDEX idx_listings_product ON listings(product_id);
CREATE INDEX idx_listings_marketplace ON listings(marketplace);
CREATE INDEX idx_listings_sku ON listings(seller_sku);
CREATE INDEX idx_listings_status ON listings(status);
```

#### 1.4 素材表 (assets)

```sql
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 关联
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,

    -- 类型
    asset_type VARCHAR(20) NOT NULL, -- image, video, document
    asset_role VARCHAR(50), -- main, pt, gallery, a_plus

    -- 文件信息
    original_url TEXT,
    local_path VARCHAR(500),
    file_name VARCHAR(255),
    file_size BIGINT,
    mime_type VARCHAR(100),
    width INTEGER,
    height INTEGER,
    duration INTEGER, -- 视频时长（秒）

    -- AI 处理
    ai_processed BOOLEAN DEFAULT false,
    ai_prompt TEXT,
    ai_model VARCHAR(100),

    -- Amazon 要求
    amazon_asset_id VARCHAR(100),
    upload_status VARCHAR(20) DEFAULT 'pending', -- pending, uploaded, failed

    -- 排序
    position INTEGER DEFAULT 0,

    -- 时间戳
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_assets_product ON assets(product_id);
CREATE INDEX idx_assets_type ON assets(asset_type);
CREATE INDEX idx_assets_role ON assets(asset_role);
```

### 2. 供应商相关表

#### 2.1 供应商表 (suppliers)

```sql
CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 基本信息
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE,

    -- 联系方式
    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    website VARCHAR(255),

    -- 地址
    country VARCHAR(2),
    province VARCHAR(100),
    city VARCHAR(100),
    address TEXT,

    -- 支付
    bank_account JSONB,
    payment_terms VARCHAR(100),
    currency VARCHAR(3) DEFAULT 'CNY',

    -- 评级
    rating DECIMAL(3, 2),
    total_orders INTEGER DEFAULT 0,
    total_amount DECIMAL(15, 2) DEFAULT 0,

    -- 状态
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, blocked

    -- 时间戳
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_suppliers_code ON suppliers(code);
CREATE INDEX idx_suppliers_status ON suppliers(status);
CREATE INDEX idx_suppliers_country ON suppliers(country);
```

#### 2.2 供应商产品表 (supplier_products)

```sql
CREATE TABLE supplier_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 关联
    supplier_id UUID NOT NULL REFERENCES suppliers(id),
    product_id UUID REFERENCES products(id),

    -- 供应商产品信息
    supplier_sku VARCHAR(100),
    supplier_product_name TEXT,
    supplier_product_url TEXT,

    -- 价格和 MOQ
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CNY',
    moq INTEGER DEFAULT 1, -- 最小起订量

    -- 物流
    lead_time_days INTEGER DEFAULT 7,
    weight DECIMAL(10, 2),
    package_dimensions JSONB,

    -- 时间戳
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT unique_supplier_product UNIQUE(supplier_id, supplier_sku)
);

-- 索引
CREATE INDEX idx_supplier_products_supplier ON supplier_products(supplier_id);
CREATE INDEX idx_supplier_products_product ON supplier_products(product_id);
```

### 3. 订单相关表

#### 3.1 订单表 (orders)

```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Amazon 订单号
    amazon_order_id VARCHAR(50) UNIQUE NOT NULL,
    marketplace_id VARCHAR(20),

    -- 客户
    customer_id UUID REFERENCES customers(id),
    buyer_email VARCHAR(255),
    buyer_name VARCHAR(255),

    -- 地址
    ship_address JSONB,

    -- 金额
    order_total DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    tax_amount DECIMAL(10, 2),
    shipping_amount DECIMAL(10, 2),

    -- 状态
    order_status VARCHAR(20) DEFAULT 'pending',
    fulfillment_type VARCHAR(20), -- FBA, FBM

    -- 时间
    order_date TIMESTAMPTZ NOT NULL,
    ship_date TIMESTAMPTZ,
    expected_delivery_date TIMESTAMPTZ,
    actual_delivery_date TIMESTAMPTZ,

    -- 本地
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_orders_amazon_id ON orders(amazon_order_id);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(order_status);
CREATE INDEX idx_orders_date ON orders(order_date DESC);
```

#### 3.2 订单明细表 (order_items)

```sql
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 关联
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    listing_id UUID REFERENCES listings(id),
    product_id UUID REFERENCES products(id),

    -- Amazon 信息
    amazon_order_item_id VARCHAR(50) UNIQUE NOT NULL,
    asin VARCHAR(20),

    -- 商品信息
    title TEXT,
    quantity_ordered INTEGER NOT NULL,
    quantity_shipped INTEGER DEFAULT 0,

    -- 金额
    unit_price DECIMAL(10, 2),
    total_price DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',

    -- 时间戳
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_listing ON order_items(listing_id);
CREATE INDEX idx_order_items_asin ON order_items(asin);
```

### 4. 客服相关表

#### 4.1 客户表 (customers)

```sql
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Amazon 信息
    amazon_customer_id VARCHAR(50) UNIQUE,
    buyer_name VARCHAR(255),
    buyer_email VARCHAR(255),

    -- 统计
    total_orders INTEGER DEFAULT 0,
    total_spent DECIMAL(10, 2) DEFAULT 0,
    last_order_date TIMESTAMPTZ,

    -- 分级
    tier VARCHAR(20) DEFAULT 'regular', -- regular, vip, blacklisted
    tags JSONB DEFAULT '[]'::jsonb,

    -- 备注
    notes TEXT,

    -- 时间戳
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_customers_amazon_id ON customers(amazon_customer_id);
CREATE INDEX idx_customers_email ON customers(buyer_email);
CREATE INDEX idx_customers_tier ON customers(tier);
```

#### 4.2 消息表 (messages)

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 关联
    customer_id UUID REFERENCES customers(id),
    order_id UUID REFERENCES orders(id),

    -- 渠道
    channel VARCHAR(20) NOT NULL, -- amazon, email, whatsapp, telegram
    channel_message_id VARCHAR(100),

    -- 方向
    direction VARCHAR(10) NOT NULL, -- inbound, outbound

    -- 内容
    subject VARCHAR(500),
    body TEXT NOT NULL,
    attachments JSONB DEFAULT '[]'::jsonb,

    -- AI 处理
    ai_analyzed BOOLEAN DEFAULT false,
    ai_sentiment VARCHAR(20), -- positive, neutral, negative
    ai_category VARCHAR(50),
    ai_suggested_response TEXT,

    -- 状态
    status VARCHAR(20) DEFAULT 'open', -- open, responded, resolved, closed
    assigned_to UUID,

    -- 时间
    received_at TIMESTAMPTZ DEFAULT NOW(),
    responded_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ
);

-- 索引
CREATE INDEX idx_messages_customer ON messages(customer_id);
CREATE INDEX idx_messages_order ON messages(order_id);
CREATE INDEX idx_messages_status ON messages(status);
CREATE INDEX idx_messages_channel ON messages(channel);
CREATE INDEX idx_messages_received ON messages(received_at DESC);
```

### 5. 财务相关表

#### 5.1 收入表 (revenue)

```sql
CREATE TABLE revenue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 关联
    order_id UUID REFERENCES orders(id),
    listing_id UUID REFERENCES listings(id),

    -- 金额
    gross_amount DECIMAL(10, 2) NOT NULL,
    commission_fee DECIMAL(10, 2) DEFAULT 0,
    fba_fee DECIMAL(10, 2) DEFAULT 0,
    other_fee DECIMAL(10, 2) DEFAULT 0,
    net_amount DECIMAL(10, 2) NOT NULL,

    -- 汇率
    currency VARCHAR(3) NOT NULL,
    exchange_rate DECIMAL(10, 6),

    -- 时间
    transaction_date TIMESTAMPTZ NOT NULL,
    deposit_date TIMESTAMPTZ,

    -- 状态
    status VARCHAR(20) DEFAULT 'pending', -- pending, deposited

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_revenue_order ON revenue(order_id);
CREATE INDEX idx_revenue_listing ON revenue(listing_id);
CREATE INDEX idx_revenue_date ON revenue(transaction_date DESC);
```

#### 5.2 成本表 (costs)

```sql
CREATE TABLE costs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 关联
    order_id UUID REFERENCES orders(id),
    listing_id UUID REFERENCES listings(id),
    supplier_id UUID REFERENCES suppliers(id),

    -- 成本类型
    cost_type VARCHAR(50) NOT NULL, -- purchase, shipping, advertising, storage, other

    -- 金额
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CNY',
    exchange_rate DECIMAL(10, 6),

    -- 详情
    description TEXT,
    invoice_number VARCHAR(100),
    invoice_date DATE,
    attachment_url TEXT,

    -- 时间
    incurred_date TIMESTAMPTZ NOT NULL,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_costs_order ON costs(order_id);
CREATE INDEX idx_costs_listing ON costs(listing_id);
CREATE INDEX idx_costs_supplier ON costs(supplier_id);
CREATE INDEX idx_costs_type ON costs(cost_type);
CREATE INDEX idx_costs_date ON costs(incurred_date DESC);
```

---

## 索引优化

### 查询优化策略

```sql
-- 1. 复合索引（覆盖常用查询）
CREATE INDEX idx_listings_product_status
    ON listings(product_id, status)
    WHERE status = 'active';

-- 2. 部分索引（只索引活跃数据）
CREATE INDEX idx_active_products
    ON products(asin, title)
    WHERE id IN (
        SELECT product_id FROM listings WHERE status = 'active'
    );

-- 3. 表达式索引
CREATE INDEX idx_products_title_lower
    ON products(LOWER(title));

-- 4. JSONB 索引
CREATE INDEX idx_products_images
    ON products USING gin((images->'main'));

-- 5. 时间范围查询优化
CREATE INDEX idx_orders_date_range
    ON orders(order_date DESC NULLS LAST)
    INCLUDE (amazon_order_id, order_status);
```

---

## 数据迁移

### Alembic 配置

```python
# alembic/env.py
from alembic import context
from sqlalchemy import engine_from_config
import sys
sys.path.insert(0, '/app/backend')

from database import Base
from models import *  # 导入所有模型

target_metadata = Base.metadata

# 迁移脚本示例
# alembic/versions/001_initial.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    """创建初始表结构"""
    op.create_table(
        'products',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('asin', sa.String(20), unique=True, nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('brand', sa.String(255)),
        sa.Column('category_id', postgresql.UUID(as_uuid=True)),
        sa.Column('images', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
    )

    # ... 其他表

def downgrade():
    """回滚"""
    op.drop_table('products')
    # ...
```

---

**下一步**: 查看 [04_AI_INTEGRATION.md](./04_AI_INTEGRATION.md) 了解 AI 集成方案
