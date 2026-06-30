import re
import json

with open("actions_results.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Extract all JSON blocks
json_blocks = re.findall(
    r"```json\s*(.*?)\s*```",
    text,
    re.DOTALL
)

urls = []

def extract_urls(obj):
    if isinstance(obj, dict):
        for value in obj.values():
            extract_urls(value)

    elif isinstance(obj, list):
        for item in obj:
            extract_urls(item)

    elif isinstance(obj, str):
        if obj.startswith(("http://", "https://")):
            urls.append(obj)

for block in json_blocks:
    try:
        data = json.loads(block)
        extract_urls(data)
    except json.JSONDecodeError:
        pass

# Remove duplicates
urls = list(dict.fromkeys(urls))

with open("website_urls.json", "w", encoding="utf-8") as f:
    json.dump(urls, f, indent=4)

print(urls)