# The Polite Scraper

A respectful, deterministic scraping pipeline that extracts structured book data from the Books to Scrape sandbox.

## Target Classification

- **Target Site:** Books to Scrape (`https://books.toscrape.com/`)
- **Purpose & Permission:** The site explicitly states on its homepage that it is an open playground and sandbox built specifically for practicing web scraping[cite: 8].
- **Scope:** Exactly the first 3 catalogue pages (60 books total)[cite: 8].
- **Data Collected:** Book title, product URL, price, availability status, star rating, product description, source page URL, and fetch timestamp[cite: 8].
- **Robots.txt Result:** A request to `https://books.toscrape.com/robots.txt` returns HTTP `404` (no robots file found)[cite: 8].
- **Politeness Pledge:** "I will not reuse this code on another site without checking its rules and terms first."[cite: 8]
