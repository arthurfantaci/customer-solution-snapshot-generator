# Performance Monitoring and Optimization

This document describes the comprehensive performance monitoring and optimization tools available for the Customer Solution Snapshot Generator.

## Overview

The performance suite includes several tools designed to help you monitor, benchmark, and optimize the transcript processing system:

- **Benchmark Suite** (`benchmark.py`) - Comprehensive performance testing
- **System Monitor** (`monitor.py`) - Real-time performance monitoring
- **Optimization Profiler** (`optimize.py`) - Code profiling and bottleneck analysis
- **Performance Dashboard** (`performance_dashboard.py`) - Unified dashboard and reporting

## Prerequisites

Install the required dependencies:

```bash
pip install -r requirements-dev.txt
```

Key dependencies for performance monitoring:
- `psutil` - System and process monitoring
- `memory-profiler` - Memory usage profiling
- `line-profiler` - Line-by-line performance profiling

## Tools Overview

### 1. Benchmark Suite (`benchmark.py`)

Runs comprehensive performance benchmarks across different file sizes and configurations.

**Features:**
- Multi-size file testing (0.1 MB to 10 MB)
- CPU and memory usage monitoring
- Throughput calculation
- Statistical analysis of results
- JSON report generation

**Usage:**
```bash
# Run full benchmark suite
python benchmark.py

# The script will test different file sizes and generate results
```

**Output:**
- Console output with real-time results
- JSON report file: `benchmark_results_YYYYMMDD_HHMMSS.json`

### 2. System Monitor (`monitor.py`)

Provides real-time monitoring of system and application performance.

**Features:**
- System resource monitoring (CPU, memory, disk)
- Application-specific metrics
- Performance alerts and thresholds
- Historical data tracking
- Periodic performance reports

**Usage:**
```bash
# Start monitoring (runs until interrupted)
python monitor.py

# Monitor will display real-time metrics and alerts
```

**Output:**
- Real-time console output
- Periodic performance reports
- Alert notifications when thresholds are exceeded

### 3. Optimization Profiler (`optimize.py`)

Performs detailed code profiling to identify performance bottlenecks.

**Features:**
- CPU profiling with function-level analysis
- Memory usage profiling
- Bottleneck identification
- Optimization recommendations
- Multi-size testing

**Usage:**
```bash
# Run optimization analysis
python optimize.py

# Generates detailed profiling reports
```

**Output:**
- Detailed console analysis
- JSON optimization reports
- Performance recommendations

### 4. Performance Dashboard (`performance_dashboard.py`)

Unified dashboard that combines all performance monitoring capabilities.

**Features:**
- Integrated benchmarking, monitoring, and profiling
- HTML dashboard generation
- Multiple operation modes
- Comprehensive reporting
- Browser-based visualization

**Usage:**
```bash
# Run comprehensive analysis
python performance_dashboard.py --mode comprehensive

# Generate HTML dashboard
python performance_dashboard.py --mode dashboard --open

# Run specific modes
python performance_dashboard.py --mode benchmark
python performance_dashboard.py --mode monitor --duration 120
python performance_dashboard.py --mode optimize
```

**Options:**
- `--mode`: Choose operation mode (`benchmark`, `monitor`, `optimize`, `dashboard`, `comprehensive`)
- `--output`: Specify output file for reports
- `--duration`: Set monitoring duration in seconds
- `--open`: Automatically open HTML report in browser

## Performance Metrics

### Benchmark Metrics

The benchmark suite measures:
- **Processing Time**: Total time to process files
- **Memory Usage**: Peak and average memory consumption
- **CPU Usage**: Processor utilization during processing
- **Throughput**: Data processing rate (MB/s)
- **Success Rate**: Percentage of successful processing attempts

### System Metrics

The monitoring system tracks:
- **CPU Usage**: System-wide processor utilization
- **Memory Usage**: RAM consumption and availability
- **Disk Usage**: Storage space and I/O activity
- **Process Count**: Number of running processes
- **Load Average**: System load metrics (Unix/Linux)

### Application Metrics

For the transcript processor:
- **Process CPU**: Application-specific CPU usage
- **Process Memory**: Application memory consumption
- **Thread Count**: Number of active threads
- **File Handles**: Open file descriptor count
- **Uptime**: Application runtime duration

## Performance Targets

### Recommended Performance Targets

Based on testing and optimization:

| File Size | Processing Time | Memory Usage | Throughput |
|-----------|----------------|--------------|------------|
| < 1 MB    | < 5 seconds    | < 100 MB     | > 0.2 MB/s |
| 1-10 MB   | < 30 seconds   | < 300 MB     | > 0.3 MB/s |
| 10-50 MB  | < 2 minutes    | < 500 MB     | > 0.4 MB/s |

### Alert Thresholds

Default alerting thresholds:
- **CPU Usage**: > 80%
- **Memory Usage**: > 85%
- **Disk Usage**: > 90%
- **Disk Free Space**: < 1 GB
- **Process Memory**: > 1 GB

## Optimization Strategies

### Common Bottlenecks

1. **NLP Processing**: spaCy model loading and processing
2. **File I/O**: Large file reading and writing
3. **Memory Usage**: Inefficient data structures
4. **API Calls**: External service latency

### Optimization Recommendations

1. **Model Optimization**:
   - Use smaller spaCy models when possible
   - Implement model caching and reuse
   - Consider batch processing for multiple files

2. **Memory Management**:
   - Implement streaming for large files
   - Use generators instead of loading entire files
   - Clear unused variables and objects

3. **I/O Optimization**:
   - Use buffered I/O for large files
   - Implement async processing where possible
   - Cache frequently accessed data

4. **CPU Optimization**:
   - Profile CPU-intensive functions
   - Consider parallel processing for independent tasks
   - Optimize regular expressions and string operations

## Monitoring in Production

### Docker Integration

The performance tools are integrated with Docker:

```bash
# Run performance check in container
docker run your-app python benchmark.py

# Monitor container performance
docker run your-app python monitor.py
```

### Health Checks

The `healthcheck.py` script includes performance validation:
- Memory usage monitoring
- CPU usage checks
- Disk space verification
- Application responsiveness

### Continuous Monitoring

For production environments:

1. **Set up monitoring alerts**:
   - Configure alert thresholds
   - Set up notification channels
   - Monitor long-term trends

2. **Performance regression testing**:
   - Run benchmarks after code changes
   - Compare performance metrics
   - Identify performance regressions

3. **Capacity planning**:
   - Monitor resource usage trends
   - Plan for scaling requirements
   - Optimize resource allocation

## Troubleshooting

### Common Issues

1. **High Memory Usage**:
   - Check for memory leaks in long-running processes
   - Optimize data structures and algorithms
   - Implement streaming for large files

2. **Slow Processing**:
   - Profile code to identify bottlenecks
   - Optimize NLP model usage
   - Consider caching strategies

3. **System Resource Exhaustion**:
   - Monitor system resources
   - Implement resource limits
   - Scale horizontally if needed

### Performance Debugging

1. **Use profiling tools**:
   ```bash
   python optimize.py  # Detailed profiling
   ```

2. **Monitor in real-time**:
   ```bash
   python monitor.py  # Real-time monitoring
   ```

3. **Generate comprehensive reports**:
   ```bash
   python performance_dashboard.py --mode comprehensive --open
   ```

## Best Practices

1. **Regular Benchmarking**:
   - Run benchmarks after major changes
   - Establish performance baselines
   - Track performance trends over time

2. **Proactive Monitoring**:
   - Set up automated monitoring
   - Configure appropriate alerts
   - Review performance reports regularly

3. **Optimization Workflow**:
   - Profile before optimizing
   - Focus on actual bottlenecks
   - Measure improvements objectively

4. **Documentation**:
   - Document performance requirements
   - Record optimization decisions
   - Share performance insights with team

## Additional Resources

- [Python Performance Profiling](https://docs.python.org/3/library/profile.html)
- [Memory Profiler Documentation](https://pypi.org/project/memory-profiler/)
- [psutil Documentation](https://psutil.readthedocs.io/)
- [spaCy Performance Tips](https://spacy.io/usage/processing-pipelines#performance)

## Support

For performance-related issues:
1. Run the performance dashboard to gather metrics
2. Check the optimization recommendations
3. Review the troubleshooting guide
4. Consult the main project documentation

---

*This performance monitoring suite is designed to help you maintain optimal performance for the Customer Solution Snapshot Generator. Regular monitoring and optimization are key to ensuring efficient transcript processing.*