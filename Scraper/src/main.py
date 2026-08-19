import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, HttpUrl, ValidationError

# Directories
BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "cache"
OUTPUT_DIR = BASE_DIR / "output"

START_URL = "https://books.toscrape.com/catalogue/page-1.html"
MAX_CATALOGUE_PAGES = 3

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/your-username/your-repo)"
}
TIMEOUT_SECONDS = 10
REQUEST_DELAY_SECONDS = 0.5


# --- Pydantic Schema ---
class BookRecord(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: Optional[str] = None
    description: Optional[str] = None
    source_page: HttpUrl
    fetched_at: str


def fetch_and_cache(url: str, cache_file_name: str) -> tuple[str, bool]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / cache_file_name

    if cache_path.exists():
        html_content = cache_path.read_text(encoding="utf-8")
        return html_content, True

    time.sleep(REQUEST_DELAY_SECONDS)

    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch {url}. Status code: {response.status_code}")

    html_content = response.text
    cache_path.write_text(html_content, encoding="utf-8")
    return html_content, False


def discover_book_urls(start_url: str, max_pages: int = 3) -> list[dict[str, str]]:
    current_url = start_url
    pages_crawled = 0
    discovered_items = []

    while current_url and pages_crawled < max_pages:
        pages_crawled += 1
        cache_filename = f"catalogue-page-{pages_crawled}.html"
        html_content, _ = fetch_and_cache(current_url, cache_filename)

        soup = BeautifulSoup(html_content, "html.parser")
        product_links = soup.select("article.product_pod h3 a")

        for link in product_links:
            relative_href = link.get("href")
            absolute_url = urljoin(current_url, relative_href)
            discovered_items.append({
                "product_url": absolute_url,
                "source_page": current_url,
            })

        next_button = soup.select_one("li.next a")
        if next_button:
            next_href = next_button.get("href")
            current_url = urljoin(current_url, next_href)
        else:
            current_url = None

    return discovered_items


def extract_book_details(product_url: str, source_page: str) -> dict:
    url_hash = hashlib.md5(product_url.encode("utf-8")).hexdigest()[:10]
    cache_filename = f"book-{url_hash}.html"

    html_content, _ = fetch_and_cache(product_url, cache_filename)
    soup = BeautifulSoup(html_content, "html.parser")
    product_main = soup.select_one("div.product_main")

    title = product_main.select_one("h1").get_text(strip=True) if product_main and product_main.select_one("h1") else None
    price_text = product_main.select_one("p.price_color").get_text(strip=True) if product_main and product_main.select_one("p.price_color") else None
    
    avail_elem = product_main.select_one("p.instock.availability") if product_main else None
    availability_text = " ".join(avail_elem.get_text().split()) if avail_elem else None

    rating_elem = product_main.select_one("p.star-rating") if product_main else None
    rating_text = None
    if rating_elem:
        classes = rating_elem.get("class", [])
        rating_classes = [c for c in classes if c != "star-rating"]
        if rating_classes:
            rating_text = rating_classes[0]

    desc_header = soup.select_one("#product_description")
    desc_elem = desc_header.find_next_sibling("p") if desc_header else None
    description = desc_elem.get_text(strip=True) if desc_elem else None

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def normalize_and_validate(raw_record: dict) -> tuple[Optional[dict], Optional[dict]]:
    # Convert '£51.77' to float 51.77
    raw_price = raw_record.get("price_text") or ""
    match = re.search(r"[\d.]+", raw_price)
    price_gbp = float(match.group()) if match else None

    normalized_candidate = {
        **raw_record,
        "price_gbp": price_gbp,
    }

    try:
        validated = BookRecord(**normalized_candidate)
        # Convert Pydantic model to a standard dict (casting HttpUrl to string)
        return validated.model_dump(mode="json"), None
    except ValidationError as exc:
        return None, {
            "record": raw_record,
            "error": exc.errors(),
        }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    discovered_books = discover_book_urls(START_URL, MAX_CATALOGUE_PAGES)
    
    # Canonical URL deduplication
    seen_urls = set()
    unique_books = []
    for item in discovered_books:
        if item["product_url"] not in seen_urls:
            seen_urls.add(item["product_url"])
            unique_books.append(item)

    print(f"Extracting, normalizing, and validating {len(unique_books)} books...")
    valid_records = []
    error_records = []

    for book in unique_books:
        raw_record = extract_book_details(book["product_url"], book["source_page"])
        valid_doc, error_doc = normalize_and_validate(raw_record)
        
        if valid_doc:
            valid_records.append(valid_doc)
        else:
            error_records.append(error_doc)

    # Save validated records
    books_file = OUTPUT_DIR / "books.json"
    books_file.write_text(json.dumps(valid_records, indent=2), encoding="utf-8")

    # Save error records if any
    if error_records:
        errors_file = OUTPUT_DIR / "errors.json"
        errors_file.write_text(json.dumps(error_records, indent=2), encoding="utf-8")

    print(f"Validated records written to {books_file} : {len(valid_records)}")
    if error_records:
        print(f"Errors written: {len(error_records)}")


if __name__ == "__main__":
    main()