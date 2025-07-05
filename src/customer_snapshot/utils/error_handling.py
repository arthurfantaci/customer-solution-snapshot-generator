"""
Enhanced error handling utilities for Customer Solution Snapshot Generator.

This module provides decorators, context managers, and utilities for robust
error handling with automatic tracking and recovery mechanisms.
"""

import os
import sys
import time
import logging
import functools
from typing import Optional, Callable, Any, Type, Union, List
from contextlib import contextmanager

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ..monitoring.error_tracker import (
    ErrorTracker, ErrorContext, ErrorCategory, get_error_tracker, track_exception
)

logger = logging.getLogger(__name__)


class ErrorHandlingConfig:
    """Configuration for error handling behavior."""
    
    def __init__(self):
        self.retry_attempts = 3
        self.retry_delay = 1.0  # seconds
        self.retry_backoff_factor = 2.0
        self.enable_tracking = True
        self.raise_on_failure = True
        self.fallback_value = None
        self.timeout = None


def with_error_tracking(
    category: Optional[ErrorCategory] = None,
    context_data: Optional[dict] = None,
    reraise: bool = True
):
    """
    Decorator to automatically track errors with context information.
    
    Args:
        category: Error category for classification
        context_data: Additional context data to include
        reraise: Whether to re-raise the exception after tracking
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Create context
                context = ErrorContext(
                    function_name=func.__name__,
                    module_name=func.__module__,
                    additional_data={
                        'args_count': len(args),
                        'kwargs_keys': list(kwargs.keys()),
                        **(context_data or {})
                    }
                )
                
                # Track the error
                error_tracker = get_error_tracker()
                error_tracker.track_exception(e, context)
                
                if reraise:
                    raise
                else:
                    logger.error(f"Error in {func.__name__}: {e}")
                    return None
        
        return wrapper
    return decorator


def with_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Decorator to retry function execution on failure.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff_factor: Multiplier for delay after each attempt
        exceptions: Tuple of exceptions to catch and retry
        on_retry: Callback function called before each retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:  # Last attempt
                        # Track the final failure
                        context = ErrorContext(
                            function_name=func.__name__,
                            module_name=func.__module__,
                            additional_data={
                                'retry_attempt': attempt + 1,
                                'max_attempts': max_attempts,
                                'final_failure': True
                            }
                        )
                        get_error_tracker().track_exception(e, context)
                        raise e
                    
                    # Log retry attempt
                    logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}")
                    
                    # Call retry callback if provided
                    if on_retry:
                        try:
                            on_retry(attempt + 1, e, *args, **kwargs)
                        except Exception as callback_error:
                            logger.error(f"Error in retry callback: {callback_error}")
                    
                    # Wait before retry
                    if attempt < max_attempts - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator


def with_timeout(timeout_seconds: float):
    """
    Decorator to add timeout to function execution.
    
    Args:
        timeout_seconds: Maximum execution time in seconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Function {func.__name__} timed out after {timeout_seconds} seconds")
            
            # Set timeout signal
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(timeout_seconds))
            
            try:
                result = func(*args, **kwargs)
                signal.alarm(0)  # Cancel timeout
                return result
            except TimeoutError as e:
                # Track timeout error
                context = ErrorContext(
                    function_name=func.__name__,
                    module_name=func.__module__,
                    additional_data={
                        'timeout_seconds': timeout_seconds,
                        'error_type': 'timeout'
                    }
                )
                get_error_tracker().track_exception(e, context)
                raise
            finally:
                signal.signal(signal.SIGALRM, old_handler)
                signal.alarm(0)
        
        return wrapper
    return decorator


def with_fallback(fallback_value: Any = None, exceptions: tuple = (Exception,)):
    """
    Decorator to provide fallback value on exception.
    
    Args:
        fallback_value: Value to return if function fails
        exceptions: Tuple of exceptions to catch
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                logger.warning(f"Function {func.__name__} failed, using fallback: {e}")
                
                # Track the error
                context = ErrorContext(
                    function_name=func.__name__,
                    module_name=func.__module__,
                    additional_data={
                        'fallback_used': True,
                        'fallback_value': str(fallback_value)
                    }
                )
                get_error_tracker().track_exception(e, context)
                
                return fallback_value
        
        return wrapper
    return decorator


@contextmanager
def error_context(context_data: dict, category: Optional[ErrorCategory] = None):
    """
    Context manager for tracking errors with additional context.
    
    Args:
        context_data: Dictionary of context information
        category: Error category for classification
    """
    try:
        yield
    except Exception as e:
        # Create enhanced context
        import inspect
        frame = inspect.currentframe().f_back
        
        context = ErrorContext(
            function_name=frame.f_code.co_name,
            module_name=frame.f_globals.get('__name__'),
            file_path=frame.f_code.co_filename,
            line_number=frame.f_lineno,
            additional_data=context_data
        )
        
        # Track the error
        error_tracker = get_error_tracker()
        error_record = error_tracker.track_exception(e, context)
        
        # Override category if specified
        if category:
            error_record.category = category
        
        raise


@contextmanager
def suppress_errors(exceptions: tuple = (Exception,), log_errors: bool = True):
    """
    Context manager to suppress and log errors.
    
    Args:
        exceptions: Tuple of exceptions to suppress
        log_errors: Whether to log suppressed errors
    """
    try:
        yield
    except exceptions as e:
        if log_errors:
            logger.error(f"Suppressed error: {e}")
            
            # Track the suppressed error
            context = ErrorContext(
                additional_data={
                    'suppressed': True,
                    'error_type': 'suppressed'
                }
            )
            get_error_tracker().track_exception(e, context)


class ErrorBoundary:
    """Error boundary for containing and handling errors in code sections."""
    
    def __init__(self, name: str, fallback_value: Any = None, 
                 reraise: bool = False, track_errors: bool = True):
        self.name = name
        self.fallback_value = fallback_value
        self.reraise = reraise
        self.track_errors = track_errors
        self.errors = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            if self.track_errors:
                context = ErrorContext(
                    additional_data={
                        'error_boundary': self.name,
                        'boundary_type': 'contained'
                    }
                )
                error_record = get_error_tracker().track_exception(exc_val, context)
                self.errors.append(error_record)
            
            if not self.reraise:
                logger.error(f"Error in boundary '{self.name}': {exc_val}")
                return True  # Suppress the exception
        
        return False
    
    def get_result(self, default_value: Any = None):
        """Get result value, fallback if errors occurred."""
        if self.errors:
            return self.fallback_value if self.fallback_value is not None else default_value
        return None


def safe_execute(func: Callable, *args, fallback_value: Any = None, 
                retry_count: int = 0, **kwargs) -> Any:
    """
    Safely execute a function with error handling and optional retry.
    
    Args:
        func: Function to execute
        *args: Function arguments
        fallback_value: Value to return on failure
        retry_count: Number of retry attempts
        **kwargs: Function keyword arguments
    
    Returns:
        Function result or fallback value
    """
    last_exception = None
    
    for attempt in range(retry_count + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            
            # Track the error
            context = ErrorContext(
                function_name=func.__name__ if hasattr(func, '__name__') else 'unknown',
                additional_data={
                    'attempt': attempt + 1,
                    'max_attempts': retry_count + 1,
                    'safe_execute': True
                }
            )
            get_error_tracker().track_exception(e, context)
            
            if attempt < retry_count:
                logger.warning(f"Attempt {attempt + 1} failed, retrying: {e}")
                time.sleep(1.0 * (attempt + 1))  # Progressive delay
            else:
                logger.error(f"All attempts failed for {func.__name__ if hasattr(func, '__name__') else 'function'}: {e}")
    
    return fallback_value


class CircuitBreaker:
    """Circuit breaker pattern implementation for fault tolerance."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60,
                 expected_exception: Type[Exception] = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == 'open':
                if self._should_attempt_reset():
                    self.state = 'half-open'
                else:
                    raise Exception(f"Circuit breaker is OPEN for {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure(e, func.__name__)
                raise
        
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt to reset."""
        return (time.time() - self.last_failure_time) >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful execution."""
        self.failure_count = 0
        self.state = 'closed'
    
    def _on_failure(self, exception: Exception, func_name: str):
        """Handle failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'open'
            logger.warning(f"Circuit breaker OPENED for {func_name} after {self.failure_count} failures")
        
        # Track the failure
        context = ErrorContext(
            function_name=func_name,
            additional_data={
                'circuit_breaker_state': self.state,
                'failure_count': self.failure_count,
                'threshold': self.failure_threshold
            }
        )
        get_error_tracker().track_exception(exception, context)


# Predefined error handling configurations
STANDARD_CONFIG = ErrorHandlingConfig()
STANDARD_CONFIG.retry_attempts = 3
STANDARD_CONFIG.retry_delay = 1.0

AGGRESSIVE_RETRY_CONFIG = ErrorHandlingConfig()
AGGRESSIVE_RETRY_CONFIG.retry_attempts = 5
AGGRESSIVE_RETRY_CONFIG.retry_delay = 0.5

NO_RETRY_CONFIG = ErrorHandlingConfig()
NO_RETRY_CONFIG.retry_attempts = 1
NO_RETRY_CONFIG.retry_delay = 0

SILENT_FAIL_CONFIG = ErrorHandlingConfig()
SILENT_FAIL_CONFIG.retry_attempts = 1
SILENT_FAIL_CONFIG.raise_on_failure = False


# Common error handling patterns
def handle_file_operations(func: Callable) -> Callable:
    """Error handler specifically for file operations."""
    return with_error_tracking(
        category=ErrorCategory.FILE_IO
    )(with_retry(
        max_attempts=3,
        exceptions=(IOError, OSError, FileNotFoundError, PermissionError)
    )(func))


def handle_network_operations(func: Callable) -> Callable:
    """Error handler specifically for network operations."""
    return with_error_tracking(
        category=ErrorCategory.NETWORK_ERROR
    )(with_retry(
        max_attempts=3,
        delay=2.0,
        exceptions=(ConnectionError, TimeoutError)
    )(func))


def handle_api_calls(func: Callable) -> Callable:
    """Error handler specifically for API calls."""
    return with_error_tracking(
        category=ErrorCategory.API_ERROR
    )(with_retry(
        max_attempts=3,
        delay=1.0,
        backoff_factor=2.0
    )(with_timeout(30.0)(func)))


def handle_parsing_operations(func: Callable) -> Callable:
    """Error handler specifically for parsing operations."""
    return with_error_tracking(
        category=ErrorCategory.PARSING_ERROR
    )(with_fallback(
        fallback_value=None
    )(func))