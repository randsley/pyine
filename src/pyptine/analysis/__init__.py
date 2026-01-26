"""Data analysis module for pyptine.

Provides methods for advanced statistical calculations on indicator data,
including year-over-year growth, month-over-month changes, and moving averages.
"""

from pyptine.analysis.metrics import (
    calculate_moving_average,
    calculate_mom_change,
    calculate_yoy_growth,
)

__all__ = [
    "calculate_yoy_growth",
    "calculate_mom_change",
    "calculate_moving_average",
]
