import os
from pathlib import Path

folders = [
    "./",
    "html_pages",
]

extensions = [".json", ".txt", ".html"]

for folder in folders:

    if not os.path.exists(folder):
        continue

    for file in Path(folder).glob("*"):

        if file.suffix.lower() in extensions:
            file.unlink()
            print(f"Deleted {file}")

print("Cleanup completed.")