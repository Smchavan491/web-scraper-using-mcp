import json
import os
import httpx
import asyncio
from utils import clean_html_to_text
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("docs")

SERPER_API_URL = "https://google.serper.dev/search"

async def web_search(query: str)->dict | None:
    payload = json.dumps({"q": query,"num": 2})
    headers = {
    'X-API-KEY': os.getenv("SERPER_API_KEY"),
    'Content-Type': 'application/json'
    }


    async with httpx.AsyncClient() as client:
        response = await client.post(
            SERPER_API_URL, data=payload, headers=headers, timeout=30.0
        )
        response.raise_for_status()
        return response.json()
        



# step 2: convert html to text using trafilatura
async def fetch_url(url: str) -> str | None:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            cleaned_response = clean_html_to_text(response.text)
            return cleaned_response
    except (httpx.HTTPError, httpx.TimeoutException) as e:
        print(f"Failed to fetch {url}: {e}")
        return None


# Step3: Read documentation and write code accordingly

docs_urls = {
    "langchain": "docs.langchain.com",
    "llama-index": "docs.llamaindex.ai",
    "openai": "platform.openai.com/docs",
    "uv": "docs.astral.sh/uv",
}
@mcp.tool()
async def get_docs(query:str, library: str):
    """
    Search the latest docs for a given query and library.
    Supports langchain, openai, llama-index and uv.

    Args:
        query: The query to search for (e.g. "Publish a package with UV")
        library: The library to search in (e.g. "uv")

    Returns:
        Summarized text from the docs with source links.
    """
    if library not in docs_urls:
        raise ValueError(f"Library '{library}' is not supported." )

    query = f"site:{docs_urls[library]} {query}"
    results = await web_search(query) 

    if not results or "organic" not in results or len(results["organic"]) == 0:
        return "Not found"

    links = [result.get("link", "") for result in results["organic"]]

    # Fetch all URLs concurrently instead of one at a time
    fetched_pages = await asyncio.gather(
        *[fetch_url(link) for link in links], return_exceptions=True
    )

    text_parts = []
    for link, raw in zip(links, fetched_pages):
        if isinstance(raw, Exception) or not raw:
            continue
        labled = f"SOURCE: {link}\n\n{raw}"
        text_parts.append(labled)

    if not text_parts:
        return "Not found"
    return "\n\n".join(text_parts)

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__": 
    main()