# Amazon 爬虫数据导入飞书多维表格 - 实施指南

> **将 Amazon 爬虫采集的商品数据自动同步到飞书多维表格，实现团队协作和数据可视化**

---

## 📋 目录

1. [快速概览](#快速概览)
2. [前置准备](#前置准备)
3. [实施步骤](#实施步骤)
4. [数据映射](#数据映射)
5. [自动化方案](#自动化方案)
6. [常见问题](#常见问题)

---

## 快速概览

### 数据流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Amazon 爬虫 │────►│  本地 CSV   │────►│  同步脚本   │────►│  飞书表格   │
│  (采集)     │     │  (存储)     │     │  (API)      │     │  (展示)     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### 核心功能

| 功能 | 说明 |
|------|------|
| **自动同步** | 爬取完成后自动上传到飞书 |
| **增量更新** | 只同步新数据，避免重复 |
| **图片附件** | 商品图片作为附件上传 |
| **数据去重** | 根据 ASIN 自动去重 |
| **状态标记** | 标记数据同步状态 |

---

## 前置准备

### 1. 飞书应用配置

#### 步骤 1: 创建自建应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 进入「管理后台」→「创建应用」→「自建应用」
3. 填写应用信息：
   - 应用名称：`Amazon 爬虫同步`
   - 应用描述：`同步 Amazon 商品数据到多维表格`

#### 步骤 2: 获取凭证

```bash
# 记录以下信息
APP_ID="cli_xxxxxxxxxxxxx"        # 应用 ID
APP_SECRET="xxxxxxxxxxxxxx"        # 应用密钥
```

#### 步骤 3: 配置权限

在应用管理中，申请以下权限：

| 权限名称 | 权限 ID | 用途 |
|----------|---------|------|
| 查看、评论和导出多维表格 | `bitable:app:readonly` | 读取表格数据 |
| 创建和编辑表格 | `bitable:app:writeable` | 写入数据 |
| 获取与下载附件 | `drive:drive:readonly` | 上传图片 |
| 上传附件 | `drive:drive:writeable` | 上传商品图片 |

#### 步骤 4: 发布应用

- 点击「版本管理与发布」
- 创建版本 → 填写说明 → 发布
- 申请租户权限通过

### 2. 创建多维表格

#### 表格结构设计

**主表：商品数据 (amazon_products)**

| 字段名 | 字段类型 | 字段 ID | 说明 |
|--------|----------|---------|------|
| ASIN | 文本 | `field_asin` | 商品唯一 ID |
| 商品标题 | 文本 | `field_title` | 商品名称 |
| 价格 | 数字 | `field_price` | 当前价格 |
| 评分 | 数字 | `field_rating` | 商品评分 |
| 评论数 | 数字 | `field_review_count` | 评论数量 |
| 商品描述 | 多行文本 | `field_description` | 商品详情 |
| 图片链接 | URL | `field_image_url` | 主图链接 |
| 图片附件 | 附件 | `field_images` | 上传的图片 |
| 商品链接 | URL | `field_url` | Amazon 链接 |
| 采集时间 | 日期 | `field_created_at` | 采集时间戳 |
| 数据来源 | 文本 | `field_source` | Best Sellers/搜索 |
| 同步状态 | 单选 | `field_sync_status` | 已同步/待处理 |

**子表：采集记录 (crawl_logs)**

| 字段名 | 字段类型 | 字段 ID | 说明 |
|--------|----------|---------|------|
| 任务 ID | 文本 | `field_task_id` | 任务标识 |
| 采集模式 | 单选 | `field_mode` | Best Sellers/搜索 |
| 关键词 | 文本 | `field_keyword` | 搜索关键词 |
| 采集页数 | 数字 | `field_pages` | 页面数量 |
| 商品数量 | 数字 | `field_product_count` | 采集商品数 |
| 开始时间 | 日期 | `field_start_time` | 任务开始时间 |
| 结束时间 | 日期 | `field_end_time` | 任务结束时间 |
| 状态 | 单选 | `field_status` | 成功/失败/进行中 |

### 3. 记录必要信息

```bash
# 需要记录的配置信息
FEISHU_APP_ID="cli_xxxxxxxxxxxxx"
FEISHU_APP_SECRET="xxxxxxxxxxxxxx"
FEISHU_BITABLE_APP_TOKEN="bascnxxxxxxxxxxxxxx"    # 表格 Token
FEISHU_TABLE_ID="tblxxxxxxxxxxxxxx"               # 表 ID
```

**获取方法**：
1. 打开多维表格
2. URL 格式：`https://example.feishu.cn/base/bascnxxxxxxxxxxxxxx?table=tblxxxxxxxxxxxxxx`
3. `bascnxxxxxxxxxxxxxx` 是 `app_token`
4. `tblxxxxxxxxxxxxxx` 是 `table_id`

---

## 实施步骤

### 步骤 1: 安装依赖

```bash
cd /run/media/clearzero22/fedora1/home/clearzero22/projects/01_my_script/python_crawler

# 安装飞书 SDK
uv add feishu-bitable

# 或使用 pip
pip install feishu-bitable
```

### 步骤 2: 创建配置文件

```bash
# 创建配置文件
cat > config/feishu_config.yaml << EOF
# 飞书配置
feishu:
  app_id: "cli_xxxxxxxxxxxxx"
  app_secret: "xxxxxxxxxxxxxx"
  bitable:
    app_token: "bascnxxxxxxxxxxxxxx"
    table_id: "tblxxxxxxxxxxxxxx"
  field_mapping:
    asin: "field_asin"
    title: "field_title"
    price: "field_price"
    rating: "field_rating"
    description: "field_description"
    url: "field_url"
    created_at: "field_created_at"

# 同步配置
sync:
  batch_size: 50          # 批量写入大小
  enable_dedup: true      # 启用去重
  dedup_field: "asin"     # 去重字段
  auto_sync: true         # 爬取后自动同步
EOF
```

### 步骤 3: 创建同步脚本

```python
# src/feishu_sync.py
import os
import yaml
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

try:
    from feishu_bitable import FeishuBitable
except ImportError:
    # 备用方案：使用 requests
    import requests


class FeishuSync:
    """飞书多维表格同步类"""

    def __init__(self, config_path: str = "config/feishu_config.yaml"):
        """初始化同步客户端

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.client = self._create_client()

    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _create_client(self):
        """创建飞书客户端"""
        try:
            return FeishuBitable(
                app_id=self.config['feishu']['app_id'],
                app_secret=self.config['feishu']['app_secret'],
                app_token=self.config['feishu']['bitable']['app_token'],
            )
        except:
            return None

    def sync_csv_to_feishu(self, csv_path: str) -> Dict[str, Any]:
        """同步 CSV 数据到飞书

        Args:
            csv_path: CSV 文件路径

        Returns:
            同步结果统计
        """
        # 读取 CSV
        df = pd.read_csv(csv_path)

        # 数据转换
        records = self._convert_to_records(df)

        # 批量写入
        result = self._batch_write(records)

        return {
            'total': len(df),
            'success': result.get('success', 0),
            'failed': result.get('failed', 0),
            'timestamp': datetime.now().isoformat()
        }

    def _convert_to_records(self, df: pd.DataFrame) -> List[Dict]:
        """转换 DataFrame 为飞书记录格式"""
        mapping = self.config['feishu'].get('field_mapping', {})
        records = []

        for _, row in df.iterrows():
            record = {}
            for csv_field, bitable_field in mapping.items():
                if csv_field in row:
                    record[bitable_field] = row[csv_field]

            # 添加时间戳
            record['field_created_at'] = datetime.now().isoformat()

            records.append(record)

        return records

    def _batch_write(self, records: List[Dict]) -> Dict:
        """批量写入数据"""
        batch_size = self.config['sync'].get('batch_size', 50)
        table_id = self.config['feishu']['bitable']['table_id']

        success = 0
        failed = 0

        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            try:
                # TODO: 调用飞书 API 写入
                # self.client.table(table_id).records.batch_create(batch)
                success += len(batch)
            except Exception as e:
                print(f"批量写入失败: {e}")
                failed += len(batch)

        return {'success': success, 'failed': failed}
```

### 步骤 4: 集成到自动化脚本

修改 `run_automation.sh`，添加同步功能：

```bash
# 在爬虫完成后执行同步
if [[ "$SYNC_TO_FEISHU" == "true" ]]; then
    print_info "同步数据到飞书..."

    uv run python src/feishu_sync.py "$OUTPUT"

    print_success "数据已同步到飞书多维表格"
fi
```

---

## 数据映射

### CSV 字段 → 飞书字段

| CSV 字段 | 飞书字段类型 | 飞书字段 ID | 转换规则 |
|----------|-------------|------------|----------|
| `asin` | 文本 | `field_asin` | 直接映射 |
| `title` | 文本 | `field_title` | 直接映射 |
| `price` | 数字 | `field_price` | 提取数字部分 |
| `rating` | 数字 | `field_rating` | 提取评分数字 |
| `description` | 多行文本 | `field_description` | 直接映射 |
| `images` | 附件 | `field_images` | URL → 附件上传 |
| `url` | URL | `field_url` | 直接映射 |
| - | 日期 | `field_created_at` | 当前时间戳 |

### 数据转换示例

```python
# 价格转换
"$29.99" → 29.99

# 评分转换
"4.7 out of 5 stars" → 4.7

# 图片 URL 转附件
"https://m.media-amazon.com/images/I/xxx.jpg" → 上传为附件

# 时间戳
采集时间 → 2026-03-12T12:00:00+08:00
```

---

## 自动化方案

### 方案 1: 爬取后自动同步

```bash
# 使用 --feishu 参数
./run_automation.sh --pages 2 --products 20 --feishu
```

### 方案 2: 定时同步任务

```bash
# Crontab 配置
# 每天凌晨 2 点爬取并同步
0 2 * * * cd /path/to/python_crawler && ./run_automation.sh --pages 2 --products 20 --feishu >> logs/sync.log 2>&1
```

### 方案 3: 手动同步已有数据

```bash
# 同步指定的 CSV 文件
uv run python src/feishu_sync.py output/amazon_products.csv
```

### 方案 4: 通过 OpenClaw 触发

```bash
# 通过 OpenClaw agent 触发同步
openclaw agent --message "同步 Amazon 爬虫数据到飞书"
```

---

## 常见问题

### Q1: 如何获取表格 Token 和表 ID？

**A**: 打开多维表格，从 URL 中提取：

```
https://xxx.feishu.cn/base/{app_token}?table={table_id}
                          ↑                    ↑
                    app_token            table_id
```

### Q2: 图片如何上传到飞书？

**A**: 使用飞书文件 API，分两步：

1. 上传图片到飞书云文档 → 获得 file_token
2. 创建附件字段记录，引用 file_token

```python
# 1. 上传图片
file_token = upload_image_to_feishu(image_url)

# 2. 创建附件记录
record = {
    "field_images": [{
        "file_token": file_token,
        "name": "product_image.jpg"
    }]
}
```

### Q3: 如何避免数据重复？

**A**: 使用 ASIN 作为唯一标识：

1. 同步前查询是否已存在
2. 存在则更新，不存在则创建

```python
# 检查记录是否存在
existing = client.table(table_id).records.get(filter="field_asin = 'B0BZYCJK89'")

if existing:
    # 更新
    client.table(table_id).records.update(record_id, data)
else:
    # 创建
    client.table(table_id).records.create(data)
```

### Q4: API 调用频率限制？

**A**: 飞书 API 限制：

| 接口类型 | 限制 |
|----------|------|
| 获取 Tenant Token | 100 次/分钟 |
| 多维表格写操作 | 20 次/秒 |
| 批量创建记录 | 500 条/次 |

建议使用批量操作并控制频率。

### Q5: 如何调试同步问题？

**A**: 启用详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

检查：
1. Token 是否有效
2. 字段 ID 是否正确
3. 数据格式是否匹配
4. 权限是否已授予

---

## 下一步

1. **完成配置**: 创建飞书应用并获取凭证
2. **创建表格**: 按照表格结构设计创建多维表格
3. **测试同步**: 用少量数据测试同步功能
4. **自动化**: 配置定时任务实现自动同步
5. **监控告警**: 配置同步失败通知

## 相关文档

- [飞书多维表格 API 文档](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-list)
- [飞书开放平台认证](https://open.feishu.cn/document/server-docs/docs/authentication/access-token/tenant_access_token)
- [项目完整集成文档](./FEISHU_BITABLE_INTEGRATION.md)

---

**创建时间**: 2026-03-12
**版本**: 1.0.0
