from tavily import TavilyClient

import os

client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))


def search(query):
    """Search the internet for query.

    Args:
        query: Search terms to look for
    """
    response = client.search(
        query = query,
        max_results = 5,
        include_raw_content = False
        )
    
    # print(f"Search Response - {response}")
    return response