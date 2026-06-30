import asyncio
import json
from urllib.parse import quote
import os
import sys

from playwright.async_api import async_playwright
from langchain_ollama import ChatOllama
os.environ["OLLAMA_HOST"] = "http://192.168.43.30:11434"

query = sys.argv[1]

subquery = f"{query} pdf"

llm = ChatOllama(
    model="deepseek-r1:32b",
    temperature=0
)


async def get_links():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=False
        )

        page = await browser.new_page()

        await page.goto(
            f"https://www.google.com/search?q={quote(subquery)}",
            wait_until="networkidle",
            timeout=60000
        )

        print("Solve CAPTCHA if it appears.")
        input("Press ENTER after Google search results are visible...")

        links = await page.evaluate("""
        () => {
            return [...document.querySelectorAll("a")]
                .map(a => a.href)
                .filter(href => href.startsWith("http"));
        }
        """)

        await browser.close()

        # remove duplicates
        links = list(dict.fromkeys(links))

        return links


async def main():

    links = await get_links()

    print(f"Extracted {len(links)} links")

    prompt = f"""
You are given a list of URLs extracted from a Google Search page.

Search Query:
{subquery}

Remove:

- Google URLs
- Cache URLs
- Translate URLs
- Maps URLs
- Ads
- Login pages
- Tracking URLs
- Image URLs

Keep only the website URLs that are relevant to the search query.

Return ONLY valid JSON.

Example:

[
    "https://unsplash.com/s/photos/red-car",
    "https://www.pexels.com/search/red-car/",
    "https://pixabay.com/images/search/red-car/"
]

URLs:

# {json.dumps(links, indent=2)}
"""

    response = llm.invoke(prompt)

    print(response.content)

    history_data = response.content
    # Save to JSON 
    with open("browser_history.json", "w") as f:
        json.dump(history_data, f, indent=4)

    print("History saved to browser_history.json")





asyncio.run(main()) 