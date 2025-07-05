#!/usr/bin/env python3
"""
System monitoring script for Customer Solution Snapshot Generator.

This script provides real-time monitoring of system performance,
resource usage, and application health metrics.
"""

import time
import os
import sys
import json
import signal
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import queue

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import psutil
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    print("Warning: psutil not available. Install with: pip install psutil")

from customer_snapshot.utils.config import Config


@dataclass
class SystemMetrics:
    """System performance metrics snapshot."""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    process_count: int
    load_average: Optional[List[float]] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ApplicationMetrics:
    """Application-specific metrics."""
    timestamp: str
    process_id: int
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    threads: int
    files_open: int
    status: str
    uptime_seconds: float
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class PerformanceAlert:
    """Performance alert definition."""
    timestamp: str
    level: str  # INFO, WARNING, CRITICAL
    metric: str
    value: float
    threshold: float
    message: str
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class SystemMonitor:
    """Monitors system-level performance metrics."""
    
    def __init__(self):
        self.running = False
        self.metrics_history = []
        self.max_history = 1000  # Keep last 1000 readings
        
    def get_current_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        if not MONITORING_AVAILABLE:
            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=0,
                memory_percent=0,
                memory_used_mb=0,
                memory_available_mb=0,
                disk_usage_percent=0,
                disk_free_gb=0,
                process_count=0
            )
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        memory_used_mb = memory.used / 1024 / 1024
        memory_available_mb = memory.available / 1024 / 1024
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_usage_percent = (disk.used / disk.total) * 100
        disk_free_gb = disk.free / 1024 / 1024 / 1024
        
        # Process count
        process_count = len(psutil.pids())
        
        # Load average (Unix/Linux only)
        load_average = None
        if hasattr(os, 'getloadavg'):
            try:
                load_average = list(os.getloadavg())
            except OSError:
                pass
        
        return SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory_used_mb,
            memory_available_mb=memory_available_mb,
            disk_usage_percent=disk_usage_percent,
            disk_free_gb=disk_free_gb,
            process_count=process_count,
            load_average=load_average
        )
    
    def add_metrics(self, metrics: SystemMetrics):
        """Add metrics to history."""
        self.metrics_history.append(metrics)
        
        # Keep only recent history
        if len(self.metrics_history) > self.max_history:
            self.metrics_history = self.metrics_history[-self.max_history:]
    
    def get_metrics_summary(self, minutes: int = 5) -> Dict[str, Any]:
        """Get metrics summary for the last N minutes."""
        if not self.metrics_history:
            return {}
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m.timestamp) >= cutoff_time
        ]
        
        if not recent_metrics:
            return {}
        
        cpu_values = [m.cpu_percent for m in recent_metrics]
        memory_values = [m.memory_percent for m in recent_metrics]
        
        return {
            'time_period_minutes': minutes,
            'samples': len(recent_metrics),
            'cpu': {
                'average': sum(cpu_values) / len(cpu_values),
                'min': min(cpu_values),
                'max': max(cpu_values),
                'current': recent_metrics[-1].cpu_percent
            },
            'memory': {
                'average': sum(memory_values) / len(memory_values),
                'min': min(memory_values),
                'max': max(memory_values),
                'current': recent_metrics[-1].memory_percent
            },
            'disk_free_gb': recent_metrics[-1].disk_free_gb,
            'timestamp': recent_metrics[-1].timestamp
        }


class ApplicationMonitor:
    """Monitors application-specific metrics."""
    
    def __init__(self, process_name: str = "customer-snapshot"):
        self.process_name = process_name
        self.monitored_process = None
        self.start_time = None
        
    def find_process(self) -> Optional[psutil.Process]:
        """Find the application process."""
        if not MONITORING_AVAILABLE:
            return None
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if self.process_name in proc.info['name']:
                    return proc
                if proc.info['cmdline'] and any(self.process_name in arg for arg in proc.info['cmdline']):
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    def get_current_metrics(self) -> Optional[ApplicationMetrics]:
        """Get current application metrics."""
        if not MONITORING_AVAILABLE:
            return None
        
        proc = self.find_process()
        if not proc:
            return None
        
        try:
            # Get process info
            with proc.oneshot():
                cpu_percent = proc.cpu_percent()
                memory_info = proc.memory_info()
                memory_percent = proc.memory_percent()
                threads = proc.num_threads()
                
                # Get file descriptors (Unix/Linux only)
                try:
                    files_open = proc.num_fds()
                except (AttributeError, psutil.AccessDenied):
                    files_open = 0
                
                # Calculate uptime
                create_time = proc.create_time()
                uptime_seconds = time.time() - create_time
                
                return ApplicationMetrics(
                    timestamp=datetime.now().isoformat(),
                    process_id=proc.pid,
                    cpu_percent=cpu_percent,
                    memory_mb=memory_info.rss / 1024 / 1024,
                    memory_percent=memory_percent,
                    threads=threads,
                    files_open=files_open,
                    status=proc.status(),
                    uptime_seconds=uptime_seconds
                )
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"Error getting process metrics: {e}")
            return None


class AlertManager:
    """Manages performance alerts and notifications."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.get_default()
        self.alerts = []
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_usage_percent': 90.0,
            'disk_free_gb': 1.0,
            'process_memory_mb': 1024.0
        }
        
    def check_system_alerts(self, metrics: SystemMetrics) -> List[PerformanceAlert]:
        """Check for system-level alerts."""
        alerts = []
        
        # CPU usage alert
        if metrics.cpu_percent > self.alert_thresholds['cpu_percent']:
            alerts.append(PerformanceAlert(
                timestamp=datetime.now().isoformat(),
                level='WARNING',
                metric='cpu_percent',
                value=metrics.cpu_percent,
                threshold=self.alert_thresholds['cpu_percent'],
                message=f"High CPU usage: {metrics.cpu_percent:.1f}%"
            ))
        
        # Memory usage alert
        if metrics.memory_percent > self.alert_thresholds['memory_percent']:
            alerts.append(PerformanceAlert(
                timestamp=datetime.now().isoformat(),
                level='WARNING',
                metric='memory_percent',
                value=metrics.memory_percent,
                threshold=self.alert_thresholds['memory_percent'],
                message=f"High memory usage: {metrics.memory_percent:.1f}%"
            ))
        
        # Disk usage alert
        if metrics.disk_usage_percent > self.alert_thresholds['disk_usage_percent']:
            alerts.append(PerformanceAlert(
                timestamp=datetime.now().isoformat(),
                level='CRITICAL',
                metric='disk_usage_percent',
                value=metrics.disk_usage_percent,
                threshold=self.alert_thresholds['disk_usage_percent'],
                message=f"High disk usage: {metrics.disk_usage_percent:.1f}%"
            ))
        
        # Low disk space alert
        if metrics.disk_free_gb < self.alert_thresholds['disk_free_gb']:
            alerts.append(PerformanceAlert(
                timestamp=datetime.now().isoformat(),
                level='CRITICAL',
                metric='disk_free_gb',
                value=metrics.disk_free_gb,
                threshold=self.alert_thresholds['disk_free_gb'],
                message=f"Low disk space: {metrics.disk_free_gb:.1f} GB free"
            ))
        
        return alerts
    
    def check_application_alerts(self, metrics: ApplicationMetrics) -> List[PerformanceAlert]:
        """Check for application-level alerts."""
        alerts = []
        
        # Application memory usage
        if metrics.memory_mb > self.alert_thresholds['process_memory_mb']:
            alerts.append(PerformanceAlert(
                timestamp=datetime.now().isoformat(),
                level='WARNING',
                metric='process_memory_mb',
                value=metrics.memory_mb,
                threshold=self.alert_thresholds['process_memory_mb'],
                message=f"High application memory usage: {metrics.memory_mb:.1f} MB"
            ))
        
        return alerts
    
    def process_alerts(self, alerts: List[PerformanceAlert]):
        """Process and handle alerts."""
        for alert in alerts:
            self.alerts.append(alert)
            self.log_alert(alert)
    
    def log_alert(self, alert: PerformanceAlert):
        """Log an alert."""
        level_emoji = {
            'INFO': '📘',
            'WARNING': '⚠️',
            'CRITICAL': '🚨'
        }
        
        print(f"{level_emoji.get(alert.level, '📋')} {alert.level}: {alert.message}")
        
        # Log to file if configured
        if hasattr(self.config, 'log_file') and self.config.log_file:
            logging.basicConfig(
                filename=self.config.log_file,
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
            logging.info(f"ALERT {alert.level}: {alert.message}")


class PerformanceMonitor:
    """Main performance monitoring coordinator."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.get_default()
        self.system_monitor = SystemMonitor()
        self.app_monitor = ApplicationMonitor()
        self.alert_manager = AlertManager(config)
        
        self.running = False
        self.monitor_thread = None
        self.metrics_queue = queue.Queue()
        
        # Monitoring settings
        self.monitor_interval = 10  # seconds
        self.report_interval = 300  # seconds (5 minutes)
        self.last_report_time = time.time()
        
    def start_monitoring(self):
        """Start the monitoring system."""
        if self.running:
            print("Monitoring already running")
            return
        
        print("🔍 Starting performance monitoring...")
        print(f"   Monitor interval: {self.monitor_interval} seconds")
        print(f"   Report interval: {self.report_interval} seconds")
        print(f"   Monitoring available: {MONITORING_AVAILABLE}")
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print("✅ Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring system."""
        if not self.running:
            return
        
        print("⏹️  Stopping performance monitoring...")
        self.running = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        print("✅ Performance monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                # Collect system metrics
                system_metrics = self.system_monitor.get_current_metrics()
                self.system_monitor.add_metrics(system_metrics)
                
                # Collect application metrics
                app_metrics = self.app_monitor.get_current_metrics()
                
                # Check for alerts
                system_alerts = self.alert_manager.check_system_alerts(system_metrics)
                app_alerts = []
                if app_metrics:
                    app_alerts = self.alert_manager.check_application_alerts(app_metrics)
                
                # Process alerts
                all_alerts = system_alerts + app_alerts
                if all_alerts:
                    self.alert_manager.process_alerts(all_alerts)
                
                # Generate periodic reports
                current_time = time.time()
                if current_time - self.last_report_time >= self.report_interval:
                    self._generate_report()
                    self.last_report_time = current_time
                
                # Store metrics in queue for external access
                self.metrics_queue.put({
                    'system': system_metrics,
                    'application': app_metrics,
                    'alerts': all_alerts
                })
                
                time.sleep(self.monitor_interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(self.monitor_interval)
    
    def _generate_report(self):
        """Generate a periodic performance report."""
        print("\n" + "=" * 50)
        print(f"📊 PERFORMANCE REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # System summary
        summary = self.system_monitor.get_metrics_summary(minutes=5)
        if summary:
            print(f"🖥️  System (last {summary['time_period_minutes']} minutes):")
            print(f"   CPU: {summary['cpu']['current']:.1f}% current, "
                  f"{summary['cpu']['average']:.1f}% avg, "
                  f"{summary['cpu']['max']:.1f}% peak")
            print(f"   Memory: {summary['memory']['current']:.1f}% current, "
                  f"{summary['memory']['average']:.1f}% avg, "
                  f"{summary['memory']['max']:.1f}% peak")
            print(f"   Disk free: {summary['disk_free_gb']:.1f} GB")
        
        # Application status
        app_metrics = self.app_monitor.get_current_metrics()
        if app_metrics:
            print(f"🚀 Application:")
            print(f"   Process ID: {app_metrics.process_id}")
            print(f"   Status: {app_metrics.status}")
            print(f"   Memory: {app_metrics.memory_mb:.1f} MB")
            print(f"   CPU: {app_metrics.cpu_percent:.1f}%")
            print(f"   Uptime: {app_metrics.uptime_seconds / 3600:.1f} hours")
        else:
            print("🚀 Application: Not found or not running")
        
        # Recent alerts
        recent_alerts = [
            alert for alert in self.alert_manager.alerts
            if datetime.fromisoformat(alert.timestamp) > datetime.now() - timedelta(minutes=5)
        ]
        
        if recent_alerts:
            print(f"🚨 Recent alerts ({len(recent_alerts)}):")
            for alert in recent_alerts[-5:]:  # Show last 5 alerts
                print(f"   {alert.level}: {alert.message}")
        else:
            print("✅ No recent alerts")
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current monitoring status."""
        system_metrics = self.system_monitor.get_current_metrics()
        app_metrics = self.app_monitor.get_current_metrics()
        
        return {
            'monitoring_active': self.running,
            'system_metrics': asdict(system_metrics),
            'application_metrics': asdict(app_metrics) if app_metrics else None,
            'recent_alerts': len([
                alert for alert in self.alert_manager.alerts
                if datetime.fromisoformat(alert.timestamp) > datetime.now() - timedelta(minutes=5)
            ]),
            'total_alerts': len(self.alert_manager.alerts)
        }


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    print("\n🛑 Received shutdown signal")
    if 'monitor' in globals():
        monitor.stop_monitoring()
    exit(0)


def main():
    """Main monitoring application."""
    print("📈 Customer Solution Snapshot Generator - Performance Monitor")
    print("=" * 60)
    
    if not MONITORING_AVAILABLE:
        print("❌ Error: psutil not available.")
        print("   Install with: pip install psutil")
        return 1
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize monitor
        config = Config.get_default()
        global monitor
        monitor = PerformanceMonitor(config)
        
        # Start monitoring
        monitor.start_monitoring()
        
        # Keep the main thread alive
        print("🔄 Monitoring active. Press Ctrl+C to stop.")
        while monitor.running:
            time.sleep(1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped by user")
    except Exception as e:
        print(f"💥 Monitoring failed: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())