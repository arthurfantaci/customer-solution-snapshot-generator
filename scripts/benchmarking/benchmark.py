#!/usr/bin/env python3
"""
Performance benchmarking script for Customer Solution Snapshot Generator.

This script provides comprehensive benchmarking capabilities to measure
performance across different file sizes, configurations, and system conditions.
"""

import json
import os
import statistics
import sys
import tempfile
import time
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Optional


# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

try:
    import memory_profiler
    import psutil

    PROFILING_AVAILABLE = True
except ImportError:
    PROFILING_AVAILABLE = False

from customer_snapshot.core.processor import TranscriptProcessor
from customer_snapshot.utils.config import Config


@dataclass
class BenchmarkResult:
    """Represents the result of a single benchmark run."""

    test_name: str
    file_size_mb: float
    processing_time_seconds: float
    memory_usage_mb: float
    peak_memory_mb: float
    cpu_usage_percent: float
    success: bool
    error_message: Optional[str] = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class BenchmarkSuite:
    """Represents results from a complete benchmark suite."""

    system_info: dict[str, Any]
    test_results: list[BenchmarkResult]
    summary_stats: dict[str, Any]
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class PerformanceMonitor:
    """Monitors system performance during benchmark execution."""

    def __init__(self):
        self.process = psutil.Process()
        self.start_time = None
        self.start_memory = None
        self.start_cpu = None
        self.peak_memory = 0
        self.cpu_samples = []

    def start_monitoring(self):
        """Start performance monitoring."""
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.start_cpu = self.process.cpu_percent()
        self.peak_memory = self.start_memory
        self.cpu_samples = []

    def sample_performance(self):
        """Sample current performance metrics."""
        if not self.start_time:
            return

        current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        current_cpu = self.process.cpu_percent()

        self.peak_memory = max(self.peak_memory, current_memory)
        self.cpu_samples.append(current_cpu)

    def get_metrics(self) -> dict[str, float]:
        """Get current performance metrics."""
        if not self.start_time:
            return {}

        elapsed_time = time.time() - self.start_time
        current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        avg_cpu = statistics.mean(self.cpu_samples) if self.cpu_samples else 0

        return {
            "elapsed_time": elapsed_time,
            "current_memory_mb": current_memory,
            "peak_memory_mb": self.peak_memory,
            "average_cpu_percent": avg_cpu,
            "memory_delta_mb": current_memory - self.start_memory,
        }


class BenchmarkRunner:
    """Runs comprehensive benchmarks on the transcript processor."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.get_default()
        self.processor = TranscriptProcessor(self.config)
        self.monitor = PerformanceMonitor() if PROFILING_AVAILABLE else None

    def create_test_vtt(self, size_mb: float) -> str:
        """Create a test VTT file of specified size."""
        # Base VTT content
        base_content = """WEBVTT

00:00:01.000 --> 00:00:05.000
Test Speaker: This is a performance test transcript for the Customer Solution Snapshot Generator.

00:00:05.000 --> 00:00:10.000
Test Speaker: We are testing various file sizes to measure processing performance.

00:00:10.000 --> 00:00:15.000
Test Speaker: The system should handle different scales efficiently with optimal memory usage.

00:00:15.000 --> 00:00:20.000
Test Speaker: This includes NLP processing, entity extraction, and output generation.

00:00:20.000 --> 00:00:25.000
Test Speaker: Performance monitoring helps us identify bottlenecks and optimization opportunities.

"""

        # Calculate how many times to repeat content to reach target size
        base_size = len(base_content.encode("utf-8"))
        target_size = int(size_mb * 1024 * 1024)  # Convert MB to bytes
        repetitions = max(1, target_size // base_size)

        # Create content with timestamp increments
        content = "WEBVTT\n\n"
        for i in range(repetitions):
            start_time = i * 30  # 30 seconds per block
            end_time = start_time + 25

            # Format timestamps
            start_min, start_sec = divmod(start_time, 60)
            end_min, end_sec = divmod(end_time, 60)

            content += f"{start_min:02d}:{start_sec:02d}.000 --> {end_min:02d}:{end_sec:02d}.000\n"
            content += f"Test Speaker {i + 1}: Performance test content block {i + 1}. "
            content += (
                "Testing system scalability and efficiency with various file sizes. "
            )
            content += "This helps identify performance characteristics across different scales.\n\n"

        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".vtt", delete=False) as f:
            f.write(content)
            return f.name

    def run_single_benchmark(
        self, test_name: str, file_size_mb: float
    ) -> BenchmarkResult:
        """Run a single benchmark test."""
        print(f"Running benchmark: {test_name} (Size: {file_size_mb:.2f} MB)")

        # Create test file
        test_file = None
        try:
            test_file = self.create_test_vtt(file_size_mb)
            actual_size = os.path.getsize(test_file) / 1024 / 1024  # MB

            # Start monitoring
            if self.monitor:
                self.monitor.start_monitoring()

            start_time = time.time()

            # Process file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".md", delete=False
            ) as output_file:
                self.processor.process_file(test_file, output_file.name)

                # Sample performance periodically during processing
                if self.monitor:
                    self.monitor.sample_performance()

                end_time = time.time()
                processing_time = end_time - start_time

                # Get final metrics
                if self.monitor:
                    metrics = self.monitor.get_metrics()
                    memory_usage = metrics.get("current_memory_mb", 0)
                    peak_memory = metrics.get("peak_memory_mb", 0)
                    cpu_usage = metrics.get("average_cpu_percent", 0)
                else:
                    memory_usage = 0
                    peak_memory = 0
                    cpu_usage = 0

                # Clean up output file
                os.unlink(output_file.name)

                return BenchmarkResult(
                    test_name=test_name,
                    file_size_mb=actual_size,
                    processing_time_seconds=processing_time,
                    memory_usage_mb=memory_usage,
                    peak_memory_mb=peak_memory,
                    cpu_usage_percent=cpu_usage,
                    success=True,
                )

        except Exception as e:
            return BenchmarkResult(
                test_name=test_name,
                file_size_mb=file_size_mb,
                processing_time_seconds=0,
                memory_usage_mb=0,
                peak_memory_mb=0,
                cpu_usage_percent=0,
                success=False,
                error_message=str(e),
            )
        finally:
            # Clean up test file
            if test_file and os.path.exists(test_file):
                os.unlink(test_file)

    def run_benchmark_suite(
        self, test_sizes: Optional[list[float]] = None
    ) -> BenchmarkSuite:
        """Run a complete benchmark suite."""
        if test_sizes is None:
            test_sizes = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]  # MB

        print("🏃 Starting comprehensive benchmark suite...")
        print(f"📊 Testing file sizes: {test_sizes} MB")
        print(f"🔧 Profiling available: {PROFILING_AVAILABLE}")
        print("=" * 60)

        results = []

        for size in test_sizes:
            test_name = f"File_{size:.1f}MB"
            result = self.run_single_benchmark(test_name, size)
            results.append(result)

            if result.success:
                print(f"✅ {test_name}: {result.processing_time_seconds:.2f}s")
            else:
                print(f"❌ {test_name}: {result.error_message}")

        # Calculate summary statistics
        successful_results = [r for r in results if r.success]
        summary_stats = self._calculate_summary_stats(successful_results)

        # Get system information
        system_info = self._get_system_info()

        return BenchmarkSuite(
            system_info=system_info, test_results=results, summary_stats=summary_stats
        )

    def _calculate_summary_stats(
        self, results: list[BenchmarkResult]
    ) -> dict[str, Any]:
        """Calculate summary statistics from benchmark results."""
        if not results:
            return {}

        processing_times = [r.processing_time_seconds for r in results]
        memory_usage = [r.memory_usage_mb for r in results]
        peak_memory = [r.peak_memory_mb for r in results]
        cpu_usage = [r.cpu_usage_percent for r in results]
        file_sizes = [r.file_size_mb for r in results]

        return {
            "total_tests": len(results),
            "successful_tests": sum(1 for r in results if r.success),
            "processing_time": {
                "mean": statistics.mean(processing_times),
                "median": statistics.median(processing_times),
                "min": min(processing_times),
                "max": max(processing_times),
                "std_dev": statistics.stdev(processing_times)
                if len(processing_times) > 1
                else 0,
            },
            "memory_usage": {
                "mean": statistics.mean(memory_usage),
                "median": statistics.median(memory_usage),
                "min": min(memory_usage),
                "max": max(memory_usage),
                "peak_max": max(peak_memory) if peak_memory else 0,
            },
            "cpu_usage": {
                "mean": statistics.mean(cpu_usage),
                "median": statistics.median(cpu_usage),
                "min": min(cpu_usage),
                "max": max(cpu_usage),
            },
            "file_sizes": {
                "min": min(file_sizes),
                "max": max(file_sizes),
                "total": sum(file_sizes),
            },
            "throughput": {
                "mb_per_second": sum(file_sizes) / sum(processing_times)
                if processing_times
                else 0
            },
        }

    def _get_system_info(self) -> dict[str, Any]:
        """Get system information for benchmark context."""
        system_info = {
            "python_version": sys.version,
            "platform": sys.platform,
            "timestamp": datetime.now().isoformat(),
        }

        if PROFILING_AVAILABLE:
            system_info.update(
                {
                    "cpu_count": psutil.cpu_count(),
                    "memory_total_gb": psutil.virtual_memory().total
                    / 1024
                    / 1024
                    / 1024,
                    "memory_available_gb": psutil.virtual_memory().available
                    / 1024
                    / 1024
                    / 1024,
                    "disk_usage_gb": psutil.disk_usage("/").total / 1024 / 1024 / 1024,
                }
            )

        return system_info

    def save_results(self, results: BenchmarkSuite, output_file: Optional[str] = None):
        """Save benchmark results to JSON file."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"benchmark_results_{timestamp}.json"

        # Convert to dict for JSON serialization
        results_dict = asdict(results)

        with open(output_file, "w") as f:
            json.dump(results_dict, f, indent=2)

        print(f"📁 Benchmark results saved to: {output_file}")
        return output_file

    def print_results(self, results: BenchmarkSuite):
        """Print formatted benchmark results."""
        print("\n" + "=" * 60)
        print("📊 BENCHMARK RESULTS SUMMARY")
        print("=" * 60)

        # System info
        print("🖥️  System Info:")
        print(f"   Python: {results.system_info.get('python_version', 'Unknown')}")
        print(f"   Platform: {results.system_info.get('platform', 'Unknown')}")
        if "cpu_count" in results.system_info:
            print(f"   CPU Cores: {results.system_info['cpu_count']}")
            print(f"   Memory: {results.system_info['memory_total_gb']:.1f} GB")

        # Summary stats
        stats = results.summary_stats
        print("\n📈 Performance Summary:")
        print(
            f"   Tests: {stats['successful_tests']}/{stats['total_tests']} successful"
        )
        print(
            f"   Processing Time: {stats['processing_time']['mean']:.2f}s avg, "
            f"{stats['processing_time']['min']:.2f}s min, "
            f"{stats['processing_time']['max']:.2f}s max"
        )
        print(
            f"   Memory Usage: {stats['memory_usage']['mean']:.1f} MB avg, "
            f"{stats['memory_usage']['peak_max']:.1f} MB peak"
        )
        print(f"   Throughput: {stats['throughput']['mb_per_second']:.2f} MB/s")

        # Individual results
        print("\n📋 Individual Test Results:")
        for result in results.test_results:
            if result.success:
                print(
                    f"   ✅ {result.test_name}: "
                    f"{result.processing_time_seconds:.2f}s, "
                    f"{result.memory_usage_mb:.1f} MB, "
                    f"{result.cpu_usage_percent:.1f}% CPU"
                )
            else:
                print(f"   ❌ {result.test_name}: {result.error_message}")


def main():
    """Main benchmark execution function."""
    print("🚀 Customer Solution Snapshot Generator - Performance Benchmark")
    print("=" * 60)

    # Check if profiling is available
    if not PROFILING_AVAILABLE:
        print("⚠️  Warning: psutil and memory_profiler not available.")
        print("   Install with: pip install psutil memory-profiler")
        print("   Performance monitoring will be limited.\n")

    try:
        # Initialize benchmark runner
        config = Config.get_default()
        runner = BenchmarkRunner(config)

        # Define test sizes (in MB)
        test_sizes = [0.1, 0.5, 1.0, 2.0, 5.0]  # Start with smaller sizes

        # Run benchmark suite
        results = runner.run_benchmark_suite(test_sizes)

        # Print results
        runner.print_results(results)

        # Save results
        output_file = runner.save_results(results)

        print("\n🎉 Benchmark completed successfully!")
        print(f"📄 Results saved to: {output_file}")

    except KeyboardInterrupt:
        print("\n⏹️  Benchmark interrupted by user")
    except Exception as e:
        print(f"\n💥 Benchmark failed: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
