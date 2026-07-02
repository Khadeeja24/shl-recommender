from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    page.goto("https://www.shl.com/products/product-catalog/?start=0&type=1", wait_until="networkidle")
    
    # Print page title
    print("Title:", page.title())
    
    # Print full HTML to see structure
    html = page.content()
    print("\nHTML preview (first 3000 chars):")
    print(html[:3000])
    
    browser.close()