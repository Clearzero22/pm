"""
Product detail page parser with human-like scrolling simulation.
"""
import logging
import random
from typing import Any

logger = logging.getLogger(__name__)


def human_like_scroll(page, max_scrolls: int = 5):
    """Simulate human scrolling behavior.

    Args:
        page: Playwright Page object
        max_scrolls: Maximum number of scroll actions
    """
    logger.debug("      Simulating human scroll behavior...")

    for i in range(max_scrolls):
        # Random scroll distance (humans don't scroll uniformly)
        scroll_distance = random.randint(300, 800)
        page.evaluate(f"window.scrollBy(0, {scroll_distance})")

        # Random pause between scrolls (humans pause to read)
        pause_time = random.uniform(0.5, 2.0)
        page.wait_for_timeout(int(pause_time * 1000))

        # Check if we've reached the bottom
        is_bottom = page.evaluate(
            "() => (window.innerHeight + window.scrollY) >= document.body.scrollHeight - 100"
        )
        if is_bottom:
            logger.debug(f"      Reached bottom after {i + 1} scrolls")
            break

    # Scroll back to top
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(500)


def extract_images(page) -> list[str]:
    """Extract all product images from the detail page.

    Args:
        page: Playwright Page object

    Returns:
        List of image URLs
    """
    images = []

    try:
        # Method 1: Main landing image (highest priority)
        try:
            main_img = page.locator("#landingImage").first
            if main_img.count() > 0:
                # Prefer data-old-hires (high res), fallback to src
                hires = main_img.get_attribute("data-old-hires") or ""
                src = main_img.get_attribute("src") or ""
                img_url = hires if hires and ".jpg" in hires else src
                if img_url and "media-amazon.com/images/" in img_url:
                    images.append(img_url)
                    logger.debug(f"      Found main image")
        except Exception as e:
            logger.debug(f"      Main image error: {e}")

        # Method 2: Alt images (thumbnails that link to full size)
        try:
            alt_imgs = page.locator("#altImages img").all()
            for img in alt_imgs[:10]:
                src = img.get_attribute("src") or ""
                # Skip tiny thumbnails and icons
                if "media-amazon.com/images/" in src:
                    # Convert to high-res version if it's a thumbnail
                    if "_AC_US" in src or "_AC_UL" in src:
                        # Extract the base image ID
                        parts = src.split("/I/")
                        if len(parts) > 1:
                            base = parts[1].split("._")[0]
                            high_res = f"https://m.media-amazon.com/images/I/{base}._AC_SL1500_.jpg"
                            images.append(high_res)
                    else:
                        images.append(src)
        except Exception as e:
            logger.debug(f"      Alt images error: {e}")

        # Deduplicate while preserving order
        seen = set()
        unique_images = []
        for img in images:
            if img and "media-amazon.com" in img and img not in seen:
                seen.add(img)
                unique_images.append(img)

        logger.debug(f"      Found {len(unique_images)} unique images")
        return unique_images[:10]  # Limit to 10 images

    except Exception as e:
        logger.warning(f"      Error extracting images: {e}")
        return []


def extract_title(page) -> str:
    """Extract product title from detail page.

    Args:
        page: Playwright Page object

    Returns:
        Product title
    """
    title_selectors = [
        "#productTitle",
        "#title h1",
        ".product-title",
        "h1.a-size-large",
    ]

    for selector in title_selectors:
        try:
            el = page.locator(selector).first
            if el.count() > 0:
                title = el.text_content(timeout=2000)
                if title and len(title) > 5:
                    logger.debug(f"      Found title: {title[:50]}...")
                    return title.strip()
        except:
            continue

    return "N/A"


def extract_description(page) -> str:
    """Extract product description from detail page.

    Args:
        page: Playwright Page object

    Returns:
        Product description
    """
    description = ""

    try:
        # Method 1: Feature bullets (most reliable)
        bullets = page.locator("#feature-bullets ul li").all()
        if bullets and len(bullets) > 1:
            bullet_texts = []
            for bullet in bullets[:10]:  # Max 10 bullets
                text = bullet.text_content(timeout=1000) or ""
                if text and len(text.strip()) > 3:
                    clean = text.strip()
                    # Skip common non-descriptive bullets
                    if not clean.lower().startswith(("see more", "make sure")):
                        bullet_texts.append(clean)

            if bullet_texts:
                description = " | ".join(bullet_texts)
                logger.debug(f"      Found {len(bullet_texts)} bullet points")
                return description

        # Method 2: Product description block
        desc_selectors = [
            "#productDescription",
            "#desc-bullets",
            ".a-expander-content",
        ]

        for selector in desc_selectors:
            try:
                el = page.locator(selector).first
                if el.count() > 0:
                    desc = el.text_content(timeout=2000)
                    if desc and len(desc) > 50:
                        description = desc.strip()[:500]  # Limit length
                        logger.debug(f"      Found description: {len(description)} chars")
                        return description
            except:
                continue

    except Exception as e:
        logger.warning(f"      Error extracting description: {e}")

    return "N/A"


def extract_price(page) -> str:
    """Extract product price from detail page.

    Args:
        page: Playwright Page object

    Returns:
        Product price
    """
    price_selectors = [
        ".a-price .a-offscreen",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        ".a-price-whole",
    ]

    for selector in price_selectors:
        try:
            el = page.locator(selector).first
            if el.count() > 0:
                price = el.text_content(timeout=1000)
                if price and "$" in price:
                    return price.strip()
        except:
            continue

    return "N/A"


def extract_rating(page) -> str:
    """Extract product rating from detail page.

    Args:
        page: Playwright Page object

    Returns:
        Product rating
    """
    try:
        rating_el = page.locator("[data-hook='average-star-rating'] span").first
        if rating_el.count() > 0:
            rating = rating_el.text_content(timeout=1000)
            if rating:
                return rating.strip()
    except:
        pass

    return "N/A"


def parse_product_detail(page, asin: str) -> dict[str, Any] | None:
    """Parse complete product detail page.

    Args:
        page: Playwright Page object (already navigated to product)
        asin: Product ASIN

    Returns:
        Dictionary with complete product data
    """
    logger.info(f"    Extracting details for ASIN: {asin}")

    try:
        # Scroll to load all content
        human_like_scroll(page, max_scrolls=5)

        # Extract all data
        title = extract_title(page)
        price = extract_price(page)
        rating = extract_rating(page)
        description = extract_description(page)
        images = extract_images(page)

        # Combine images into single string
        images_str = " | ".join(images) if images else "N/A"

        product = {
            "asin": asin,
            "title": title,
            "price": price,
            "rating": rating,
            "description": description[:500] if description else "N/A",  # Limit for CSV
            "images": images_str,
            "image_count": len(images),
            "url": page.url,
        }

        logger.info(f"      ✓ Extracted: {title[:40]}...")
        return product

    except Exception as e:
        logger.error(f"      ✗ Error parsing product detail: {e}")
        return None
