# Scripts Directory

This directory contains operational scripts for development, deployment, monitoring, and optimization of the Customer Solution Snapshot Generator.

## Directory Structure

```
scripts/
├── benchmarking/       # Performance benchmarking and analysis
├── deployment/         # Deployment and release automation
├── monitoring/         # System monitoring and dashboards
└── optimization/       # Performance optimization tools
```

## Usage

All scripts should be run from the project root directory:

```bash
# From project root
python scripts/benchmarking/benchmark.py
python scripts/deployment/deploy.py
# etc.
```

Or using uv:

```bash
uv run python scripts/benchmarking/benchmark.py
```

## Script Categories

### Benchmarking
Performance testing and analysis tools.

### Deployment
Tools for deploying and releasing the application.

### Monitoring
Real-time monitoring and operational dashboards.

### Optimization
Performance optimization and profiling tools.

## Requirements

Most scripts require the development dependencies:

```bash
uv sync --extra dev
```

See individual subdirectory READMEs for specific requirements.
