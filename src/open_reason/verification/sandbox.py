"""Isolated execution for untrusted or generated code.

The verifier assumes code may be hostile. Docker is preferred when available.
The subprocess fallback uses a temporary directory, a timeout, a stripped
environment, and (on POSIX) resource limits. It is not a security boundary
equivalent to a container and must not be used to run arbitrary third-party
code on a trusted host.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass
class SandboxResult:
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool
    backend: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and not self.timed_out


DOCKER_IMAGE = "python:3.12-alpine"
DOCKER_PYTHON = "python"
_PYTHON_NAMES = {"python", "python3", "python.exe", "python3.exe", "py.exe", "py"}
_NODE_NAMES = {"node", "node.exe"}


def docker_available() -> bool:
    return shutil.which("docker") is not None


def rewrite_command_for_docker(
    command: list[str],
    *,
    python_executable: str | None = None,
) -> list[str]:
    """Map host interpreter paths onto binaries that exist in DOCKER_IMAGE.

    GitHub Actions sets sys.executable to a hostedtoolcache path that is not
    present inside python:3.12-alpine. Always run the image interpreter.
    """
    if not command:
        return list(command)
    rewritten = list(command)
    first = rewritten[0]
    name = Path(first).name.lower()
    host_python = python_executable or sys.executable
    if first in {host_python, sys.executable} or name in _PYTHON_NAMES:
        rewritten[0] = DOCKER_PYTHON
    elif name in _NODE_NAMES:
        rewritten[0] = "node"
    return rewritten


class Sandbox:
    def __init__(
        self,
        *,
        timeout_s: int = 12,
        memory_mb: int = 512,
        python_executable: str | None = None,
    ) -> None:
        self.timeout_s = timeout_s
        self.memory_mb = memory_mb
        self.python_executable = python_executable or sys.executable
        self.backend = "docker" if docker_available() else "subprocess"

    @property
    def python_command(self) -> str:
        """Interpreter to invoke for this backend (image python under Docker)."""
        return DOCKER_PYTHON if self.backend == "docker" else self.python_executable

    def python_argv(self, script: str = "harness.py") -> list[str]:
        return [self.python_command, script]

    def run(
        self,
        files: Mapping[str, str],
        command: list[str],
        *,
        stdin: str | None = None,
    ) -> SandboxResult:
        if self.backend == "docker":
            return self._run_docker(files, command, stdin=stdin)
        return self._run_subprocess(files, command, stdin=stdin)

    def run_python(
        self,
        files: Mapping[str, str],
        command: list[str] | None = None,
        *,
        stdin: str | None = None,
    ) -> SandboxResult:
        command = command or self.python_argv()
        return self.run(files, command, stdin=stdin)

    def docker_argv(self, work: Path, command: list[str]) -> list[str]:
        """Build `docker run` argv. The inner command uses image interpreters."""
        inner = rewrite_command_for_docker(command, python_executable=self.python_executable)
        return [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--cpus",
            "1",
            "--memory",
            f"{self.memory_mb}m",
            "--pids-limit",
            "64",
            "--read-only",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=64m",
            "-e",
            "PYTHONDONTWRITEBYTECODE=1",
            "-e",
            "PYTHONHASHSEED=0",
            "-e",
            "PYTHONSAFEPATH=1",
            "-e",
            "HOME=/tmp",
            "-v",
            f"{work}:/work:ro",
            "-w",
            "/work",
            DOCKER_IMAGE,
            *inner,
        ]

    def _run_subprocess(
        self,
        files: Mapping[str, str],
        command: list[str],
        *,
        stdin: str | None,
    ) -> SandboxResult:
        work = Path(tempfile.mkdtemp(prefix="open-reason-sandbox-"))
        try:
            _write_files(work, files)
            env = {
                "PYTHONSAFEPATH": "1",
                "PYTHONHASHSEED": "0",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PATH": os.environ.get("PATH", ""),
                "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
                "WINDIR": os.environ.get("WINDIR", ""),
                "TEMP": str(work),
                "TMP": str(work),
            }
            preexec = None
            if os.name == "posix":

                def _limits() -> None:
                    try:
                        import resource

                        mem = self.memory_mb * 1024 * 1024
                        resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
                        resource.setrlimit(resource.RLIMIT_CPU, (self.timeout_s, self.timeout_s))
                        resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))
                    except (ValueError, OSError):
                        return

                preexec = _limits
            try:
                completed = subprocess.run(
                    command,
                    cwd=work,
                    env=env,
                    input=stdin,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    capture_output=True,
                    timeout=self.timeout_s,
                    preexec_fn=preexec,
                )
                return SandboxResult(
                    completed.returncode,
                    completed.stdout[-8000:],
                    completed.stderr[-8000:],
                    False,
                    "subprocess",
                )
            except subprocess.TimeoutExpired as exc:
                stdout = (exc.stdout or "")[-8000:]
                stderr = (exc.stderr or "")[-8000:]
                if isinstance(stdout, bytes):
                    stdout = stdout.decode("utf-8", "replace")
                if isinstance(stderr, bytes):
                    stderr = stderr.decode("utf-8", "replace")
                return SandboxResult(124, stdout, stderr or "timeout", True, "subprocess")
        finally:
            shutil.rmtree(work, ignore_errors=True)

    def _run_docker(
        self,
        files: Mapping[str, str],
        command: list[str],
        *,
        stdin: str | None,
    ) -> SandboxResult:
        work = Path(tempfile.mkdtemp(prefix="open-reason-docker-"))
        try:
            _write_files(work, files)
            docker_cmd = self.docker_argv(work, command)
            try:
                completed = subprocess.run(
                    docker_cmd,
                    input=stdin,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    capture_output=True,
                    timeout=self.timeout_s + 8,
                )
                return SandboxResult(
                    completed.returncode,
                    completed.stdout[-8000:],
                    completed.stderr[-8000:],
                    False,
                    "docker",
                )
            except subprocess.TimeoutExpired:
                return SandboxResult(124, "", "timeout", True, "docker")
        finally:
            shutil.rmtree(work, ignore_errors=True)


def _write_files(root: Path, files: Mapping[str, str]) -> None:
    for name, content in files.items():
        target = (root / name).resolve()
        if root.resolve() not in target.parents and target != root.resolve():
            raise ValueError(f"refusing to write outside sandbox: {name}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")


PYTHON_HARNESS = '''\
import json
import traceback
import unittest

loader = unittest.defaultTestLoader
suite = loader.discover(".", pattern="test_*.py")
result = unittest.TextTestRunner(verbosity=2).run(suite)
payload = {
    "tests_run": result.testsRun,
    "failures": len(result.failures),
    "errors": len(result.errors),
    "skipped": len(result.skipped),
    "passed": result.wasSuccessful(),
}
print("OPEN_REASON_RESULT " + json.dumps(payload))
raise SystemExit(0 if result.wasSuccessful() else 1)
'''
