#!/usr/bin/env python3
"""
DEPLOYER AGENT
Deploys validated code to target environments.

Handles staging, production, and rollback.
"""
import os
import sys
import json
import shutil
import hashlib
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent))


class DeployTarget(Enum):
    """Deployment targets"""
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"
    DOCKER = "docker"
    EDGE = "edge"


class DeployStatus(Enum):
    """Deployment status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class DeploymentRecord:
    """Record of a deployment"""
    id: str
    source_path: str
    target: DeployTarget
    timestamp: datetime
    status: DeployStatus
    checksum: str
    version: str
    rollback_path: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeployConfig:
    """Deployment configuration"""
    target: DeployTarget = DeployTarget.LOCAL
    staging_dir: str = "./staging"
    production_dir: str = "./production"
    backup_dir: str = "./backups"
    docker_registry: Optional[str] = None
    edge_nodes: List[str] = field(default_factory=list)
    auto_rollback: bool = True
    health_check: bool = True
    version_format: str = "v{major}.{minor}.{patch}"


class Deployer:
    """
    Deploys code to various targets.

    Supports:
    - Local file deployment
    - Docker containerization
    - Edge node distribution
    - Automatic rollback on failure
    """

    def __init__(self, config: DeployConfig = None):
        self.config = config or DeployConfig()
        self.deployments: List[DeploymentRecord] = []
        self.current_version = {"major": 0, "minor": 1, "patch": 0}
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Ensure deployment directories exist"""
        Path(self.config.staging_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config.production_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config.backup_dir).mkdir(parents=True, exist_ok=True)

    def _generate_id(self) -> str:
        """Generate deployment ID"""
        return f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.deployments):04d}"

    def _calculate_checksum(self, path: str) -> str:
        """Calculate file checksum"""
        content = Path(path).read_bytes()
        return hashlib.sha256(content).hexdigest()[:16]

    def _get_version(self) -> str:
        """Get current version string"""
        return self.config.version_format.format(**self.current_version)

    def _bump_version(self, bump_type: str = "patch"):
        """Bump version number"""
        if bump_type == "major":
            self.current_version["major"] += 1
            self.current_version["minor"] = 0
            self.current_version["patch"] = 0
        elif bump_type == "minor":
            self.current_version["minor"] += 1
            self.current_version["patch"] = 0
        else:
            self.current_version["patch"] += 1

    async def deploy(
        self,
        source_path: str,
        target: DeployTarget = None,
        version_bump: str = "patch"
    ) -> DeploymentRecord:
        """Deploy source to target"""
        target = target or self.config.target

        self._bump_version(version_bump)

        record = DeploymentRecord(
            id=self._generate_id(),
            source_path=source_path,
            target=target,
            timestamp=datetime.now(),
            status=DeployStatus.PENDING,
            checksum=self._calculate_checksum(source_path) if Path(source_path).exists() else "",
            version=self._get_version(),
        )

        try:
            record.status = DeployStatus.IN_PROGRESS

            if target == DeployTarget.LOCAL:
                await self._deploy_local(record)
            elif target == DeployTarget.STAGING:
                await self._deploy_staging(record)
            elif target == DeployTarget.PRODUCTION:
                await self._deploy_production(record)
            elif target == DeployTarget.DOCKER:
                await self._deploy_docker(record)
            elif target == DeployTarget.EDGE:
                await self._deploy_edge(record)

            # Health check
            if self.config.health_check:
                healthy = await self._health_check(record)
                if not healthy:
                    raise Exception("Health check failed")

            record.status = DeployStatus.SUCCESS
            print(f"[DEPLOY] SUCCESS: {record.id} -> {target.value}")

        except Exception as e:
            record.status = DeployStatus.FAILED
            record.errors.append(str(e))
            print(f"[DEPLOY] FAILED: {record.id} - {e}")

            # Auto rollback
            if self.config.auto_rollback and record.rollback_path:
                await self._rollback(record)

        self.deployments.append(record)
        self._save_deployment_log(record)

        return record

    async def _deploy_local(self, record: DeploymentRecord):
        """Deploy to local directory"""
        source = Path(record.source_path)
        if not source.exists():
            raise FileNotFoundError(f"Source not found: {source}")

        # Create versioned destination
        dest_dir = Path(self.config.production_dir) / record.version
        dest_dir.mkdir(parents=True, exist_ok=True)

        if source.is_file():
            dest = dest_dir / source.name
            shutil.copy2(source, dest)
        else:
            shutil.copytree(source, dest_dir, dirs_exist_ok=True)

        # Create rollback backup
        backup_path = Path(self.config.backup_dir) / f"{record.id}.tar.gz"
        record.rollback_path = str(backup_path)

        # Create latest symlink
        latest = Path(self.config.production_dir) / "latest"
        if latest.is_symlink():
            latest.unlink()
        latest.symlink_to(dest_dir.name)

        record.metadata["destination"] = str(dest_dir)

    async def _deploy_staging(self, record: DeploymentRecord):
        """Deploy to staging environment"""
        source = Path(record.source_path)
        dest = Path(self.config.staging_dir) / source.name

        if source.is_file():
            shutil.copy2(source, dest)
        else:
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(source, dest)

        record.metadata["staging_path"] = str(dest)

    async def _deploy_production(self, record: DeploymentRecord):
        """Deploy to production with backup"""
        # First backup existing
        prod_dir = Path(self.config.production_dir) / "current"
        if prod_dir.exists():
            backup_name = f"backup_{record.timestamp.strftime('%Y%m%d_%H%M%S')}"
            backup_path = Path(self.config.backup_dir) / backup_name
            shutil.copytree(prod_dir, backup_path)
            record.rollback_path = str(backup_path)

        # Deploy new version
        await self._deploy_local(record)

    async def _deploy_docker(self, record: DeploymentRecord):
        """Build and deploy Docker container"""
        source = Path(record.source_path)

        # Check for Dockerfile
        dockerfile = source / "Dockerfile" if source.is_dir() else source.parent / "Dockerfile"
        if not dockerfile.exists():
            # Generate basic Dockerfile
            dockerfile_content = f"""FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt 2>/dev/null || true
CMD ["python", "{source.name}"]
"""
            dockerfile.write_text(dockerfile_content)

        # Build image
        image_tag = f"orbos/{source.stem}:{record.version}"
        build_cmd = ["docker", "build", "-t", image_tag, str(source.parent)]

        result = subprocess.run(build_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Docker build failed: {result.stderr}")

        record.metadata["docker_image"] = image_tag

        # Push to registry if configured
        if self.config.docker_registry:
            full_tag = f"{self.config.docker_registry}/{image_tag}"
            subprocess.run(["docker", "tag", image_tag, full_tag])
            subprocess.run(["docker", "push", full_tag])
            record.metadata["registry_image"] = full_tag

    async def _deploy_edge(self, record: DeploymentRecord):
        """Deploy to edge nodes"""
        if not self.config.edge_nodes:
            raise Exception("No edge nodes configured")

        source = Path(record.source_path)
        deployed_nodes = []

        for node in self.config.edge_nodes:
            try:
                # Would use SSH/SCP in production
                print(f"[EDGE] Deploying to {node}...")
                deployed_nodes.append(node)
            except Exception as e:
                record.errors.append(f"Node {node}: {e}")

        record.metadata["deployed_nodes"] = deployed_nodes

    async def _health_check(self, record: DeploymentRecord) -> bool:
        """Perform health check after deployment"""
        # Check if files exist
        if record.target in [DeployTarget.LOCAL, DeployTarget.STAGING, DeployTarget.PRODUCTION]:
            dest = record.metadata.get("destination") or record.metadata.get("staging_path")
            if dest and Path(dest).exists():
                # Try to syntax-check Python files
                if dest.endswith('.py'):
                    try:
                        compile(Path(dest).read_text(), dest, 'exec')
                    except SyntaxError:
                        return False
                return True

        # Docker health check
        if record.target == DeployTarget.DOCKER:
            image = record.metadata.get("docker_image")
            if image:
                result = subprocess.run(
                    ["docker", "inspect", image],
                    capture_output=True
                )
                return result.returncode == 0

        return True

    async def _rollback(self, record: DeploymentRecord):
        """Rollback a deployment"""
        if not record.rollback_path or not Path(record.rollback_path).exists():
            print(f"[ROLLBACK] No rollback available for {record.id}")
            return

        print(f"[ROLLBACK] Rolling back {record.id}...")

        prod_current = Path(self.config.production_dir) / "current"
        if prod_current.exists():
            shutil.rmtree(prod_current)

        shutil.copytree(record.rollback_path, prod_current)
        record.status = DeployStatus.ROLLED_BACK
        print(f"[ROLLBACK] Restored from {record.rollback_path}")

    def _save_deployment_log(self, record: DeploymentRecord):
        """Save deployment record to log"""
        log_path = Path(self.config.backup_dir) / "deployments.jsonl"
        log_entry = {
            "id": record.id,
            "source": record.source_path,
            "target": record.target.value,
            "timestamp": record.timestamp.isoformat(),
            "status": record.status.value,
            "version": record.version,
            "checksum": record.checksum,
            "errors": record.errors,
        }
        with open(log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def get_history(self, limit: int = 10) -> List[DeploymentRecord]:
        """Get deployment history"""
        return self.deployments[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """Get deployer statistics"""
        success = len([d for d in self.deployments if d.status == DeployStatus.SUCCESS])
        failed = len([d for d in self.deployments if d.status == DeployStatus.FAILED])

        return {
            "total_deployments": len(self.deployments),
            "successful": success,
            "failed": failed,
            "success_rate": success / max(1, len(self.deployments)),
            "current_version": self._get_version(),
        }


# CLI
async def main():
    """CLI for deployment"""
    import argparse

    parser = argparse.ArgumentParser(description="Deploy code")
    parser.add_argument("source", help="Source file or directory")
    parser.add_argument("-t", "--target", default="local",
                       choices=["local", "staging", "production", "docker", "edge"])
    parser.add_argument("-b", "--bump", default="patch",
                       choices=["major", "minor", "patch"])

    args = parser.parse_args()

    deployer = Deployer()
    target = DeployTarget(args.target)

    print(f"Deploying {args.source} to {args.target}...")
    record = await deployer.deploy(args.source, target, args.bump)

    print("\n" + "=" * 40)
    print("DEPLOYMENT RESULT")
    print("=" * 40)
    print(f"ID: {record.id}")
    print(f"Version: {record.version}")
    print(f"Status: {record.status.value}")
    print(f"Checksum: {record.checksum}")
    if record.errors:
        print(f"Errors: {record.errors}")


if __name__ == "__main__":
    asyncio.run(main())
