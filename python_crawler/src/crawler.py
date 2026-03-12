"""
Amazon Best Sellers crawler with product detail extraction.
Clicks into each product page to extract complete information.
"""
import logging
import random
import time
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

from .product_detail_parser import parse_product_detail
from .utils import deduplicate, write_to_csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


class AmazonCrawler:
    """Crawler for Amazon Best Sellers with detail page extraction."""

    BASE_URL = "https://www.amazon.com/gp/bestsellers/"

    def __init__(
        self,
        max_pages: int = 1,
        max_products: int = 10,
        headless: bool = True,
        output_dir: Path = Path("output"),
    ):
        """Initialize crawler.

        Args:
            max_pages: Maximum number of Best Sellers pages to crawl
            max_products: Maximum products to extract per page
            headless: Run browser in headless mode
            output_dir: Directory for output files
        """
        self.max_pages = max_pages
        self.max_products = max_products
        self.headless = headless
        self.output_dir = output_dir
        self.all_products = []

        logger.info(f"Crawler initialized: pages={max_pages}, products_per_page={max_products}")

    def crawl(self) -> list[dict]:
        """Run the crawler.

        Returns:
            List of all products with full details
        """
        logger.info("=" * 60)
        logger.info("Amazon Best Sellers Crawler - Detail Extraction Mode")
        logger.info("=" * 60)

        with sync_playwright() as p:
            # Launch browser with maximized window
            browser = p.chromium.launch(
                headless=self.headless,
                args=['--start-maximized']
            )
            # Get screen size and set viewport accordingly
            context = browser.new_context(
                viewport={'width': 2560, 'height': 1440},  # 2K resolution
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = context.new_page()

            # Inject responsive script to handle window resize
            page.add_init_script("""
                // Make page fully responsive
                window.addEventListener('resize', function() {
                    document.body.style.width = '100%';
                    document.body.style.height = '100%';
                });

                // Set initial responsive styles
                document.addEventListener('DOMContentLoaded', function() {
                    document.body.style.width = '100%';
                    document.body.style.height = '100%';
                    document.body.style.overflowX = 'hidden';
                });
            """)

            for page_num in range(1, self.max_pages + 1):
                url = f"{self.BASE_URL}?pg={page_num}" if page_num > 1 else self.BASE_URL
                logger.info(f"\n>>> Best Sellers Page {page_num}/{self.max_pages}")

                products = self._crawl_listing_page(page, url)
                self.all_products.extend(products)

                logger.info(f"    ✓ Page {page_num} complete: {len(products)} products extracted")

                if page_num < self.max_pages:
                    self._human_pause(2, 4)

            browser.close()

        # Deduplicate by ASIN
        before_count = len(self.all_products)
        self.all_products = deduplicate(self.all_products, "asin")
        after_count = len(self.all_products)

        logger.info("\n" + "=" * 60)
        logger.info(f"CRAWL COMPLETE: {after_count} unique products")
        logger.info("=" * 60)

        return self.all_products

    def _crawl_listing_page(self, page: Page, url: str) -> list[dict]:
        """Crawl a listing page and extract product details.

        Args:
            page: Playwright Page object
            url: Best Sellers listing URL

        Returns:
            List of products with full details
        """
        products = []

        try:
            # Navigate to listing page
            logger.debug(f"    Loading: {url}")
            page.goto(url, timeout=30000, wait_until="domcontentloaded")

            # Force responsive layout after navigation
            self._ensure_responsive_layout(page)

            # Wait for page to settle
            self._human_pause(3, 5)

            # Find all product cards with data-asin
            product_cards = page.locator("[data-asin]").all()
            logger.info(f"    Found {len(product_cards)} product cards")

            # Limit products to extract
            cards_to_process = min(len(product_cards), self.max_products)
            logger.info(f"    Processing {cards_to_process} products...")

            for idx in range(cards_to_process):
                card = product_cards[idx]

                # Get ASIN
                asin = card.get_attribute("data-asin")
                if not asin:
                    continue

                logger.info(f"\n    [{idx + 1}/{cards_to_process}] ASIN: {asin}")

                # Click on product and extract details
                product = self._extract_product_details(page, card, asin, idx + 1)
                if product:
                    products.append(product)

                # Go back to listing if we navigated away
                if page.url != url:
                    page.go_back()
                    self._human_pause(1, 2)

                    # Re-find cards since we went back
                    product_cards = page.locator("[data-asin]").all()

        except Exception as e:
            logger.error(f"    Error crawling listing page: {e}")

        return products

    def _extract_product_details(
        self, page: Page, card, asin: str, index: int
    ) -> dict | None:
        """Click into product and extract full details.

        Args:
            page: Playwright Page object
            card: Product card element
            asin: Product ASIN
            index: Product index for logging

        Returns:
            Product data dict or None
        """
        try:
            # Scroll card into view
            card.scroll_into_view_if_needed()
            self._human_pause(0.5, 1)

            # Click on product link
            link = card.locator("h2 a").first
            if link.count() == 0:
                link = card.locator("a[href*='/dp/']").first

            if link.count() > 0:
                # Navigate to product page
                link.click(timeout=5000)

                # Wait for navigation
                page.wait_for_load_state("domcontentloaded", timeout=10000)

                # Force responsive layout
                self._ensure_responsive_layout(page)
                self._human_pause(2, 3)

                # Extract product details
                product = parse_product_detail(page, asin)

                return product

        except Exception as e:
            logger.warning(f"      Error extracting details: {e}")

        return None

    def _ensure_responsive_layout(self, page: Page):
        """Force responsive layout after page navigation.

        Args:
            page: Playwright Page object
        """
        try:
            # Get current window size
            size = page.viewport_size
            if size:
                page.set_viewport_size({"width": size["width"], "height": size["height"]})

            # Force body to be responsive
            page.evaluate("""
                () => {
                    document.body.style.width = '100%';
                    document.body.style.maxWidth = '100%';
                    document.body.style.overflowX = 'hidden';
                    window.dispatchEvent(new Event('resize'));
                }
            """)
        except Exception as e:
            logger.debug(f"      Responsive layout adjustment: {e}")

    def _human_pause(self, min_sec: float, max_sec: float):
        """Pause for a random duration to simulate human behavior.

        Args:
            min_sec: Minimum pause seconds
            max_sec: Maximum pause seconds
        """
        pause = random.uniform(min_sec, max_sec)
        time.sleep(pause)

    def save_csv(self, filename: str = "amazon_products.csv") -> None:
        """Save results to CSV.

        Args:
            filename: Output filename (can be relative or absolute path)
        """
        filepath = Path(filename)

        # Only use output_dir if filename is just a name (no directory)
        if filepath.parent == Path("."):
            self.output_dir.mkdir(exist_ok=True)
            filepath = self.output_dir / filename

        write_to_csv(self.all_products, filepath)
        logger.info(f"✓ CSV saved: {filepath}")


def main():
    """Main entry point."""
    crawler = AmazonCrawler(
        max_pages=1,        # Number of Best Sellers pages
        max_products=5,     # Products per page (increase for more)
        headless=False,     # Show browser for debugging
    )

    crawler.crawl()
    crawler.save_csv()


if __name__ == "__main__":
    main()
