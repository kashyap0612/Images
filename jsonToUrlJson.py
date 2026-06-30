# import json
# import re

# INPUT_FILE = "browser_history.json"          # Your input file
# OUTPUT_FILE = "website_urls.json"  # Output file

# # Read the raw string from the JSON file
# with open(INPUT_FILE, "r", encoding="utf-8") as f:
#     text = json.load(f)

# # Convert escaped characters (\n, \") to normal text
# text = bytes(text, "utf-8").decode("unicode_escape")

# # Remove the Markdown code fences
# text = re.sub(r"```json\s*", "", text)
# text = re.sub(r"```", "", text)
# text = text.strip()

# # Convert the JSON array string into a Python list
# urls = json.loads(text)

# # Save as a proper JSON array
# with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
#     json.dump(urls, f, indent=4)

# print(f"Saved {len(urls)} URLs to {OUTPUT_FILE}")

import json
import re

INPUT_FILE = "browser_history.json"
OUTPUT_FILE = "website_urls.json"

# Read the input JSON
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# Convert everything to a single string
text = json.dumps(data)

# Decode escaped characters (e.g. \n, \")
text = bytes(text, "utf-8").decode("unicode_escape")

# Extract all https URLs
urls = re.findall(r'https://[^\s"\\]+', text)

# Remove duplicates while preserving order
urls = list(dict.fromkeys(urls))

# Save to JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(urls, f, indent=4)

print(f"Found {len(urls)} URLs.")
print(f"Saved to {OUTPUT_FILE}")