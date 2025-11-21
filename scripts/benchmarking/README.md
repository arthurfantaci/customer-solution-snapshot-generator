# Benchmarking Scripts

Performance benchmarking and analysis tools for the Customer Solution Snapshot Generator.

## Scripts

### benchmark.py
Comprehensive benchmarking suite for testing application performance.

**Features:**
- File processing benchmarks
- Memory usage profiling
- CPU performance metrics
- I/O performance tests
- Generates detailed reports

**Usage:**
```bash
python scripts/benchmarking/benchmark.py
```

**Output:**
- Console report with metrics
- JSON export of results
- Performance trends analysis

### performance_dashboard.py
Interactive dashboard for visualizing performance metrics.

**Features:**
- Real-time performance monitoring
- Historical trend analysis
- Comparative benchmarking
- Visual charts and graphs

**Usage:**
```bash
python scripts/benchmarking/performance_dashboard.py
```

**Access:**
Opens a web interface at `http://localhost:8080`

## Requirements

```bash
uv sync --extra dev
```

Additional dependencies:
- psutil (system metrics)
- memory-profiler (memory profiling)

## Best Practices

1. Run benchmarks on a consistent system
2. Close other applications during benchmarking
3. Run multiple iterations for reliable results
4. Compare results over time to detect regressions

## Output Examples

```
Benchmark Results:
- File Processing: 1.23s (avg)
- Memory Usage: 245MB (peak)
- CPU Usage: 35% (avg)
- Throughput: 15 files/sec
```
