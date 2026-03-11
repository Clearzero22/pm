#!/usr/bin/env python
"""
并行爬虫 - 多进程、多窗口、多标签页
使用 multiprocessing 实现真正的并行执行
"""
import logging
import multiprocessing as mp
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from playwright.sync_api import sync_playwright

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


class ParallelCrawlerWorker:
    """并行爬虫工作进程"""

    def __init__(self, worker_id: int, headless: bool = True):
        self.worker_id = worker_id
        self.headless = headless

    def run(self, tasks: list[dict]) -> list[dict]:
        """执行分配的任务列表

        Args:
            tasks: 任务列表，每个任务包含 url, keyword 等信息

        Returns:
            结果列表
        """
        results = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context()

            logger.info(f"[Worker {self.worker_id}] 启动，分配 {len(tasks)} 个任务")

            for idx, task in enumerate(tasks):
                try:
                    result = self._process_task(context, task, idx + 1)
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.error(f"[Worker {self.worker_id}] 任务失败: {e}")

            browser.close()
            logger.info(f"[Worker {self.worker_id}] 完成，成功 {len(results)}/{len(tasks)}")

        return results

    def _process_task(self, context, task: dict, index: int) -> dict | None:
        """处理单个任务

        Args:
            context: Browser context
            task: 任务字典
            index: 任务索引

        Returns:
            结果字典
        """
        url = task.get("url")
        keyword = task.get("keyword", "")

        page = context.new_page()

        try:
            logger.info(f"[Worker {self.worker_id}] [{index}] 正在加载: {keyword or url}")

            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(2)  # 等待页面稳定

            # 提取页面标题作为简单验证
            title = page.title() or "N/A"

            # 获取页面URL（可能被重定向）
            final_url = page.url

            result = {
                "worker_id": self.worker_id,
                "task_index": index,
                "keyword": keyword,
                "url": url,
                "final_url": final_url,
                "title": title,
                "status": "success",
            }

            logger.info(f"[Worker {self.worker_id}] [{index}] ✓ {title[:50]}")
            return result

        except Exception as e:
            logger.error(f"[Worker {self.worker_id}] [{index}] ✗ {e}")
            return {
                "worker_id": self.worker_id,
                "task_index": index,
                "keyword": keyword,
                "url": url,
                "error": str(e),
                "status": "failed",
            }
        finally:
            page.close()


def parallel_search(
    keywords: list[str],
    workers: int = 3,
    headless: bool = True,
) -> list[dict]:
    """并行搜索多个关键词

    Args:
        keywords: 关键词列表
        workers: 工作进程数
        headless: 是否无头模式

    Returns:
        所有结果列表
    """
    logger.info("=" * 60)
    logger.info(f"并行搜索爬虫 - {workers} 个工作进程")
    logger.info("=" * 60)

    # 分配任务给各个工作进程
    tasks_per_worker = len(keywords) // workers
    remainder = len(keywords) % workers

    task_batches = []
    start = 0
    for i in range(workers):
        # 前面的进程多分配一个任务（处理余数）
        count = tasks_per_worker + (1 if i < remainder else 0)
        batch = keywords[start:start + count]
        task_batches.append(batch)
        start += count

    # 打印任务分配
    for i, batch in enumerate(task_batches):
        logger.info(f"  Worker {i + 1}: {len(batch)} 个任务")

    # 使用进程池执行
    all_results = []

    with ProcessPoolExecutor(max_workers=workers) as executor:
        # 提交所有任务
        futures = {}
        for i, batch in enumerate(task_batches):
            # 将任务转换为 URL 列表
            task_list = [
                {
                    "keyword": kw,
                    "url": f"https://www.amazon.com/s?k={kw.replace(' ', '+')}",
                }
                for kw in batch
            ]

            future = executor.submit(
                run_worker,
                i + 1,  # worker_id
                task_list,
                headless,
            )
            futures[future] = i + 1

        # 收集结果
        for future in as_completed(futures):
            worker_id = futures[future]
            try:
                results = future.result()
                all_results.extend(results)
                logger.info(f"Worker {worker_id} 返回 {len(results)} 个结果")
            except Exception as e:
                logger.error(f"Worker {worker_id} 执行失败: {e}")

    logger.info("\n" + "=" * 60)
    logger.info(f"并行搜索完成: 总计 {len(all_results)} 个结果")
    logger.info("=" * 60)

    return all_results


def run_worker(worker_id: int, tasks: list[dict], headless: bool) -> list[dict]:
    """工作进程入口函数（需要在顶层定义以便 pickle）

    Args:
        worker_id: 工作进程ID
        tasks: 任务列表
        headless: 是否无头模式

    Returns:
        结果列表
    """
    worker = ParallelCrawlerWorker(worker_id, headless)
    return worker.run(tasks)


class MultiWindowCrawler:
    """多窗口爬虫 - 每个窗口独立处理任务"""

    def __init__(self, num_windows: int = 3, tabs_per_window: int = 3):
        self.num_windows = num_windows
        self.tabs_per_window = tabs_per_window

    def run_parallel(self, keywords: list[str]) -> list[dict]:
        """并行运行多个窗口

        Args:
            keywords: 关键词列表

        Returns:
            所有结果
        """
        logger.info("=" * 60)
        logger.info(f"多窗口爬虫 - {self.num_windows} 窗口 x {self.tabs_per_window} 标签")
        logger.info("=" * 60)

        # 分配任务
        total_tasks = min(len(keywords), self.num_windows * self.tabs_per_window)
        keywords_to_process = keywords[:total_tasks]

        # 使用进程池
        all_results = []

        with ProcessPoolExecutor(max_workers=self.num_windows) as executor:
            futures = []

            for window_id in range(self.num_windows):
                # 计算这个窗口的任务
                start_idx = window_id * self.tabs_per_window
                end_idx = min(start_idx + self.tabs_per_window, total_tasks)

                if start_idx >= total_tasks:
                    break

                window_keywords = keywords_to_process[start_idx:end_idx]

                if not window_keywords:
                    continue

                # 提交任务
                future = executor.submit(
                    self._run_window,
                    window_id + 1,
                    window_keywords,
                    self.tabs_per_window,
                )
                futures.append(future)
                logger.info(f"  窗口 {window_id + 1}: {len(window_keywords)} 个任务")

            # 收集结果
            for future in as_completed(futures):
                try:
                    results = future.result()
                    all_results.extend(results)
                except Exception as e:
                    logger.error(f"窗口执行失败: {e}")

        logger.info(f"\n✓ 完成: {len(all_results)} 个结果")
        return all_results

    def _run_window(self, window_id: int, keywords: list[str], max_tabs: int) -> list[dict]:
        """单个窗口的工作函数

        Args:
            window_id: 窗口ID
            keywords: 关键词列表
            max_tabs: 最大标签数

        Returns:
            结果列表
        """
        results = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()

            logger.info(f"[窗口 {window_id}] 打开浏览器，处理 {len(keywords)} 个关键词")

            # 创建多个标签页
            pages = []
            for keyword in keywords:
                page = context.new_page()
                pages.append((page, keyword))

            # 并发导航（注意：同步API仍然是串行的）
            for idx, (page, keyword) in enumerate(pages):
                try:
                    url = f"https://www.amazon.com/s?k={keyword.replace(' ', '+')}"
                    logger.info(f"[窗口 {window_id}] [{idx + 1}] {keyword}")

                    page.goto(url, timeout=30000, wait_until="domcontentloaded")
                    time.sleep(2)

                    title = page.title() or "N/A"
                    results.append({
                        "window_id": window_id,
                        "keyword": keyword,
                        "title": title,
                        "url": page.url,
                        "status": "success",
                    })

                except Exception as e:
                    logger.error(f"[窗口 {window_id}] [{idx + 1}] 失败: {e}")
                    results.append({
                        "window_id": window_id,
                        "keyword": keyword,
                        "error": str(e),
                        "status": "failed",
                    })

            logger.info(f"[窗口 {window_id}] 保持打开 5 秒...")
            time.sleep(5)

            browser.close()
            logger.info(f"[窗口 {window_id}] 完成")

        return results


def main():
    """主函数"""
    print("\n🚀 并行爬虫测试")
    print("\n选择模式:")
    print("  1. 多进程搜索 (3个进程，每个处理多个关键词)")
    print("  2. 多窗口爬虫 (3个窗口，每个3个标签)")
    print("  3. 大规模测试 (5个窗口，每个5个标签)")

    choice = input("\nEnter choice (1-3): ").strip()

    # 测试关键词
    keywords = [
        "water bottle",
        "blender",
        "coffee maker",
        "mouse",
        "keyboard",
        "headphones",
        "charger",
        "cable",
        "monitor",
        "speaker",
        "webcam",
        "microphone",
        "stand",
        "hub",
        "dock",
    ]

    if choice == "1":
        # 多进程搜索
        results = parallel_search(
            keywords[:9],  # 9个关键词
            workers=3,
            headless=False,  # 显示浏览器
        )

    elif choice == "2":
        # 多窗口爬虫
        crawler = MultiWindowCrawler(num_windows=3, tabs_per_window=3)
        results = crawler.run_parallel(keywords[:9])

    elif choice == "3":
        # 大规模测试
        crawler = MultiWindowCrawler(num_windows=5, tabs_per_window=5)
        results = crawler.run_parallel(keywords[:25])

    else:
        print("无效选择，运行模式1...")
        results = parallel_search(keywords[:9], workers=3, headless=False)

    # 打印结果摘要
    print("\n" + "=" * 60)
    print("结果摘要")
    print("=" * 60)
    success = sum(1 for r in results if r.get("status") == "success")
    failed = sum(1 for r in results if r.get("status") == "failed")
    print(f"  成功: {success}")
    print(f"  失败: {failed}")
    print(f"  总计: {len(results)}")


if __name__ == "__main__":
    # Windows 下需要这个
    mp.set_start_method("spawn", force=True)

    main()
