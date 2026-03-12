# AI 功能集成方案

> **跨境电商全工作流系统** - AI 引擎设计与实现

**版本**: v1.0.0
**更新时间**: 2026-03-12
**优先级**: 🔥 最高 (AI 修图)

---

## 目录

1. [AI 功能概览](#ai-功能概览)
2. [AI 修图系统](#ai-修图系统)
3. [AI 文案生成](#ai-文案生成)
4. [AI 提示词优化](#ai-提示词优化)
5. [AI 智能客服](#ai-智能客服)
6. [模型选型](#模型选型)
7. [成本优化](#成本优化)

---

## AI 功能概览

### 功能矩阵

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          AI 功能矩阵                                    │
├─────────────┬─────────────┬─────────────┬─────────────┬───────────────┤
│   功能      │   输入      │   模型      │   输出      │   优先级      │
├─────────────┼─────────────┼─────────────┼─────────────┼───────────────┤
│ 背景移除    │ 产品图片    │ rembg/SD    │ 透明PNG     │ ⭐⭐⭐⭐⭐    │
│ 场景合成    │ 产品+背景   │ SD XL       │ 合成图片    │ ⭐⭐⭐⭐⭐    │
│ 图片增强    │ 低清图片    │ Real-ESRGAN │ 高清图片    │ ⭐⭐⭐⭐      │
│ 标题生成    │ 产品信息    │ GPT-4       │ SEO标题     │ ⭐⭐⭐⭐      │
│ 文案生成    │ 产品信息    │ GPT-4       │ 五点描述    │ ⭐⭐⭐⭐      │
│ A+页面      │ 产品图片    │ GPT-4+SD    │ HTML+图片   │ ⭐⭐⭐       │
│ 关键词优化  │ 竞品数据    │ GPT-4       │ 关键词列表  │ ⭐⭐⭐⭐      │
│ 客服回复    │ 客户消息    │ GPT-4+RAG   │ 回复文本    │ ⭐⭐⭐       │
│ 评价分析    │ 评价内容    │ GPT-4       │ 情感/标签   │ ⭐⭐⭐       │
│ 选品分析    │ 市场数据    │ GPT-4+Lang  │ 评分报告    │ ⭐⭐⭐⭐⭐    │
└─────────────┴─────────────┴─────────────┴─────────────┴───────────────┘
```

### AI 引擎架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          AI 引擎架构                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    API Gateway (FastAPI)                        │   │
│  │  /api/v1/ai/image/*  /api/v1/ai/text/*  /api/v1/ai/chat/*      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    AI Orchestrator                              │   │
│  │  • 任务路由  • 模型选择  • 结果聚合  • 错误重试                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│         ┌────────────────────┼────────────────────┐                    │
│         │                    │                    │                    │
│         ▼                    ▼                    ▼                    │
│  ┌────────────┐      ┌────────────┐      ┌────────────┐              │
│  │ Image AI   │      │  Text AI   │      │ Chat AI    │              │
│  │  Service   │      │  Service   │      │  Service   │              │
│  ├────────────┤      ├────────────┤      ├────────────┤              │
│  │ rembg      │      │ OpenAI     │      │ GPT-4      │              │
│  │ SD XL      │      │ Claude     │      │ RAG        │              │
│  │ ESRGAN     │      │ Local LLM  │      │ Vector DB  │              │
│  └────────────┘      └────────────┘      └────────────┘              │
│         │                    │                    │                    │
│         └────────────────────┼────────────────────┘                    │
│                              │                                          │
│                              ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Shared Services                              │   │
│  │  • Prompt Manager  • Cache Layer  • Queue  • Monitoring         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## AI 修图系统

### 功能流程图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI 修图工作流                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  输入: 产品原图 (来自 1688/摄影师)                                       │
│    │                                                                    │
│    ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Step 1: 图片预处理                                             │   │
│  │  • 格式转换  • 尺寸标准化  • 质量检查                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│    │                                                                    │
│    ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Step 2: 背景移除 (rembg)                                       │   │
│  │  • 自动检测主体  • 精细边缘  • 透明背景                          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│    │                                                                    │
│    ├───────────────────────────────────────────────────────────────┐   │
│    │                                                               │   │
│    ▼ (路径A)                                             ▼ (路径B)    │
│  ┌─────────────────────┐                             ┌─────────────────┐│
│  │  场景合成            │                             │  纯白背景        ││
│  │  (Stable Diffusion)  │                             │  (直接输出)      ││
│  └─────────────────────┘                             └─────────────────┘│
│    │                                                               │   │
│    ▼                                                               │   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Step 3: 图片增强 (Real-ESRGAN)                                │   │
│  │  • 超分辨率  • 去噪  • 锐化                                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│    │                                                                    │
│    ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Step 4: 批量生成                                               │   │
│  │  • 多角度变体  • 不同场景  • 尺寸适配                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│    │                                                                    │
│    ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Step 5: Amazon 规范检查                                        │   │
│  │  • 尺寸限制  • 文件大小  • 格式要求                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│    │                                                                    │
│    ▼                                                                    │
│  输出: Amazon 合规图片集 (主图/PT图/Gallery图)                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 实现代码

#### 背景移除

```python
# backend/ai/image/background_removal.py
from typing import List, Optional
import io
from PIL import Image
import rembg
from fastapi import UploadFile, HTTPException

class BackgroundRemovalService:
    """背景移除服务"""

    def __init__(self, model_name: str = "u2net"):
        """初始化模型"""
        self.session = rembg.new_session(model_name)

    async def remove_background(
        self,
        image: UploadFile,
        return_format: str = "png"
    ) -> bytes:
        """
        移除图片背景

        Args:
            image: 上传的图片
            return_format: 返回格式 (png/webp)

        Returns:
            处理后的图片字节流
        """
        try:
            # 读取图片
            input_image = await image.read()

            # 处理图片
            output_image = rembg.remove(
                input_image,
                session=self.session,
                alpha_matting=True,  # 启用 alpha 抠图优化
                alpha_matting_foreground_threshold=270,
                alpha_matting_background_threshold=20,
                alpha_matting_erode_size=11
            )

            # 转换格式
            if return_format == "webp":
                img = Image.open(io.BytesIO(output_image))
                buffer = io.BytesIO()
                img.save(buffer, format="WEBP", quality=95)
                return buffer.getvalue()

            return output_image

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"背景移除失败: {str(e)}")

    async def batch_remove_background(
        self,
        images: List[UploadFile]
    ) -> List[bytes]:
        """批量移除背景"""
        results = []
        for image in images:
            result = await self.remove_background(image)
            results.append(result)
        return results
```

#### 场景合成 (Stable Diffusion)

```python
# backend/ai/image/composition.py
from typing import List, Optional
import io
import base64
from PIL import Image
import torch
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
from fastapi import HTTPException

class ImageCompositionService:
    """图片场景合成服务"""

    def __init__(self):
        """初始化 Stable Diffusion"""
        # 加载 ControlNet (用于保持产品主体)
        controlnet = ControlNetModel.from_pretrained(
            "lllyasviel/sd-controlnet-canny",
            torch_dtype=torch.float16
        )

        # 加载主模型
        self.pipe = StableDiffusionControlNetPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            controlnet=controlnet,
            torch_dtype=torch.float16,
            safety_checker=None
        )

        # 优化
        self.pipe = self.pipe.to("cuda")
        self.pipe.enable_model_cpu_offload()

    async def compose_scene(
        self,
        product_image: bytes,
        background_prompt: str,
        negative_prompt: str = "",
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5
    ) -> bytes:
        """
        场景合成

        Args:
            product_image: 产品图片（无背景）
            background_prompt: 背景描述
            negative_prompt: 负面提示词
            num_inference_steps: 推理步数
            guidance_scale: 引导系数

        Returns:
            合成后的图片
        """
        try:
            # 加载产品图片
            product = Image.open(io.BytesIO(product_image)).convert("RGB")

            # 生成边缘检测 (用于 ControlNet)
            from cv2 import Canny, cvtColor, COLOR_RGB2GRAY
            import numpy as np

            img_array = np.array(product)
            edges = Canny(img_array, 100, 200)
            canny_image = Image.fromarray(edges).convert("RGB")

            # 默认负面提示词
            default_negative = """
            low quality, blurry, distorted, deformed, ugly,
            bad anatomy, bad proportions, duplicate, watermark,
            text, logo, signature, extra limbs
            """
            negative_prompt = f"{default_negative}, {negative_prompt}"

            # 生成图片
            result = self.pipe(
                prompt=background_prompt,
                negative_prompt=negative_prompt,
                image=canny_image,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                height=1024,
                width=1024
            ).images[0]

            # 保存到字节流
            buffer = io.BytesIO()
            result.save(buffer, format="PNG", quality=95)
            return buffer.getvalue()

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"场景合成失败: {str(e)}")

    # 预设场景
    SCENE_PROMPTS = {
        "minimalist_white": "professional product photography, clean white background, studio lighting, high quality, 4k",
        "modern_living": "modern living room, natural lighting, lifestyle scene, interior design, photorealistic",
        "kitchen_counter": "kitchen counter, marble surface, bright natural light, culinary scene, professional",
        "office_desk": "modern office desk, clean workspace, productivity scene, natural lighting",
        "outdoor_nature": "outdoor nature scene, natural environment, soft sunlight, lifestyle photography",
    }
```

#### 批量生成

```python
# backend/ai/image/batch_generator.py
from typing import List, Dict
import asyncio
from pathlib import Path

class BatchImageGenerator:
    """批量图片生成器"""

    def __init__(
        self,
        background_service: BackgroundRemovalService,
        composition_service: ImageCompositionService
    ):
        self.bg_service = background_service
        self.comp_service = composition_service

    async def generate_product_images(
        self,
        product_image: UploadFile,
        scenes: List[str] = None,
        generate_variants: bool = True
    ) -> Dict[str, List[bytes]]:
        """
        生成完整产品图片集

        Args:
            product_image: 产品原图
            scenes: 场景列表
            generate_variants: 是否生成变体

        Returns:
            {
                "main": [...],      # 主图
                "pt": [...],        # PT图
                "gallery": [...]    # Gallery图
            }
        """
        # 默认场景
        if scenes is None:
            scenes = ["minimalist_white", "modern_living", "kitchen_counter"]

        images = {
            "main": [],
            "pt": [],
            "gallery": []
        }

        # Step 1: 背景移除
        product_no_bg = await self.bg_service.remove_background(product_image)

        # Step 2: 生成主图 (纯白背景)
        from PIL import Image
        import io

        img = Image.open(io.BytesIO(product_no_bg))
        white_bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        white_bg.paste(img, mask=img.split()[3])

        buffer = io.BytesIO()
        white_bg.convert("RGB").save(buffer, format="JPEG", quality=95)
        images["main"].append(buffer.getvalue())

        # Step 3: 生成场景图
        for scene in scenes:
            prompt = ImageCompositionService.SCENE_PROMPTS.get(scene, scene)
            scene_image = await self.comp_service.compose_scene(
                product_image=product_no_bg,
                background_prompt=prompt
            )

            if scene == "minimalist_white":
                images["pt"].append(scene_image)
            else:
                images["gallery"].append(scene_image)

        # Step 4: 生成变体 (不同角度)
        if generate_variants:
            # 这里可以结合 3D 模型或多角度拍摄
            pass

        return images

    async def batch_generate_products(
        self,
        products: List[UploadFile]
    ) -> List[Dict[str, List[bytes]]]:
        """批量处理多个产品"""
        tasks = [
            self.generate_product_images(product)
            for product in products
        ]
        return await asyncio.gather(*tasks)
```

### API 端点

```python
# backend/api/routes/ai_image.py
from fastapi import APIRouter, UploadFile, File, Form
from typing import List

router = APIRouter(prefix="/api/v1/ai/image", tags=["AI Image"])

@router.post("/remove-background")
async def remove_background(
    image: UploadFile = File(...),
    format: str = Form("png")
):
    """移除图片背景"""
    service = BackgroundRemovalService()
    result = await service.remove_background(image, format)
    return Response(content=result, media_type=f"image/{format}")

@router.post("/compose-scene")
async def compose_scene(
    product_image: UploadFile = File(...),
    background_prompt: str = Form(...),
    negative_prompt: str = Form(""),
    steps: int = Form(50)
):
    """场景合成"""
    service = ImageCompositionService()
    result = await service.compose_scene(
        product_image=await product_image.read(),
        background_prompt=background_prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=steps
    )
    return Response(content=result, media_type="image/png")

@router.post("/generate-product-set")
async def generate_product_set(
    images: List[UploadFile] = File(...),
    scenes: str = Form("minimalist_white,modern_living")
):
    """生成完整产品图片集"""
    scene_list = scenes.split(",")

    service = BatchImageGenerator(
        BackgroundRemovalService(),
        ImageCompositionService()
    )

    results = await service.batch_generate_products(images)

    # 上传到 MinIO 并返回 URL
    # ...

    return {
        "products": len(results),
        "images_per_product": sum(len(v) for v in results[0].values())
    }
```

---

## AI 文案生成

### 功能架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI 文案生成流程                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  输入: 产品信息 (图片/标题/类目/特性)                                     │
│    │                                                                    │
│    ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Step 1: 信息提取 (GPT-4 Vision)                               │   │
│  │  • 图片分析  • 特征识别  • 卖点提取                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│    │                                                                    │
│    ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Step 2: 关键词研究 (内置数据库 + API)                           │   │
│  │  • 搜索量  • 竞争度  • 相关词                                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│    │                                                                    │
│    ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Step 3: 文案生成 (GPT-4 + Prompt 模板)                         │   │
│  │  • 标题 (200字符)                                                │   │
│  │  • 五点描述 (5点 × 100字符)                                       │   │
│  │  • Search Terms (249字节)                                        │   │
│  │  • A+ 页面内容                                                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│    │                                                                    │
│    ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Step 4: SEO 优化                                               │   │
│  │  • 关键词密度  • 可读性  • 合规检查                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│    │                                                                    │
│    ▼                                                                    │
│  输出: 优化后的文案 (JSON)                                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Prompt 模板

```python
# backend/ai/text/prompts.py

PROMPT_TEMPLATES = {
    "product_title": """
你是一位专业的 Amazon SEO 文案专家。请根据以下产品信息生成优化后的商品标题。

**产品信息:**
{product_info}

**要求:**
1. 标题长度: 150-200 字符
2. 包含核心关键词: {keywords}
3. 结构: 品牌 + 产品名称 + 核心特性 + 适用场景
4. 避免堆砌关键词，保持自然流畅
5. 突出卖点和差异化

**输出格式:**
只返回优化后的标题，不要其他内容。

Title: """,
    # ... 其他模板
}
```

---

## AI 智能客服

### RAG 架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        RAG (检索增强生成)                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  用户消息                                                               │
│    │                                                                    │
│    ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  意图识别                                                        │   │
│  │  • 分类: 订单/产品/退款/投诉/咨询                                 │   │
│  │  • 情感: 积极/中性/负面                                          │   │
│  │  • 紧急度: 低/中/高                                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│    │                                                                    │
│    ├───────────────────────────────────────────────────────────────┐   │
│    │                                                               │   │
│    ▼ (常见问题)                                         ▼ (复杂问题)   │
│  ┌─────────────────────┐                             ┌─────────────────┐│
│  │  知识库检索          │                             │  LLM 生成        ││
│  │  • FAQ              │                             │  • 上下文理解    ││
│  │  • 历史回复          │                             │  • 知识检索      ││
│  └─────────────────────┘                             │  • 个性化回复    ││
│         │                                            └─────────────────┘│
│         │                                                       │       │
│         └───────────────────────────┬───────────────────────────┘       │
│                                     │                                   │
│                                     ▼                                   │
│                          ┌─────────────────────┐                         │
│                          │  回复后处理          │                         │
│                          │  • 多语言翻译        │                         │
│                          │  • 语气调整          │                         │
│                          │  • 合规检查          │                         │
│                          └─────────────────────┘                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 模型选型

### 推荐配置

| 功能 | 模型选择 | 部署方式 | 预估成本 |
|------|----------|----------|----------|
| **背景移除** | rembg u2net | 本地 | 免费 |
| **场景合成** | SDXL 1.0 | 本地 (GPU) | GPU 成本 |
| **图片增强** | Real-ESRGAN | 本地 | 免费 |
| **文案生成** | GPT-4 Turbo | API | $0.01/1K tokens |
| **客服** | GPT-4 + RAG | API | $0.01/1K tokens |
| **嵌入** | text-embedding-3-small | API | $0.00002/1K tokens |

### 混合策略

```python
# 混合 AI 服务配置
AI_CONFIG = {
    "background_removal": {
        "provider": "local",
        "model": "rembg",
        "cost": 0
    },
    "image_generation": {
        "provider": "local",
        "model": "SDXL",
        "gpu_required": True,
        "cost": "gpu_amortization"
    },
    "copywriting": {
        "provider": "openai",
        "model": "gpt-4-turbo",
        "cost_per_1k_tokens": 0.01
    },
    "customer_service": {
        "provider": "openai",
        "model": "gpt-4-turbo",
        "context_window": 128000,
        "cost_per_1k_tokens": 0.01
    }
}
```

---

## 成本优化

### 成本控制策略

```python
# backend/ai/cost_optimizer.py

class CostOptimizer:
    """AI 成本优化器"""

    def __init__(self):
        self.cost_tracker = {}

    async def optimize_request(
        self,
        task: str,
        input_data: dict
    ) -> dict:
        """优化 AI 请求"""

        # 1. 检查缓存
        cached = await self._check_cache(task, input_data)
        if cached:
            return cached

        # 2. 模型选择
        model = self._select_model(task, input_data)

        # 3. Token 优化
        optimized_input = self._optimize_tokens(input_data)

        # 4. 批量处理
        if self._can_batch(task):
            return await self._batch_process(task, optimized_input)

        # 5. 执行请求
        result = await self._execute(model, optimized_input)

        # 6. 缓存结果
        await self._cache_result(task, input_data, result)

        return result

    def _select_model(self, task: str, input_data: dict) -> str:
        """根据任务选择最优模型"""
        # 简单任务用小模型
        if task in ["background_removal", "image_enhance"]:
            return "local_model"

        # 长文本用大上下文模型
        if input_data.get("token_count", 0) > 8000:
            return "gpt-4-turbo-128k"

        # 默认
        return "gpt-4-turbo"
```

---

**下一步**: 查看 [05_OPENCLAW_INTEGRATION.md](./05_OPENCLAW_INTEGRATION.md)
