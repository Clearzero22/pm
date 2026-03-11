"""Amazon Best Sellers crawler entry point."""
import argparse
import logging

from src.crawler import AmazonCrawler


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
    """Run the Amazon Best Sellers crawler."""
    parser = argparse.ArgumentParser(
        description="Amazon Best Sellers Crawler - Extract product details"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level (default: INFO)",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Number of Best Sellers pages to crawl (default: 1)",
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
    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)

    # Print config
    print("=" * 60)
    print("Amazon Best Sellers Crawler - Detail Extraction")
    print("=" * 60)
    print(f"  Pages:         {args.pages}")
    print(f"  Products/page: {args.products}")
    print(f"  Headless:      {args.headless}")
    print(f"  Output:        {args.output}")
    print("=" * 60)

    # Create and run crawler
    crawler = AmazonCrawler(
        max_pages=args.pages,
        max_products=args.products,
        headless=args.headless,
    )

    crawler.crawl()
    crawler.save_csv(args.output)


if __name__ == "__main__":
    main()
