# 并行爬虫性能优化分析

## 当前性能瓶颈

### 1. 网络IO瓶颈
```
每个任务耗时分解：
├── DNS解析: ~50ms
├── TCP连接: ~100ms
├── TLS握手: ~150ms
├── HTTP请求: ~100ms
├── 服务器处理: ~200ms
├── 内容传输: ~300ms
└── DOM解析: ~200ms
总计: ~1100ms 理论最小值
```

**当前实际: ~4000ms/任务** (有3倍优化空间)

### 2. 等待策略瓶颈
```python
# 当前实现 - 过度等待
page.goto(url, wait_until="domcontentloaded")  # 等待DOM
time.sleep(1.5)  # 固定等待 - 浪费时间！
```

### 3. 资源加载瓶颈
Amazon页面加载大量不需要的资源：
- 高清图片 (每个页面10+张)
- CSS文件 (5+个)
- JavaScript文件 (10+个)
- 跟踪脚本

### 4. 同步API限制
Playwright Sync API 即使在多进程下，每个进程内部仍是串行：
```python
for page in pages:
    page.goto()  # 串行等待
```

---

## 优化方案

### 方案A: 减少等待时间 (简单)

| 优化项 | 当前 | 优化后 | 提升 |
|--------|------|--------|------|
| wait_until | domcontentloaded | commit (更快) | -200ms |
| 固定延迟 | 1.5s | 0.5s | -1000ms |
| 超时时间 | 30s | 15s | N/A |

**预期提升: 1.5x - 2x**

---

### 方案B: 禁用资源加载 (中等)

```python
# 禁用不需要的资源
context.route("**/*.{png,jpg,jpeg,webp,gif}", lambda route: route.abort())
context.route("**/analytics/**", lambda route: route.abort())
context.route("**/tracking/**", lambda route: route.abort())
```

**预期提升: 2x - 3x**

---

### 方案C: 并行发起请求 (高级)

```python
# 同时创建多个页面并导航
pages = [context.new_page() for _ in range(5)]

# 同时发起所有请求（不等待完成）
for page, url in zip(pages, urls):
    page.goto(url, wait_until="commit")  # 立即返回

# 等待所有页面完成
for page in pages:
    page.wait_for_load_state("domcontentloaded")
```

**预期提升: 3x - 5x**

---

### 方案D: 异步API重写 (最佳)

```python
# 使用 async_playwright + asyncio
async def crawl_async():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()

        # 真正的并行
        tasks = [navigate_and_extract(context, url) for url in urls]
        results = await asyncio.gather(*tasks)
```

**预期提升: 5x - 10x**

---

### 方案E: CDP优化 (极限)

使用 Chrome DevTools Protocol 直接控制：
- 禁用图片渲染
- 禁用CSS执行
- 禁用JavaScript执行
- 只获取HTML源码

**预期提升: 10x - 20x**

---

## 推荐实施路线

### 第1步: 快速优化 (1小时)
```
1. 减少 sleep 时间
2. 优化 wait_until 策略
3. 添加缓存机制
```
**目标: 1.5x 提升**

### 第2步: 资源优化 (2小时)
```
1. 禁用图片加载
2. 禁用跟踪脚本
3. 设置请求拦截
```
**目标: 2-3x 提升**

### 第3步: 并行请求 (3小时)
```
1. 同时发起所有请求
2. 批量等待完成
3. 结果聚合处理
```
**目标: 3-5x 提升**

### 第4步: 异步重写 (可选，长期)
```
1. 重写为 async/await
2. 使用 asyncio.gather
3. 信号量控制并发
```
**目标: 5-10x 提升**

---

## 性能对比预测

| 方案 | 当前耗时 | 优化后 | 提升 | 实施难度 |
|------|----------|--------|------|----------|
| 当前 | 4000ms | - | 1x | - |
| 方案A | 4000ms | 2000ms | 2x | ⭐ |
| 方案B | 4000ms | 1500ms | 2.7x | ⭐⭐ |
| 方案C | 4000ms | 1000ms | 4x | ⭐⭐⭐ |
| 方案D | 4000ms | 500ms | 8x | ⭐⭐⭐⭐ |
| 方案E | 4000ms | 250ms | 16x | ⭐⭐⭐⭐⭐ |

---

## 其他优化建议

### 1. 连接复用
```python
# 保持浏览器实例，复用TCP连接
browser = p.chromium.launch()
# 处理多个任务
# 最后关闭
```

### 2. DNS预解析
```python
# 预先解析域名
page.goto("https://www.amazon.com")  # 第一次慢
# 后续任务复用连接
```

### 3. 请求批处理
```python
# 批量处理相似请求
batch_urls = urls[i:i+10]
# 同时处理一批
```

### 4. 智能重试
```python
# 失败任务智能重试
# 区分临时失败和永久失败
```

### 5. 结果缓存
```python
# 缓存已访问的URL
# 避免重复请求
```

---

## 监控指标

需要监控的指标：
- 每个任务的实际耗时
- 网络等待时间占比
- DOM解析时间占比
- 内存使用情况
- CPU使用情况
- 成功率/失败率

---

## 建议从哪个方案开始？

**推荐: 方案A + 方案B 组合**
- 实施简单（2-3小时）
- 预期提升 2-3x
- 风险低
- 不需要大规模重构
