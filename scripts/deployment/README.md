# Deployment Scripts

Automation tools for deploying and releasing the Customer Solution Snapshot Generator.

## Scripts

### deploy.py
Automated deployment script for various environments.

**Supports:**
- Docker deployment
- Kubernetes deployment
- Docker Compose deployment
- Environment configuration
- Health checks

**Usage:**
```bash
# Deploy to Docker
python scripts/deployment/deploy.py --target docker

# Deploy to Kubernetes
python scripts/deployment/deploy.py --target kubernetes

# Deploy with Docker Compose
python scripts/deployment/deploy.py --target compose
```

**Configuration:**
Edit `deployment/config.yaml` for environment-specific settings.

### release.py
Release automation and version management.

**Features:**
- Version bumping (major/minor/patch)
- Changelog generation
- Git tagging
- Build verification
- Release notes creation

**Usage:**
```bash
# Create patch release
python scripts/deployment/release.py --type patch

# Create minor release
python scripts/deployment/release.py --type minor

# Create major release
python scripts/deployment/release.py --type major
```

### healthcheck.py
Health check utility for deployed applications.

**Features:**
- HTTP endpoint checks
- Database connectivity
- External service verification
- Resource utilization checks
- Detailed status reporting

**Usage:**
```bash
# Check local deployment
python scripts/deployment/healthcheck.py --host localhost --port 8080

# Check production
python scripts/deployment/healthcheck.py --host prod.example.com
```

**Exit Codes:**
- `0`: All checks passed
- `1`: One or more checks failed

## Requirements

```bash
uv sync --extra dev
```

## Environment Variables

Create a `.env` file with:
```ini
DOCKER_REGISTRY=your-registry
KUBECONFIG=/path/to/kubeconfig
ENVIRONMENT=production
```

## Deployment Workflow

1. **Test locally:**
   ```bash
   uv run pytest
   ```

2. **Run health checks:**
   ```bash
   python scripts/deployment/healthcheck.py
   ```

3. **Create release:**
   ```bash
   python scripts/deployment/release.py --type patch
   ```

4. **Deploy:**
   ```bash
   python scripts/deployment/deploy.py --target kubernetes
   ```

5. **Verify deployment:**
   ```bash
   python scripts/deployment/healthcheck.py --host production
   ```

## See Also

- [DEPLOYMENT.md](../../DEPLOYMENT.md) - Detailed deployment guide
- [RELEASE_PROCESS.md](../../RELEASE_PROCESS.md) - Release procedures
