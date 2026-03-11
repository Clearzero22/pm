"""
Parser module for extracting product data from Amazon pages.
Uses multiple strategies to handle Amazon's dynamic content loading.
"""
import json
import logging
import re

logger = logging.getLogger(__name__)


def safe_get_text(locator, selector: str, default: str = "N/A") -> str:
    """Safely get text content from a locator.

    Args:
        locator: Playwright Locator
        selector: CSS selector
        default: Default value if not found

    Returns:
        Text content or default value
    """
    try:
        el = locator.locator(selector).first
        if el.count() > 0:
            return el.text_content(timeout=500) or default
    except:
        pass
    return default


def safe_get_attr(locator, selector: str, attr: str, default: str = "N/A") -> str:
    """Safely get attribute from a locator.

    Args:
        locator: Playwright Locator
        selector: CSS selector
        attr: Attribute name
        default: Default value if not found

    Returns:
        Attribute value or default value
    """
    try:
        el = locator.locator(selector).first
        if el.count() > 0:
            return el.get_attribute(attr) or default
    except:
        pass
    return default


def parse_product_card(card, index: int) -> dict | None:
    """Parse a single product card element with error handling.

    Args:
        card: Playwright Locator for product card
        index: Product index for logging

    Returns:
        Dictionary with product data or None if parsing fails
    """
    try:
        # Get ASIN from data-asin attribute
        asin = card.get_attribute("data-asin") or ""
        if not asin:
            return None

        # Build URL from ASIN
        url = f"https://www.amazon.com/dp/{asin}"

        # Try to get product name (multiple selectors)
        name = safe_get_text(card, "h2 a span") or safe_get_text(card, "h3 a span") or f"Product {asin}"

        # Price - try different selectors
        price = safe_get_text(card, ".a-price span.a-offscreen")
        if price == "N/A":
            price = safe_get_text(card, ".a-price .a-offscreen")
        if price == "N/A":
            price = safe_get_text(card, "span.a-price")

        # Rating
        rating = safe_get_text(card, "i.a-icon-star-small span")
        if rating == "N/A":
            rating = safe_get_text(card, "i.a-icon-alt span")

        # Review count
        reviews = safe_get_text(card, "a[href*='#customerReviews']")
        reviews = reviews.replace(",", "") if reviews else "0"

        # Image
        image = safe_get_attr(card, ".a-section img", "src") or safe_get_attr(card, "img", "src")

        # Rank (from data-cel-widget or similar)
        rank = ""
        try:
            widget = card.get_attribute("data-cel-widget") or ""
            if widget:
                rank_match = re.search(r'(\d+)', widget)
                if rank_match:
                    rank = rank_match.group(1)
        except:
            pass

        product = {
            "name": name.strip(),
            "url": url,
            "price": price,
            "rating": rating,
            "review_count": reviews,
            "image_url": image,
            "asin": asin,
            "rank": rank,
        }

        logger.debug(f"      [{index}] Parsed: {name[:40]}...")
        return product

    except Exception as e:
        logger.warning(f"      [{index}] Parse error: {e}")
        return None


def extract_products_from_json(page) -> list[dict]:
    """Extract products from data-a-carousel-options JSON.

    Args:
        page: Playwright Page object

    Returns:
        List of product dictionaries
    """
    products = []

    try:
        # Find all elements with carousel data
        carousels = page.locator("[data-a-carousel-options]").all()
        logger.debug(f"Found {len(carousels)} carousels")

        for idx, carousel in enumerate(carousels, 1):
            try:
                options_str = carousel.get_attribute("data-a-carousel-options")
                if not options_str:
                    continue

                # Parse JSON
                options = json.loads(options_str)

                # Extract product list
                if "ajax" in options and "id_list" in options["ajax"]:
                    product_list = options["ajax"]["id_list"]

                    for item in product_list:
                        product_id = item.get("id", "")
                        if not product_id:
                            continue

                        # Build product URL
                        url = f"https://www.amazon.com/dp/{product_id}"

                        # Extract rank if available
                        rank = ""
                        if "metadataMap" in item:
                            rank = item["metadataMap"].get("render.zg.rank", "")

                        products.append({
                            "name": f"Product {product_id}",
                            "url": url,
                            "price": "N/A",
                            "rating": "N/A",
                            "review_count": "0",
                            "image_url": "N/A",
                            "asin": product_id,
                            "rank": rank,
                        })

                    logger.debug(f"  Carousel {idx}: extracted {len(product_list)} products")

            except Exception as e:
                logger.warning(f"  Error parsing carousel {idx}: {e}")
                continue

    except Exception as e:
        logger.error(f"Error in JSON extraction: {e}")

    return products


def parse_page(page, page_num: int) -> list[dict]:
    """Parse all products from current page using multiple strategies.

    Args:
        page: Playwright Page object
        page_num: Current page number

    Returns:
        List of product dictionaries
    """
    logger.debug(f"    Attempting to parse page {page_num}...")

    products = []

    # Strategy 1: Try [data-asin] cards (most reliable for Amazon)
    try:
        cards = page.locator("[data-asin]").all()
        if len(cards) > 0:
            logger.debug(f"    Found {len(cards)} cards with [data-asin] selector")

            for i, card in enumerate(cards, 1):
                product = parse_product_card(card, i)
                if product:
                    products.append(product)

            if products:
                logger.info(f"    Successfully parsed {len(products)} products from [data-asin]")
                return products

    except Exception as e:
        logger.debug(f"    [data-asin] strategy failed: {e}")

    # Strategy 2: Extract from JSON data (fallback)
    logger.debug("    Trying JSON extraction strategy...")
    products = extract_products_from_json(page)

    if products:
        logger.info(f"    Extracted {len(products)} products from JSON data")
    else:
        logger.warning("    No products found using any strategy")

    return products
