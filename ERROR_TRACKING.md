# Error Tracking and Analysis System

This document provides comprehensive guidance for the error tracking and analysis capabilities of the Customer Solution Snapshot Generator.

## Overview

The error tracking system provides enterprise-grade error monitoring and analysis with:

- **Comprehensive Error Tracking**: Automatic error capture and classification
- **Error Analysis Dashboard**: Real-time error monitoring and analysis
- **Error Handling Utilities**: Decorators and utilities for robust error handling
- **Error Aggregation**: Intelligent grouping of similar errors
- **Error Recovery**: Retry patterns, circuit breakers, and fallback mechanisms
- **Error Export**: Export capabilities for analysis and reporting
- **Integration Support**: Seamless integration with alerting systems

## Quick Start

### Basic Error Tracking

```python
from src.customer_snapshot.monitoring.error_tracker import get_error_tracker, track_exception
from src.customer_snapshot.utils.error_handling import with_error_tracking

# Manual error tracking
try:
    risky_operation()
except Exception as e:
    track_exception(e)

# Automatic error tracking with decorator
@with_error_tracking()
def my_function():
    # Function code here
    pass
```

### Error Analysis Dashboard

```bash
# Start interactive error analysis dashboard
python error_analysis_dashboard.py --mode interactive

# Generate error report
python error_analysis_dashboard.py --mode report --output error_report.json

# Get error statistics
python error_analysis_dashboard.py --mode stats --json
```

### Error Handling Patterns

```python
from src.customer_snapshot.utils.error_handling import (
    with_retry, with_fallback, ErrorBoundary, safe_execute
)

# Retry pattern
@with_retry(max_attempts=3, delay=1.0)
def unreliable_operation():
    # Operation that might fail
    pass

# Fallback pattern
@with_fallback(fallback_value="default")
def risky_operation():
    # Operation with fallback
    pass

# Error boundary
with ErrorBoundary("data_processing") as boundary:
    process_data()
result = boundary.get_result()
```

## Error Tracking System

### Error Classification

The system automatically classifies errors into categories:

1. **Authentication Errors** - Login, credential, authorization issues
2. **API Errors** - HTTP, REST, service communication errors
3. **Network Errors** - Connection, timeout, DNS issues
4. **File I/O Errors** - File access, permission, disk issues
5. **Parsing Errors** - JSON, XML, CSV, format issues
6. **Memory Errors** - Out of memory, allocation issues
7. **Timeout Errors** - Operation timeouts, deadlines
8. **Configuration Errors** - Settings, parameter, environment issues
9. **Dependency Errors** - Import, module, package issues
10. **Business Logic Errors** - Application-specific errors
11. **Validation Errors** - Input validation, schema issues
12. **Unknown Errors** - Unclassified errors

### Error Severity Levels

- **DEBUG** - Debug information
- **INFO** - Informational messages
- **WARNING** - Warning conditions
- **ERROR** - Error conditions
- **CRITICAL** - Critical errors affecting functionality
- **FATAL** - Fatal errors causing system failure

### Error Aggregation

Similar errors are automatically grouped using fingerprinting:

```python
from src.customer_snapshot.monitoring.error_tracker import ErrorAggregator

aggregator = ErrorAggregator()

# Errors with same signature are grouped
error1 = track_error("Connection failed", "ConnectionError", stack_trace)
error2 = track_error("Connection failed", "ConnectionError", stack_trace)
# error2 will be aggregated with error1, count incremented
```

### Error Context

Rich context information is captured with each error:

```python
from src.customer_snapshot.monitoring.error_tracker import ErrorContext

context = ErrorContext(
    user_id="user123",
    session_id="session456", 
    function_name="process_file",
    module_name="processor",
    file_path="/app/processor.py",
    line_number=42,
    additional_data={
        "file_size": 1024,
        "operation": "parse_vtt"
    }
)

track_exception(exception, context)
```

### Usage Examples

#### Basic Error Tracking

```python
from src.customer_snapshot.monitoring.error_tracker import get_error_tracker

# Get global error tracker
error_tracker = get_error_tracker()

# Start background processing
error_tracker.start_background_processing()

# Track an error manually
error_record = error_tracker.track_error(
    error_message="File not found",
    exception_type="FileNotFoundError",
    stack_trace="traceback...",
    context=ErrorContext(function_name="load_file")
)

# Track an exception
try:
    risky_operation()
except Exception as e:
    error_record = error_tracker.track_exception(e)

# Get error statistics
stats = error_tracker.get_error_stats()
print(f"Total errors: {stats.total_errors}")
print(f"Error rate: {stats.error_rate} errors/second")

# Get recent errors
recent_errors = error_tracker.get_recent_errors(hours=24)

# Resolve an error
error_tracker.resolve_error(error_id, "Fixed by updating configuration")
```

#### Error Trends and Analysis

```python
# Get error trends
trends = error_tracker.get_error_trends(days=7)
for trend in trends:
    print(f"{trend['date']}: {trend['total_errors']} errors")

# Export errors for analysis
error_tracker.export_errors("errors.json", format='json')
error_tracker.export_errors("errors.csv", format='csv')

# Stop background processing
error_tracker.stop_background_processing()
```

## Error Handling Utilities

### Decorators

#### Error Tracking Decorator

```python
from src.customer_snapshot.utils.error_handling import with_error_tracking
from src.customer_snapshot.monitoring.error_tracker import ErrorCategory

@with_error_tracking(category=ErrorCategory.API_ERROR)
def call_external_api():
    # API call code
    pass
```

#### Retry Decorator

```python
from src.customer_snapshot.utils.error_handling import with_retry

@with_retry(max_attempts=3, delay=1.0, backoff_factor=2.0)
def unreliable_operation():
    # Operation that might fail
    pass

# Custom retry callback
def on_retry_callback(attempt, exception, *args, **kwargs):
    print(f"Retry attempt {attempt}: {exception}")

@with_retry(max_attempts=5, on_retry=on_retry_callback)
def operation_with_callback():
    pass
```

#### Timeout Decorator

```python
from src.customer_snapshot.utils.error_handling import with_timeout

@with_timeout(30.0)  # 30 second timeout
def long_running_operation():
    # Long operation
    pass
```

#### Fallback Decorator

```python
from src.customer_snapshot.utils.error_handling import with_fallback

@with_fallback(fallback_value="default_result")
def risky_operation():
    # Operation that might fail
    pass

# Custom exception handling
@with_fallback(fallback_value=None, exceptions=(ValueError, TypeError))
def type_sensitive_operation():
    pass
```

### Context Managers

#### Error Context Manager

```python
from src.customer_snapshot.utils.error_handling import error_context
from src.customer_snapshot.monitoring.error_tracker import ErrorCategory

with error_context({"operation": "file_processing", "file_id": "123"}):
    process_file("data.txt")
```

#### Error Suppression

```python
from src.customer_snapshot.utils.error_handling import suppress_errors

# Suppress specific errors
with suppress_errors((ValueError, TypeError)):
    risky_operation()

# Suppress all errors
with suppress_errors():
    any_operation()
```

#### Error Boundary

```python
from src.customer_snapshot.utils.error_handling import ErrorBoundary

# Error boundary with fallback
with ErrorBoundary("data_processing", fallback_value={}) as boundary:
    result = process_data()

if boundary.errors:
    print(f"Errors occurred: {len(boundary.errors)}")
    result = boundary.get_result()  # Returns fallback value
```

### Utility Functions

#### Safe Execute

```python
from src.customer_snapshot.utils.error_handling import safe_execute

# Execute with fallback
result = safe_execute(
    risky_function,
    arg1, arg2,
    fallback_value="safe_default",
    retry_count=2
)
```

#### Circuit Breaker

```python
from src.customer_snapshot.utils.error_handling import CircuitBreaker

# Apply circuit breaker to function
@CircuitBreaker(failure_threshold=5, recovery_timeout=60)
def external_service_call():
    # Call to external service
    pass

# Circuit breaker states: closed -> open -> half-open -> closed
```

### Predefined Error Handlers

```python
from src.customer_snapshot.utils.error_handling import (
    handle_file_operations,
    handle_network_operations, 
    handle_api_calls,
    handle_parsing_operations
)

# File operations with retry and tracking
@handle_file_operations
def read_large_file(filepath):
    with open(filepath, 'r') as f:
        return f.read()

# Network operations with retry and timeout
@handle_network_operations  
def download_data(url):
    response = requests.get(url)
    return response.json()

# API calls with comprehensive error handling
@handle_api_calls
def call_anthropic_api(prompt):
    # API call implementation
    pass

# Parsing operations with fallback
@handle_parsing_operations
def parse_json_data(data):
    return json.loads(data)
```

## Error Analysis Dashboard

### Interactive Dashboard

The interactive dashboard provides real-time error monitoring:

```bash
# Start interactive dashboard
python error_analysis_dashboard.py --mode interactive

# Dashboard commands:
# r - Refresh display
# e - Export errors
# v - View error details
# s - Show detailed statistics
# h - Show help
# q - Quit
```

### Dashboard Features

#### Overall Statistics
- Total error count
- Current error rate (errors per second)
- Resolution rate percentage
- Mean time to resolution

#### Error Breakdown
- Errors by severity (fatal, critical, error, warning, info, debug)
- Errors by category (authentication, API, network, file I/O, etc.)
- Error trends over time

#### Recent Errors
- Last 24 hours of errors
- Error details with context
- Error frequency and patterns

#### Top Errors
- Most frequent error patterns
- Error impact analysis
- Resolution status

### Dashboard Modes

```bash
# Interactive mode with real-time updates
python error_analysis_dashboard.py --mode interactive --interval 5

# Generate comprehensive report
python error_analysis_dashboard.py --mode report --output detailed_report.json

# Get current statistics
python error_analysis_dashboard.py --mode stats --json

# Quick health check
python error_analysis_dashboard.py --mode health
```

### Example Dashboard Output

```
================================================================================
🔍 CUSTOMER SOLUTION SNAPSHOT GENERATOR - ERROR ANALYSIS DASHBOARD
================================================================================
📅 Last Updated: 2024-01-15T14:30:00

📊 OVERALL ERROR STATISTICS
----------------------------------------
   📈 Total Errors: 45
   ⚡ Current Error Rate: 0.05 errors/second
   🔄 Resolution Rate: 78.0%
   ⏱️  Mean Time to Resolution: 2.3 hours

🚨 ERROR SEVERITY BREAKDOWN
----------------------------------------
   🚨 CRITICAL: 2 (4.4%)
   ❌ ERROR: 15 (33.3%)
   ⚠️  WARNING: 20 (44.4%)
   ℹ️  INFO: 8 (17.8%)

📂 ERROR CATEGORY BREAKDOWN
----------------------------------------
   🌐 Api Error: 12 (26.7%)
   📁 File Io: 8 (17.8%)
   📡 Network Error: 7 (15.6%)
   ✅ Validation: 6 (13.3%)
   🔐 Authentication: 4 (8.9%)

🕐 RECENT ERRORS (Last 24 Hours)
----------------------------------------
   ❌ ConnectionError: API timeout during request processing...
      ID: 550e8400-e29b-41d4-a716-446655440000
      Time: 2 hours ago
      Count: 3
      Function: call_anthropic_api

   ⚠️  ValidationError: Invalid VTT timestamp format...
      ID: 6ba7b810-9dad-11d1-80b4-00c04fd430c8
      Time: 45 minutes ago
      Count: 1
      Function: parse_vtt_file
```

## Integration with Alerting

### Alert Integration

The error tracker integrates with the alerting system:

```python
from src.customer_snapshot.monitoring.error_tracker import get_error_tracker
from src.customer_snapshot.monitoring.alerting import AlertingService

# Set up alerting integration
error_tracker = get_error_tracker()
alerting_service = AlertingService()

# Set alert callback
error_tracker.set_alert_callback(alerting_service.send_alert)

# Critical errors will automatically trigger alerts
# Error spikes will trigger warning alerts
```

### Alert Conditions

Automatic alerts are triggered for:

1. **Critical/Fatal Errors** - Immediate alert on occurrence
2. **Error Spikes** - Alert when error rate exceeds threshold
3. **High Error Rate** - Alert when error rate is sustained
4. **Circuit Breaker Trips** - Alert when circuit breakers open

### Alert Configuration

Configure alert thresholds:

```python
error_tracker.alert_thresholds = {
    'error_rate': 0.1,      # 10% error rate
    'critical_errors': 5,   # 5 critical errors in window
    'error_spike': 2.0      # 2x increase in errors
}
```

## Configuration

### Environment Variables

```bash
# Error tracking configuration
export ENABLE_ERROR_TRACKING=true
export ERROR_TRACKING_BACKGROUND=true
export ERROR_CACHE_SIZE=10000
export ERROR_HISTORY_SIZE=50000

# Error analysis
export ERROR_ANALYSIS_DASHBOARD_PORT=8082
export ERROR_EXPORT_FORMAT=json
export ERROR_AGGREGATION_WINDOW=300

# Error handling
export DEFAULT_RETRY_ATTEMPTS=3
export DEFAULT_RETRY_DELAY=1.0
export DEFAULT_TIMEOUT=30.0
export CIRCUIT_BREAKER_THRESHOLD=5
export CIRCUIT_BREAKER_TIMEOUT=60
```

### Configuration in Code

```python
from src.customer_snapshot.monitoring.error_tracker import ErrorTracker
from src.customer_snapshot.utils.config import Config

# Custom configuration
config = Config.get_default()
error_tracker = ErrorTracker(config)

# Custom aggregator settings
error_tracker.aggregator.max_errors = 5000
error_tracker.aggregator.aggregation_window = 600  # 10 minutes

# Custom alert thresholds
error_tracker.alert_thresholds = {
    'error_rate': 0.05,     # 5% error rate
    'critical_errors': 3,   # 3 critical errors
    'error_spike': 1.5      # 50% increase
}
```

## Testing

### Running Tests

```bash
# Run all error tracking tests
python test_error_tracking.py --mode both --verbose

# Run only unit tests
python test_error_tracking.py --mode unit

# Run comprehensive integration tests
python test_error_tracking.py --mode comprehensive
```

### Test Coverage

The test suite covers:

- Error classification and categorization
- Error aggregation and fingerprinting
- Error tracking and storage
- Error statistics and analysis
- Error handling decorators and utilities
- Error export functionality
- Dashboard functionality
- Integration with alerting system

### Example Test

```python
# Test error tracking with context
def test_error_with_context():
    error_tracker = get_error_tracker()
    
    context = ErrorContext(
        function_name="test_function",
        additional_data={"test_key": "test_value"}
    )
    
    error_record = error_tracker.track_error(
        error_message="Test error",
        exception_type="TestError", 
        stack_trace="test stack trace",
        context=context
    )
    
    assert error_record.context.function_name == "test_function"
    assert error_record.context.additional_data["test_key"] == "test_value"
```

## Performance Considerations

### Resource Usage

The error tracking system is designed to be lightweight:

- **Memory Impact**: ~50MB for 10,000 errors
- **CPU Impact**: <2% additional CPU usage
- **Storage Impact**: ~1KB per error record
- **Network Impact**: Minimal (only for exports/alerts)

### Optimization Tips

1. **Adjust History Size**:
```python
error_tracker.error_history = deque(maxlen=10000)  # Reduce from 50,000
```

2. **Limit Context Data**:
```python
context = ErrorContext(
    function_name=func.__name__,
    # Avoid large additional_data
    additional_data={"key": str(value)[:100]}  # Truncate large values
)
```

3. **Configure Aggregation**:
```python
error_tracker.aggregator.aggregation_window = 600  # 10 minutes (longer window)
error_tracker.aggregator.max_errors = 5000  # Smaller cache
```

4. **Disable Features in Production**:
```python
# Disable detailed stack traces in production
if production_mode:
    error_tracker.include_full_stack_trace = False
```

## Security Considerations

### Data Sanitization

Error data is automatically sanitized:

- API keys and tokens are redacted
- Personal information is masked
- File paths are sanitized
- Large data structures are truncated

### Sensitive Data Handling

```python
# Configure data sanitization
error_tracker.sanitize_patterns = [
    r'api_key=\w+',
    r'password=\w+', 
    r'token=\w+',
    r'\b\d{4}-\d{4}-\d{4}-\d{4}\b'  # Credit card numbers
]
```

### Access Control

```python
# Secure error export
def secure_export(user_role):
    if user_role != 'admin':
        raise PermissionError("Only admins can export error data")
    
    return error_tracker.export_errors("secure_export.json")
```

## Troubleshooting

### Common Issues

**Error Tracking Not Working:**
```bash
# Check if error tracker is initialized
python -c "
from src.customer_snapshot.monitoring.error_tracker import get_error_tracker
tracker = get_error_tracker()
print('Error tracker initialized:', tracker is not None)
"
```

**Dashboard Not Starting:**
```bash
# Check dashboard dependencies
python error_analysis_dashboard.py --mode stats
```

**High Memory Usage:**
```bash
# Check error history size
python -c "
from src.customer_snapshot.monitoring.error_tracker import get_error_tracker
tracker = get_error_tracker()
print('Error history size:', len(tracker.error_history))
print('Error cache size:', len(tracker.aggregator.error_cache))
"
```

**Errors Not Being Aggregated:**
```bash
# Check fingerprint generation
python -c "
from src.customer_snapshot.monitoring.error_tracker import ErrorAggregator, ErrorContext
agg = ErrorAggregator()
context = ErrorContext(function_name='test')
fp = agg.generate_fingerprint('test error', 'TestError', 'stack', context)
print('Fingerprint:', fp)
"
```

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger('src.customer_snapshot.monitoring.error_tracker').setLevel(logging.DEBUG)
```

### Performance Monitoring

Monitor error tracking performance:

```python
# Get performance metrics
stats = error_tracker.get_error_stats()
print(f"Processing rate: {stats.error_rate} errors/second")

# Monitor memory usage
import psutil
process = psutil.Process()
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB")
```

## Best Practices

### Development
- Use error tracking decorators for all external operations
- Add rich context information to errors
- Test error handling paths regularly
- Monitor error patterns during development

### Staging
- Enable comprehensive error tracking
- Test error analysis dashboard
- Validate error export functionality
- Test integration with alerting system

### Production
- Enable background error processing
- Configure appropriate alert thresholds
- Set up regular error report generation
- Monitor error tracking system performance
- Implement log rotation for error exports

### Maintenance
- Regular review of error patterns
- Update error classification rules
- Adjust alert thresholds based on trends
- Clean up resolved errors periodically
- Review error handling effectiveness

## Support

For error tracking related issues:

1. **Check error tracker status**: `python error_analysis_dashboard.py --mode stats`
2. **Review error logs**: Check application logs for error tracking messages
3. **Test error tracking**: `python test_error_tracking.py --mode comprehensive`
4. **Validate configuration**: Review error tracking configuration
5. **Check integrations**: Verify alerting system integration

---

*This error tracking system provides enterprise-grade error monitoring and analysis for the Customer Solution Snapshot Generator, ensuring robust error handling and comprehensive error analysis capabilities.*