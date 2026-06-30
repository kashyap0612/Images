import json
import re

# KEYWORDS = [
#     "goat",
#     "animal"
# ]

with open("image_urls.json", "r", encoding="utf-8") as f:
    data = json.load(f)

filtered_urls = []

for item in data:

    result_text = item.get("result", "")

    urls = re.findall(
        r'https?://[^"\',\s]+',
        result_text
    )

    for url in urls:

        url_lower = url.lower()

        # if any(
        #     keyword.lower() in url_lower
        #     for keyword in KEYWORDS
        # ):
        filtered_urls.append(url)

# Remove duplicates
filtered_urls = list(dict.fromkeys(filtered_urls))

with open(
    "filtered_image_urls.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        filtered_urls,
        f,
        indent=4
    )

print(
    f"Saved {len(filtered_urls)} matching URLs"
)