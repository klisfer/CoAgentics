# # backend/tools/web_search_tool.py
# from tavily import TavilyClient
# import os

# def search(query: str) -> str:
#     """
#     Performs a web search for a given query and returns a concise summary of the results.
    
#     Args:
#         query: The search query.
        
#     Returns:
#         A summary of the search results.
#     """
#     try:
#         api_key = os.environ["TAVILY_API_KEY"]
#         client = TavilyClient(api_key=api_key)
#         response = client.search(query=query, search_depth="basic")
#         if response.get('results'):
#             return response['results'][0]['content']
#         return "No search results found."
#     except KeyError:
#         return "Error: TAVILY_API_KEY environment variable not set."
#     except Exception as e:
#         return f"An error occurred during web search: {e}" 