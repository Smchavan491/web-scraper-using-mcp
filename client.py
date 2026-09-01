import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from groq import Groq
import os
from utils import get_response_from_llm
from dotenv import load_dotenv

load_dotenv()

# Initialize the MCP client session
server_params = StdioServerParameters(
        command="uv",
        args=["run", "main.py"],
        env = None,
    )

# Create a client session

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # Initialize connection with the MCP server
            await session.initialize()


             # Get available tools
            tools = await session.list_tools()
            print("Available tools:")

            for tool in tools.tools:
                print("-", tool.name)
                
            query = "How to used chroma db with langchain"
            library = "langchain"
            res = await session.call_tool(
                "get_docs",
                arguments={"query": query, "library": library},
            )
            print("Result:")
            print(res.content)

            context = res.content
            user_prompt_with_context = f"Query: {query}, Context: {context}"

            # LLM function to create human redable response
            SYSTEM_PROMPT = """
                Answer using only the provided context.
                If there is missing info then say you don't know.
                Keep every 'SOURCE:' line exactly.
                List all sources at the end.
                """
            answer = get_response_from_llm(user_prompt=user_prompt_with_context,system_prompt=SYSTEM_PROMPT,model="openai/gpt-oss-20b")
            print("Answer:", answer)

if __name__ == "__main__":
    asyncio.run(main())