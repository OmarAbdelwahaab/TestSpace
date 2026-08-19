# The Polite Scraper

A robust, respectful Python scraping pipeline that extracts structured book data across the first 3 catalogue pages of Books to Scrape.

---

## Target Classification

* **Target Site:** Books to Scrape (`[https://books.toscrape.com/](https://books.toscrape.com/)`)
* **Target Purpose:** An open sandbox built explicitly for testing and learning web scraping.
* **Scope:** Exactly the first 3 catalogue pages (60 books total)[cite: 8].
* **Robots Exclusion:** `[https://books.toscrape.com/robots.txt](https://books.toscrape.com/robots.txt)` returns HTTP `404` (no exclusion directives found)[cite: 8].
* **Politeness Pledge:** *"I will not reuse this code on another site without checking its rules and terms first."*[cite: 8]

---

## Quick Start

1. Navigate to the scraper directory:
   ```bash
   cd scraper
   ```
2. Set up a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Run the pipeline:
   ```bash
   python src/main.py
   ```

---

## Data Schema

Every record is validated with Pydantic against this structure before saving to `output/books.json`[cite: 8]:

| Field | Type | Description |
|---|---|---|
| `title` | `str` | Book title extracted from the product heading[cite: 8] |
| `product_url` | `HttpUrl` | Canonical, absolute URL of the product detail page[cite: 8] |
| `price_text` | `str` | Raw price string as displayed on the page (e.g., `"£51.77"`)[cite: 8] |
| `price_gbp` | `float` | Cleaned, numeric price value for sorting and calculations (e.g., `51.77`)[cite: 8] |
| `availability_text` | `str` | Raw inventory status string (e.g., `"In stock (22 available)"`)[cite: 8] |
| `rating_text` | `Optional[str]` | Star rating string (`"One"`, `"Two"`, `"Three"`, etc.)[cite: 8] |
| `description` | `Optional[str]` | Cleaned product description or `null` if omitted[cite: 8] |
| `source_page` | `HttpUrl` | Absolute URL of the catalogue page where the item was discovered[cite: 8] |
| `fetched_at` | `str` | ISO 8601 UTC timestamp recording data provenance[cite: 8] |

---

## Politeness Policies

* **Honest User-Agent:** Requests identify themselves with `FlyRankInternship-A9/1.0 (+[https://github.com/your-username/your-repo](https://github.com/your-username/your-repo))`[cite: 8].
* **Rate Limiting:** Enforces a minimum 500ms delay between live network requests[cite: 8].
* **Defensive Timeouts:** All HTTP requests enforce a strict 10-second timeout[cite: 8].
* **Disk Caching:** All fetched HTML is cached locally in `cache/` during development to eliminate redundant load on the host[cite: 8].
* **No-Browser Architecture:** The website renders all content directly in static HTML from the server; using a headless browser (like Playwright or Selenium) would add unnecessary memory and CPU cost without providing any benefit[cite: 8].

---

## Run Report Evidence

Sample execution output recorded in `output/run-report.json`[cite: 8]:

```json
{
  "start_time": "2026-08-19T17:28:00.000000+00:00",
  "end_time": "2026-08-19T17:28:03.250000+00:00",
  "duration_seconds": 3.25,
  "pages_fetched": 0,
  "cache_hits": 63,
  "failed_pages": 1,
  "valid_records": 60,
  "invalid_records": 0
}
```

---

## Known Limitations

* **Sequential Execution:** Requests are dispatched serially; scaling beyond small catalogues would require an asynchronous worker pool or task queue[cite: 8].
* **DOM Structure Dependency:** Extraction relies on specific CSS classes (`.product_main`, `.price_color`); structural layout changes on the site would require updating the extraction selectors[cite: 8].

---

## Ethics Note

* Prefer official REST/GraphQL APIs whenever provided by the platform[cite: 8].
* Always review and respect `robots.txt` directives and site terms of service[cite: 8].
* Never bypass authentication barriers, paywalls, or rate-limiting measures[cite: 8].
* Collect only the specific data fields required by your application[cite: 8].