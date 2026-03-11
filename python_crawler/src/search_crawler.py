"""
Amazon Search Crawler - Search products by keyword.
Clicks into each product page to extract complete information.
"""
import logging
import random
import time
import urllib.parse
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

from .product_detail_parser import parse_product_detail
from .utils import deduplicate, write_to_csv

logger = logging.getLogger(__name__)


class AmazonSearchCrawler:
    """Crawler for Amazon search results with detail page extraction."""

    SEARCH_BASE_URL = "https://www.amazon.com/s"

    # Search sorting options
    SORT_OPTIONS = {
        "relevance": "relevance-blender",      # 默认排序
        "price-asc": "price-asc-rank",         # 价格从低到高
        "price-desc": "price-desc-rank",       # 价格从高到低
        "review-rank": "review-rank",          # 评论排序
        "date-desc": "date-desc-rank",         # 最新发布
    }

    def __init__(
        self,
        keyword: str,
        max_pages: int = 1,
        max_products: int = 10,
        sort_by: str = "relevance",
        category: str | None = None,
        headless: bool = True,
        output_dir: Path = Path("output"),
    ):
        """Initialize search crawler.

        Args:
            keyword: Search keyword (e.g., "water bottle")
            max_pages: Maximum number of search result pages to crawl
            max_products: Maximum products to extract per page
            sort_by: Sort order (relevance, price-asc, price-desc, review-rank, date-desc)
            category: Amazon category filter (e.g., "kitchen", "electronics")
            headless: Run browser in headless mode
            output_dir: Directory for output files
        """
        self.keyword = keyword
        self.max_pages = max_pages
        self.max_products = max_products
        self.sort_by = sort_by
        self.category = category
        self.headless = headless
        self.output_dir = output_dir
        self.all_products = []

        logger.info(
            f"SearchCrawler initialized: keyword='{keyword}', "
            f"pages={max_pages}, products_per_page={max_products}, "
            f"sort={sort_by}"
        )

    def crawl(self) -> list[dict]:
        """Run the search crawler.

        Returns:
            List of all products with full details
        """
        logger.info("=" * 60)
        logger.info(f"Amazon Search Crawler - Keyword: '{self.keyword}'")
        logger.info("=" * 60)

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                args=['--start-maximized']
            )
            context = browser.new_context(
                viewport={'width': 2560, 'height': 1440},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = context.new_page()

            # Inject responsive script
            page.add_init_script("""
                window.addEventListener('resize', function() {
                    document.body.style.width = '100%';
                    document.body.style.height = '100%';
                });
                document.addEventListener('DOMContentLoaded', function() {
                    document.body.style.width = '100%';
                    document.body.style.height = '100%';
                    document.body.style.overflowX = 'hidden';
                });
            """)

            for page_num in range(1, self.max_pages + 1):
                url = self._build_search_url(page_num)
                logger.info(f"\n>>> Search Page {page_num}/{self.max_pages}")
                logger.debug(f"    URL: {url}")

                products = self._crawl_search_page(page, url)
                self.all_products.extend(products)

                logger.info(f"    ✓ Page {page_num} complete: {len(products)} products")

                if page_num < self.max_pages:
                    self._human_pause(2, 4)

            browser.close()

        # Deduplicate by ASIN
        before_count = len(self.all_products)
        self.all_products = deduplicate(self.all_products, "asin")
        after_count = len(self.all_products)

        logger.info("\n" + "=" * 60)
        logger.info(f"SEARCH COMPLETE: {after_count} unique products")
        logger.info(f"  Keyword: {self.keyword}")
        logger.info(f"  Removed {before_count - after_count} duplicates")
        logger.info("=" * 60)

        return self.all_products

    def _build_search_url(self, page_num: int = 1) -> str:
        """Build search URL with parameters.

        Args:
            page_num: Page number (1-based)

        Returns:
            Complete search URL
        """
        # Encode keyword for URL
        encoded_keyword = urllib.parse.quote(self.keyword)

        # Build base URL with keyword
        params = [f"k={encoded_keyword}"]

        # Add category if specified
        if self.category:
            params.insert(0, f"i={self.category}")

        # Add sorting
        if self.sort_by in self.SORT_OPTIONS:
            params.append(f"s={self.SORT_OPTIONS[self.sort_by]}")

        # Add page number
        if page_num > 1:
            params.append(f"page={page_num}")

        return f"{self.SEARCH_BASE_URL}?{'&'.join(params)}"

    def _crawl_search_page(self, page: Page, url: str) -> list[dict]:
        """Crawl a search result page and extract product details.

        Args:
            page: Playwright Page object
            url: Search result URL

        Returns:
            List of products with full details
        """
        products = []

        try:
            # Navigate to search page
            logger.debug(f"    Loading: {url}")
            page.goto(url, timeout=30000, wait_until="domcontentloaded")

            self._ensure_responsive_layout(page)
            self._human_pause(3, 5)

            # Collect ASINs from search results (don't click yet)
            asins = self._collect_asins_from_search(page)

            if not asins:
                logger.warning("    No ASINs found on search page.")
                return products

            logger.info(f"    Found {len(asins)} products")

            # Process limited number of products
            asins_to_process = asins[:self.max_products]
            logger.info(f"    Processing {len(asins_to_process)} products...")

            for idx, asin in enumerate(asins_to_process):
                logger.info(f"\n    [{idx + 1}/{len(asins_to_process)}] ASIN: {asin}")

                # Navigate directly to product page (more reliable than clicking)
                product = self._extract_product_by_asin(page, asin, idx + 1)
                if product:
                    products.append(product)

        except Exception as e:
            logger.error(f"    Error crawling search page: {e}")
            import traceback
            logger.debug(traceback.format_exc())

        return products

    def _collect_asins_from_search(self, page: Page) -> list[str]:
        """Collect all ASINs from search results page.

        Args:
            page: Playwright Page object

        Returns:
            List of ASIN strings
        """
        asins = []

        # Get all elements with data-asin attribute
        try:
            cards = page.locator("[data-asin]").all()
            for card in cards:
                asin = card.get_attribute("data-asin")
                if asin and len(asin) == 10:  # Valid ASIN length
                    # Skip obvious ads (Sponsored items often have specific classes)
                    parent = card.evaluate("el => el.parentElement?.className || ''")
                    if "AdHolder" not in parent:
                        asins.append(asin)
        except Exception as e:
            logger.debug(f"    Error collecting ASINs: {e}")

        return asins

    def _extract_product_by_asin(self, page: Page, asin: str, index: int) -> dict | None:
        """Extract product details by navigating directly to product page.

        Args:
            page: Playwright Page object
            asin: Product ASIN
            index: Product index for logging

        Returns:
            Product data dict or None
        """
        try:
            # Construct product URL directly
            product_url = f"https://www.amazon.com/dp/{asin}"

            logger.debug(f"      Navigating to: {product_url}")
            page.goto(product_url, timeout=30000, wait_until="domcontentloaded")

            self._ensure_responsive_layout(page)
            self._human_pause(2, 3)

            logger.debug(f"      Parsing product detail...")
            product = parse_product_detail(page, asin)

            if product:
                product["search_keyword"] = self.keyword
                logger.debug(f"      ✓ Product extracted: {product.get('title', 'N/A')[:50]}...")
                return product
            else:
                logger.warning(f"      parse_product_detail returned None")

        except Exception as e:
            logger.warning(f"      Error extracting product {asin}: {e}")

        return None

    def _find_product_cards(self, page: Page) -> list:
        """Find product cards using multiple possible selectors.

        Args:
            page: Playwright Page object

        Returns:
            List of product card elements
        """
        # Try different selectors for search results
        selectors = [
            "[data-asin]",              # Standard
            "[data-component-type='s-search-result']",  # Search result type
            ".s-result-item",           # CSS class
        ]

        for selector in selectors:
            try:
                cards = page.locator(selector).all()
                # Filter out empty cards (ads, etc.)
                valid_cards = [c for c in cards if c.get_attribute("data-asin")]
                if valid_cards:
                    logger.debug(f"    Using selector: {selector} ({len(valid_cards)} cards)")
                    return valid_cards
            except Exception:
                continue

        return []

    def _extract_asin_from_card(self, card) -> str | None:
        """Extract ASIN from product card link.

        Args:
            card: Product card element

        Returns:
            ASIN string or None
        """
        try:
            link = card.locator("a[href*='/dp/']").first
            if link.count() > 0:
                href = link.get_attribute("href") or ""
                # Extract ASIN from /dp/ASIN or /dp/ASIN/
                import re
                match = re.search(r'/dp/([A-Z0-9]{10})', href)
                if match:
                    return match.group(1)
        except Exception:
            pass
        return None

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
        search_url = page.url
        try:
            card.scroll_into_view_if_needed()
            self._human_pause(0.5, 1)

            # Try multiple selectors for product link (search page has different structure)
            link_selectors = [
                "h2 a",                                    # Title link (most common)
                "a[href*='/dp/']",                         # Direct product link
                "[data-cy='title-recipe-title'] a",        # New Amazon layout
                ".s-link-inherit-style",                   # Alternative link style
                ".a-link-normal",                          # Standard Amazon link
            ]

            link = None
            for selector in link_selectors:
                try:
                    test_link = card.locator(selector).first
                    if test_link.count() > 0:
                        href = test_link.get_attribute("href") or ""
                        # Make sure it's a product link (contains /dp/)
                        if "/dp/" in href:
                            link = test_link
                            logger.debug(f"      Using selector: {selector}")
                            break
                except Exception:
                    continue

            if link:
                logger.debug(f"      Clicking product link...")
                link.click(timeout=5000)
                page.wait_for_load_state("domcontentloaded", timeout=10000)

                self._ensure_responsive_layout(page)
                self._human_pause(2, 3)

                logger.debug(f"      Parsing product detail...")
                product = parse_product_detail(page, asin)
                # Add search metadata
                if product:
                    product["search_keyword"] = self.keyword
                    logger.debug(f"      ✓ Product extracted: {product.get('title', 'N/A')[:50]}...")
                else:
                    logger.warning(f"      parse_product_detail returned None")

                return product
            else:
                logger.warning(f"      No product link found in card")

        except Exception as e:
            logger.warning(f"      Error extracting details: {e}")
            import traceback
            logger.debug(traceback.format_exc())

        return None

    def _ensure_responsive_layout(self, page: Page):
        """Force responsive layout after page navigation.

        Args:
            page: Playwright Page object
        """
        try:
            size = page.viewport_size
            if size:
                page.set_viewport_size({"width": size["width"], "height": size["height"]})

            page.evaluate("""
                () => {
                    document.body.style.width = '100%';
                    document.body.style.maxWidth = '100%';
                    document.body.style.overflowX = 'hidden';
                    window.dispatchEvent(new Event('resize'));
                }
            """)
        except Exception as e:
            logger.debug(f"      Responsive layout: {e}")

    def _human_pause(self, min_sec: float, max_sec: float):
        """Pause for a random duration to simulate human behavior.

        Args:
            min_sec: Minimum pause seconds
            max_sec: Maximum pause seconds
        """
        pause = random.uniform(min_sec, max_sec)
        time.sleep(pause)

    def save_csv(self, filename: str | None = None) -> None:
        """Save results to CSV.

        Args:
            filename: Output filename (auto-generated if None)
        """
        self.output_dir.mkdir(exist_ok=True)

        if filename is None:
            # Generate filename from keyword
            safe_keyword = self.keyword.replace(" ", "_").replace("/", "_")[:30]
            filename = f"amazon_search_{safe_keyword}.csv"

        filepath = self.output_dir / filename
        write_to_csv(self.all_products, filepath)
        logger.info(f"✓ CSV saved: {filepath}")


def main():
    """Main entry point for testing."""
    crawler = AmazonSearchCrawler(
        keyword="water bottle",
        max_pages=1,
        max_products=5,
        sort_by="review-rank",
        headless=False,
    )

    products = crawler.crawl()
    crawler.save_csv()

    print(f"\n✓ Found {len(products)} products")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    main()
