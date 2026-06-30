from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json

HTML_FILE = "html/google_search.html"
OUTPUT_FILE = "website_urls.json"

with open(HTML_FILE, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

urls = []
seen = set()

for a in soup.find_all("a", href=True):

    href = a["href"]

    # Google search results look like:
    # /url?q=https://unsplash.com/s/photos/red-car&sa=...

    if href.startswith("/url?q="):

        real_url = href.split("/url?q=")[1].split("&")[0]

        domain = urlparse(real_url).netloc

        # Skip Google URLs
        if "google." in domain:
            continue

        if real_url not in seen:
            seen.add(real_url)
            urls.append(real_url)

# Keep only the first 10 websites
urls = urls[:10]

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(urls, f, indent=4)

print(f"Saved {len(urls)} website URLs.")
