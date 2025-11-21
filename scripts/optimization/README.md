# Optimization Scripts

Performance optimization and profiling tools for the Customer Solution Snapshot Generator.

## Scripts

### optimize.py
Automated performance optimization and profiling tool.

**Features:**
- Memory usage analysis
- CPU profiling
- I/O optimization
- Code hotspot identification
- Optimization recommendations

**Usage:**
```bash
# Run full optimization analysis
python scripts/optimization/optimize.py

# Profile specific module
python scripts/optimization/optimize.py --module transcript_processing

# Memory profiling
python scripts/optimization/optimize.py --profile memory

# CPU profiling
python scripts/optimization/optimize.py --profile cpu
```

**Output:**
- Profiling reports
- Optimization recommendations
- Before/after comparisons
- Bottleneck identification

## Optimization Workflow

### 1. Initial Profiling
```bash
python scripts/optimization/optimize.py --baseline
```

This creates a baseline performance profile.

### 2. Identify Bottlenecks
```bash
python scripts/optimization/optimize.py --analyze
```

Generates report showing:
- Slow functions
- Memory leaks
- I/O bottlenecks
- CPU-intensive operations

### 3. Apply Optimizations
Review recommendations and apply changes to code.

### 4. Verify Improvements
```bash
python scripts/optimization/optimize.py --compare baseline
```

Compares performance against baseline.

## Profiling Types

### Memory Profiling
```bash
python scripts/optimization/optimize.py --profile memory
```

**Shows:**
- Memory usage per function
- Allocation patterns
- Memory leaks
- Peak memory usage

### CPU Profiling
```bash
python scripts/optimization/optimize.py --profile cpu
```

**Shows:**
- Function call times
- Call frequency
- CPU hotspots
- Execution paths

### I/O Profiling
```bash
python scripts/optimization/optimize.py --profile io
```

**Shows:**
- File operations
- Network calls
- Database queries
- I/O wait times

## Requirements

```bash
uv sync --extra dev
```

Additional tools:
- memory-profiler (memory analysis)
- line-profiler (line-by-line profiling)
- psutil (system metrics)

## Common Optimizations

### 1. Memory Optimization
- Use generators instead of lists
- Implement streaming for large files
- Clear unused objects
- Use `__slots__` for classes

### 2. CPU Optimization
- Cache expensive computations
- Use list comprehensions
- Avoid repeated function calls
- Vectorize operations

### 3. I/O Optimization
- Batch file operations
- Use async I/O
- Implement caching
- Reduce network round-trips

## Example Output

```
Optimization Report
==================

Memory Usage:
  Peak: 245MB → 180MB (-27%)
  Average: 120MB → 95MB (-21%)

CPU Time:
  Total: 3.2s → 1.8s (-44%)
  Hotspots reduced: 3

I/O Operations:
  File reads: 150 → 45 (-70%)
  Network calls: 25 → 15 (-40%)

Recommendations:
  ✓ Cache frequently accessed data
  ✓ Use lazy loading for models
  ✓ Implement connection pooling
```

## See Also

- [PERFORMANCE.md](../../PERFORMANCE.md) - Performance guide
- [MEMORY_OPTIMIZATION.md](../../MEMORY_OPTIMIZATION.md) - Memory optimization details
