# Manual Test Scripts

Manual testing scripts for specific subsystems and features that require interactive testing or specialized scenarios.

## Scripts

### test_error_system_standalone.py
Standalone test for the error tracking system.

**Purpose:**
- Test error aggregation
- Verify error fingerprinting
- Test alert generation
- Validate error statistics

**Usage:**
```bash
python tests/manual/test_error_system_standalone.py
```

**Tests:**
- Error recording and retrieval
- Error grouping by fingerprint
- Alert threshold triggering
- Statistics calculation
- Export functionality

### test_error_tracking.py
Comprehensive error tracking integration tests.

**Purpose:**
- Test error tracking in realistic scenarios
- Verify integration with monitoring
- Test error recovery mechanisms
- Validate error reporting

**Usage:**
```bash
python tests/manual/test_error_tracking.py
```

**Scenarios:**
- Multiple concurrent errors
- Error spike detection
- Alert routing
- Error trend analysis
- Export and reporting

### test_memory_optimization.py
Memory optimization validation tests.

**Purpose:**
- Verify memory optimization features
- Test streaming implementations
- Validate cleanup mechanisms
- Check for memory leaks

**Usage:**
```bash
python tests/manual/test_memory_optimization.py
```

**Tests:**
- Large file processing
- Memory limit enforcement
- Streaming vs loading
- Garbage collection
- Memory leak detection

## Why Manual Tests?

These tests are in `tests/manual/` because they:

1. **Require human observation** - Visual inspection of dashboards, logs, or metrics
2. **Take significant time** - Long-running tests that don't fit in automated CI
3. **Need specific setup** - Require external services or specific configurations
4. **Interactive validation** - User needs to verify behavior manually
5. **Resource intensive** - May consume significant memory/CPU

## Running Manual Tests

### Prerequisites

```bash
# Install dev dependencies
uv sync --extra dev

# Ensure services are running (if needed)
python scripts/monitoring/monitor.py &
```

### Run Individual Tests

```bash
# Run specific test
python tests/manual/test_error_system_standalone.py

# Run with verbose output
python tests/manual/test_error_system_standalone.py --verbose

# Run and export results
python tests/manual/test_error_system_standalone.py --export results.json
```

### Run All Manual Tests

```bash
# From project root
for test in tests/manual/test_*.py; do
    echo "Running $test..."
    python "$test"
    echo "---"
done
```

## Test Results

Manual tests typically output:
- Console reports (pass/fail)
- Detailed logs
- Performance metrics
- Visual dashboards (where applicable)

Example output:
```
Test Error System - Results
===========================
✓ Error recording: PASS
✓ Error grouping: PASS
✓ Alert generation: PASS
⚠ Statistics calculation: WARN (slight delay observed)
✓ Export functionality: PASS

Overall: 4/5 PASS, 1 WARNING
```

## Best Practices

1. **Run in clean environment** - No other processes interfering
2. **Check logs** - Review logs for unexpected warnings
3. **Monitor resources** - Watch memory/CPU during tests
4. **Document issues** - Note any anomalies for investigation
5. **Run periodically** - Include in release checklist

## Integration with CI/CD

While these are manual tests, consider:
- Running on demand in CI with longer timeouts
- Scheduling nightly runs for long tests
- Storing results for trend analysis
- Alerting on failures

## Moving to Automated Tests

If a manual test becomes stable and fast enough:

1. Move to `tests/integration/` or `tests/unit/`
2. Add to pytest suite
3. Update CI/CD configuration
4. Remove from manual tests

## See Also

- [tests/unit/](../unit/) - Automated unit tests
- [tests/integration/](../integration/) - Automated integration tests
- [tests/conftest.py](../conftest.py) - Shared test fixtures
- [pytest.ini](../../pytest.ini) - pytest configuration
