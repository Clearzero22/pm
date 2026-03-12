# AI电子邮件处理完整指南

> 从基础原理到工程实现的完整技术方案

---

## 目录

1. [概述](#1-概述)
2. [AI邮件处理核心能力](#2-ai邮件处理核心能力)
3. [技术架构](#3-技术架构)
4. [核心功能模块](#4-核心功能模块)
5. [工程实现](#5-工程实现)
6. [LLM集成方案](#6-llm集成方案)
7. [完整代码示例](#7-完整代码示例)
8. [部署与优化](#8-部署与优化)
9. [安全与隐私](#9-安全与隐私)

---

## 1. 概述

### 1.1 AI邮件处理的价值

```
┌─────────────────────────────────────────────────────────────────┐
│                     传统邮件处理 vs AI邮件处理                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  传统方式:                    AI方式:                            │
│  ❌ 手动分类                  ✅ 自动智能分类                     │
│  ❌ 逐一回复                  ✅ 自动起草回复                     │
│  ❌ 漏掉重要邮件              ✅ 优先级智能排序                   │
│  ❌ 浪费大量时间              ✅ 节省80%处理时间                  │
│  ❌ 无法分析趋势              ✅ 数据洞察与预测                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 应用场景

```yaml
个人用户:
  - 智能邮件分类（工作/个人/促销）
  - 垃圾邮件过滤
  - 重要邮件提醒
  - 自动回复生成
  - 日程提取与安排

企业用户:
  - 客服邮件自动分类
  - 工单自动创建
  - 情感分析（客户满意度）
  - 意图识别（售后/咨询/投诉）
  - 智能路由分配

专业场景:
  - 发票/合同自动提取
  - 邮件摘要生成
  - 多语言翻译
  - 合规性检查
  - 数据脱敏
```

---

## 2. AI邮件处理核心能力

### 2.1 能力矩阵

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI邮件处理能力图谱                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ 理解能力    │  │ 生成能力    │  │ 决策能力    │             │
│  │             │  │             │  │             │             │
│  │ • 意图识别  │  │ • 回复生成  │  │ • 优先级    │             │
│  │ • 情感分析  │  │ • 摘要生成  │  │ • 路由决策  │             │
│  │ • 实体提取  │  │ • 翻译      │  │ • 分类标签  │             │
│  │ • 主题检测  │  │ • 重写      │  │ • 垃圾检测  │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ 提取能力    │  │ 分析能力    │  │ 交互能力    │             │
│  │             │  │             │  │             │             │
│  │ • 关键信息  │  │ • 趋势分析  │  │ • 对话管理  │             │
│  │ • 结构化数据│  │ • 异常检测  │  │ • 任务执行  │             │
│  │ • 附件解析  │  │ • 统计报告  │  │ • 系统集成  │             │
│  │ • 链接提取  │  │ • 预测      │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 处理流程

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  收邮件  │ →  │  预处理  │ →  │  AI分析  │ →  │  执行动作 │
│          │    │          │    │          │    │          │
│ • IMAP   │    │ • 解析   │    │ • 分类   │    │ • 标签   │
│ • POP3   │    │ • 清洗   │    │ • 意图   │    │ • 回复   │
│ • API    │    │ • 提取   │    │ • 情感   │    │ • 路由   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
```

---

## 3. 技术架构

### 3.1 系统架构设计

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          AI邮件处理系统架构                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                           接入层                                    │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │ │
│  │  │ IMAP/POP3│  │   API    │  │  Webhook │  │  Forward │          │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘          │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                          │                               │
│                                          ▼                               │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                          处理层                                     │ │
│  │  ┌─────────────────────────────────────────────────────────────┐  │ │
│  │  │                    邮件解析器                                │  │ │
│  │  │  • MIME解析  • 附件提取  • HTML清洗  • 文本提取             │  │ │
│  │  └─────────────────────────────────────────────────────────────┘  │ │
│  │                                   │                                 │ │
│  │  ┌─────────────────────────────────────────────────────────────┐  │ │
│  │  │                    AI引擎                                    │  │ │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │  │ │
│  │  │  │ 分类模型  │  │ 意图识别  │  │ 情感分析  │  │ NER实体   │    │  │ │
│  │  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │  │ │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │  │ │
│  │  │  │ LLM生成  │  │ 摘要生成  │  │ 翻译引擎  │  │ 相似度    │    │  │ │
│  │  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │  │ │
│  │  └─────────────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                          │                               │
│                                          ▼                               │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                          决策层                                     │ │
│  │  ┌─────────────────────────────────────────────────────────────┐  │ │
│  │  │                    规则引擎                                    │  │ │
│  │  │  • 业务规则  • 工作流  • 条件判断  • 分发逻辑                 │  │ │
│  │  └─────────────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────────────┐  │ │
│  │  │                    任务调度                                    │  │ │
│  │  │  • 队列管理  • 定时任务  • 优先级  • 重试机制                 │  │ │
│  │  └─────────────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                          │                               │
│                                          ▼                               │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                          执行层                                     │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │ │
│  │  │ 发送邮件  │  │ 标签管理  │  │ 数据存储  │  │ 第三方API │          │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘          │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                          存储层                                     │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │ │
│  │  │ PostgreSQL│  │  Redis   │  │ 向量DB   │  │ 对象存储  │          │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘          │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 技术选型

```yaml
# 语言与框架
Backend:
  language: Python
  framework: FastAPI
  原因:
    - 丰富的AI/ML库生态
    - 异步支持
    - 易于部署

# AI/ML框架
AI Frameworks:
  传统ML: scikit-learn
    - 邮件分类
    - 垃圾检测
    - 情感分析

  深度学习: PyTorch / TensorFlow
    - 复杂NLP任务
    - 自定义模型

  LLM集成: OpenAI API / LangChain
    - 意图识别
    - 文本生成
    - 摘要提取

# NLP工具
NLP:
  基础: spaCy
    - 命名实体识别
    - 词性标注
    - 句法分析

  高级: Transformers
    - 预训练模型
    - BERT/RoBERTa
    - 多语言支持

# 邮件处理
Email:
  解析: email-validator, mail-parser
    - MIME解析
    - 附件提取

  接收: imap-tools, aioimaplib
    - IMAP客户端
    - 异步支持

  发送: smtplib, sendgrid
    - SMTP发送
    - API发送

# 任务队列
Queue:
  框架: Celery + Redis
    - 异步任务处理
    - 定时任务
    - 重试机制

# 数据库
Databases:
  主库: PostgreSQL
    - 结构化数据
    - 全文搜索

  缓存: Redis
    - 队列
    - 会话
    - 限流

  向量: Qdrant / Weaviate
    - 语义搜索
    - 相似邮件
```

---

## 4. 核心功能模块

### 4.1 邮件分类

```python
# models/email_classifier.py

from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib

class EmailClassifier:
    """
    邮件智能分类器

    支持的分类类型:
    - 工作/个人/促销
    - 紧急/普通/低优先级
    - 内部/外部/客户
    - 支持/销售/账单等
    """

    def __init__(self, model_path: str = None):
        self.categories = [
            '工作', '个人', '促销', '社交',
            '通知', '账单', '新闻', '其他'
        ]
        self.pipeline = self._build_pipeline()

        if model_path:
            self.load_model(model_path)

    def _build_pipeline(self) -> Pipeline:
        """构建分类流水线"""
        return Pipeline([
            ('vectorizer', TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                stop_words='english'
            )),
            ('classifier', MultinomialNB())
        ])

    def train(self, emails: List[str], labels: List[str]) -> None:
        """
        训练分类器

        Args:
            emails: 邮件文本列表
            labels: 对应的类别标签
        """
        self.pipeline.fit(emails, labels)

    def predict(self, email_text: str) -> Dict:
        """
        预测邮件类别

        Returns:
            {
                'category': '工作',
                'confidence': 0.95,
                'probabilities': {...}
            }
        """
        # 预测类别
        category = self.pipeline.predict([email_text])[0]

        # 获取概率
        probabilities = self.pipeline.predict_proba([email_text])[0]
        prob_dict = {
            cat: prob for cat, prob in zip(self.categories, probabilities)
        }

        return {
            'category': category,
            'confidence': max(probabilities),
            'probabilities': prob_dict
        }

    def predict_batch(self, emails: List[str]) -> List[Dict]:
        """批量预测"""
        categories = self.pipeline.predict(emails)
        probabilities = self.pipeline.predict_proba(emails)

        results = []
        for cat, probs in zip(categories, probabilities):
            prob_dict = {
                category: prob for category, prob in zip(self.categories, probs)
            }
            results.append({
                'category': cat,
                'confidence': max(probs),
                'probabilities': prob_dict
            })

        return results

    def save_model(self, path: str) -> None:
        """保存模型"""
        joblib.dump(self.pipeline, path)

    def load_model(self, path: str) -> None:
        """加载模型"""
        self.pipeline = joblib.load(path)


# 使用LLM进行分类（更智能但成本更高）

class LLMEmailClassifier:
    """
    基于LLM的邮件分类器

    优点:
    - 理解上下文
    - 少样本学习
    - 无需训练数据

    缺点:
    - API成本
    - 延迟较高
    """

    def __init__(self, api_key: str):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)

    async def classify(
        self,
        email: Dict,
        categories: List[str] = None
    ) -> Dict:
        """
        使用LLM分类邮件

        Args:
            email: 邮件字典 {subject, body, sender, ...}
            categories: 自定义分类列表

        Returns:
            分类结果
        """
        if not categories:
            categories = [
                '工作-紧急', '工作-普通', '工作-低优先级',
                '个人-家庭', '个人-朋友',
                '促销', '账单', '通知', '新闻', '其他'
            ]

        prompt = f"""
你是一个邮件分类专家。请分析以下邮件并将其归类到最合适的类别。

邮件信息:
主题: {email.get('subject', '')}
发件人: {email.get('sender', '')}
正文: {email.get('body', '')[:500]}

可选类别:
{chr(10).join(f"- {cat}" for cat in categories)}

请以JSON格式返回:
{{
    "category": "类别名称",
    "reasoning": "分类理由",
    "priority": "high/medium/low",
    "confidence": 0.95
}}
"""

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        import json
        result = json.loads(response.choices[0].message.content)
        return result
```

### 4.2 意图识别

```python
# models/intent_recognizer.py

from typing import List, Dict, Optional
from enum import Enum

class EmailIntent(Enum):
    """邮件意图类型"""
    # 交易类
    PURCHASE = "购买"  # 购买咨询/下单
    REFUND = "退款"    # 退款申请
    RETURN = "退货"    # 退货处理

    # 咨询类
    INQUIRY = "咨询"   # 产品咨询
    SUPPORT = "支持"   # 技术支持
    INFO = "信息"      # 信息查询

    # 投诉类
    COMPLAINT = "投诉"  # 投诉建议
    ESCALATION = "升级" # 升级处理

    # 确认类
    CONFIRMATION = "确认"  # 订单确认
    VERIFICATION = "验证"  # 身份验证

    # 营销类
    MARKETING = "营销"     # 营销邮件
    NEWSLETTER = "订阅"    # 订阅邮件

    # 其他
    OTHER = "其他"


class IntentRecognizer:
    """邮件意图识别器"""

    # 关键词规则
    INTENT_KEYWORDS = {
        EmailIntent.PURCHASE: [
            'buy', 'order', 'purchase', 'how much',
            'price', 'pricing', 'quote', '购买', '价格', '报价'
        ],
        EmailIntent.REFUND: [
            'refund', 'money back', 'chargeback',
            '退款', '返款'
        ],
        EmailIntent.RETURN: [
            'return', 'exchange', 'send back',
            '退货', '换货'
        ],
        EmailIntent.INQUIRY: [
            'question', 'ask', 'want to know',
            'how to', 'what is', '咨询', '问', '如何'
        ],
        EmailIntent.SUPPORT: [
            'help', 'support', 'issue', 'problem',
            'broken', 'not working', '帮助', '支持', '问题'
        ],
        EmailIntent.COMPLAINT: [
            'complaint', 'unhappy', 'disappointed',
            '投诉', '不满意', '失望'
        ],
        EmailIntent.CONFIRMATION: [
            'confirm', 'confirmation', 'verified',
            '确认', '验证'
        ],
    }

    def __init__(self, use_llm: bool = False):
        self.use_llm = use_llm

    def recognize(self, email: Dict) -> Dict:
        """
        识别邮件意图

        Returns:
            {
                'intent': EmailIntent.PURCHASE,
                'confidence': 0.85,
                'entities': {...}
            }
        """
        if self.use_llm:
            return self._llm_recognize(email)
        else:
            return self._rule_based_recognize(email)

    def _rule_based_recognize(self, email: Dict) -> Dict:
        """基于规则的意图识别"""
        text = (
            email.get('subject', '') + ' ' +
            email.get('body', '')
        ).lower()

        # 计算每个意图的匹配分数
        intent_scores = {}
        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                intent_scores[intent] = score

        # 返回最高分意图
        if intent_scores:
            intent = max(intent_scores, key=intent_scores.get)
            confidence = min(intent_scores[intent] * 0.2, 1.0)
        else:
            intent = EmailIntent.OTHER
            confidence = 0.5

        return {
            'intent': intent,
            'confidence': confidence,
            'scores': intent_scores
        }

    async def _llm_recognize(self, email: Dict) -> Dict:
        """使用LLM识别意图"""
        from openai import OpenAI
        import json

        client = OpenAI()

        prompt = f"""
识别以下邮件的意图类型。

邮件:
主题: {email.get('subject', '')}
发件人: {email.get('sender', '')}
正文: {email.get('body', '')[:800]}

可能的意图类型:
- PURCHASE: 购买相关
- REFUND: 退款相关
- RETURN: 退货相关
- INQUIRY: 产品咨询
- SUPPORT: 技术支持
- COMPLAINT: 投诉建议
- CONFIRMATION: 确认类
- MARKETING: 营销类
- OTHER: 其他

请返回JSON:
{{
    "intent": "意图类型",
    "confidence": 0.95,
    "reasoning": "识别依据",
    "entities": {{
        "product": "产品名",
        "order_id": "订单号",
        "amount": "金额"
    }}
}}
"""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        # 转换为枚举
        try:
            result['intent'] = EmailIntent(result['intent'].upper())
        except:
            result['intent'] = EmailIntent.OTHER

        return result
```

### 4.3 情感分析

```python
# models/sentiment_analyzer.py

from typing import Dict, List
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class SentimentAnalyzer:
    """
    邮件情感分析器

    用途:
    - 客户满意度监控
    - 紧急邮件识别
    - 投诉预警
    """

    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()

    def analyze(self, email_text: str) -> Dict:
        """
        分析邮件情感

        Returns:
            {
                'sentiment': 'positive/negative/neutral',
                'score': 0.85,
                'emotions': {
                    'joy': 0.6,
                    'anger': 0.1,
                    'fear': 0.05,
                    'sadness': 0.1
                },
                'urgency': 'high/medium/low'
            }
        """
        # VADER情感分析
        vader_scores = self.vader.polarity_scores(email_text)

        # TextBlob分析
        blob = TextBlob(email_text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        # 判断情感倾向
        if vader_scores['compound'] >= 0.05:
            sentiment = 'positive'
        elif vader_scores['compound'] <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

        # 判断紧急程度
        urgency = self._detect_urgency(email_text)

        # 检测情绪
        emotions = self._detect_emotions(email_text)

        return {
            'sentiment': sentiment,
            'vader_scores': vader_scores,
            'polarity': polarity,
            'subjectivity': subjectivity,
            'emotions': emotions,
            'urgency': urgency
        }

    def _detect_urgency(self, text: str) -> str:
        """检测邮件紧急程度"""
        text_lower = text.lower()

        urgent_keywords = [
            'urgent', 'asap', 'immediately', 'emergency',
            '紧急', '尽快', '立即'
        ]

        urgent_count = sum(1 for kw in urgent_keywords if kw in text_lower)

        if urgent_count >= 2:
            return 'high'
        elif urgent_count == 1:
            return 'medium'
        else:
            return 'low'

    def _detect_emotions(self, text: str) -> Dict[str, float]:
        """检测情绪（简化版）"""
        emotions = {
            'joy': 0.0,
            'anger': 0.0,
            'fear': 0.0,
            'sadness': 0.0,
            'surprise': 0.0
        }

        text_lower = text.lower()

        # 积极情绪
        joy_keywords = ['happy', 'great', 'love', 'thank', '开心', '感谢', '满意']
        emotions['joy'] = sum(1 for kw in joy_keywords if kw in text_lower) * 0.2

        # 愤怒
        anger_keywords = ['angry', 'furious', 'terrible', 'disappointed', '生气', '愤怒', '失望']
        emotions['anger'] = sum(1 for kw in anger_keywords if kw in text_lower) * 0.3

        # 恐惧
        fear_keywords = ['worried', 'concerned', 'afraid', '担心', '害怕']
        emotions['fear'] = sum(1 for kw in fear_keywords if kw in text_lower) * 0.2

        # 悲伤
        sadness_keywords = ['sad', 'upset', 'disappointed', '难过', '伤心']
        emotions['sadness'] = sum(1 for kw in sadness_keywords if kw in text_lower) * 0.2

        # 惊讶
        surprise_keywords = ['surprised', 'shocked', 'unexpected', '惊讶', '震惊']
        emotions['surprise'] = sum(1 for kw in surprise_keywords if kw in text_lower) * 0.2

        return emotions

    def analyze_batch(self, emails: List[str]) -> List[Dict]:
        """批量分析"""
        return [self.analyze(email) for email in emails]


# LLM情感分析（更精准）

class LLMSentimentAnalyzer:
    """
    基于LLM的情感分析
    """

    def __init__(self, api_key: str):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)

    async def analyze(self, email: Dict) -> Dict:
        """使用LLM分析情感"""
        import json

        prompt = f"""
分析以下邮件的情感和客户情绪。

邮件:
主题: {email.get('subject', '')}
发件人: {email.get('sender', '')}
正文: {email.get('body', '')[:1000]}

请返回JSON:
{{
    "overall_sentiment": "positive/neutral/negative",
    "sentiment_score": 0.85,
    "customer_satisfaction": "high/medium/low",
    "emotional_state": "calm/agitated/frustrated/excited",
    "key_concerns": ["关注点1", "关注点2"],
    "recommended_action": "建议的处理方式",
    "urgency_level": "high/medium/low"
}}
"""

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result
```

### 4.4 信息提取

```python
# models/information_extractor.py

import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import phonenumbers
from email_validator import validate_email, EmailNotValidError

class InformationExtractor:
    """
    邮件信息提取器

    提取的信息类型:
    - 联系方式: 邮箱、电话、网址
    - 订单信息: 订单号、金额、日期
    - 个人信息: 姓名、地址
    - 时间日期: 会议时间、截止日期
    - 附件信息: 文件名、类型
    """

    # 订单号模式
    ORDER_ID_PATTERNS = [
        r'order\s*[:#]?\s*([A-Z0-9-]+)',
        r'订单\s*号\s*[:：]?\s*([A-Z0-9-]+)',
        r'purchase\s*order\s*[:#]?\s*([A-Z0-9-]+)',
        r'PO\s*[:#]?\s*([A-Z0-9-]+)',
        r'#([A-Z0-9]{8,})',
    ]

    # 金额模式
    MONEY_PATTERNS = [
        r'\$?\s*([\d,]+\.?\d*)\s*(USD|CNY|EUR|GBP|元|美元)?',
        r'([\d,]+\.?\d*)\s*(dollars?|yuan|euros?|pounds?)',
    ]

    # 日期时间模式
    DATETIME_PATTERNS = [
        r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}',
    ]

    def __init__(self):
        pass

    def extract(self, email_text: str) -> Dict[str, Any]:
        """
        提取邮件中的关键信息

        Returns:
            {
                'emails': ['email@example.com'],
                'phones': ['+1234567890'],
                'urls': ['https://example.com'],
                'order_ids': ['ABC-123'],
                'amounts': [99.99],
                'dates': ['2024-01-15'],
                'names': ['John Doe'],
                'addresses': ['123 Main St'],
                'tracking_numbers': ['1Z999AA10123456784']
            }
        """
        return {
            'emails': self.extract_emails(email_text),
            'phones': self.extract_phones(email_text),
            'urls': self.extract_urls(email_text),
            'order_ids': self.extract_order_ids(email_text),
            'amounts': self.extract_amounts(email_text),
            'dates': self.extract_dates(email_text),
            'names': self.extract_names(email_text),
            'addresses': self.extract_addresses(email_text),
            'tracking_numbers': self.extract_tracking_numbers(email_text)
        }

    def extract_emails(self, text: str) -> List[str]:
        """提取邮箱地址"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text, re.IGNORECASE)

        # 验证邮箱格式
        valid_emails = []
        for email in set(emails):
            try:
                validate_email(email)
                valid_emails.append(email)
            except EmailNotValidError:
                pass

        return valid_emails

    def extract_phones(self, text: str) -> List[str]:
        """提取电话号码"""
        phones = []

        # 国际格式
        for match in phonenumbers.PhoneNumberMatcher(text, None):
            phones.append(phonenumbers.format_number(
                match.number,
                phonenumbers.PhoneNumberFormat.E164
            ))

        # 简单格式 (需要phonenumbers无法识别时)
        simple_patterns = [
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # US format
            r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b',  # China format
        ]

        for pattern in simple_patterns:
            matches = re.findall(pattern, text)
            phones.extend(matches)

        return list(set(phones))

    def extract_urls(self, text: str) -> List[str]:
        """提取URL"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        return list(set(urls))

    def extract_order_ids(self, text: str) -> List[str]:
        """提取订单号"""
        order_ids = []

        for pattern in self.ORDER_ID_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            order_ids.extend(matches)

        return list(set(order_ids))

    def extract_amounts(self, text: str) -> List[float]:
        """提取金额"""
        amounts = []

        for pattern in self.MONEY_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    amount_str = match[0]
                else:
                    amount_str = match

                try:
                    amount = float(amount_str.replace(',', ''))
                    if 0 < amount < 100000:  # 合理范围
                        amounts.append(amount)
                except ValueError:
                    pass

        return list(set(amounts))

    def extract_dates(self, text: str) -> List[str]:
        """提取日期"""
        dates = []

        for pattern in self.DATETIME_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)

        return list(set(dates))

    def extract_names(self, text: str) -> List[str]:
        """提取人名（简化版，建议使用NER）"""
        # 署名模式
        signature_patterns = [
            r'Best\s+regards?,?\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'Best,?\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'Cheers,?\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'From:\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
        ]

        names = []
        for pattern in signature_patterns:
            matches = re.findall(pattern, text)
            names.extend(matches)

        return list(set(names))

    def extract_addresses(self, text: str) -> List[str]:
        """提取地址（简化版）"""
        # 美国地址格式
        address_pattern = r'\d+\s+[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z]{2})?\s+\d{5}(?:-\d{4})?'
        addresses = re.findall(address_pattern, text)

        return list(set(addresses))

    def extract_tracking_numbers(self, text: str) -> List[str]:
        """提取物流追踪号"""
        # FedEx
        fedex_pattern = r'\b(\d{12,14})\b'
        # UPS
        ups_pattern = r'\b(1Z[A-Z0-9]{16})\b'
        # USPS
        usps_pattern = r'\b(\d{20,22})\b'

        tracking_numbers = []
        for pattern in [fedex_pattern, ups_pattern, usps_pattern]:
            matches = re.findall(pattern, text)
            tracking_numbers.extend(matches)

        return list(set(tracking_numbers))


# LLM信息提取

class LLMInformationExtractor:
    """
    基于LLM的信息提取
    """

    def __init__(self, api_key: str):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)

    async def extract(
        self,
        email: Dict,
        schema: Dict = None
    ) -> Dict:
        """
        使用LLM提取结构化信息

        Args:
            email: 邮件数据
            schema: 自定义提取字段
        """
        import json

        if not schema:
            schema = {
                "customer_name": "客户姓名",
                "order_number": "订单号",
                "product_name": "产品名称",
                "issue_description": "问题描述",
                "requested_action": "请求的操作",
                "urgency": "紧急程度",
                "follow_up_required": "是否需要后续跟进"
            }

        schema_str = json.dumps(schema, ensure_ascii=False, indent=2)

        prompt = f"""
从以下邮件中提取结构化信息。

邮件:
主题: {email.get('subject', '')}
发件人: {email.get('sender', '')}
正文: {email.get('body', '')}

请按照以下schema提取信息:
{schema_str}

如果某个字段在邮件中找不到，使用null。
返回JSON格式。
"""

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result
```

### 4.5 摘要生成

```python
# models/summarizer.py

from typing import Dict, List
import hashlib

class EmailSummarizer:
    """
    邮件摘要生成器
    """

    def __init__(self, use_llm: bool = True, api_key: str = None):
        self.use_llm = use_llm
        self.api_key = api_key

    async def summarize(
        self,
        email: Dict,
        max_length: int = 100,
        style: str = "concise"
    ) -> Dict:
        """
        生成邮件摘要

        Args:
            email: 邮件数据
            max_length: 摘要最大长度
            style: 摘要风格 (concise/detailed/bullet_points)

        Returns:
            {
                'summary': '摘要文本',
                'key_points': ['要点1', '要点2'],
                'action_items': ['行动项1'],
                'topics': ['主题1', '主题2']
            }
        """
        if self.use_llm:
            return await self._llm_summarize(email, max_length, style)
        else:
            return self._extractive_summarize(email, max_length)

    async def _llm_summarize(
        self,
        email: Dict,
        max_length: int,
        style: str
    ) -> Dict:
        """使用LLM生成摘要"""
        from openai import OpenAI
        import json

        client = OpenAI(api_key=self.api_key)

        style_instructions = {
            "concise": "简洁，一句话概括",
            "detailed": "详细，保留主要信息",
            "bullet_points": "要点列表，清晰易读"
        }

        prompt = f"""
为以下邮件生成摘要。

邮件:
主题: {email.get('subject', '')}
发件人: {email.get('sender', '')}
时间: {email.get('date', '')}
正文:
{email.get('body', '')[:3000]}

要求:
1. 摘要风格: {style_instructions.get(style, "简洁")}
2. 摘要长度: 不超过{max_length}字
3. 提取关键要点（3-5个）
4. 识别需要采取的行动项
5. 识别主要话题

返回JSON:
{{
    "summary": "一句话摘要",
    "key_points": ["要点1", "要点2", "要点3"],
    "action_items": ["行动项1", "行动项2"],
    "topics": ["话题1", "话题2"],
    "urgency": "high/medium/low"
}}
"""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result

    def _extractive_summarize(
        self,
        email: Dict,
        max_length: int
    ) -> Dict:
        """抽取式摘要（不使用LLM）"""
        body = email.get('body', '')

        # 简单处理：取前N个字符
        summary = body[:max_length]

        # 提取关键句（包含重要关键词的句子）
        important_keywords = [
            'urgent', 'asap', 'deadline', 'important',
            '请', '紧急', '重要', '必须'
        ]

        key_points = []
        sentences = body.split('. ')
        for sentence in sentences:
            if any(kw in sentence.lower() for kw in important_keywords):
                key_points.append(sentence.strip())

        return {
            'summary': summary,
            'key_points': key_points[:5],
            'action_items': [],
            'topics': []
        }

    async def summarize_thread(
        self,
        emails: List[Dict]
    ) -> Dict:
        """
        生成邮件线程摘要

        Args:
            emails: 按时间排序的邮件列表

        Returns:
            整个邮件线程的摘要
        """
        if not emails:
            return {'summary': '空邮件线程', 'participants': [], 'timeline': []}

        from openai import OpenAI
        import json

        client = OpenAI(api_key=self.api_key)

        # 构建邮件线程摘要
        thread_summary = []
        for i, email in enumerate(emails):
            thread_summary.append(f"""
邮件 {i+1}:
发件人: {email.get('sender', '')}
时间: {email.get('date', '')}
主题: {email.get('subject', '')}
内容: {email.get('body', '')[:500]}
""")

        prompt = f"""
为以下邮件线程生成摘要。

邮件线程:
{chr(10).join(thread_summary)}

请返回JSON:
{{
    "summary": "整个线程的摘要",
    "participants": ["参与者1", "参与者2"],
    "topic": "讨论的主题",
    "key_points": ["关键点1", "关键点2"],
    "resolution": "解决方案或结论",
    "status": "ongoing/resolved/pending",
    "timeline": [
        {{"date": "日期", "event": "事件", "participant": "参与者"}}
    ]
}}
"""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result
```

---

## 5. 工程实现

### 5.1 邮件接收服务

```python
# services/email_receiver.py

import asyncio
import email
from email import policy
from email.parser import BytesParser
from imap_tools import MailBox, AND
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class EmailReceiver:
    """
    邮件接收服务

    支持IMAP协议，可扩展支持POP3
    """

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 993,
        use_ssl: bool = True
    ):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.use_ssl = use_ssl

    async def fetch_emails(
        self,
        folder: str = 'INBOX',
        limit: int = 10,
        unread_only: bool = True,
        since: Optional[str] = None
    ) -> List[Dict]:
        """
        获取邮件

        Args:
            folder: 邮箱文件夹
            limit: 获取数量限制
            unread_only: 是否只获取未读邮件
            since: 起始日期 (格式: 01-Jan-2024)

        Returns:
            邮件列表
        """
        try:
            with MailBox(self.host).login(
                self.username,
                self.password,
                initial_folder=folder
            ) as mailbox:

                # 构建查询条件
                criteria = []
                if unread_only:
                    criteria.append(['UNSEEN'])
                if since:
                    criteria.append(['SINCE', since])

                # 查询邮件
                if criteria:
                    query = AND(*criteria)
                else:
                    query = ALL

                emails = []
                for msg in mailbox.fetch(
                    criteria=query,
                    limit=limit,
                    mark_seen=False
                ):
                    emails.append(self._parse_email(msg))

                logger.info(f"获取到 {len(emails)} 封邮件")
                return emails

        except Exception as e:
            logger.error(f"获取邮件失败: {e}")
            raise

    def _parse_email(self, msg) -> Dict:
        """
        解析邮件

        Returns:
            {
                'id': '邮件ID',
                'subject': '主题',
                'from': '发件人',
                'to': '收件人',
                'date': '日期',
                'body': '正文',
                'html': 'HTML内容',
                'attachments': ['附件列表'],
                'headers': {'header_name': 'value'}
            }
        """
        return {
            'uid': msg.uid,
            'subject': msg.subject,
            'from': str(msg.from_) if msg.from_ else None,
            'to': [str(t) for t in msg.to] if msg.to else [],
            'cc': [str(c) for c in msg.cc] if msg.cc else [],
            'date': msg.date,
            'body': msg.text,
            'html': msg.html,
            'attachments': [
                {
                    'filename': att.filename,
                    'size': att.size,
                    'content_type': att.content_type,
                    'payload': att.payload
                }
                for att in msg.attachments
            ],
            'flags': msg.flags,
            'headers': dict(msg.headers)
        }

    async def mark_as_read(self, uid: int, folder: str = 'INBOX'):
        """标记邮件为已读"""
        try:
            with MailBox(self.host).login(
                self.username,
                self.password,
                initial_folder=folder
            ) as mailbox:
                mailbox.seen([uid])
                logger.info(f"邮件 {uid} 已标记为已读")
        except Exception as e:
            logger.error(f"标记已读失败: {e}")

    async def move_email(
        self,
        uid: int,
        from_folder: str,
        to_folder: str
    ):
        """移动邮件到其他文件夹"""
        try:
            with MailBox(self.host).login(
                self.username,
                self.password,
                initial_folder=from_folder
            ) as mailbox:
                mailbox.move([uid], to_folder)
                logger.info(f"邮件 {uid} 已移动到 {to_folder}")
        except Exception as e:
            logger.error(f"移动邮件失败: {e}")

    async def add_label(
        self,
        uid: int,
        label: str,
        folder: str = 'INBOX'
    ):
        """为邮件添加标签（Gmail风格）"""
        try:
            with MailBox(self.host).login(
                self.username,
                self.password,
                initial_folder=folder
            ) as mailbox:
                mailbox.flag([uid], f'\\{label}', True)
                logger.info(f"邮件 {uid} 已添加标签 {label}")
        except Exception as e:
            logger.error(f"添加标签失败: {e}")


# Webhook接收服务

class EmailWebhookReceiver:
    """
    邮件Webhook接收服务

    适用于:
    - SendGrid Webhook
    - Mailgun Webhook
    - AWS SES Webhook
    """

    def __init__(self, webhook_secret: str):
        self.webhook_secret = webhook_secret

    async def receive_webhook(self, payload: Dict) -> Dict:
        """
        接收Webhook推送的邮件

        Args:
            payload: Webhook payload

        Returns:
            解析后的邮件数据
        """
        # 验证签名（根据服务商不同而不同）
        if not self._verify_signature(payload):
            raise ValueError("Invalid webhook signature")

        # 解析邮件数据
        email_data = {
            'id': payload.get('id'),
            'subject': payload.get('subject'),
            'from': payload.get('from'),
            'to': payload.get('to'),
            'date': payload.get('date'),
            'body': payload.get('text') or payload.get('html'),
            'html': payload.get('html'),
            'attachments': payload.get('attachments', []),
            'headers': payload.get('headers', {}),
            'raw': payload
        }

        return email_data

    def _verify_signature(self, payload: Dict) -> bool:
        """验证Webhook签名"""
        # 实现签名验证逻辑
        # 根据不同服务商的验证方式实现
        return True
```

### 5.2 邮件处理管道

```python
# services/email_pipeline.py

from typing import Dict, List, Optional
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailProcessingPipeline:
    """
    邮件处理管道

    处理流程:
    1. 接收邮件
    2. 预处理（解析、清洗）
    3. AI分析（分类、意图、情感）
    4. 决策（路由、标签、优先级）
    5. 执行（回复、转发、存储）
    """

    def __init__(
        self,
        classifier,
        intent_recognizer,
        sentiment_analyzer,
        info_extractor,
        summarizer
    ):
        self.classifier = classifier
        self.intent_recognizer = intent_recognizer
        self.sentiment_analyzer = sentiment_analyzer
        self.info_extractor = info_extractor
        self.summarizer = summarizer

        # 处理配置
        self.config = {
            'auto_classify': True,
            'auto_summarize': True,
            'detect_urgency': True,
            'extract_entities': True
        }

    async def process(
        self,
        email: Dict,
        config: Optional[Dict] = None
    ) -> Dict:
        """
        处理单封邮件

        Returns:
            {
                'original': email,
                'analysis': {...},
                'actions': [...],
                'metadata': {...}
            }
        """
        if config:
            self.config.update(config)

        result = {
            'original': email,
            'analysis': {},
            'actions': [],
            'metadata': {
                'processed_at': datetime.now().isoformat(),
                'processing_time': 0
            }
        }

        start_time = datetime.now()

        try:
            # ========== 步骤1: 预处理 ==========
            logger.info(f"开始处理邮件: {email.get('subject', '')}")
            processed_email = self._preprocess(email)

            # ========== 步骤2: AI分析 ==========
            analysis_tasks = []

            if self.config.get('auto_classify'):
                analysis_tasks.append(self._classify(processed_email))

            analysis_tasks.append(self._recognize_intent(processed_email))
            analysis_tasks.append(self._analyze_sentiment(processed_email))

            if self.config.get('extract_entities'):
                analysis_tasks.append(self._extract_info(processed_email))

            if self.config.get('auto_summarize'):
                analysis_tasks.append(self._summarize(processed_email))

            # 并行执行分析任务
            analysis_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)

            # 整合分析结果
            for analysis in analysis_results:
                if isinstance(analysis, Exception):
                    logger.error(f"分析任务失败: {analysis}")
                else:
                    result['analysis'].update(analysis)

            # ========== 步骤3: 决策 ==========
            actions = await self._decide_actions(processed_email, result['analysis'])
            result['actions'] = actions

            # ========== 步骤4: 执行动作 ==========
            if self.config.get('auto_execute'):
                executed = await self._execute_actions(processed_email, actions)
                result['executed'] = executed

            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds()
            result['metadata']['processing_time'] = processing_time

            logger.info(f"邮件处理完成，耗时: {processing_time:.2f}秒")

            return result

        except Exception as e:
            logger.error(f"邮件处理失败: {e}")
            result['error'] = str(e)
            return result

    def _preprocess(self, email: Dict) -> Dict:
        """预处理邮件"""
        # 合并主题和正文
        text = f"{email.get('subject', '')}\n\n{email.get('body', '')}"

        # 清洗文本
        text = self._clean_text(text)

        processed = email.copy()
        processed['clean_text'] = text
        processed['word_count'] = len(text.split())

        return processed

    def _clean_text(self, text: str) -> str:
        """清洗文本"""
        import re

        # 移除多余的空白
        text = re.sub(r'\s+', ' ', text)

        # 移除邮件回复符号
        text = re.sub(r'^>.*$', '', text, flags=re.MULTILINE)

        # 移除常见签名
        text = re.sub(
            r'--\s*\n.*$',
            '',
            text,
            flags=re.DOTALL
        )

        return text.strip()

    async def _classify(self, email: Dict) -> Dict:
        """分类"""
        text = email.get('clean_text', '')
        result = self.classifier.predict(text)
        return {'classification': result}

    async def _recognize_intent(self, email: Dict) -> Dict:
        """意图识别"""
        result = self.intent_recognizer.recognize(email)
        return {'intent': result}

    async def _analyze_sentiment(self, email: Dict) -> Dict:
        """情感分析"""
        text = email.get('body', '')
        result = self.sentiment_analyzer.analyze(text)
        return {'sentiment': result}

    async def _extract_info(self, email: Dict) -> Dict:
        """信息提取"""
        text = email.get('clean_text', '')
        result = self.info_extractor.extract(text)
        return {'extracted_info': result}

    async def _summarize(self, email: Dict) -> Dict:
        """摘要生成"""
        result = await self.summarizer.summarize(email)
        return {'summary': result}

    async def _decide_actions(
        self,
        email: Dict,
        analysis: Dict
    ) -> List[Dict]:
        """决策需要执行的动作"""
        actions = []

        # 基于分类的动作
        classification = analysis.get('classification', {})
        category = classification.get('category', '')

        if category == '工作':
            actions.append({
                'type': 'label',
                'value': 'Work',
                'reason': '自动分类为工作邮件'
            })

        # 基于紧急程度的动作
        sentiment = analysis.get('sentiment', {})
        urgency = sentiment.get('urgency', 'low')

        if urgency == 'high':
            actions.append({
                'type': 'label',
                'value': 'Urgent',
                'reason': '检测到高紧急程度'
            })
            actions.append({
                'type': 'notify',
                'value': 'immediate',
                'reason': '紧急邮件需要立即处理'
            })

        # 基于意图的动作
        intent = analysis.get('intent', {})
        intent_type = intent.get('intent')

        if intent_type == 'complaint':
            actions.append({
                'type': 'route',
                'value': 'customer_service',
                'reason': '投诉邮件需要客服处理'
            })
            actions.append({
                'type': 'priority',
                'value': 'high',
                'reason': '投诉需要优先处理'
            })

        # 基于情感的动作
        overall_sentiment = sentiment.get('sentiment', '')

        if overall_sentiment == 'negative':
            actions.append({
                'type': 'escalate',
                'value': True,
                'reason': '负面情感需要关注'
            })

        return actions

    async def _execute_actions(
        self,
        email: Dict,
        actions: List[Dict]
    ) -> List[Dict]:
        """执行动作"""
        executed = []

        for action in actions:
            try:
                result = await self._execute_single_action(email, action)
                executed.append({
                    'action': action,
                    'result': result,
                    'status': 'success'
                })
            except Exception as e:
                executed.append({
                    'action': action,
                    'error': str(e),
                    'status': 'failed'
                })

        return executed

    async def _execute_single_action(
        self,
        email: Dict,
        action: Dict
    ) -> Dict:
        """执行单个动作"""
        action_type = action.get('type')

        if action_type == 'label':
            # 添加标签
            return await self._add_label(email, action['value'])

        elif action_type == 'notify':
            # 发送通知
            return await self._send_notification(email, action['value'])

        elif action_type == 'route':
            # 路由到指定处理人
            return await self._route_email(email, action['value'])

        elif action_type == 'priority':
            # 设置优先级
            return await self._set_priority(email, action['value'])

        else:
            raise ValueError(f"Unknown action type: {action_type}")

    async def _add_label(self, email: Dict, label: str) -> Dict:
        """添加标签"""
        # 实现标签添加逻辑
        logger.info(f"为邮件添加标签: {label}")
        return {'label_added': label}

    async def _send_notification(self, email: Dict, urgency: str) -> Dict:
        """发送通知"""
        # 实现通知发送逻辑
        logger.info(f"发送{urgency}级别通知")
        return {'notification_sent': True}

    async def _route_email(self, email: Dict, route_to: str) -> Dict:
        """路由邮件"""
        # 实现路由逻辑
        logger.info(f"邮件路由到: {route_to}")
        return {'routed_to': route_to}

    async def _set_priority(self, email: Dict, priority: str) -> Dict:
        """设置优先级"""
        logger.info(f"设置邮件优先级: {priority}")
        return {'priority': priority}


# 批量处理

class BatchEmailProcessor:
    """
    批量邮件处理器
    """

    def __init__(self, pipeline: EmailProcessingPipeline):
        self.pipeline = pipeline

    async def process_batch(
        self,
        emails: List[Dict],
        max_concurrent: int = 5
    ) -> List[Dict]:
        """
        批量处理邮件

        Args:
            emails: 邮件列表
            max_concurrent: 最大并发数

        Returns:
            处理结果列表
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_with_limit(email):
            async with semaphore:
                return await self.pipeline.process(email)

        tasks = [process_with_limit(email) for email in emails]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return list(results)
```

---

## 6. LLM集成方案

### 6.1 OpenAI集成

```python
# integrations/openai_client.py

from typing import Dict, List, Optional
import openai
from openai import AsyncOpenAI
import logging

logger = logging.getLogger(__name__)


class OpenAIEmailProcessor:
    """
    使用OpenAI处理邮件
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.3
    ):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature

    async def generate_reply(
        self,
        email: Dict,
        reply_type: str = "professional",
        tone: str = "polite",
        include_points: List[str] = None
    ) -> Dict:
        """
        生成回复邮件

        Args:
            email: 原始邮件
            reply_type: 回复类型 (professional/casual/detailed)
            tone: 语气 (polite/firm/empathetic)
            include_points: 需要包含的要点

        Returns:
            {
                'subject': '回复主题',
                'body': '回复正文',
                'suggested_attachments': []
            }
        """
        tone_instructions = {
            "polite": "礼貌、专业、友好",
            "firm": "坚定、明确、不退让",
            "empathetic": "同理心、理解、关怀",
            "casual": "轻松、随意、友好"
        }

        type_instructions = {
            "professional": "正式、商务风格",
            "casual": "非正式、轻松风格",
            "detailed": "详细、全面解释",
            "brief": "简洁、直奔主题"
        }

        points_str = ""
        if include_points:
            points_str = f"\n\n必须包含以下要点:\n" + "\n".join(f"- {p}" for p in include_points)

        prompt = f"""
为以下邮件生成回复。

原始邮件:
主题: {email.get('subject', '')}
发件人: {email.get('from', '')}
日期: {email.get('date', '')}
正文:
{email.get('body', '')}

回复要求:
- 语气: {tone_instructions.get(tone, "礼貌")}
- 风格: {type_instructions.get(reply_type, "专业")}
- 长度: 100-300字
{points_str}

请生成一个完整、专业的回复。

返回JSON:
{{
    "subject": "回复主题（通常以Re:开头）",
    "body": "回复正文",
    "closing": "结语（如Best regards）",
    "suggested_attachments": ["建议附件1"],
    "notes": "给发件人的备注"
}}
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的邮件回复助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            logger.error(f"生成回复失败: {e}")
            raise

    async def detect_phishing(self, email: Dict) -> Dict:
        """
        检测钓鱼邮件

        Returns:
            {
                'is_phishing': false,
                'confidence': 0.05,
                'indicators': [],
                'explanation': '解释'
            }
        """
        prompt = f"""
分析以下邮件是否为钓鱼邮件。

邮件:
主题: {email.get('subject', '')}
发件人: {email.get('from', '')}
回复地址: {email.get('reply_to', email.get('from', ''))}
正文:
{email.get('body', '')[:2000]}

检查以下指标:
1. 发件人地址是否可疑
2. 是否要求紧急操作
3. 是否要求敏感信息（密码、信用卡等）
4. 是否有可疑链接
5. 是否有语法或拼写错误
6. 是否威胁账户安全

返回JSON:
{{
    "is_phishing": true/false,
    "confidence": 0.95,
    "risk_level": "high/medium/low",
    "indicators": [
        {{"type": "suspicious_sender", "description": "..."}},
        {{"type": "urgent_action", "description": "..."}}
    ],
    "explanation": "详细分析",
    "recommended_action": "建议操作"
}}
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)

            # 如果是钓鱼邮件，发送警告
            if result.get('is_phishing') and result.get('confidence', 0) > 0.7:
                logger.warning(f"检测到钓鱼邮件! {email.get('subject', '')}")

            return result

        except Exception as e:
            logger.error(f"钓鱼检测失败: {e}")
            return {
                'is_phishing': False,
                'confidence': 0,
                'error': str(e)
            }

    async def extract_invoice_data(self, email: Dict) -> Dict:
        """
        从邮件中提取发票/账单数据
        """
        prompt = f"""
从以下邮件中提取发票/账单信息。

邮件:
主题: {email.get('subject', '')}
发件人: {email.get('from', '')}
正文:
{email.get('body', '')[:2000]}

返回JSON:
{{
    "is_invoice": true/false,
    "invoice_number": "发票号",
    "invoice_date": "开票日期",
    "due_date": "到期日",
    "amount": 金额,
    "currency": "币种",
    "vendor": "供应商",
    "vendor_address": "供应商地址",
    "line_items": [
        {{"description": "项目", "quantity": 数量, "unit_price": 单价, "amount": 金额}}
    ],
    "tax_amount": 税额,
    "total_amount": 总金额,
    "payment_method": "支付方式",
    "payment_details": "支付详情"
}}
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            logger.error(f"发票数据提取失败: {e}")
            return {'is_invoice': False, 'error': str(e)}

    async def detect_urgency_and_priority(self, email: Dict) -> Dict:
        """
        检测邮件紧急程度和优先级
        """
        prompt = f"""
评估以下邮件的紧急程度和优先级。

邮件:
主题: {email.get('subject', '')}
发件人: {email.get('from', '')}
收件人: {email.get('to', [])}
时间: {email.get('date', '')}
正文:
{email.get('body', '')[:1500]}

返回JSON:
{{
    "urgency": "critical/high/medium/low",
    "urgency_confidence": 0.9,
    "priority": 1-5,
    "response_deadline": "建议的回复截止时间",
    "indicators": [
        {{"type": "keyword", "value": "urgent", "weight": 0.3}},
        {{"type": "sender_importance", "value": "VIP客户", "weight": 0.5}}
    ],
    "recommended_action_timeframe": "immediate/within_2_hours/within_24_hours/within_week",
    "reasoning": "详细分析"
}}
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            logger.error(f"紧急程度检测失败: {e}")
            return {
                'urgency': 'low',
                'priority': 3,
                'error': str(e)
            }
```

### 6.2 LangChain集成

```python
# integrations/langchain_emails.py

from typing import Dict, List
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
import logging

logger = logging.getLogger(__name__)


class LangChainEmailAssistant:
    """
    使用LangChain构建邮件助手
    """

    def __init__(
        self,
        openai_api_key: str,
        model: str = "gpt-4",
        temperature: float = 0.3
    ):
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model=model,
            temperature=temperature
        )

        # 构建对话记忆
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )

    async def chat_about_email(
        self,
        email: Dict,
        user_message: str,
        chat_history: List = None
    ) -> str:
        """
        关于邮件的对话

        用途:
        - 询问邮件内容
        - 请求生成回复
        - 请求提取信息
        """
        email_context = f"""
当前邮件:
主题: {email.get('subject', '')}
发件人: {email.get('from', '')}
正文: {email.get('body', '')[:1000]}
"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个智能邮件助手。你可以帮助用户:
1. 理解邮件内容
2. 生成回复建议
3. 提取关键信息
4. 回答关于邮件的问题

请用中文回答，保持专业和友好。"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{email_context}\n\n用户问题: {user_message}")
        ])

        conversation = ConversationChain(
            llm=self.llm,
            prompt=prompt,
            memory=self.memory if not chat_history else None,
            verbose=True
        )

        # 如果有历史记录，手动设置
        if chat_history:
            for msg in chat_history:
                if isinstance(msg, dict):
                    if msg['role'] == 'user':
                        self.memory.chat_memory.add_user_message(msg['content'])
                    else:
                        self.memory.chat_memory.add_ai_message(msg['content'])

        response = await conversation.apredict(
            email_context=email_context,
            user_message=user_message
        )

        return response

    async def analyze_email_thread(
        self,
        emails: List[Dict]
    ) -> Dict:
        """
        分析邮件线程
        """
        # 构建线程摘要
        thread_summary = "邮件线程摘要:\n\n"
        for i, email in enumerate(emails, 1):
            thread_summary += f"邮件{i}:\n"
            thread_summary += f"  发件人: {email.get('from', '')}\n"
            thread_summary += f"  日期: {email.get('date', '')}\n"
            thread_summary += f"  内容: {email.get('body', '')[:300]}\n\n"

        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是邮件分析专家。请分析邮件线程并提供洞察。"),
            ("human", "{thread_summary}\n\n请提供:")
        ])

        analysis = await self.llm.apredict(
            thread_summary=thread_summary + """
1. 讨论的主要话题是什么?
2. 当前状态如何?
3. 是否有未解决的问题?
4. 下一步建议是什么?
5. 参与者立场如何?
"""
        )

        return {
            'thread_summary': analysis,
            'email_count': len(emails),
            'participants': list(set(e.get('from', '') for e in emails))
        }

    def build_email_chain(self):
        """
        构建邮件处理链

        链式处理:
        接收邮件 → 分类 → 提取信息 → 生成摘要 → 建议动作
        """
        from langchain.chains import SequentialChain
        from langchain.chains import LLMChain

        # 分类链
        classify_prompt = ChatPromptTemplate.from_template(
            "分类以下邮件:\n\n主题: {subject}\n正文: {body}\n\n"
            "返回类别 (工作/个人/促销/账单/通知/其他):"
        )
        classify_chain = LLMChain(
            llm=self.llm,
            prompt=classify_prompt,
            output_key="category"
        )

        # 提取链
        extract_prompt = ChatPromptTemplate.from_template(
            "从以下邮件中提取关键信息:\n\n{email_text}\n\n"
            "提取: 订单号、金额、日期、联系人:"
        )
        extract_chain = LLMChain(
            llm=self.llm,
            prompt=extract_prompt,
            output_key="extracted_info"
        )

        # 摘要链
        summarize_prompt = ChatPromptTemplate.from_template(
            "总结以下邮件:\n\n{email_text}\n\n"
            "摘要(50字以内):"
        )
        summarize_chain = LLMChain(
            llm=self.llm,
            prompt=summarize_prompt,
            output_key="summary"
        )

        # 建议动作链
        action_prompt = ChatPromptTemplate.from_template(
            "基于以下邮件信息建议下一步动作:\n\n"
            "类别: {category}\n"
            "摘要: {summary}\n"
            "提取信息: {extracted_info}\n\n"
            "建议动作:"
        )
        action_chain = LLMChain(
            llm=self.llm,
            prompt=action_prompt,
            output_key="suggested_action"
        )

        # 组合成顺序链
        overall_chain = SequentialChain(
            chains=[
                classify_chain,
                extract_chain,
                summarize_chain,
                action_chain
            ],
            input_variables=["subject", "body", "email_text"],
            output_variables=["category", "extracted_info", "summary", "suggested_action"],
            verbose=True
        )

        return overall_chain
```

---

## 7. 完整代码示例

### 7.1 主应用

```python
# app.py

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging

from services.email_receiver import EmailReceiver
from services.email_pipeline import EmailProcessingPipeline, BatchEmailProcessor
from models.email_classifier import EmailClassifier, LLMEmailClassifier
from models.intent_recognizer import IntentRecognizer
from models.sentiment_analyzer import SentimentAnalyzer
from models.information_extractor import InformationExtractor
from models.summarizer import EmailSummarizer
from integrations.openai_client import OpenAIEmailProcessor

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="AI Email Processing API",
    description="智能邮件处理服务",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局组件
class Components:
    classifier = None
    intent_recognizer = None
    sentiment_analyzer = None
    info_extractor = None
    summarizer = None
    pipeline = None
    openai_processor = None

    @classmethod
    async def initialize(cls, config: dict):
        """初始化所有组件"""
        # 传统ML模型
        cls.classifier = EmailClassifier()
        cls.intent_recognizer = IntentRecognizer(use_llm=False)
        cls.sentiment_analyzer = SentimentAnalyzer()
        cls.info_extractor = InformationExtractor()
        cls.summarizer = EmailSummarizer(use_llm=True, api_key=config.get('openai_api_key'))

        # LLM处理器
        if config.get('openai_api_key'):
            cls.openai_processor = OpenAIEmailProcessor(
                api_key=config['openai_api_key']
            )

        # 处理管道
        cls.pipeline = EmailProcessingPipeline(
            classifier=cls.classifier,
            intent_recognizer=cls.intent_recognizer,
            sentiment_analyzer=cls.sentiment_analyzer,
            info_extractor=cls.info_extractor,
            summarizer=cls.summarizer
        )

        logger.info("所有组件初始化完成")


# 数据模型
class EmailModel(BaseModel):
    subject: str
    from: str
    to: List[str]
    date: Optional[str] = None
    body: str
    html: Optional[str] = None


class ProcessEmailRequest(BaseModel):
    email: EmailModel
    config: Optional[dict] = None


class GenerateReplyRequest(BaseModel):
    email: EmailModel
    reply_type: str = "professional"
    tone: str = "polite"
    include_points: Optional[List[str]] = None


class AnalyzeRequest(BaseModel):
    email_text: str


# API端点

@app.on_event("startup")
async def startup_event():
    """启动时初始化"""
    config = {
        'openai_api_key': 'your-api-key-here'  # 从环境变量获取
    }
    await Components.initialize(config)


@app.get("/")
async def root():
    """健康检查"""
    return {
        "status": "running",
        "service": "AI Email Processing API",
        "version": "1.0.0"
    }


@app.post("/api/email/process")
async def process_email(request: ProcessEmailRequest):
    """
    处理邮件（完整流程）

    包括: 分类、意图识别、情感分析、信息提取、摘要
    """
    try:
        email_dict = request.email.dict()
        result = await Components.pipeline.process(
            email=email_dict,
            config=request.config
        )
        return result
    except Exception as e:
        logger.error(f"处理邮件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/email/classify")
async def classify_email(request: AnalyzeRequest):
    """分类邮件"""
    try:
        result = Components.classifier.predict(request.email_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/email/intent")
async def recognize_intent(request: AnalyzeRequest):
    """识别意图"""
    try:
        email_dict = {'body': request.email_text}
        result = Components.intent_recognizer.recognize(email_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/email/sentiment")
async def analyze_sentiment(request: AnalyzeRequest):
    """分析情感"""
    try:
        result = Components.sentiment_analyzer.analyze(request.email_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/email/extract")
async def extract_info(request: AnalyzeRequest):
    """提取信息"""
    try:
        result = Components.info_extractor.extract(request.email_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/email/summarize")
async def summarize_email(request: AnalyzeRequest):
    """生成摘要"""
    try:
        email_dict = {'body': request.email_text}
        result = await Components.summarizer.summarize(email_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/email/reply/generate")
async def generate_reply(request: GenerateReplyRequest):
    """生成回复"""
    try:
        if not Components.openai_processor:
            raise HTTPException(status_code=501, detail="OpenAI未配置")

        email_dict = request.email.dict()
        result = await Components.openai_processor.generate_reply(
            email=email_dict,
            reply_type=request.reply_type,
            tone=request.tone,
            include_points=request.include_points
        )
        return result
    except Exception as e:
        logger.error(f"生成回复失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/email/phishing/check")
async def check_phishing(request: AnalyzeRequest):
    """检测钓鱼邮件"""
    try:
        if not Components.openai_processor:
            raise HTTPException(status_code=501, detail="OpenAI未配置")

        email_dict = {'body': request.email_text}
        result = await Components.openai_processor.detect_phishing(email_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/email/invoice/extract")
async def extract_invoice(request: AnalyzeRequest):
    """提取发票信息"""
    try:
        if not Components.openai_processor:
            raise HTTPException(status_code=501, detail="OpenAI未配置")

        email_dict = {'body': request.email_text}
        result = await Components.openai_processor.extract_invoice_data(email_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 7.2 配置文件

```python
# config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False

    # 邮件配置
    imap_host: str
    imap_username: str
    imap_password: str
    imap_port: int = 993

    # OpenAI配置
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"

    # 数据库配置
    database_url: str = "postgresql://user:pass@localhost/emaildb"
    redis_url: str = "redis://localhost:6379/0"

    # 处理配置
    max_concurrent_emails: int = 5
    processing_timeout: int = 300

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 8. 部署与优化

### 8.1 Docker部署

```dockerfile
# Dockerfile

FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml

version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - IMAP_HOST=${IMAP_HOST}
      - IMAP_USERNAME=${IMAP_USERNAME}
      - IMAP_PASSWORD=${IMAP_PASSWORD}
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=emaildb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    volumes:
      - redis_data:/data

  worker:
    build: .
    command: celery -A tasks worker --loglevel=info
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - redis

volumes:
  postgres_data:
  redis_data:
```

### 8.2 性能优化

```python
# utils/cache.py

from functools import wraps
from typing import Dict, Any
import hashlib
import json
import redis
import pickle

redis_client = redis.Redis(host='localhost', port=6379, db=0)


def cache_result(ttl: int = 3600):
    """
    缓存函数结果

    Args:
        ttl: 过期时间（秒）
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = _generate_cache_key(func.__name__, args, kwargs)

            # 尝试从缓存获取
            cached = redis_client.get(cache_key)
            if cached:
                return pickle.loads(cached)

            # 执行函数
            result = await func(*args, **kwargs)

            # 存入缓存
            redis_client.setex(
                cache_key,
                ttl,
                pickle.dumps(result)
            )

            return result
        return wrapper
    return decorator


def _generate_cache_key(func_name: str, args: tuple, kwargs: dict) -> str:
    """生成缓存键"""
    # 简化实现
    key_data = {
        'func': func_name,
        'args': str(args),
        'kwargs': str(sorted(kwargs.items()))
    }
    key_hash = hashlib.md5(json.dumps(key_data).encode()).hexdigest()
    return f"cache:{func_name}:{key_hash}"


# 使用示例

@cache_result(ttl=1800)
async def classify_email_cached(email_text: str):
    """带缓存的邮件分类"""
    # 实际分类逻辑
    pass
```

### 8.3 监控与日志

```python
# utils/monitoring.py

import time
import logging
from prometheus_client import Counter, Histogram, Gauge
import structlog

# Prometheus指标
email_processed = Counter('emails_processed_total', 'Total emails processed')
email_processing_time = Histogram('email_processing_seconds', 'Email processing time')
emails_in_queue = Gauge('emails_in_queue', 'Emails waiting to be processed')

# 结构化日志
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


def track_processing(func):
    """追踪处理时间"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            result = await func(*args, **kwargs)

            # 记录成功
            email_processed.inc()
            processing_time = time.time() - start_time
            email_processing_time.observe(processing_time)

            logger.info(
                "email_processed",
                function=func.__name__,
                processing_time=processing_time,
                status="success"
            )

            return result

        except Exception as e:
            logger.error(
                "email_processing_failed",
                function=func.__name__,
                error=str(e),
                status="error"
            )
            raise

    return wrapper
```

---

## 9. 安全与隐私

### 9.1 数据脱敏

```python
# utils/data_sanitizer.py

import re
from typing import Dict, List

class EmailDataSanitizer:
    """
    邮件数据脱敏器

    用于在发送到LLM前移除敏感信息
    """

    # 敏感信息模式
    PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        'api_key': r'\b[A-Za-z0-9]{32,}\b',
    }

    def sanitize(self, email: Dict) -> Dict:
        """脱敏邮件数据"""
        sanitized = email.copy()

        # 脱敏主题
        if sanitized.get('subject'):
            sanitized['subject'] = self._sanitize_text(sanitized['subject'])

        # 脱敏正文
        if sanitized.get('body'):
            sanitized['body'] = self._sanitize_text(sanitized['body'])

        # 脱敏发件人（保留域名）
        if sanitized.get('from'):
            sanitized['from'] = self._sanitize_email(sanitized['from'])

        # 脱敏收件人
        if sanitized.get('to'):
            sanitized['to'] = [
                self._sanitize_email(addr)
                for addr in sanitized['to']
            ]

        return sanitized

    def _sanitize_text(self, text: str) -> str:
        """脱敏文本"""
        for type_, pattern in self.PATTERNS.items():
            text = re.sub(
                pattern,
                self._replacement(type_),
                text
            )
        return text

    def _sanitize_email(self, email: str) -> str:
        """脱敏邮箱地址"""
        # 保留域名，隐藏用户名部分
        match = re.match(r'([^@]+)@(.+)', email)
        if match:
            username, domain = match.groups()
            # 保留首字母和长度
            masked = username[0] + '*' * (len(username) - 1)
            return f"{masked}@{domain}"
        return email

    def _replacement(self, type_: str) -> str:
        """生成替换字符串"""
        replacements = {
            'email': '[EMAIL_REDACTED]',
            'phone': '[PHONE_REDACTED]',
            'ssn': '[SSN_REDACTED]',
            'credit_card': '[CARD_REDACTED]',
            'ip_address': '[IP_REDACTED]',
            'api_key': '[API_KEY_REDACTED]',
        }
        return replacements.get(type_, '[REDACTED]')
```

### 9.2 权限控制

```python
# utils/auth.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """验证访问令牌"""
    token = credentials.credentials

    # 验证逻辑（示例）
    if token != "valid-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    return {"user": "authenticated", "scope": ["read", "write"]}


# 使用示例

@app.post("/api/email/process")
async def process_email(
    request: ProcessEmailRequest,
    auth: Dict = Depends(verify_token)
):
    """需要认证的处理端点"""
    if "write" not in auth.get("scope", []):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # 处理逻辑
    pass
```

---

## 总结

本文档提供了AI邮件处理的完整解决方案，涵盖：

### ✅ 核心能力

| 能力 | 实现方式 |
|------|----------|
| 邮件分类 | 传统ML / LLM |
| 意图识别 | 规则引擎 / LLM |
| 情感分析 | VADER / TextBlob / LLM |
| 信息提取 | 正则 / NER / LLM |
| 摘要生成 | 抽取式 / 生成式 |
| 回复生成 | OpenAI / LangChain |

### 🎯 应用场景

- **个人用户**: 智能分类、自动回复、摘要提醒
- **企业客服**: 工单分类、意图路由、情感监控
- **财务处理**: 发票提取、账单管理
- **安全防护**: 钓鱼检测、垃圾过滤

### 🚀 下一步

1. 根据需求选择技术栈
2. 实现核心处理管道
3. 集成邮件服务器
4. 部署监控告警
5. 持续优化模型

---

**文档版本:** v1.0
**最后更新:** 2026-03-12
