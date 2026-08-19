import os
import requests
from pathlib import Path

CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
PAGE_1_URL = "https://books.toscrape.com/catalogue/page-1.html"

# Polite robot headers with an honest User-Agent
HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/your-username/your-repo)"
}
TIMEOUT_SECONDS = 10


def fetch_and_cache(url: str, cache_file_name: str) -> str:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / cache_file_name

    # Check local cache first
    if cache_path.exists():
        html_content = cache_path.read_text(encoding="utf-8")
        print(f"[CACHE HIT] Read {len(html_content)} bytes from {cache_path.name}")
        return html_content

    # Polite fetch with status checking and timeout
    print(f"[FETCH] Requesting {url}...")
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS)

    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to fetch {url}. Status code: {response.status_code}"
        )

    html_content = response.text
    cache_path.write_text(html_content, encoding="utf-8")
    print(f"[SAVED] {len(html_content)} bytes written to {cache_path.name}")

    return html_content


def main():
    fetch_and_cache(PAGE_1_URL, "catalogue-page-1.html")


if __name__ == "__main__":
    main()