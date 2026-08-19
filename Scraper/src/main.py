import time
import requests
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup

CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
START_URL = "https://books.toscrape.com/catalogue/page-1.html"
MAX_CATALOGUE_PAGES = 3

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/your-username/your-repo)"
}
TIMEOUT_SECONDS = 10
REQUEST_DELAY_SECONDS = 0.5


def fetch_and_cache(url: str, cache_file_name: str) -> tuple[str, bool]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / cache_file_name

    if cache_path.exists():
        html_content = cache_path.read_text(encoding="utf-8")
        print(f"[CACHE HIT] {cache_path.name} ({len(html_content)} bytes)")
        return html_content, True

    # Politeness delay for live network requests
    time.sleep(REQUEST_DELAY_SECONDS)

    print(f"[FETCH] Requesting {url}...")
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS)

    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch {url}. Status code: {response.status_code}")

    html_content = response.text
    cache_path.write_text(html_content, encoding="utf-8")
    print(f"[SAVED] {cache_path.name} ({len(html_content)} bytes)")

    return html_content, False


def discover_book_urls(start_url: str, max_pages: int = 3) -> tuple[list[str], int]:
    current_url = start_url
    pages_crawled = 0
    all_book_urls = []

    while current_url and pages_crawled < max_pages:
        pages_crawled += 1
        cache_filename = f"catalogue-page-{pages_crawled}.html"
        html_content, _ = fetch_and_cache(current_url, cache_filename)

        soup = BeautifulSoup(html_content, "html.parser")

        # Extract all book links from product cards
        product_pods = soup.select("article.product_pod h3 a")
        for link in product_pods:
            relative_href = link.get("href")
            absolute_url = urljoin(current_url, relative_href)
            all_book_urls.append(absolute_url)

        # Follow the "next" page link
        next_button = soup.select_one("li.next a")
        if next_button:
            next_href = next_button.get("href")
            current_url = urljoin(current_url, next_href)
        else:
            current_url = None

    return all_book_urls, pages_crawled


def main():
    book_urls, pages_count = discover_book_urls(START_URL, MAX_CATALOGUE_PAGES)
    unique_urls = list(dict.fromkeys(book_urls))

    print(
        f"catalogue_pages = {pages_count}, "
        f"discovered = {len(book_urls)}, "
        f"unique_urls = {len(unique_urls)}"
    )


if __name__ == "__main__":
    main()