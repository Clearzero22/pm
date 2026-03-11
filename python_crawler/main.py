"""Amazon crawler entry point - Best Sellers & Search modes."""
import argparse
import logging

from src.crawler import AmazonCrawler
from src.search_crawler import AmazonSearchCrawler


def setup_logging(level: str = "INFO"):
    """Configure logging level.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    """Run the Amazon crawler - Best Sellers or Search mode."""
    parser = argparse.ArgumentParser(
        description="Amazon Crawler - Best Sellers & Keyword Search",
        epilog="Examples:\n"
              "  Best Sellers: uv run python main.py --pages 2\n"
              "  Search:       uv run python main.py --search 'water bottle' --sort review-rank",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level (default: INFO)",
    )

    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--search",
        type=str,
        metavar="KEYWORD",
        help="Search mode: crawl by keyword instead of Best Sellers",
    )

    # Common parameters
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Number of pages to crawl (default: 1)",
    )
    parser.add_argument(
        "--products",
        type=int,
        default=5,
        help="Max products to extract per page (default: 5)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="amazon_products.csv",
        help="Output CSV filename (default: amazon_products.csv)",
    )

    # Search-specific parameters
    parser.add_argument(
        "--sort",
        type=str,
        choices=["relevance", "price-asc", "price-desc", "review-rank", "date-desc"],
        default="relevance",
        help="Sort search results (default: relevance)",
    )
    parser.add_argument(
        "--category",
        type=str,
        metavar="CATEGORY",
        help="Filter by Amazon category (e.g., kitchen, electronics)",
    )

    args = parser.parse_args()
    setup_logging(args.log_level)

    # Determine mode
    if args.search:
        # SEARCH MODE
        print("=" * 60)
        print("Amazon Search Crawler")
        print("=" * 60)
        print(f"  Keyword:       {args.search}")
        print(f"  Pages:         {args.pages}")
        print(f"  Products/page: {args.products}")
        print(f"  Sort by:       {args.sort}")
        if args.category:
            print(f"  Category:      {args.category}")
        print(f"  Headless:      {args.headless}")
        print(f"  Output:        {args.output}")
        print("=" * 60)

        crawler = AmazonSearchCrawler(
            keyword=args.search,
            max_pages=args.pages,
            max_products=args.products,
            sort_by=args.sort,
            category=args.category,
            headless=args.headless,
        )
        crawler.crawl()
        crawler.save_csv(args.output)

    else:
        # BEST SELLERS MODE (default)
        print("=" * 60)
        print("Amazon Best Sellers Crawler")
        print("=" * 60)
        print(f"  Pages:         {args.pages}")
        print(f"  Products/page: {args.products}")
        print(f"  Headless:      {args.headless}")
        print(f"  Output:        {args.output}")
        print("=" * 60)

        crawler = AmazonCrawler(
            max_pages=args.pages,
            max_products=args.products,
            headless=args.headless,
        )
        crawler.crawl()
        crawler.save_csv(args.output)


if __name__ == "__main__":
    main()
