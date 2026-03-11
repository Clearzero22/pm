#!/usr/bin/env python
"""
大规模并行测试 - 25个任务同时执行
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


def run_window(window_id: int, keywords: list[str]) -> list[dict]:
    """单个窗口的工作函数"""
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        logger.info(f"[窗口 {window_id}] 启动，处理 {len(keywords)} 个任务")

        for idx, keyword in enumerate(keywords):
            page = context.new_page()

            try:
                url = f"https://www.amazon.com/s?k={keyword.replace(' ', '+')}"
                logger.info(f"[窗口 {window_id}] [{idx + 1}/{len(keywords)}] {keyword}")

                page.goto(url, timeout=30000, wait_until="domcontentloaded")
                time.sleep(1.5)  # 等待页面稳定

                title = page.title() or "N/A"
                results.append({
                    "window_id": window_id,
                    "keyword": keyword,
                    "title": title[:50],
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
            finally:
                page.close()

        logger.info(f"[窗口 {window_id}] 完成 {len(results)}/{len(keywords)}")

        # 保持浏览器打开以便观察
        time.sleep(3)
        browser.close()

    return results


def main():
    """25任务并行测试"""
    # 25个关键词
    keywords = [
        "water bottle", "blender", "coffee maker", "mouse", "keyboard",
        "headphones", "charger", "cable", "monitor", "speaker",
        "webcam", "microphone", "stand", "hub", "dock",
        "router", "adapter", "case", "screen", "lamp",
        "fan", "heater", "cooler", "drive", "memory",
    ]

    windows = 5
    tasks_per_window = 5

    logger.info("=" * 60)
    logger.info(f"🚀 大规模并行测试 - {windows} 窗口 x {tasks_per_window} 任务 = {len(keywords)} 总任务")
    logger.info("=" * 60)

    # 分配任务
    task_batches = []
    for i in range(windows):
        start = i * tasks_per_window
        end = start + tasks_per_window
        batch = keywords[start:end]
        task_batches.append(batch)
        logger.info(f"  窗口 {i + 1}: {', '.join(batch)}")

    logger.info("\n开始并行执行...\n")
    start_time = time.time()

    # 并行执行
    all_results = []

    with ProcessPoolExecutor(max_workers=windows) as executor:
        futures = {}

        for i, batch in enumerate(task_batches):
            future = executor.submit(run_window, i + 1, batch)
            futures[future] = i + 1

        for future in as_completed(futures):
            window_id = futures[future]
            try:
                results = future.result()
                all_results.extend(results)
            except Exception as e:
                logger.error(f"窗口 {window_id} 执行失败: {e}")

    elapsed = time.time() - start_time

    # 统计结果
    success = sum(1 for r in all_results if r.get("status") == "success")
    failed = sum(1 for r in all_results if r.get("status") == "failed")

    logger.info("\n" + "=" * 60)
    logger.info("✓ 测试完成")
    logger.info("=" * 60)
    logger.info(f"  总任务: {len(all_results)}")
    logger.info(f"  成功: {success}")
    logger.info(f"  失败: {failed}")
    logger.info(f"  总耗时: {elapsed:.2f} 秒")
    logger.info(f"  平均每任务: {elapsed/len(all_results):.2f} 秒")
    logger.info(f"  速度提升: ~{25/elapsed:.1f}x (vs 串行)")


if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)
    main()
