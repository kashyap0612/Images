import json
import base64
import os

# Load JSON file
with open("browser_history.json", "r") as f:
    data = json.load(f)

# Create output folder
os.makedirs("screenshots", exist_ok=True)

# Extract screenshots
history = data.get("history", [])

for i, step in enumerate(history):
    screenshot_base64 = step.get("state", {}).get("screenshot")

    if screenshot_base64:
        image_data = base64.b64decode(screenshot_base64)

        filename = f"screenshots/step_{i+1}.png"

        with open(filename, "wb") as img_file:
            img_file.write(image_data)

        print(f"Saved: {filename}")