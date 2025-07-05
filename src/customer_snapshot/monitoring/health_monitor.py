"""
Comprehensive health monitoring system for Customer Solution Snapshot Generator.

This module provides advanced health checking capabilities including dependency monitoring,
performance health, and system resource monitoring with configurable thresholds and alerts.
"""

import os
import sys
import time
import json
import logging
import threading
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import tempfile

try:
    import psutil
    import requests
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ..utils.config import Config
from ..utils.memory_optimizer import MemoryTracker

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health check status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check operation."""
    name: str
    status: HealthStatus
    message: str
    details: Dict[str, Any]
    timestamp: str
    response_time_ms: float
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class SystemMetrics:
    """System-level metrics snapshot."""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    disk_free_gb: float
    load_average: Optional[List[float]]
    network_io: Dict[str, int]
    process_count: int
    uptime_seconds: float
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ApplicationMetrics:
    """Application-specific metrics."""
    timestamp: str
    requests_total: int
    requests_per_second: float
    average_response_time_ms: float
    error_rate_percent: float
    active_connections: int
    memory_usage_mb: float
    cache_hit_rate: float
    queue_size: int
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class BaseHealthCheck:
    """Base class for health checks."""
    
    def __init__(self, name: str, config: Optional[Config] = None):
        self.name = name
        self.config = config or Config.get_default()
        self.enabled = True
        
    def check(self) -> HealthCheckResult:
        """Perform the health check."""
        start_time = time.time()
        
        try:
            if not self.enabled:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNKNOWN,
                    message="Health check disabled",
                    details={},
                    timestamp=datetime.now().isoformat(),
                    response_time_ms=0
                )
            
            result = self._perform_check()
            result.response_time_ms = (time.time() - start_time) * 1000
            return result
            
        except Exception as e:
            logger.error(f"Health check {self.name} failed: {e}")
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.CRITICAL,
                message=f"Health check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now().isoformat(),
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    def _perform_check(self) -> HealthCheckResult:
        """Override this method to implement specific health check logic."""
        raise NotImplementedError


class SystemResourcesHealthCheck(BaseHealthCheck):
    """Health check for system resources (CPU, memory, disk)."""
    
    def __init__(self, config: Optional[Config] = None):
        super().__init__("system_resources", config)
        self.cpu_warning_threshold = 70.0
        self.cpu_critical_threshold = 90.0
        self.memory_warning_threshold = 80.0
        self.memory_critical_threshold = 95.0
        self.disk_warning_threshold = 80.0
        self.disk_critical_threshold = 95.0
    
    def _perform_check(self) -> HealthCheckResult:
        if not MONITORING_AVAILABLE:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.WARNING,
                message="psutil not available, limited monitoring",
                details={},
                timestamp=datetime.now().isoformat(),
                response_time_ms=0
            )
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        disk_usage_percent = (disk.used / disk.total) * 100
        disk_free_gb = disk.free / (1024**3)
        
        # Determine overall status
        status = HealthStatus.HEALTHY
        issues = []
        
        # Check CPU
        if cpu_percent >= self.cpu_critical_threshold:
            status = HealthStatus.CRITICAL
            issues.append(f"Critical CPU usage: {cpu_percent:.1f}%")
        elif cpu_percent >= self.cpu_warning_threshold:
            if status == HealthStatus.HEALTHY:
                status = HealthStatus.WARNING
            issues.append(f"High CPU usage: {cpu_percent:.1f}%")
        
        # Check Memory
        if memory.percent >= self.memory_critical_threshold:
            status = HealthStatus.CRITICAL
            issues.append(f"Critical memory usage: {memory.percent:.1f}%")
        elif memory.percent >= self.memory_warning_threshold:
            if status == HealthStatus.HEALTHY:
                status = HealthStatus.WARNING
            issues.append(f"High memory usage: {memory.percent:.1f}%")
        
        # Check Disk
        if disk_usage_percent >= self.disk_critical_threshold:
            status = HealthStatus.CRITICAL
            issues.append(f"Critical disk usage: {disk_usage_percent:.1f}%")
        elif disk_usage_percent >= self.disk_warning_threshold:
            if status == HealthStatus.HEALTHY:
                status = HealthStatus.WARNING
            issues.append(f"High disk usage: {disk_usage_percent:.1f}%")
        
        message = "System resources healthy" if not issues else "; ".join(issues)
        
        return HealthCheckResult(
            name=self.name,
            status=status,
            message=message,
            details={
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_usage_percent": disk_usage_percent,
                "disk_free_gb": disk_free_gb,
                "thresholds": {
                    "cpu_warning": self.cpu_warning_threshold,
                    "cpu_critical": self.cpu_critical_threshold,
                    "memory_warning": self.memory_warning_threshold,
                    "memory_critical": self.memory_critical_threshold,
                    "disk_warning": self.disk_warning_threshold,
                    "disk_critical": self.disk_critical_threshold
                }
            },
            timestamp=datetime.now().isoformat(),
            response_time_ms=0
        )


class ApplicationHealthCheck(BaseHealthCheck):
    """Health check for application-specific functionality."""
    
    def __init__(self, config: Optional[Config] = None):
        super().__init__("application", config)
        self.memory_tracker = MemoryTracker()
    
    def _perform_check(self) -> HealthCheckResult:
        issues = []
        status = HealthStatus.HEALTHY
        
        # Check if we can import main modules
        try:
            from ...core.processor import TranscriptProcessor
            from ...io.vtt_reader import VTTReader
            from ...core.nlp_engine import NLPEngine
        except ImportError as e:
            status = HealthStatus.CRITICAL
            issues.append(f"Failed to import core modules: {e}")
        
        # Check NLP models
        try:
            import spacy
            nlp = spacy.load('en_core_web_sm')
        except Exception as e:
            status = HealthStatus.CRITICAL
            issues.append(f"spaCy model not available: {e}")
        
        # Check NLTK data
        try:
            import nltk
            nltk.data.find('tokenizers/punkt')
        except Exception as e:
            status = HealthStatus.WARNING
            issues.append(f"NLTK data not available: {e}")
        
        # Check configuration
        try:
            config = Config.get_default()
            config.validate()
        except Exception as e:
            status = HealthStatus.CRITICAL
            issues.append(f"Invalid configuration: {e}")
        
        # Check memory usage
        if MONITORING_AVAILABLE:
            current_memory = self.memory_tracker.get_current_metrics()
            if current_memory.rss_mb > 2048:  # 2GB limit
                status = HealthStatus.WARNING
                issues.append(f"High memory usage: {current_memory.rss_mb:.1f} MB")
        
        # Test basic functionality
        try:
            # Create a simple test VTT content
            test_content = """WEBVTT

00:00:01.000 --> 00:00:05.000
Test Speaker: This is a health check test."""
            
            # Test VTT parsing
            with tempfile.NamedTemporaryFile(mode='w', suffix='.vtt', delete=False) as f:
                f.write(test_content)
                test_file = f.name
            
            try:
                from ...io.vtt_reader import VTTReader
                reader = VTTReader(self.config)
                text = reader.read_vtt(test_file)
                
                if not text or len(text) < 10:
                    status = HealthStatus.WARNING
                    issues.append("VTT parsing returned minimal content")
                    
            finally:
                os.unlink(test_file)
                
        except Exception as e:
            status = HealthStatus.WARNING
            issues.append(f"Functional test failed: {e}")
        
        message = "Application healthy" if not issues else "; ".join(issues)
        
        return HealthCheckResult(
            name=self.name,
            status=status,
            message=message,
            details={
                "modules_loaded": status != HealthStatus.CRITICAL,
                "nlp_models_available": "spaCy model not available" not in message,
                "memory_usage_mb": current_memory.rss_mb if MONITORING_AVAILABLE else 0,
                "functional_test_passed": "Functional test failed" not in message
            },
            timestamp=datetime.now().isoformat(),
            response_time_ms=0
        )


class DependencyHealthCheck(BaseHealthCheck):
    """Health check for external dependencies."""
    
    def __init__(self, config: Optional[Config] = None):
        super().__init__("dependencies", config)
    
    def _perform_check(self) -> HealthCheckResult:
        issues = []
        status = HealthStatus.HEALTHY
        dependency_status = {}
        
        # Check API connectivity (if API keys are configured)
        if self.config.anthropic_api_key:
            anthropic_status = self._check_anthropic_api()
            dependency_status["anthropic"] = anthropic_status
            if anthropic_status["status"] != "healthy":
                if anthropic_status["status"] == "critical":
                    status = HealthStatus.CRITICAL
                else:
                    status = HealthStatus.WARNING
                issues.append(f"Anthropic API: {anthropic_status['message']}")
        
        # Check file system permissions
        fs_status = self._check_filesystem()
        dependency_status["filesystem"] = fs_status
        if fs_status["status"] != "healthy":
            status = HealthStatus.CRITICAL
            issues.append(f"Filesystem: {fs_status['message']}")
        
        # Check Python environment
        python_status = self._check_python_environment()
        dependency_status["python_environment"] = python_status
        if python_status["status"] != "healthy":
            if python_status["status"] == "critical":
                status = HealthStatus.CRITICAL
            else:
                status = HealthStatus.WARNING
            issues.append(f"Python environment: {python_status['message']}")
        
        message = "All dependencies healthy" if not issues else "; ".join(issues)
        
        return HealthCheckResult(
            name=self.name,
            status=status,
            message=message,
            details=dependency_status,
            timestamp=datetime.now().isoformat(),
            response_time_ms=0
        )
    
    def _check_anthropic_api(self) -> Dict[str, Any]:
        """Check Anthropic API connectivity."""
        try:
            import anthropic
            
            # Create client with timeout
            client = anthropic.Anthropic(
                api_key=self.config.anthropic_api_key,
                timeout=10.0
            )
            
            # Simple API test
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            
            return {
                "status": "healthy",
                "message": "API accessible",
                "response_received": True
            }
            
        except Exception as e:
            error_msg = str(e)
            if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
                return {
                    "status": "critical",
                    "message": "Authentication failed",
                    "error": error_msg
                }
            elif "timeout" in error_msg.lower() or "connection" in error_msg.lower():
                return {
                    "status": "warning",
                    "message": "Connection issues",
                    "error": error_msg
                }
            else:
                return {
                    "status": "warning",
                    "message": "API test failed",
                    "error": error_msg
                }
    
    def _check_filesystem(self) -> Dict[str, Any]:
        """Check filesystem permissions and access."""
        try:
            # Check input/output directories
            directories = [
                self.config.input_dir,
                self.config.output_dir,
                self.config.data_dir
            ]
            
            for directory in directories:
                if not directory.exists():
                    directory.mkdir(parents=True, exist_ok=True)
                
                # Test write permissions
                test_file = directory / ".health_check_test"
                try:
                    test_file.write_text("health check test")
                    test_file.unlink()
                except Exception as e:
                    return {
                        "status": "critical",
                        "message": f"Cannot write to {directory}",
                        "error": str(e)
                    }
            
            return {
                "status": "healthy",
                "message": "Filesystem accessible",
                "directories_checked": len(directories)
            }
            
        except Exception as e:
            return {
                "status": "critical",
                "message": "Filesystem check failed",
                "error": str(e)
            }
    
    def _check_python_environment(self) -> Dict[str, Any]:
        """Check Python environment and dependencies."""
        try:
            import pkg_resources
            
            required_packages = [
                'spacy',
                'nltk', 
                'webvtt-py',
                'anthropic'
            ]
            
            missing_packages = []
            package_versions = {}
            
            for package in required_packages:
                try:
                    version = pkg_resources.get_distribution(package).version
                    package_versions[package] = version
                except pkg_resources.DistributionNotFound:
                    missing_packages.append(package)
            
            if missing_packages:
                return {
                    "status": "critical",
                    "message": f"Missing packages: {', '.join(missing_packages)}",
                    "installed_packages": package_versions,
                    "missing_packages": missing_packages
                }
            
            return {
                "status": "healthy",
                "message": "All required packages available",
                "package_versions": package_versions,
                "python_version": sys.version.split()[0]
            }
            
        except Exception as e:
            return {
                "status": "warning",
                "message": "Package check failed",
                "error": str(e)
            }


class PerformanceHealthCheck(BaseHealthCheck):
    """Health check for application performance metrics."""
    
    def __init__(self, config: Optional[Config] = None):
        super().__init__("performance", config)
        self.response_time_threshold_ms = 5000  # 5 seconds
        self.memory_growth_threshold_mb = 100   # 100MB
        self.memory_tracker = MemoryTracker()
    
    def _perform_check(self) -> HealthCheckResult:
        issues = []
        status = HealthStatus.HEALTHY
        performance_metrics = {}
        
        # Test processing performance
        processing_metrics = self._test_processing_performance()
        performance_metrics["processing"] = processing_metrics
        
        if processing_metrics["response_time_ms"] > self.response_time_threshold_ms:
            status = HealthStatus.WARNING
            issues.append(f"Slow processing: {processing_metrics['response_time_ms']:.0f}ms")
        
        # Check memory performance
        if MONITORING_AVAILABLE:
            memory_metrics = self._check_memory_performance()
            performance_metrics["memory"] = memory_metrics
            
            if memory_metrics.get("growth_rate_mb", 0) > self.memory_growth_threshold_mb:
                status = HealthStatus.WARNING
                issues.append(f"High memory growth: {memory_metrics['growth_rate_mb']:.1f}MB")
        
        # Check system load
        if MONITORING_AVAILABLE:
            load_metrics = self._check_system_load()
            performance_metrics["system_load"] = load_metrics
            
            if load_metrics.get("load_average_1m", 0) > psutil.cpu_count() * 2:
                status = HealthStatus.WARNING
                issues.append("High system load")
        
        message = "Performance healthy" if not issues else "; ".join(issues)
        
        return HealthCheckResult(
            name=self.name,
            status=status,
            message=message,
            details=performance_metrics,
            timestamp=datetime.now().isoformat(),
            response_time_ms=0
        )
    
    def _test_processing_performance(self) -> Dict[str, Any]:
        """Test basic processing performance."""
        try:
            start_time = time.time()
            
            # Create simple test data
            test_content = """WEBVTT

00:00:01.000 --> 00:00:05.000
Performance Test: This is a performance health check test for the transcript processor.

00:00:05.000 --> 00:00:10.000
Performance Test: Testing response time and basic functionality."""
            
            # Test processing
            with tempfile.NamedTemporaryFile(mode='w', suffix='.vtt', delete=False) as f:
                f.write(test_content)
                test_file = f.name
            
            try:
                from ...io.vtt_reader import VTTReader
                reader = VTTReader(self.config)
                text = reader.read_vtt(test_file)
                
                # Simple NLP test
                from ...core.nlp_engine import NLPEngine
                nlp_engine = NLPEngine(self.config)
                cleaned_text = nlp_engine.clean_text(text)
                
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                
                return {
                    "response_time_ms": response_time_ms,
                    "text_processed_chars": len(cleaned_text),
                    "success": True
                }
                
            finally:
                os.unlink(test_file)
                
        except Exception as e:
            return {
                "response_time_ms": 0,
                "success": False,
                "error": str(e)
            }
    
    def _check_memory_performance(self) -> Dict[str, Any]:
        """Check memory performance metrics."""
        try:
            current_metrics = self.memory_tracker.get_current_metrics()
            
            # Simple memory growth estimation
            growth_rate = 0
            if hasattr(self, '_last_memory_check'):
                time_diff = time.time() - self._last_memory_check_time
                memory_diff = current_metrics.rss_mb - self._last_memory_check
                if time_diff > 0:
                    growth_rate = (memory_diff / time_diff) * 60  # MB per minute
            
            self._last_memory_check = current_metrics.rss_mb
            self._last_memory_check_time = time.time()
            
            return {
                "current_memory_mb": current_metrics.rss_mb,
                "memory_percent": current_metrics.percent,
                "growth_rate_mb": growth_rate,
                "gc_objects": current_metrics.gc_objects
            }
            
        except Exception as e:
            return {
                "error": str(e)
            }
    
    def _check_system_load(self) -> Dict[str, Any]:
        """Check system load metrics."""
        try:
            if hasattr(os, 'getloadavg'):
                load_avg = os.getloadavg()
                return {
                    "load_average_1m": load_avg[0],
                    "load_average_5m": load_avg[1],
                    "load_average_15m": load_avg[2],
                    "cpu_count": psutil.cpu_count()
                }
            else:
                return {
                    "load_average_unavailable": True,
                    "cpu_count": psutil.cpu_count()
                }
                
        except Exception as e:
            return {
                "error": str(e)
            }


class HealthMonitor:
    """Comprehensive health monitoring coordinator."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.get_default()
        self.health_checks = self._initialize_health_checks()
        self.monitoring_enabled = True
        self.monitor_thread = None
        self.check_interval = 30  # seconds
        self.health_history = []
        self.max_history = 1000
        
    def _initialize_health_checks(self) -> List[BaseHealthCheck]:
        """Initialize all health checks."""
        return [
            SystemResourcesHealthCheck(self.config),
            ApplicationHealthCheck(self.config),
            DependencyHealthCheck(self.config),
            PerformanceHealthCheck(self.config)
        ]
    
    def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """Run all health checks and return results."""
        results = {}
        
        for health_check in self.health_checks:
            try:
                result = health_check.check()
                results[health_check.name] = result
                logger.debug(f"Health check {health_check.name}: {result.status.value}")
            except Exception as e:
                logger.error(f"Health check {health_check.name} failed: {e}")
                results[health_check.name] = HealthCheckResult(
                    name=health_check.name,
                    status=HealthStatus.CRITICAL,
                    message=f"Health check execution failed: {str(e)}",
                    details={"error": str(e)},
                    timestamp=datetime.now().isoformat(),
                    response_time_ms=0
                )
        
        # Store in history
        self._add_to_history(results)
        
        return results
    
    def get_overall_status(self) -> HealthStatus:
        """Get overall system health status."""
        results = self.run_all_checks()
        
        if not results:
            return HealthStatus.UNKNOWN
        
        # Determine overall status based on individual checks
        statuses = [result.status for result in results.values()]
        
        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        elif HealthStatus.WARNING in statuses:
            return HealthStatus.WARNING
        elif all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary."""
        results = self.run_all_checks()
        overall_status = self.get_overall_status()
        
        return {
            "overall_status": overall_status.value,
            "timestamp": datetime.now().isoformat(),
            "checks": {name: asdict(result) for name, result in results.items()},
            "summary": {
                "total_checks": len(results),
                "healthy_checks": sum(1 for r in results.values() if r.status == HealthStatus.HEALTHY),
                "warning_checks": sum(1 for r in results.values() if r.status == HealthStatus.WARNING),
                "critical_checks": sum(1 for r in results.values() if r.status == HealthStatus.CRITICAL),
                "average_response_time_ms": sum(r.response_time_ms for r in results.values()) / len(results) if results else 0
            }
        }
    
    def start_monitoring(self):
        """Start continuous health monitoring."""
        if self.monitoring_enabled and not self.monitor_thread:
            self.monitor_thread = threading.Thread(target=self._monitoring_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            logger.info("Health monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous health monitoring."""
        self.monitoring_enabled = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            self.monitor_thread = None
        logger.info("Health monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_enabled:
            try:
                summary = self.get_health_summary()
                
                # Log overall status
                status = summary["overall_status"]
                if status == "critical":
                    logger.error("System health is CRITICAL")
                elif status == "warning":
                    logger.warning("System health has WARNINGS")
                else:
                    logger.info("System health is HEALTHY")
                
                # Log specific issues
                for check_name, check_result in summary["checks"].items():
                    if check_result["status"] in ["warning", "critical"]:
                        logger.warning(f"Health check {check_name}: {check_result['message']}")
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Health monitoring loop error: {e}")
                time.sleep(self.check_interval)
    
    def _add_to_history(self, results: Dict[str, HealthCheckResult]):
        """Add results to history."""
        self.health_history.append({
            "timestamp": datetime.now().isoformat(),
            "results": results
        })
        
        # Limit history size
        if len(self.health_history) > self.max_history:
            self.health_history = self.health_history[-self.max_history:]
    
    def get_health_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get health trends over specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_history = [
            entry for entry in self.health_history
            if datetime.fromisoformat(entry["timestamp"]) >= cutoff_time
        ]
        
        if not recent_history:
            return {"error": "No recent health data available"}
        
        # Calculate trends
        trends = {}
        for check_name in self.health_checks[0].name if self.health_checks else []:
            check_statuses = []
            for entry in recent_history:
                if check_name in entry["results"]:
                    check_statuses.append(entry["results"][check_name].status)
            
            if check_statuses:
                trends[check_name] = {
                    "total_checks": len(check_statuses),
                    "healthy_count": check_statuses.count(HealthStatus.HEALTHY),
                    "warning_count": check_statuses.count(HealthStatus.WARNING),
                    "critical_count": check_statuses.count(HealthStatus.CRITICAL),
                    "latest_status": check_statuses[-1].value if check_statuses else "unknown"
                }
        
        return {
            "time_period_hours": hours,
            "data_points": len(recent_history),
            "trends": trends
        }