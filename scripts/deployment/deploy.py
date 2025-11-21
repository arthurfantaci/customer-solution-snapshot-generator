#!/usr/bin/env python3
"""
Deployment automation script for Customer Solution Snapshot Generator.

This script provides comprehensive deployment automation for various environments
including local development, staging, and production deployments.
"""

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml


# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DeploymentError(Exception):
    """Custom exception for deployment errors."""

    pass


class EnvironmentConfig:
    """Configuration for deployment environments."""

    def __init__(self, env_name: str, config_data: dict[str, Any]):
        self.name = env_name
        self.config = config_data

    @property
    def docker_image(self) -> str:
        return self.config.get("docker_image", "customer-snapshot-generator")

    @property
    def docker_tag(self) -> str:
        return self.config.get("docker_tag", "latest")

    @property
    def memory_limit(self) -> str:
        return self.config.get("memory_limit", "2g")

    @property
    def cpu_limit(self) -> str:
        return self.config.get("cpu_limit", "2.0")

    @property
    def replicas(self) -> int:
        return self.config.get("replicas", 1)

    @property
    def environment_vars(self) -> dict[str, str]:
        return self.config.get("environment_vars", {})

    @property
    def health_check_path(self) -> str:
        return self.config.get("health_check_path", "/health")

    @property
    def port(self) -> int:
        return self.config.get("port", 8080)


class DeploymentAutomation:
    """Main deployment automation orchestrator."""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent
        self.deployment_config_file = self.project_root / "deployment" / "config.yaml"
        self.docker_compose_template = (
            self.project_root / "deployment" / "docker-compose.template.yml"
        )
        self.k8s_templates_dir = self.project_root / "deployment" / "kubernetes"

        # Create deployment directory structure
        self.setup_deployment_structure()

        # Load deployment configurations
        self.environments = self.load_deployment_config()

    def setup_deployment_structure(self):
        """Create deployment directory structure."""
        directories = [
            self.project_root / "deployment",
            self.project_root / "deployment" / "kubernetes",
            self.project_root / "deployment" / "docker",
            self.project_root / "deployment" / "scripts",
            self.project_root / "deployment" / "terraform",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {directory}")

    def load_deployment_config(self) -> dict[str, EnvironmentConfig]:
        """Load deployment configuration from YAML file."""
        if not self.deployment_config_file.exists():
            self.create_default_deployment_config()

        try:
            with open(self.deployment_config_file) as f:
                config_data = yaml.safe_load(f)

            environments = {}
            for env_name, env_config in config_data.get("environments", {}).items():
                environments[env_name] = EnvironmentConfig(env_name, env_config)

            logger.info(f"Loaded configuration for {len(environments)} environments")
            return environments

        except Exception as e:
            logger.error(f"Failed to load deployment config: {e}")
            raise DeploymentError(f"Invalid deployment configuration: {e}")

    def create_default_deployment_config(self):
        """Create default deployment configuration."""
        default_config = {
            "environments": {
                "development": {
                    "docker_image": "customer-snapshot-generator",
                    "docker_tag": "dev",
                    "memory_limit": "1g",
                    "cpu_limit": "1.0",
                    "replicas": 1,
                    "port": 8080,
                    "environment_vars": {
                        "LOG_LEVEL": "DEBUG",
                        "ENABLE_MEMORY_MONITORING": "true",
                        "DEBUG": "true",
                    },
                },
                "staging": {
                    "docker_image": "customer-snapshot-generator",
                    "docker_tag": "staging",
                    "memory_limit": "2g",
                    "cpu_limit": "2.0",
                    "replicas": 2,
                    "port": 8080,
                    "environment_vars": {
                        "LOG_LEVEL": "INFO",
                        "ENABLE_MEMORY_MONITORING": "true",
                        "DEBUG": "false",
                    },
                },
                "production": {
                    "docker_image": "customer-snapshot-generator",
                    "docker_tag": "latest",
                    "memory_limit": "4g",
                    "cpu_limit": "4.0",
                    "replicas": 3,
                    "port": 8080,
                    "environment_vars": {
                        "LOG_LEVEL": "INFO",
                        "ENABLE_MEMORY_MONITORING": "true",
                        "DEBUG": "false",
                    },
                },
            }
        }

        with open(self.deployment_config_file, "w") as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)

        logger.info(f"Created default deployment config: {self.deployment_config_file}")

    def build_docker_image(self, tag: str = "latest", push: bool = False) -> str:
        """Build Docker image for the application."""
        logger.info(f"Building Docker image with tag: {tag}")

        # Check if Dockerfile exists
        dockerfile_path = self.project_root / "Dockerfile"
        if not dockerfile_path.exists():
            raise DeploymentError("Dockerfile not found in project root")

        # Build image
        image_name = f"customer-snapshot-generator:{tag}"
        build_cmd = [
            "docker",
            "build",
            "-t",
            image_name,
            "--build-arg",
            f"BUILD_DATE={datetime.now().isoformat()}",
            "--build-arg",
            f"VCS_REF={self.get_git_commit()}",
            str(self.project_root),
        ]

        try:
            subprocess.run(build_cmd, check=True, capture_output=True, text=True)
            logger.info("Docker image built successfully")

            # Push to registry if requested
            if push:
                self.push_docker_image(image_name)

            return image_name

        except subprocess.CalledProcessError as e:
            logger.error(f"Docker build failed: {e.stderr}")
            raise DeploymentError(f"Docker build failed: {e}")

    def push_docker_image(self, image_name: str):
        """Push Docker image to registry."""
        logger.info(f"Pushing Docker image: {image_name}")

        try:
            subprocess.run(["docker", "push", image_name], check=True)
            logger.info("Docker image pushed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Docker push failed: {e}")
            raise DeploymentError(f"Docker push failed: {e}")

    def get_git_commit(self) -> str:
        """Get current git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            return result.stdout.strip()[:8]
        except subprocess.CalledProcessError:
            return "unknown"

    def create_docker_compose_file(self, environment: str) -> Path:
        """Create Docker Compose file for specified environment."""
        if environment not in self.environments:
            raise DeploymentError(f"Unknown environment: {environment}")

        env_config = self.environments[environment]

        # Docker Compose configuration
        compose_config = {
            "version": "3.8",
            "services": {
                "customer-snapshot-generator": {
                    "image": f"{env_config.docker_image}:{env_config.docker_tag}",
                    "container_name": f"customer-snapshot-{environment}",
                    "ports": [f"{env_config.port}:8080"],
                    "environment": env_config.environment_vars,
                    "deploy": {
                        "resources": {
                            "limits": {
                                "memory": env_config.memory_limit,
                                "cpus": env_config.cpu_limit,
                            }
                        }
                    },
                    "healthcheck": {
                        "test": ["CMD", "python", "/usr/local/bin/healthcheck.py"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3,
                        "start_period": "30s",
                    },
                    "restart": "unless-stopped",
                    "volumes": ["./data:/app/data", "./logs:/app/logs"],
                }
            },
            "volumes": {"app_data": None, "app_logs": None},
        }

        # Write Docker Compose file
        compose_file = (
            self.project_root
            / "deployment"
            / "docker"
            / f"docker-compose.{environment}.yml"
        )
        with open(compose_file, "w") as f:
            yaml.dump(compose_config, f, default_flow_style=False, indent=2)

        logger.info(f"Created Docker Compose file: {compose_file}")
        return compose_file

    def create_kubernetes_manifests(self, environment: str) -> list[Path]:
        """Create Kubernetes manifests for specified environment."""
        if environment not in self.environments:
            raise DeploymentError(f"Unknown environment: {environment}")

        env_config = self.environments[environment]
        manifests = []

        # Deployment manifest
        deployment_manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"customer-snapshot-generator-{environment}",
                "labels": {
                    "app": "customer-snapshot-generator",
                    "environment": environment,
                },
            },
            "spec": {
                "replicas": env_config.replicas,
                "selector": {
                    "matchLabels": {
                        "app": "customer-snapshot-generator",
                        "environment": environment,
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "customer-snapshot-generator",
                            "environment": environment,
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "customer-snapshot-generator",
                                "image": f"{env_config.docker_image}:{env_config.docker_tag}",
                                "ports": [{"containerPort": 8080}],
                                "env": [
                                    {"name": k, "value": v}
                                    for k, v in env_config.environment_vars.items()
                                ],
                                "resources": {
                                    "limits": {
                                        "memory": env_config.memory_limit,
                                        "cpu": env_config.cpu_limit,
                                    },
                                    "requests": {"memory": "512Mi", "cpu": "0.5"},
                                },
                                "livenessProbe": {
                                    "exec": {
                                        "command": [
                                            "python",
                                            "/usr/local/bin/healthcheck.py",
                                        ]
                                    },
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 30,
                                },
                                "readinessProbe": {
                                    "exec": {
                                        "command": [
                                            "python",
                                            "/usr/local/bin/healthcheck.py",
                                        ]
                                    },
                                    "initialDelaySeconds": 10,
                                    "periodSeconds": 10,
                                },
                            }
                        ]
                    },
                },
            },
        }

        deployment_file = self.k8s_templates_dir / f"deployment-{environment}.yaml"
        with open(deployment_file, "w") as f:
            yaml.dump(deployment_manifest, f, default_flow_style=False, indent=2)
        manifests.append(deployment_file)

        # Service manifest
        service_manifest = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"customer-snapshot-generator-service-{environment}",
                "labels": {
                    "app": "customer-snapshot-generator",
                    "environment": environment,
                },
            },
            "spec": {
                "selector": {
                    "app": "customer-snapshot-generator",
                    "environment": environment,
                },
                "ports": [{"protocol": "TCP", "port": 80, "targetPort": 8080}],
                "type": "ClusterIP",
            },
        }

        service_file = self.k8s_templates_dir / f"service-{environment}.yaml"
        with open(service_file, "w") as f:
            yaml.dump(service_manifest, f, default_flow_style=False, indent=2)
        manifests.append(service_file)

        # ConfigMap for environment variables
        configmap_manifest = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"customer-snapshot-generator-config-{environment}",
                "labels": {
                    "app": "customer-snapshot-generator",
                    "environment": environment,
                },
            },
            "data": env_config.environment_vars,
        }

        configmap_file = self.k8s_templates_dir / f"configmap-{environment}.yaml"
        with open(configmap_file, "w") as f:
            yaml.dump(configmap_manifest, f, default_flow_style=False, indent=2)
        manifests.append(configmap_file)

        logger.info(f"Created {len(manifests)} Kubernetes manifests for {environment}")
        return manifests

    def deploy_docker_compose(self, environment: str, build: bool = True):
        """Deploy using Docker Compose."""
        logger.info(f"Deploying to {environment} using Docker Compose")

        # Build image if requested
        if build:
            env_config = self.environments[environment]
            self.build_docker_image(env_config.docker_tag)

        # Create Docker Compose file
        compose_file = self.create_docker_compose_file(environment)

        # Deploy using Docker Compose
        try:
            subprocess.run(
                ["docker-compose", "-f", str(compose_file), "up", "-d"],
                check=True,
                cwd=self.project_root,
            )

            logger.info(f"Successfully deployed {environment} environment")

        except subprocess.CalledProcessError as e:
            logger.error(f"Docker Compose deployment failed: {e}")
            raise DeploymentError(f"Deployment failed: {e}")

    def deploy_kubernetes(self, environment: str, namespace: str = "default"):
        """Deploy to Kubernetes cluster."""
        logger.info(
            f"Deploying to {environment} on Kubernetes (namespace: {namespace})"
        )

        # Create Kubernetes manifests
        manifests = self.create_kubernetes_manifests(environment)

        # Apply manifests
        try:
            for manifest in manifests:
                subprocess.run(
                    ["kubectl", "apply", "-f", str(manifest), "-n", namespace],
                    check=True,
                )

            logger.info(f"Successfully deployed {environment} to Kubernetes")

        except subprocess.CalledProcessError as e:
            logger.error(f"Kubernetes deployment failed: {e}")
            raise DeploymentError(f"Kubernetes deployment failed: {e}")

    def rollback_deployment(
        self, environment: str, deployment_type: str = "docker-compose"
    ):
        """Rollback deployment to previous version."""
        logger.info(f"Rolling back {environment} deployment ({deployment_type})")

        if deployment_type == "docker-compose":
            compose_file = (
                self.project_root
                / "deployment"
                / "docker"
                / f"docker-compose.{environment}.yml"
            )
            try:
                subprocess.run(
                    ["docker-compose", "-f", str(compose_file), "down"], check=True
                )
                logger.info("Rollback completed")
            except subprocess.CalledProcessError as e:
                raise DeploymentError(f"Rollback failed: {e}")

        elif deployment_type == "kubernetes":
            try:
                subprocess.run(
                    [
                        "kubectl",
                        "rollout",
                        "undo",
                        f"deployment/customer-snapshot-generator-{environment}",
                    ],
                    check=True,
                )
                logger.info("Kubernetes rollback completed")
            except subprocess.CalledProcessError as e:
                raise DeploymentError(f"Kubernetes rollback failed: {e}")

    def health_check(self, environment: str, timeout: int = 60) -> bool:
        """Perform health check on deployed application."""
        env_config = self.environments[environment]

        # For Docker Compose deployments
        try:
            import time

            import requests

            url = f"http://localhost:{env_config.port}/health"
            start_time = time.time()

            while time.time() - start_time < timeout:
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        logger.info("Health check passed")
                        return True
                except requests.RequestException:
                    pass

                time.sleep(5)

            logger.error("Health check failed - timeout")
            return False

        except ImportError:
            logger.warning("requests library not available, skipping HTTP health check")

            # Fallback to container status check
            try:
                result = subprocess.run(
                    [
                        "docker",
                        "ps",
                        "--filter",
                        f"name=customer-snapshot-{environment}",
                        "--format",
                        "{{.Status}}",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                status = result.stdout.strip()
                is_healthy = "Up" in status
                logger.info(
                    f"Container status check: {status} ({'healthy' if is_healthy else 'unhealthy'})"
                )
                return is_healthy

            except subprocess.CalledProcessError:
                logger.error("Container status check failed")
                return False

    def get_deployment_status(self, environment: str) -> dict[str, Any]:
        """Get current deployment status."""
        status = {
            "environment": environment,
            "timestamp": datetime.now().isoformat(),
            "containers": [],
            "services": [],
            "health": "unknown",
        }

        # Check Docker containers
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    f"name=customer-snapshot-{environment}",
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            if result.stdout.strip():
                container_info = json.loads(result.stdout)
                status["containers"].append(container_info)

        except (subprocess.CalledProcessError, json.JSONDecodeError):
            pass

        # Perform health check
        status["health"] = (
            "healthy" if self.health_check(environment, timeout=10) else "unhealthy"
        )

        return status


def main():
    """Main deployment script entry point."""
    parser = argparse.ArgumentParser(
        description="Customer Solution Snapshot Generator Deployment"
    )
    parser.add_argument(
        "command",
        choices=["build", "deploy", "rollback", "status", "health"],
        help="Deployment command",
    )
    parser.add_argument(
        "--environment",
        "-e",
        default="development",
        help="Target environment (development, staging, production)",
    )
    parser.add_argument(
        "--type",
        "-t",
        choices=["docker-compose", "kubernetes"],
        default="docker-compose",
        help="Deployment type",
    )
    parser.add_argument(
        "--build", action="store_true", help="Build image before deployment"
    )
    parser.add_argument("--push", action="store_true", help="Push image to registry")
    parser.add_argument(
        "--namespace", "-n", default="default", help="Kubernetes namespace"
    )
    parser.add_argument("--tag", default="latest", help="Docker image tag")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        deployment = DeploymentAutomation()

        if args.command == "build":
            image_name = deployment.build_docker_image(args.tag, args.push)
            print(f"✅ Built image: {image_name}")

        elif args.command == "deploy":
            if args.type == "docker-compose":
                deployment.deploy_docker_compose(args.environment, args.build)
            elif args.type == "kubernetes":
                deployment.deploy_kubernetes(args.environment, args.namespace)
            print(f"✅ Deployed {args.environment} using {args.type}")

        elif args.command == "rollback":
            deployment.rollback_deployment(args.environment, args.type)
            print(f"✅ Rolled back {args.environment} deployment")

        elif args.command == "status":
            status = deployment.get_deployment_status(args.environment)
            print(json.dumps(status, indent=2))

        elif args.command == "health":
            is_healthy = deployment.health_check(args.environment)
            print(f"Health check: {'✅ HEALTHY' if is_healthy else '❌ UNHEALTHY'}")
            sys.exit(0 if is_healthy else 1)

    except DeploymentError as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
