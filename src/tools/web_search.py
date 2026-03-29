"""Web search tool using DuckDuckGo."""

from ddgs import DDGS
from base import Tool, ToolResult, ToolParams

class SearchParams(ToolParams):
    query: str

class WebSearchTool(Tool):
    def __init__ (self, max_results: int=2):
        self._max_results = max_results

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return (
            "Search the web for current information. "
            "Use this when you need up-to-date facts, news, or information not in your training data."
        )

    @property
    def params_class(self) -> type[ToolParams]:
        return SearchParams

    async def execute(self, params: ToolParams) -> ToolResult:
        assert isinstance(params, SearchParams)
        try:
            results = DDGS().text(
                params.query,
                max_results=self._max_results,
                backend="google",
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

            return ToolResult.ok(result="\n\n".join(formatted))
        except Exception as e:
            return ToolResult.fail(error=str(e))
