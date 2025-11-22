"""Error tracking module for Customer Solution Snapshot Generator.

This module provides error tracking and analysis capabilities.
"""

from .error_tracker import (
    ErrorCategory,
    ErrorContext,
    ErrorRecord,
    ErrorSeverity,
    ErrorStats,
    ErrorTracker,
    get_error_tracker,
)


__all__ = [
    "ErrorCategory",
    "ErrorContext",
    "ErrorRecord",
    "ErrorSeverity",
    "ErrorStats",
    "ErrorTracker",
    "get_error_tracker",
]
