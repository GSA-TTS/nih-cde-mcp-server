import httpx
from typing import Dict, Any, List

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

def trim_cde_search_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Trim NIH CDE search response to keep:
      - search metadata
      - for each result:
            stewardOrg
            NIH_Endorsed
            tinyID
            designation
            definition
            sourceName
    """

    # Preserve top-level metadata
    trimmed_response = {
        "resultsTotal": response.get("resultsTotal"),
        "resultsRetrieved": response.get("resultsRetrieved"),
        "from": response.get("from"),
        "page": response.get("page"),
        "resultPerPage": response.get("resultPerPage"),
        "has_more": response.get("has_more"),
        "docs": []
    }

    docs = response.get("docs", [])

    for doc in docs:
        # stewardOrg name
        steward_name = None
        if isinstance(doc.get("stewardOrg"), dict):
            steward_name = doc["stewardOrg"].get("name")

        # first definition
        definition_text = None
        definitions = doc.get("definitions", [])
        if definitions and isinstance(definitions, list):
            definition_text = definitions[0].get("definition")

        # first designation
        designation_text = None
        designations = doc.get("designations", [])
        if designations and isinstance(designations, list):
            designation_text = designations[0].get("designation")

        # all source names
        source_names: List[str] = []
        for source in doc.get("sources", []):
            if isinstance(source, dict) and "sourceName" in source:
                source_names.append(source["sourceName"])

        trimmed_doc = {
            "stewardOrg": steward_name,
            "NIH_Endorsed": doc.get("NIH_Endorsed"),
            "tinyID": doc.get("tinyId"),  # normalize casing
            "designation": designation_text,
            "definition": definition_text,
            "sourceName": source_names
        }

        trimmed_response["docs"].append(trimmed_doc)

    return trimmed_response
