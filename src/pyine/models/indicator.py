"""Pydantic models for INE indicators and dimensions."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DimensionValue(BaseModel):
    """Single dimension value/category.

    Represents a specific value that can be used to filter data
    along a particular dimension (e.g., a specific year, region, or category).
    """

    code: str = Field(..., description="Dimension value code")
    label: str = Field(..., description="Human-readable label")
    order: Optional[int] = Field(None, description="Display order")


class Dimension(BaseModel):
    """Dimension definition for an indicator.

    Dimensions allow filtering and organizing statistical data
    (e.g., time period, geographic region, demographic category).
    """

    id: int = Field(..., description="Dimension identifier")
    name: str = Field(..., description="Dimension name")
    description: Optional[str] = Field(None, description="Dimension description")
    values: List[DimensionValue] = Field(default_factory=list, description="Available values")


class Indicator(BaseModel):
    """Indicator metadata from INE catalogue.

    Represents a statistical indicator with its metadata including
    title, description, theme classification, and update information.
    """

    varcd: str = Field(..., description="Indicator code (e.g., '0004167')")
    title: str = Field(..., description="Indicator title")
    description: Optional[str] = Field(None, description="Detailed description")
    theme: Optional[str] = Field(None, description="Primary theme")
    subtheme: Optional[str] = Field(None, description="Sub-theme")
    keywords: List[str] = Field(default_factory=list, description="Search keywords")
    periodicity: Optional[str] = Field(None, description="Update frequency")
    last_period: Optional[str] = Field(None, description="Last data period")
    last_update: Optional[datetime] = Field(None, description="Last update timestamp")
    geo_last_level: Optional[str] = Field(None, description="Geographic detail level")
    unit: Optional[str] = Field(None, description="Unit of measurement")

    # API URLs
    html_url: Optional[str] = Field(None, description="Web page URL")
    metadata_url: Optional[str] = Field(None, description="Metadata API URL")
    data_url: Optional[str] = Field(None, description="Data API URL")
    source: Optional[str] = Field(None, description="Data source")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "varcd": "0004167",
                "title": "Resident population",
                "description": "Annual resident population estimates",
                "theme": "Population",
                "keywords": ["population", "residents", "demographics"],
                "periodicity": "Annual",
                "last_period": "2023",
            }
        }
    )


class IndicatorMetadata(BaseModel):
    """Complete metadata for an indicator including dimensions.

    Extends basic indicator information with dimension definitions
    and other metadata required for data queries.
    """

    indicator_code: str = Field(..., description="Indicator code")
    indicator_name: str = Field(..., description="Indicator name")
    language: str = Field(..., description="Language (PT or EN)")
    dimensions: List[Dimension] = Field(default_factory=list, description="Available dimensions")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    source: Optional[str] = Field(None, description="Data source")
    notes: Optional[str] = Field(None, description="Additional notes")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "indicator_code": "0004167",
                "indicator_name": "Resident population",
                "language": "EN",
                "dimensions": [
                    {
                        "id": 1,
                        "name": "Period",
                        "values": [
                            {"code": "2020", "label": "2020"},
                            {"code": "2021", "label": "2021"},
                        ],
                    }
                ],
            }
        }
    )
