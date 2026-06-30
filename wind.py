import asyncio
import json
from browser_use import Agent, Browser
from browser_use.llm.litellm import ChatLiteLLM

async def main():

    llm = ChatLiteLLM(
        model="ollama/deepseek-r1:32b",
        api_base="http://192.168.43.30:11434"
    )

    browser = Browser(
        headless=False,
        user_data_dir="/Users/tribhuwan01/browser-use-profile"
    )

    agent = Agent(
        task=""" Search for the 10 different goat image websites.
            Return the Website Urls of different tabs,
        Return ONLY valid JSON in this format: 
        { "urls": 
            [ "https://example1.com", "https://example2.com", "https://example3.com", "https://example4.com", "https://example5.com" ] 
            }
             Do not return markdown. 
             Do not return explanations. 
             Do not return anything except JSON. """,
        llm=llm,
        browser=browser
    )

    result = await agent.run()
    history_data = result.model_dump()
    # Save to JSON
    with open("browser_history.json", "w") as f:
        json.dump(history_data, f, indent=4)

    print("History saved to browser_history.json")

asyncio.run(main())