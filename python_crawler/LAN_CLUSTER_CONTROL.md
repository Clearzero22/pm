# 局域网集群控制系统技术文档

> **构建企业级分布式爬虫集群，统一调度管理多台主机**
>
> ⚠️ **重要声明**: 本文档仅供合法的企业内部使用。请确保你的操作符合公司政策和当地法律法规，仅对你有管理权限的设备进行控制。

---

## 目录

1. [系统概述](#1-系统概述)
2. [架构设计](#2-架构设计)
3. [技术选型](#3-技术选型)
4. [核心模块实现](#4-核心模块实现)
5. [部署与配置](#5-部署与配置)
6. [安全与权限](#6-安全与权限)
7. [监控与运维](#7-监控与运维)

---

## 1. 系统概述

### 1.1 应用场景

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        企业爬虫集群应用场景                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  场景一：大规模数据采集                                                     │
│  ├── 问题：单机爬虫速度慢、效率低                                           │
│  ├── 方案：10-100 台主机并行爬取                                             │
│  └── 效果：采集速度提升 10-100 倍                                             │
│                                                                             │
│  场景二：多账号管理                                                         │
│  ├── 问题：单 IP 多账号登录易被封                                            │
│  ├── 方案：每台主机独立 IP 和账号                                             │
│  └── 效果：降低封号风险                                                      │
│                                                                             │
│  场景三：7x24 小时不间断运行                                                 │
│  ├── 问题：单机故障导致任务中断                                             │
│  ├── 方案：任务分布式执行、故障自动转移                                     │
│  └── 效果：系统可用性 99.9%+                                                 │
│                                                                             │
│  场景四：资源优化                                                           │
│  ├── 问题：办公电脑闲置浪费                                                 │
│  ├── 方案：利用闲置计算资源执行爬虫任务                                     │
│  └── 效果：降低服务器成本                                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 系统目标

| 目标 | 指标 | 说明 |
|------|------|------|
| **集中管理** | 统一管理 100+ 节点 | 单控制台管理所有主机 |
| **任务调度** | 支持 1000+ 并发任务 | 智能分配任务到各节点 |
| **高可用** | 99.9% 可用性 | 节点故障自动转移 |
| **易扩展** | 分钟级扩容 | 新节点快速加入集群 |
| **可观测** | 实时监控 | 任务状态、资源使用可视化 |

### 1.3 网络拓扑

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        局域网集群网络拓扑                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                          ┌─────────────────┐                               │
│                          │   控制节点       │                               │
│                          │  (Master Node)  │                               │
│                          │  192.168.1.100  │                               │
│                          └────────┬────────┘                               │
│                                   │                                        │
│              ┌────────────────────┼────────────────────┐                  │
│              │                    │                    │                   │
│              ▼                    ▼                    ▼                   │
│     ┌───────────────┐    ┌───────────────┐    ┌───────────────┐          │
│     │  工作节点 1    │    │  工作节点 2    │    │  工作节点 N    │          │
│     │  Worker-01    │    │  Worker-02    │    │  Worker-N     │          │
│     │ 192.168.1.101 │    │ 192.168.1.102 │    │ 192.168.1.10N │          │
│     └───────────────┘    └───────────────┘    └───────────────┘          │
│                                                                             │
│  通信协议：HTTP/gRPC/WebSocket                                              │
│  网络要求：局域网内互通                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 架构设计

### 2.1 系统架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           集群系统架构                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      控制平面 (Control Plane)                        │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │  API 网关     │  │  任务调度器   │  │  节点管理    │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │  监控中心    │  │  日志聚合    │  │  配置管理    │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                      │
│  ┌───────────────────────────────────┼───────────────────────────────────┐ │
│  │                      数据层 (Data Layer)                               │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │ │
│  │  │  Redis       │  │  PostgreSQL  │  │  RabbitMQ    │                │ │
│  │  │  (缓存/锁)   │  │  (任务存储)  │  │  (消息队列)  │                │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                      │                                      │
│  ┌───────────────────────────────────┼───────────────────────────────────┐ │
│  │                      执行层 (Execution Layer)                          │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │ │
│  │  │ Worker 1 │  │ Worker 2 │  │ Worker 3 │  │ Worker N │             │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘             │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 节点角色定义

| 角色 | 职责 | 部署数量 |
|------|------|----------|
| **Master** | 任务调度、节点管理、API 服务 | 1（可主备） |
| **Worker** | 执行爬虫任务、上报状态 | N（弹性伸缩） |
| **Redis** | 分布式缓存、锁、消息队列 | 1-3（集群） |
| **Database** | 任务存储、结果存储 | 1（可主从） |

### 2.3 通信协议

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           节点通信协议                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Master → Worker (任务下发)                                                 │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ POST /api/v1/tasks/assign                                            │  │
│  │ Content-Type: application/json                                       │  │
│  │                                                                      │  │
│  │ {                                                                    │  │
│  │   "task_id": "task_001",                                             │  │
│  │   "task_type": "crawler",                                            │  │
│  │   "payload": {                                                       │  │
│  │     "url": "https://example.com",                                    │  │
│  │     "params": {...}                                                  │  │
│  │   },                                                                 │  │
│  │   "timeout": 300,                                                    │  │
│  │   "priority": 1                                                      │  │
│  │ }                                                                    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  Worker → Master (状态上报)                                                 │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ POST /api/v1/tasks/report                                            │  │
│  │ Content-Type: application/json                                       │  │
│  │                                                                      │  │
│  │ {                                                                    │  │
│  │   "task_id": "task_001",                                             │  │
│  │   "worker_id": "worker_001",                                         │  │
│  │   "status": "running",  // pending/running/completed/failed          │  │
│  │   "progress": 50,                                                    │  │
│  │   "result": {...},                                                   │  │
│  │   "error": null                                                      │  │
│  │ }                                                                    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  Worker → Master (心跳)                                                     │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ POST /api/v1/heartbeat                                               │  │
│  │ Content-Type: application/json                                       │  │
│  │                                                                      │  │
│  │ {                                                                    │  │
│  │   "worker_id": "worker_001",                                         │  │
│  │   "timestamp": 1705305600,                                           │  │
│  │   "resources": {                                                     │  │
│  │     "cpu": 45.2,                                                     │  │
│  │     "memory": 67.8,                                                  │  │
│  │     "disk": 34.5                                                     │  │
│  │   },                                                                 │  │
│  │   "active_tasks": 3                                                  │  │
│  │ }                                                                    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 技术选型

### 3.1 方案对比

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        集群方案对比                                          │
├──────────────────┬──────────────────┬──────────────────┬────────────────────┤
│       特性        │   Celery +      │   Ray             │   自研轻量级       │
│                  │   Redis         │                   │   框架             │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ 成熟度           │ ⭐⭐⭐⭐⭐          │ ⭐⭐⭐⭐⭐          │ ⭐⭐⭐              │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ 学习曲线         │ 中等             │ 陡峭             │ 低                │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ 灵活性           │ 高               │ 中               │ 最高              │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ 资源占用         │ 中等             │ 较高             │ 低                │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ 适合场景         │ 通用任务队列     │ AI/计算密集型     │ 爬虫专用          │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ 推荐指数         │ ⭐⭐⭐⭐           │ ⭐⭐⭐            │ ⭐⭐⭐⭐⭐          │
└──────────────────┴──────────────────┴──────────────────┴────────────────────┘
```

### 3.2 推荐技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| **控制节点** | Python + FastAPI | 高性能 API 服务 |
| **工作节点** | Python + aiohttp | 轻量级客户端 |
| **消息队列** | Redis Streams | 任务队列、发布订阅 |
| **数据存储** | PostgreSQL | 任务和结果存储 |
| **缓存** | Redis | 分布式锁、缓存 |
| **前端监控** | Vue3 + ECharts | 可视化 Dashboard |
| **部署** | Docker + Docker Compose | 容器化部署 |

---

## 4. 核心模块实现

### 4.1 Master 节点实现

```python
# master/app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import redis.asyncio as redis
from datetime import datetime
import uuid

app = FastAPI(title="爬虫集群控制中心")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis 连接
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

# 内存存储（生产环境用数据库）
workers: Dict[str, Dict[str, Any]] = {}
tasks: Dict[str, Dict[str, Any]] = {}


class TaskCreate(BaseModel):
    """任务创建请求"""
    task_type: str
    payload: Dict[str, Any]
    priority: int = 1
    timeout: int = 300


class TaskReport(BaseModel):
    """任务状态上报"""
    task_id: str
    worker_id: str
    status: str  # pending/running/completed/failed
    progress: int = 0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class Heartbeat(BaseModel):
    """心跳请求"""
    worker_id: str
    resources: Dict[str, float]
    active_tasks: int = 0


@app.post("/api/v1/tasks")
async def create_task(task: TaskCreate):
    """创建任务"""
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    
    task_data = {
        "task_id": task_id,
        "task_type": task.task_type,
        "payload": task.payload,
        "priority": task.priority,
        "timeout": task.timeout,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "worker_id": None,
        "result": None,
        "error": None,
    }
    
    tasks[task_id] = task_data
    
    # 推送到任务队列
    await redis_client.xadd(
        "task_queue",
        {"task_id": task_id, "priority": str(task.priority)},
        maxlen=10000
    )
    
    return {"task_id": task_id, "status": "created"}


@app.get("/api/v1/tasks")
async def list_tasks(status: Optional[str] = None):
    """获取任务列表"""
    result = []
    for task_id, task in tasks.items():
        if status is None or task["status"] == status:
            result.append(task)
    return sorted(result, key=lambda x: x["created_at"], reverse=True)


@app.get("/api/v1/tasks/{task_id}")
async def get_task(task_id: str):
    """获取任务详情"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]


@app.post("/api/v1/workers/register")
async def register_worker(worker_id: str):
    """注册工作节点"""
    workers[worker_id] = {
        "worker_id": worker_id,
        "status": "online",
        "registered_at": datetime.now().isoformat(),
        "last_heartbeat": datetime.now().isoformat(),
        "resources": {},
        "active_tasks": 0,
    }
    
    return {"status": "registered", "worker_id": worker_id}


@app.post("/api/v1/heartbeat")
async def heartbeat(hb: Heartbeat):
    """接收心跳"""
    if hb.worker_id not in workers:
        # 自动注册
        await register_worker(hb.worker_id)
    
    workers[hb.worker_id].update({
        "last_heartbeat": datetime.now().isoformat(),
        "status": "online",
        "resources": hb.resources,
        "active_tasks": hb.active_tasks,
    })
    
    return {"status": "ok"}


@app.post("/api/v1/tasks/assign")
async def assign_task(worker_id: str):
    """工作节点领取任务"""
    # 从队列获取任务
    task = await redis_client.xread({"task_queue": "0-0"}, count=1)
    
    if not task:
        return {"status": "no_task"}
    
    task_id = task[0][1][0][1]["task_id"]
    
    if task_id in tasks:
        tasks[task_id]["status"] = "running"
        tasks[task_id]["worker_id"] = worker_id
        
        # 更新工作节点任务数
        workers[worker_id]["active_tasks"] += 1
        
        return {
            "status": "assigned",
            "task": tasks[task_id]
        }
    
    return {"status": "no_task"}


@app.post("/api/v1/tasks/report")
async def report_task(report: TaskReport):
    """接收任务状态报告"""
    if report.task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    tasks[report.task_id].update({
        "status": report.status,
        "progress": report.progress,
        "result": report.result,
        "error": report.error,
        "completed_at": datetime.now().isoformat() if report.status in ["completed", "failed"] else None,
    })
    
    # 更新工作节点任务数
    if report.status in ["completed", "failed"]:
        workers[report.worker_id]["active_tasks"] -= 1
    
    return {"status": "ok"}


@app.get("/api/v1/workers")
async def list_workers():
    """获取工作节点列表"""
    # 检查离线节点（5 分钟无心跳）
    now = datetime.now()
    for worker_id, worker in workers.items():
        last_hb = datetime.fromisoformat(worker["last_heartbeat"])
        if (now - last_hb).total_seconds() > 300:
            worker["status"] = "offline"
    
    return list(workers.values())


@app.get("/api/v1/stats")
async def get_stats():
    """获取集群统计"""
    online_workers = sum(1 for w in workers.values() if w["status"] == "online")
    
    return {
        "total_workers": len(workers),
        "online_workers": online_workers,
        "offline_workers": len(workers) - online_workers,
        "total_tasks": len(tasks),
        "pending_tasks": sum(1 for t in tasks.values() if t["status"] == "pending"),
        "running_tasks": sum(1 for t in tasks.values() if t["status"] == "running"),
        "completed_tasks": sum(1 for t in tasks.values() if t["status"] == "completed"),
        "failed_tasks": sum(1 for t in tasks.values() if t["status"] == "failed"),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 4.2 Worker 节点实现

```python
# worker/worker.py
import asyncio
import aiohttp
import psutil
import platform
import uuid
from typing import Optional, Dict, Any
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkerNode:
    """
    工作节点
    
    功能:
    - 自动注册到 Master
    - 定期心跳上报
    - 领取并执行任务
    - 上报任务状态
    """
    
    def __init__(
        self,
        master_url: str = "http://localhost:8000",
        worker_id: Optional[str] = None,
        max_concurrent_tasks: int = 3,
    ):
        self.master_url = master_url.rstrip("/")
        self.worker_id = worker_id or f"worker_{uuid.uuid4().hex[:8]}"
        self.max_concurrent_tasks = max_concurrent_tasks
        self.active_tasks = 0
        self.running = False
        
        # 生成唯一 ID（基于 MAC 地址）
        mac = uuid.getnode()
        self.worker_id = f"worker_{mac:012x}"
        
        logger.info(f"Worker 初始化完成：{self.worker_id}")
    
    async def register(self) -> bool:
        """注册到 Master"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.master_url}/api/v1/workers/register",
                    params={"worker_id": self.worker_id}
                ) as resp:
                    if resp.status == 200:
                        logger.info(f"注册成功：{self.worker_id}")
                        return True
                    else:
                        logger.error(f"注册失败：{resp.status}")
                        return False
        except Exception as e:
            logger.error(f"注册异常：{e}")
            return False
    
    async def send_heartbeat(self):
        """发送心跳"""
        try:
            # 收集资源信息
            resources = {
                "cpu": psutil.cpu_percent(interval=1),
                "memory": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage("/").percent,
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.master_url}/api/v1/heartbeat",
                    json={
                        "worker_id": self.worker_id,
                        "resources": resources,
                        "active_tasks": self.active_tasks,
                    }
                ) as resp:
                    if resp.status != 200:
                        logger.warning(f"心跳失败：{resp.status}")
        except Exception as e:
            logger.error(f"心跳异常：{e}")
    
    async def fetch_task(self) -> Optional[Dict[str, Any]]:
        """领取任务"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.master_url}/api/v1/tasks/assign",
                    params={"worker_id": self.worker_id}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data["status"] == "assigned":
                            logger.info(f"领取到任务：{data['task']['task_id']}")
                            return data["task"]
        except Exception as e:
            logger.error(f"领取任务异常：{e}")
        
        return None
    
    async def report_task(
        self,
        task_id: str,
        status: str,
        progress: int = 0,
        result: Optional[Dict] = None,
        error: Optional[str] = None,
    ):
        """上报任务状态"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.master_url}/api/v1/tasks/report",
                    json={
                        "task_id": task_id,
                        "worker_id": self.worker_id,
                        "status": status,
                        "progress": progress,
                        "result": result,
                        "error": error,
                    }
                ) as resp:
                    if resp.status != 200:
                        logger.warning(f"任务上报失败：{resp.status}")
        except Exception as e:
            logger.error(f"任务上报异常：{e}")
    
    async def execute_task(self, task: Dict[str, Any]):
        """执行任务"""
        task_id = task["task_id"]
        task_type = task["task_type"]
        payload = task["payload"]
        
        try:
            self.active_tasks += 1
            
            # 上报开始
            await self.report_task(task_id, "running", progress=0)
            
            # 根据任务类型执行
            if task_type == "crawler":
                result = await self._run_crawler(payload)
            elif task_type == "data_process":
                result = await self._run_processor(payload)
            else:
                raise ValueError(f"未知任务类型：{task_type}")
            
            # 上报完成
            await self.report_task(task_id, "completed", progress=100, result=result)
            logger.info(f"任务完成：{task_id}")
            
        except Exception as e:
            logger.error(f"任务失败：{task_id}, 错误：{e}")
            await self.report_task(task_id, "failed", error=str(e))
        
        finally:
            self.active_tasks -= 1
    
    async def _run_crawler(self, payload: Dict[str, Any]) -> Dict:
        """执行爬虫任务"""
        from playwright.async_api import async_playwright
        
        url = payload.get("url")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            await page.goto(url, wait_until="domcontentloaded")
            
            # 提取数据
            title = await page.title()
            html = await page.content()
            
            await browser.close()
            
            return {
                "title": title,
                "url": url,
                "html_length": len(html),
            }
    
    async def _run_processor(self, payload: Dict[str, Any]) -> Dict:
        """执行数据处理任务"""
        # 模拟处理
        await asyncio.sleep(1)
        
        return {
            "processed": True,
            "data": payload.get("data"),
        }
    
    async def run(self):
        """启动 Worker"""
        self.running = True
        
        logger.info("Worker 启动中...")
        
        # 注册
        if not await self.register():
            logger.error("注册失败，退出")
            return
        
        # 启动后台任务
        asyncio.create_task(self._heartbeat_loop())
        asyncio.create_task(self._task_loop())
        
        logger.info("Worker 已启动，等待任务...")
        
        # 保持运行
        while self.running:
            await asyncio.sleep(1)
    
    async def _heartbeat_loop(self):
        """心跳循环"""
        while self.running:
            await self.send_heartbeat()
            await asyncio.sleep(30)  # 30 秒心跳
    
    async def _task_loop(self):
        """任务领取循环"""
        while self.running:
            # 检查并发限制
            if self.active_tasks >= self.max_concurrent_tasks:
                await asyncio.sleep(5)
                continue
            
            # 领取任务
            task = await self.fetch_task()
            
            if task:
                # 执行任务
                asyncio.create_task(self.execute_task(task))
            else:
                await asyncio.sleep(5)  # 无任务，等待
    
    async def stop(self):
        """停止 Worker"""
        self.running = False
        logger.info("Worker 停止中...")


async def main():
    # 从环境变量读取配置
    import os
    
    master_url = os.getenv("MASTER_URL", "http://localhost:8000")
    
    worker = WorkerNode(
        master_url=master_url,
        max_concurrent_tasks=3,
    )
    
    try:
        await worker.run()
    except KeyboardInterrupt:
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
```

### 4.3 Worker 批量部署脚本

```python
# scripts/deploy_workers.py
#!/usr/bin/env python3
"""
批量部署 Worker 节点

通过 SSH 在多台主机上部署 Worker
"""

import asyncio
import asyncssh
from pathlib import Path
from typing import List
import yaml


class WorkerDeployer:
    """Worker 部署器"""
    
    def __init__(self, config_file: str = "hosts.yaml"):
        with open(config_file, "r") as f:
            self.config = yaml.safe_load(f)
        
        self.master_url = self.config.get("master_url")
        self.hosts = self.config.get("hosts", [])
    
    async def deploy_to_host(
        self,
        host: str,
        username: str,
        password: str = None,
        ssh_key: str = None,
    ):
        """在单台主机上部署"""
        try:
            # SSH 连接
            if ssh_key:
                conn = await asyncssh.connect(
                    host,
                    username=username,
                    client_keys=[ssh_key]
                )
            else:
                conn = await asyncssh.connect(
                    host,
                    username=username,
                    password=password
                )
            
            print(f"[{host}] 已连接")
            
            # 创建目录
            await conn.run("mkdir -p ~/crawler_worker")
            
            # 传输文件
            await asyncssh.scp("worker/worker.py", (conn, "~/crawler_worker/"))
            await asyncssh.scp("requirements.txt", (conn, "~/crawler_worker/"))
            
            # 安装依赖
            await conn.run(
                "cd ~/crawler_worker && pip install -r requirements.txt"
            )
            
            # 创建 systemd 服务
            service_content = f"""[Unit]
Description=Crawler Worker
After=network.target

[Service]
Type=simple
User={username}
WorkingDirectory=/home/{username}/crawler_worker
Environment=MASTER_URL={self.master_url}
ExecStart=/usr/bin/python3 worker.py
Restart=always

[Install]
WantedBy=multi-user.target
"""
            
            # 写入服务文件
            await conn.run(f"echo '{service_content}' | sudo tee /etc/systemd/system/crawler-worker.service")
            
            # 启用服务
            await conn.run("sudo systemctl daemon-reload")
            await conn.run("sudo systemctl enable crawler-worker")
            await conn.run("sudo systemctl start crawler-worker")
            
            print(f"[{host}] 部署完成")
            
            conn.close()
            
        except Exception as e:
            print(f"[{host}] 部署失败：{e}")
    
    async def deploy_all(self):
        """批量部署所有主机"""
        tasks = []
        
        for host_config in self.hosts:
            task = self.deploy_to_host(
                host=host_config["host"],
                username=host_config["username"],
                password=host_config.get("password"),
                ssh_key=host_config.get("ssh_key"),
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    deployer = WorkerDeployer()
    asyncio.run(deployer.deploy_all())
```

### 4.4 监控 Dashboard

```python
# dashboard/app.py
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="爬虫集群监控",
    page_icon="🕷️",
    layout="wide"
)

MASTER_URL = "http://localhost:8000"

st.title("🕷️ 爬虫集群监控中心")

# 自动刷新
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True
    st.session_state.last_update = datetime.now()

# 侧边栏
st.sidebar.header("设置")
auto_refresh = st.sidebar.checkbox("自动刷新", value=True)
refresh_interval = st.sidebar.slider("刷新间隔（秒）", 5, 60, 10)

if st.sidebar.button("手动刷新"):
    st.session_state.last_update = datetime.now()

# 获取数据
try:
    stats_resp = requests.get(f"{MASTER_URL}/api/v1/stats", timeout=5)
    workers_resp = requests.get(f"{MASTER_URL}/api/v1/workers", timeout=5)
    tasks_resp = requests.get(f"{MASTER_URL}/api/v1/tasks", timeout=5)
    
    stats = stats_resp.json()
    workers = workers_resp.json()
    tasks = tasks_resp.json()
    
except Exception as e:
    st.error(f"连接 Master 失败：{e}")
    st.stop()

# 统计指标
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("工作节点", f"{stats['online_workers']}/{stats['total_workers']}")

with col2:
    st.metric("运行中任务", stats["running_tasks"])

with col3:
    st.metric("待处理任务", stats["pending_tasks"])

with col4:
    st.metric("今日完成", stats["completed_tasks"])

# 工作节点状态
st.subheader("工作节点状态")

if workers:
    df = pd.DataFrame(workers)
    
    # 状态分布
    status_count = df["status"].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            values=status_count.values,
            names=status_count.index,
            title="节点状态分布"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 资源使用
        df["cpu"] = df["resources"].apply(lambda x: x.get("cpu", 0) if x else 0)
        df["memory"] = df["resources"].apply(lambda x: x.get("memory", 0) if x else 0)
        
        fig = px.bar(
            df,
            x="worker_id",
            y=["cpu", "memory"],
            title="资源使用率",
            barmode="group"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 详细列表
    st.dataframe(
        df[["worker_id", "status", "active_tasks", "last_heartbeat"]],
        use_container_width=True
    )
else:
    st.info("暂无工作节点")

# 任务列表
st.subheader("最近任务")

if tasks:
    task_df = pd.DataFrame(tasks[:20])
    
    # 状态颜色
    status_colors = {
        "pending": "🟡",
        "running": "🔵",
        "completed": "🟢",
        "failed": "🔴"
    }
    
    task_df["status"] = task_df["status"].apply(
        lambda x: f"{status_colors.get(x, '⚪')} {x}"
    )
    
    st.dataframe(
        task_df[["task_id", "task_type", "status", "worker_id", "created_at"]],
        use_container_width=True
    )

# 自动刷新逻辑
if auto_refresh:
    import time
    time.sleep(refresh_interval)
    st.rerun()
```

---

## 5. 部署与配置

### 5.1 Docker Compose 部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: crawler
      POSTGRES_USER: crawler
      POSTGRES_PASSWORD: ${DB_PASSWORD:-crawler123}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Master 节点
  master:
    build:
      context: .
      dockerfile: Dockerfile.master
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://crawler:crawler123@postgres:5432/crawler
    depends_on:
      - redis
      - postgres
    volumes:
      - ./master:/app
      - ./logs:/app/logs

  # Dashboard
  dashboard:
    build:
      context: ./dashboard
    ports:
      - "8501:8501"
    environment:
      - MASTER_URL=http://master:8000
    depends_on:
      - master

  # Worker（示例 3 个，可复制多个）
  worker-1:
    build:
      context: .
      dockerfile: Dockerfile.worker
    environment:
      - MASTER_URL=http://master:8000
      - MAX_CONCURRENT_TASKS=3
    depends_on:
      - master
    volumes:
      - ./worker:/app

  worker-2:
    build:
      context: .
      dockerfile: Dockerfile.worker
    environment:
      - MASTER_URL=http://master:8000
      - MAX_CONCURRENT_TASKS=3
    depends_on:
      - master

  worker-3:
    build:
      context: .
      dockerfile: Dockerfile.worker
    environment:
      - MASTER_URL=http://master:8000
      - MAX_CONCURRENT_TASKS=3
    depends_on:
      - master

volumes:
  redis_data:
  postgres_data:
```

### 5.2 主机配置文件

```yaml
# hosts.yaml
# 集群主机配置

master_url: "http://192.168.1.100:8000"

hosts:
  - host: "192.168.1.101"
    username: "crawler"
    ssh_key: "~/.ssh/id_rsa"
    label: "办公区 -01"

  - host: "192.168.1.102"
    username: "crawler"
    ssh_key: "~/.ssh/id_rsa"
    label: "办公区 -02"

  - host: "192.168.1.103"
    username: "crawler"
    ssh_key: "~/.ssh/id_rsa"
    label: "办公区 -03"

  - host: "192.168.1.104"
    username: "crawler"
    ssh_key: "~/.ssh/id_rsa"
    label: "办公区 -04"

  - host: "192.168.1.105"
    username: "crawler"
    password: "your_password"
    label: "测试区 -01"
```

### 5.3 快速启动

```bash
# 1. 启动 Master 和基础设施
docker-compose up -d redis postgres master dashboard

# 2. 查看日志
docker-compose logs -f master

# 3. 访问 Dashboard
# http://localhost:8501

# 4. 启动 Worker（本地测试）
python worker/worker.py

# 5. 批量部署到局域网主机
python scripts/deploy_workers.py

# 6. 查看集群状态
curl http://localhost:8000/api/v1/stats
```

---

## 6. 安全与权限

### 6.1 认证配置

```python
# master/auth.py
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from typing import Optional

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# 从环境变量读取 API Keys
VALID_API_KEYS = set(os.getenv("VALID_API_KEYS", "").split(","))


async def verify_api_key(api_key: Optional[str] = Security(API_KEY_HEADER)):
    """验证 API Key"""
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API Key")
    
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    return api_key
```

### 6.2 网络隔离

```yaml
# docker-compose.yml (网络配置)
networks:
  crawler_net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

services:
  master:
    networks:
      crawler_net:
        ipv4_address: 172.20.0.10
  
  worker:
    networks:
      crawler_net:
        ipv4_address: 172.20.0.100
```

---

## 7. 监控与运维

### 7.1 Prometheus 监控

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'master'
    static_configs:
      - targets: ['master:8000']
    metrics_path: '/metrics'

  - job_name: 'workers'
    static_configs:
      - targets: ['worker-1:8000', 'worker-2:8000', 'worker-3:8000']
```

### 7.2 告警规则

```yaml
# alerts.yml
groups:
  - name: crawler_alerts
    rules:
      - alert: WorkerOffline
        expr: worker_status == 0
        for: 5m
        annotations:
          summary: "Worker 离线"

      - alert: TaskQueueBacklog
        expr: task_queue_size > 1000
        for: 15m
        annotations:
          summary: "任务队列积压"
```

---

## 附录

### A. 依赖文件

```txt
# requirements.txt
# Master
fastapi==0.109.0
uvicorn==0.27.0
redis==5.0.1
psycopg2-binary==2.9.9

# Worker
aiohttp==3.9.1
playwright==1.40.0
psutil==5.9.7

# 通用
pydantic==2.5.3
python-dotenv==1.0.0
```

### B. 故障排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| Worker 无法连接 Master | 网络不通、防火墙 | 检查网络、关闭防火墙 |
| 任务长时间 pending | 无可用 Worker | 增加 Worker 节点 |
| Worker 频繁离线 | 资源不足、网络不稳定 | 检查资源、优化网络 |

---

*文档版本：0.1.0 | 最后更新：2026-03-12*
