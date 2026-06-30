import asyncio
import json
import os

from browser_use import Agent
from langchain_ollama import ChatOllama


os.environ["OLLAMA_HOST"] = "http://192.168.43.30:11434"
# os.environ["OLLAMA_HOST"] = "https://d6be-103-196-217-233.ngrok-free.app/"

llm = ChatOllama(
    model="deepseek-r1:32b",
    # model="qwen3.6:35b",
    temperature=0,
)

async def main():
    agent = Agent(
        # task="get all the news about the umar khalid form everywhere like news channels, google and different sources",
        task=""" Search for the 10 different goat image websites.
        Return ONLY valid JSON in this format: 
        { "urls": 
            [ "https://example1.com", "https://example2.com", "https://example3.com", "https://example4.com", "https://example5.com" ] 
            }
             Do not return markdown. 
             Do not return explanations. 
             Do not return anything except JSON. """,
        llm=llm,
        use_vision=True
    )

    # Run the agent
    result = await agent.run()

    # Full history data
    # history_data = agent.history.model_dump()
    history_data = result.model_dump()
    # Save to JSON 
    with open("browser_history.json", "w") as f:
        json.dump(history_data, f, indent=4)

    print("History saved to browser_history.json")

asyncio.run(main())



# export OLLAMA_HOST=http://192.168.43.30:11434