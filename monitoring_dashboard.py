#!/usr/bin/env python3
"""
Comprehensive monitoring dashboard for Customer Solution Snapshot Generator.

This script provides a unified interface for monitoring system health,
performance metrics, alerts, and overall system status.
"""

import os
import sys
import json
import time
import argparse
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import psutil
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

from src.customer_snapshot.monitoring.health_monitor import HealthMonitor, HealthStatus
from src.customer_snapshot.monitoring.system_monitor import SystemMonitor
from src.customer_snapshot.monitoring.alerting import AlertingService
from src.customer_snapshot.utils.config import Config


class MonitoringDashboard:
    """Comprehensive monitoring dashboard."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.get_default()
        
        # Initialize monitoring components
        self.health_monitor = HealthMonitor(self.config)
        self.system_monitor = SystemMonitor(self.config)
        self.alerting_service = AlertingService(self.config)
        
        # Dashboard state
        self.running = False
        self.refresh_interval = 5  # seconds
        
    def start_monitoring(self):
        """Start all monitoring services."""
        print("🚀 Starting monitoring services...")
        
        try:
            self.system_monitor.start()
            self.alerting_service.start()
            print("✅ All monitoring services started successfully")
            
        except Exception as e:
            print(f"❌ Failed to start monitoring services: {e}")
            raise
    
    def stop_monitoring(self):
        """Stop all monitoring services."""
        print("⏹️  Stopping monitoring services...")
        
        try:
            self.system_monitor.stop()
            self.alerting_service.stop()
            print("✅ All monitoring services stopped")
            
        except Exception as e:
            print(f"❌ Error stopping monitoring services: {e}")
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        try:
            health_summary = self.health_monitor.get_health_summary()
            system_status = self.system_monitor.get_status()
            alerting_status = self.alerting_service.get_notification_status()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_status": health_summary.get("overall_status", "unknown"),
                "health": health_summary,
                "system": system_status,
                "alerting": alerting_status,
                "monitoring_available": MONITORING_AVAILABLE
            }
            
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "error": f"Failed to get status: {e}",
                "overall_status": "unknown"
            }
    
    def display_dashboard(self):
        """Display comprehensive monitoring dashboard."""
        try:
            # Clear screen
            os.system('clear' if os.name == 'posix' else 'cls')
            
            status = self.get_comprehensive_status()
            
            # Header
            print("=" * 80)
            print("🔍 CUSTOMER SOLUTION SNAPSHOT GENERATOR - MONITORING DASHBOARD")
            print("=" * 80)
            print(f"📅 Last Updated: {status['timestamp']}")
            print(f"🔧 Monitoring Available: {'✅ Yes' if status['monitoring_available'] else '❌ Limited'}")
            print()
            
            # Overall Status
            overall_status = status.get("overall_status", "unknown")
            status_emoji = {
                "healthy": "✅",
                "warning": "⚠️",
                "critical": "🚨",
                "unknown": "❓"
            }
            
            print(f"🌡️  OVERALL STATUS: {status_emoji.get(overall_status, '❓')} {overall_status.upper()}")
            print()
            
            # Health Checks
            self._display_health_section(status.get("health", {}))
            
            # System Metrics
            self._display_system_section(status.get("system", {}))
            
            # Alerting Status
            self._display_alerting_section(status.get("alerting", {}))
            
            # Performance Summary
            self._display_performance_section(status)
            
            print("=" * 80)
            print("💡 Commands: [r]efresh, [s]tart monitoring, [q]uit")
            print("=" * 80)
            
        except Exception as e:
            print(f"❌ Error displaying dashboard: {e}")
    
    def _display_health_section(self, health_data: Dict[str, Any]):
        """Display health check section."""
        print("🏥 HEALTH CHECKS")
        print("-" * 40)
        
        if not health_data or "checks" not in health_data:
            print("   No health data available")
            print()
            return
        
        checks = health_data.get("checks", {})
        summary = health_data.get("summary", {})
        
        # Display individual checks
        for check_name, check_result in checks.items():
            status = check_result.get("status", "unknown")
            message = check_result.get("message", "No message")
            response_time = check_result.get("response_time_ms", 0)
            
            status_symbol = {
                "healthy": "✅",
                "warning": "⚠️", 
                "critical": "🚨",
                "unknown": "❓"
            }.get(status, "❓")
            
            print(f"   {status_symbol} {check_name.replace('_', ' ').title()}")
            print(f"      Status: {status.upper()}")
            print(f"      Message: {message}")
            print(f"      Response Time: {response_time:.1f}ms")
            print()
        
        # Display summary
        total_checks = summary.get("total_checks", 0)
        healthy_checks = summary.get("healthy_checks", 0)
        warning_checks = summary.get("warning_checks", 0)
        critical_checks = summary.get("critical_checks", 0)
        
        print(f"   📊 Summary: {healthy_checks}/{total_checks} healthy")
        if warning_checks > 0:
            print(f"   ⚠️  Warnings: {warning_checks}")
        if critical_checks > 0:
            print(f"   🚨 Critical: {critical_checks}")
        print()
    
    def _display_system_section(self, system_data: Dict[str, Any]):
        """Display system monitoring section."""
        print("💻 SYSTEM MONITORING")
        print("-" * 40)
        
        if not system_data:
            print("   No system data available")
            print()
            return
        
        # Monitoring status
        monitoring_enabled = system_data.get("monitoring_enabled", False)
        prometheus_enabled = system_data.get("prometheus_enabled", False)
        prometheus_running = system_data.get("prometheus_running", False)
        
        print(f"   🔍 Monitoring Active: {'✅ Yes' if monitoring_enabled else '❌ No'}")
        print(f"   📊 Prometheus: {'✅ Running' if prometheus_running else '❌ Stopped' if prometheus_enabled else '⚪ Disabled'}")
        
        # Health status from system monitor
        health_info = system_data.get("health", {})
        if health_info:
            overall_status = health_info.get("overall_status", "unknown")
            print(f"   🌡️  Health Status: {overall_status.upper()}")
        
        print()
    
    def _display_alerting_section(self, alerting_data: Dict[str, Any]):
        """Display alerting section."""
        print("🚨 ALERTING SYSTEM")
        print("-" * 40)
        
        if not alerting_data:
            print("   No alerting data available")
            print()
            return
        
        processing_enabled = alerting_data.get("processing_enabled", False)
        queue_size = alerting_data.get("queue_size", 0)
        total_notifications = alerting_data.get("total_notifications", 0)
        recent_notifications = alerting_data.get("recent_notifications", 0)
        active_notifiers = alerting_data.get("active_notifiers", [])
        
        print(f"   🔄 Processing: {'✅ Active' if processing_enabled else '❌ Stopped'}")
        print(f"   📬 Queue Size: {queue_size}")
        print(f"   📧 Total Notifications: {total_notifications}")
        print(f"   📬 Recent (24h): {recent_notifications}")
        
        if active_notifiers:
            notifier_names = [str(n).split('.')[-1] for n in active_notifiers]
            print(f"   📢 Active Channels: {', '.join(notifier_names)}")
        else:
            print(f"   📢 Active Channels: None configured")
        
        print()
    
    def _display_performance_section(self, status_data: Dict[str, Any]):
        """Display performance metrics section."""
        print("📈 PERFORMANCE METRICS")
        print("-" * 40)
        
        if not MONITORING_AVAILABLE:
            print("   ⚠️  Limited performance data (psutil not available)")
            print()
            return
        
        try:
            # Get current system metrics
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Display metrics with color coding
            print(f"   🖥️  CPU Usage: {self._format_metric_with_status(cpu_percent, 70, 90)}%")
            print(f"   🧠 Memory Usage: {self._format_metric_with_status(memory.percent, 80, 95)}%")
            print(f"   💾 Disk Usage: {self._format_metric_with_status((disk.used/disk.total)*100, 80, 95)}%")
            print(f"   💿 Free Space: {disk.free / (1024**3):.1f} GB")
            
            # Load average (if available)
            if hasattr(os, 'getloadavg'):
                try:
                    load_avg = os.getloadavg()
                    cpu_count = psutil.cpu_count()
                    load_percent = (load_avg[0] / cpu_count) * 100
                    print(f"   ⚡ Load Average: {self._format_metric_with_status(load_percent, 100, 200)}% (1m)")
                except OSError:
                    pass
            
            # Process info
            try:
                current_process = psutil.Process()
                uptime = time.time() - current_process.create_time()
                uptime_hours = uptime / 3600
                print(f"   ⏱️  Uptime: {uptime_hours:.1f} hours")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            
        except Exception as e:
            print(f"   ❌ Error getting performance metrics: {e}")
        
        print()
    
    def _format_metric_with_status(self, value: float, warning_threshold: float, critical_threshold: float) -> str:
        """Format metric value with status indicator."""
        if value >= critical_threshold:
            return f"🚨 {value:.1f}"
        elif value >= warning_threshold:
            return f"⚠️  {value:.1f}"
        else:
            return f"✅ {value:.1f}"
    
    def interactive_mode(self):
        """Run dashboard in interactive mode."""
        self.running = True
        
        print("🚀 Starting Customer Solution Snapshot Generator Monitoring Dashboard")
        print("=" * 80)
        
        try:
            # Start monitoring services
            self.start_monitoring()
            
            while self.running:
                # Display dashboard
                self.display_dashboard()
                
                # Wait for user input or auto-refresh
                import select
                import sys
                
                if select.select([sys.stdin], [], [], self.refresh_interval) == ([sys.stdin], [], []):
                    user_input = input().strip().lower()
                    
                    if user_input == 'q':
                        self.running = False
                    elif user_input == 'r':
                        continue  # Refresh immediately
                    elif user_input == 's':
                        try:
                            self.start_monitoring()
                            print("✅ Monitoring services restarted")
                            time.sleep(2)
                        except Exception as e:
                            print(f"❌ Failed to start monitoring: {e}")
                            time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n⏹️  Dashboard interrupted by user")
        finally:
            self.stop_monitoring()
            print("👋 Monitoring dashboard stopped")
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """Generate monitoring report."""
        status = self.get_comprehensive_status()
        
        # Create detailed report
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "generator": "Customer Solution Snapshot Generator Monitoring Dashboard",
                "version": "1.0.0"
            },
            "system_status": status
        }
        
        # Add historical data if available
        try:
            health_trends = self.health_monitor.get_health_trends(hours=24)
            report["health_trends"] = health_trends
        except Exception as e:
            report["health_trends_error"] = str(e)
        
        # Save report
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"monitoring_report_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Monitoring report saved to: {output_file}")
        return output_file
    
    def health_check_only(self) -> bool:
        """Run health check only and return True if healthy."""
        try:
            overall_status = self.health_monitor.get_overall_status()
            return overall_status == HealthStatus.HEALTHY
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False


def main():
    """Main dashboard application."""
    parser = argparse.ArgumentParser(description="Customer Solution Snapshot Generator Monitoring Dashboard")
    parser.add_argument('--mode', choices=['interactive', 'status', 'health', 'report'], 
                       default='interactive', help='Dashboard mode')
    parser.add_argument('--output', help='Output file for reports')
    parser.add_argument('--interval', type=int, default=5, help='Refresh interval for interactive mode')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    args = parser.parse_args()
    
    try:
        # Initialize dashboard
        config = Config.get_default()
        dashboard = MonitoringDashboard(config)
        dashboard.refresh_interval = args.interval
        
        if args.mode == 'interactive':
            dashboard.interactive_mode()
            
        elif args.mode == 'status':
            status = dashboard.get_comprehensive_status()
            if args.json:
                print(json.dumps(status, indent=2))
            else:
                dashboard.display_dashboard()
                
        elif args.mode == 'health':
            is_healthy = dashboard.health_check_only()
            if args.json:
                print(json.dumps({"healthy": is_healthy}))
            else:
                print(f"Health Status: {'✅ HEALTHY' if is_healthy else '❌ UNHEALTHY'}")
            return 0 if is_healthy else 1
            
        elif args.mode == 'report':
            report_file = dashboard.generate_report(args.output)
            if not args.json:
                print(f"✅ Report generated: {report_file}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️  Dashboard interrupted by user")
        return 0
    except Exception as e:
        print(f"💥 Dashboard failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())