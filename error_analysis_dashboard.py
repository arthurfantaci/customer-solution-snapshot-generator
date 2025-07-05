#!/usr/bin/env python3
"""
Error Analysis Dashboard for Customer Solution Snapshot Generator.

This dashboard provides comprehensive error analysis, tracking, and management
capabilities with real-time monitoring and historical analysis.
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.customer_snapshot.monitoring.error_tracker import (
    ErrorTracker, ErrorSeverity, ErrorCategory, ErrorContext, get_error_tracker
)
from src.customer_snapshot.utils.config import Config


class ErrorAnalysisDashboard:
    """Comprehensive error analysis dashboard."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.get_default()
        self.error_tracker = get_error_tracker()
        self.refresh_interval = 10  # seconds
        self.running = False
    
    def display_dashboard(self):
        """Display comprehensive error analysis dashboard."""
        try:
            # Clear screen
            os.system('clear' if os.name == 'posix' else 'cls')
            
            # Get error statistics
            stats = self.error_tracker.get_error_stats()
            recent_errors = self.error_tracker.get_recent_errors(hours=24)
            
            # Header
            print("=" * 80)
            print("🔍 CUSTOMER SOLUTION SNAPSHOT GENERATOR - ERROR ANALYSIS DASHBOARD")
            print("=" * 80)
            print(f"📅 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
            # Overall Statistics
            self._display_overall_stats(stats)
            
            # Error Severity Breakdown
            self._display_severity_breakdown(stats)
            
            # Error Categories
            self._display_category_breakdown(stats)
            
            # Recent Errors
            self._display_recent_errors(recent_errors[:10])
            
            # Top Errors
            self._display_top_errors(stats.top_errors)
            
            # Error Trends
            self._display_error_trends()
            
            print("=" * 80)
            print("💡 Commands: [r]efresh, [e]xport, [v]iew error, [s]tats, [q]uit")
            print("=" * 80)
            
        except Exception as e:
            print(f"❌ Error displaying dashboard: {e}")
    
    def _display_overall_stats(self, stats):
        """Display overall error statistics."""
        print("📊 OVERALL ERROR STATISTICS")
        print("-" * 40)
        print(f"   📈 Total Errors: {stats.total_errors}")
        print(f"   ⚡ Current Error Rate: {stats.error_rate:.2f} errors/second")
        print(f"   🔄 Resolution Rate: {stats.resolution_rate:.1%}")
        
        if stats.mean_time_to_resolution > 0:
            mttr_hours = stats.mean_time_to_resolution / 3600
            print(f"   ⏱️  Mean Time to Resolution: {mttr_hours:.1f} hours")
        
        print()
    
    def _display_severity_breakdown(self, stats):
        """Display error severity breakdown."""
        print("🚨 ERROR SEVERITY BREAKDOWN")
        print("-" * 40)
        
        severity_order = ['fatal', 'critical', 'error', 'warning', 'info', 'debug']
        severity_icons = {
            'fatal': '💀',
            'critical': '🚨',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'debug': '🐛'
        }
        
        total_by_severity = sum(stats.errors_by_severity.values())
        
        for severity in severity_order:
            count = stats.errors_by_severity.get(severity, 0)
            if count > 0:
                percentage = (count / total_by_severity) * 100 if total_by_severity > 0 else 0
                icon = severity_icons.get(severity, '❓')
                print(f"   {icon} {severity.upper()}: {count} ({percentage:.1f}%)")
        
        print()
    
    def _display_category_breakdown(self, stats):
        """Display error category breakdown."""
        print("📂 ERROR CATEGORY BREAKDOWN")
        print("-" * 40)
        
        category_icons = {
            'authentication': '🔐',
            'authorization': '🚫',
            'validation': '✅',
            'api_error': '🌐',
            'network_error': '📡',
            'file_io': '📁',
            'parsing_error': '📋',
            'memory_error': '💾',
            'timeout': '⏰',
            'configuration': '⚙️',
            'dependency': '📦',
            'business_logic': '💼',
            'unknown': '❓'
        }
        
        # Sort categories by count
        sorted_categories = sorted(
            stats.errors_by_category.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        total_by_category = sum(stats.errors_by_category.values())
        
        for category, count in sorted_categories[:8]:  # Top 8 categories
            if count > 0:
                percentage = (count / total_by_category) * 100 if total_by_category > 0 else 0
                icon = category_icons.get(category, '❓')
                category_name = category.replace('_', ' ').title()
                print(f"   {icon} {category_name}: {count} ({percentage:.1f}%)")
        
        print()
    
    def _display_recent_errors(self, recent_errors):
        """Display recent errors."""
        print("🕐 RECENT ERRORS (Last 24 Hours)")
        print("-" * 40)
        
        if not recent_errors:
            print("   ✅ No recent errors")
            print()
            return
        
        for error in recent_errors:
            timestamp = datetime.fromisoformat(error.timestamp)
            time_ago = self._format_time_ago(timestamp)
            
            severity_icon = {
                'fatal': '💀',
                'critical': '🚨',
                'error': '❌',
                'warning': '⚠️',
                'info': 'ℹ️',
                'debug': '🐛'
            }.get(error.severity.value, '❓')
            
            print(f"   {severity_icon} {error.exception_type}: {error.message[:50]}...")
            print(f"      ID: {error.id}")
            print(f"      Time: {time_ago}")
            print(f"      Count: {error.count}")
            if error.context.function_name:
                print(f"      Function: {error.context.function_name}")
            print()
    
    def _display_top_errors(self, top_errors):
        """Display most frequent errors."""
        print("🔥 TOP ERRORS (Most Frequent)")
        print("-" * 40)
        
        if not top_errors:
            print("   ✅ No error data available")
            print()
            return
        
        for i, error in enumerate(top_errors[:5], 1):
            severity_icon = {
                'fatal': '💀',
                'critical': '🚨',
                'error': '❌',
                'warning': '⚠️',
                'info': 'ℹ️',
                'debug': '🐛'
            }.get(error['severity'], '❓')
            
            print(f"   {i}. {severity_icon} {error['message']}")
            print(f"      Count: {error['count']}")
            print(f"      Category: {error['category'].replace('_', ' ').title()}")
            print(f"      Last Seen: {self._format_time_ago(datetime.fromisoformat(error['last_seen']))}")
            print()
    
    def _display_error_trends(self):
        """Display error trends."""
        print("📈 ERROR TRENDS (Last 7 Days)")
        print("-" * 40)
        
        try:
            trends = self.error_tracker.get_error_trends(days=7)
            
            if not trends:
                print("   ⚠️  No trend data available")
                print()
                return
            
            for trend in trends:
                date = trend['date']
                total = trend['total_errors']
                critical = trend['critical_errors']
                rate = trend['error_rate']
                category = trend['top_category']
                
                print(f"   📅 {date}: {total} errors ({rate:.2f}/sec)")
                if critical > 0:
                    print(f"      🚨 Critical: {critical}")
                if category != 'none':
                    print(f"      📂 Top Category: {category.replace('_', ' ').title()}")
                print()
        
        except Exception as e:
            print(f"   ❌ Error getting trends: {e}")
            print()
    
    def _format_time_ago(self, timestamp: datetime) -> str:
        """Format timestamp as 'time ago' string."""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago"
        else:
            return "just now"
    
    def interactive_mode(self):
        """Run dashboard in interactive mode."""
        self.running = True
        
        print("🚀 Starting Customer Solution Snapshot Generator Error Analysis Dashboard")
        print("=" * 80)
        
        try:
            while self.running:
                # Display dashboard
                self.display_dashboard()
                
                # Wait for user input or auto-refresh
                import select
                
                if select.select([sys.stdin], [], [], self.refresh_interval) == ([sys.stdin], [], []):
                    user_input = input().strip().lower()
                    
                    if user_input == 'q':
                        self.running = False
                    elif user_input == 'r':
                        continue  # Refresh immediately
                    elif user_input == 'e':
                        self._export_errors()
                    elif user_input == 'v':
                        self._view_error_details()
                    elif user_input == 's':
                        self._detailed_stats()
                    elif user_input == 'h':
                        self._show_help()
                
        except KeyboardInterrupt:
            print("\n⏹️  Dashboard interrupted by user")
        finally:
            print("👋 Error analysis dashboard stopped")
    
    def _export_errors(self):
        """Export errors to file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"error_export_{timestamp}.json"
            
            self.error_tracker.export_errors(filename, format='json')
            print(f"📄 Errors exported to: {filename}")
            input("Press Enter to continue...")
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            input("Press Enter to continue...")
    
    def _view_error_details(self):
        """View detailed error information."""
        try:
            error_id = input("Enter Error ID: ").strip()
            if not error_id:
                return
            
            error = self.error_tracker.get_error_by_id(error_id)
            if not error:
                print(f"❌ Error not found: {error_id}")
                input("Press Enter to continue...")
                return
            
            # Display detailed error information
            print("\n" + "=" * 60)
            print("🔍 DETAILED ERROR INFORMATION")
            print("=" * 60)
            print(f"ID: {error.id}")
            print(f"Timestamp: {error.timestamp}")
            print(f"Severity: {error.severity.value.upper()}")
            print(f"Category: {error.category.value.replace('_', ' ').title()}")
            print(f"Exception Type: {error.exception_type}")
            print(f"Message: {error.message}")
            print(f"Count: {error.count}")
            print(f"First Seen: {error.first_seen}")
            print(f"Last Seen: {error.last_seen}")
            print(f"Resolved: {'Yes' if error.resolved else 'No'}")
            
            if error.context.function_name:
                print(f"Function: {error.context.function_name}")
            if error.context.module_name:
                print(f"Module: {error.context.module_name}")
            if error.context.file_path:
                print(f"File: {error.context.file_path}")
            if error.context.line_number:
                print(f"Line: {error.context.line_number}")
            
            print("\nStack Trace:")
            print("-" * 40)
            print(error.stack_trace)
            
            if error.resolution_notes:
                print("\nResolution Notes:")
                print("-" * 40)
                print(error.resolution_notes)
            
            print("\n" + "=" * 60)
            
            # Option to resolve error
            if not error.resolved:
                resolve = input("Mark as resolved? (y/n): ").strip().lower()
                if resolve == 'y':
                    notes = input("Resolution notes: ").strip()
                    if self.error_tracker.resolve_error(error.id, notes):
                        print("✅ Error marked as resolved")
                    else:
                        print("❌ Failed to resolve error")
            
            input("Press Enter to continue...")
            
        except Exception as e:
            print(f"❌ Error viewing details: {e}")
            input("Press Enter to continue...")
    
    def _detailed_stats(self):
        """Show detailed statistics."""
        try:
            print("\n" + "=" * 60)
            print("📊 DETAILED ERROR STATISTICS")
            print("=" * 60)
            
            stats = self.error_tracker.get_error_stats()
            
            # Time-based analysis
            print("⏰ TIME-BASED ANALYSIS")
            print("-" * 30)
            
            for hours in [1, 6, 24, 168]:  # 1h, 6h, 24h, 1week
                recent = self.error_tracker.get_recent_errors(hours=hours)
                if hours == 1:
                    period = "Last Hour"
                elif hours == 6:
                    period = "Last 6 Hours"
                elif hours == 24:
                    period = "Last 24 Hours"
                else:
                    period = "Last Week"
                
                print(f"{period}: {len(recent)} errors")
            
            print("\n📂 CATEGORY ANALYSIS")
            print("-" * 30)
            
            for category, count in stats.errors_by_category.items():
                if count > 0:
                    print(f"{category.replace('_', ' ').title()}: {count}")
            
            print("\n🚨 SEVERITY ANALYSIS")
            print("-" * 30)
            
            for severity, count in stats.errors_by_severity.items():
                if count > 0:
                    print(f"{severity.upper()}: {count}")
            
            print("\n" + "=" * 60)
            input("Press Enter to continue...")
            
        except Exception as e:
            print(f"❌ Error getting detailed stats: {e}")
            input("Press Enter to continue...")
    
    def _show_help(self):
        """Show help information."""
        print("\n" + "=" * 60)
        print("💡 HELP - ERROR ANALYSIS DASHBOARD")
        print("=" * 60)
        print("Commands:")
        print("  r - Refresh dashboard")
        print("  e - Export errors to JSON file")
        print("  v - View detailed error information")
        print("  s - Show detailed statistics")
        print("  h - Show this help")
        print("  q - Quit dashboard")
        print("\nThe dashboard auto-refreshes every 10 seconds.")
        print("Error tracking runs continuously in the background.")
        print("=" * 60)
        input("Press Enter to continue...")
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """Generate comprehensive error analysis report."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"error_analysis_report_{timestamp}.json"
        
        stats = self.error_tracker.get_error_stats()
        recent_errors = self.error_tracker.get_recent_errors(hours=24)
        trends = self.error_tracker.get_error_trends(days=7)
        
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "generator": "Customer Solution Snapshot Generator Error Analysis Dashboard",
                "version": "1.0.0"
            },
            "summary": {
                "total_errors": stats.total_errors,
                "current_error_rate": stats.error_rate,
                "resolution_rate": stats.resolution_rate,
                "mean_time_to_resolution": stats.mean_time_to_resolution
            },
            "statistics": {
                "errors_by_severity": stats.errors_by_severity,
                "errors_by_category": stats.errors_by_category,
                "top_errors": stats.top_errors
            },
            "recent_errors": [
                {
                    "id": error.id,
                    "timestamp": error.timestamp,
                    "severity": error.severity.value,
                    "category": error.category.value,
                    "message": error.message,
                    "count": error.count,
                    "resolved": error.resolved
                }
                for error in recent_errors
            ],
            "trends": trends
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Error analysis report saved to: {output_file}")
        return output_file


def main():
    """Main dashboard application."""
    parser = argparse.ArgumentParser(description="Customer Solution Snapshot Generator Error Analysis Dashboard")
    parser.add_argument('--mode', choices=['interactive', 'report', 'stats'], 
                       default='interactive', help='Dashboard mode')
    parser.add_argument('--output', help='Output file for reports')
    parser.add_argument('--hours', type=int, default=24, help='Hours for recent error analysis')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    args = parser.parse_args()
    
    try:
        # Initialize dashboard
        config = Config.get_default()
        dashboard = ErrorAnalysisDashboard(config)
        
        # Start error tracker background processing
        dashboard.error_tracker.start_background_processing()
        
        try:
            if args.mode == 'interactive':
                dashboard.interactive_mode()
            elif args.mode == 'report':
                report_file = dashboard.generate_report(args.output)
                if not args.json:
                    print(f"✅ Report generated: {report_file}")
            elif args.mode == 'stats':
                stats = dashboard.error_tracker.get_error_stats()
                if args.json:
                    print(json.dumps({
                        "total_errors": stats.total_errors,
                        "error_rate": stats.error_rate,
                        "resolution_rate": stats.resolution_rate,
                        "errors_by_severity": stats.errors_by_severity,
                        "errors_by_category": stats.errors_by_category
                    }, indent=2))
                else:
                    print(f"Total Errors: {stats.total_errors}")
                    print(f"Error Rate: {stats.error_rate:.2f} errors/second")
                    print(f"Resolution Rate: {stats.resolution_rate:.1%}")
        
        finally:
            dashboard.error_tracker.stop_background_processing()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️  Dashboard interrupted by user")
        return 0
    except Exception as e:
        print(f"💥 Dashboard failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())