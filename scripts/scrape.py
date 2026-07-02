import json
import time
from playwright.sync_api import sync_playwright

BASE_URL = "https://www.shl.com"

def scrape_all_pages():
    all_assessments = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        start = 0
        while start <= 372:
            url = f"{BASE_URL}/products/product-catalog/?start={start}&type=1"
            print(f"Scraping page start={start} ...")

            page.goto(url, wait_until="networkidle")
            time.sleep(2)  # let JS fully load

            # Get all rows from the Individual Test Solutions table
            rows = page.query_selector_all("table tr")

            if not rows:
                print("  No rows found on this page")
                start += 12
                continue

            found = 0
            for row in rows[1:]:  # skip header
                cols = row.query_selector_all("td")
                if not cols:
                    continue

                name_tag = cols[0].query_selector("a")
                if not name_tag:
                    continue

                name = name_tag.inner_text().strip()
                href = name_tag.get_attribute("href") or ""
                full_url = BASE_URL + href if href.startswith("/") else href
                test_type = cols[-1].inner_text().strip() if len(cols) > 1 else "K"

                all_assessments.append({
                    "name": name,
                    "url": full_url,
                    "description": f"{name} — SHL Individual Test Solution. Test type: {test_type}",
                    "test_type": test_type
                })
                found += 1

            print(f"  Found {found} tests")

            if found == 0:
                print("  Empty page — stopping.")
                break

            start += 12

        browser.close()

    print(f"\nTotal scraped: {len(all_assessments)}")

    with open("data/catalog.json", "w") as f:
        json.dump(all_assessments, f, indent=2)

    print("Saved to data/catalog.json ✅")

if __name__ == "__main__":
    scrape_all_pages()