# Upgrading Guide

This guide helps you upgrade between versions of the Customer Solution Snapshot Generator.

## General Upgrade Process

1. **Check Current Version**
   ```bash
   customer-snapshot --version
   ```

2. **Review Breaking Changes**
   - Check the [CHANGELOG.md](CHANGELOG.md) for your target version
   - Review any breaking changes or deprecations

3. **Backup Configuration**
   ```bash
   cp .env .env.backup
   cp monitoring_config.yaml monitoring_config.yaml.backup
   ```

4. **Upgrade Package**
   ```bash
   # Using pip
   pip install --upgrade customer-snapshot

   # Using Docker
   docker pull arthurfantaci/customer-snapshot-generator:latest
   ```

5. **Verify Installation**
   ```bash
   customer-snapshot config-info
   ```

## Version-Specific Upgrade Notes

### Upgrading to v1.0.0

#### Breaking Changes

1. **Configuration Format**
   - Old: Environment variables only
   - New: YAML configuration files supported

   Migration:
   ```bash
   # Generate new config from environment
   customer-snapshot config migrate --from-env
   ```

2. **API Changes**
   - `process_transcript()` renamed to `process_file()`
   - New required parameter: `output_format`

   Update your code:
   ```python
   # Old
   processor.process_transcript(input_file)

   # New
   processor.process_file(input_file, output_format="markdown")
   ```

3. **Docker Volume Mounts**
   - Old: `/data`
   - New: `/app/data/input` and `/app/data/output`

   Update docker-compose.yml:
   ```yaml
   # Old
   volumes:
     - ./data:/data

   # New
   volumes:
     - ./input:/app/data/input
     - ./output:/app/data/output
   ```

#### New Features

- Error tracking system
- Performance monitoring
- Health checks
- Prometheus metrics
- Memory optimization

#### Migration Steps

1. **Update Dependencies**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   python -m nltk.downloader punkt
   ```

2. **Update Configuration**
   ```bash
   # Create new config file
   cp .env.example .env

   # Update with your settings
   nano .env
   ```

3. **Enable New Features**
   ```yaml
   # monitoring_config.yaml
   error_tracking:
     enabled: true

   system_monitoring:
     enabled: true
   ```

### Upgrading to v0.2.0

#### Changes

1. **New CLI Commands**
   - Added `benchmark` command
   - Added `monitor` command

2. **Configuration Updates**
   - New optional settings for monitoring
   - Performance tuning options

#### Migration Steps

1. **Update Package**
   ```bash
   pip install customer-snapshot==0.2.0
   ```

2. **Optional: Enable Monitoring**
   ```bash
   export ENABLE_MONITORING=true
   export PROMETHEUS_PORT=8081
   ```

## Docker Upgrade

### Using Docker Compose

1. **Update docker-compose.yml**
   ```yaml
   version: '3.8'
   services:
     customer-snapshot:
       image: arthurfantaci/customer-snapshot-generator:v1.0.0
       # ... rest of configuration
   ```

2. **Pull New Image**
   ```bash
   docker-compose pull
   ```

3. **Restart Services**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Using Kubernetes

1. **Update Deployment**
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: customer-snapshot
   spec:
     template:
       spec:
         containers:
         - name: customer-snapshot
           image: arthurfantaci/customer-snapshot-generator:v1.0.0
   ```

2. **Apply Changes**
   ```bash
   kubectl apply -f deployment.yaml
   ```

3. **Monitor Rollout**
   ```bash
   kubectl rollout status deployment/customer-snapshot
   ```

## Rollback Procedures

### Using Pip

```bash
# Rollback to specific version
pip install customer-snapshot==0.1.0
```

### Using Docker

```bash
# Rollback to previous version
docker pull arthurfantaci/customer-snapshot-generator:v0.1.0
docker tag arthurfantaci/customer-snapshot-generator:v0.1.0 \
  arthurfantaci/customer-snapshot-generator:latest
```

### Using Kubernetes

```bash
# Rollback deployment
kubectl rollout undo deployment/customer-snapshot

# Or to specific revision
kubectl rollout undo deployment/customer-snapshot --to-revision=2
```

## Data Migration

### VTT File Format

No changes to VTT file format between versions. All existing files remain compatible.

### Output Format

v1.0.0 introduces new output format options:
- Markdown (default, backward compatible)
- HTML (new)
- JSON (new)

To maintain compatibility, use:
```bash
customer-snapshot process input.vtt --output-format markdown
```

### Configuration Migration

#### Environment Variables to YAML

```python
# migration_script.py
import os
import yaml

# Read environment variables
config = {
    'api': {
        'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY'),
        'model': os.getenv('MODEL_NAME', 'claude-3-sonnet-20240229')
    },
    'processing': {
        'chunk_size': int(os.getenv('CHUNK_SIZE', '500')),
        'enable_caching': os.getenv('ENABLE_CACHING', 'true').lower() == 'true'
    }
}

# Write YAML config
with open('config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False)
```

## Troubleshooting Upgrades

### Common Issues

1. **Import Errors After Upgrade**
   ```bash
   # Clear Python cache
   find . -type d -name __pycache__ -exec rm -rf {} +

   # Reinstall package
   pip uninstall customer-snapshot
   pip install customer-snapshot
   ```

2. **Docker Container Fails to Start**
   ```bash
   # Check logs
   docker logs customer-snapshot

   # Verify health check
   docker exec customer-snapshot python /usr/local/bin/healthcheck.py
   ```

3. **Configuration Not Recognized**
   ```bash
   # Validate configuration
   customer-snapshot config validate

   # Check environment variables
   customer-snapshot config-info
   ```

### Getting Help

If you encounter issues:

1. Check the [troubleshooting guide](docs/troubleshooting.md)
2. Search [existing issues](https://github.com/arthurfantaci/customer-solution-snapshot-generator/issues)
3. Create a new issue with:
   - Current version
   - Target version
   - Error messages
   - Steps to reproduce

## Best Practices

### Before Upgrading

1. **Test in Development**
   - Always test upgrades in a development environment first
   - Run your test suite against the new version
   - Verify all integrations work correctly

2. **Review Dependencies**
   - Check for updated Python package requirements
   - Verify model compatibility (spaCy, NLTK)
   - Update Docker base images if needed

3. **Plan Downtime**
   - Schedule upgrades during low-usage periods
   - Prepare rollback plan
   - Notify users of maintenance

### After Upgrading

1. **Verify Functionality**
   ```bash
   # Run health check
   python healthcheck.py

   # Process test file
   customer-snapshot process test.vtt --output test_output.md

   # Check monitoring
   python monitoring_dashboard.py --mode status
   ```

2. **Monitor Performance**
   - Watch error rates
   - Check processing times
   - Monitor resource usage

3. **Update Documentation**
   - Update internal docs with new features
   - Train team on new functionality
   - Update integration guides

---

*For version-specific details, always refer to the [CHANGELOG.md](CHANGELOG.md) and release notes.*
