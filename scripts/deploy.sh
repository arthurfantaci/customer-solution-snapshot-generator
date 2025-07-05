#!/bin/bash

# Customer Solution Snapshot Generator - Deployment Script
# Simplified deployment automation for common operations

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="development"
DEPLOYMENT_TYPE="docker-compose"
BUILD_IMAGE="false"
PUSH_IMAGE="false"
VERBOSE="false"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
Customer Solution Snapshot Generator - Deployment Script

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    build       Build Docker image
    deploy      Deploy to specified environment
    rollback    Rollback deployment
    status      Get deployment status
    health      Check application health
    logs        View application logs
    clean       Clean up resources

Options:
    -e, --environment ENV     Target environment (development|staging|production) [default: development]
    -t, --type TYPE          Deployment type (docker-compose|kubernetes) [default: docker-compose]
    -b, --build             Build image before deployment
    -p, --push              Push image to registry
    -n, --namespace NS      Kubernetes namespace [default: default]
    --tag TAG               Docker image tag [default: latest]
    -v, --verbose           Verbose output
    -h, --help              Show this help message

Examples:
    $0 build --tag v1.0.0 --push
    $0 deploy --environment staging --build
    $0 deploy --type kubernetes --namespace production
    $0 status --environment production
    $0 logs --environment development --follow

EOF
}

# Parse command line arguments
parse_args() {
    COMMAND=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            build|deploy|rollback|status|health|logs|clean)
                COMMAND="$1"
                shift
                ;;
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -t|--type)
                DEPLOYMENT_TYPE="$2"
                shift 2
                ;;
            -b|--build)
                BUILD_IMAGE="true"
                shift
                ;;
            -p|--push)
                PUSH_IMAGE="true"
                shift
                ;;
            -n|--namespace)
                KUBERNETES_NAMESPACE="$2"
                shift 2
                ;;
            --tag)
                DOCKER_TAG="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE="true"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    if [[ -z "$COMMAND" ]]; then
        log_error "No command specified"
        show_help
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    local missing_tools=()
    
    # Check for required tools
    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    fi
    
    if [[ "$DEPLOYMENT_TYPE" == "docker-compose" ]] && ! command -v docker-compose &> /dev/null; then
        missing_tools+=("docker-compose")
    fi
    
    if [[ "$DEPLOYMENT_TYPE" == "kubernetes" ]] && ! command -v kubectl &> /dev/null; then
        missing_tools+=("kubectl")
    fi
    
    if ! command -v python3 &> /dev/null; then
        missing_tools+=("python3")
    fi
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_error "Please install the missing tools and try again"
        exit 1
    fi
    
    # Check if we're in the right directory
    if [[ ! -f "$PROJECT_ROOT/Dockerfile" ]]; then
        log_error "Dockerfile not found in project root: $PROJECT_ROOT"
        exit 1
    fi
    
    log_info "Prerequisites check passed"
}

# Build Docker image
build_image() {
    log_info "Building Docker image..."
    
    local tag="${DOCKER_TAG:-latest}"
    local image_name="customer-snapshot-generator:$tag"
    local build_args=""
    
    # Add build arguments
    build_args="--build-arg BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    
    # Get git commit if available
    if command -v git &> /dev/null && git rev-parse --git-dir &> /dev/null; then
        local git_commit=$(git rev-parse --short HEAD)
        build_args="$build_args --build-arg VCS_REF=$git_commit"
    fi
    
    # Build image
    if [[ "$VERBOSE" == "true" ]]; then
        docker build $build_args -t "$image_name" "$PROJECT_ROOT"
    else
        docker build $build_args -t "$image_name" "$PROJECT_ROOT" > /dev/null
    fi
    
    log_success "Docker image built: $image_name"
    
    # Push if requested
    if [[ "$PUSH_IMAGE" == "true" ]]; then
        log_info "Pushing image to registry..."
        docker push "$image_name"
        log_success "Image pushed: $image_name"
    fi
}

# Deploy application
deploy_application() {
    log_info "Deploying to $ENVIRONMENT environment using $DEPLOYMENT_TYPE"
    
    # Build image if requested
    if [[ "$BUILD_IMAGE" == "true" ]]; then
        build_image
    fi
    
    # Prepare deployment arguments
    local deploy_args="deploy --environment $ENVIRONMENT --type $DEPLOYMENT_TYPE"
    
    if [[ "$BUILD_IMAGE" == "true" ]]; then
        deploy_args="$deploy_args --build"
    fi
    
    if [[ "$DEPLOYMENT_TYPE" == "kubernetes" ]] && [[ -n "${KUBERNETES_NAMESPACE:-}" ]]; then
        deploy_args="$deploy_args --namespace $KUBERNETES_NAMESPACE"
    fi
    
    if [[ "$VERBOSE" == "true" ]]; then
        deploy_args="$deploy_args --verbose"
    fi
    
    # Execute deployment
    python3 "$PROJECT_ROOT/deploy.py" $deploy_args
    
    log_success "Deployment completed"
    
    # Wait for health check
    log_info "Waiting for application to be healthy..."
    sleep 10
    
    if python3 "$PROJECT_ROOT/deploy.py" health --environment "$ENVIRONMENT"; then
        log_success "Application is healthy and ready"
    else
        log_warning "Application health check failed"
    fi
}

# Rollback deployment
rollback_deployment() {
    log_info "Rolling back $ENVIRONMENT deployment"
    
    python3 "$PROJECT_ROOT/deploy.py" rollback --environment "$ENVIRONMENT" --type "$DEPLOYMENT_TYPE"
    
    log_success "Rollback completed"
}

# Get deployment status
get_status() {
    log_info "Getting deployment status for $ENVIRONMENT"
    
    python3 "$PROJECT_ROOT/deploy.py" status --environment "$ENVIRONMENT"
}

# Check application health
check_health() {
    log_info "Checking application health for $ENVIRONMENT"
    
    if python3 "$PROJECT_ROOT/deploy.py" health --environment "$ENVIRONMENT"; then
        log_success "Application is healthy"
        exit 0
    else
        log_error "Application is unhealthy"
        exit 1
    fi
}

# View application logs
view_logs() {
    log_info "Viewing logs for $ENVIRONMENT"
    
    if [[ "$DEPLOYMENT_TYPE" == "docker-compose" ]]; then
        local compose_file="$PROJECT_ROOT/deployment/docker/docker-compose.$ENVIRONMENT.yml"
        
        if [[ -f "$compose_file" ]]; then
            if [[ "${FOLLOW_LOGS:-false}" == "true" ]]; then
                docker-compose -f "$compose_file" logs -f
            else
                docker-compose -f "$compose_file" logs --tail=100
            fi
        else
            log_error "Docker Compose file not found: $compose_file"
            exit 1
        fi
    elif [[ "$DEPLOYMENT_TYPE" == "kubernetes" ]]; then
        local namespace="${KUBERNETES_NAMESPACE:-default}"
        
        if [[ "${FOLLOW_LOGS:-false}" == "true" ]]; then
            kubectl logs -f -l app=customer-snapshot-generator,environment="$ENVIRONMENT" -n "$namespace"
        else
            kubectl logs --tail=100 -l app=customer-snapshot-generator,environment="$ENVIRONMENT" -n "$namespace"
        fi
    fi
}

# Clean up resources
cleanup_resources() {
    log_info "Cleaning up resources for $ENVIRONMENT"
    
    if [[ "$DEPLOYMENT_TYPE" == "docker-compose" ]]; then
        local compose_file="$PROJECT_ROOT/deployment/docker/docker-compose.$ENVIRONMENT.yml"
        
        if [[ -f "$compose_file" ]]; then
            docker-compose -f "$compose_file" down --volumes --remove-orphans
            log_success "Docker Compose resources cleaned up"
        fi
        
        # Clean up unused images
        docker image prune -f
        log_success "Unused Docker images cleaned up"
        
    elif [[ "$DEPLOYMENT_TYPE" == "kubernetes" ]]; then
        local namespace="${KUBERNETES_NAMESPACE:-default}"
        
        kubectl delete -l app=customer-snapshot-generator,environment="$ENVIRONMENT" -n "$namespace" \
            deployment,service,configmap --ignore-not-found=true
        
        log_success "Kubernetes resources cleaned up"
    fi
}

# Main execution
main() {
    # Parse arguments
    parse_args "$@"
    
    # Set additional variables based on command
    if [[ "$COMMAND" == "logs" ]]; then
        # Check for --follow flag in logs command
        for arg in "$@"; do
            if [[ "$arg" == "--follow" || "$arg" == "-f" ]]; then
                FOLLOW_LOGS="true"
                break
            fi
        done
    fi
    
    # Print deployment info
    log_info "Customer Solution Snapshot Generator - Deployment Script"
    log_info "Environment: $ENVIRONMENT"
    log_info "Deployment Type: $DEPLOYMENT_TYPE"
    log_info "Command: $COMMAND"
    echo
    
    # Check prerequisites
    check_prerequisites
    
    # Execute command
    case "$COMMAND" in
        build)
            build_image
            ;;
        deploy)
            deploy_application
            ;;
        rollback)
            rollback_deployment
            ;;
        status)
            get_status
            ;;
        health)
            check_health
            ;;
        logs)
            view_logs
            ;;
        clean)
            cleanup_resources
            ;;
        *)
            log_error "Unknown command: $COMMAND"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"