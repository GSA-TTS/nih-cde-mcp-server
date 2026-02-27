import json
from fastmcp import FastMCP
from cde.models import GetDataElementInput, SearchDataElementsInput
from cde.utils import _make_cde_request, _make_cde_post_request, _handle_api_error


def register_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="cde_get_data_element",
        annotations={
            "title": "Get CDE Data Element by TinyId",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def cde_get_data_element(params: GetDataElementInput) -> str:
        """Retrieve a NIH Common Data Element (CDE) by its tinyId.

        Fetches detailed metadata for a single CDE from the NIH CDE Repository,
        including its designations, definitions, value domain, classification,
        registration status, and associated concepts.

        Args:
            params (GetDataElementInput): Validated input parameters containing:
                - tinyId (str): The unique tinyId identifier for the CDE
                  (e.g., 'PDjBiGXjO')

        Returns:
            str: JSON-formatted string containing the CDE record with the
            following key fields:

            {
                "tinyId": str,               # Short unique identifier
                "elementType": str,          # Always "cde"
                "designations": [            # Names/labels for this element
                    {
                        "designation": str,  # The name text
                        "tags": [str],       # Role tags (e.g., "Preferred Question Text")
                        "sources": [str]     # Source organization(s)
                    }
                ],
                "definitions": [             # Definitions of the element
                    {
                        "definition": str,
                        "tags": [str],
                        "sources": [str]
                    }
                ],
                "valueDomain": {
                    "datatype": str,         # e.g., "Number", "Text", "Date"
                    "permissibleValues": []  # Allowed values if enumerated
                },
                "registrationState": {
                    "registrationStatus": str,   # e.g., "Qualified", "Standard"
                    "administrativeStatus": str  # e.g., "Published"
                },
                "nihEndorsed": bool,         # Whether NIH has endorsed this CDE
                "stewardOrg": {"name": str}, # Owning organization
                "classification": [...],     # Org classification tree
                "dataElementConcept": {      # Underlying scientific concept
                    "concepts": [
                        {
                            "name": str,
                            "origin": str,    # e.g., "NCI Thesaurus"
                            "originId": str   # e.g., "C25150"
                        }
                    ]
                },
                "properties": [              # Key-value metadata pairs
                    {"key": str, "value": str}
                ],
                "created": str,              # ISO 8601 timestamp
                "updated": str              # ISO 8601 timestamp
            }

            Error response:
            "Error: <error message>"

        Examples:
            - Use when: "Get the CDE for PDjBiGXjO" -> params with tinyId="PDjBiGXjO"
            - Use when: "Look up CDE details for tinyId X9kPmQr2w"
            - Don't use when: You need to search CDEs by keyword (use cde_search instead)
        """
        try:
            data = await _make_cde_request(f"/de/{params.tinyId}")
            return json.dumps(data, indent=2)
        except Exception as e:
            return _handle_api_error(e)

    @mcp.tool(
        name="cde_search_data_elements",
        annotations={
            "title": "Search NIH CDE Repository",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def cde_search_data_elements(params: SearchDataElementsInput) -> str:
        """Search the NIH CDE Repository for Common Data Elements (CDEs).

        Performs a keyword and/or filtered search across the NIH CDE Repository.
        Supports filtering by organization, registration status, datatype, and
        NIH endorsement. Results are paginated.

        Args:
            params (SearchDataElementsInput): Validated input parameters containing:
                - searchTerm (Optional[str]): Keyword(s) to search (e.g., 'blood pressure')
                - page (int): Page number, 1-indexed (default: 1)
                - resultPerPage (int): Results per page, 1-100 (default: 20)
                - nihEndorsed (Optional[bool]): Restrict to NIH-endorsed CDEs only
                - selectedOrg (Optional[str]): Filter by steward org (e.g., 'NINDS', 'NCI')
                - selectedOrgAlt (Optional[str]): Secondary org filter
                - selectedStatuses (Optional[List[str]]): Filter by registration status;
                  valid values: 'Qualified', 'Standard', 'Candidate', 'Recorded',
                  'Preferred Standard'
                - selectedDatatypes (Optional[List[str]]): Filter by value domain datatype;
                  valid values: 'Date', 'Number', 'Text', 'Value List', 'File',
                  'Geo Location', 'Time', 'Externally Defined'
                - selectedElements (Optional[List[str]]): Filter to specific tinyIds
                - selectedElementsAlt (Optional[List[str]]): Secondary tinyId filter
                - excludeOrgs (Optional[List[str]]): Org names to exclude
                - excludeAllOrgs (Optional[bool]): Exclude all org-owned CDEs

        Returns:
            str: JSON-formatted string with the following schema:

            {
                "resultsTotal": int,       # Total matching CDEs across all pages
                "resultsRetrieved": int,   # Number of CDEs in this response
                "from": int,               # 1-based index of first result
                "page": int,               # Current page number
                "resultPerPage": int,      # Page size used
                "has_more": bool,          # Whether additional pages exist
                "docs": [                  # Array of CDE records
                    {
                        "tinyId": str,
                        "elementType": str,      # "cde"
                        "designations": [...],   # Names/labels
                        "definitions": [...],    # Definitions
                        "valueDomain": {
                            "datatype": str,
                            "permissibleValues": [...]
                        },
                        "registrationState": {
                            "registrationStatus": str,
                            "administrativeStatus": str
                        },
                        "nihEndorsed": bool,
                        "stewardOrg": {"name": str},
                        "created": str,
                        "updated": str
                    }
                ]
            }

            Error response:
            "Error: <error message>"

        Examples:
            - Use when: "Search for CDEs about blood pressure"
              -> params with searchTerm="blood pressure"
            - Use when: "Find NIH-endorsed CDEs for diabetes from NINDS"
              -> params with searchTerm="diabetes", nihEndorsed=True, selectedOrg="NINDS"
            - Use when: "Show me page 2 of Value List CDEs"
              -> params with selectedDatatypes=["Value List"], page=2
            - Don't use when: You have a tinyId and need full details
              (use cde_get_data_element instead)
        """
        try:
            body = params.model_dump(exclude_none=True)
            data = await _make_cde_post_request("/de/search", body)
            result = {
                "resultsTotal": data.get("resultsTotal", 0),
                "resultsRetrieved": data.get("resultsRetrieved", 0),
                "from": data.get("from", 1),
                "page": params.page,
                "resultPerPage": params.resultPerPage,
                "has_more": data.get("resultsTotal", 0) > (params.page * params.resultPerPage),
                "docs": data.get("docs", []),
            }
            return json.dumps(result, indent=2)
        except Exception as e:
            return _handle_api_error(e)
