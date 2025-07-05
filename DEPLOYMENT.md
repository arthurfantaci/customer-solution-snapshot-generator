# Deployment Automation Guide

This document provides comprehensive guidance for deploying the Customer Solution Snapshot Generator across different environments using automated deployment scripts and configurations.

## Overview

The deployment automation system supports multiple deployment strategies:

- **Docker Compose**: For local development and small-scale deployments
- **Kubernetes**: For production and scalable deployments
- **CI/CD Integration**: Automated deployments via GitHub Actions
- **Multi-Environment**: Development, staging, and production configurations

## Quick Start

### Prerequisites

Install required tools:

```bash
# Docker and Docker Compose
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Kubernetes tools (for K8s deployments)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Python dependencies
pip install pyyaml requests
```

### Simple Deployment

```bash
# Deploy to development environment
./scripts/deploy.sh deploy --environment development --build

# Check deployment status
./scripts/deploy.sh status --environment development

# View logs
./scripts/deploy.sh logs --environment development --follow
```

## Deployment Tools

### 1. Main Deployment Script (`deploy.py`)

Python-based deployment automation with comprehensive features:

```bash
# Build Docker image
python deploy.py build --tag v1.0.0 --push

# Deploy to staging
python deploy.py deploy --environment staging --type docker-compose --build

# Deploy to Kubernetes
python deploy.py deploy --environment production --type kubernetes --namespace production

# Check application health
python deploy.py health --environment production

# Get deployment status
python deploy.py status --environment staging
```

### 2. Shell Script Wrapper (`scripts/deploy.sh`)

Simplified shell interface for common operations:

```bash
# Deploy with build
./scripts/deploy.sh deploy -e staging -b

# Rollback deployment
./scripts/deploy.sh rollback -e staging

# Clean up resources
./scripts/deploy.sh clean -e development

# View live logs
./scripts/deploy.sh logs -e production -f
```

## Environment Configurations

### Development Environment

**Characteristics:**
- Single replica
- Debug logging enabled
- Memory profiling enabled
- 1GB memory limit
- Local volume mounts

**Usage:**
```bash
./scripts/deploy.sh deploy -e development -b
```

### Staging Environment

**Characteristics:**
- 2 replicas for testing load balancing
- INFO logging
- Production-like configuration
- 2GB memory limit
- Persistent volumes

**Usage:**
```bash
./scripts/deploy.sh deploy -e staging -t docker-compose
```

### Production Environment

**Characteristics:**
- 3 replicas for high availability
- Optimized resource allocation
- 4GB memory limit
- Full monitoring and alerting
- Backup and disaster recovery

**Usage:**
```bash
python deploy.py deploy --environment production --type kubernetes --namespace production
```

## Configuration Management

### Deployment Configuration (`deployment/config.yaml`)

Central configuration file defining environment-specific settings:

```yaml
environments:
  production:
    docker_image: customer-snapshot-generator
    docker_tag: latest
    memory_limit: 4g
    cpu_limit: "4.0"
    replicas: 3
    environment_vars:
      LOG_LEVEL: INFO
      MEMORY_LIMIT_MB: "2048"
```

### Environment Variables

Configure deployments using environment variables:

```bash
# Docker settings
export DOCKER_IMAGE=customer-snapshot-generator
export DOCKER_TAG=v1.0.0

# Resource limits
export MEMORY_LIMIT=2g
export CPU_LIMIT=2.0

# Application settings
export LOG_LEVEL=INFO
export ENABLE_MEMORY_MONITORING=true
```

## Docker Compose Deployments

### Structure

Docker Compose deployments include:
- Main application container
- Redis for caching (optional)
- PostgreSQL for metadata (optional)
- Nginx reverse proxy (optional)
- Prometheus monitoring (optional)
- Grafana visualization (optional)

### Deployment Commands

```bash
# Basic deployment
docker-compose -f deployment/docker/docker-compose.production.yml up -d

# With build
docker-compose -f deployment/docker/docker-compose.production.yml up -d --build

# Scale application
docker-compose -f deployment/docker/docker-compose.production.yml up -d --scale customer-snapshot-generator=3

# Update service
docker-compose -f deployment/docker/docker-compose.production.yml up -d customer-snapshot-generator
```

### Monitoring

```bash
# View logs
docker-compose -f deployment/docker/docker-compose.production.yml logs -f

# Check container status
docker-compose -f deployment/docker/docker-compose.production.yml ps

# Resource usage
docker stats
```

## Kubernetes Deployments

### Cluster Requirements

- Kubernetes 1.20+
- 8GB+ available memory
- 4+ CPU cores
- Persistent volume support
- Ingress controller (optional)

### Deployment Process

1. **Apply namespace and RBAC:**
```bash
kubectl apply -f deployment/kubernetes/namespace.yaml
```

2. **Create secrets:**
```bash
# Update secret values first
kubectl apply -f deployment/kubernetes/secret.yaml
```

3. **Apply configuration:**
```bash
kubectl apply -f deployment/kubernetes/configmap.yaml
```

4. **Deploy application:**
```bash
kubectl apply -f deployment/kubernetes/deployment.yaml
kubectl apply -f deployment/kubernetes/service.yaml
```

5. **Verify deployment:**
```bash
kubectl get pods -n customer-snapshot-generator
kubectl get services -n customer-snapshot-generator
```

### Scaling

```bash
# Scale to 5 replicas
kubectl scale deployment customer-snapshot-generator --replicas=5 -n customer-snapshot-generator

# Horizontal Pod Autoscaler
kubectl autoscale deployment customer-snapshot-generator --cpu-percent=70 --min=3 --max=10 -n customer-snapshot-generator
```

### Rolling Updates

```bash
# Update image
kubectl set image deployment/customer-snapshot-generator customer-snapshot-generator=customer-snapshot-generator:v1.1.0 -n customer-snapshot-generator

# Monitor rollout
kubectl rollout status deployment/customer-snapshot-generator -n customer-snapshot-generator

# Rollback if needed
kubectl rollout undo deployment/customer-snapshot-generator -n customer-snapshot-generator
```

## CI/CD Integration

### GitHub Actions Pipeline

The included CI/CD pipeline (`.github/workflows/ci-cd.yml`) provides:

- **Automated Testing**: Unit tests, integration tests, security scans
- **Multi-Platform Builds**: Docker images for AMD64 and ARM64
- **Automated Deployments**: Staging on develop branch, production on tags
- **Security Scanning**: Vulnerability scanning with Trivy
- **Performance Testing**: Automated benchmarking

### Pipeline Triggers

- **Pull Requests**: Run tests and build validation
- **Develop Branch**: Deploy to staging environment
- **Tagged Releases**: Deploy to production environment

### Required Secrets

Configure these secrets in GitHub repository settings:

```bash
# Container registry
GITHUB_TOKEN  # Automatically provided

# Deployment credentials
STAGING_HOST
STAGING_SSH_KEY
KUBE_CONFIG
PRODUCTION_REGISTRY

# API keys
ANTHROPIC_API_KEY
VOYAGEAI_API_KEY
TAVILY_API_KEY

# Monitoring
SLACK_WEBHOOK  # For deployment notifications
```

## Security Considerations

### Container Security

- **Non-root user**: Containers run as user 1000
- **Read-only filesystem**: Where possible
- **No privilege escalation**: Security context enforced
- **Minimal base image**: Alpine-based images
- **Regular updates**: Automated dependency updates

### Secret Management

- **Environment separation**: Different secrets per environment
- **External secret management**: Integration with HashiCorp Vault
- **Rotation**: Regular secret rotation procedures
- **Encryption**: Secrets encrypted at rest and in transit

### Network Security

- **Network policies**: Restricted ingress/egress
- **TLS encryption**: All communications encrypted
- **Firewall rules**: Minimal required ports
- **VPN access**: Restricted administrative access

## Monitoring and Observability

### Health Checks

- **Application health**: Custom health check endpoint
- **Container health**: Docker/Kubernetes health checks
- **Dependency health**: Database and cache connectivity
- **Performance health**: Memory and CPU monitoring

### Logging

- **Structured logging**: JSON format for machine processing
- **Log aggregation**: Centralized log collection
- **Log retention**: Configurable retention policies
- **Security logging**: Audit trail for security events

### Metrics

- **Application metrics**: Custom business metrics
- **System metrics**: CPU, memory, disk, network
- **Performance metrics**: Response times, throughput
- **Error metrics**: Error rates and types

### Alerting

Configure alerts for:
- High memory usage (>80%)
- High CPU usage (>85%)
- Error rate spikes (>5%)
- Health check failures
- Deployment failures

## Backup and Disaster Recovery

### Data Backup

```bash
# Backup application data
kubectl exec -it deployment/customer-snapshot-generator -n customer-snapshot-generator -- tar czf - /app/data | gzip > backup-$(date +%Y%m%d).tar.gz

# Backup database (if using PostgreSQL)
kubectl exec -it postgres-0 -n customer-snapshot-generator -- pg_dump -U app_user customer_snapshot | gzip > db-backup-$(date +%Y%m%d).sql.gz
```

### Disaster Recovery

1. **Infrastructure Recovery:**
   - Provision new infrastructure
   - Deploy from latest known good configuration
   - Restore data from backups

2. **Application Recovery:**
   - Deploy latest stable version
   - Restore application data
   - Verify functionality

3. **Database Recovery:**
   - Restore database from backup
   - Verify data integrity
   - Update application connections

## Troubleshooting

### Common Issues

**Deployment Failures:**
```bash
# Check deployment status
kubectl describe deployment customer-snapshot-generator -n customer-snapshot-generator

# Check pod logs
kubectl logs -l app=customer-snapshot-generator -n customer-snapshot-generator --tail=100

# Check events
kubectl get events -n customer-snapshot-generator --sort-by='.lastTimestamp'
```

**Health Check Failures:**
```bash
# Manual health check
python deploy.py health --environment production

# Container health check
docker exec customer-snapshot-production python /usr/local/bin/healthcheck.py

# Check resource usage
kubectl top pods -n customer-snapshot-generator
```

**Performance Issues:**
```bash
# Monitor resource usage
kubectl top nodes
kubectl top pods -n customer-snapshot-generator

# Check application metrics
curl http://localhost:8080/metrics

# Run performance tests
python benchmark.py
```

### Debug Mode

Enable debug mode for troubleshooting:

```bash
# Deploy with debug mode
DEBUG=true ./scripts/deploy.sh deploy -e development

# Check debug logs
kubectl logs -l app=customer-snapshot-generator -n customer-snapshot-generator -f | grep DEBUG
```

## Best Practices

### Development

- **Test locally first**: Always test deployments locally
- **Use staging**: Test in staging before production
- **Version everything**: Tag all deployments with versions
- **Monitor deployments**: Watch metrics during deployments

### Operations

- **Blue-green deployments**: Zero-downtime deployments
- **Canary releases**: Gradual rollouts for safety
- **Rollback plans**: Always have rollback procedures ready
- **Regular testing**: Test disaster recovery procedures

### Security

- **Principle of least privilege**: Minimal required permissions
- **Regular updates**: Keep all components updated
- **Security scanning**: Regular vulnerability assessments
- **Access control**: Audit and control access regularly

## Performance Optimization

### Resource Tuning

```yaml
# Production resource configuration
resources:
  requests:
    memory: "2Gi"
    cpu: "1000m"
  limits:
    memory: "4Gi"
    cpu: "2000m"
```

### Scaling Strategies

- **Horizontal scaling**: Add more replicas for load
- **Vertical scaling**: Increase resource limits
- **Auto-scaling**: Configure HPA for automatic scaling
- **Load balancing**: Distribute traffic efficiently

### Performance Monitoring

- Monitor response times and throughput
- Track resource utilization trends
- Set up performance alerts
- Regular performance testing

## Support and Maintenance

### Regular Maintenance

- **Security updates**: Monthly security patch updates
- **Dependency updates**: Regular dependency updates
- **Performance reviews**: Quarterly performance assessments
- **Backup verification**: Monthly backup restoration tests

### Support Procedures

1. **Issue Identification**: Monitor alerts and logs
2. **Impact Assessment**: Determine severity and scope
3. **Resolution**: Apply appropriate fixes
4. **Post-Incident**: Document and improve processes

---

*This deployment automation system provides enterprise-grade deployment capabilities with comprehensive monitoring, security, and scalability features for the Customer Solution Snapshot Generator.*