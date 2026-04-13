import json
import os
import subprocess
from dataclasses import dataclass

import docker
from docker.errors import DockerException

from app.core.config import get_settings


@dataclass
class SandboxResult:
    findings: list[dict]
    stdout: str
    stderr: str


class ContainerManager:
    def __init__(self) -> None:
        self.settings = get_settings()

    def execute_plugin(self, plugin_name: str, target: str) -> SandboxResult:
        command = ["python", "-m", "app.sandbox_runner", "--plugin", plugin_name, "--target", target]
        try:
            return self._execute_in_docker(command)
        except DockerException:
            return self._execute_locally(command)

    def _execute_in_docker(self, command: list[str]) -> SandboxResult:
        client = docker.from_env() if not self.settings.docker_host else docker.DockerClient(base_url=self.settings.docker_host)
        container = client.containers.run(
            self.settings.sandbox_runner_image,
            command=command,
            detach=True,
            network_mode=self.settings.sandbox_network,
            mem_limit=self.settings.sandbox_memory_limit,
            nano_cpus=int(float(self.settings.sandbox_cpu_limit) * 1_000_000_000),
            read_only=True,
            remove=False,
            security_opt=["no-new-privileges:true"],
            cap_drop=["ALL"],
        )
        result = container.wait(timeout=self.settings.sandbox_timeout_seconds)
        stdout = container.logs(stdout=True, stderr=False).decode("utf-8")
        stderr = container.logs(stdout=False, stderr=True).decode("utf-8")
        container.remove(force=True)
        if result["StatusCode"] != 0:
            raise RuntimeError(stderr or stdout or "Sandbox container failed.")
        findings = json.loads(stdout or "[]")
        return SandboxResult(findings=findings, stdout=stdout, stderr=stderr)

    def _execute_locally(self, command: list[str]) -> SandboxResult:
        env = os.environ.copy()
        completed = subprocess.run(command, capture_output=True, text=True, check=True, env=env, timeout=self.settings.sandbox_timeout_seconds)
        findings = json.loads(completed.stdout or "[]")
        return SandboxResult(findings=findings, stdout=completed.stdout, stderr=completed.stderr)

