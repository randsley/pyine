from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from pyine.models.indicator import Indicator
from pyine.processors.csv import export_to_csv
from pyine.processors.json import export_to_json

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class DataPoint(BaseModel):
    """Single data point from INE API.

    Represents one observation with its dimension values and the measured value.
    """

    value: Optional[float] = Field(None, description="Measured value")
    dimensions: Dict[str, str] = Field(default_factory=dict, description="Dimension values")
    unit: Optional[str] = Field(None, description="Unit of measurement")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "value": 10295909.0,
                "dimensions": {"Period": "2021", "Geographic localization": "Portugal"},
                "unit": "No.",
            }
        }
    )


class DataResponse(BaseModel):
    """Wrapper for data API response.

    Contains the indicator data along with metadata about the indicator
    and when the data was retrieved.
    """

    varcd: str = Field(..., description="Indicator code")
    title: str = Field(..., description="Indicator name")
    language: str = Field(..., description="Language (PT or EN)")
    data: List[Dict[str, Any]] = Field(default_factory=list, description="Raw data points")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    extraction_date: datetime = Field(
        default_factory=datetime.now, description="When data was extracted"
    )

    def to_dataframe(self) -> "pd.DataFrame":
        """Convert data to pandas DataFrame.

        Returns:
            pandas DataFrame with the indicator data.

        Raises:
            ImportError: If pandas is not installed.

        Example:
            >>> response = DataResponse(...)
            >>> df = response.to_dataframe()
            >>> print(df.head())
        """
        if not PANDAS_AVAILABLE:
            raise ImportError(
                "pandas is required to convert data to DataFrame. "
                "Install it with: pip install pandas"
            )

        if not self.data:
            return pd.DataFrame()

        return pd.DataFrame(self.data)

    def to_csv(
        self,
        filepath: Union[str, Path],
        include_metadata: bool = True,
        **kwargs: Any,
    ) -> None:
        """Export data to CSV file.

        Args:
            filepath: Output file path
            include_metadata: Include metadata as comment header
            **kwargs: Additional arguments passed to df.to_csv()
        """
        df = self.to_dataframe()
        metadata = {
            "indicator": self.varcd,
            "title": self.title,
            "unit": self.unit,
            "language": self.language,
            "extraction_date": self.extraction_date.isoformat(),
        }
        export_to_csv(df, Path(filepath), include_metadata=include_metadata, metadata=metadata, **kwargs)

    def to_json(
        self,
        filepath: Union[str, Path],
        pretty: bool = True,
        **kwargs: Any,
    ) -> None:
        """Export data to JSON file.

        Args:
            filepath: Output file path
            pretty: Use pretty printing
            **kwargs: Additional arguments passed to json.dump()
        """
        data = self.model_dump(mode="json")
        export_to_json(data, Path(filepath), pretty=pretty, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary.

        Returns:
            Dictionary representation of the response.
        """
        return self.model_dump()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "varcd": "0004167",
                "title": "Resident population",
                "language": "EN",
                "data": [
                    {"Period": "2020", "Geographic localization": "Portugal", "value": 10298252},
                    {"Period": "2021", "Geographic localization": "Portugal", "value": 10295909},
                ],
                "unit": "No.",
            }
        }
    )


class CatalogueResponse(BaseModel):
    """Wrapper for catalogue API response.

    Contains a list of indicators returned from the catalogue query.
    """

    indicators: List["Indicator"] = Field(default_factory=list, description="List of indicators")
    language: str = Field(..., description="Language (PT or EN)")
    extraction_date: datetime = Field(
        default_factory=datetime.now, description="When data was extracted"
    )
    total_count: int = Field(0, description="Total number of indicators")

    def __len__(self) -> int:
        """Return number of indicators."""
        return len(self.indicators)

    def __iter__(self):
        """Iterate over indicators."""
        return iter(self.indicators)

    def __getitem__(self, index: int) -> Indicator:
        """Get indicator by index."""
        return self.indicators[index]


CatalogueResponse.model_rebuild()
