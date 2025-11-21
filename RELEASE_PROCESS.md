# Production Release Process

This document describes the production release process for the Customer Solution Snapshot Generator.

## Overview

The release process is fully automated using GitHub Actions and Python scripts, ensuring consistent, reliable releases with comprehensive validation at each step.

## Release Types

### Version Numbering

We follow [Semantic Versioning](https://semver.org/) (SemVer):

- **Major Release (v1.0.0)**: Breaking changes, major features
- **Minor Release (v0.1.0)**: New features, backward compatible
- **Patch Release (v0.0.1)**: Bug fixes, minor improvements
- **Hotfix Release (v0.0.1-hotfix)**: Critical fixes for production

### Release Channels

- **Stable**: Production-ready releases (no prerelease tag)
- **Beta**: Pre-release testing (v1.0.0-beta)
- **Hotfix**: Emergency fixes (v1.0.0-hotfix)

## Automated Release Workflow

### 1. Pre-Release Validation

The workflow performs comprehensive validation:

- **Version Validation**: Ensures proper version format
- **Duplicate Check**: Prevents releasing existing versions
- **Changelog Generation**: Automatic release notes from commits

### 2. Quality Assurance

#### Test Suite Execution
- Unit tests across Python 3.8-3.11
- Integration tests
- Security scanning with Bandit
- Code coverage analysis

#### Performance Validation
- Benchmark execution
- Memory usage analysis
- Processing time validation
- Performance regression detection

#### Docker Validation
- Image build verification
- Health check execution
- Security scanning with Trivy
- Multi-architecture support (amd64, arm64)

### 3. Artifact Generation

The workflow builds multiple release artifacts:

- **Python Package**: Wheel and source distribution
- **Docker Images**: Multi-architecture images
- **Source Archive**: Complete source code bundle
- **Documentation**: API and user documentation

### 4. Publishing

#### GitHub Release
- Creates tagged release
- Uploads all artifacts
- Publishes release notes

#### Package Registries
- PyPI publication (if configured)
- Docker Hub publication
- GitHub Container Registry

#### Documentation
- Deploys to GitHub Pages
- Updates version-specific docs
- Updates 'latest' symlink

### 5. Post-Release Validation

Automated verification of:
- Docker image availability
- Documentation accessibility
- Package installation
- Version consistency

## Manual Release Process

### Prerequisites

1. **Environment Setup**:
```bash
pip install semver requests gitpython toml
pip install -r requirements-dev.txt
```

2. **Permissions**:
- GitHub repository write access
- Docker Hub push access (if applicable)
- PyPI upload access (if applicable)

### Using the Release Script

#### 1. Prepare Release

```bash
# Check current version
./release.py patch --dry-run

# Create patch release
./release.py patch

# Create minor release
./release.py minor

# Create major release
./release.py major

# Create hotfix
./release.py hotfix

# Specify exact version
./release.py patch --version v1.2.3
```

#### 2. Review and Merge

The script will:
1. Run all tests
2. Generate changelog
3. Build artifacts
4. Create release branch
5. Push to GitHub

Then:
1. Create PR on GitHub
2. Get approval
3. Merge PR

#### 3. Tag and Release

After PR is merged:

```bash
# Pull latest changes
git checkout main
git pull

# Create and push tag
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3
```

The GitHub Actions workflow will handle the rest automatically.

### Manual GitHub Actions Trigger

You can also trigger releases directly from GitHub:

1. Go to Actions → Production Release
2. Click "Run workflow"
3. Enter version (e.g., v1.2.3)
4. Select release type
5. Click "Run workflow"

## Release Checklist

### Pre-Release

- [ ] All tests passing
- [ ] No security vulnerabilities
- [ ] Performance benchmarks acceptable
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version numbers updated

### During Release

- [ ] Release branch created
- [ ] PR approved and merged
- [ ] Tag created and pushed
- [ ] GitHub Actions workflow running

### Post-Release

- [ ] GitHub Release published
- [ ] Docker images available
- [ ] Documentation deployed
- [ ] Package installable
- [ ] Smoke tests passing

## Rollback Process

If issues are discovered after release:

### 1. Immediate Mitigation

```bash
# Mark release as pre-release on GitHub
# This warns users but keeps artifacts available
```

### 2. Create Hotfix

```bash
# Create hotfix branch
git checkout -b hotfix/v1.2.4 v1.2.3

# Fix issues
# ...

# Create hotfix release
./release.py hotfix --version v1.2.4
```

### 3. Docker Rollback

```bash
# Re-tag previous version as latest
docker pull username/customer-snapshot-generator:v1.2.2
docker tag username/customer-snapshot-generator:v1.2.2 \
  username/customer-snapshot-generator:latest
docker push username/customer-snapshot-generator:latest
```

## CI/CD Pipeline

### GitHub Actions Workflows

1. **release.yml**: Main production release workflow
2. **test.yml**: Continuous testing on all commits
3. **ci-cd.yml**: Development builds and deployments

### Workflow Triggers

- **Tag Push**: Triggers full release (v*)
- **Manual Dispatch**: Allows manual releases
- **PR Merge to Main**: Runs validation only

### Environment Variables

Required secrets in GitHub:
- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub password
- `PYPI_API_TOKEN`: PyPI upload token (optional)

## Monitoring Releases

### Release Health Metrics

Monitor after each release:

1. **Download Statistics**
   - GitHub Release downloads
   - Docker Hub pulls
   - PyPI downloads

2. **Error Rates**
   - Monitor error tracking dashboard
   - Check for new error patterns
   - Watch for increased error rates

3. **Performance Metrics**
   - Processing time trends
   - Memory usage patterns
   - API response times

### Automated Alerts

Set up alerts for:
- Failed deployments
- High error rates post-release
- Performance degradation
- Security vulnerabilities

## Security Considerations

### Code Signing

Future enhancement: Implement GPG signing for:
- Git tags
- Release artifacts
- Docker images

### Vulnerability Scanning

Automated scanning includes:
- Python dependencies (Safety)
- Docker images (Trivy)
- Source code (Bandit)

### Access Control

- Use GitHub environment protection rules
- Require PR approvals for releases
- Limit Docker Hub push access
- Use least-privilege principles

## Troubleshooting

### Common Issues

#### Release Workflow Fails

1. **Version Already Exists**
   - Delete tag if testing
   - Use different version

2. **Tests Failing**
   - Fix tests before release
   - Use `--skip-tests` for emergency

3. **Docker Build Fails**
   - Check Dockerfile syntax
   - Verify base image availability
   - Review build logs

#### Post-Release Issues

1. **Package Not Installable**
   - Check PyPI upload logs
   - Verify package metadata
   - Test in clean environment

2. **Docker Image Not Working**
   - Check multi-arch builds
   - Verify health checks
   - Test with docker run

3. **Documentation Not Updated**
   - Check GitHub Pages settings
   - Verify build artifacts
   - Clear CDN cache

### Debug Commands

```bash
# Check current tags
git tag -l

# Verify package build
python -m build --sdist --wheel

# Test Docker build locally
docker build -t test .
docker run --rm test customer-snapshot --version

# Run specific workflow
gh workflow run release.yml -f version=v1.2.3
```

## Best Practices

### Commit Messages

Follow conventional commits:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Test updates
- `chore:` Maintenance

### Testing

- Run full test suite before release
- Test on multiple Python versions
- Verify Docker image on multiple platforms
- Perform integration tests

### Communication

- Announce major releases
- Document breaking changes
- Update migration guides
- Notify users of deprecations

## Release Schedule

Recommended schedule:
- **Patch releases**: As needed for bug fixes
- **Minor releases**: Monthly or bi-monthly
- **Major releases**: Quarterly or bi-annually
- **Hotfixes**: Within 24 hours of critical issues

## Support

For release-related issues:

1. Check GitHub Actions logs
2. Review release script output
3. Consult troubleshooting section
4. Contact release team

---

*This release process ensures high-quality, consistent releases with minimal manual intervention and maximum reliability.*
