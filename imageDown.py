import json
import requests
import os
import sys

query = sys.argv[1]

subquery = query.replace(" ", "_")

# Load image URLs
with open("image_urls.json", "r") as f:
    urls = json.load(f)

os.makedirs(subquery, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0"
}

count = 0

for url in urls:
    # Skip unwanted images
    if any(x in url.lower() for x in [
        "profile-",
        "favicon",
        "apple-touch-icon",
        "opengraph",
        ".svg",
        "adzerk",
        "crop=faces"
    ]):
        continue

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30,
            stream=True
        )

        if response.status_code == 200:

            ext = ".jpg"

            if ".webp" in url:
                ext = ".webp"
            elif ".png" in url:
                ext = ".png"

            filename = f"{subquery}/image_{count+1}{ext}"

            with open(filename, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            count += 1
            print(f"Downloaded {filename}")

    except Exception as e:
        print(f"Failed: {url}")
        print(e)

print(f"\nTotal downloaded: {count}")