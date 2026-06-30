import asyncio
import os

from browser_use import Agent
from langchain_ollama import ChatOllama

os.environ["OLLAMA_HOST"] = "http://192.168.43.30:11434"

llm = ChatOllama(
    model="deepseek-r1:32b",
    temperature=0
)

async def main():
    agent = Agent(
        task = """
            Go to cardekho.com.

            Search for cars.

            Find 5 red hyundai car images.
            save the html of 5 different cars page. 

            Do not return anything else.""",
        llm=llm,
        use_vision=False
    )

    await agent.run()

    # Get the current Playwright page
    page = await agent.browser_context.get_current_page()

    # Extract rendered HTML
    html = await page.content()

    with open("website.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("HTML saved successfully")

asyncio.run(main())