#!/usr/bin/env python3
"""
Performance Dashboard for Customer Solution Snapshot Generator.

This script provides a comprehensive performance monitoring and analysis dashboard
that combines benchmarking, monitoring, and optimization capabilities.
"""

import time
import os
import sys
import json
import argparse
import webbrowser
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import tempfile

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import our performance modules
from benchmark import BenchmarkRunner
from monitor import PerformanceMonitor
from optimize import PerformanceProfiler

try:
    import psutil
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

from customer_snapshot.utils.config import Config


class PerformanceDashboard:
    """Comprehensive performance dashboard and analysis system."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.get_default()
        self.benchmark_runner = BenchmarkRunner(config)
        self.monitor = PerformanceMonitor(config)
        self.profiler = PerformanceProfiler(config)
        
        # Dashboard state
        self.is_monitoring = False
        self.dashboard_data = {
            'benchmark_results': [],
            'monitoring_data': [],
            'optimization_reports': [],
            'alerts': []
        }
        
    def run_quick_benchmark(self) -> Dict[str, Any]:
        """Run a quick benchmark suite."""
        print("🚀 Running quick benchmark suite...")
        
        # Small test sizes for quick results
        test_sizes = [0.1, 0.5, 1.0]  # MB
        
        results = self.benchmark_runner.run_benchmark_suite(test_sizes)
        
        # Add to dashboard data
        self.dashboard_data['benchmark_results'].append({
            'timestamp': datetime.now().isoformat(),
            'results': results.__dict__
        })
        
        return results.__dict__
    
    def start_monitoring(self):
        """Start continuous performance monitoring."""
        if self.is_monitoring:
            print("⚠️  Monitoring already active")
            return
        
        print("🔍 Starting performance monitoring...")
        self.monitor.start_monitoring()
        self.is_monitoring = True
        
        # Start data collection thread
        self.monitor_thread = threading.Thread(target=self._collect_monitoring_data)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print("✅ Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        if not self.is_monitoring:
            return
        
        print("⏹️  Stopping performance monitoring...")
        self.monitor.stop_monitoring()
        self.is_monitoring = False
        print("✅ Performance monitoring stopped")
    
    def _collect_monitoring_data(self):
        """Collect monitoring data in background."""
        while self.is_monitoring:
            try:
                # Get current status
                status = self.monitor.get_current_status()
                
                # Add to dashboard data
                self.dashboard_data['monitoring_data'].append({
                    'timestamp': datetime.now().isoformat(),
                    'status': status
                })
                
                # Keep only recent data (last 1000 entries)
                if len(self.dashboard_data['monitoring_data']) > 1000:
                    self.dashboard_data['monitoring_data'] = self.dashboard_data['monitoring_data'][-1000:]
                
                time.sleep(10)  # Collect every 10 seconds
                
            except Exception as e:
                print(f"Error collecting monitoring data: {e}")
                time.sleep(10)
    
    def run_optimization_analysis(self) -> Dict[str, Any]:
        """Run comprehensive optimization analysis."""
        print("⚡ Running optimization analysis...")
        
        # Run profiling with different file sizes
        test_sizes = [0.5, 1.0]  # MB
        reports = []
        
        for size in test_sizes:
            print(f"   Profiling with {size:.1f} MB file...")
            report = self.profiler.run_comprehensive_profile(size)
            reports.append(report.__dict__)
        
        # Add to dashboard data
        self.dashboard_data['optimization_reports'].append({
            'timestamp': datetime.now().isoformat(),
            'reports': reports
        })
        
        return reports
    
    def generate_html_report(self, output_file: str = None) -> str:
        """Generate HTML dashboard report."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"performance_dashboard_{timestamp}.html"
        
        html_content = self._create_html_dashboard()
        
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        return output_file
    
    def _create_html_dashboard(self) -> str:
        """Create HTML dashboard content."""
        # Get latest data
        latest_benchmark = self.dashboard_data['benchmark_results'][-1] if self.dashboard_data['benchmark_results'] else None
        latest_monitoring = self.dashboard_data['monitoring_data'][-10:] if self.dashboard_data['monitoring_data'] else []
        latest_optimization = self.dashboard_data['optimization_reports'][-1] if self.dashboard_data['optimization_reports'] else None
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Performance Dashboard - Customer Solution Snapshot Generator</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2980B9, #3498DB);
            color: white;
            padding: 2rem 0;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        
        .header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }}
        
        .card {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #3498DB;
        }}
        
        .card h2 {{
            color: #2980B9;
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }}
        
        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid #eee;
        }}
        
        .metric:last-child {{
            border-bottom: none;
        }}
        
        .metric-label {{
            font-weight: 500;
            color: #555;
        }}
        
        .metric-value {{
            font-weight: bold;
            color: #2980B9;
        }}
        
        .status-good {{
            color: #27AE60;
        }}
        
        .status-warning {{
            color: #F39C12;
        }}
        
        .status-critical {{
            color: #E74C3C;
        }}
        
        .chart-placeholder {{
            background: #f8f9fa;
            border: 2px dashed #dee2e6;
            border-radius: 4px;
            padding: 2rem;
            text-align: center;
            color: #6c757d;
            margin: 1rem 0;
        }}
        
        .recommendations {{
            background: #e8f5e8;
            border: 1px solid #c3e6c3;
            border-radius: 4px;
            padding: 1rem;
            margin-top: 1rem;
        }}
        
        .recommendations h3 {{
            color: #155724;
            margin-bottom: 0.5rem;
        }}
        
        .recommendations ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        
        .recommendations li {{
            padding: 0.25rem 0;
            color: #155724;
        }}
        
        .recommendations li:before {{
            content: "💡 ";
            margin-right: 0.5rem;
        }}
        
        .timestamp {{
            font-size: 0.9rem;
            color: #6c757d;
            text-align: right;
            margin-top: 1rem;
        }}
        
        @media (max-width: 768px) {{
            .dashboard-grid {{
                grid-template-columns: 1fr;
            }}
            
            .container {{
                padding: 1rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Performance Dashboard</h1>
        <p>Customer Solution Snapshot Generator</p>
    </div>
    
    <div class="container">
        <div class="dashboard-grid">
            <!-- System Overview -->
            <div class="card">
                <h2>📊 System Overview</h2>
                <div class="metric">
                    <span class="metric-label">Dashboard Generated</span>
                    <span class="metric-value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Monitoring Available</span>
                    <span class="metric-value {'status-good' if MONITORING_AVAILABLE else 'status-warning'}">
                        {'✅ Yes' if MONITORING_AVAILABLE else '⚠️ Limited'}
                    </span>
                </div>
                <div class="metric">
                    <span class="metric-label">Python Version</span>
                    <span class="metric-value">{sys.version.split()[0]}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Platform</span>
                    <span class="metric-value">{sys.platform}</span>
                </div>
            </div>
            
            <!-- Benchmark Results -->
            <div class="card">
                <h2>🏃 Benchmark Results</h2>
                {self._render_benchmark_section(latest_benchmark)}
            </div>
            
            <!-- Monitoring Status -->
            <div class="card">
                <h2>🔍 Monitoring Status</h2>
                {self._render_monitoring_section(latest_monitoring)}
            </div>
            
            <!-- Optimization Analysis -->
            <div class="card">
                <h2>⚡ Optimization Analysis</h2>
                {self._render_optimization_section(latest_optimization)}
            </div>
            
            <!-- Performance Trends -->
            <div class="card">
                <h2>📈 Performance Trends</h2>
                <div class="chart-placeholder">
                    <p>📊 Performance trend visualization would appear here</p>
                    <p>Consider integrating with Chart.js or similar for interactive charts</p>
                </div>
            </div>
            
            <!-- Recommendations -->
            <div class="card">
                <h2>💡 Recommendations</h2>
                {self._render_recommendations_section()}
            </div>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds if monitoring is active
        setInterval(() => {{
            if (document.querySelector('.monitoring-active')) {{
                location.reload();
            }}
        }}, 30000);
    </script>
</body>
</html>
        """
        
        return html
    
    def _render_benchmark_section(self, benchmark_data: Optional[Dict]) -> str:
        """Render benchmark results section."""
        if not benchmark_data:
            return """
                <div class="metric">
                    <span class="metric-label">Status</span>
                    <span class="metric-value status-warning">No benchmark data available</span>
                </div>
                <p>Run benchmark suite to see performance metrics.</p>
            """
        
        results = benchmark_data.get('results', {})
        summary = results.get('summary_stats', {})
        
        if not summary:
            return "<p>No benchmark summary available</p>"
        
        processing_time = summary.get('processing_time', {})
        memory_usage = summary.get('memory_usage', {})
        throughput = summary.get('throughput', {})
        
        return f"""
            <div class="metric">
                <span class="metric-label">Tests Completed</span>
                <span class="metric-value status-good">{summary.get('successful_tests', 0)}/{summary.get('total_tests', 0)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Avg Processing Time</span>
                <span class="metric-value">{processing_time.get('mean', 0):.2f}s</span>
            </div>
            <div class="metric">
                <span class="metric-label">Peak Memory Usage</span>
                <span class="metric-value">{memory_usage.get('peak_max', 0):.1f} MB</span>
            </div>
            <div class="metric">
                <span class="metric-label">Throughput</span>
                <span class="metric-value">{throughput.get('mb_per_second', 0):.2f} MB/s</span>
            </div>
            <div class="timestamp">Last run: {benchmark_data.get('timestamp', 'Unknown')}</div>
        """
    
    def _render_monitoring_section(self, monitoring_data: List[Dict]) -> str:
        """Render monitoring status section."""
        if not monitoring_data:
            return """
                <div class="metric">
                    <span class="metric-label">Status</span>
                    <span class="metric-value status-warning">No monitoring data available</span>
                </div>
                <p>Start monitoring to see real-time performance metrics.</p>
            """
        
        latest = monitoring_data[-1] if monitoring_data else {}
        status = latest.get('status', {})
        
        if not status:
            return "<p>No monitoring status available</p>"
        
        monitoring_active = status.get('monitoring_active', False)
        system_metrics = status.get('system_metrics', {})
        
        return f"""
            <div class="metric">
                <span class="metric-label">Monitoring Active</span>
                <span class="metric-value {'status-good' if monitoring_active else 'status-warning'}">
                    {'✅ Yes' if monitoring_active else '⚠️ No'}
                </span>
            </div>
            <div class="metric">
                <span class="metric-label">CPU Usage</span>
                <span class="metric-value">{system_metrics.get('cpu_percent', 0):.1f}%</span>
            </div>
            <div class="metric">
                <span class="metric-label">Memory Usage</span>
                <span class="metric-value">{system_metrics.get('memory_percent', 0):.1f}%</span>
            </div>
            <div class="metric">
                <span class="metric-label">Recent Alerts</span>
                <span class="metric-value">{status.get('recent_alerts', 0)}</span>
            </div>
            <div class="timestamp">Last update: {latest.get('timestamp', 'Unknown')}</div>
        """
    
    def _render_optimization_section(self, optimization_data: Optional[Dict]) -> str:
        """Render optimization analysis section."""
        if not optimization_data:
            return """
                <div class="metric">
                    <span class="metric-label">Status</span>
                    <span class="metric-value status-warning">No optimization data available</span>
                </div>
                <p>Run optimization analysis to identify performance bottlenecks.</p>
            """
        
        reports = optimization_data.get('reports', [])
        if not reports:
            return "<p>No optimization reports available</p>"
        
        # Use the first report for display
        report = reports[0]
        
        return f"""
            <div class="metric">
                <span class="metric-label">Execution Time</span>
                <span class="metric-value">{report.get('total_execution_time', 0):.2f}s</span>
            </div>
            <div class="metric">
                <span class="metric-label">Peak Memory</span>
                <span class="metric-value">{report.get('peak_memory_mb', 0):.1f} MB</span>
            </div>
            <div class="metric">
                <span class="metric-label">Bottlenecks Found</span>
                <span class="metric-value">{len(report.get('bottlenecks', []))}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Recommendations</span>
                <span class="metric-value">{len(report.get('recommendations', []))}</span>
            </div>
            <div class="timestamp">Last analysis: {optimization_data.get('timestamp', 'Unknown')}</div>
        """
    
    def _render_recommendations_section(self) -> str:
        """Render recommendations section."""
        recommendations = [
            "Run benchmarks regularly to track performance trends",
            "Monitor system resources during peak usage",
            "Profile code to identify performance bottlenecks",
            "Consider caching for frequently accessed data",
            "Implement batch processing for large files",
            "Use appropriate data structures for your use case",
            "Monitor memory usage patterns for potential leaks",
            "Consider async processing for I/O-bound operations"
        ]
        
        recommendations_html = "\n".join([f"<li>{rec}</li>" for rec in recommendations])
        
        return f"""
            <div class="recommendations">
                <h3>General Performance Tips</h3>
                <ul>
                    {recommendations_html}
                </ul>
            </div>
        """
    
    def run_comprehensive_analysis(self):
        """Run comprehensive performance analysis."""
        print("🔍 Starting comprehensive performance analysis...")
        print("=" * 60)
        
        # Run benchmark suite
        print("\n1. Running benchmark suite...")
        self.run_quick_benchmark()
        
        # Run optimization analysis
        print("\n2. Running optimization analysis...")
        self.run_optimization_analysis()
        
        # Generate HTML report
        print("\n3. Generating HTML dashboard...")
        html_file = self.generate_html_report()
        
        print(f"\n✅ Comprehensive analysis completed!")
        print(f"📄 HTML dashboard: {html_file}")
        
        return html_file
    
    def save_dashboard_data(self, output_file: str = None):
        """Save dashboard data to JSON file."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"dashboard_data_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(self.dashboard_data, f, indent=2)
        
        print(f"📁 Dashboard data saved to: {output_file}")
        return output_file


def main():
    """Main dashboard application."""
    parser = argparse.ArgumentParser(description="Performance Dashboard for Customer Solution Snapshot Generator")
    parser.add_argument('--mode', choices=['benchmark', 'monitor', 'optimize', 'dashboard', 'comprehensive'], 
                       default='comprehensive', help='Operating mode')
    parser.add_argument('--output', help='Output file for reports')
    parser.add_argument('--duration', type=int, default=60, help='Monitoring duration in seconds')
    parser.add_argument('--open', action='store_true', help='Open HTML report in browser')
    
    args = parser.parse_args()
    
    print("📊 Customer Solution Snapshot Generator - Performance Dashboard")
    print("=" * 70)
    
    if not MONITORING_AVAILABLE:
        print("⚠️  Warning: Advanced monitoring not available.")
        print("   Install with: pip install psutil memory-profiler line-profiler")
        print("   Basic functionality will still work.\n")
    
    try:
        # Initialize dashboard
        config = Config.get_default()
        dashboard = PerformanceDashboard(config)
        
        if args.mode == 'benchmark':
            print("🏃 Running benchmark suite...")
            dashboard.run_quick_benchmark()
            
        elif args.mode == 'monitor':
            print(f"🔍 Starting monitoring for {args.duration} seconds...")
            dashboard.start_monitoring()
            time.sleep(args.duration)
            dashboard.stop_monitoring()
            
        elif args.mode == 'optimize':
            print("⚡ Running optimization analysis...")
            dashboard.run_optimization_analysis()
            
        elif args.mode == 'dashboard':
            print("📊 Generating HTML dashboard...")
            html_file = dashboard.generate_html_report(args.output)
            if args.open:
                webbrowser.open(f"file://{os.path.abspath(html_file)}")
            
        else:  # comprehensive
            print("🔍 Running comprehensive performance analysis...")
            html_file = dashboard.run_comprehensive_analysis()
            if args.open:
                webbrowser.open(f"file://{os.path.abspath(html_file)}")
        
        # Save dashboard data
        dashboard.save_dashboard_data()
        
        print(f"\n🎉 Performance dashboard completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Dashboard interrupted by user")
        if 'dashboard' in locals():
            dashboard.stop_monitoring()
    except Exception as e:
        print(f"\n💥 Dashboard failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())