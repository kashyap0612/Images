# from playwright.sync_api import sync_playwright

# with sync_playwright() as p:
#     browser = p.chromium.launch(headless=False)

#     page = browser.new_page()

#     page.goto(
#         "https://unsplash.com/s/photos/luxury-car",
#         wait_until="networkidle"
#     )

#     print(page.title())

#     html = page.content()

#     with open("unsplash.html", "w", encoding="utf-8") as f:
#         f.write(html)

#     browser.close()

import json
import os
from playwright.sync_api import sync_playwright

# Load URLs
with open("website_urls.json", "r") as f:
    urls = json.load(f)

os.makedirs("html_pages", exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    for i, url in enumerate(urls, start=1):
        try:
            page = browser.new_page()

            print(f"Opening: {url}")

            page.goto(
                url,
                wait_until="networkidle",
                timeout=60000
            )

            html = page.content()

            with open(
                f"html_pages/page_{i}.html",
                "w",
                encoding="utf-8"
            ) as f:
                f.write(html)

            print(f"Saved page_{i}.html")

            page.close()

        except Exception as e:
            print(f"Error on {url}")
            print(e)

    browser.close()