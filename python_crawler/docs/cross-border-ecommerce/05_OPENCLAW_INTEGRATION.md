# OpenClaw 消息网关集成

> **跨境电商全工作流系统** - 消息控制与通知中心

**版本**: v1.0.0
**更新时间**: 2026-03-12

---

## 目录

1. [OpenClaw 简介](#openclaw-简介)
2. [集成架构](#集成架构)
3. [Skill 开发](#skill-开发)
4. [消息处理](#消息处理)
5. [通知系统](#通知系统)
6. [安全配置](#安全配置)

---

## OpenClaw 简介

### 什么是 OpenClaw

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          OpenClaw 网关                                   │
│                    (自托管 AI Agent 消息网关)                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  Telegram   │  │  WhatsApp   │  │  Discord    │  │  iMessage   │   │
│  │             │  │             │  │             │  │             │   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘   │
│         │                │                │                │           │
│         └────────────────┼────────────────┼────────────────┘           │
│                          │                │                            │
│                          ▼                ▼                            │
│              ┌─────────────────────────────────┐                       │
│              │      OpenClaw Gateway           │                       │
│              │      (端口: 18789)              │                       │
│              ├─────────────────────────────────┤                       │
│              │  • 消息路由                     │                       │
│              │  • Agent 控制                   │                       │
│              │  • Skill 调用                   │                       │
│              │  • 认证授权                     │                       │
│              └───────────────┬─────────────────┘                       │
│                              │                                          │
│                              ▼                                          │
│              ┌─────────────────────────────────┐                       │
│              │     AI Agent / Backend API      │                       │
│              │  (本系统的 Python 服务)         │                       │
│              └─────────────────────────────────┘                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 核心功能

| 功能 | 说明 |
|------|------|
| **多渠道支持** | Telegram, WhatsApp, Discord, iMessage, Email |
| **双向通信** | 接收指令 + 推送通知 |
| **Skill 系统** | AgentSkills 兼容的技能扩展 |
| **认证授权** | 用户白名单、群组管理 |
| **消息路由** | 智能分发到对应 Agent |

---

## 集成架构

### 系统集成图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      OpenClaw 集成架构                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  用户消息                                                               │
│    │                                                                    │
│    ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    消息渠道                                      │   │
│  │  Telegram / WhatsApp / Discord                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│    │                                                                    │
│    ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                 OpenClaw Gateway (18789)                         │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │ 消息解析器    │  │  路由引擎     │  │  认证模块     │          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│    │                                                                    │
│    ├───────────────────────────────────────────────────────────────┐   │
│    │                                                               │   │
│    ▼ (指令)                                              ▼ (通知)     │
│  ┌─────────────────────┐                             ┌─────────────────┐│
│  │  Backend API        │                             │  Notification  ││
│  │  (FastAPI)          │                             │  Service       ││
│  │                     │                             │                ││
│  │  /api/v1/commands   │                             │  • 推送告警     ││
│  │  /api/v1/tasks      │                             │  • 状态更新     ││
│  │  /api/v1/query      │                             │  • 报告生成     ││
│  └─────────────────────┘                             └─────────────────┘│
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 数据流向

```
指令流向:
Telegram → OpenClaw → Backend API → 业务处理 → 结果返回 → OpenClaw → Telegram

通知流向:
Backend API → Notification Service → OpenClaw → Telegram/WhatsApp/Discord
```

---

## Skill 开发

### Skill 目录结构

```
~/.openclaw/skills/
├── ecommerce/                    # 主 Skill 目录
│   ├── SKILL.md                 # Skill 定义
│   ├── run.sh                   # 执行脚本
│   ├── config.yaml              # 配置文件
│   └── lib/                     # 辅助函数
│       ├── parser.py
│       └── formatter.py
│
├── ecommerce-selection/         # 选品子模块
├── ecommerce-creative/          # 创作子模块
└── ecommerce-customer/          # 客服子模块
```

### 主 Skill 定义

```markdown
# SKILL.md

---
name: ecommerce
description: Amazon E-commerce Automation System. Control your entire e-commerce workflow through messages - product selection, AI creative, operations, customer service, and financial analysis.
metadata: {
  "openclaw": {
    "emoji": "🛒",
    "category": "automation",
    "requires": {
      "bins": ["python3", "uv"],
      "services": ["api:8000"]
    },
    "config": {
      "apiEndpoint": "http://localhost:8000",
      "timeout": 300
    }
  }
}
---

# Amazon E-commerce Automation System

## Overview

Complete control of your Amazon e-commerce business through chat messages.

## Quick Commands

### Product Selection
```
/ecommerce selection analyze --asin B0XXX
/ecommerce selection trends --category electronics
/ecommerce selection profit --asin B0XXX --cost 50
```

### AI Creative
```
/ecommerce creative image --input product.jpg --scenes white,living
/ecommerce creative copy --asin B0XXX --language en
/ecommerce creative keywords --asin B0XXX
```

### Operations
```
/ecommerce ops list --status active
/ecommerce ops price --asin B0XXX --price 29.99
/ecommerce ops inventory --asin B0XXX --quantity 100
```

### Customer Service
```
/ecommerce cs messages --unread
/ecommerce cs reply --message-id 123 --auto
/ecommerce cs refund --order-id 111-1111111-1111111
```

### Finance
```
/ecommerce finance revenue --today
/ecommerce finance profit --month 2026-03
/ecommerce finance cashflow --forecast 30d
```

## Full Workflow

Complete pipeline from product selection to launch:
```
/ecommerce pipeline --asin B0XXX --auto
```
```

### 执行脚本

```bash
#!/bin/bash
# ~/.openclaw/skills/ecommerce/run.sh

set -e

# 配置
API_ENDPOINT="${API_ENDPOINT:-http://localhost:8000}"
TIMEOUT="${TIMEOUT:-300}"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 日志
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 帮助
show_help() {
    echo "🛒 Amazon E-commerce Automation System"
    echo ""
    echo "Usage: $0 <module> <command> [options]"
    echo ""
    echo "Modules:"
    echo "  selection  - Product selection and analysis"
    echo "  creative   - AI creative tools"
    echo "  ops        - Operations management"
    echo "  cs         - Customer service"
    echo "  finance    - Financial analysis"
    echo ""
    echo "Examples:"
    echo "  $0 selection analyze --asin B0XXX"
    echo "  $0 creative image --input product.jpg"
    echo "  $0 cs messages --unread"
}

# API 调用
api_call() {
    local endpoint=$1
    shift
    local params="$@"

    log_info "Calling API: $endpoint"

    response=$(curl -s -X POST \
        "${API_ENDPOINT}${endpoint}" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${OPENCLAW_API_TOKEN}" \
        -d "$params" \
        --max-time $TIMEOUT
    )

    echo "$response"
}

# 解析命令
MODULE=$1
COMMAND=$2
shift 2 || true

case "$MODULE" in
    selection)
        case "$COMMAND" in
            analyze)
                log_info "分析产品: $@"
                api_call "/api/v1/selection/analyze" "{\"asin\":\"$1\"}"
                ;;
            trends)
                log_info "趋势分析: $@"
                api_call "/api/v1/selection/trends" "{\"category\":\"$1\"}"
                ;;
            profit)
                log_info "利润计算: $@"
                api_call "/api/v1/selection/profit" "{\"asin\":\"$1\",\"cost\":$2}"
                ;;
            *)
                log_error "Unknown command: $COMMAND"
                ;;
        esac
        ;;

    creative)
        case "$COMMAND" in
            image)
                log_info "AI 图片生成..."
                api_call "/api/v1/ai/image/generate-product-set" "{\"image_path\":\"$1\"}"
                ;;
            copy)
                log_info "AI 文案生成..."
                api_call "/api/v1/ai/copywriting/generate" "{\"asin\":\"$1\"}"
                ;;
            *)
                log_error "Unknown command: $COMMAND"
                ;;
        esac
        ;;

    ops)
        case "$COMMAND" in
            list)
                log_info "获取上架列表..."
                api_call "/api/v1/operations/listings"
                ;;
            price)
                log_info "更新价格..."
                api_call "/api/v1/operations/update-price" "{\"asin\":\"$1\",\"price\":$2}"
                ;;
            *)
                log_error "Unknown command: $COMMAND"
                ;;
        esac
        ;;

    cs)
        case "$COMMAND" in
            messages)
                log_info "获取未读消息..."
                api_call "/api/v1/customer/messages" "{\"status\":\"unread\"}"
                ;;
            reply)
                log_info "AI 自动回复..."
                api_call "/api/v1/customer/auto-reply" "{\"message_id\":$1}"
                ;;
            *)
                log_error "Unknown command: $COMMAND"
                ;;
        esac
        ;;

    finance)
        case "$COMMAND" in
            revenue)
                log_info "收入统计..."
                api_call "/api/v1/finance/revenue" "{\"period\":\"today\"}"
                ;;
            profit)
                log_info "利润分析..."
                api_call "/api/v1/finance/profit" "{\"period\":\"month\"}"
                ;;
            *)
                log_error "Unknown command: $COMMAND"
                ;;
        esac
        ;;

    *)
        log_error "Unknown module: $MODULE"
        show_help
        exit 1
        ;;
esac
```

---

## 消息处理

### 消息路由

```python
# backend/api/routes/openclaw.py
from fastapi import APIRouter, HTTPException
from typing import Optional

router = APIRouter(prefix="/api/v1/openclaw", tags=["OpenClaw"])

class MessageRouter:
    """OpenClaw 消息路由器"""

    def __init__(self):
        self.routes = {
            "selection": SelectionHandler(),
            "creative": CreativeHandler(),
            "operations": OperationsHandler(),
            "customer": CustomerHandler(),
            "finance": FinanceHandler(),
        }

    async def route_message(
        self,
        channel: str,
        sender: str,
        message: str
    ) -> str:
        """路由消息到对应处理器"""
        try:
            # 解析消息
            parsed = self.parse_message(message)

            # 获取处理器
            handler = self.routes.get(parsed.module)
            if not handler:
                return f"❌ 未知模块: {parsed.module}"

            # 执行命令
            result = await handler.execute(parsed.command, parsed.params)

            # 格式化响应
            return self.format_response(result)

        except Exception as e:
            return f"❌ 错误: {str(e)}"

    def parse_message(self, message: str) -> ParsedMessage:
        """解析消息"""
        # 支持多种格式:
        # /ecommerce selection analyze --asin B0XXX
        # selection analyze B0XXX
        # 分析产品 B0XXX

        # 简化实现
        parts = message.strip().split()
        return ParsedMessage(
            module=parts[1] if len(parts) > 1 else None,
            command=parts[2] if len(parts) > 2 else None,
            params=parts[3:]
        )

    def format_response(self, result: dict) -> str:
        """格式化响应"""
        if result.get("success"):
            return f"✅ {result.get('message', '操作成功')}"
        else:
            return f"❌ {result.get('error', '操作失败')}"

router = MessageRouter()

@router.post("/command")
async def handle_command(request: OpenClawCommand):
    """处理来自 OpenClaw 的命令"""
    result = await router.route_message(
        channel=request.channel,
        sender=request.sender,
        message=request.message
    )
    return {"response": result}
```

---

## 通知系统

### 通知类型

```python
# backend/services/notification/openclaw_notifier.py

from typing import List, Dict
import httpx

class OpenClawNotifier:
    """OpenClaw 通知服务"""

    def __init__(self, gateway_url: str = "http://localhost:18789"):
        self.gateway_url = gateway_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def send_notification(
        self,
        channels: List[str],
        message: str,
        recipients: List[str] = None,
        priority: str = "normal"
    ):
        """
        发送通知

        Args:
            channels: 渠道列表 ["telegram", "whatsapp"]
            message: 消息内容
            recipients: 接收者列表
            priority: 优先级 (low, normal, high, urgent)
        """
        payload = {
            "channels": channels,
            "message": message,
            "recipients": recipients or [],
            "priority": priority
        }

        response = await self.client.post(
            f"{self.gateway_url}/api/v1/notify",
            json=payload
        )

        return response.json()

    # 预定义通知模板
    async def notify_order_received(self, order: dict):
        """新订单通知"""
        message = f"""
🛒 新订单通知

订单号: {order['amazon_order_id']}
客户: {order['customer_name']}
金额: {order['currency']} {order['total']}
市场: {order['marketplace']}

时间: {order['order_date']}
        """.strip()

        await self.send_notification(
            channels=["telegram"],
            message=message,
            priority="high"
        )

    async def notify_low_inventory(self, product: dict, current: int, threshold: int):
        """库存不足告警"""
        message = f"""
⚠️ 库存不足告警

产品: {product['title']}
ASIN: {product['asin']}
当前库存: {current}
告警阈值: {threshold}

请及时补货！
        """.strip()

        await self.send_notification(
            channels=["telegram", "whatsapp"],
            message=message,
            priority="urgent"
        )

    async def notify_customer_message(self, message: dict):
        """客户消息通知"""
        msg_type = "📧 新消息"
        if message.get("sentiment") == "negative":
            msg_type = "🚨 负面消息"

        text = f"""
{msg_type}

客户: {message['customer_name']}
渠道: {message['channel']}
内容: {message['body'][:100]}...

请及时回复！
        """.strip()

        await self.send_notification(
            channels=["telegram"],
            message=text,
            priority="high" if message.get("sentiment") == "negative" else "normal"
        )

    async def notify_daily_report(self, report: dict):
        """每日报告"""
        message = f"""
📊 每日运营报告

日期: {report['date']}

📈 收入: ${report['revenue']:.2f}
📦 订单: {report['orders']}
🛍️ 新上架: {report['new_listings']}
💬 未读消息: {report['unread_messages']}

🔗 查看详情: {report['dashboard_url']}
        """.strip()

        await self.send_notification(
            channels=["telegram"],
            message=message,
            priority="normal"
        )
```

### 自动化通知规则

```python
# backend/services/notification/rules.py

NOTIFICATION_RULES = {
    "order_events": {
        "received": {"notify": True, "priority": "high"},
        "shipped": {"notify": True, "priority": "normal"},
        "delivered": {"notify": True, "priority": "normal"},
        "cancelled": {"notify": True, "priority": "high"},
        "refund_requested": {"notify": True, "priority": "urgent"},
    },
    "inventory": {
        "low_stock": {"threshold": 10, "notify": True, "priority": "urgent"},
        "out_of_stock": {"threshold": 0, "notify": True, "priority": "urgent"},
    },
    "customer_service": {
        "new_message": {"notify": True, "priority": "normal"},
        "negative_sentiment": {"notify": True, "priority": "high"},
        "refund_request": {"notify": True, "priority": "urgent"},
    },
    "finance": {
        "daily_report": {"schedule": "0 18 * * *", "notify": True},
        "low_cashflow": {"threshold": 5000, "notify": True, "priority": "urgent"},
    }
}
```

---

## 安全配置

### 认证授权

```python
# backend/api/middleware/openclaw_auth.py

from fastapi import Security, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

ALLOWED_SENDERS = {
    "telegram": ["@your_username", "@trusted_contact"],
    "whatsapp": ["+15550101"],
    "discord": ["your_discord_id"]
}

async def verify_openclaw_request(
    channel: str,
    sender: str,
    token: str
) -> bool:
    """验证 OpenClaw 请求"""

    # 1. 验证 Token
    if token != os.getenv("OPENCLAW_API_TOKEN"):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    # 2. 验证发送者白名单
    allowed = ALLOWED_SENDERS.get(channel, [])
    if allowed and sender not in allowed:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Sender not authorized"
        )

    return True
```

---

**下一步**: 查看 [07_DEPLOYMENT.md](./07_DEPLOYMENT.md)
