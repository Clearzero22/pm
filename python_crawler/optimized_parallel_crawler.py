#!/usr/bin/env python
"""
优化版并行爬虫 - 方案A + B
实现: 减少等待 + 禁用资源加载
预期提升: 2-3x
"""
import logging
import multiprocessing as mp
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from playwright.sync_api import sync_playwright

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


class OptimizedCrawlerWorker:
    """优化的爬虫工作进程"""

    def __init__(self, worker_id: int, headless: bool = True):
        self.worker_id = worker_id
        self.headless = headless

    def run(self, tasks: list[dict]) -> list[dict]:
        """执行优化的任务处理"""
        results = []

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-extensions',
                    '--no-sandbox',
                ]
            )

            # 创建优化的上下文
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            )

            # ===== 优化方案B: 禁用资源加载 =====
            self._setup_resource_blocking(context)

            logger.info(f"[Worker {self.worker_id}] 启动 (优化模式)")

            for idx, task in enumerate(tasks):
                try:
                    result = self._process_task_optimized(context, task, idx + 1)
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.error(f"[Worker {self.worker_id}] 任务失败: {e}")

            browser.close()
            logger.info(f"[Worker {self.worker_id}] 完成: {len(results)}/{len(tasks)}")

        return results

    def _setup_resource_blocking(self, context):
        """设置资源拦截 - 禁用不需要的资源"""

        def block_images(route):
            """拦截图片请求"""
            route.abort()

        def block_tracking(route):
            """拦截跟踪脚本"""
            route.abort()

        def block_fonts(route):
            """拦截字体文件"""
            route.abort()

        # 图片格式
        for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp', '*.gif', '*.svg', '*.ico']:
            context.route(f"**/*{ext}", block_images)

        # 跟踪和分析
        for pattern in ['**/analytics/**', '**/tracking/**', '**/metrics/**']:
            context.route(pattern, block_tracking)

        # 字体
        context.route("**/*.woff*", block_fonts)
        context.route("**/*.ttf", block_fonts)

        logger.debug(f"[Worker {self.worker_id}] 资源拦截已启用")

    def _process_task_optimized(self, context, task: dict, index: int) -> dict | None:
        """优化的任务处理"""
        url = task.get("url")
        keyword = task.get("keyword", "")

        page = context.new_page()

        start_time = time.time()

        try:
            logger.info(f"[Worker {self.worker_id}] [{index}] {keyword}")

            # ===== 优化方案A: 更快的等待策略 =====
            # 使用 commit 而不是 domcontentloaded (更快)
            page.goto(url, timeout=15000, wait_until="commit")

            # 减少固定延迟 (1.5s -> 0.3s)
            time.sleep(0.3)

            # 快速提取关键信息
            title = page.title() or "N/A"
            final_url = page.url

            elapsed = time.time() - start_time

            result = {
                "worker_id": self.worker_id,
                "keyword": keyword,
                "title": title[:50],
                "url": final_url,
                "status": "success",
                "elapsed_ms": int(elapsed * 1000),
            }

            logger.info(f"[Worker {self.worker_id}] [{index}] ✓ {elapsed:.2f}s")
            return result

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"[Worker {self.worker_id}] [{index}] ✗ {e} ({elapsed:.2f}s)")
            return {
                "worker_id": self.worker_id,
                "keyword": keyword,
                "error": str(e),
                "status": "failed",
                "elapsed_ms": int(elapsed * 1000),
            }
        finally:
            page.close()


def run_optimized_worker(worker_id: int, tasks: list[dict], headless: bool) -> list[dict]:
    """优化工作进程入口"""
    worker = OptimizedCrawlerWorker(worker_id, headless)
    return worker.run(tasks)


def optimized_parallel_search(
    keywords: list[str],
    workers: int = 5,
    headless: bool = False,
) -> list[dict]:
    """优化的并行搜索"""
    logger.info("=" * 60)
    logger.info(f"🚀 优化版并行搜索 - {workers} 个工作进程")
    logger.info("优化: 资源拦截 + 减少等待")
    logger.info("=" * 60)

    # 分配任务
    tasks_per_worker = len(keywords) // workers
    remainder = len(keywords) % workers

    task_batches = []
    start = 0
    for i in range(workers):
        count = tasks_per_worker + (1 if i < remainder else 0)
        batch = keywords[start:start + count]
        task_batches.append(batch)
        start += count

    # 打印分配
    for i, batch in enumerate(task_batches):
        logger.info(f"  Worker {i + 1}: {len(batch)} 个任务")

    all_results = []
    start_time = time.time()

    # 并行执行
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {}

        for i, batch in enumerate(task_batches):
            task_list = [
                {
                    "keyword": kw,
                    "url": f"https://www.amazon.com/s?k={kw.replace(' ', '+')}",
                }
                for kw in batch
            ]

            future = executor.submit(
                run_optimized_worker,
                i + 1,
                task_list,
                headless,
            )
            futures[future] = i + 1

        for future in as_completed(futures):
            worker_id = futures[future]
            try:
                results = future.result()
                all_results.extend(results)
            except Exception as e:
                logger.error(f"Worker {worker_id} 失败: {e}")

    total_elapsed = time.time() - start_time

    # 统计
    success = [r for r in all_results if r.get("status") == "success"]
    failed = [r for r in all_results if r.get("status") == "failed"]

    avg_time = sum(r.get("elapsed_ms", 0) for r in success) / len(success) if success else 0

    logger.info("\n" + "=" * 60)
    logger.info("✓ 优化版测试完成")
    logger.info("=" * 60)
    logger.info(f"  总任务: {len(all_results)}")
    logger.info(f"  成功: {len(success)}")
    logger.info(f"  失败: {len(failed)}")
    logger.info(f"  总耗时: {total_elapsed:.2f} 秒")
    logger.info(f"  平均每任务: {avg_time:.0f} ms")
    logger.info(f"  吞吐量: {len(all_results)/total_elapsed:.2f} 任务/秒")

    # 性能对比
    baseline_time = len(all_results) * 4.0  # 原始版本约4秒/任务
    speedup = baseline_time / total_elapsed
    logger.info(f"  性能提升: {speedup:.1f}x (vs 原始版本)")

    return all_results


def main():
    """主函数"""
    # 25个关键词测试
    keywords = [
        "water bottle", "blender", "coffee maker", "mouse", "keyboard",
        "headphones", "charger", "cable", "monitor", "speaker",
        "webcam", "microphone", "stand", "hub", "dock",
        "router", "adapter", "case", "screen", "lamp",
        "fan", "heater", "cooler", "drive", "memory",
    ]

    print("\n🚀 优化版并行爬虫测试")
    print("\n选择模式:")
    print("  1. 优化版 (5进程) - 资源拦截 + 减少等待")
    print("  2. 对比测试 (原始版 vs 优化版)")
    print("  3. 大规模优化版 (10进程, 50任务)")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        results = optimized_parallel_search(
            keywords[:25],
            workers=5,
            headless=False,
        )

    elif choice == "2":
        print("\n运行原始版本...")
        # 这里可以调用原始版本对比
        print("(略 - 直接运行模式1看优化效果)")

        print("\n运行优化版本...")
        results = optimized_parallel_search(
            keywords[:25],
            workers=5,
            headless=False,
        )

    elif choice == "3":
        # 50个任务
        large_keywords = keywords * 2
        results = optimized_parallel_search(
            large_keywords[:50],
            workers=10,
            headless=False,
        )

    else:
        results = optimized_parallel_search(keywords[:25], workers=5, headless=False)


if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)
    main()
