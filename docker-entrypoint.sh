#!/bin/bash

# Docker entrypoint script for Customer Solution Snapshot Generator
# Provides flexible startup options and environment setup

set -euo pipefail

# Default values
DEBUG=${DEBUG:-false}
LOG_LEVEL=${LOG_LEVEL:-INFO}
WORKERS=${WORKERS:-1}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Print banner
print_banner() {
    cat << "EOF"
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    Customer Solution Snapshot Generator                       ║
║                           Production Docker Container                         ║
╚═══════════════════════════════════════════════════════════════════════════════╝
EOF
}

# Validate environment
validate_environment() {
    log_info "Validating environment configuration..."

    # Check required environment variables
    if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
        log_warn "ANTHROPIC_API_KEY not set. Some features may not work."
    else
        log_success "ANTHROPIC_API_KEY is configured"
    fi

    # Check optional environment variables
    if [[ -n "${VOYAGEAI_API_KEY:-}" ]]; then
        log_success "VOYAGEAI_API_KEY is configured"
    fi

    if [[ -n "${TAVILY_API_KEY:-}" ]]; then
        log_success "TAVILY_API_KEY is configured"
    fi

    # Validate log level
    case "${LOG_LEVEL}" in
        DEBUG|INFO|WARNING|ERROR|CRITICAL)
            log_success "Log level set to: ${LOG_LEVEL}"
            ;;
        *)
            log_warn "Invalid log level '${LOG_LEVEL}'. Using INFO."
            export LOG_LEVEL=INFO
            ;;
    esac
}

# Setup directories
setup_directories() {
    log_info "Setting up data directories..."

    # Ensure directories exist and have correct permissions
    directories=(
        "/app/data/input"
        "/app/data/output"
        "/app/data/templates"
        "/app/data/logs"
        "/app/data/cache"
    )

    for dir in "${directories[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log_info "Created directory: $dir"
        fi
    done

    # Set proper permissions
    chmod 755 /app/data/*
    log_success "Directory setup completed"
}

# Initialize application
initialize_app() {
    log_info "Initializing application..."

    # Check if models are available
    if python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
        log_success "spaCy model loaded successfully"
    else
        log_warn "spaCy model not found, downloading..."
        python -m spacy download en_core_web_sm
    fi

    # Check NLTK data
    if python -c "import nltk; nltk.data.find('tokenizers/punkt')" 2>/dev/null; then
        log_success "NLTK data available"
    else
        log_warn "NLTK data not found, downloading..."
        python -c "import nltk; nltk.download('punkt', quiet=True)"
    fi

    # Test configuration
    if python -c "from customer_snapshot.utils.config import Config; Config.get_default().validate()" 2>/dev/null; then
        log_success "Configuration validation passed"
    else
        log_error "Configuration validation failed"
        exit 1
    fi
}

# Health check function
health_check() {
    log_info "Running health check..."

    # Check if the CLI is working
    if customer-snapshot config-info >/dev/null 2>&1; then
        log_success "CLI health check passed"
        return 0
    else
        log_error "CLI health check failed"
        return 1
    fi
}

# Run system test
run_system_test() {
    log_info "Running system test..."

    # Create a temporary test file
    cat > /tmp/test.vtt << 'EOF'
WEBVTT

00:00:01.000 --> 00:00:05.000
Test Speaker: This is a system test transcript.

00:00:05.000 --> 00:00:10.000
Test Speaker: Testing the Customer Solution Snapshot Generator.
EOF

    # Run the test
    if customer-snapshot process /tmp/test.vtt -o /tmp/test_output.md >/dev/null 2>&1; then
        log_success "System test passed"
        rm -f /tmp/test.vtt /tmp/test_output.md
        return 0
    else
        log_error "System test failed"
        rm -f /tmp/test.vtt /tmp/test_output.md
        return 1
    fi
}

# Handle different startup modes
handle_command() {
    case "${1:-}" in
        "server")
            log_info "Starting in server mode..."
            # Future: Start web server
            log_warn "Server mode not yet implemented"
            exit 1
            ;;
        "worker")
            log_info "Starting in worker mode..."
            # Future: Start background worker
            log_warn "Worker mode not yet implemented"
            exit 1
            ;;
        "test")
            log_info "Running in test mode..."
            run_system_test
            exit $?
            ;;
        "health")
            health_check
            exit $?
            ;;
        "bash"|"sh")
            log_info "Starting interactive shell..."
            exec /bin/bash
            ;;
        "customer-snapshot")
            # Pass through to CLI
            shift
            log_info "Executing CLI command: customer-snapshot $*"
            exec customer-snapshot "$@"
            ;;
        *)
            # Default: pass through all arguments
            log_info "Executing command: $*"
            exec "$@"
            ;;
    esac
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    # Add any cleanup tasks here
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Main execution
main() {
    print_banner

    # Setup
    validate_environment
    setup_directories
    initialize_app

    # Handle the command
    if [[ $# -eq 0 ]]; then
        log_info "No command specified, showing help..."
        customer-snapshot --help
    else
        handle_command "$@"
    fi
}

# Execute main function with all arguments
main "$@"
