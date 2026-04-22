"""Web search tool using DuckDuckGo."""

import asyncio

from ddgs import DDGS

from src.tools import ToolResult


class WebSearchTool:
    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return (
            "Search the web for current information. "
            "Use this when you need up-to-date facts, news, or information not in your training data."
        )

    def __init__(self, max_results: int = 2):
        self._max_results = max_results

    async def execute(self, query: str) -> ToolResult:
        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, lambda: DDGS().text(query, max_results=self._max_results, backend="google")
            )
            if not results:
                return ToolResult(success=True, result="No search results found.")

            formatted = []
            for r in results:
                formatted.append(
                    f"- {r.get('title', 'No title')}\n"
                    f"  {r.get('url', '')}\n"
                    f"  {r.get('body', 'No description')[:200]}"
                )

            return ToolResult(success=True, result="\n\n".join(formatted))
        except Exception as e:
            return ToolResult(success=False, result=None, error=str(e))
