"""
Memory optimization utilities for Customer Solution Snapshot Generator.

This module provides memory-efficient processing strategies, monitoring tools,
and optimization techniques for handling large transcript files.
"""

import functools
import gc
import logging
import mmap
import threading
import weakref
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import (
    Any,
    Callable,
    Optional,
    TypeVar,
)

import psutil


try:
    from pympler import muppy, summary, tracker

    PYMPLER_AVAILABLE = True
except ImportError:
    PYMPLER_AVAILABLE = False

from .config import Config


T = TypeVar("T")


@dataclass
class MemoryMetrics:
    """Memory usage metrics snapshot."""

    timestamp: str
    rss_mb: float  # Resident Set Size
    vms_mb: float  # Virtual Memory Size
    percent: float  # Memory percentage
    available_mb: float
    swap_used_mb: float
    gc_objects: int

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class MemoryTracker:
    """Tracks memory usage and provides optimization insights."""

    def __init__(self):
        self.process = psutil.Process()
        self.baseline_memory = None
        self.peak_memory = 0
        self.snapshots = []
        self.max_snapshots = 1000

        if PYMPLER_AVAILABLE:
            self.pympler_tracker = tracker.SummaryTracker()
        else:
            self.pympler_tracker = None

    def get_current_metrics(self) -> MemoryMetrics:
        """Get current memory metrics."""
        memory_info = self.process.memory_info()
        system_memory = psutil.virtual_memory()
        swap_memory = psutil.swap_memory()

        rss_mb = memory_info.rss / 1024 / 1024
        vms_mb = memory_info.vms / 1024 / 1024
        available_mb = system_memory.available / 1024 / 1024
        swap_used_mb = swap_memory.used / 1024 / 1024

        # Track peak memory
        self.peak_memory = max(self.peak_memory, rss_mb)

        # Count garbage collector objects
        gc_objects = len(gc.get_objects())

        return MemoryMetrics(
            timestamp=datetime.now().isoformat(),
            rss_mb=rss_mb,
            vms_mb=vms_mb,
            percent=self.process.memory_percent(),
            available_mb=available_mb,
            swap_used_mb=swap_used_mb,
            gc_objects=gc_objects,
        )

    def set_baseline(self):
        """Set current memory usage as baseline."""
        self.baseline_memory = self.get_current_metrics()
        logging.info(f"Memory baseline set: {self.baseline_memory.rss_mb:.1f} MB")

    def take_snapshot(self, label: str = "") -> MemoryMetrics:
        """Take a memory snapshot."""
        metrics = self.get_current_metrics()

        # Add to snapshots
        snapshot_data = {
            "label": label,
            "metrics": metrics,
            "delta_from_baseline": None,
        }

        if self.baseline_memory:
            snapshot_data["delta_from_baseline"] = (
                metrics.rss_mb - self.baseline_memory.rss_mb
            )

        self.snapshots.append(snapshot_data)

        # Limit snapshot history
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots = self.snapshots[-self.max_snapshots :]

        return metrics

    def get_memory_growth(self) -> Optional[float]:
        """Get memory growth since baseline in MB."""
        if not self.baseline_memory:
            return None

        current = self.get_current_metrics()
        return current.rss_mb - self.baseline_memory.rss_mb

    def get_peak_memory(self) -> float:
        """Get peak memory usage in MB."""
        return self.peak_memory

    def analyze_memory_usage(self) -> dict[str, Any]:
        """Analyze memory usage patterns."""
        if len(self.snapshots) < 2:
            return {"error": "Insufficient snapshots for analysis"}

        # Calculate memory trends
        memory_values = [s["metrics"].rss_mb for s in self.snapshots]
        growth_rate = (memory_values[-1] - memory_values[0]) / len(memory_values)

        # Identify memory spikes
        avg_memory = sum(memory_values) / len(memory_values)
        spikes = [s for s in self.snapshots if s["metrics"].rss_mb > avg_memory * 1.5]

        return {
            "snapshots_count": len(self.snapshots),
            "baseline_memory_mb": self.baseline_memory.rss_mb
            if self.baseline_memory
            else None,
            "current_memory_mb": memory_values[-1],
            "peak_memory_mb": self.peak_memory,
            "average_memory_mb": avg_memory,
            "memory_growth_rate_mb": growth_rate,
            "memory_spikes": len(spikes),
            "gc_objects_current": self.snapshots[-1]["metrics"].gc_objects,
            "analysis_timestamp": datetime.now().isoformat(),
        }

    def print_memory_report(self):
        """Print formatted memory usage report."""
        analysis = self.analyze_memory_usage()

        print("\n" + "=" * 50)
        print("🧠 MEMORY USAGE ANALYSIS")
        print("=" * 50)

        if "error" in analysis:
            print(f"❌ {analysis['error']}")
            return

        print(f"📊 Snapshots analyzed: {analysis['snapshots_count']}")

        if analysis["baseline_memory_mb"]:
            print(f"🏁 Baseline memory: {analysis['baseline_memory_mb']:.1f} MB")

        print(f"📈 Current memory: {analysis['current_memory_mb']:.1f} MB")
        print(f"🔺 Peak memory: {analysis['peak_memory_mb']:.1f} MB")
        print(f"📊 Average memory: {analysis['average_memory_mb']:.1f} MB")
        print(f"📈 Growth rate: {analysis['memory_growth_rate_mb']:.2f} MB/snapshot")
        print(f"⚡ Memory spikes: {analysis['memory_spikes']}")
        print(f"🗑️  GC objects: {analysis['gc_objects_current']:,}")

        # Memory usage status
        current_mb = analysis["current_memory_mb"]
        if current_mb > 1000:
            print("🚨 HIGH MEMORY USAGE - Consider optimization")
        elif current_mb > 500:
            print("⚠️  MODERATE MEMORY USAGE - Monitor closely")
        else:
            print("✅ NORMAL MEMORY USAGE")


class MemoryOptimizer:
    """Provides memory optimization strategies and utilities."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.get_default()
        self.tracker = MemoryTracker()
        self._object_cache = weakref.WeakValueDictionary()

    @contextmanager
    def memory_monitoring(self, operation_name: str = "operation"):
        """Context manager for monitoring memory during operations."""
        self.tracker.take_snapshot(f"Before {operation_name}")

        try:
            yield self.tracker
        finally:
            self.tracker.take_snapshot(f"After {operation_name}")

            # Force garbage collection
            self.force_garbage_collection()

    def force_garbage_collection(self):
        """Force garbage collection and return collected objects count."""
        collected = gc.collect()
        logging.debug(f"Garbage collection freed {collected} objects")
        return collected

    def optimize_for_large_files(self):
        """Apply optimizations for processing large files."""
        # Increase garbage collection frequency
        gc.set_threshold(700, 10, 10)  # More aggressive GC

        # Disable debug flags that consume memory
        gc.set_debug(0)

        logging.info("Applied large file memory optimizations")

    def get_memory_efficient_reader(
        self, file_path: str, chunk_size: int = 8192
    ) -> Iterator[str]:
        """Get memory-efficient file reader using chunks."""
        try:
            with open(file_path, encoding="utf-8", buffering=chunk_size) as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
            raise

    def get_mmap_reader(self, file_path: str) -> Iterator[bytes]:
        """Get memory-mapped file reader for large files."""
        try:
            with open(file_path, "rb") as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
                    yield mmapped_file
        except Exception as e:
            logging.error(f"Error memory-mapping file {file_path}: {e}")
            raise

    @functools.lru_cache(maxsize=128)
    def cached_operation(self, key: str, operation: Callable[[], T]) -> T:
        """Cache expensive operations with memory management."""
        return operation()

    def clear_caches(self):
        """Clear all internal caches to free memory."""
        self.cached_operation.cache_clear()
        self._object_cache.clear()
        logging.info("Cleared internal caches")

    def stream_process_large_text(
        self, text: str, chunk_size: int = 10000
    ) -> Iterator[str]:
        """Process large text in chunks to manage memory."""
        for i in range(0, len(text), chunk_size):
            yield text[i : i + chunk_size]


class StreamingVTTReader:
    """Memory-efficient VTT file reader that processes files in chunks."""

    def __init__(self, chunk_size: int = 8192):
        self.chunk_size = chunk_size
        self.buffer = ""

    def read_streaming(self, file_path: str) -> Iterator[dict[str, Any]]:
        """Read VTT file in chunks and yield complete subtitle entries."""
        try:
            with open(file_path, encoding="utf-8") as f:
                current_subtitle = {}
                in_subtitle = False

                for line in f:
                    line = line.strip()

                    # Skip WEBVTT header and empty lines at start
                    if not line or line == "WEBVTT":
                        continue

                    # Check if this is a timestamp line
                    if "-->" in line:
                        current_subtitle["timestamp"] = line
                        in_subtitle = True
                        current_subtitle["text"] = []
                        continue

                    # If we're in a subtitle and hit an empty line, yield the subtitle
                    if in_subtitle and not line:
                        if current_subtitle.get("text"):
                            current_subtitle["text"] = " ".join(
                                current_subtitle["text"]
                            )
                            yield current_subtitle

                        current_subtitle = {}
                        in_subtitle = False
                        continue

                    # Add text lines to current subtitle
                    if in_subtitle:
                        current_subtitle["text"].append(line)

                # Yield final subtitle if exists
                if in_subtitle and current_subtitle.get("text"):
                    current_subtitle["text"] = " ".join(current_subtitle["text"])
                    yield current_subtitle

        except Exception as e:
            logging.error(f"Error streaming VTT file {file_path}: {e}")
            raise


class MemoryEfficientNLPProcessor:
    """Memory-efficient NLP processing for large texts."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.get_default()
        self.optimizer = MemoryOptimizer(config)
        self._nlp_model = None

    @property
    def nlp_model(self):
        """Lazy-load NLP model to save memory."""
        if self._nlp_model is None:
            try:
                import spacy

                self._nlp_model = spacy.load("en_core_web_sm")
                # Disable unnecessary pipeline components to save memory
                self._nlp_model.disable_pipes(["parser", "tagger"])
            except Exception as e:
                logging.error(f"Error loading spaCy model: {e}")
                raise
        return self._nlp_model

    def process_text_streaming(
        self, text: str, chunk_size: int = 10000
    ) -> Iterator[dict[str, Any]]:
        """Process large text in memory-efficient chunks."""
        with self.optimizer.memory_monitoring("NLP processing"):
            for chunk in self.optimizer.stream_process_large_text(text, chunk_size):
                # Process chunk with NLP
                doc = self.nlp_model(chunk)

                # Extract entities and yield results
                entities = [(ent.text, ent.label_) for ent in doc.ents]

                yield {"text": chunk, "entities": entities, "length": len(chunk)}

                # Force cleanup after each chunk
                del doc
                self.optimizer.force_garbage_collection()

    def extract_entities_batch(
        self, texts: list[str], batch_size: int = 10
    ) -> Iterator[list[dict[str, Any]]]:
        """Process multiple texts in memory-efficient batches."""
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            with self.optimizer.memory_monitoring(f"Batch {i // batch_size + 1}"):
                results = []

                for text in batch:
                    doc = self.nlp_model(text)
                    entities = [(ent.text, ent.label_) for ent in doc.ents]
                    results.append({"text": text, "entities": entities})
                    del doc

                yield results

                # Cleanup after batch
                self.optimizer.force_garbage_collection()


def memory_profile(func: Callable) -> Callable:
    """Decorator to profile memory usage of functions."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        tracker = MemoryTracker()
        tracker.set_baseline()
        tracker.take_snapshot(f"Start {func.__name__}")

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            tracker.take_snapshot(f"End {func.__name__}")

            # Log memory usage
            growth = tracker.get_memory_growth()
            if growth and growth > 10:  # More than 10MB growth
                logging.warning(
                    f"Function {func.__name__} used {growth:.1f} MB of memory"
                )

            tracker.print_memory_report()

    return wrapper


def memory_limit(max_mb: int):
    """Decorator to enforce memory limits on functions."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tracker = MemoryTracker()

            def check_memory():
                current = tracker.get_current_metrics()
                if current.rss_mb > max_mb:
                    raise MemoryError(
                        f"Function {func.__name__} exceeded memory limit: "
                        f"{current.rss_mb:.1f} MB > {max_mb} MB"
                    )

            # Check before execution
            check_memory()

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Check after execution
                check_memory()

        return wrapper

    return decorator


class MemoryMonitoringService:
    """Background service for continuous memory monitoring."""

    def __init__(self, config: Optional[Config] = None, interval: int = 30):
        self.config = config or Config.get_default()
        self.interval = interval
        self.tracker = MemoryTracker()
        self.running = False
        self.thread = None

        # Alert thresholds
        self.memory_threshold_mb = 1000  # 1GB
        self.growth_threshold_mb = 100  # 100MB growth

    def start(self):
        """Start the monitoring service."""
        if self.running:
            return

        self.running = True
        self.tracker.set_baseline()
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()

        logging.info(f"Memory monitoring service started (interval: {self.interval}s)")

    def stop(self):
        """Stop the monitoring service."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)

        logging.info("Memory monitoring service stopped")

    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                metrics = self.tracker.take_snapshot("Periodic check")

                # Check for alerts
                self._check_alerts(metrics)

                # Log periodic status
                if len(self.tracker.snapshots) % 10 == 0:  # Every 10 snapshots
                    logging.info(
                        f"Memory status: {metrics.rss_mb:.1f} MB RSS, "
                        f"{metrics.percent:.1f}% of system memory"
                    )

                threading.Event().wait(self.interval)

            except Exception as e:
                logging.error(f"Error in memory monitoring loop: {e}")
                threading.Event().wait(self.interval)

    def _check_alerts(self, metrics: MemoryMetrics):
        """Check for memory-related alerts."""
        # High memory usage alert
        if metrics.rss_mb > self.memory_threshold_mb:
            logging.warning(
                f"High memory usage alert: {metrics.rss_mb:.1f} MB "
                f"(threshold: {self.memory_threshold_mb} MB)"
            )

        # Memory growth alert
        growth = self.tracker.get_memory_growth()
        if growth and growth > self.growth_threshold_mb:
            logging.warning(
                f"High memory growth alert: +{growth:.1f} MB "
                f"(threshold: {self.growth_threshold_mb} MB)"
            )

        # System memory pressure alert
        if metrics.available_mb < 500:  # Less than 500MB available
            logging.critical(
                f"System memory pressure: only {metrics.available_mb:.1f} MB available"
            )


# Global memory monitoring service instance
_memory_service = None


def start_memory_monitoring(config: Optional[Config] = None, interval: int = 30):
    """Start global memory monitoring service."""
    global _memory_service

    if _memory_service is None:
        _memory_service = MemoryMonitoringService(config, interval)

    _memory_service.start()
    return _memory_service


def stop_memory_monitoring():
    """Stop global memory monitoring service."""
    global _memory_service

    if _memory_service:
        _memory_service.stop()


def get_memory_status() -> dict[str, Any]:
    """Get current memory status from global service."""
    global _memory_service

    if _memory_service:
        return _memory_service.tracker.analyze_memory_usage()
    else:
        # Return basic metrics if service not running
        tracker = MemoryTracker()
        return {
            "current_memory_mb": tracker.get_current_metrics().rss_mb,
            "service_running": False,
        }
