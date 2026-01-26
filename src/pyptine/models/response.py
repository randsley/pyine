from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from pyptine.models.indicator import Indicator
from pyptine.processors.csv import export_to_csv
from pyptine.processors.json import export_to_json

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
    dimensions: dict[str, str] = Field(default_factory=dict, description="Dimension values")
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
    data: list[dict[str, Any]] = Field(default_factory=list, description="Raw data points")
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
        export_to_csv(
            df, Path(filepath), include_metadata=include_metadata, metadata=metadata, **kwargs
        )

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

    def to_dict(self) -> dict[str, Any]:
        """Convert response to dictionary.

        Returns:
            Dictionary representation of the response.
        """
        return self.model_dump(mode="python")

    def calculate_yoy_growth(
        self,
        value_column: str = "value",
        period_column: str = "Period",
    ) -> "DataResponse":
        """Calculate year-over-year growth rates.

        Compares each period's value to the same period in the previous year.
        Creates a new DataResponse with an added 'yoy_growth' column.

        Args:
            value_column: Name of the column containing values (default: "value")
            period_column: Name of the column containing time period (default: "Period")

        Returns:
            New DataResponse with YoY growth calculations added

        Raises:
            ImportError: If pandas is not installed

        Example:
            >>> response = ine.get_data("0004167")
            >>> yoy_response = response.calculate_yoy_growth()
            >>> df = yoy_response.to_dataframe()
            >>> print(df[['Period', 'value', 'yoy_growth']].head())
        """
        from pyptine.analysis.metrics import calculate_yoy_growth

        new_data = calculate_yoy_growth(self.data, value_column, period_column)
        return DataResponse(
            varcd=self.varcd,
            title=self.title,
            language=self.language,
            data=new_data,
            unit=self.unit,
            extraction_date=self.extraction_date,
        )

    def calculate_mom_change(
        self,
        value_column: str = "value",
        period_column: str = "Period",
    ) -> "DataResponse":
        """Calculate month-over-month percentage changes.

        Compares each period's value to the immediately preceding period.
        Creates a new DataResponse with an added 'mom_change' column.

        Args:
            value_column: Name of the column containing values (default: "value")
            period_column: Name of the column containing time period (default: "Period")

        Returns:
            New DataResponse with MoM change calculations added

        Raises:
            ImportError: If pandas is not installed

        Example:
            >>> response = ine.get_data("0004127")
            >>> mom_response = response.calculate_mom_change()
            >>> df = mom_response.to_dataframe()
            >>> print(df[['Period', 'value', 'mom_change']].head())
        """
        from pyptine.analysis.metrics import calculate_mom_change

        new_data = calculate_mom_change(self.data, value_column, period_column)
        return DataResponse(
            varcd=self.varcd,
            title=self.title,
            language=self.language,
            data=new_data,
            unit=self.unit,
            extraction_date=self.extraction_date,
        )

    def calculate_moving_average(
        self,
        window: int = 3,
        value_column: str = "value",
        period_column: str = "Period",
    ) -> "DataResponse":
        """Calculate simple moving average over a time window.

        Computes the rolling mean of values over a specified window size.
        Creates a new DataResponse with an added 'moving_avg' column.

        Args:
            window: Number of periods to include in the moving average (default: 3)
            value_column: Name of the column containing values (default: "value")
            period_column: Name of the column containing time period (default: "Period")

        Returns:
            New DataResponse with moving average calculations added

        Raises:
            ImportError: If pandas is not installed
            ValueError: If window size is invalid

        Example:
            >>> response = ine.get_data("0004127")
            >>> ma_response = response.calculate_moving_average(window=12)
            >>> df = ma_response.to_dataframe()
            >>> print(df[['Period', 'value', 'moving_avg']].head(15))
        """
        from pyptine.analysis.metrics import calculate_moving_average

        new_data = calculate_moving_average(self.data, window, value_column, period_column)
        return DataResponse(
            varcd=self.varcd,
            title=self.title,
            language=self.language,
            data=new_data,
            unit=self.unit,
            extraction_date=self.extraction_date,
        )

    def calculate_exponential_moving_average(
        self,
        span: int = 3,
        value_column: str = "value",
        period_column: str = "Period",
    ) -> "DataResponse":
        """Calculate exponential moving average.

        Computes the exponentially weighted moving mean, giving more weight to recent values.
        Creates a new DataResponse with an added 'ema' column.

        Args:
            span: Span parameter for EMA calculation (default: 3)
            value_column: Name of the column containing values (default: "value")
            period_column: Name of the column containing time period (default: "Period")

        Returns:
            New DataResponse with EMA calculations added

        Raises:
            ImportError: If pandas is not installed
            ValueError: If span is invalid

        Example:
            >>> response = ine.get_data("0004127")
            >>> ema_response = response.calculate_exponential_moving_average(span=10)
            >>> df = ema_response.to_dataframe()
            >>> print(df[['Period', 'value', 'ema']].head(15))
        """
        from pyptine.analysis.metrics import calculate_exponential_moving_average

        new_data = calculate_exponential_moving_average(self.data, span, value_column, period_column)
        return DataResponse(
            varcd=self.varcd,
            title=self.title,
            language=self.language,
            data=new_data,
            unit=self.unit,
            extraction_date=self.extraction_date,
        )

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

    indicators: list["Indicator"] = Field(default_factory=list, description="List of indicators")
    language: str = Field(..., description="Language (PT or EN)")
    extraction_date: datetime = Field(
        default_factory=datetime.now, description="When data was extracted"
    )
    total_count: int = Field(0, description="Total number of indicators")

    def __len__(self) -> int:
        """Return number of indicators."""
        return len(self.indicators)

    def __iter__(self) -> Iterator[Indicator]:  # type: ignore[override]
        """Iterate over indicators."""
        return iter(self.indicators)

    def __getitem__(self, index: int) -> Indicator:
        """Get indicator by index."""
        return self.indicators[index]


CatalogueResponse.model_rebuild()
