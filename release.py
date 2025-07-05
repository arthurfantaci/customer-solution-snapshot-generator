#!/usr/bin/env python3
"""
Production release automation script for Customer Solution Snapshot Generator.

This script handles the complete release process including version bumping,
changelog generation, testing, building, and publishing.
"""

import os
import sys
import json
import subprocess
import argparse
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re

try:
    import semver
    import requests
    from git import Repo
    import toml
except ImportError:
    print("Error: Required dependencies not installed.")
    print("Please install: pip install semver requests gitpython toml")
    sys.exit(1)


class ReleaseManager:
    """Manages the complete release process."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.repo = Repo(self.repo_path)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load release configuration."""
        config_file = self.repo_path / "pyproject.toml"
        if config_file.exists():
            with open(config_file) as f:
                data = toml.load(f)
                return data.get("tool", {}).get("release", {})
        return {}
    
    def get_current_version(self) -> str:
        """Get current version from git tags."""
        try:
            # Get all version tags
            tags = [tag.name for tag in self.repo.tags if tag.name.startswith('v')]
            if not tags:
                return "v0.0.0"
            
            # Sort by semver and return latest
            tags.sort(key=lambda x: semver.VersionInfo.parse(x[1:]))
            return tags[-1]
        except Exception as e:
            print(f"Warning: Could not determine current version: {e}")
            return "v0.0.0"
    
    def bump_version(self, current: str, bump_type: str) -> str:
        """Bump version based on type."""
        # Remove 'v' prefix
        version = semver.VersionInfo.parse(current[1:] if current.startswith('v') else current)
        
        if bump_type == "major":
            version = version.bump_major()
        elif bump_type == "minor":
            version = version.bump_minor()
        elif bump_type == "patch":
            version = version.bump_patch()
        elif bump_type == "hotfix":
            # For hotfix, bump patch and add prerelease
            version = version.bump_patch()
            version = version.replace(prerelease="hotfix")
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")
        
        return f"v{version}"
    
    def generate_changelog(self, from_tag: Optional[str] = None, to_tag: str = "HEAD") -> str:
        """Generate changelog between tags."""
        if from_tag is None:
            # Get previous tag
            tags = [tag.name for tag in self.repo.tags if tag.name.startswith('v')]
            if tags:
                tags.sort(key=lambda x: semver.VersionInfo.parse(x[1:]))
                from_tag = tags[-1] if len(tags) > 0 else None
        
        # Get commits
        if from_tag:
            commits = list(self.repo.iter_commits(f"{from_tag}..{to_tag}"))
        else:
            commits = list(self.repo.iter_commits(to_tag))
        
        # Categorize commits
        features = []
        fixes = []
        docs = []
        refactors = []
        tests = []
        others = []
        
        for commit in commits:
            message = commit.message.strip()
            if message.startswith("feat:") or message.startswith("feature:"):
                features.append(message)
            elif message.startswith("fix:") or message.startswith("bugfix:"):
                fixes.append(message)
            elif message.startswith("docs:"):
                docs.append(message)
            elif message.startswith("refactor:"):
                refactors.append(message)
            elif message.startswith("test:"):
                tests.append(message)
            else:
                others.append(message)
        
        # Build changelog
        changelog = []
        
        if features:
            changelog.append("### 🚀 Features")
            for feat in features:
                changelog.append(f"- {feat}")
            changelog.append("")
        
        if fixes:
            changelog.append("### 🐛 Bug Fixes")
            for fix in fixes:
                changelog.append(f"- {fix}")
            changelog.append("")
        
        if refactors:
            changelog.append("### ♻️ Refactoring")
            for ref in refactors:
                changelog.append(f"- {ref}")
            changelog.append("")
        
        if docs:
            changelog.append("### 📚 Documentation")
            for doc in docs:
                changelog.append(f"- {doc}")
            changelog.append("")
        
        if tests:
            changelog.append("### 🧪 Tests")
            for test in tests:
                changelog.append(f"- {test}")
            changelog.append("")
        
        if others and len(others) <= 10:  # Only show if not too many
            changelog.append("### 🔧 Other Changes")
            for other in others:
                changelog.append(f"- {other}")
            changelog.append("")
        
        # Add contributors
        contributors = set()
        for commit in commits:
            contributors.add(commit.author.name)
        
        if contributors:
            changelog.append("### 👥 Contributors")
            for contributor in sorted(contributors):
                changelog.append(f"- @{contributor}")
        
        return "\n".join(changelog)
    
    def run_tests(self) -> bool:
        """Run all tests."""
        print("🧪 Running tests...")
        
        try:
            # Run unit tests
            result = subprocess.run(
                ["pytest", "tests/", "--cov=src/customer_snapshot", "--cov-report=term"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("❌ Unit tests failed:")
                print(result.stdout)
                print(result.stderr)
                return False
            
            print("✅ Unit tests passed")
            
            # Run integration tests
            print("🧪 Running integration tests...")
            result = subprocess.run(
                ["python", "test_error_system_standalone.py"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("❌ Integration tests failed:")
                print(result.stdout)
                return False
            
            print("✅ Integration tests passed")
            
            # Run security scan
            print("🔒 Running security scan...")
            result = subprocess.run(
                ["bandit", "-r", "src/", "-f", "json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode not in [0, 1]:  # bandit returns 1 if issues found
                print("❌ Security scan failed")
                return False
            
            # Parse bandit results
            try:
                bandit_results = json.loads(result.stdout)
                high_issues = [i for i in bandit_results.get("results", []) 
                             if i.get("issue_severity") == "HIGH"]
                
                if high_issues:
                    print(f"⚠️  Found {len(high_issues)} high severity security issues")
                    for issue in high_issues[:3]:  # Show first 3
                        print(f"  - {issue['issue_text']} at {issue['filename']}:{issue['line_number']}")
                else:
                    print("✅ No high severity security issues found")
            except:
                print("⚠️  Could not parse security scan results")
            
            return True
            
        except FileNotFoundError as e:
            print(f"❌ Test command not found: {e}")
            return False
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return False
    
    def run_benchmarks(self) -> bool:
        """Run performance benchmarks."""
        print("📊 Running performance benchmarks...")
        
        try:
            result = subprocess.run(
                ["python", "benchmark.py", "--output", "benchmark-results.json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("❌ Benchmarks failed")
                return False
            
            # Check benchmark results
            with open("benchmark-results.json") as f:
                results = json.load(f)
            
            # Validate performance
            small_file_time = results.get("small_file", {}).get("processing_time", float('inf'))
            medium_file_memory = results.get("medium_file", {}).get("memory_peak_mb", float('inf'))
            
            if small_file_time > 5.0:
                print(f"⚠️  Small file processing slow: {small_file_time:.2f}s (threshold: 5.0s)")
            else:
                print(f"✅ Small file processing: {small_file_time:.2f}s")
            
            if medium_file_memory > 500:
                print(f"⚠️  High memory usage: {medium_file_memory:.1f}MB (threshold: 500MB)")
            else:
                print(f"✅ Memory usage: {medium_file_memory:.1f}MB")
            
            return True
            
        except Exception as e:
            print(f"❌ Benchmark execution failed: {e}")
            return False
    
    def build_artifacts(self, version: str) -> List[Path]:
        """Build release artifacts."""
        print("📦 Building release artifacts...")
        artifacts = []
        
        try:
            # Clean previous builds
            for dir in ["dist", "build"]:
                if Path(dir).exists():
                    shutil.rmtree(dir)
            
            # Update version in pyproject.toml
            self._update_version_file(version)
            
            # Build Python package
            result = subprocess.run(
                ["python", "-m", "build"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("❌ Package build failed")
                print(result.stderr)
                return []
            
            # Collect wheel and sdist
            for file in Path("dist").glob("*"):
                artifacts.append(file)
                print(f"✅ Built: {file.name}")
            
            # Create source archive
            archive_name = f"customer-snapshot-generator-{version}.tar.gz"
            subprocess.run([
                "tar", "-czf", archive_name,
                "--exclude=.git",
                "--exclude=__pycache__",
                "--exclude=*.pyc",
                "--exclude=.pytest_cache",
                "--exclude=htmlcov",
                "--exclude=dist",
                "--exclude=build",
                "--exclude=*.egg-info",
                "."
            ])
            
            artifacts.append(Path(archive_name))
            print(f"✅ Created source archive: {archive_name}")
            
            return artifacts
            
        except Exception as e:
            print(f"❌ Build failed: {e}")
            return []
    
    def _update_version_file(self, version: str):
        """Update version in pyproject.toml."""
        config_file = self.repo_path / "pyproject.toml"
        if config_file.exists():
            with open(config_file) as f:
                data = toml.load(f)
            
            # Update version (remove 'v' prefix)
            clean_version = version[1:] if version.startswith('v') else version
            data["project"]["version"] = clean_version
            
            with open(config_file, 'w') as f:
                toml.dump(data, f)
    
    def validate_docker_build(self) -> bool:
        """Validate Docker image can be built."""
        print("🐳 Validating Docker build...")
        
        try:
            # Build test image
            result = subprocess.run(
                ["docker", "build", "-t", "customer-snapshot:test", "."],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("❌ Docker build failed")
                print(result.stderr)
                return False
            
            print("✅ Docker image built successfully")
            
            # Test image
            result = subprocess.run(
                ["docker", "run", "--rm", "customer-snapshot:test", 
                 "python", "/usr/local/bin/healthcheck.py"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("❌ Docker health check failed")
                return False
            
            print("✅ Docker health check passed")
            
            # Clean up
            subprocess.run(["docker", "rmi", "customer-snapshot:test"], 
                         capture_output=True)
            
            return True
            
        except FileNotFoundError:
            print("⚠️  Docker not found, skipping Docker validation")
            return True
        except Exception as e:
            print(f"❌ Docker validation failed: {e}")
            return False
    
    def create_release_pr(self, version: str, changelog: str) -> Optional[str]:
        """Create a pull request for the release."""
        print("📝 Creating release pull request...")
        
        try:
            # Create release branch
            branch_name = f"release/{version}"
            self.repo.create_head(branch_name)
            self.repo.heads[branch_name].checkout()
            
            # Update CHANGELOG.md
            changelog_file = self.repo_path / "CHANGELOG.md"
            existing_content = ""
            if changelog_file.exists():
                with open(changelog_file) as f:
                    existing_content = f.read()
            
            # Add new release to changelog
            new_content = f"""# Changelog

## [{version}] - {datetime.now().strftime('%Y-%m-%d')}

{changelog}

{existing_content.replace('# Changelog', '').strip()}
"""
            
            with open(changelog_file, 'w') as f:
                f.write(new_content)
            
            # Update version file
            self._update_version_file(version)
            
            # Commit changes
            self.repo.index.add(["CHANGELOG.md", "pyproject.toml"])
            self.repo.index.commit(f"chore: prepare release {version}")
            
            # Push branch
            origin = self.repo.remote("origin")
            origin.push(branch_name)
            
            print(f"✅ Created release branch: {branch_name}")
            print("📌 Please create a pull request manually on GitHub")
            
            return branch_name
            
        except Exception as e:
            print(f"❌ Failed to create release PR: {e}")
            return None
    
    def perform_release(self, version: str, bump_type: str, 
                       skip_tests: bool = False,
                       skip_pr: bool = False) -> bool:
        """Perform complete release process."""
        print(f"🚀 Starting release process for {version}")
        print("=" * 60)
        
        # Check for uncommitted changes
        if self.repo.is_dirty():
            print("❌ Repository has uncommitted changes")
            print("Please commit or stash changes before releasing")
            return False
        
        # Ensure on main branch
        if self.repo.active_branch.name != "main":
            print(f"⚠️  Not on main branch (current: {self.repo.active_branch.name})")
            response = input("Switch to main branch? (y/n): ")
            if response.lower() == 'y':
                self.repo.heads.main.checkout()
            else:
                return False
        
        # Pull latest changes
        print("📥 Pulling latest changes...")
        origin = self.repo.remote("origin")
        origin.pull()
        
        # Generate changelog
        print("📝 Generating changelog...")
        current_version = self.get_current_version()
        changelog = self.generate_changelog(from_tag=current_version)
        
        print("\n--- CHANGELOG ---")
        print(changelog)
        print("-" * 40)
        
        # Run tests
        if not skip_tests:
            if not self.run_tests():
                print("❌ Tests failed. Aborting release.")
                return False
            
            if not self.run_benchmarks():
                print("⚠️  Benchmarks completed with warnings")
        
        # Validate Docker build
        if not self.validate_docker_build():
            print("⚠️  Docker validation completed with warnings")
        
        # Build artifacts
        artifacts = self.build_artifacts(version)
        if not artifacts:
            print("❌ Failed to build artifacts")
            return False
        
        print(f"\n✅ Built {len(artifacts)} artifacts")
        
        # Create release PR
        if not skip_pr:
            branch = self.create_release_pr(version, changelog)
            if branch:
                print(f"\n✅ Release preparation complete!")
                print(f"Next steps:")
                print(f"1. Create PR from '{branch}' to 'main' on GitHub")
                print(f"2. Get PR reviewed and approved")
                print(f"3. Merge PR")
                print(f"4. Run: git checkout main && git pull")
                print(f"5. Run: git tag -a {version} -m 'Release {version}'")
                print(f"6. Run: git push origin {version}")
                print(f"7. GitHub Actions will handle the rest!")
        else:
            print(f"\n✅ Release preparation complete!")
            print(f"Next steps:")
            print(f"1. Review changes")
            print(f"2. Run: git tag -a {version} -m 'Release {version}'")
            print(f"3. Run: git push origin {version}")
            print(f"4. GitHub Actions will handle the rest!")
        
        return True


def main():
    """Main release script."""
    parser = argparse.ArgumentParser(
        description="Production release automation for Customer Solution Snapshot Generator"
    )
    parser.add_argument(
        "bump_type",
        choices=["major", "minor", "patch", "hotfix"],
        help="Type of version bump"
    )
    parser.add_argument(
        "--version",
        help="Explicit version (overrides bump type)"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running tests"
    )
    parser.add_argument(
        "--skip-pr",
        action="store_true", 
        help="Skip creating pull request"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without doing it"
    )
    
    args = parser.parse_args()
    
    # Initialize release manager
    try:
        manager = ReleaseManager()
    except Exception as e:
        print(f"❌ Failed to initialize release manager: {e}")
        return 1
    
    # Determine version
    current_version = manager.get_current_version()
    print(f"Current version: {current_version}")
    
    if args.version:
        new_version = args.version
        if not new_version.startswith('v'):
            new_version = f'v{new_version}'
    else:
        new_version = manager.bump_version(current_version, args.bump_type)
    
    print(f"New version: {new_version}")
    
    if args.dry_run:
        print("\n🔍 DRY RUN - No changes will be made")
        print(f"Would bump version from {current_version} to {new_version}")
        changelog = manager.generate_changelog(from_tag=current_version)
        print("\nChangelog preview:")
        print(changelog)
        return 0
    
    # Confirm release
    print(f"\n⚠️  About to release version {new_version}")
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("❌ Release cancelled")
        return 1
    
    # Perform release
    success = manager.perform_release(
        new_version, 
        args.bump_type,
        skip_tests=args.skip_tests,
        skip_pr=args.skip_pr
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())