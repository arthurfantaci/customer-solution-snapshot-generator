#!/usr/bin/env python3
"""
Test suite for error tracking and analysis functionality.

This script tests the error tracking system, error analysis dashboard,
and error handling utilities to ensure they work correctly.
"""

import os
import sys
import time
import json
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.customer_snapshot.monitoring.error_tracker import (
    ErrorTracker, ErrorSeverity, ErrorCategory, ErrorContext, ErrorRecord,
    ErrorClassifier, ErrorAggregator, get_error_tracker, track_error, track_exception
)
from src.customer_snapshot.utils.error_handling import (
    with_error_tracking, with_retry, with_timeout, with_fallback, 
    error_context, suppress_errors, ErrorBoundary, safe_execute, CircuitBreaker
)


class TestErrorClassifier(unittest.TestCase):
    """Test error classification functionality."""
    
    def setUp(self):
        self.classifier = ErrorClassifier()
    
    def test_authentication_error_classification(self):
        """Test classification of authentication errors."""
        message = "Authentication failed: invalid credentials"
        exception_type = "AuthenticationError"
        stack_trace = "Traceback: authentication module failed"
        
        category = self.classifier.classify_error(message, exception_type, stack_trace)
        self.assertEqual(category, ErrorCategory.AUTHENTICATION)
    
    def test_api_error_classification(self):
        """Test classification of API errors."""
        message = "HTTP 502 Bad Gateway: service unavailable"
        exception_type = "HTTPError"
        stack_trace = "requests.exceptions.HTTPError"
        
        category = self.classifier.classify_error(message, exception_type, stack_trace)
        self.assertEqual(category, ErrorCategory.API_ERROR)
    
    def test_file_io_classification(self):
        """Test classification of file I/O errors."""
        message = "File not found: /path/to/file.txt"
        exception_type = "FileNotFoundError"
        stack_trace = "open('/path/to/file.txt')"
        
        category = self.classifier.classify_error(message, exception_type, stack_trace)
        self.assertEqual(category, ErrorCategory.FILE_IO)
    
    def test_severity_determination(self):
        """Test error severity determination."""
        # Critical error
        severity = self.classifier.determine_severity("SystemError", "system failure")
        self.assertEqual(severity, ErrorSeverity.CRITICAL)
        
        # Fatal error
        severity = self.classifier.determine_severity("Exception", "fatal error occurred")
        self.assertEqual(severity, ErrorSeverity.FATAL)
        
        # Regular error
        severity = self.classifier.determine_severity("ValueError", "invalid value")
        self.assertEqual(severity, ErrorSeverity.ERROR)


class TestErrorAggregator(unittest.TestCase):
    """Test error aggregation functionality."""
    
    def setUp(self):
        self.aggregator = ErrorAggregator()
    
    def test_fingerprint_generation(self):
        """Test error fingerprint generation."""
        context = ErrorContext(function_name="test_func", module_name="test_module")
        
        fingerprint1 = self.aggregator.generate_fingerprint(
            "Test error", "ValueError", "stack trace", context
        )
        fingerprint2 = self.aggregator.generate_fingerprint(
            "Test error", "ValueError", "stack trace", context
        )
        
        self.assertEqual(fingerprint1, fingerprint2)
    
    def test_error_aggregation(self):
        """Test that similar errors are aggregated."""
        context = ErrorContext(function_name="test_func")
        
        error1 = ErrorRecord(
            id="1",
            timestamp=datetime.now().isoformat(),
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.UNKNOWN,
            message="Test error",
            exception_type="ValueError",
            stack_trace="stack trace",
            context=context,
            fingerprint=self.aggregator.generate_fingerprint(
                "Test error", "ValueError", "stack trace", context
            )
        )
        
        error2 = ErrorRecord(
            id="2",
            timestamp=datetime.now().isoformat(),
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.UNKNOWN,
            message="Test error",
            exception_type="ValueError",
            stack_trace="stack trace",
            context=context,
            fingerprint=self.aggregator.generate_fingerprint(
                "Test error", "ValueError", "stack trace", context
            )
        )
        
        # Add first error
        result1 = self.aggregator.add_error(error1)
        self.assertEqual(result1.count, 1)
        
        # Add similar error - should aggregate
        result2 = self.aggregator.add_error(error2)
        self.assertEqual(result2.count, 2)
        self.assertEqual(result1.id, result2.id)  # Same error object


class TestErrorTracker(unittest.TestCase):
    """Test error tracking functionality."""
    
    def setUp(self):
        self.error_tracker = ErrorTracker()
    
    def test_track_error(self):
        """Test basic error tracking."""
        context = ErrorContext(function_name="test_function")
        
        error_record = self.error_tracker.track_error(
            error_message="Test error message",
            exception_type="TestError",
            stack_trace="test stack trace",
            context=context
        )
        
        self.assertIsNotNone(error_record.id)
        self.assertEqual(error_record.message, "Test error message")
        self.assertEqual(error_record.exception_type, "TestError")
        self.assertEqual(error_record.context.function_name, "test_function")
    
    def test_track_exception(self):
        """Test exception tracking."""
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            context = ErrorContext(function_name="test_exception_function")
            error_record = self.error_tracker.track_exception(e, context)
            
            self.assertEqual(error_record.exception_type, "ValueError")
            self.assertEqual(error_record.message, "Test exception")
    
    def test_error_statistics(self):
        """Test error statistics calculation."""
        # Track some errors
        for i in range(5):
            self.error_tracker.track_error(
                error_message=f"Error {i}",
                exception_type="TestError",
                stack_trace="stack trace"
            )
        
        # Update statistics
        self.error_tracker._update_statistics()
        
        stats = self.error_tracker.get_error_stats()
        self.assertEqual(stats.total_errors, 5)
    
    def test_recent_errors(self):
        """Test recent error retrieval."""
        # Track an error
        self.error_tracker.track_error(
            error_message="Recent error",
            exception_type="TestError",
            stack_trace="stack trace"
        )
        
        recent_errors = self.error_tracker.get_recent_errors(hours=1)
        self.assertEqual(len(recent_errors), 1)
        self.assertEqual(recent_errors[0].message, "Recent error")
    
    def test_error_resolution(self):
        """Test error resolution functionality."""
        # Track an error
        error_record = self.error_tracker.track_error(
            error_message="Resolvable error",
            exception_type="TestError",
            stack_trace="stack trace"
        )
        
        # Resolve the error
        success = self.error_tracker.resolve_error(error_record.id, "Fixed the issue")
        self.assertTrue(success)
        
        # Check that error is marked as resolved
        resolved_error = self.error_tracker.get_error_by_id(error_record.id)
        self.assertTrue(resolved_error.resolved)
        self.assertEqual(resolved_error.resolution_notes, "Fixed the issue")


class TestErrorHandlingDecorators(unittest.TestCase):
    """Test error handling decorators and utilities."""
    
    def test_error_tracking_decorator(self):
        """Test error tracking decorator."""
        @with_error_tracking(category=ErrorCategory.BUSINESS_LOGIC)
        def failing_function():
            raise ValueError("Decorated function error")
        
        with self.assertRaises(ValueError):
            failing_function()
        
        # Check that error was tracked
        error_tracker = get_error_tracker()
        recent_errors = error_tracker.get_recent_errors(hours=1)
        self.assertTrue(any(e.message == "Decorated function error" for e in recent_errors))
    
    def test_retry_decorator(self):
        """Test retry decorator."""
        call_count = 0
        
        @with_retry(max_attempts=3, delay=0.1)
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary failure")
            return "success"
        
        result = flaky_function()
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 3)
    
    def test_fallback_decorator(self):
        """Test fallback decorator."""
        @with_fallback(fallback_value="default_value")
        def failing_function():
            raise ValueError("Function failed")
        
        result = failing_function()
        self.assertEqual(result, "default_value")
    
    def test_error_context_manager(self):
        """Test error context manager."""
        with self.assertRaises(ValueError):
            with error_context({"operation": "test_operation"}):
                raise ValueError("Context manager error")
        
        # Check that error was tracked with context
        error_tracker = get_error_tracker()
        recent_errors = error_tracker.get_recent_errors(hours=1)
        context_error = next((e for e in recent_errors if e.message == "Context manager error"), None)
        self.assertIsNotNone(context_error)
        self.assertEqual(context_error.context.additional_data["operation"], "test_operation")
    
    def test_error_boundary(self):
        """Test error boundary."""
        with ErrorBoundary("test_boundary", fallback_value="boundary_fallback") as boundary:
            raise ValueError("Boundary error")
        
        self.assertEqual(len(boundary.errors), 1)
        self.assertEqual(boundary.get_result(), "boundary_fallback")
    
    def test_suppress_errors(self):
        """Test error suppression."""
        with suppress_errors((ValueError,)):
            raise ValueError("Suppressed error")
        
        # Should not raise an exception
        self.assertTrue(True)  # If we reach here, suppression worked
    
    def test_safe_execute(self):
        """Test safe execute function."""
        def failing_function():
            raise ValueError("Safe execute error")
        
        result = safe_execute(failing_function, fallback_value="safe_fallback")
        self.assertEqual(result, "safe_fallback")
    
    def test_circuit_breaker(self):
        """Test circuit breaker pattern."""
        call_count = 0
        
        @CircuitBreaker(failure_threshold=3, recovery_timeout=1)
        def unreliable_function():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Service unavailable")
        
        # Trigger circuit breaker
        for _ in range(3):
            with self.assertRaises(ConnectionError):
                unreliable_function()
        
        # Circuit should be open now
        with self.assertRaises(Exception) as cm:
            unreliable_function()
        
        self.assertIn("Circuit breaker is OPEN", str(cm.exception))


class TestErrorExport(unittest.TestCase):
    """Test error export functionality."""
    
    def setUp(self):
        self.error_tracker = ErrorTracker()
        self.temp_dir = tempfile.mkdtemp()
    
    def test_json_export(self):
        """Test JSON export functionality."""
        # Track some test errors
        for i in range(3):
            self.error_tracker.track_error(
                error_message=f"Export test error {i}",
                exception_type="ExportTestError",
                stack_trace="export test stack trace"
            )
        
        # Export to JSON
        export_file = os.path.join(self.temp_dir, "test_export.json")
        self.error_tracker.export_errors(export_file, format='json')
        
        # Verify export file
        self.assertTrue(os.path.exists(export_file))
        
        with open(export_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['total_errors'], 3)
        self.assertIn('errors', data)
        self.assertEqual(len(data['errors']), 3)
    
    def test_csv_export(self):
        """Test CSV export functionality."""
        # Track a test error
        self.error_tracker.track_error(
            error_message="CSV export test error",
            exception_type="CSVTestError",
            stack_trace="csv test stack trace"
        )
        
        # Export to CSV
        export_file = os.path.join(self.temp_dir, "test_export.csv")
        self.error_tracker.export_errors(export_file, format='csv')
        
        # Verify export file
        self.assertTrue(os.path.exists(export_file))
        
        with open(export_file, 'r') as f:
            content = f.read()
        
        self.assertIn("CSV export test error", content)
        self.assertIn("CSVTestError", content)


def run_comprehensive_test():
    """Run comprehensive test of error tracking system."""
    print("🧪 Running comprehensive error tracking test...")
    print("=" * 60)
    
    # Test different error scenarios
    error_tracker = get_error_tracker()
    error_tracker.start_background_processing()
    
    try:
        # Test 1: Authentication error
        print("1. Testing authentication error...")
        try:
            raise PermissionError("Access denied: invalid API key")
        except Exception as e:
            context = ErrorContext(
                function_name="authenticate_user",
                module_name="auth_module",
                additional_data={"user_id": "test_user"}
            )
            track_exception(e, context)
        
        # Test 2: Network error with retry
        print("2. Testing network error with retry...")
        @with_retry(max_attempts=3, delay=0.1)
        @with_error_tracking(category=ErrorCategory.NETWORK_ERROR)
        def unreliable_network_call():
            import random
            if random.random() < 0.7:  # 70% chance of failure
                raise ConnectionError("Network timeout")
            return "Success"
        
        try:
            result = unreliable_network_call()
            print(f"   Network call result: {result}")
        except:
            print("   Network call ultimately failed")
        
        # Test 3: File I/O error with fallback
        print("3. Testing file I/O error with fallback...")
        @with_fallback(fallback_value="default_content")
        @with_error_tracking(category=ErrorCategory.FILE_IO)
        def read_config_file():
            raise FileNotFoundError("Config file not found")
        
        content = read_config_file()
        print(f"   File content (with fallback): {content}")
        
        # Test 4: Error boundary
        print("4. Testing error boundary...")
        with ErrorBoundary("parsing_section", fallback_value={}) as boundary:
            # Simulate parsing error
            raise json.JSONDecodeError("Invalid JSON", "test", 0)
        
        result = boundary.get_result()
        print(f"   Boundary result: {result}")
        
        # Test 5: Circuit breaker
        print("5. Testing circuit breaker...")
        @CircuitBreaker(failure_threshold=2, recovery_timeout=1)
        def failing_service():
            raise Exception("Service unavailable")
        
        for i in range(4):
            try:
                failing_service()
            except Exception as e:
                print(f"   Attempt {i+1}: {e}")
        
        # Wait for statistics update
        print("\n⏳ Waiting for statistics update...")
        time.sleep(2)
        error_tracker._update_statistics()
        
        # Display results
        print("\n📊 ERROR TRACKING RESULTS")
        print("-" * 40)
        
        stats = error_tracker.get_error_stats()
        print(f"Total Errors: {stats.total_errors}")
        print(f"Error Rate: {stats.error_rate:.2f} errors/second")
        
        print("\nErrors by Severity:")
        for severity, count in stats.errors_by_severity.items():
            print(f"  {severity.upper()}: {count}")
        
        print("\nErrors by Category:")
        for category, count in stats.errors_by_category.items():
            print(f"  {category.replace('_', ' ').title()}: {count}")
        
        print("\nTop Errors:")
        for i, error in enumerate(stats.top_errors[:3], 1):
            print(f"  {i}. {error['message'][:50]}... (Count: {error['count']})")
        
        # Test export
        print("\n📤 Testing error export...")
        export_file = f"error_test_export_{int(time.time())}.json"
        error_tracker.export_errors(export_file)
        print(f"Exported to: {export_file}")
        
        print("\n✅ Comprehensive error tracking test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        error_tracker.stop_background_processing()


def main():
    """Main test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Error tracking system test suite")
    parser.add_argument('--mode', choices=['unit', 'comprehensive', 'both'], 
                       default='both', help='Test mode to run')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.mode in ['unit', 'both']:
        print("🧪 Running unit tests...")
        
        # Create test suite
        test_suite = unittest.TestSuite()
        
        # Add test cases
        test_classes = [
            TestErrorClassifier,
            TestErrorAggregator, 
            TestErrorTracker,
            TestErrorHandlingDecorators,
            TestErrorExport
        ]
        
        for test_class in test_classes:
            tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
            test_suite.addTests(tests)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
        result = runner.run(test_suite)
        
        if not result.wasSuccessful():
            print(f"\n❌ Unit tests failed: {len(result.failures)} failures, {len(result.errors)} errors")
            return 1
        else:
            print("\n✅ All unit tests passed!")
    
    if args.mode in ['comprehensive', 'both']:
        print("\n" + "=" * 60)
        run_comprehensive_test()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())