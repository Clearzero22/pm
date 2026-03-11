"""
Utility functions for Amazon crawler.
"""
import csv
import re
from pathlib import Path
from typing import Any, List


def clean_text(text: str) -> str:
    """Clean text for CSV output.

    Args:
        text: Raw text

    Returns:
        Cleaned text safe for CSV
    """
    if not text or text == "N/A":
        return ""

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove newlines and special chars
    text = text.replace("\n", " ").replace("\r", "")
    text = re.sub(r"[^\w\s\-\.,;:/@()]", "", text)

    return text.strip()


def write_to_csv(data: List[dict[str, Any]], filepath: Path) -> None:
    """Write data to CSV file with proper formatting.

    Args:
        data: List of dictionaries containing product data
        filepath: Path to output CSV file
    """
    if not data:
        print("No data to write")
        return

    # Define field order
    fieldnames = [
        "asin",
        "title",
        "price",
        "rating",
        "description",
        "image_count",
        "images",
        "url",
    ]

    # Clean data
    cleaned_data = []
    for item in data:
        cleaned_item = {}
        for key in fieldnames:
            value = item.get(key, "")
            if isinstance(value, str):
                value = clean_text(value)
            cleaned_item[key] = value
        cleaned_data.append(cleaned_item)

    # Write to CSV
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(cleaned_data)

    print(f"Saved {len(data)} items to {filepath}")


def deduplicate(items: List[dict[str, Any]], key: str = "asin") -> List[dict[str, Any]]:
    """Remove duplicate items based on key.

    Args:
        items: List of dictionaries
        key: Key to use for deduplication

    Returns:
        Deduplicated list
    """
    seen = set()
    result = []
    for item in items:
        value = item.get(key)
        if value and value not in seen:
            seen.add(value)
            result.append(item)
    return result
