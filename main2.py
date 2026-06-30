import asyncio
from browser_use import Agent
from langchain_ollama import ChatOllama
import os
os.environ["OLLAMA_HOST"] = "https://5644-103-196-217-233.ngrok-free.app/"

llm = ChatOllama(
    model="deepseek-r1:32b",
    temperature=0,
)

async def main():
    agent = Agent(
        task="Open google and find the most expensive car in india",
        llm=llm,
        use_vision=False
    )

    await agent.run()

asyncio.run(main())