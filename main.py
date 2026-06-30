import subprocess
import os
scripts = [
    # "saveJson.py",
    # "extract_text.py",
    # "textToJsonUrl.py",
    "playwright_main_html.py",
    "jsonToUrlJson.py",
    "2_beautifulSoap1.py",
    "download_imageHtml.py",
    "imageDown.py",
    "deleteFile.py",
    "CLIPmodel.py"
    
]

query = "camel pdf"

for script in scripts:

    print(f"\nRunning {script}")

    result = subprocess.run(
        ["python", script, query]
    )

    if result.returncode != 0:
        print(f"Failed at {script}")
        break

print("\nPipeline Completed")
