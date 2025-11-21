# Monitoring Scripts

Real-time monitoring and operational dashboards for the Customer Solution Snapshot Generator.

## Scripts

### monitor.py
Real-time system and application monitoring.

**Monitors:**
- CPU and memory usage
- Application health
- Error rates
- Request throughput
- Resource utilization

**Usage:**
```bash
# Start monitoring
python scripts/monitoring/monitor.py

# Monitor specific host
python scripts/monitoring/monitor.py --host localhost --port 8080

# Export metrics
python scripts/monitoring/monitor.py --export prometheus
```

**Output:**
- Console metrics (real-time)
- Prometheus metrics export
- Alert notifications

### monitoring_dashboard.py
Web-based monitoring dashboard with visualization.

**Features:**
- Real-time metrics display
- Historical charts
- Alert management
- System health overview
- Custom metric tracking

**Usage:**
```bash
python scripts/monitoring/monitoring_dashboard.py
```

**Access:**
Dashboard available at `http://localhost:8090`

**Views:**
- System Overview
- Application Metrics
- Error Tracking
- Performance Trends
- Alert History

### error_analysis_dashboard.py
Specialized dashboard for error tracking and analysis.

**Features:**
- Error aggregation and grouping
- Stack trace analysis
- Error frequency trends
- Root cause identification
- Alert configuration

**Usage:**
```bash
python scripts/monitoring/error_analysis_dashboard.py
```

**Access:**
Dashboard available at `http://localhost:8091`

**Features:**
- Error severity classification
- Automatic error grouping
- Timeline visualization
- Export error reports
- Integration with alerting

## Requirements

```bash
uv sync --extra dev
```

Additional requirements:
- psutil (system metrics)
- prometheus-client (metrics export)

## Configuration

Create `monitoring_config.yaml`:
```yaml
monitoring:
  enabled: true
  interval: 60  # seconds
  metrics:
    - cpu
    - memory
    - disk
    - network

  alerts:
    cpu_threshold: 80
    memory_threshold: 85
    error_rate_threshold: 10
```

## Monitoring Workflow

1. **Start monitoring:**
   ```bash
   python scripts/monitoring/monitor.py &
   ```

2. **Open dashboards:**
   ```bash
   python scripts/monitoring/monitoring_dashboard.py &
   python scripts/monitoring/error_analysis_dashboard.py &
   ```

3. **Access dashboards:**
   - Main: http://localhost:8090
   - Errors: http://localhost:8091

4. **Configure alerts** via dashboard UI

## Integration

### Prometheus
```bash
# Start monitor with Prometheus export
python scripts/monitoring/monitor.py --export prometheus --port 8081
```

Then configure Prometheus to scrape `http://localhost:8081/metrics`

### Grafana
Import the dashboard templates from `deployment/grafana/`

## See Also

- [MONITORING.md](../../MONITORING.md) - Monitoring documentation
- [ERROR_TRACKING.md](../../ERROR_TRACKING.md) - Error tracking guide
