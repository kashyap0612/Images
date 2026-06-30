import json
import requests
import os

# Load file
with open("browser_history.json", "r") as f:
    data = json.load(f)

# Create folder
os.makedirs("downloaded_images", exist_ok=True)

# Extract tabs
tabs = data["history"][0]["state"]["tabs"]

count = 1

for tab in tabs:

    url = tab["url"]

    # Download only direct image links
    if url.endswith((".jpg", ".jpeg", ".png", ".webp")):

        try:
            response = requests.get(url)

            if response.status_code == 200:

                extension = url.split(".")[-1]

                filename = f"downloaded_images/image_{count}.{extension}"

                with open(filename, "wb") as img:
                    img.write(response.content)

                print(f"Downloaded: {filename}")

                count += 1

        except Exception as e:
            print("Error:", e)