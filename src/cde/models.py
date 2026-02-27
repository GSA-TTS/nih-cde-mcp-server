from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class GetDataElementInput(BaseModel):
    """Input model for retrieving a CDE by tinyId."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    tinyId: str = Field(
        ...,
        description="The tinyId identifier for the Common Data Element (e.g., 'PDjBiGXjO')",
        min_length=1,
        max_length=50,
    )


class SearchDataElementsInput(BaseModel):
    """Input model for searching CDEs."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    searchTerm: Optional[str] = Field(
        default=None,
        description="Keyword(s) to search across CDE names, definitions, and metadata (e.g., 'blood pressure')",
    )
    page: int = Field(
        default=1,
        description="Page number for pagination (1-indexed)",
        ge=1,
    )
    resultPerPage: int = Field(
        default=20,
        description="Number of results to return per page",
        ge=1,
        le=100,
    )
    nihEndorsed: Optional[bool] = Field(
        default=None,
        description="If true, restrict results to NIH-endorsed CDEs only",
    )
    selectedOrg: Optional[str] = Field(
        default=None,
        description="Filter by steward organization name (e.g., 'NINDS', 'NCI')",
    )
    selectedOrgAlt: Optional[str] = Field(
        default=None,
        description="Secondary organization filter",
    )
    selectedStatuses: Optional[List[str]] = Field(
        default=None,
        description=(
            "Filter by registration status. Valid values: "
            "'Qualified', 'Standard', 'Candidate', 'Recorded', 'Preferred Standard'"
        ),
    )
    selectedDatatypes: Optional[List[str]] = Field(
        default=None,
        description=(
            "Filter by value domain datatype. Valid values: "
            "'Date', 'Number', 'Text', 'Value List', 'File', 'Geo Location', 'Time', 'Externally Defined'"
        ),
    )
    selectedElements: Optional[List[str]] = Field(
        default=None,
        description="Filter to CDEs belonging to specific tinyIds",
    )
    selectedElementsAlt: Optional[List[str]] = Field(
        default=None,
        description="Secondary element filter by tinyIds",
    )
    excludeOrgs: Optional[List[str]] = Field(
        default=None,
        description="List of organization names to exclude from results",
    )
    excludeAllOrgs: Optional[bool] = Field(
        default=None,
        description="If true, exclude CDEs owned by any organization",
    )
