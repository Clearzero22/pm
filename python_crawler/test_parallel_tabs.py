#!/usr/bin/env python
"""
并行打开多个标签页测试脚本
验证 Playwright 能否同时处理多个标签页
"""
import time
from playwright.sync_api import sync_playwright


def test_single_browser_multiple_pages():
    """方案A: 单浏览器多标签页 - 最简单"""
    print("=" * 60)
    print("方案A: 单浏览器多标签页")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        pages = []
        urls = [
            "https://www.amazon.com",
            "https://www.amazon.com/gp/bestsellers/",
            "https://www.amazon.com/s?k=water+bottle",
            "https://www.amazon.com/s?k=blender",
        ]

        print(f"\n打开 {len(urls)} 个标签页...")

        for i, url in enumerate(urls):
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded")
            pages.append(page)
            print(f"  [{i+1}] {url}")

        print(f"\n✓ 已打开 {len(pages)} 个标签页")
        print("浏览器将保持打开 10 秒...")
        time.sleep(10)

        browser.close()
        print("\n✓ 测试完成")


def test_multiple_contexts():
    """方案B: 多浏览器上下文 - 更好的隔离"""
    print("\n" + "=" * 60)
    print("方案B: 多浏览器上下文")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        contexts = []
        pages = []
        keywords = ["water bottle", "blender", "coffee maker", "mouse", "keyboard"]

        print(f"\n创建 {len(keywords)} 个上下文，每个搜索一个关键词...")

        for i, keyword in enumerate(keywords):
            context = browser.new_context()
            page = context.new_page()

            url = f"https://www.amazon.com/s?k={keyword.replace(' ', '+')}"
            page.goto(url, wait_until="domcontentloaded")

            contexts.append(context)
            pages.append(page)
            print(f"  [{i+1}] Context {i+1} → {keyword}")

        print(f"\n✓ 已创建 {len(contexts)} 个上下文")
        print("浏览器将保持打开 10 秒...")
        time.sleep(10)

        for context in contexts:
            context.close()
        browser.close()
        print("\n✓ 测试完成")


def test_20_tabs_simple():
    """测试: 打开20个标签页"""
    print("\n" + "=" * 60)
    print("测试: 并行打开20个亚马逊标签页")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        pages = []
        base_urls = [
            "https://www.amazon.com",
            "https://www.amazon.com/gp/bestsellers/",
            "https://www.amazon.com/gp/new-releases/",
            "https://www.amazon.com/gp/movers-and-shakers/",
        ]

        # 搜索URL
        search_keywords = [f"keyword{i}" for i in range(16)]

        print(f"\n打开 20 个标签页 (4个主页 + 16个搜索)...")

        # 打开主页类URL
        for i, url in enumerate(base_urls):
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded")
            pages.append(page)
            print(f"  [{i+1}/20] {url}")

        # 打开搜索页
        for i, keyword in enumerate(search_keywords):
            page = context.new_page()
            url = f"https://www.amazon.com/s?k={keyword}"
            page.goto(url, wait_until="domcontentloaded")
            pages.append(page)
            print(f"  [{i+5}/20] Search: {keyword}")

        print(f"\n✓ 已打开 {len(pages)} 个标签页")
        print("浏览器将保持打开 15 秒，请观察浏览器...")
        time.sleep(15)

        browser.close()
        print("\n✓ 测试完成")


def test_parallel_navigation():
    """测试: 并行导航（所有标签页同时加载）"""
    print("\n" + "=" * 60)
    print("测试: 并行导航性能")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        # 先创建所有页面对象
        print("创建 10 个页面对象...")
        pages = [context.new_page() for _ in range(10)]

        # 准备URL
        keywords = ["water bottle", "blender", "coffee maker", "mouse", "keyboard",
                   "headphones", "charger", "cable", "monitor", "speaker"]
        urls = [f"https://www.amazon.com/s?k={kw.replace(' ', '+')}" for kw in keywords]

        # 并行导航（同时发起请求）
        print(f"\n同时发起 {len(urls)} 个页面请求...")
        start_time = time.time()

        for i, (page, url) in enumerate(zip(pages, urls)):
            print(f"  [{i+1}] {keywords[i]}")
            # 注意：goto 默认会等待，所以这里是串行等待
            # 真正的并行需要异步API
            page.goto(url, wait_until="domcontentloaded")

        elapsed = time.time() - start_time
        print(f"\n✓ 完成 {len(pages)} 个页面")
        print(f"  总耗时: {elapsed:.2f} 秒")
        print(f"  平均每个: {elapsed/len(pages):.2f} 秒")

        time.sleep(5)
        browser.close()
        print("\n✓ 测试完成")


def main():
    """主函数"""
    print("\n🧪 Playwright 并行标签页测试套件")
    print("\n选择测试:")
    print("  1. 单浏览器多标签页 (4个)")
    print("  2. 多浏览器上下文 (5个)")
    print("  3. 打开20个标签页")
    print("  4. 并行导航性能测试")
    print("  5. 运行所有测试")

    choice = input("\nEnter choice (1-5): ").strip()

    if choice == "1":
        test_single_browser_multiple_pages()
    elif choice == "2":
        test_multiple_contexts()
    elif choice == "3":
        test_20_tabs_simple()
    elif choice == "4":
        test_parallel_navigation()
    elif choice == "5":
        test_single_browser_multiple_pages()
        test_multiple_contexts()
        test_20_tabs_simple()
        test_parallel_navigation()
        print("\n" + "=" * 60)
        print("所有测试完成")
        print("=" * 60)
    else:
        print("无效选择，运行测试3...")
        test_20_tabs_simple()


if __name__ == "__main__":
    main()
