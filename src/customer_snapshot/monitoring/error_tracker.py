"""
Application error tracking and analysis system for Customer Solution Snapshot Generator.

This module provides comprehensive error tracking, analysis, and reporting capabilities
including error categorization, trend analysis, and integration with alerting systems.
"""

import hashlib
import json
import logging
import os
import sys
import threading
import time
import traceback
import uuid
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional


# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ..utils.config import Config
from .system_monitor import Alert


logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    FATAL = "fatal"


class ErrorCategory(Enum):
    """Error categories for classification."""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    API_ERROR = "api_error"
    NETWORK_ERROR = "network_error"
    FILE_IO = "file_io"
    PARSING_ERROR = "parsing_error"
    MEMORY_ERROR = "memory_error"
    TIMEOUT = "timeout"
    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"
    BUSINESS_LOGIC = "business_logic"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Context information for an error."""

    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    function_name: Optional[str] = None
    module_name: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    method: Optional[str] = None
    url: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    additional_data: Optional[dict[str, Any]] = None


@dataclass
class ErrorRecord:
    """Individual error record."""

    id: str
    timestamp: str
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    exception_type: str
    stack_trace: str
    context: ErrorContext
    fingerprint: str
    count: int = 1
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    resolved: bool = False
    resolution_notes: Optional[str] = None

    def __post_init__(self):
        """Initialize default values for ID and timestamps."""
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if not self.first_seen:
            self.first_seen = self.timestamp
        if not self.last_seen:
            self.last_seen = self.timestamp


@dataclass
class ErrorStats:
    """Error statistics for analysis."""

    total_errors: int
    error_rate: float
    errors_by_severity: dict[str, int]
    errors_by_category: dict[str, int]
    top_errors: list[dict[str, Any]]
    error_trends: list[dict[str, Any]]
    resolution_rate: float
    mean_time_to_resolution: float


class ErrorClassifier:
    """Classifies errors into categories based on patterns."""

    def __init__(self):
        """Initialize error classifier with classification rules."""
        self.classification_rules = {
            ErrorCategory.AUTHENTICATION: [
                "authentication",
                "auth",
                "login",
                "credential",
                "unauthorized",
                "401",
            ],
            ErrorCategory.AUTHORIZATION: [
                "authorization",
                "permission",
                "access denied",
                "forbidden",
                "403",
            ],
            ErrorCategory.VALIDATION: [
                "validation",
                "invalid",
                "schema",
                "format",
                "constraint",
                "400",
            ],
            ErrorCategory.API_ERROR: [
                "api",
                "http",
                "rest",
                "endpoint",
                "service",
                "502",
                "503",
                "504",
            ],
            ErrorCategory.NETWORK_ERROR: [
                "network",
                "connection",
                "timeout",
                "dns",
                "socket",
                "unreachable",
            ],
            ErrorCategory.FILE_IO: [
                "file",
                "io",
                "read",
                "write",
                "permission",
                "not found",
                "disk",
            ],
            ErrorCategory.PARSING_ERROR: [
                "parse",
                "json",
                "xml",
                "csv",
                "format",
                "decode",
                "encode",
            ],
            ErrorCategory.MEMORY_ERROR: [
                "memory",
                "out of memory",
                "allocation",
                "heap",
                "oom",
            ],
            ErrorCategory.TIMEOUT: ["timeout", "deadline", "expired", "time limit"],
            ErrorCategory.CONFIGURATION: [
                "config",
                "setting",
                "parameter",
                "env",
                "missing",
            ],
            ErrorCategory.DEPENDENCY: [
                "import",
                "module",
                "package",
                "dependency",
                "version",
            ],
        }

    def classify_error(
        self, error_message: str, exception_type: str, stack_trace: str
    ) -> ErrorCategory:
        """Classify error based on message and stack trace."""
        text_to_analyze = f"{error_message} {exception_type} {stack_trace}".lower()

        # Score each category
        category_scores = {}
        for category, keywords in self.classification_rules.items():
            score = sum(1 for keyword in keywords if keyword in text_to_analyze)
            if score > 0:
                category_scores[category] = score

        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)

        return ErrorCategory.UNKNOWN

    def determine_severity(
        self, exception_type: str, error_message: str
    ) -> ErrorSeverity:
        """Determine error severity based on exception type and message."""
        exception_type_lower = exception_type.lower()
        message_lower = error_message.lower()

        # Critical errors
        if any(
            keyword in exception_type_lower
            for keyword in [
                "systemerror",
                "memorytool",
                "keyboardinterrupt",
                "systemexit",
            ]
        ):
            return ErrorSeverity.CRITICAL

        # Fatal errors
        if any(
            keyword in message_lower
            for keyword in ["fatal", "critical", "emergency", "system failure"]
        ):
            return ErrorSeverity.FATAL

        # Error level
        if any(
            keyword in exception_type_lower
            for keyword in ["error", "exception", "failure"]
        ):
            return ErrorSeverity.ERROR

        # Warning level
        if any(
            keyword in exception_type_lower for keyword in ["warning", "deprecation"]
        ):
            return ErrorSeverity.WARNING

        return ErrorSeverity.ERROR


class ErrorAggregator:
    """Aggregates similar errors to reduce noise."""

    def __init__(self, max_errors: int = 10000):
        """Initialize error aggregator.

        Args:
            max_errors: Maximum number of errors to cache (default: 10000).
        """
        self.max_errors = max_errors
        self.error_cache = {}
        self.error_counts = defaultdict(int)

    def generate_fingerprint(
        self,
        error_message: str,
        exception_type: str,
        stack_trace: str,
        context: ErrorContext,
    ) -> str:
        """Generate unique fingerprint for error grouping."""
        # Create fingerprint based on error signature
        signature_parts = [
            exception_type,
            error_message[:200],  # First 200 chars of message
            context.function_name or "",
            context.module_name or "",
            str(context.line_number) if context.line_number else "",
        ]

        # Extract relevant stack trace lines (skip system/library frames)
        stack_lines = []
        for line in stack_trace.split("\n"):
            if any(
                path in line for path in ["/customer_snapshot/", "customer_snapshot"]
            ):
                stack_lines.append(line.strip())

        signature_parts.extend(stack_lines[:3])  # Top 3 relevant stack frames

        signature = "|".join(signature_parts)
        # Use SHA256 instead of MD5 for security best practices
        return hashlib.sha256(signature.encode()).hexdigest()

    def add_error(self, error_record: ErrorRecord) -> ErrorRecord:
        """Add error to aggregator, updating existing if similar."""
        fingerprint = error_record.fingerprint

        if fingerprint in self.error_cache:
            # Update existing error
            existing = self.error_cache[fingerprint]
            existing.count += 1
            existing.last_seen = error_record.timestamp
            self.error_counts[fingerprint] += 1
            return existing
        else:
            # Add new error
            self.error_cache[fingerprint] = error_record
            self.error_counts[fingerprint] = 1

            # Clean up old errors if needed
            if len(self.error_cache) > self.max_errors:
                self._cleanup_old_errors()

            return error_record

    def _cleanup_old_errors(self):
        """Remove old errors to maintain cache size."""
        # Sort by last seen time and remove oldest 10%
        sorted_errors = sorted(self.error_cache.items(), key=lambda x: x[1].last_seen)

        to_remove = len(sorted_errors) // 10
        for fingerprint, _ in sorted_errors[:to_remove]:
            del self.error_cache[fingerprint]
            del self.error_counts[fingerprint]

    def get_top_errors(self, limit: int = 10) -> list[ErrorRecord]:
        """Get most frequent errors."""
        sorted_errors = sorted(
            self.error_cache.items(), key=lambda x: x[1].count, reverse=True
        )

        return [error for _, error in sorted_errors[:limit]]


class ErrorTracker:
    """Main error tracking and analysis system."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize error tracker.

        Args:
            config: Configuration object (default: Config.get_default()).
        """
        self.config = config or Config.get_default()
        self.classifier = ErrorClassifier()
        self.aggregator = ErrorAggregator()

        # Error storage
        self.error_history = deque(maxlen=50000)  # Keep last 50k errors
        self.error_stats = ErrorStats(
            total_errors=0,
            error_rate=0.0,
            errors_by_severity={},
            errors_by_category={},
            top_errors=[],
            error_trends=[],
            resolution_rate=0.0,
            mean_time_to_resolution=0.0,
        )

        # Alerting integration
        self.alert_callback: Optional[Callable] = None
        self.alert_thresholds = {
            "error_rate": 0.1,  # 10% error rate
            "critical_errors": 5,  # 5 critical errors in window
            "error_spike": 2.0,  # 2x increase in errors
        }

        # Background processing
        self.processing_enabled = False
        self.stats_thread = None
        self.stats_interval = 60  # Update stats every minute

        # Setup logging handler
        self.setup_logging_handler()

    def setup_logging_handler(self):
        """Setup logging handler to capture application errors."""

        class ErrorTrackingHandler(logging.Handler):
            def __init__(self, error_tracker):
                """Initialize error tracking handler.

                Args:
                    error_tracker: The ErrorTracker instance to send errors to.
                """
                super().__init__()
                self.error_tracker = error_tracker

            def emit(self, record):
                if record.levelno >= logging.ERROR:
                    # Extract error information
                    error_message = record.getMessage()
                    exception_type = (
                        record.exc_info[0].__name__ if record.exc_info else "LogError"
                    )
                    stack_trace = self.format(record)

                    # Create context
                    context = ErrorContext(
                        function_name=record.funcName,
                        module_name=record.module
                        if hasattr(record, "module")
                        else record.name,
                        file_path=record.pathname,
                        line_number=record.lineno,
                        additional_data={
                            "logger_name": record.name,
                            "level": record.levelname,
                            "thread": record.thread,
                            "process": record.process,
                        },
                    )

                    # Track error
                    self.error_tracker.track_error(
                        error_message=error_message,
                        exception_type=exception_type,
                        stack_trace=stack_trace,
                        context=context,
                    )

        # Add handler to root logger
        handler = ErrorTrackingHandler(self)
        handler.setLevel(logging.ERROR)
        logging.getLogger().addHandler(handler)

    def track_error(
        self,
        error_message: str,
        exception_type: str,
        stack_trace: str,
        context: Optional[ErrorContext] = None,
        severity: Optional[ErrorSeverity] = None,
        category: Optional[ErrorCategory] = None,
    ) -> ErrorRecord:
        """Track an error occurrence."""
        if context is None:
            context = ErrorContext()

        # Classify error if not provided
        if severity is None:
            severity = self.classifier.determine_severity(exception_type, error_message)

        if category is None:
            category = self.classifier.classify_error(
                error_message, exception_type, stack_trace
            )

        # Create error record
        error_record = ErrorRecord(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            severity=severity,
            category=category,
            message=error_message,
            exception_type=exception_type,
            stack_trace=stack_trace,
            context=context,
            fingerprint=self.aggregator.generate_fingerprint(
                error_message, exception_type, stack_trace, context
            ),
        )

        # Aggregate similar errors
        aggregated_error = self.aggregator.add_error(error_record)

        # Store in history
        self.error_history.append(aggregated_error)

        # Check for alerting conditions
        self._check_alert_conditions(aggregated_error)

        logger.debug(f"Tracked error: {error_record.id} - {error_message}")
        return aggregated_error

    def track_exception(
        self, exception: Exception, context: Optional[ErrorContext] = None
    ) -> ErrorRecord:
        """Track an exception object."""
        error_message = str(exception)
        exception_type = type(exception).__name__
        stack_trace = traceback.format_exc()

        return self.track_error(
            error_message=error_message,
            exception_type=exception_type,
            stack_trace=stack_trace,
            context=context,
        )

    def start_background_processing(self):
        """Start background processing for statistics and alerts."""
        self.processing_enabled = True
        self.stats_thread = threading.Thread(target=self._update_stats_loop)
        self.stats_thread.daemon = True
        self.stats_thread.start()
        logger.info("Error tracker background processing started")

    def stop_background_processing(self):
        """Stop background processing."""
        self.processing_enabled = False
        if self.stats_thread:
            self.stats_thread.join(timeout=5)
        logger.info("Error tracker background processing stopped")

    def _update_stats_loop(self):
        """Background loop for updating statistics."""
        while self.processing_enabled:
            try:
                self._update_statistics()
                time.sleep(self.stats_interval)
            except Exception as e:
                logger.error(f"Error updating error statistics: {e}")

    def _update_statistics(self):
        """Update error statistics."""
        current_time = datetime.now()
        hour_ago = current_time - timedelta(hours=1)
        day_ago = current_time - timedelta(days=1)

        # Recent errors (last hour)
        recent_errors = [
            error
            for error in self.error_history
            if datetime.fromisoformat(error.timestamp) > hour_ago
        ]

        # Daily errors
        daily_errors = [
            error
            for error in self.error_history
            if datetime.fromisoformat(error.timestamp) > day_ago
        ]

        # Calculate statistics
        self.error_stats.total_errors = len(self.error_history)
        self.error_stats.error_rate = len(recent_errors) / 3600  # errors per second

        # Group by severity
        severity_counts = defaultdict(int)
        for error in daily_errors:
            severity_counts[error.severity.value] += error.count
        self.error_stats.errors_by_severity = dict(severity_counts)

        # Group by category
        category_counts = defaultdict(int)
        for error in daily_errors:
            category_counts[error.category.value] += error.count
        self.error_stats.errors_by_category = dict(category_counts)

        # Top errors
        self.error_stats.top_errors = [
            {
                "fingerprint": error.fingerprint,
                "message": error.message[:100],
                "count": error.count,
                "severity": error.severity.value,
                "category": error.category.value,
                "last_seen": error.last_seen,
            }
            for error in self.aggregator.get_top_errors(10)
        ]

        # Resolution stats
        resolved_errors = [error for error in self.error_history if error.resolved]
        self.error_stats.resolution_rate = len(resolved_errors) / max(
            len(self.error_history), 1
        )

        # Mean time to resolution
        if resolved_errors:
            resolution_times = []
            for error in resolved_errors:
                if error.resolution_notes:
                    first_seen = datetime.fromisoformat(error.first_seen)
                    last_seen = datetime.fromisoformat(error.last_seen)
                    resolution_times.append((last_seen - first_seen).total_seconds())

            if resolution_times:
                self.error_stats.mean_time_to_resolution = sum(resolution_times) / len(
                    resolution_times
                )

    def _check_alert_conditions(self, error: ErrorRecord):
        """Check if error should trigger alerts."""
        if not self.alert_callback:
            return

        # Critical error alert
        if error.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.FATAL]:
            alert = Alert(
                name="critical_error",
                level="CRITICAL",
                message=f"Critical error detected: {error.message}",
                timestamp=error.timestamp,
                details={
                    "error_id": error.id,
                    "exception_type": error.exception_type,
                    "category": error.category.value,
                    "fingerprint": error.fingerprint,
                    "count": error.count,
                },
            )
            self.alert_callback(alert)

        # Error spike detection
        recent_errors = [
            e
            for e in self.error_history
            if datetime.fromisoformat(e.timestamp)
            > datetime.now() - timedelta(minutes=10)
        ]

        if len(recent_errors) > 20:  # More than 20 errors in 10 minutes
            alert = Alert(
                name="error_spike",
                level="WARNING",
                message=f"Error spike detected: {len(recent_errors)} errors in 10 minutes",
                timestamp=datetime.now().isoformat(),
                details={"error_count": len(recent_errors), "window_minutes": 10},
            )
            self.alert_callback(alert)

    def set_alert_callback(self, callback: Callable):
        """Set callback function for alerts."""
        self.alert_callback = callback

    def get_error_stats(self) -> ErrorStats:
        """Get current error statistics."""
        return self.error_stats

    def get_recent_errors(self, hours: int = 24) -> list[ErrorRecord]:
        """Get recent errors within specified hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            error
            for error in self.error_history
            if datetime.fromisoformat(error.timestamp) > cutoff_time
        ]

    def get_error_by_id(self, error_id: str) -> Optional[ErrorRecord]:
        """Get error by ID."""
        for error in self.error_history:
            if error.id == error_id:
                return error
        return None

    def resolve_error(self, error_id: str, resolution_notes: str) -> bool:
        """Mark error as resolved."""
        error = self.get_error_by_id(error_id)
        if error:
            error.resolved = True
            error.resolution_notes = resolution_notes
            logger.info(f"Error {error_id} marked as resolved")
            return True
        return False

    def get_error_trends(self, days: int = 7) -> list[dict[str, Any]]:
        """Get error trends over specified days."""
        trends = []
        end_date = datetime.now()

        for i in range(days):
            day_start = end_date - timedelta(days=i + 1)
            day_end = end_date - timedelta(days=i)

            day_errors = [
                error
                for error in self.error_history
                if day_start <= datetime.fromisoformat(error.timestamp) < day_end
            ]

            trends.append(
                {
                    "date": day_start.strftime("%Y-%m-%d"),
                    "total_errors": len(day_errors),
                    "critical_errors": len(
                        [e for e in day_errors if e.severity == ErrorSeverity.CRITICAL]
                    ),
                    "error_rate": len(day_errors) / 86400,  # per second
                    "top_category": self._get_top_category(day_errors),
                }
            )

        return list(reversed(trends))

    def _get_top_category(self, errors: list[ErrorRecord]) -> str:
        """Get most common error category from list."""
        if not errors:
            return "none"

        category_counts = defaultdict(int)
        for error in errors:
            category_counts[error.category.value] += error.count

        return (
            max(category_counts, key=category_counts.get) if category_counts else "none"
        )

    def export_errors(self, output_file: str, format: str = "json") -> str:
        """Export errors to file."""
        if format == "json":
            data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_errors": len(self.error_history),
                "statistics": asdict(self.error_stats),
                "errors": [asdict(error) for error in self.error_history],
            }

            with open(output_file, "w") as f:
                json.dump(data, f, indent=2, default=str)

        elif format == "csv":
            import csv

            with open(output_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "ID",
                        "Timestamp",
                        "Severity",
                        "Category",
                        "Message",
                        "Exception Type",
                        "Count",
                        "Resolved",
                        "Function",
                        "Module",
                    ]
                )

                for error in self.error_history:
                    writer.writerow(
                        [
                            error.id,
                            error.timestamp,
                            error.severity.value,
                            error.category.value,
                            error.message,
                            error.exception_type,
                            error.count,
                            error.resolved,
                            error.context.function_name or "",
                            error.context.module_name or "",
                        ]
                    )

        logger.info(f"Exported {len(self.error_history)} errors to {output_file}")
        return output_file


# Global error tracker instance
_error_tracker = None


def get_error_tracker() -> ErrorTracker:
    """Get global error tracker instance."""
    global _error_tracker
    if _error_tracker is None:
        _error_tracker = ErrorTracker()
    return _error_tracker


def track_error(
    error_message: str,
    exception_type: str = "Error",
    context: Optional[ErrorContext] = None,
) -> ErrorRecord:
    """Convenience function to track error."""
    return get_error_tracker().track_error(
        error_message=error_message,
        exception_type=exception_type,
        stack_trace=traceback.format_stack(),
        context=context,
    )


def track_exception(
    exception: Exception, context: Optional[ErrorContext] = None
) -> ErrorRecord:
    """Convenience function to track exception."""
    return get_error_tracker().track_exception(exception, context)


# Decorator for automatic error tracking
def track_errors(category: Optional[ErrorCategory] = None):
    """Decorator to automatically track errors in functions."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = ErrorContext(
                    function_name=func.__name__,
                    module_name=func.__module__,
                    additional_data={
                        "args": str(args)[:200],
                        "kwargs": str(kwargs)[:200],
                    },
                )

                get_error_tracker().track_exception(e, context)
                raise  # Re-raise the exception

        return wrapper

    return decorator
