# Health Checks and System Monitoring

This document provides comprehensive guidance for the health checking and system monitoring capabilities of the Customer Solution Snapshot Generator.

## Overview

The monitoring system provides enterprise-grade observability with:

- **Comprehensive Health Checks**: Multi-layered health validation
- **Real-time System Monitoring**: Resource and performance tracking
- **Advanced Alerting**: Multi-channel notifications with escalation
- **Performance Monitoring**: Memory optimization and performance tracking
- **Interactive Dashboard**: Real-time monitoring visualization
- **Integration Support**: Prometheus, Grafana, and external systems

## Quick Start

### Basic Health Check

```bash
# Simple health check
python healthcheck.py

# Advanced monitoring dashboard
python monitoring_dashboard.py --mode interactive

# Generate monitoring report
python monitoring_dashboard.py --mode report --output health_report.json
```

### Start Monitoring Services

```bash
# Start all monitoring services
python -c "
from src.customer_snapshot.monitoring.system_monitor import SystemMonitor
from src.customer_snapshot.utils.config import Config
monitor = SystemMonitor(Config.get_default())
monitor.start()
"
```

## Health Check System

### Health Check Categories

1. **System Resources Health Check**
   - CPU usage monitoring
   - Memory consumption tracking
   - Disk space validation
   - System load assessment

2. **Application Health Check**
   - Core module import validation
   - NLP model availability
   - Configuration validation
   - Functional testing

3. **Dependency Health Check**
   - External API connectivity
   - Filesystem permissions
   - Python environment validation
   - Database connectivity (if configured)

4. **Performance Health Check**
   - Processing performance testing
   - Memory usage patterns
   - System load monitoring
   - Response time validation

### Health Status Levels

- **HEALTHY**: All systems operational
- **WARNING**: Issues detected but service functional
- **CRITICAL**: Serious issues affecting functionality
- **UNKNOWN**: Unable to determine status

### Usage Examples

```python
from src.customer_snapshot.monitoring.health_monitor import HealthMonitor

# Initialize health monitor
health_monitor = HealthMonitor()

# Run all health checks
results = health_monitor.run_all_checks()

# Get overall status
overall_status = health_monitor.get_overall_status()

# Get detailed health summary
summary = health_monitor.get_health_summary()
```

## System Monitoring

### Metrics Collection

The system collects three categories of metrics:

1. **System Metrics**
   - CPU usage (total and per-core)
   - Memory usage (RSS, VMS, available)
   - Disk usage and free space
   - Network I/O statistics
   - Load average
   - Process count

2. **Application Metrics**
   - Application CPU and memory usage
   - Thread count
   - File descriptor usage
   - Application uptime
   - Processing statistics

3. **Business Metrics**
   - Files processed count
   - Processing duration
   - Error rates
   - Cache hit rates

### Configuration

Configure monitoring through `monitoring_config.yaml`:

```yaml
system_monitoring:
  enabled: true
  collection_interval: 10  # seconds

  prometheus:
    enabled: true
    port: 8081

  metrics:
    system_metrics: true
    application_metrics: true
    business_metrics: true
```

### Prometheus Integration

Enable Prometheus metrics export:

```yaml
system_monitoring:
  prometheus:
    enabled: true
    port: 8081
    path: "/metrics"
```

Access metrics at: `http://localhost:8081/metrics`

### Usage Examples

```python
from src.customer_snapshot.monitoring.system_monitor import SystemMonitor

# Initialize system monitor
system_monitor = SystemMonitor()

# Start monitoring
system_monitor.start()

# Get current metrics
metrics = system_monitor.get_metrics_snapshot()

# Get monitoring status
status = system_monitor.get_status()
```

## Alerting System

### Alert Rules

Configure alerting rules in `monitoring_config.yaml`:

```yaml
alerting:
  rules:
    - name: "high_cpu_usage"
      metric: "system_cpu_usage_percent"
      condition: "greater_than"
      threshold: 85.0
      severity: "warning"
      message: "High CPU usage detected"
```

### Notification Channels

#### Email Notifications

```yaml
notifications:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "alerts@example.com"
    password: "app_password"
    recipients:
      - "admin@example.com"
```

#### Slack Notifications

```yaml
notifications:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/..."
    channel: "#alerts"
    severity_filter: ["warning", "critical"]
```

#### Webhook Notifications

```yaml
notifications:
  webhook:
    enabled: true
    url: "https://api.external-system.com/alerts"
    method: "POST"
    headers:
      Content-Type: "application/json"
      Authorization: "Bearer token"
```

### Alert Escalation

Configure escalation policies:

```yaml
escalation:
  rules:
    - name: "critical_escalation"
      condition: "time_based"
      threshold: 15  # minutes
      action: "escalate"
      target: "emergency"
```

### Usage Examples

```python
from src.customer_snapshot.monitoring.alerting import AlertingService

# Initialize alerting service
alerting = AlertingService()

# Start alert processing
alerting.start()

# Send custom alert
from src.customer_snapshot.monitoring.system_monitor import Alert
alert = Alert(
    name="custom_alert",
    level="WARNING",
    message="Custom alert message",
    details={"key": "value"}
)
alerting.send_alert(alert)
```

## Monitoring Dashboard

### Interactive Dashboard

Start the interactive monitoring dashboard:

```bash
python monitoring_dashboard.py --mode interactive --interval 5
```

**Dashboard Features:**
- Real-time health status
- System resource monitoring
- Performance metrics
- Alert notifications
- Historical trends

**Dashboard Commands:**
- `r` - Refresh display
- `s` - Start/restart monitoring services
- `q` - Quit dashboard

### Dashboard Modes

```bash
# Interactive mode
python monitoring_dashboard.py --mode interactive

# Status snapshot
python monitoring_dashboard.py --mode status --json

# Health check only
python monitoring_dashboard.py --mode health

# Generate report
python monitoring_dashboard.py --mode report --output report.json
```

### Example Output

```
================================================================================
🔍 CUSTOMER SOLUTION SNAPSHOT GENERATOR - MONITORING DASHBOARD
================================================================================
📅 Last Updated: 2024-01-15T10:30:00
🔧 Monitoring Available: ✅ Yes

🌡️  OVERALL STATUS: ✅ HEALTHY

🏥 HEALTH CHECKS
----------------------------------------
   ✅ System Resources
      Status: HEALTHY
      Message: System resources healthy
      Response Time: 245.3ms

   ✅ Application
      Status: HEALTHY
      Message: Application healthy
      Response Time: 156.7ms

💻 SYSTEM MONITORING
----------------------------------------
   🔍 Monitoring Active: ✅ Yes
   📊 Prometheus: ✅ Running
   🌡️  Health Status: HEALTHY

📈 PERFORMANCE METRICS
----------------------------------------
   🖥️  CPU Usage: ✅ 23.4%
   🧠 Memory Usage: ✅ 45.2%
   💾 Disk Usage: ✅ 67.8%
   💿 Free Space: 125.3 GB
   ⏱️  Uptime: 24.7 hours
```

## Configuration

### Environment Variables

Configure monitoring through environment variables:

```bash
# Health monitoring
export ENABLE_HEALTH_MONITORING=true
export HEALTH_CHECK_INTERVAL=30

# System monitoring
export ENABLE_SYSTEM_MONITORING=true
export METRICS_COLLECTION_INTERVAL=10
export PROMETHEUS_ENABLED=true
export PROMETHEUS_PORT=8081

# Alerting
export ENABLE_ALERTING=true
export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."
export EMAIL_ALERTS_ENABLED=true
export SMTP_SERVER="smtp.gmail.com"
export ALERT_EMAIL_RECIPIENTS="admin@example.com,ops@example.com"

# Dashboard
export MONITORING_DASHBOARD_PORT=8080
export DASHBOARD_REFRESH_INTERVAL=5
```

### Configuration File

Use `monitoring_config.yaml` for detailed configuration:

```yaml
# Load configuration
from src.customer_snapshot.utils.config import Config
config = Config.get_default()

# Override with monitoring config
import yaml
with open('monitoring_config.yaml') as f:
    monitoring_config = yaml.safe_load(f)
```

## Docker Integration

### Health Checks in Docker

The Docker container includes built-in health checks:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python /usr/local/bin/healthcheck.py
```

### Docker Compose Monitoring

```yaml
services:
  customer-snapshot-generator:
    image: customer-snapshot-generator:latest
    healthcheck:
      test: ["CMD", "python", "/usr/local/bin/healthcheck.py"]
      interval: 30s
      timeout: 10s
      retries: 3
    environment:
      - ENABLE_HEALTH_MONITORING=true
      - PROMETHEUS_ENABLED=true
      - PROMETHEUS_PORT=8081
    ports:
      - "8080:8080"
      - "8081:8081"  # Prometheus metrics
```

### Kubernetes Health Checks

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: customer-snapshot-generator
    image: customer-snapshot-generator:latest
    livenessProbe:
      exec:
        command:
        - python
        - /usr/local/bin/healthcheck.py
      initialDelaySeconds: 60
      periodSeconds: 30
    readinessProbe:
      exec:
        command:
        - python
        - /usr/local/bin/healthcheck.py
      initialDelaySeconds: 30
      periodSeconds: 10
```

## Integration with External Systems

### Prometheus Integration

1. **Enable Prometheus exporter:**
```python
from src.customer_snapshot.monitoring.system_monitor import SystemMonitor
monitor = SystemMonitor()
monitor.start()  # Starts Prometheus exporter on port 8081
```

2. **Configure Prometheus scraping:**
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'customer-snapshot-generator'
    static_configs:
      - targets: ['localhost:8081']
    scrape_interval: 15s
```

### Grafana Dashboards

Import the included Grafana dashboard:

```bash
# Import dashboard JSON
curl -X POST \
  http://grafana:3000/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -d @grafana_dashboard.json
```

### Datadog Integration

```python
# Configure Datadog metrics
import datadog
datadog.initialize(api_key='your_api_key', app_key='your_app_key')

# Send custom metrics
from datadog import statsd
statsd.gauge('customer_snapshot.health_score', 95)
```

## Troubleshooting

### Common Issues

**Health Checks Failing:**
```bash
# Debug health checks
python healthcheck.py --verbose

# Check specific component
python -c "
from src.customer_snapshot.monitoring.health_monitor import SystemResourcesHealthCheck
check = SystemResourcesHealthCheck()
result = check.check()
print(result.message)
"
```

**Monitoring Not Starting:**
```bash
# Check monitoring status
python monitoring_dashboard.py --mode status

# Verify configuration
python -c "
from src.customer_snapshot.utils.config import Config
config = Config.get_default()
print('Monitoring enabled:', getattr(config, 'enable_monitoring', False))
"
```

**Prometheus Metrics Not Available:**
```bash
# Test metrics endpoint
curl http://localhost:8081/metrics

# Check if service is running
netstat -tlnp | grep 8081
```

**Alerts Not Sending:**
```bash
# Test alerting service
python -c "
from src.customer_snapshot.monitoring.alerting import AlertingService
service = AlertingService()
status = service.get_notification_status()
print(status)
"
```

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python monitoring_dashboard.py --mode interactive
```

### Health Check Bypass

For debugging, temporarily disable health checks:

```bash
export DISABLE_HEALTH_CHECKS=true
```

## Performance Considerations

### Resource Usage

The monitoring system is designed to be lightweight:

- **CPU Impact**: < 5% additional CPU usage
- **Memory Impact**: < 100MB additional memory
- **Network Impact**: Minimal (only for alerts/metrics export)
- **Disk Impact**: Configurable log rotation

### Optimization Tips

1. **Adjust Collection Intervals:**
```yaml
system_monitoring:
  collection_interval: 30  # Increase for lower resource usage
```

2. **Limit Metrics Retention:**
```yaml
system_monitoring:
  metrics_retention: 3600  # 1 hour instead of 24 hours
```

3. **Disable Unused Features:**
```yaml
performance:
  benchmarking:
    enabled: false  # Disable if not needed
```

4. **Configure Alert Aggregation:**
```yaml
alerting:
  aggregation_window: 600  # 10 minutes (longer window = fewer alerts)
```

## Security Considerations

### Access Control

Secure monitoring endpoints:

```yaml
security:
  api_auth:
    enabled: true
    method: "token"
    tokens:
      - "secure_monitoring_token"
```

### Sensitive Data

Monitoring logs are automatically sanitized:
- API keys are redacted
- Personal information is masked
- Error details are filtered

### Network Security

Configure firewalls for monitoring ports:

```bash
# Allow Prometheus metrics (internal only)
iptables -A INPUT -p tcp --dport 8081 -s 10.0.0.0/8 -j ACCEPT

# Allow dashboard (authenticated users only)
iptables -A INPUT -p tcp --dport 8080 -s trusted_network -j ACCEPT
```

## Best Practices

### Development

- Enable verbose health checks during development
- Use debug dashboard mode
- Test alert configurations
- Validate monitoring configurations

### Staging

- Enable email alerts to staging team
- Test escalation policies
- Validate external integrations
- Monitor performance impact

### Production

- Enable all monitoring features
- Configure proper alert thresholds
- Set up external monitoring integration
- Implement proper access controls
- Schedule regular monitoring reviews

### Maintenance

- Regular log rotation
- Periodic configuration reviews
- Alert threshold adjustments
- Performance baseline updates
- Security audit of monitoring components

## Support

For monitoring-related issues:

1. **Check monitoring dashboard**: `python monitoring_dashboard.py --mode status`
2. **Review health checks**: `python healthcheck.py --verbose`
3. **Validate configuration**: Review `monitoring_config.yaml`
4. **Check logs**: Review monitoring and application logs
5. **Test components**: Use individual monitoring component tests

---

*This monitoring system provides enterprise-grade observability for the Customer Solution Snapshot Generator, ensuring reliable operation and proactive issue detection.*
