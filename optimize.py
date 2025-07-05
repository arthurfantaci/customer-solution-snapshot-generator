#!/usr/bin/env python3
"""
Performance optimization and profiling script for Customer Solution Snapshot Generator.

This script provides detailed performance analysis, bottleneck identification,
and optimization recommendations for the transcript processing system.
"""

import time
import os
import sys
import json
import cProfile
import pstats
import tempfile
import traceback
from io import StringIO
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from functools import wraps

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import line_profiler
    import memory_profiler
    import psutil
    PROFILING_AVAILABLE = True
except ImportError:
    PROFILING_AVAILABLE = False

from customer_snapshot.core.processor import TranscriptProcessor
from customer_snapshot.utils.config import Config


@dataclass
class ProfileResult:
    """Results from performance profiling."""
    function_name: str
    total_time: float
    calls: int
    time_per_call: float
    cumulative_time: float
    filename: str
    line_number: int


@dataclass
class MemoryProfile:
    """Memory usage profiling results."""
    function_name: str
    line_number: int
    memory_usage: float
    increment: float
    line_content: str


@dataclass
class OptimizationReport:
    """Comprehensive optimization analysis report."""
    timestamp: str
    total_execution_time: float
    peak_memory_mb: float
    cpu_profiles: List[ProfileResult]
    memory_profiles: List[MemoryProfile]
    bottlenecks: List[str]
    recommendations: List[str]
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class PerformanceProfiler:
    """Comprehensive performance profiling system."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.get_default()
        self.profiler = None
        self.profile_data = None
        
    def profile_function(self, func):
        """Decorator to profile a specific function."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not PROFILING_AVAILABLE:
                return func(*args, **kwargs)
            
            # CPU profiling
            profiler = cProfile.Profile()
            profiler.enable()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                profiler.disable()
                
                # Save profile stats
                stats = pstats.Stats(profiler)
                stats.sort_stats('cumulative')
                
                # Store for analysis
                self.profile_data = stats
                
        return wrapper
    
    def profile_memory(self, func):
        """Decorator to profile memory usage."""
        if not PROFILING_AVAILABLE:
            return func
            
        @memory_profiler.profile
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    
    def create_test_data(self, size_mb: float = 1.0) -> str:
        """Create test VTT data for profiling."""
        content = """WEBVTT

00:00:01.000 --> 00:00:05.000
Test Speaker: This is a comprehensive performance test for the Customer Solution Snapshot Generator.

00:00:05.000 --> 00:00:10.000
Test Speaker: We are analyzing system performance across different components and identifying bottlenecks.

00:00:10.000 --> 00:00:15.000
Test Speaker: The system processes transcripts using advanced NLP techniques with spaCy and NLTK.

00:00:15.000 --> 00:00:20.000
Test Speaker: Performance optimization is crucial for handling large-scale transcript processing efficiently.

00:00:20.000 --> 00:00:25.000
Test Speaker: This includes entity extraction, topic modeling, and content enhancement using AI models.

"""
        
        # Calculate repetitions to reach target size
        base_size = len(content.encode('utf-8'))
        target_size = int(size_mb * 1024 * 1024)
        repetitions = max(1, target_size // base_size)
        
        # Generate content
        full_content = "WEBVTT\n\n"
        for i in range(repetitions):
            start_seconds = i * 30
            end_seconds = start_seconds + 25
            
            start_min, start_sec = divmod(start_seconds, 60)
            end_min, end_sec = divmod(end_seconds, 60)
            
            full_content += f"{start_min:02d}:{start_sec:02d}.000 --> {end_min:02d}:{end_sec:02d}.000\n"
            full_content += f"Performance Speaker {i+1}: Analyzing performance characteristics of the transcript processing pipeline. "
            full_content += f"This includes NLP processing, entity extraction, topic modeling, and output generation. "
            full_content += f"Block {i+1} of {repetitions} for comprehensive performance analysis.\n\n"
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.vtt', delete=False) as f:
            f.write(full_content)
            return f.name
    
    def analyze_cpu_profile(self, stats: pstats.Stats) -> List[ProfileResult]:
        """Analyze CPU profiling results."""
        if not stats:
            return []
        
        # Get top functions by cumulative time
        string_buffer = StringIO()
        stats.print_stats(30)  # Top 30 functions
        profile_output = string_buffer.getvalue()
        
        results = []
        lines = profile_output.split('\n')
        
        for line in lines:
            if line.strip() and not line.startswith('ncalls') and not line.startswith('Ordered'):
                parts = line.split()
                if len(parts) >= 6:
                    try:
                        ncalls = parts[0]
                        tottime = float(parts[1])
                        percall = float(parts[2]) if parts[2] != '0.000' else 0.0
                        cumtime = float(parts[3])
                        percall2 = float(parts[4]) if parts[4] != '0.000' else 0.0
                        filename_func = ' '.join(parts[5:])
                        
                        # Parse calls count
                        calls = int(ncalls.split('/')[0]) if '/' in ncalls else int(ncalls)
                        
                        # Extract function name and file info
                        if ':' in filename_func:
                            file_info, func_name = filename_func.rsplit(':', 1)
                            if '(' in func_name:
                                func_name = func_name.split('(')[0]
                        else:
                            file_info = filename_func
                            func_name = 'unknown'
                        
                        results.append(ProfileResult(
                            function_name=func_name,
                            total_time=tottime,
                            calls=calls,
                            time_per_call=percall,
                            cumulative_time=cumtime,
                            filename=file_info,
                            line_number=0
                        ))
                    except (ValueError, IndexError):
                        continue
        
        return results
    
    def run_comprehensive_profile(self, test_file_size: float = 1.0) -> OptimizationReport:
        """Run comprehensive performance profiling."""
        print(f"🔍 Starting comprehensive performance profiling...")
        print(f"   Test file size: {test_file_size:.1f} MB")
        print(f"   Profiling tools available: {PROFILING_AVAILABLE}")
        
        # Create test data
        test_file = self.create_test_data(test_file_size)
        
        try:
            # Initialize processor
            processor = TranscriptProcessor(self.config)
            
            # Start profiling
            profiler = cProfile.Profile()
            
            # Monitor memory
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024 if PROFILING_AVAILABLE else 0
            peak_memory = start_memory
            
            # Profile the processing
            profiler.enable()
            start_time = time.time()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as output_file:
                processor.process_file(test_file, output_file.name)
                
                # Monitor peak memory
                if PROFILING_AVAILABLE:
                    current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    peak_memory = max(peak_memory, current_memory)
                
                end_time = time.time()
                profiler.disable()
                
                # Clean up output file
                os.unlink(output_file.name)
            
            # Analyze results
            total_time = end_time - start_time
            stats = pstats.Stats(profiler)
            stats.sort_stats('cumulative')
            
            cpu_profiles = self.analyze_cpu_profile(stats)
            
            # Generate bottleneck analysis
            bottlenecks = self.identify_bottlenecks(cpu_profiles, total_time)
            
            # Generate optimization recommendations
            recommendations = self.generate_recommendations(cpu_profiles, bottlenecks, peak_memory)
            
            return OptimizationReport(
                timestamp=datetime.now().isoformat(),
                total_execution_time=total_time,
                peak_memory_mb=peak_memory,
                cpu_profiles=cpu_profiles[:10],  # Top 10 functions
                memory_profiles=[],  # TODO: Implement memory profiling
                bottlenecks=bottlenecks,
                recommendations=recommendations
            )
            
        finally:
            # Clean up test file
            if os.path.exists(test_file):
                os.unlink(test_file)
    
    def identify_bottlenecks(self, cpu_profiles: List[ProfileResult], total_time: float) -> List[str]:
        """Identify performance bottlenecks."""
        bottlenecks = []
        
        if not cpu_profiles:
            return bottlenecks
        
        # Find functions taking more than 10% of total time
        for profile in cpu_profiles:
            if profile.cumulative_time > total_time * 0.1:
                bottlenecks.append(
                    f"Function '{profile.function_name}' takes {profile.cumulative_time:.2f}s "
                    f"({profile.cumulative_time/total_time*100:.1f}% of total time)"
                )
        
        # Find functions with high call counts
        for profile in cpu_profiles:
            if profile.calls > 10000:
                bottlenecks.append(
                    f"Function '{profile.function_name}' called {profile.calls} times "
                    f"({profile.time_per_call*1000:.2f}ms per call)"
                )
        
        # Find slow individual functions
        for profile in cpu_profiles:
            if profile.time_per_call > 0.01:  # 10ms per call
                bottlenecks.append(
                    f"Function '{profile.function_name}' slow per call: "
                    f"{profile.time_per_call*1000:.2f}ms average"
                )
        
        return bottlenecks
    
    def generate_recommendations(self, cpu_profiles: List[ProfileResult], 
                               bottlenecks: List[str], peak_memory: float) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Memory optimization
        if peak_memory > 500:  # > 500MB
            recommendations.append(
                f"High memory usage detected ({peak_memory:.1f} MB). "
                "Consider implementing streaming processing for large files."
            )
        
        # CPU optimization
        slow_functions = [p for p in cpu_profiles if p.time_per_call > 0.01]
        if slow_functions:
            recommendations.append(
                "Optimize slow functions: " + 
                ", ".join([f"'{p.function_name}'" for p in slow_functions[:3]])
            )
        
        # High call count functions
        frequent_functions = [p for p in cpu_profiles if p.calls > 5000]
        if frequent_functions:
            recommendations.append(
                "Consider caching or reducing calls for frequently called functions: " +
                ", ".join([f"'{p.function_name}'" for p in frequent_functions[:3]])
            )
        
        # NLP-specific optimizations
        nlp_functions = [p for p in cpu_profiles if 'nlp' in p.function_name.lower() or 'spacy' in p.function_name.lower()]
        if nlp_functions:
            recommendations.append(
                "NLP processing detected. Consider using smaller models or batch processing for better performance."
            )
        
        # I/O optimization
        io_functions = [p for p in cpu_profiles if any(keyword in p.function_name.lower() 
                                                     for keyword in ['read', 'write', 'open', 'close'])]
        if io_functions:
            recommendations.append(
                "I/O operations detected. Consider using buffered I/O or async processing for large files."
            )
        
        # General recommendations
        recommendations.extend([
            "Use profiling results to guide optimization efforts",
            "Consider implementing caching for expensive operations",
            "Monitor memory usage patterns for potential leaks",
            "Test performance with various file sizes",
            "Consider parallel processing for CPU-intensive tasks"
        ])
        
        return recommendations
    
    def save_profile_report(self, report: OptimizationReport, output_file: str = None):
        """Save optimization report to file."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"optimization_report_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(asdict(report), f, indent=2)
        
        print(f"📁 Optimization report saved to: {output_file}")
        return output_file
    
    def print_optimization_report(self, report: OptimizationReport):
        """Print formatted optimization report."""
        print("\n" + "=" * 70)
        print("🚀 PERFORMANCE OPTIMIZATION REPORT")
        print("=" * 70)
        
        print(f"⏱️  Total Execution Time: {report.total_execution_time:.2f} seconds")
        print(f"🧠 Peak Memory Usage: {report.peak_memory_mb:.1f} MB")
        print(f"📊 Analysis Date: {report.timestamp}")
        
        # Top CPU functions
        print(f"\n🔥 Top CPU-Intensive Functions:")
        for i, profile in enumerate(report.cpu_profiles[:5], 1):
            print(f"   {i}. {profile.function_name}")
            print(f"      Total Time: {profile.total_time:.3f}s")
            print(f"      Calls: {profile.calls}")
            print(f"      Time/Call: {profile.time_per_call*1000:.2f}ms")
            print(f"      Cumulative: {profile.cumulative_time:.3f}s")
            print()
        
        # Bottlenecks
        if report.bottlenecks:
            print(f"🚨 Identified Bottlenecks:")
            for i, bottleneck in enumerate(report.bottlenecks, 1):
                print(f"   {i}. {bottleneck}")
            print()
        
        # Recommendations
        print(f"💡 Optimization Recommendations:")
        for i, rec in enumerate(report.recommendations, 1):
            print(f"   {i}. {rec}")
        
        print("\n" + "=" * 70)


def main():
    """Main optimization and profiling application."""
    print("⚡ Customer Solution Snapshot Generator - Performance Optimizer")
    print("=" * 70)
    
    if not PROFILING_AVAILABLE:
        print("⚠️  Warning: Some profiling tools not available.")
        print("   Install with: pip install line-profiler memory-profiler psutil")
        print("   Basic profiling will still be available.\n")
    
    try:
        # Initialize profiler
        config = Config.get_default()
        profiler = PerformanceProfiler(config)
        
        # Test different file sizes
        test_sizes = [0.5, 1.0, 2.0]  # MB
        
        for size in test_sizes:
            print(f"\n🔍 Profiling with {size:.1f} MB test file...")
            
            # Run comprehensive profiling
            report = profiler.run_comprehensive_profile(size)
            
            # Print results
            profiler.print_optimization_report(report)
            
            # Save detailed report
            output_file = f"optimization_report_{size:.1f}MB_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            profiler.save_profile_report(report, output_file)
            
            print(f"📄 Detailed report saved to: {output_file}")
        
        print(f"\n🎉 Performance optimization analysis completed!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Profiling interrupted by user")
    except Exception as e:
        print(f"\n💥 Profiling failed: {e}")
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())