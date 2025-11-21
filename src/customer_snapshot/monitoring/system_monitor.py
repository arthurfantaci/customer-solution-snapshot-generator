"""
System monitoring service for Customer Solution Snapshot Generator.

This module provides comprehensive system monitoring including metrics collection,
alerting, and performance tracking with integration to external monitoring systems.
"""

import logging
import os
import queue
import sys
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Optional


try:
    import psutil
    import requests

    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ..utils.config import Config
from .health_monitor import HealthMonitor


logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """A single metric data point."""

    name: str
    value: float
    timestamp: str
    labels: dict[str, str]
    unit: str = ""

    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class Alert:
    """System alert definition."""

    name: str
    level: str  # INFO, WARNING, CRITICAL
    message: str
    timestamp: str
    details: dict[str, Any]
    resolved: bool = False

    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class MetricsCollector:
    """Collects various system and application metrics."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize metrics collector.

        Args:
            config: Configuration object (default: Config.get_default()).
        """
        self.config = config or Config.get_default()
        self.collection_interval = 10  # seconds
        self.metrics_buffer = queue.Queue(maxsize=10000)
        self.running = False

    def collect_system_metrics(self) -> list[MetricPoint]:
        """Collect system-level metrics."""
        metrics = []
        timestamp = datetime.now().isoformat()

        if not MONITORING_AVAILABLE:
            return metrics

        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics.append(
                MetricPoint(
                    name="system_cpu_usage_percent",
                    value=cpu_percent,
                    timestamp=timestamp,
                    labels={"type": "total"},
                    unit="percent",
                )
            )

            # Per-CPU metrics
            cpu_percents = psutil.cpu_percent(percpu=True)
            for i, cpu_pct in enumerate(cpu_percents):
                metrics.append(
                    MetricPoint(
                        name="system_cpu_usage_percent",
                        value=cpu_pct,
                        timestamp=timestamp,
                        labels={"type": "per_cpu", "cpu": str(i)},
                        unit="percent",
                    )
                )

            # Memory metrics
            memory = psutil.virtual_memory()
            metrics.extend(
                [
                    MetricPoint(
                        name="system_memory_usage_bytes",
                        value=memory.used,
                        timestamp=timestamp,
                        labels={"type": "used"},
                        unit="bytes",
                    ),
                    MetricPoint(
                        name="system_memory_usage_bytes",
                        value=memory.available,
                        timestamp=timestamp,
                        labels={"type": "available"},
                        unit="bytes",
                    ),
                    MetricPoint(
                        name="system_memory_usage_percent",
                        value=memory.percent,
                        timestamp=timestamp,
                        labels={"type": "usage"},
                        unit="percent",
                    ),
                ]
            )

            # Disk metrics
            disk = psutil.disk_usage("/")
            metrics.extend(
                [
                    MetricPoint(
                        name="system_disk_usage_bytes",
                        value=disk.used,
                        timestamp=timestamp,
                        labels={"type": "used", "mount": "/"},
                        unit="bytes",
                    ),
                    MetricPoint(
                        name="system_disk_usage_bytes",
                        value=disk.free,
                        timestamp=timestamp,
                        labels={"type": "free", "mount": "/"},
                        unit="bytes",
                    ),
                    MetricPoint(
                        name="system_disk_usage_percent",
                        value=(disk.used / disk.total) * 100,
                        timestamp=timestamp,
                        labels={"mount": "/"},
                        unit="percent",
                    ),
                ]
            )

            # Network metrics
            net_io = psutil.net_io_counters()
            if net_io:
                metrics.extend(
                    [
                        MetricPoint(
                            name="system_network_bytes_total",
                            value=net_io.bytes_sent,
                            timestamp=timestamp,
                            labels={"direction": "sent"},
                            unit="bytes",
                        ),
                        MetricPoint(
                            name="system_network_bytes_total",
                            value=net_io.bytes_recv,
                            timestamp=timestamp,
                            labels={"direction": "received"},
                            unit="bytes",
                        ),
                        MetricPoint(
                            name="system_network_packets_total",
                            value=net_io.packets_sent,
                            timestamp=timestamp,
                            labels={"direction": "sent"},
                            unit="packets",
                        ),
                        MetricPoint(
                            name="system_network_packets_total",
                            value=net_io.packets_recv,
                            timestamp=timestamp,
                            labels={"direction": "received"},
                            unit="packets",
                        ),
                    ]
                )

            # Load average (Unix/Linux only)
            if hasattr(os, "getloadavg"):
                try:
                    load_avg = os.getloadavg()
                    for i, period in enumerate(["1m", "5m", "15m"]):
                        metrics.append(
                            MetricPoint(
                                name="system_load_average",
                                value=load_avg[i],
                                timestamp=timestamp,
                                labels={"period": period},
                                unit="",
                            )
                        )
                except OSError:
                    pass

            # Process count
            process_count = len(psutil.pids())
            metrics.append(
                MetricPoint(
                    name="system_processes_total",
                    value=process_count,
                    timestamp=timestamp,
                    labels={},
                    unit="count",
                )
            )

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

        return metrics

    def collect_application_metrics(self) -> list[MetricPoint]:
        """Collect application-specific metrics."""
        metrics = []
        timestamp = datetime.now().isoformat()

        if not MONITORING_AVAILABLE:
            return metrics

        try:
            # Find application process
            current_process = psutil.Process()

            # Application CPU and memory
            cpu_percent = current_process.cpu_percent()
            memory_info = current_process.memory_info()
            memory_percent = current_process.memory_percent()

            metrics.extend(
                [
                    MetricPoint(
                        name="application_cpu_usage_percent",
                        value=cpu_percent,
                        timestamp=timestamp,
                        labels={"process": "customer_snapshot"},
                        unit="percent",
                    ),
                    MetricPoint(
                        name="application_memory_usage_bytes",
                        value=memory_info.rss,
                        timestamp=timestamp,
                        labels={"process": "customer_snapshot", "type": "rss"},
                        unit="bytes",
                    ),
                    MetricPoint(
                        name="application_memory_usage_bytes",
                        value=memory_info.vms,
                        timestamp=timestamp,
                        labels={"process": "customer_snapshot", "type": "vms"},
                        unit="bytes",
                    ),
                    MetricPoint(
                        name="application_memory_usage_percent",
                        value=memory_percent,
                        timestamp=timestamp,
                        labels={"process": "customer_snapshot"},
                        unit="percent",
                    ),
                ]
            )

            # Thread count
            try:
                thread_count = current_process.num_threads()
                metrics.append(
                    MetricPoint(
                        name="application_threads_total",
                        value=thread_count,
                        timestamp=timestamp,
                        labels={"process": "customer_snapshot"},
                        unit="count",
                    )
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

            # File descriptors (Unix/Linux only)
            try:
                fd_count = current_process.num_fds()
                metrics.append(
                    MetricPoint(
                        name="application_file_descriptors_total",
                        value=fd_count,
                        timestamp=timestamp,
                        labels={"process": "customer_snapshot"},
                        unit="count",
                    )
                )
            except (AttributeError, psutil.NoSuchProcess, psutil.AccessDenied):
                pass

            # Uptime
            create_time = current_process.create_time()
            uptime_seconds = time.time() - create_time
            metrics.append(
                MetricPoint(
                    name="application_uptime_seconds",
                    value=uptime_seconds,
                    timestamp=timestamp,
                    labels={"process": "customer_snapshot"},
                    unit="seconds",
                )
            )

        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")

        return metrics

    def collect_business_metrics(self) -> list[MetricPoint]:
        """Collect business/application-specific metrics."""
        metrics = []
        timestamp = datetime.now().isoformat()

        # These would be populated by the application
        # For now, we'll add placeholders

        # File processing metrics (would be updated by the application)
        metrics.extend(
            [
                MetricPoint(
                    name="files_processed_total",
                    value=0,  # Would be updated by application
                    timestamp=timestamp,
                    labels={"type": "vtt"},
                    unit="count",
                ),
                MetricPoint(
                    name="processing_duration_seconds",
                    value=0,  # Would be updated by application
                    timestamp=timestamp,
                    labels={"type": "average"},
                    unit="seconds",
                ),
                MetricPoint(
                    name="processing_errors_total",
                    value=0,  # Would be updated by application
                    timestamp=timestamp,
                    labels={"type": "all"},
                    unit="count",
                ),
            ]
        )

        return metrics

    def collect_all_metrics(self) -> list[MetricPoint]:
        """Collect all available metrics."""
        all_metrics = []

        try:
            all_metrics.extend(self.collect_system_metrics())
            all_metrics.extend(self.collect_application_metrics())
            all_metrics.extend(self.collect_business_metrics())
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")

        return all_metrics


class AlertManager:
    """Manages system alerts and notifications."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize alert manager.

        Args:
            config: Configuration object (default: Config.get_default()).
        """
        self.config = config or Config.get_default()
        self.alerts = []
        self.alert_rules = self._initialize_alert_rules()
        self.max_alerts = 1000

    def _initialize_alert_rules(self) -> list[dict[str, Any]]:
        """Initialize default alert rules."""
        return [
            {
                "name": "high_cpu_usage",
                "metric": "system_cpu_usage_percent",
                "condition": "greater_than",
                "threshold": 85.0,
                "level": "WARNING",
                "message": "High CPU usage detected",
            },
            {
                "name": "critical_cpu_usage",
                "metric": "system_cpu_usage_percent",
                "condition": "greater_than",
                "threshold": 95.0,
                "level": "CRITICAL",
                "message": "Critical CPU usage detected",
            },
            {
                "name": "high_memory_usage",
                "metric": "system_memory_usage_percent",
                "condition": "greater_than",
                "threshold": 80.0,
                "level": "WARNING",
                "message": "High memory usage detected",
            },
            {
                "name": "critical_memory_usage",
                "metric": "system_memory_usage_percent",
                "condition": "greater_than",
                "threshold": 95.0,
                "level": "CRITICAL",
                "message": "Critical memory usage detected",
            },
            {
                "name": "high_disk_usage",
                "metric": "system_disk_usage_percent",
                "condition": "greater_than",
                "threshold": 85.0,
                "level": "WARNING",
                "message": "High disk usage detected",
            },
            {
                "name": "critical_disk_usage",
                "metric": "system_disk_usage_percent",
                "condition": "greater_than",
                "threshold": 95.0,
                "level": "CRITICAL",
                "message": "Critical disk usage detected",
            },
            {
                "name": "application_high_memory",
                "metric": "application_memory_usage_percent",
                "condition": "greater_than",
                "threshold": 75.0,
                "level": "WARNING",
                "message": "Application using high memory",
            },
        ]

    def evaluate_alerts(self, metrics: list[MetricPoint]) -> list[Alert]:
        """Evaluate metrics against alert rules."""
        new_alerts = []

        for rule in self.alert_rules:
            try:
                # Find relevant metrics
                relevant_metrics = [m for m in metrics if m.name == rule["metric"]]

                for metric in relevant_metrics:
                    triggered = self._evaluate_condition(
                        metric.value, rule["condition"], rule["threshold"]
                    )

                    if triggered:
                        alert = Alert(
                            name=rule["name"],
                            level=rule["level"],
                            message=f"{rule['message']}: {metric.value:.1f}{metric.unit}",
                            timestamp=datetime.now().isoformat(),
                            details={
                                "metric_name": metric.name,
                                "metric_value": metric.value,
                                "threshold": rule["threshold"],
                                "labels": metric.labels,
                            },
                        )
                        new_alerts.append(alert)

            except Exception as e:
                logger.error(f"Error evaluating alert rule {rule['name']}: {e}")

        # Add to alerts list
        self.alerts.extend(new_alerts)

        # Limit alerts history
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[-self.max_alerts :]

        return new_alerts

    def _evaluate_condition(
        self, value: float, condition: str, threshold: float
    ) -> bool:
        """Evaluate alert condition."""
        if condition == "greater_than":
            return value > threshold
        elif condition == "less_than":
            return value < threshold
        elif condition == "equals":
            return abs(value - threshold) < 0.001
        else:
            return False

    def get_active_alerts(self) -> list[Alert]:
        """Get currently active (unresolved) alerts."""
        return [alert for alert in self.alerts if not alert.resolved]

    def resolve_alert(self, alert_name: str):
        """Mark alerts as resolved."""
        for alert in self.alerts:
            if alert.name == alert_name and not alert.resolved:
                alert.resolved = True

    def get_alert_summary(self) -> dict[str, Any]:
        """Get alert summary statistics."""
        active_alerts = self.get_active_alerts()

        return {
            "total_alerts": len(self.alerts),
            "active_alerts": len(active_alerts),
            "critical_alerts": len([a for a in active_alerts if a.level == "CRITICAL"]),
            "warning_alerts": len([a for a in active_alerts if a.level == "WARNING"]),
            "info_alerts": len([a for a in active_alerts if a.level == "INFO"]),
            "latest_alert": self.alerts[-1].timestamp if self.alerts else None,
        }


class PrometheusExporter:
    """Exports metrics in Prometheus format."""

    def __init__(self, port: int = 8081, bind_address: str = "127.0.0.1"):
        """Initialize Prometheus exporter.

        Args:
            port: Port to bind the metrics server to.
            bind_address: IP address to bind to (default: localhost for security).
        """
        self.port = port
        self.bind_address = bind_address  # Default to localhost for security
        self.server = None
        self.running = False

    def format_metrics(self, metrics: list[MetricPoint]) -> str:
        """Format metrics in Prometheus exposition format."""
        output = []

        # Group metrics by name
        metrics_by_name = {}
        for metric in metrics:
            if metric.name not in metrics_by_name:
                metrics_by_name[metric.name] = []
            metrics_by_name[metric.name].append(metric)

        for metric_name, metric_list in metrics_by_name.items():
            # Add help and type info
            output.append(f"# HELP {metric_name} Auto-generated metric")
            output.append(f"# TYPE {metric_name} gauge")

            for metric in metric_list:
                # Format labels
                if metric.labels:
                    labels_str = ",".join(
                        [f'{k}="{v}"' for k, v in metric.labels.items()]
                    )
                    metric_line = f"{metric_name}{{{labels_str}}} {metric.value}"
                else:
                    metric_line = f"{metric_name} {metric.value}"

                output.append(metric_line)

        return "\n".join(output) + "\n"

    def start_server(self, metrics_collector: MetricsCollector):
        """Start Prometheus metrics server."""
        try:
            from http.server import BaseHTTPRequestHandler, HTTPServer

            class MetricsHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == "/metrics":
                        try:
                            metrics = metrics_collector.collect_all_metrics()
                            prometheus_output = self.server.exporter.format_metrics(
                                metrics
                            )

                            self.send_response(200)
                            self.send_header(
                                "Content-Type", "text/plain; charset=utf-8"
                            )
                            self.end_headers()
                            self.wfile.write(prometheus_output.encode("utf-8"))
                        except Exception as e:
                            logger.error(f"Error generating metrics: {e}")
                            self.send_error(500, f"Internal server error: {e}")
                    else:
                        self.send_error(404, "Not found")

                def log_message(self, format, *args):
                    # Suppress HTTP server logs
                    pass

            # Bind to specified address (default: localhost for security)
            self.server = HTTPServer((self.bind_address, self.port), MetricsHandler)
            self.server.exporter = self

            # Start server in thread
            server_thread = threading.Thread(target=self.server.serve_forever)
            server_thread.daemon = True
            server_thread.start()

            self.running = True
            logger.info(
                f"Prometheus metrics server started on {self.bind_address}:{self.port}"
            )

        except Exception as e:
            logger.error(f"Failed to start Prometheus server: {e}")

    def stop_server(self):
        """Stop Prometheus metrics server."""
        if self.server:
            self.server.shutdown()
            self.server = None
            self.running = False
            logger.info("Prometheus metrics server stopped")


class SystemMonitor:
    """Main system monitoring coordinator."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize system monitor.

        Args:
            config: Configuration object (default: Config.get_default()).
        """
        self.config = config or Config.get_default()
        self.health_monitor = HealthMonitor(config)
        self.metrics_collector = MetricsCollector(config)
        self.alert_manager = AlertManager(config)
        self.prometheus_exporter = None

        self.monitoring_enabled = False
        self.monitor_thread = None
        self.collection_interval = 30  # seconds

        # Enable Prometheus exporter if configured
        if getattr(config, "enable_prometheus_metrics", False):
            prometheus_port = getattr(config, "prometheus_port", 8081)
            self.prometheus_exporter = PrometheusExporter(prometheus_port)

    def start(self):
        """Start all monitoring services."""
        logger.info("Starting system monitoring...")

        # Start health monitoring
        self.health_monitor.start_monitoring()

        # Start Prometheus exporter
        if self.prometheus_exporter:
            self.prometheus_exporter.start_server(self.metrics_collector)

        # Start main monitoring loop
        self.monitoring_enabled = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        logger.info("System monitoring started successfully")

    def stop(self):
        """Stop all monitoring services."""
        logger.info("Stopping system monitoring...")

        # Stop monitoring loop
        self.monitoring_enabled = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        # Stop health monitoring
        self.health_monitor.stop_monitoring()

        # Stop Prometheus exporter
        if self.prometheus_exporter:
            self.prometheus_exporter.stop_server()

        logger.info("System monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_enabled:
            try:
                # Collect metrics
                metrics = self.metrics_collector.collect_all_metrics()

                # Evaluate alerts
                new_alerts = self.alert_manager.evaluate_alerts(metrics)

                # Log new alerts
                for alert in new_alerts:
                    if alert.level == "CRITICAL":
                        logger.error(f"CRITICAL ALERT: {alert.message}")
                    elif alert.level == "WARNING":
                        logger.warning(f"WARNING ALERT: {alert.message}")
                    else:
                        logger.info(f"INFO ALERT: {alert.message}")

                # Log monitoring status periodically
                if len(metrics) > 0:
                    logger.debug(f"Collected {len(metrics)} metrics")

                time.sleep(self.collection_interval)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.collection_interval)

    def get_status(self) -> dict[str, Any]:
        """Get comprehensive monitoring status."""
        health_summary = self.health_monitor.get_health_summary()
        alert_summary = self.alert_manager.get_alert_summary()

        return {
            "monitoring_enabled": self.monitoring_enabled,
            "timestamp": datetime.now().isoformat(),
            "health": health_summary,
            "alerts": alert_summary,
            "prometheus_enabled": self.prometheus_exporter is not None,
            "prometheus_running": self.prometheus_exporter.running
            if self.prometheus_exporter
            else False,
        }

    def get_metrics_snapshot(self) -> dict[str, Any]:
        """Get current metrics snapshot."""
        metrics = self.metrics_collector.collect_all_metrics()

        return {
            "timestamp": datetime.now().isoformat(),
            "metrics_count": len(metrics),
            "metrics": [asdict(metric) for metric in metrics],
        }
