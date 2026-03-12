# 客服系统模块

> **跨境电商全工作流系统** - AI 智能客服与消息处理

**优先级**: ⭐⭐⭐⭐
**预计工作量**: 2-3 周

---

## 目录

1. [模块概述](#模块概述)
2. [功能设计](#功能设计)
3. [AI 客服](#ai-客服)
4. [消息聚合](#消息聚合)
5. [API 设计](#api-设计)

---

## 模块概述

### 业务价值

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AI 客服业务价值                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  传统客服方式:                                                           │
│  • 人工客服: ¥8,000-15,000/月                                          │
│  • 响应时间: 2-8 小时                                                 │
│  • 工作时间: 8-12 小时/天                                             │
│  • 语言限制: 只能客服懂的语言                                         │
│                                                                         │
│  AI 客服方式:                                                            │
│  • AI 成本: ¥500-1,000/月 (API 调用)                                  │
│  • 响应时间: < 30 秒                                                  │
│  • 工作时间: 24/7                                                      │
│  • 多语言: 支持 20+ 语言                                               │
│                                                                         │
│  成本节省: 70-90%                                                       │
│  响应速度: 95%+ 提升                                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 核心功能

| 功能 | 说明 | 优先级 |
|------|------|--------|
| **消息聚合** | 多渠道消息统一接入 | ⭐⭐⭐⭐⭐ |
| **AI 回复** | GPT-4 自动生成回复 | ⭐⭐⭐⭐⭐ |
| **知识库** | RAG 向量检索增强 | ⭐⭐⭐⭐ |
| **工单管理** | 状态跟踪、分类处理 | ⭐⭐⭐ |
| **退款处理** | 自动退款审核流程 | ⭐⭐⭐ |

---

## 功能设计

### 1. 消息聚合

#### 支持渠道

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          消息渠道集成                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Amazon Messages     │  Email    │  WhatsApp  │  Telegram  │         │
│                      │           │            │            │         │
│  ┌────────────────┐  │  ┌──────┐  │  ┌──────┐  │  ┌──────┐         │
│  │  • 买家消息   │  │  │SMTP │  │  │ API │  │  │ Bot  │         │
│  │  • 退货请求   │  │  │     │  │  │     │  │  │     │         │
│  │  • 商品咨询   │  │  └──────┘  │  └──────┘  │  └──────┘         │
│  └────────────────┘  │           │            │            │         │
│          │           │           │            │            │         │
│          └───────────┴───────────┴────────────┴────────────┘         │
│                          │                                            │
│                          ▼                                            │
│              ┌─────────────────────────────────┐                       │
│              │      Message Aggregator         │                       │
│              ├─────────────────────────────────┤                       │
│              │  • 统一数据格式                  │                       │
│              │  • 消息去重                      │                       │
│              │  • 优先级路由                    │                       │
│              │  • 实时推送                      │                       │
│              └─────────────────────────────────┘                       │
│                          │                                            │
│                          ▼                                            │
│              ┌─────────────────────────────────┐                       │
│              │      Message Database            │                       │
│              ├─────────────────────────────────┤                       │
│              │  • messages (消息主表)          │                       │
│              │  • conversations (对话)        │                       │
│              │  • customers (客户)            │                       │
│              │  • attachments (附件)          │                       │
│              └─────────────────────────────────┘                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 代码实现

```python
# backend/services/customer/message_aggregator.py

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum
import asyncio

class ChannelType(Enum):
    """消息渠道类型"""
    AMAZON = "amazon"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"

class MessagePriority(Enum):
    """消息优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class MessageAggregator:
    """消息聚合器"""

    def __init__(self, db, cache, notification_service):
        self.db = db
        self.cache = cache
        self.notification = notification_service
        self.adapters = {
            ChannelType.AMAZON: AmazonMessageAdapter(),
            ChannelType.EMAIL: EmailMessageAdapter(),
            ChannelType.WHATSAPP: WhatsAppMessageAdapter(),
            ChannelType.TELEGRAM: TelegramMessageAdapter(),
        }

    async def fetch_messages(
        self,
        channels: List[ChannelType] = None,
        since: datetime = None,
        limit: int = 100
    ) -> List[Dict]:
        """从多个渠道拉取消息"""
        if channels is None:
            channels = list(ChannelType)

        # 默认拉取最近 1 小时的消息
        if since is None:
            since = datetime.now() - timedelta(hours=1)

        tasks = [
            self._fetch_from_channel(channel, since, limit)
            for channel in channels
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 合并结果
        all_messages = []
        for result in results:
            if isinstance(result, Exception):
                print(f"Error fetching from channel: {result}")
                continue
            all_messages.extend(result)

        # 去重
        unique_messages = self._deduplicate_messages(all_messages)

        # 按优先级排序
        sorted_messages = self._sort_by_priority(unique_messages)

        return sorted_messages[:limit]

    async def _fetch_from_channel(
        self,
        channel: ChannelType,
        since: datetime,
        limit: int
    ) -> List[Dict]:
        """从单个渠道拉取消息"""
        adapter = self.adapters[channel]
        return await adapter.fetch_messages(since, limit)

    def _deduplicate_messages(self, messages: List[Dict]) -> List[Dict]:
        """消息去重"""
        seen = set()
        unique = []

        for msg in messages:
            # 使用内容哈希去重
            content_hash = self._hash_message(msg)
            if content_hash not in seen:
                seen.add(content_hash)
                unique.append(msg)

        return unique

    def _hash_message(self, message: Dict) -> str:
        """计算消息哈希"""
        import hashlib
        content = f"{message.get('channel')}:{message.get('sender')}:{message.get('body')}"
        return hashlib.md5(content.encode()).hexdigest()

    def _sort_by_priority(self, messages: List[Dict]) -> List[Dict]:
        """按优先级排序"""
        priority_order = {
            MessagePriority.URGENT: 4,
            MessagePriority.HIGH: 3,
            MessagePriority.NORMAL: 2,
            MessagePriority.LOW: 1
        }

        return sorted(
            messages,
            key=lambda m: priority_order.get(
                m.get("priority", MessagePriority.NORMAL),
                2
            ),
            reverse=True
        )

    async def process_message(self, message: Dict):
        """处理新消息"""
        # 1. 意图识别
        intent = await self._classify_intent(message)

        # 2. 情感分析
        sentiment = await self._analyze_sentiment(message)

        # 3. 优先级评估
        priority = self._determine_priority(intent, sentiment)

        # 4. 保存到数据库
        await self._save_message(message, intent, sentiment, priority)

        # 5. 通知相关人员
        if priority in [MessagePriority.HIGH, MessagePriority.URGENT]:
            await self.notification.send_notification(
                "新紧急消息",
                message,
                priority=priority.value
            )

    async def _classify_intent(self, message: Dict) -> str:
        """分类消息意图"""
        body = message.get("body", "").lower()

        # 简单关键词匹配
        if any(word in body for word in ["refund", "return", "退货", "退款"]):
            return "refund_request"
        elif any(word in body for word in ["shipping", "delivery", "物流", "配送"]):
            return "shipping_inquiry"
        elif any(word in body for word in ["damaged", "defective", "损坏", "有问题"]):
            return "product_issue"
        elif any(word in body for word in ["cancel", "取消"]):
            return "cancellation_request"
        elif any(word in body for word in ["price", "discount", "价格", "折扣"]):
            return "pricing_inquiry"
        else:
            return "general_inquiry"

    async def _analyze_sentiment(self, message: Dict) -> str:
        """分析情感"""
        # 使用 GPT-4 或传统 NLP
        # 简化实现
        body = message.get("body", "")

        # 简单规则
        negative_words = ["disappointed", "terrible", "worst", "angry", "frustrated"]
        positive_words = ["great", "excellent", "happy", "satisfied", "love"]

        neg_count = sum(1 for word in negative_words if word.lower() in body.lower())
        pos_count = sum(1 for word in positive_words if word.lower() in body.lower())

        if neg_count > pos_count:
            return "negative"
        elif pos_count > neg_count:
            return "positive"
        else:
            return "neutral"
```

### 2. AI 客服 (RAG)

#### 架构设计

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         RAG (检索增强生成)                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  用户消息                                                               │
│    │                                                                    │
│    ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  意图识别                                                        │   │
│  │  • 分类: 退款/物流/产品/一般                                     │   │
│  │  • 情感: 积极/中性/负面                                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│    │                                                                    │
│    ├───────────────────────────────────────────────────────────────┐   │
│    │                                                               │   │
│    ▼ (简单问题)                                        ▼ (复杂问题)       │   │
│  ┌───────────────────┐                             ┌───────────────┐   │
│  │  FAQ 检索         │                             │  LLM 生成     │   │
│  │  • 知识库查询      │                             │  • GPT-4       │   │
│  │  • 返回标准答案    │                             │  • 上下文理解   │   │
│  └───────────────────┘                             └───────────────┘   │
│         │                                                       │       │   │
│         └───────────────────────────────────────────────────────┘       │   │
│                              │                                            │   │
│                              ▼                                            │   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  回复后处理                                                      │   │
│  │  • 多语言翻译                                                    │   │
│  │  • 语气调整                                                      │   │
│  │  • 合规检查                                                      │   │
│  │  • 人工审核 (高优先级)                                          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 代码实现

```python
# backend/services/customer/ai_agent.py

from typing import List, Dict, Optional
from datetime import datetime
import openai

class AICustomerServiceAgent:
    """AI 客服代理"""

    def __init__(self, vector_db, llm_client):
        self.vector_db = vector_db
        self.llm = llm_client

    async def generate_reply(
        self,
        message: Dict,
        conversation_history: List[Dict] = None,
        customer_data: Dict = None
    ) -> Dict:
        """
        生成 AI 回复

        Args:
            message: 当前消息
            conversation_history: 对话历史
            customer_data: 客户数据

        Returns:
            {
                "reply": "生成的回复",
                "confidence": 0.95,
                "suggested_actions": ["退款", "换货"],
                "requires_human": false
            }
        """
        # 1. 分析意图
        intent = message.get("intent")
        sentiment = message.get("sentiment")

        # 2. 检索相关知识
        knowledge = await self._retrieve_knowledge(message, intent)

        # 3. 构建提示词
        prompt = self._build_prompt(
            message,
            knowledge,
            conversation_history,
            customer_data
        )

        # 4. 生成回复
        if knowledge and knowledge.get("confidence", 0) > 0.8:
            # 知识库匹配度高，直接使用
            reply = knowledge["answer"]
            confidence = knowledge["confidence"]
            requires_human = False
        else:
            # 使用 LLM 生成
            llm_response = await self._call_llm(prompt)
            reply = llm_response["text"]
            confidence = llm_response.get("confidence", 0.7)
            requires_human = confidence < 0.7 or sentiment == "negative"

        # 5. 提取建议操作
        suggested_actions = self._extract_actions(reply, intent)

        return {
            "reply": reply,
            "confidence": confidence,
            "suggested_actions": suggested_actions,
            "requires_human": requires_human,
            "intent": intent,
            "sentiment": sentiment
        }

    async def _retrieve_knowledge(
        self,
        message: Dict,
        intent: str
    ) -> Optional[Dict]:
        """从知识库检索相关信息"""
        query = message.get("body", "")

        # 向量搜索
        results = await self.vector_db.search(
            query=query,
            filter={"intent": intent},
            top_k=3
        )

        if results and results[0]["score"] > 0.8:
            return results[0]

        return None

    def _build_prompt(
        self,
        message: Dict,
        knowledge: Optional[Dict],
        history: List[Dict],
        customer: Dict
    ) -> str:
        """构建 LLM 提示词"""
        system_prompt = """你是一个专业的 Amazon 卖家客服 AI 助手。

你的职责:
1. 准确理解客户问题
2. 提供专业、友好的回复
3. 在需要时主动提供解决方案
4. 保持耐心和同理心

回复风格:
- 专业但亲切
- 简洁明了
- 提供具体解决方案
- 遇到不确定的问题，建议转人工客服"""

        user_content = f"客户问题: {message.get('body')}"

        if knowledge:
            user_content += f"\n相关知识: {knowledge.get('answer', '')}"

        if history:
            history_text = "\n".join([
                f"{'客服' if msg.get('direction') == 'outbound' else '客户'}: {msg.get('body')}"
                for msg in history[-5:]  # 最近 5 条
            ])
            user_content += f"\n对话历史:\n{history_text}"

        if customer:
            user_content += f"\n客户信息: {customer.get('name')} (购买 {customer.get('total_orders')} 次)"

        prompt = f"{system_prompt}\n\n{user_content}\n\n请生成回复:"

        return prompt

    async def _call_llm(self, prompt: str) -> Dict:
        """调用 LLM"""
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "你是一个专业的客服"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        return {
            "text": response.choices[0].message.content,
            "confidence": 0.85
        }

    def _extract_actions(self, reply: str, intent: str) -> List[str]:
        """从回复中提取建议操作"""
        actions = []

        # 根据意图提供操作建议
        if intent == "refund_request":
            actions = ["处理退款", "询问原因", "提供退货地址"]
        elif intent == "shipping_inquiry":
            actions = ["查询物流", "催促发货", "解释延迟"]
        elif intent == "product_issue":
            actions = ["换货", "退款", "补偿方案"]

        return actions
```

### 3. 退款处理

```python
# backend/services/customer/refund_processor.py

from typing import Dict, List
from decimal import Decimal

class RefundProcessor:
    """退款处理器"""

    async def evaluate_refund_request(
        self,
        order_id: str,
        reason: str,
        order_days: int,
        item_condition: str
    ) -> Dict:
        """
        评估退款请求

        Returns:
            {
                "approved": true,
                "refund_amount": 29.99,
                "return_label": "https://...",
                "reason": "decision_reason"
            }
        """
        # 退款规则
        policies = {
            "within_30_days": {
                "full_refund": True,
                "customer_pays_shipping": False
            },
            "30_to_180_days": {
                "full_refund": False,
                "partial_refund": True,
                "customer_pays_shipping": True
            },
            "after_180_days": {
                "full_refund": False,
                "refund": False,
                "manual_review": True
            }
        }

        # 根据规则评估
        if order_days <= 30:
            policy = policies["within_30_days"]
            approved = True
            refund_type = "full"
        elif order_days <= 180:
            policy = policies["30_to_180_days"]
            approved = True
            refund_type = "partial"
        else:
            policy = policies["after_180_days"]
            approved = False
            refund_type = "none"

        # 获取订单信息
        order = await self._get_order(order_id)
        refund_amount = order.get("total", 0) if approved else 0

        return {
            "approved": approved,
            "refund_type": refund_type,
            "refund_amount": float(refund_amount),
            "return_label": f"https://amazon.com/returns/{order_id}" if approved else None,
            "reason": self._get_decision_reason(approved, policy)
        }

    async def process_refund(
        self,
        order_id: str,
        approved: bool,
        refund_amount: float
    ) -> Dict:
        """处理退款"""
        if not approved:
            # 发送拒绝消息
            await self._send_refund_denied(order_id)
        else:
            # 创建退货授权
            return_label = await self._create_return_authorization(order_id)

            # 更新订单状态
            await self._update_order_status(order_id, "refunded")

            return {
                "order_id": order_id,
                "status": "refunded",
                "refund_amount": refund_amount,
                "return_label": return_label
            }
```

---

## API 设计

### 端点定义

```python
# backend/api/routes/customer.py

from fastapi import APIRouter, Query, BackgroundTasks
from typing import List

router = APIRouter(prefix="/api/v1/customer", tags=["Customer"])

@router.get("/messages")
async def get_messages(
    status: str = Query("all"),
    channel: str = Query("all"),
    limit: int = Query(50)
):
    """获取消息列表"""
    pass

@router.get("/messages/{message_id}")
async def get_message(message_id: str):
    """获取消息详情"""
    pass

@router.post("/messages/{message_id}/reply")
async def reply_to_message(
    message_id: str,
    reply: str = Body(..., embed=True),
    auto_generate: bool = False
):
    """回复消息"""
    if auto_generate:
        # 使用 AI 生成回复
        pass
    else:
        # 手动回复
        pass

@router.post("/messages/batch-read")
async def batch_mark_read(
    message_ids: List[str] = Body(...)
):
    """批量标记已读"""
    pass

@router.get("/conversations")
async def get_conversations(
    customer_id: str = Query(None),
    status: str = Query("open")
):
    """获取对话列表"""
    pass

@router.post("/refunds/evaluate")
async def evaluate_refund(
    order_id: str = Body(...),
    reason: str = Body(...),
    item_condition: str = Body("new")
):
    """评估退款请求"""
    pass

@router.post("/refunds/process")
async def process_refund(
    order_id: str = Body(...),
    approved: bool = Body(...),
    refund_amount: float = Body(None)
):
    """处理退款"""
    pass
```

---

## 数据模型

### 数据库表

```sql
-- 对话表
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(id),
    channel VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'open', -- open, waiting, closed
    priority VARCHAR(20) DEFAULT 'normal',
    last_message_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 消息表
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    direction VARCHAR(10) NOT NULL, -- inbound, outbound
    channel VARCHAR(20) NOT NULL,
    channel_message_id VARCHAR(100),
    subject VARCHAR(500),
    body TEXT NOT NULL,
    attachments JSONB DEFAULT '[]',
    intent VARCHAR(50),
    sentiment VARCHAR(20),
    ai_analyzed BOOLEAN DEFAULT false,
    ai_suggested_reply TEXT,
    status VARCHAR(20) DEFAULT 'open', -- open, responded, resolved
    metadata JSONB DEFAULT '{}',
    received_at TIMESTAMPTZ DEFAULT NOW(),
    responded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT direction_valid CHECK (direction IN ('inbound', 'outbound'))
);

-- 知识库文章表
CREATE TABLE knowledge_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    intent VARCHAR(50) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    keywords TEXT[],
    embedding VECTOR(1536),  -- pgvector
    priority INTEGER DEFAULT 0,
    locale VARCHAR(10) DEFAULT 'zh-CN',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建向量索引
CREATE INDEX ON knowledge_articles USING ivff (embedding vector_cosine_ops);
```

---

**预计工作量**: 2-3 周

| 阶段 | 任务 | 时间 |
|------|------|------|
| Week 1 | 消息聚合 + 意图识别 | 5 天 |
| Week 2 | AI 客服 (RAG) + 知识库 | 5 天 |
| Week 3 | 退款处理 + API 开发 | 5 天 |

---

**下一步**: 查看 [FINANCE_MODULE.md](./FINANCE_MODULE.md)
