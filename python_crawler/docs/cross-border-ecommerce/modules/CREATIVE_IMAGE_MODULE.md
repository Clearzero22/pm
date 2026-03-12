# AI 创作系统 - AI 修图模块

> **最高优先级模块** - AI 驱动的产品图片自动化处理

**优先级**: 🔥🔥🔥🔥🔥
**预计工作量**: 3-4 周

---

## 目录

1. [模块概述](#模块概述)
2. [功能设计](#功能设计)
3. [技术实现](#技术实现)
4. [API 设计](#api-设计)
5. [成本优化](#成本优化)

---

## 模块概述

### 业务价值

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AI 修图业务价值                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  传统方式:                                                               │
│  • 专业摄影师拍摄: ¥500-1000/天                                         │
│  • 设计师修图: ¥50-100/张                                               │
│  • 场景搭建: ¥200-500/场景                                             │
│  • 外包制作: 3-7 天                                                     │
│                                                                         │
│  AI 方式:                                                                │
│  • 自动背景移除: ¥0.01/张                                               │
│  • AI 场景合成: ¥0.05-0.10/张                                          │
│  • 批量处理: 100+ 张/小时                                               │
│  • 即时生成: 30 秒/张                                                   │
│                                                                         │
│  成本节省: 80-90%                                                       │
│  时间节省: 95%+                                                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 核心功能

| 功能 | 说明 | 优先级 |
|------|------|--------|
| **背景移除** | 自动检测并移除产品背景 | ⭐⭐⭐⭐⭐ |
| **场景合成** | 产品 + 背景图智能融合 | ⭐⭐⭐⭐⭐ |
| **图片增强** | 超分辨率、去噪、锐化 | ⭐⭐⭐⭐ |
| **批量生成** | 一次处理 100+ 张图片 | ⭐⭐⭐⭐⭐ |
| **格式转换** | Amazon 规范格式输出 | ⭐⭐⭐⭐ |
| **水印添加** | 品牌/Logo 水印 | ⭐⭐⭐ |

---

## 功能设计

### 1. 背景移除

#### 技术选型

```
方案对比:

┌─────────────┬────────────┬────────────┬────────────┐
│     方案     │   质量     │   成本     │   速度     │
├─────────────┼────────────┼────────────┼────────────┤
│ rembg       │ ⭐⭐⭐⭐   │   免费     │  ⚡⚡⚡    │
│ remove.bg   │ ⭐⭐⭐⭐⭐  │ $0.20/张   │  ⚡⚡      │
│ Segment Anything │ ⭐⭐⭐⭐⭐ │ GPU成本   │  ⚡       │
└─────────────┴────────────┴────────────┴────────────┘

推荐: rembg (本地部署，免费够用)
升级: Segment Anything (高质量需求)
```

#### 处理流程

```
输入: 产品原图 (供应商/摄影师)
    │
    ▼
┌─────────────────────────────────────┐
│  Step 1: 图片预处理                  │
│  • 格式统一化 (JPG/PNG)             │
│  • 尺寸标准化 (最大边长 2000px)      │
│  • 质量检查 (模糊/过曝检测)          │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  Step 2: 主体检测                   │
│  • rembg U2NET 模型                 │
│  • 自动检测主要物体                 │
│  • 边缘优化 (alpha matting)         │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  Step 3: 背景移除                   │
│  • 生成透明 PNG                     │
│  • 边缘羽化处理                     │
│  • 残留背景清理                     │
└─────────────────────────────────────┘
    │
    ▼
输出: 无背景产品图 (透明 PNG)
```

#### 代码实现

```python
# backend/services/creative/image/background_removal.py

from typing import List, Optional
import io
import numpy as np
from PIL import Image
import rembg
from fastapi import UploadFile, HTTPException
import cv2

class BackgroundRemovalService:
    """背景移除服务"""

    def __init__(self, model_name: str = "u2net"):
        """
        初始化背景移除模型

        Args:
            model_name: 模型名称
                - u2net: 默认模型，速度快
                - u2netp: 小模型，更快
                - u2net_human_seg: 人物专用
                - silueta: 轻量级
        """
        self.session = rembg.new_session(model_name)

    async def remove_background(
        self,
        image: UploadFile,
        alpha_matting: bool = True,
        return_format: str = "png"
    ) -> bytes:
        """
        移除图片背景

        Args:
            image: 上传的图片
            alpha_matting: 启用 alpha 抠图优化
            return_format: 返回格式 (png/webp/jpg)

        Returns:
            处理后的图片字节流
        """
        try:
            # 读取图片
            input_image = await image.read()

            # 预处理
            img = Image.open(io.BytesIO(input_image))

            # 转换为 RGB
            if img.mode != "RGB":
                img = img.convert("RGB")

            # 处理图片
            output_image = rembg.remove(
                img,
                session=self.session,
                alpha_matting=alpha_matting,
                alpha_matting_foreground_threshold=270,
                alpha_matting_background_threshold=20,
                alpha_matting_erode_size=11
            )

            # 边缘优化
            output_image = self._refine_edges(output_image)

            # 格式转换
            if return_format == "webp":
                buffer = io.BytesIO()
                output_image.save(buffer, format="WEBP", quality=95)
                return buffer.getvalue()
            elif return_format == "jpg":
                # 创建白色背景
                background = Image.new("RGB", output_image.size, (255, 255, 255))
                background.paste(output_image, mask=output_image.split()[3])
                buffer = io.BytesIO()
                background.save(buffer, format="JPEG", quality=95)
                return buffer.getvalue()
            else:  # PNG
                buffer = io.BytesIO()
                output_image.save(buffer, format="PNG")
                return buffer.getvalue()

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"背景移除失败: {str(e)}")

    def _refine_edges(self, image: Image.Image) -> Image.Image:
        """边缘优化"""
        # 转换为 numpy 数组
        img_array = np.array(image)

        # 高斯模糊边缘
        if img_array.shape[2] == 4:  # 有 alpha 通道
            alpha = img_array[:, :, 3]

            # 形态学操作
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            alpha = cv2.morphologyEx(alpha, cv2.MORPH_OPEN, kernel)
            alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, kernel)

            # 更新 alpha 通道
            img_array[:, :, 3] = alpha

        return Image.fromarray(img_array)

    async def batch_remove_background(
        self,
        images: List[UploadFile],
        concurrent: int = 4
    ) -> List[bytes]:
        """
        批量移除背景

        Args:
            images: 图片列表
            concurrent: 并发数

        Returns:
            处理后的图片列表
        """
        import asyncio

        async def process_single(img):
            return await self.remove_background(img)

        # 分批处理
        results = []
        for i in range(0, len(images), concurrent):
            batch = images[i:i + concurrent]
            batch_results = await asyncio.gather(*[process_single(img) for img in batch])
            results.extend(batch_results)

        return results
```

### 2. 场景合成

#### 技术选型

```
方案对比:

┌─────────────┬────────────┬────────────┬────────────┐
│     方案     │   质量     │   成本     │   速度     │
├─────────────┼────────────┼────────────┼────────────┤
│ SDXL 本地   │ ⭐⭐⭐⭐⭐  │ GPU成本   │  ⚡⚡      │
│ SD API      │ ⭐⭐⭐⭐⭐  │ $0.04/张   │  ⚡⚡⚡    │
│ DALL-E 3    │ ⭐⭐⭐⭐⭐  │ $0.04/张   │  ⚡⚡      │
│ Photoshop   │ ⭐⭐⭐⭐⭐  │ 人工成本   │  ⚡        │
└─────────────┴────────────┴────────────┴────────────┘

推荐: SDXL 本地部署 (长期成本最低)
备选: Stability AI API (无需 GPU)
```

#### 预设场景库

```python
# backend/services/creative/image/scenes.py

SCENE_TEMPLATES = {
    # Amazon 主图场景
    "amazon_main": {
        "name": "Amazon 主图 (纯白)",
        "description": "纯白色背景，符合 Amazon 主图规范",
        "aspect_ratio": "1:1",
        "resolution": "2000x2000",
        "prompt_template": "professional product photography, {product} on pure white background, studio lighting, high quality, 4k, sharp focus, clean composition --ar 1:1"
    },

    # 生活方式场景
    "minimalist_desk": {
        "name": "简约办公桌",
        "description": "现代简约办公桌场景",
        "aspect_ratio": "16:9",
        "resolution": "1920x1080",
        "prompt_template": "modern minimalist desk setup, {product} placed on clean white desk, natural window light, indoor plants, professional photography, soft shadows --ar 16:9"
    },

    "modern_living": {
        "name": "现代客厅",
        "description": "明亮现代客厅场景",
        "aspect_ratio": "16:9",
        "resolution": "1920x1080",
        "prompt_template": "modern living room with large windows, {product} on wooden coffee table, natural sunlight, plants, cozy atmosphere, architectural digest style --ar 16:9"
    },

    "kitchen_modern": {
        "name": "现代厨房",
        "description": "明亮现代厨房台面",
        "aspect_ratio": "16:9",
        "resolution": "1920x1080",
        "prompt_template": "modern marble kitchen counter, {product} on clean surface, bright natural light, kitchen utensils, culinary lifestyle, professional food photography --ar 16:9"
    },

    "bedroom_cozy": {
        "name": "温馨卧室",
        "description": "温馨舒适的卧室场景",
        "aspect_ratio": "16:9",
        "resolution": "1920x1080",
        "prompt_template": "cozy modern bedroom, {product} on nightstand, warm lighting, soft bedding, lifestyle photography, peaceful atmosphere --ar 16:9"
    },

    "outdoor_patio": {
        "name": "户外庭院",
        "description": "阳光明媚的户外场景",
        "aspect_ratio": "16:9",
        "resolution": "1920x1080",
        "prompt_template": "sunny outdoor patio or balcony, {product} on rattan table, plants, bright natural light, lifestyle scene, warm afternoon --ar 16:9"
    },

    # 特殊用途场景
    "floating_product": {
        "name": "悬浮产品",
        "description": "产品悬浮效果，适合科技产品",
        "aspect_ratio": "1:1",
        "resolution": "2000x2000",
        "prompt_template": "floating {product} in mid-air, dynamic angle, gradient background, lighting effects, studio photography, 3d render style --ar 1:1"
    },

    "flat_lay": {
        "name": "平铺展示",
        "description": "俯视平铺展示",
        "aspect_ratio": "1:1",
        "resolution": "2000x2000",
        "prompt_template": "flat lay photography, {product} arranged on surface with complementary items, top-down view, professional styling, shadow depth --ar 1:1"
    }
}
```

#### 代码实现

```python
# backend/services/creative/image/composition.py

from typing import List, Optional
import io
import base64
from PIL import Image
import torch
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
from fastapi import HTTPException

class ImageCompositionService:
    """场景合成服务"""

    def __init__(self, model_path: str = "runwayml/stable-diffusion-v1-5"):
        """
        初始化 Stable Diffusion

        Args:
            model_path: 模型路径或 HuggingFace ID
        """
        # 检查 GPU 可用性
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # 加载 ControlNet (用于保持产品主体)
        controlnet = ControlNetModel.from_pretrained(
            "lllyasviel/sd-controlnet-canny",
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        )

        # 加载主模型
        self.pipe = StableDiffusionControlNetPipeline.from_pretrained(
            model_path,
            controlnet=controlnet,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            safety_checker=None
        )

        # 优化设置
        if self.device == "cuda":
            self.pipe = self.pipe.to("cuda")
            self.pipe.enable_model_cpu_offload()
            self.pipe.enable_xformers_memory_efficient_attention()

    async def compose_scene(
        self,
        product_image: bytes,
        scene_type: str = "amazon_main",
        product_description: str = "",
        negative_prompt: str = "",
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        seed: int = -1
    ) -> bytes:
        """
        场景合成

        Args:
            product_image: 产品图片（无背景）
            scene_type: 场景类型
            product_description: 产品描述
            negative_prompt: 负面提示词
            num_inference_steps: 推理步数
            guidance_scale: 引导系数
            seed: 随机种子

        Returns:
            合成后的图片
        """
        try:
            # 获取场景配置
            scene_config = SCENE_TEMPLATES.get(scene_type, SCENE_TEMPLATES["amazon_main"])

            # 加载产品图片
            product = Image.open(io.BytesIO(product_image)).convert("RGB")

            # 构建提示词
            product_info = self._analyze_product(product, product_description)
            prompt = scene_config["prompt_template"].format(
                product=product_info["description"],
                **product_info
            )

            # 默认负面提示词
            default_negative = """
            low quality, blurry, distorted, deformed, ugly, bad anatomy,
            bad proportions, duplicate, watermark, text, logo, signature,
            extra limbs, missing limbs, floating objects, disconnected,
            mutation, mutating, poorly drawn, long neck, low resolution,
            jpeg artifacts, signature, watermark, username, artist name
            """

            negative_prompt = f"{default_negative}, {negative_prompt}"

            # 生成边缘检测 (ControlNet)
            canny_image = self._generate_canny_edges(product)

            # 随机种子
            generator = None
            if seed > 0:
                generator = torch.Generator(device=self.device).manual_seed(seed)

            # 生成图片
            result = self.pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                image=canny_image,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator,
                height=int(scene_config["resolution"].split("x")[1]),
                width=int(scene_config["resolution"].split("x")[0])
            ).images[0]

            # 保存到字节流
            buffer = io.BytesIO()
            result.save(buffer, format="PNG", quality=95)
            return buffer.getvalue()

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"场景合成失败: {str(e)}")

    def _analyze_product(self, image: Image.Image, description: str) -> dict:
        """分析产品特征"""
        # 这里可以集成图像识别模型
        # 暂时返回基础信息
        return {
            "description": description or "product",
            "category": "general",
            "colors": [],
            "style": "modern"
        }

    def _generate_canny_edges(self, image: Image.Image, low_threshold: int = 100, high_threshold: int = 200) -> Image.Image:
        """生成边缘检测图 (用于 ControlNet)"""
        import cv2
        import numpy as np

        # 转换为 numpy 数组
        img_array = np.array(image)

        # Canny 边缘检测
        edges = cv2.Canny(img_array, low_threshold, high_threshold)

        # 转换回 PIL Image
        return Image.fromarray(edges).convert("RGB")
```

### 3. 图片增强

#### 代码实现

```python
# backend/services/creative/image/enhancement.py

import io
import torch
from PIL import Image
from fastapi import HTTPException

try:
    from basicsr.archs.rrdbnet_arch import RRDBNet
    from basicsr.utils.download_util import load_file_from_url
    import cv2
    import numpy as np
    REALESRGAN_AVAILABLE = True
except ImportError:
    REALESRGAN_AVAILABLE = False

class ImageEnhancementService:
    """图片增强服务"""

    def __init__(self):
        """初始化 Real-ESRGAN 模型"""
        if not REALESRGAN_AVAILABLE:
            raise HTTPException(status_code=500, detail="Real-ESRGAN 未安装")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # 加载模型
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        model_path = "weights/RealESRGAN_x4plus.pth"

        # 下载模型（如果不存在）
        import os
        if not os.path.exists(model_path):
            os.makedirs("weights", exist_ok=True)
            load_file_from_url(
                url="https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
                model_path=model_path
            )

        # 加载权重
        model.load_state_dict(torch.load(model_path), strict=True)
        model.eval()
        model = model.to(self.device)

        self.model = model

    async def enhance_image(
        self,
        image: bytes,
        scale: int = 2,
        denoise_strength: float = 0.5
    ) -> bytes:
        """
        增强图片质量

        Args:
            image: 输入图片
            scale: 放大倍数 (2/4)
            denoise_strength: 去噪强度 (0-1)

        Returns:
            增强后的图片
        """
        try:
            # 读取图片
            img = Image.open(io.BytesIO(image))
            img_np = np.array(img)

            # 预处理
            img_np = img_np[:, :, [2, 1, 0]]  # BGR
            img_np = img_np.astype(np.float32) / 255.
            img_tensor = torch.from_numpy(np.transpose(img_np[:, :, [2, 1, 0]], (2, 0, 1))).float()

            # 添加 batch 维度
            img_tensor = img_tensor.unsqueeze(0).to(self.device)

            # 推理
            with torch.no_grad():
                output = self.model(img_tensor)

            # 后处理
            output = output.data.squeeze().float().cpu().clamp_(0, 1).numpy()
            output = np.transpose(output[[2, 1, 0], (1, 2, 0))
            output = (output * 255.).round().astype(np.uint8)

            # 转换为 PIL Image
            result_img = Image.fromarray(output)

            # 保存
            buffer = io.BytesIO()
            result_img.save(buffer, format="PNG", quality=95)
            return buffer.getvalue()

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"图片增强失败: {str(e)}")
```

### 4. 批量处理

```python
# backend/services/creative/image/batch_processor.py

from typing import List, Dict
import asyncio
from pathlib import Path

class BatchImageProcessor:
    """批量图片处理器"""

    def __init__(
        self,
        bg_service: BackgroundRemovalService,
        composition_service: ImageCompositionService,
        enhancement_service: ImageEnhancementService
    ):
        self.bg_service = bg_service
        self.comp_service = composition_service
        self.enhance_service = enhancement_service

    async def generate_product_images(
        self,
        product_image: UploadFile,
        scenes: List[str] = None,
        enhance: bool = True
    ) -> Dict[str, List[bytes]]:
        """
        生成完整产品图片集

        Args:
            product_image: 产品原图
            scenes: 场景列表
            enhance: 是否增强图片

        Returns:
            {
                "main": [主图],
                "pt": [PT图],
                "gallery": [Gallery图]
            }
        """
        if scenes is None:
            scenes = ["amazon_main", "minimalist_desk", "kitchen_modern"]

        results = {
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
        white_bg = Image.new("RGB", img.size, (255, 255, 255))
        white_bg.paste(img, mask=img.split()[3])

        buffer = io.BytesIO()
        white_bg.save(buffer, format="JPEG", quality=95)
        main_image = buffer.getvalue()

        # 可选增强
        if enhance:
            main_image = await self.enhance_service.enhance_image(main_image)

        results["main"].append(main_image)

        # Step 3: 生成场景图
        for scene in scenes:
            scene_image = await self.comp_service.compose_scene(
                product_image=product_no_bg,
                scene_type=scene
            )

            if scene == "amazon_main":
                results["pt"].append(scene_image)
            else:
                results["gallery"].append(scene_image)

        return results

    async def batch_process_products(
        self,
        products: List[UploadFile],
        scenes: List[str] = None,
        concurrent: int = 2
    ) -> List[Dict]:
        """批量处理多个产品"""
        tasks = [
            self.generate_product_images(product, scenes)
            for product in products
        ]

        # 分批执行
        results = []
        for i in range(0, len(tasks), concurrent):
            batch = tasks[i:i + concurrent]
            batch_results = await asyncio.gather(*batch)
            results.extend(batch_results)

        return results
```

---

## API 设计

### 端点定义

```python
# backend/api/routes/ai_creative.py

from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
from typing import List, Optional

router = APIRouter(prefix="/api/v1/ai/creative", tags=["AI Creative"])

@router.post("/remove-background")
async def remove_background(
    image: UploadFile = File(...),
    alpha_matting: bool = Form(True),
    format: str = Form("png")
):
    """移除图片背景"""
    service = BackgroundRemovalService()
    result = await service.remove_background(image, alpha_matting, format)
    return Response(content=result, media_type=f"image/{format}")

@router.post("/compose-scene")
async def compose_scene(
    product_image: UploadFile = File(...),
    scene_type: str = Form("amazon_main"),
    product_description: str = Form(""),
    steps: int = Form(50)
):
    """场景合成"""
    service = ImageCompositionService()
    result = await service.compose_scene(
        product_image=await product_image.read(),
        scene_type=scene_type,
        product_description=product_description,
        num_inference_steps=steps
    )
    return Response(content=result, media_type="image/png")

@router.post("/enhance")
async def enhance_image(
    image: UploadFile = File(...),
    scale: int = Form(2)
):
    """图片增强"""
    service = ImageEnhancementService()
    result = await service.enhance_image(await image.read(), scale)
    return Response(content=result, media_type="image/png")

@router.post("/generate-product-set")
async def generate_product_set(
    images: List[UploadFile] = File(...),
    scenes: str = Form("amazon_main,minimalist_desk"),
    enhance: bool = Form(True),
    background_tasks: BackgroundTasks = None
):
    """
    生成完整产品图片集

    返回:
    {
        "job_id": "abc123",
        "status": "processing",
        "total_products": 10
    }
    """
    scene_list = scenes.split(",")

    processor = BatchImageProcessor(
        BackgroundRemovalService(),
        ImageCompositionService(),
        ImageEnhancementService()
    )

    # 异步处理
    job_id = str(uuid.uuid4())

    async def process():
        results = await processor.batch_process_products(images, scene_list)
        # 保存结果到 MinIO
        await save_results(job_id, results)

    background_tasks.add_task(process)

    return {
        "job_id": job_id,
        "status": "processing",
        "total_products": len(images)
    }

@router.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """获取处理任务状态"""
    status = await get_job_status(job_id)
    return status
```

---

## 成本优化

### 成本分析

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         成本分析对比                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  方案 A: 本地部署 (RTX 3060)                                            │
│  • 硬件成本: $400 (一次性)                                             │
│  • 电费: $30/月                                                        │
│  • 每张成本: $0.003 (电费摊销)                                         │
│  • 月处理 10,000 张: $30                                              │
│                                                                         │
│  方案 B: Stability AI API                                              │
│  • SDXL 1.0: $0.04/张                                                 │
│  • 月处理 10,000 张: $400                                             │
│                                                                         │
│  方案 C: DALL-E 3 API                                                 │
│  • 1024x1024: $0.04/张                                                │
│  • 月处理 10,000 张: $400                                             │
│                                                                         │
│  方案 D: 外包设计师                                                   │
│  • $50-100/张                                                         │
│  • 月处理 100 张: $5,000-10,000                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

结论: 处理量 > 1000 张/月时，本地部署最经济
```

### GPU 优化建议

```python
# GPU 优化配置
OPTIMIZATION_SETTINGS = {
    # 模型优化
    "enable_xformers": True,  # 减少内存占用
    "enable_cpu_offload": True,  # CPU 卸载
    "use_fp16": True,  # 半精度推理

    # 批处理
    "batch_size": 1,  # 根据 GPU 内存调整
    "max_concurrent": 2,  # 最大并发任务

    # 缓存
    "cache_models": True,  # 模型缓存
    "preload_popular": True,  # 预加载热门模型
}
```

---

**预计工作量**: 3-4 周

| 阶段 | 任务 | 时间 |
|------|------|------|
| Week 1 | 背景移除 + 图片增强 | 5 天 |
| Week 2 | 场景合成 (SDXL 集成) | 5 天 |
| Week 3 | 批量处理 + API 开发 | 5 天 |
| Week 4 | 测试优化 + 文档 | 5 天 |

---

**下一步**: 查看 [API_DESIGN.md](../03_API_DESIGN.md)
