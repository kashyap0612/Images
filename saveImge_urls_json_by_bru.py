import asyncio
import json
from browser_use import Agent
from langchain_ollama import ChatOllama

llm = ChatOllama(
     model="deepseek-r1:32b",
    temperature=0
)

async def main():

    with open("website_urls.json", "r") as f:
        urls = json.load(f)

    results = []

    for url in urls:

        print(f"Processing: {url}")

        agent = Agent(
            task=f"""
            Open this URL:

            {url}

            Extract all image URLs visible on the page.

            Return ONLY JSON:

            {{
                "image_urls": [
                    "url1",
                    "url2"
                ]
            }}
            """,
            llm=llm
        )

        result = await agent.run()

        results.append({
            "page_url": url,
            "result": str(result)
        })

    with open("image_urls.json", "w") as f:
        json.dump(results, f, indent=4)

    print("Done")

asyncio.run(main())