import httpx

CDE_API_BASE_URL = "https://cde.nlm.nih.gov/api"


async def _make_cde_request(path: str) -> dict:
    """Reusable function for CDE API GET calls."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{CDE_API_BASE_URL}{path}",
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


async def _make_cde_post_request(path: str, body: dict) -> dict:
    """Reusable function for CDE API POST calls."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{CDE_API_BASE_URL}{path}",
            json=body,
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


def _handle_api_error(e: Exception) -> str:
    """Consistent error formatting across all tools."""
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 404:
            return "Error: CDE not found. Please check that the tinyId is correct."
        elif e.response.status_code == 429:
            return "Error: Rate limit exceeded. Please wait before making more requests."
        return f"Error: API request failed with status {e.response.status_code}"
    elif isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Please try again."
    return f"Error: Unexpected error occurred: {type(e).__name__}"
