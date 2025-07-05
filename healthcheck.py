#!/usr/bin/env python3
"""
Enhanced health check script for Docker container.

This script performs comprehensive health checks to ensure the
Customer Solution Snapshot Generator is functioning correctly.
Integrates with the advanced monitoring system.
"""
import sys
import os
import traceback
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_python_imports():
    """Check that all required Python modules can be imported."""
    required_modules = [
        'customer_snapshot',
        'customer_snapshot.core.processor',
        'customer_snapshot.utils.config',
        'spacy',
        'nltk',
        'webvtt',
        'anthropic',
        'click'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError as e:
            failed_imports.append(f"{module}: {e}")
    
    if failed_imports:
        print(f"❌ Import check failed:")
        for failure in failed_imports:
            print(f"   - {failure}")
        return False
    
    print("✅ All required modules imported successfully")
    return True


def check_models():
    """Check that required NLP models are available."""
    try:
        import spacy
        import nltk
        
        # Check spaCy model
        try:
            nlp = spacy.load('en_core_web_sm')
            print("✅ spaCy model 'en_core_web_sm' loaded successfully")
        except OSError:
            print("❌ spaCy model 'en_core_web_sm' not found")
            return False
        
        # Check NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
            print("✅ NLTK punkt tokenizer available")
        except LookupError:
            print("❌ NLTK punkt tokenizer not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Model check failed: {e}")
        return False


def check_configuration():
    """Check that configuration is valid."""
    try:
        from customer_snapshot.utils.config import Config
        
        config = Config.get_default()
        
        # Basic validation
        if not hasattr(config, 'anthropic_api_key'):
            print("❌ Configuration missing anthropic_api_key attribute")
            return False
        
        # Check if API key is configured
        if config.anthropic_api_key:
            print("✅ Anthropic API key is configured")
        else:
            print("⚠️  Anthropic API key not configured (some features may not work)")
        
        print("✅ Configuration validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration check failed: {e}")
        return False


def check_file_permissions():
    """Check that required directories are writable."""
    directories_to_check = [
        '/app/data/input',
        '/app/data/output',
        '/app/data/logs',
        '/tmp'
    ]
    
    for directory in directories_to_check:
        dir_path = Path(directory)
        
        # Check if directory exists
        if not dir_path.exists():
            print(f"❌ Directory does not exist: {directory}")
            return False
        
        # Check if directory is writable
        if not os.access(directory, os.W_OK):
            print(f"❌ Directory not writable: {directory}")
            return False
        
        print(f"✅ Directory accessible: {directory}")
    
    return True


def check_cli_functionality():
    """Check that the CLI is working."""
    try:
        import subprocess
        
        # Test basic CLI functionality
        result = subprocess.run(
            ['customer-snapshot', 'config-info'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ CLI functionality check passed")
            return True
        else:
            print(f"❌ CLI functionality check failed:")
            print(f"   Return code: {result.returncode}")
            print(f"   STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ CLI functionality check timed out")
        return False
    except Exception as e:
        print(f"❌ CLI functionality check failed: {e}")
        return False


def check_memory_usage():
    """Check memory usage to ensure container is healthy."""
    try:
        import psutil
        
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        if memory_percent > 90:
            print(f"❌ High memory usage: {memory_percent:.1f}%")
            return False
        elif memory_percent > 75:
            print(f"⚠️  Moderate memory usage: {memory_percent:.1f}%")
        else:
            print(f"✅ Memory usage normal: {memory_percent:.1f}%")
        
        return True
        
    except ImportError:
        # psutil not available, skip memory check
        print("⚠️  psutil not available, skipping memory check")
        return True
    except Exception as e:
        print(f"❌ Memory check failed: {e}")
        return False


def check_disk_space():
    """Check available disk space."""
    try:
        import shutil
        
        # Check disk space for /app and /tmp
        for path in ['/app', '/tmp']:
            total, used, free = shutil.disk_usage(path)
            free_percent = (free / total) * 100
            
            if free_percent < 10:
                print(f"❌ Low disk space on {path}: {free_percent:.1f}% free")
                return False
            elif free_percent < 20:
                print(f"⚠️  Limited disk space on {path}: {free_percent:.1f}% free")
            else:
                print(f"✅ Disk space OK on {path}: {free_percent:.1f}% free")
        
        return True
        
    except Exception as e:
        print(f"❌ Disk space check failed: {e}")
        return False


def run_comprehensive_health_check():
    """Run all health checks and return overall status."""
    print("🏥 Running comprehensive health check...")
    print("=" * 50)
    
    checks = [
        ("Python Imports", check_python_imports),
        ("NLP Models", check_models),
        ("Configuration", check_configuration),
        ("File Permissions", check_file_permissions),
        ("CLI Functionality", check_cli_functionality),
        ("Memory Usage", check_memory_usage),
        ("Disk Space", check_disk_space),
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_function in checks:
        print(f"\n🔍 {check_name}:")
        try:
            if check_function():
                passed += 1
            else:
                print(f"   Health check failed: {check_name}")
        except Exception as e:
            print(f"   Health check error in {check_name}: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"📊 Health Check Summary: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All health checks passed! Container is healthy.")
        return True
    else:
        print(f"⚠️  {total - passed} health check(s) failed. Container may have issues.")
        return False


def main():
    """Main health check entry point."""
    try:
        # Set up basic environment
        os.environ.setdefault('PYTHONPATH', '/app/src')
        
        # Try to use advanced health monitoring if available
        try:
            from customer_snapshot.monitoring.health_monitor import HealthMonitor, HealthStatus
            from customer_snapshot.utils.config import Config
            
            print("🔍 Using advanced health monitoring system...")
            config = Config.get_default()
            health_monitor = HealthMonitor(config)
            
            overall_status = health_monitor.get_overall_status()
            health_summary = health_monitor.get_health_summary()
            
            # Print detailed results
            print(f"Overall Status: {overall_status.value.upper()}")
            
            for check_name, check_result in health_summary.get("checks", {}).items():
                status_symbol = {
                    "healthy": "✅",
                    "warning": "⚠️",
                    "critical": "🚨",
                    "unknown": "❓"
                }.get(check_result["status"], "❓")
                
                print(f"{status_symbol} {check_name}: {check_result['message']}")
            
            # Exit based on overall status
            if overall_status in [HealthStatus.HEALTHY, HealthStatus.WARNING]:
                sys.exit(0)  # Healthy (warnings are acceptable for basic health check)
            else:
                sys.exit(1)  # Unhealthy
                
        except ImportError:
            print("📋 Advanced monitoring not available, using basic health checks...")
            # Fall back to basic health checks
            if run_comprehensive_health_check():
                sys.exit(0)  # Healthy
            else:
                sys.exit(1)  # Unhealthy
            
    except KeyboardInterrupt:
        print("\n⏹️  Health check interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Health check crashed: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()