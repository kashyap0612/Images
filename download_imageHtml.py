import os
import re
import json
from bs4 import BeautifulSoup

HTML_FOLDER = "html_pages"

all_image_urls = set()

for filename in os.listdir(HTML_FOLDER):

    if not filename.endswith(".html"):
        continue

    filepath = os.path.join(HTML_FOLDER, filename)

    print(f"Processing: {filename}")

    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # img tags
    for img in soup.find_all("img"):

        for attr in ["src", "data-src", "data-lazy-src"]:

            url = img.get(attr)

            if url and url.startswith("http"):
                all_image_urls.add(url)

    # preload images
    for link in soup.find_all("link"):

        if link.get("as") == "image":

            href = link.get("href")

            if href:
                all_image_urls.add(href)

    # og:image
    for meta in soup.find_all("meta"):

        if meta.get("property") == "og:image":

            content = meta.get("content")

            if content:
                all_image_urls.add(content)

    # regex search
    pattern = r'https?://[^\s"\']+\.(?:jpg|jpeg|png|webp|svg)'

    for match in re.finditer(pattern, html, re.IGNORECASE):
        all_image_urls.add(match.group(0))

print(f"\nTotal unique images found: {len(all_image_urls)}")

with open("image_urls.json", "w") as f:
    json.dump(list(all_image_urls), f, indent=4)

print("Saved image_urls.json")