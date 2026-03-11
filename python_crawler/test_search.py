#!/usr/bin/env python
"""Test Amazon search crawler functionality."""
import logging

from src.search_crawler import AmazonSearchCrawler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


def test_search_basic():
    """Test basic search functionality."""
    print("\n" + "=" * 60)
    print("TEST: Basic Search")
    print("=" * 60)

    crawler = AmazonSearchCrawler(
        keyword="water bottle",
        max_pages=1,
        max_products=3,
        headless=False,  # Show browser for debugging
    )

    products = crawler.crawl()
    crawler.save_csv("test_search_output.csv")

    print(f"\n✓ Test passed: {len(products)} products extracted")


def test_search_with_sort():
    """Test search with sorting."""
    print("\n" + "=" * 60)
    print("TEST: Search with Sorting (Review Rank)")
    print("=" * 60)

    crawler = AmazonSearchCrawler(
        keyword="blender",
        max_pages=1,
        max_products=3,
        sort_by="review-rank",
        headless=False,
    )

    products = crawler.crawl()
    crawler.save_csv("test_search_review_rank.csv")

    print(f"\n✓ Test passed: {len(products)} products extracted")


def test_search_price_sort():
    """Test search with price sorting."""
    print("\n" + "=" * 60)
    print("TEST: Search with Price Sort (Low to High)")
    print("=" * 60)

    crawler = AmazonSearchCrawler(
        keyword="coffee maker",
        max_pages=1,
        max_products=3,
        sort_by="price-asc",
        headless=False,
    )

    products = crawler.crawl()
    crawler.save_csv("test_search_price_asc.csv")

    print(f"\n✓ Test passed: {len(products)} products extracted")


if __name__ == "__main__":
    print("\n🧪 Amazon Search Crawler - Test Suite")
    print("Choose a test:")
    print("  1. Basic search")
    print("  2. Search with review ranking")
    print("  3. Search with price sorting")
    print("  4. Run all tests")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        test_search_basic()
    elif choice == "2":
        test_search_with_sort()
    elif choice == "3":
        test_search_price_sort()
    elif choice == "4":
        test_search_basic()
        test_search_with_sort()
        test_search_price_sort()
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETE")
        print("=" * 60)
    else:
        print("Invalid choice. Running basic search...")
        test_search_basic()
