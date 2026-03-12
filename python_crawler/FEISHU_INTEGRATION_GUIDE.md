# 飞书多维表格集成指南

## 目录

1. [概述](#一概述)
2. [飞书开放平台配置](#二飞书开放平台配置)
3. [多维表格结构设计](#三多维表格结构设计)
4. [代码实现](#四代码实现)
5. [集成到爬虫](#五集成到爬虫)
6. [自动化同步](#六自动化同步)
7. [常见问题](#七常见问题)

---

## 一、概述

### 1.1 为什么选择飞书多维表格

| 优势 | 说明 |
|------|------|
| 🆓 **免费使用** | 个人/小团队免费额度充足 |
| 📊 **多维视图** | 支持表格、看板、甘特图等多种视图 |
| 🔄 **实时协作** | 团队成员可同时编辑 |
| 🔗 **API 开放** | 完善的 API 接口支持 |
| 📱 **移动端** | 手机 App 随时查看 |
| 🤖 **自动化** | 支持飞书自动化流程 |

### 1.2 集成架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                     数据同步架构                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌──────────────┐         ┌──────────────┐         ┌──────────┐  │
│   │ Amazon 爬虫   │ ──────▶ │  数据处理层   │ ──────▶ │ 飞书 API  │  │
│   │              │         │              │         │          │  │
│   │ - Playwright │         │ - 格式转换    │         │ - 认证   │  │
│   │ - CSV 导出   │         │ - 字段映射    │         │ - 写入   │  │
│   └──────────────┘         │ - 数据验证    │         │ - 更新   │  │
│                            └──────────────┘         └────┬─────┘  │
│                                                           │        │
│                                                           ▼        │
│                                                     ┌──────────┐  │
│                                                     │ 多维表格  │  │
│                                                     │          │  │
│                                                     │ - 商品表  │  │
│                                                     │ - 选品表  │  │
│                                                     │ - 统计表  │  │
│                                                     └──────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.3 数据流程

```
爬虫抓取商品数据
       │
       ▼
  ┌─────────┐
  │ CSV 存储 │
  └────┬────┘
       │
       ▼
  ┌─────────────┐
  │ FeishuClient │ ← 飞书 API 封装
  └────┬────────┘
       │
       ├──────────────────────────────────┐
       │                                  │
       ▼                                  ▼
  ┌─────────┐                      ┌─────────────┐
  │ 新增商品 │                      │ 更新已有商品 │
  │ (添加记录)│                      │ (按 ASIN 匹配)│
  └─────────┘                      └─────────────┘
       │                                  │
       └──────────────┬───────────────────┘
                      │
                      ▼
               ┌──────────┐
               │ 多维表格  │
               └──────────┘
```

---

## 二、飞书开放平台配置

### 2.1 创建应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 登录后点击「开发者后台」
3. 点击「创建企业自建应用」

   ```
   应用名称: Amazon商品同步
   应用描述: 自动同步Amazon商品数据到多维表格
   应用图标: 上传一个图标
   ```

4. 创建完成后，记录以下信息：

   ```
   App ID: cli_xxxxxxxxxxxx
   App Secret: xxxxxxxxxxxxxxxxxxxxxxxx
   ```

### 2.2 配置权限

在应用管理页面，进入「权限管理」：

**必要权限：**

| 权限名称 | 权限 ID | 用途 |
|----------|---------|------|
| 查看、评论、编辑和管理多维表格 | `bitable:record` | 读写记录 |
| 查看多维表格 | `bitable:record:read` | 读取记录 |
| 新增多维表格数据 | `bitable:record:write` | 写入记录 |

**配置步骤：**

1. 搜索权限名称
2. 点击「申请权限」
3. 选择「所有员工可见」或「仅管理员可见」
4. 发布版本使权限生效

### 2.3 创建多维表格

1. 打开飞书，进入「多维表格」
2. 创建新的多维表格：`Amazon商品库`

3. 记录表格信息：

   ```
   多维表格 URL: https://xxx.feishu.cn/base/xxxxxxxxxxxxx
                                    ↑
                              这是 app_token
   ```

4. 创建数据表（Sheet），记录 `table_id`

---

## 三、多维表格结构设计

### 3.1 商品主表 (Products)

| 字段名 | 字段类型 | 字段 ID | 说明 |
|--------|----------|---------|------|
| ASIN | 文本 | `fldxxxxxx` | 商品唯一标识，设为主键 |
| 商品标题 | 文本 | `fldxxxxxx` | 商品名称 |
| 价格 | 数字 | `fldxxxxxx` | 当前价格 |
| 原价 | 数字 | `fldxxxxxx` | 原价（如有折扣） |
| 评分 | 数字 | `fldxxxxxx` | 评分 (1-5) |
| 评论数 | 数字 | `fldxxxxxx` | 评论总数 |
| 商品描述 | 多行文本 | `fldxxxxxx` | 商品详情描述 |
| 图片链接 | 超链接 | `fldxxxxxx` | 主图 URL |
| 图片数量 | 数字 | `fldxxxxxx` | 图片总数 |
| 变体数量 | 数字 | `fldxxxxxx` | 颜色/尺寸变体数 |
| 颜色变体 | 多选 | `fldxxxxxx` | 可选颜色列表 |
| 尺寸变体 | 多选 | `fldxxxxxx` | 可选尺寸列表 |
| 库存状态 | 单选 | `fldxxxxxx` | In Stock / Low Stock / Out of Stock |
| 配送信息 | 文本 | `fldxxxxxx` | 配送方式 |
| 是否 Prime | 复选框 | `fldxxxxxx` | Prime 标识 |
| 商品链接 | 超链接 | `fldxxxxxx` | Amazon 商品页 |
| 分类 | 单选 | `fldxxxxxx` | 商品分类 |
| 综合得分 | 数字 | `fldxxxxxx` | 选品评分 (0-100) |
| 风险等级 | 单选 | `fldxxxxxx` | 低/中/高 |
| 同步时间 | 日期 | `fldxxxxxx` | 最后同步时间 |
| 数据来源 | 单选 | `fldxxxxxx` | Best Sellers / New Releases / 搜索 |

### 3.2 选品推荐表 (Recommendations)

| 字段名 | 字段类型 | 说明 |
|--------|----------|------|
| 关联商品 | 关联 | 关联到商品主表 |
| 推荐日期 | 日期 | 生成推荐的时间 |
| 综合得分 | 数字 | 0-100 |
| 推荐级别 | 单选 | 强烈推荐 / 推荐 / 一般 |
| 风险等级 | 单选 | 低/中/高 |
| 优势标签 | 多选 | 高评分、低价、多变体等 |
| 风险标签 | 多选 | 评分低、评论少、价格高等 |
| 推荐理由 | 多行文本 | AI 生成的推荐理由 |
| 状态 | 单选 | 待处理 / 已选 / 已放弃 |

### 3.3 同步日志表 (SyncLogs)

| 字段名 | 字段类型 | 说明 |
|--------|----------|------|
| 同步时间 | 日期 | 同步执行时间 |
| 同步类型 | 单选 | 全量 / 增量 |
| 新增数量 | 数字 | 新增记录数 |
| 更新数量 | 数字 | 更新记录数 |
| 失败数量 | 数字 | 失败记录数 |
| 同步状态 | 单选 | 成功 / 部分成功 / 失败 |
| 错误信息 | 多行文本 | 错误详情 |

---

## 四、代码实现

### 4.1 项目结构

```
python_crawler/
├── src/
│   ├── feishu/                  # 飞书集成模块
│   │   ├── __init__.py
│   │   ├── client.py            # API 客户端
│   │   ├── bitable.py           # 多维表格操作
│   │   ├── mapper.py            # 字段映射
│   │   └── config.py            # 配置
│   ├── selection/               # 选品模块
│   └── ...
├── config/
│   └── feishu_config.yaml       # 飞书配置文件
└── .env                         # 环境变量（敏感信息）
```

### 4.2 配置文件

**config/feishu_config.yaml**

```yaml
# 飞书应用配置
app_id: "${FEISHU_APP_ID}"
app_secret: "${FEISHU_APP_SECRET}"

# 多维表格配置
bitable:
  app_token: "${FEISHU_APP_TOKEN}"
  tables:
    products:
      table_id: "${FEISHU_PRODUCTS_TABLE_ID}"
      name: "商品主表"
    recommendations:
      table_id: "${FEISHU_RECOMMENDATIONS_TABLE_ID}"
      name: "选品推荐表"
    logs:
      table_id: "${FEISHU_LOGS_TABLE_ID}"
      name: "同步日志表"

# 字段映射配置
field_mapping:
  products:
    asin: "ASIN"
    title: "商品标题"
    price: "价格"
    rating: "评分"
    review_count: "评论数"
    description: "商品描述"
    images: "图片链接"
    image_count: "图片数量"
    total_variants: "变体数量"
    color_variants: "颜色变体"
    size_variants: "尺寸变体"
    stock_status: "库存状态"
    shipping_info: "配送信息"
    is_prime: "是否 Prime"
    url: "商品链接"
    category: "分类"
    total_score: "综合得分"
    risk_level: "风险等级"
    sync_time: "同步时间"
    source: "数据来源"

# 同步配置
sync:
  batch_size: 100        # 每批处理数量
  retry_times: 3         # 重试次数
  retry_delay: 1         # 重试延迟(秒)
```

**.env**

```bash
# 飞书应用凭证
FEISHU_APP_ID=cli_xxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx

# 多维表格配置
FEISHU_APP_TOKEN=xxxxxxxxxxxxxx
FEISHU_PRODUCTS_TABLE_ID=tblxxxxxxxx
FEISHU_RECOMMENDATIONS_TABLE_ID=tblxxxxxxxx
FEISHU_LOGS_TABLE_ID=tblxxxxxxxx
```

### 4.3 API 客户端 (client.py)

```python
# src/feishu/client.py

"""
飞书 API 客户端
封装飞书开放平台的认证和 API 调用
"""

import os
import time
import logging
import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass
import yaml

logger = logging.getLogger(__name__)


@dataclass
class FeishuConfig:
    """飞书配置"""
    app_id: str
    app_secret: str
    app_token: str
    tables: Dict[str, Dict[str, str]]
    field_mapping: Dict[str, Dict[str, str]]
    sync: Dict[str, Any]


class FeishuClient:
    """飞书 API 客户端"""
    
    BASE_URL = "https://open.feishu.cn/open-apis"
    
    def __init__(self, config_path: str = "config/feishu_config.yaml"):
        """
        初始化客户端
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.access_token: Optional[str] = None
        self.token_expire_time: int = 0
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def _load_config(self, config_path: str) -> FeishuConfig:
        """加载配置文件"""
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        # 替换环境变量
        def replace_env(value):
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_key = value[2:-1]
                return os.environ.get(env_key, "")
            return value
        
        def process_dict(d):
            if isinstance(d, dict):
                return {k: process_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [process_dict(i) for i in d]
            elif isinstance(d, str):
                return replace_env(d)
            return d
        
        config = process_dict(config)
        
        return FeishuConfig(
            app_id=config["app_id"],
            app_secret=config["app_secret"],
            app_token=config["bitable"]["app_token"],
            tables=config["bitable"]["tables"],
            field_mapping=config["field_mapping"],
            sync=config.get("sync", {})
        )
    
    def _get_access_token(self) -> str:
        """获取访问令牌"""
        # 检查是否需要刷新
        if self.access_token and time.time() < self.token_expire_time - 60:
            return self.access_token
        
        url = f"{self.BASE_URL}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.config.app_id,
            "app_secret": self.config.app_secret
        }
        
        response = self.session.post(url, json=payload)
        result = response.json()
        
        if result.get("code") != 0:
            raise Exception(f"获取 access_token 失败: {result.get('msg')}")
        
        self.access_token = result["tenant_access_token"]
        self.token_expire_time = time.time() + result.get("expire", 7200)
        
        logger.info("✅ 成功获取飞书 access_token")
        return self.access_token
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Dict = None,
        params: Dict = None
    ) -> Dict:
        """
        发送 API 请求
        
        Args:
            method: HTTP 方法 (GET/POST/PUT/DELETE)
            endpoint: API 端点
            data: 请求体数据
            params: URL 参数
        
        Returns:
            API 响应
        """
        token = self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        url = f"{self.BASE_URL}{endpoint}"
        
        for attempt in range(self.config.sync.get("retry_times", 3)):
            try:
                if method.upper() == "GET":
                    response = self.session.get(url, headers=headers, params=params)
                elif method.upper() == "POST":
                    response = self.session.post(url, headers=headers, json=data)
                elif method.upper() == "PUT":
                    response = self.session.put(url, headers=headers, json=data)
                elif method.upper() == "DELETE":
                    response = self.session.delete(url, headers=headers, json=data)
                else:
                    raise ValueError(f"不支持的 HTTP 方法: {method}")
                
                result = response.json()
                
                if result.get("code") == 0:
                    return result.get("data", {})
                
                # 处理特定错误
                if result.get("code") == 99991663:
                    # token 过期，刷新后重试
                    self.access_token = None
                    continue
                
                logger.warning(f"API 请求失败 (尝试 {attempt + 1}): {result.get('msg')}")
                
            except requests.RequestException as e:
                logger.warning(f"网络请求异常 (尝试 {attempt + 1}): {e}")
            
            time.sleep(self.config.sync.get("retry_delay", 1))
        
        raise Exception(f"API 请求失败: {endpoint}")
    
    # ========== 多维表格操作 ==========
    
    def list_records(
        self,
        table_id: str,
        view_id: str = None,
        field_names: list = None,
        filter_condition: str = None,
        sort: list = None,
        page_size: int = 500,
        page_token: str = None
    ) -> Dict:
        """
        获取记录列表
        
        Args:
            table_id: 数据表 ID
            view_id: 视图 ID
            field_names: 返回的字段列表
            filter_condition: 过滤条件
            sort: 排序条件
            page_size: 每页数量
            page_token: 分页标记
        
        Returns:
            记录数据
        """
        endpoint = f"/bitable/v1/apps/{self.config.app_token}/tables/{table_id}/records/search"
        
        data = {"automatic_fields": False}
        
        if view_id:
            data["view_id"] = view_id
        if field_names:
            data["field_names"] = field_names
        if filter_condition:
            data["filter"] = filter_condition
        if sort:
            data["sort"] = sort
        if page_size:
            data["page_size"] = min(page_size, 500)
        if page_token:
            data["page_token"] = page_token
        
        return self._request("POST", endpoint, data=data)
    
    def get_record(self, table_id: str, record_id: str) -> Dict:
        """
        获取单条记录
        
        Args:
            table_id: 数据表 ID
            record_id: 记录 ID
        
        Returns:
            记录数据
        """
        endpoint = f"/bitable/v1/apps/{self.config.app_token}/tables/{table_id}/records/{record_id}"
        return self._request("GET", endpoint)
    
    def create_record(self, table_id: str, fields: Dict) -> Dict:
        """
        创建记录
        
        Args:
            table_id: 数据表 ID
            fields: 字段数据
        
        Returns:
            创建的记录
        """
        endpoint = f"/bitable/v1/apps/{self.config.app_token}/tables/{table_id}/records"
        data = {"fields": fields}
        return self._request("POST", endpoint, data=data)
    
    def create_records_batch(self, table_id: str, records: list) -> Dict:
        """
        批量创建记录
        
        Args:
            table_id: 数据表 ID
            records: 记录列表 [{"fields": {...}}, ...]
        
        Returns:
            创建结果
        """
        endpoint = f"/bitable/v1/apps/{self.config.app_token}/tables/{table_id}/records/batch_create"
        data = {"records": records}
        return self._request("POST", endpoint, data=data)
    
    def update_record(self, table_id: str, record_id: str, fields: Dict) -> Dict:
        """
        更新记录
        
        Args:
            table_id: 数据表 ID
            record_id: 记录 ID
            fields: 更新的字段数据
        
        Returns:
            更新的记录
        """
        endpoint = f"/bitable/v1/apps/{self.config.app_token}/tables/{table_id}/records/{record_id}"
        data = {"fields": fields}
        return self._request("PUT", endpoint, data=data)
    
    def update_records_batch(self, table_id: str, records: list) -> Dict:
        """
        批量更新记录
        
        Args:
            table_id: 数据表 ID
            records: 记录列表 [{"record_id": "xxx", "fields": {...}}, ...]
        
        Returns:
            更新结果
        """
        endpoint = f"/bitable/v1/apps/{self.config.app_token}/tables/{table_id}/records/batch_update"
        data = {"records": records}
        return self._request("POST", endpoint, data=data)
    
    def delete_record(self, table_id: str, record_id: str) -> Dict:
        """
        删除记录
        
        Args:
            table_id: 数据表 ID
            record_id: 记录 ID
        
        Returns:
            删除结果
        """
        endpoint = f"/bitable/v1/apps/{self.config.app_token}/tables/{table_id}/records/{record_id}"
        return self._request("DELETE", endpoint)
    
    def delete_records_batch(self, table_id: str, record_ids: list) -> Dict:
        """
        批量删除记录
        
        Args:
            table_id: 数据表 ID
            record_ids: 记录 ID 列表
        
        Returns:
            删除结果
        """
        endpoint = f"/bitable/v1/apps/{self.config.app_token}/tables/{table_id}/records/batch_delete"
        data = {"records": record_ids}
        return self._request("POST", endpoint, data=data)
    
    # ========== 字段操作 ==========
    
    def list_fields(self, table_id: str) -> list:
        """
        获取字段列表
        
        Args:
            table_id: 数据表 ID
        
        Returns:
            字段列表
        """
        endpoint = f"/bitable/v1/apps/{self.config.app_token}/tables/{table_id}/fields"
        result = self._request("GET", endpoint)
        return result.get("items", [])
    
    def get_field_id_by_name(self, table_id: str, field_name: str) -> Optional[str]:
        """
        根据字段名获取字段 ID
        
        Args:
            table_id: 数据表 ID
            field_name: 字段名
        
        Returns:
            字段 ID
        """
        fields = self.list_fields(table_id)
        for field in fields:
            if field.get("field_name") == field_name:
                return field.get("field_id")
        return None
```

### 4.4 字段映射器 (mapper.py)

```python
# src/feishu/mapper.py

"""
字段映射器
将爬虫数据映射为飞书多维表格字段格式
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import re


class FieldMapper:
    """字段映射器"""
    
    # 字段类型映射
    FIELD_TYPES = {
        "text": 1,           # 文本
        "number": 2,         # 数字
        "single_select": 3,  # 单选
        "multi_select": 4,   # 多选
        "date": 5,           # 日期
        "checkbox": 7,       # 复选框
        "url": 15,           # 超链接
        "attachment": 17,    # 附件
        "relation": 18,      # 关联
    }
    
    def __init__(self, field_mapping: Dict[str, str]):
        """
        初始化映射器
        
        Args:
            field_mapping: 字段名映射 {爬虫字段名: 飞书字段名}
        """
        self.field_mapping = field_mapping
    
    def map_product_to_feishu(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        将商品数据映射为飞书记录格式
        
        Args:
            product: 商品数据字典
        
        Returns:
            飞书记录格式 {"字段名": 值}
        """
        feishu_record = {}
        
        for source_field, target_field in self.field_mapping.items():
            value = product.get(source_field)
            
            if value is None:
                continue
            
            # 根据目标字段类型转换值
            mapped_value = self._convert_value(source_field, value, target_field)
            
            if mapped_value is not None:
                feishu_record[target_field] = mapped_value
        
        # 添加同步时间
        feishu_record["同步时间"] = int(datetime.now().timestamp() * 1000)
        
        return feishu_record
    
    def _convert_value(
        self,
        source_field: str,
        value: Any,
        target_field: str
    ) -> Any:
        """
        根据字段类型转换值
        
        Args:
            source_field: 源字段名
            value: 原始值
            target_field: 目标字段名
        
        Returns:
            转换后的值
        """
        # 价格字段
        if "price" in source_field.lower() or "价格" in target_field:
            return self._extract_number(value)
        
        # 评分字段
        if "rating" in source_field.lower() or "评分" in target_field:
            return self._extract_number(value)
        
        # 数量字段
        if any(k in source_field.lower() for k in ["count", "_num", "variants", "reviews"]):
            return self._extract_number(value)
        
        # 布尔字段
        if target_field in ["是否 Prime", "是否 FBA"]:
            return self._to_bool(value)
        
        # 多选字段 (颜色、尺寸变体)
        if target_field in ["颜色变体", "尺寸变体", "优势标签", "风险标签"]:
            return self._to_multi_select(value)
        
        # 单选字段
        if target_field in ["库存状态", "风险等级", "推荐级别", "状态"]:
            return self._to_single_select(value)
        
        # 超链接字段
        if "链接" in target_field or "url" in source_field.lower():
            return self._to_link(value, target_field)
        
        # 日期字段
        if "时间" in target_field or "日期" in target_field:
            return self._to_timestamp(value)
        
        # 默认返回文本
        return str(value) if value else None
    
    def _extract_number(self, value: Any) -> Optional[float]:
        """从值中提取数字"""
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # 移除货币符号和逗号
            cleaned = re.sub(r"[\$,\,\€\¥]", "", value)
            # 提取第一个数字
            match = re.search(r"[-+]?\d*\.?\d+", cleaned)
            if match:
                return float(match.group())
        
        return None
    
    def _to_bool(self, value: Any) -> bool:
        """转换为布尔值"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ["true", "yes", "1", "是"]
        return bool(value)
    
    def _to_multi_select(self, value: Any) -> List[str]:
        """转换为多选格式"""
        if isinstance(value, list):
            return value
        
        if isinstance(value, str):
            # 分隔符处理
            if "|" in value:
                return [v.strip() for v in value.split("|") if v.strip()]
            if "," in value:
                return [v.strip() for v in value.split(",") if v.strip()]
            if value.strip():
                return [value.strip()]
        
        return []
    
    def _to_single_select(self, value: Any) -> Optional[str]:
        """转换为单选格式"""
        if value is None:
            return None
        
        value_str = str(value).strip()
        
        # 风险等级映射
        risk_mapping = {
            "LOW": "低风险",
            "MEDIUM": "中风险",
            "HIGH": "高风险",
            "低风险": "低风险",
            "中风险": "中风险",
            "高风险": "高风险",
        }
        if value_str in risk_mapping:
            return risk_mapping[value_str]
        
        return value_str if value_str else None
    
    def _to_link(self, value: Any, text: str = None) -> Dict:
        """转换为超链接格式"""
        if not value:
            return None
        
        url = str(value)
        if not url.startswith("http"):
            return None
        
        return {
            "link": url,
            "text": text or url
        }
    
    def _to_timestamp(self, value: Any) -> Optional[int]:
        """转换为时间戳 (毫秒)"""
        if isinstance(value, (int, float)):
            # 假设已经是时间戳
            if value < 10000000000:
                return int(value * 1000)
            return int(value)
        
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return int(dt.timestamp() * 1000)
            except ValueError:
                pass
        
        return None
    
    def map_feishu_to_product(self, feishu_record: Dict) -> Dict[str, Any]:
        """
        将飞书记录转换回商品数据格式
        
        Args:
            feishu_record: 飞书记录
        
        Returns:
            商品数据字典
        """
        product = {}
        
        # 反向映射
        reverse_mapping = {v: k for k, v in self.field_mapping.items()}
        
        for field_name, field_value in feishu_record.items():
            source_field = reverse_mapping.get(field_name)
            
            if source_field:
                # 提取实际值
                if isinstance(field_value, dict):
                    # 超链接
                    if "link" in field_value:
                        product[source_field] = field_value["link"]
                    # 单选
                    elif "id" in field_value:
                        product[source_field] = field_value.get("text", "")
                elif isinstance(field_value, list):
                    # 多选
                    product[source_field] = [v.get("text", v) if isinstance(v, dict) else v for v in field_value]
                else:
                    product[source_field] = field_value
        
        return product
```

### 4.5 多维表格同步器 (bitable.py)

```python
# src/feishu/bitable.py

"""
多维表格同步器
负责将商品数据同步到飞书多维表格
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd

from .client import FeishuClient, FeishuConfig
from .mapper import FieldMapper

logger = logging.getLogger(__name__)


class BitableSyncer:
    """多维表格同步器"""
    
    def __init__(self, client: FeishuClient):
        """
        初始化同步器
        
        Args:
            client: 飞书客户端
        """
        self.client = client
        self.config = client.config
        
        # 初始化字段映射器
        self.product_mapper = FieldMapper(
            self.config.field_mapping.get("products", {})
        )
        
        # 缓存现有记录
        self._existing_records: Dict[str, str] = {}  # {asin: record_id}
    
    def sync_products(
        self,
        products: List[Dict],
        mode: str = "upsert",
        batch_size: int = None
    ) -> Dict:
        """
        同步商品数据到多维表格
        
        Args:
            products: 商品列表
            mode: 同步模式 (insert/replace/upsert)
            batch_size: 批量大小
        
        Returns:
            同步结果统计
        """
        batch_size = batch_size or self.config.sync.get("batch_size", 100)
        table_id = self.config.tables["products"]["table_id"]
        
        stats = {
            "total": len(products),
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "failed": 0,
            "errors": []
        }
        
        logger.info(f"开始同步 {len(products)} 个商品到飞书多维表格...")
        
        # 获取现有记录 (用于 upsert)
        if mode == "upsert":
            self._load_existing_records(table_id)
        
        # 分批处理
        for i in range(0, len(products), batch_size):
            batch = products[i:i + batch_size]
            
            if mode == "upsert":
                created, updated, failed, errors = self._upsert_batch(table_id, batch)
                stats["created"] += created
                stats["updated"] += updated
                stats["failed"] += failed
                stats["errors"].extend(errors)
            
            elif mode == "insert":
                created, failed, errors = self._insert_batch(table_id, batch)
                stats["created"] += created
                stats["failed"] += failed
                stats["errors"].extend(errors)
            
            elif mode == "replace":
                created, updated, failed, errors = self._replace_batch(table_id, batch)
                stats["created"] += created
                stats["updated"] += updated
                stats["failed"] += failed
                stats["errors"].extend(errors)
            
            logger.info(f"进度: {min(i + batch_size, len(products))}/{len(products)}")
        
        # 记录同步日志
        self._log_sync_result(stats)
        
        logger.info(f"同步完成: 新增 {stats['created']}, 更新 {stats['updated']}, 失败 {stats['failed']}")
        
        return stats
    
    def _load_existing_records(self, table_id: str):
        """加载现有记录"""
        logger.info("加载现有记录...")
        
        self._existing_records = {}
        page_token = None
        
        while True:
            result = self.client.list_records(
                table_id=table_id,
                field_names=["ASIN"],
                page_size=500,
                page_token=page_token
            )
            
            for record in result.get("items", []):
                fields = record.get("fields", {})
                asin = fields.get("ASIN")
                if asin:
                    self._existing_records[asin] = record.get("record_id")
            
            page_token = result.get("page_token")
            if not page_token:
                break
        
        logger.info(f"已加载 {len(self._existing_records)} 条现有记录")
    
    def _upsert_batch(
        self,
        table_id: str,
        products: List[Dict]
    ) -> Tuple[int, int, int, List[str]]:
        """批量 upsert"""
        to_create = []
        to_update = []
        errors = []
        
        for product in products:
            asin = product.get("asin")
            
            if not asin:
                errors.append(f"商品缺少 ASIN: {product.get('title', 'Unknown')}")
                continue
            
            fields = self.product_mapper.map_product_to_feishu(product)
            
            if asin in self._existing_records:
                # 更新
                to_update.append({
                    "record_id": self._existing_records[asin],
                    "fields": fields
                })
            else:
                # 新增
                to_create.append({"fields": fields})
        
        created = 0
        updated = 0
        failed = 0
        
        # 批量创建
        if to_create:
            try:
                self.client.create_records_batch(table_id, to_create)
                created = len(to_create)
            except Exception as e:
                errors.append(f"批量创建失败: {e}")
                failed += len(to_create)
        
        # 批量更新
        if to_update:
            try:
                self.client.update_records_batch(table_id, to_update)
                updated = len(to_update)
            except Exception as e:
                errors.append(f"批量更新失败: {e}")
                failed += len(to_update)
        
        return created, updated, failed, errors
    
    def _insert_batch(
        self,
        table_id: str,
        products: List[Dict]
    ) -> Tuple[int, int, List[str]]:
        """批量插入"""
        records = []
        errors = []
        
        for product in products:
            if not product.get("asin"):
                errors.append(f"商品缺少 ASIN: {product.get('title', 'Unknown')}")
                continue
            
            fields = self.product_mapper.map_product_to_feishu(product)
            records.append({"fields": fields})
        
        created = 0
        failed = 0
        
        if records:
            try:
                self.client.create_records_batch(table_id, records)
                created = len(records)
            except Exception as e:
                errors.append(f"批量插入失败: {e}")
                failed = len(records)
        
        return created, failed, errors
    
    def _replace_batch(
        self,
        table_id: str,
        products: List[Dict]
    ) -> Tuple[int, int, int, List[str]]:
        """批量替换 (先删除再插入)"""
        # 简化实现：直接用 upsert
        return self._upsert_batch(table_id, products)
    
    def _log_sync_result(self, stats: Dict):
        """记录同步结果到日志表"""
        logs_table_id = self.config.tables.get("logs", {}).get("table_id")
        
        if not logs_table_id:
            return
        
        log_record = {
            "fields": {
                "同步时间": int(datetime.now().timestamp() * 1000),
                "同步类型": "增量",
                "新增数量": stats["created"],
                "更新数量": stats["updated"],
                "失败数量": stats["failed"],
                "同步状态": "成功" if stats["failed"] == 0 else "部分成功",
                "错误信息": "\n".join(stats["errors"][:10]) if stats["errors"] else ""
            }
        }
        
        try:
            self.client.create_record(logs_table_id, log_record["fields"])
        except Exception as e:
            logger.warning(f"记录同步日志失败: {e}")
    
    def sync_from_csv(
        self,
        csv_path: str,
        mode: str = "upsert"
    ) -> Dict:
        """
        从 CSV 文件同步数据
        
        Args:
            csv_path: CSV 文件路径
            mode: 同步模式
        
        Returns:
            同步结果
        """
        df = pd.read_csv(csv_path)
        products = df.to_dict("records")
        
        return self.sync_products(products, mode=mode)
    
    def get_products_by_asins(self, asins: List[str]) -> List[Dict]:
        """
        根据 ASIN 获取商品记录
        
        Args:
            asins: ASIN 列表
        
        Returns:
            商品记录列表
        """
        table_id = self.config.tables["products"]["table_id"]
        
        # 构建过滤条件
        filter_condition = {
            "conjunction": "or",
            "conditions": [
                {
                    "field_name": "ASIN",
                    "operator": "is",
                    "value": [asin]
                }
                for asin in asins[:50]  # 限制条件数量
            ]
        }
        
        result = self.client.list_records(
            table_id=table_id,
            filter_condition=filter_condition
        )
        
        return [
            self.product_mapper.map_feishu_to_product(r.get("fields", {}))
            for r in result.get("items", [])
        ]
    
    def clear_table(self, table_id: str = None):
        """
        清空表格数据
        
        Args:
            table_id: 表格 ID，默认为商品表
        """
        table_id = table_id or self.config.tables["products"]["table_id"]
        
        logger.info(f"开始清空表格: {table_id}")
        
        # 获取所有记录 ID
        record_ids = []
        page_token = None
        
        while True:
            result = self.client.list_records(
                table_id=table_id,
                page_size=500,
                page_token=page_token
            )
            
            record_ids.extend([
                r.get("record_id") for r in result.get("items", [])
            ])
            
            page_token = result.get("page_token")
            if not page_token:
                break
        
        # 批量删除
        if record_ids:
            for i in range(0, len(record_ids), 500):
                batch = record_ids[i:i + 500]
                self.client.delete_records_batch(table_id, batch)
        
        logger.info(f"已删除 {len(record_ids)} 条记录")
```

### 4.6 模块初始化 (__init__.py)

```python
# src/feishu/__init__.py

"""飞书集成模块"""

from .client import FeishuClient, FeishuConfig
from .bitable import BitableSyncer
from .mapper import FieldMapper

__all__ = [
    "FeishuClient",
    "FeishuConfig",
    "BitableSyncer",
    "FieldMapper",
]
```

---

## 五、集成到爬虫

### 5.1 修改爬虫支持飞书同步

在 `src/crawler.py` 中添加飞书同步功能：

```python
# 在 AmazonCrawler 类中添加

def run_with_feishu_sync(
    self,
    pages: int = 1,
    products_per_page: int = 5,
    sync_to_feishu: bool = True,
    feishu_config_path: str = "config/feishu_config.yaml"
) -> List[Dict]:
    """
    运行爬虫并同步到飞书
    
    Args:
        pages: 爬取页数
        products_per_page: 每页商品数
        sync_to_feishu: 是否同步到飞书
        feishu_config_path: 飞书配置文件路径
    
    Returns:
        商品列表
    """
    # 1. 运行爬虫
    products = self.run(pages, products_per_page)
    
    # 2. 同步到飞书
    if sync_to_feishu and products:
        try:
            from src.feishu import FeishuClient, BitableSyncer
            
            client = FeishuClient(feishu_config_path)
            syncer = BitableSyncer(client)
            
            stats = syncer.sync_products(products, mode="upsert")
            
            self.logger.info(f"飞书同步完成: 新增 {stats['created']}, 更新 {stats['updated']}")
            
        except Exception as e:
            self.logger.error(f"飞书同步失败: {e}")
    
    return products
```

### 5.2 添加命令行参数

在 `main.py` 中添加飞书同步选项：

```python
# main.py

import argparse

def main():
    parser = argparse.ArgumentParser(description="Amazon Best Sellers 爬虫")
    
    # 现有参数
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument("--pages", type=int, default=1)
    parser.add_argument("--products", type=int, default=5)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--output", default="output/amazon_products.csv")
    
    # 新增飞书同步参数
    parser.add_argument("--sync-feishu", action="store_true", help="同步到飞书多维表格")
    parser.add_argument("--feishu-config", default="config/feishu_config.yaml", help="飞书配置文件路径")
    
    args = parser.parse_args()
    
    # ... 运行爬虫 ...
    
    # 同步到飞书
    if args.sync_feishu:
        try:
            from src.feishu import FeishuClient, BitableSyncer
            
            logger.info("开始同步到飞书...")
            
            client = FeishuClient(args.feishu_config)
            syncer = BitableSyncer(client)
            
            stats = syncer.sync_from_csv(args.output)
            
            logger.info(f"同步完成: 新增 {stats['created']}, 更新 {stats['updated']}, 失败 {stats['failed']}")
            
        except Exception as e:
            logger.error(f"飞书同步失败: {e}")

if __name__ == "__main__":
    main()
```

### 5.3 使用方法

```bash
# 爬取并同步到飞书
uv run python main.py --pages 2 --products 20 --sync-feishu

# 仅同步已有 CSV 到飞书
uv run python -c "
from src.feishu import FeishuClient, BitableSyncer

client = FeishuClient('config/feishu_config.yaml')
syncer = BitableSyncer(client)
stats = syncer.sync_from_csv('output/amazon_products.csv')
print(f'同步完成: {stats}')
"
```

---

## 六、自动化同步

### 6.1 定时同步脚本

创建 `sync_to_feishu.py`：

```python
# sync_to_feishu.py

"""
飞书自动同步脚本
可与 scheduler.py 配合使用
"""

import os
import sys
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.feishu import FeishuClient, BitableSyncer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def sync_csv_to_feishu(
    csv_path: str = "output/amazon_products.csv",
    config_path: str = "config/feishu_config.yaml",
    mode: str = "upsert"
):
    """
    同步 CSV 数据到飞书
    
    Args:
        csv_path: CSV 文件路径
        config_path: 飞书配置文件路径
        mode: 同步模式
    """
    logger.info(f"开始同步 {csv_path} 到飞书...")
    
    try:
        client = FeishuClient(config_path)
        syncer = BitableSyncer(client)
        
        stats = syncer.sync_from_csv(csv_path, mode=mode)
        
        logger.info(f"✅ 同步完成:")
        logger.info(f"   - 总数: {stats['total']}")
        logger.info(f"   - 新增: {stats['created']}")
        logger.info(f"   - 更新: {stats['updated']}")
        logger.info(f"   - 失败: {stats['failed']}")
        
        if stats['errors']:
            logger.warning(f"   - 错误: {len(stats['errors'])} 条")
            for error in stats['errors'][:5]:
                logger.warning(f"     {error}")
        
        return stats
        
    except FileNotFoundError as e:
        logger.error(f"❌ 文件不存在: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ 同步失败: {e}")
        return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="同步数据到飞书多维表格")
    parser.add_argument("--csv", default="output/amazon_products.csv", help="CSV 文件路径")
    parser.add_argument("--config", default="config/feishu_config.yaml", help="飞书配置文件")
    parser.add_argument("--mode", default="upsert", choices=["insert", "upsert", "replace"], help="同步模式")
    
    args = parser.parse_args()
    
    sync_csv_to_feishu(args.csv, args.config, args.mode)
```

### 6.2 集成到定时任务

在 `scheduler.py` 中添加飞书同步：

```python
# 在 SelectionScheduler.job() 方法中添加

def job(self):
    """定时任务：爬取 + 选品 + 同步"""
    logger.info("=" * 60)
    logger.info(f"📅 开始执行定时任务: {datetime.now()}")
    
    # 1. 运行爬虫
    if self.run_crawler():
        # 2. 运行选品
        recommendations = self.run_selection()
        
        # 3. 同步到飞书
        if self.sync_to_feishu:
            self.run_feishu_sync()
    
    logger.info("=" * 60)
    logger.info("✅ 定时任务完成")

def run_feishu_sync(self):
    """同步数据到飞书"""
    logger.info("📤 开始同步到飞书...")
    
    try:
        from src.feishu import FeishuClient, BitableSyncer
        
        client = FeishuClient("config/feishu_config.yaml")
        syncer = BitableSyncer(client)
        
        stats = syncer.sync_from_csv(self.csv_path)
        
        logger.info(f"✅ 飞书同步完成: 新增 {stats['created']}, 更新 {stats['updated']}")
        
    except Exception as e:
        logger.error(f"❌ 飞书同步失败: {e}")
```

---

## 七、常见问题

### 7.1 认证失败

**问题**: `获取 access_token 失败`

**解决方案**:
1. 检查 App ID 和 App Secret 是否正确
2. 确认应用已发布并启用
3. 检查 IP 白名单设置

```bash
# 验证配置
python -c "
from src.feishu import FeishuClient
client = FeishuClient('config/feishu_config.yaml')
print(f'App ID: {client.config.app_id}')
print(f'App Token: {client.config.app_token}')
"
```

### 7.2 权限不足

**问题**: `API 请求失败: permission denied`

**解决方案**:
1. 检查应用是否有 `bitable:record` 权限
2. 确认多维表格已共享给应用
3. 发布新版本使权限生效

### 7.3 字段类型不匹配

**问题**: `字段类型不匹配`

**解决方案**:
1. 检查多维表格字段类型设置
2. 调整 `mapper.py` 中的类型转换逻辑
3. 确保字段名称与配置一致

```python
# 调试字段类型
from src.feishu import FeishuClient

client = FeishuClient()
fields = client.list_fields(table_id)
for field in fields:
    print(f"{field['field_name']}: type={field['type']}")
```

### 7.4 批量操作限制

**问题**: `批量操作数量超限`

**解决方案**:
- 单次批量操作最多 500 条
- 调整 `batch_size` 配置参数
- 分批次处理大数据量

### 7.5 网络超时

**问题**: `请求超时`

**解决方案**:
1. 检查网络连接
2. 增加重试次数和延迟
3. 使用代理（如需要）

```yaml
# config/feishu_config.yaml
sync:
  batch_size: 50       # 减小批次大小
  retry_times: 5       # 增加重试次数
  retry_delay: 3       # 增加延迟
```

---

## 八、完整使用示例

### 8.1 初始化配置

```bash
# 1. 创建配置目录
mkdir -p config

# 2. 创建配置文件
cp config/feishu_config.yaml.example config/feishu_config.yaml

# 3. 设置环境变量
export FEISHU_APP_ID="cli_xxxxxxxxxxxx"
export FEISHU_APP_SECRET="xxxxxxxxxxxxxxxxxxxxxxxx"
export FEISHU_APP_TOKEN="xxxxxxxxxxxxxx"
export FEISHU_PRODUCTS_TABLE_ID="tblxxxxxxxx"

# 4. 或使用 .env 文件
echo "FEISHU_APP_ID=cli_xxxxxxxxxxxx" >> .env
echo "FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx" >> .env
```

### 8.2 运行同步

```bash
# 爬取并同步
uv run python main.py --pages 2 --products 20 --sync-feishu

# 单独同步
python sync_to_feishu.py --csv output/amazon_products.csv

# 定时同步 (每天 8:00)
python scheduler.py --time 08:00 --sync-feishu
```

### 8.3 验证结果

在飞书多维表格中查看：
1. 打开多维表格
2. 确认数据已同步
3. 检查字段值是否正确
4. 查看同步日志表

---

## 九、总结

### 9.1 实现清单

| 功能 | 状态 | 文件 |
|------|------|------|
| 飞书 API 客户端 | ✅ | `src/feishu/client.py` |
| 字段映射器 | ✅ | `src/feishu/mapper.py` |
| 多维表格同步器 | ✅ | `src/feishu/bitable.py` |
| 配置管理 | ✅ | `config/feishu_config.yaml` |
| 同步脚本 | ✅ | `sync_to_feishu.py` |
| 定时集成 | ✅ | `scheduler.py` |

### 9.2 扩展方向

1. **飞书机器人通知** - 同步完成后发送消息通知
2. **自动化流程** - 使用飞书自动化功能
3. **数据看板** - 创建飞书仪表盘
4. **审批流程** - 选品审批工作流

---

*文档版本: v1.0*
*创建时间: 2026-03-12*
