from pathlib import Path

from open_reason.verification.sandbox import (
    DOCKER_IMAGE,
    DOCKER_PYTHON,
    PYTHON_HARNESS,
    Sandbox,
    rewrite_command_for_docker,
)

HOSTEDTOOLCACHE_PYTHON = "/opt/hostedtoolcache/Python/3.12.14/x64/bin/python"


def test_sandbox_runs_unittest() -> None:
    files = {
        "solution.py": "def add(a, b):\n    return a + b\n",
        "test_solution.py": (
            "import unittest\nfrom solution import add\n"
            "class T(unittest.TestCase):\n"
            "    def test_add(self):\n"
            "        self.assertEqual(add(2, 3), 5)\n"
        ),
        "harness.py": PYTHON_HARNESS,
    }
    result = Sandbox(timeout_s=10).run_python(files)
    assert result.ok, result.stdout + result.stderr
    assert "OPEN_REASON_RESULT" in result.stdout


def test_rewrite_command_for_docker_drops_hostedtoolcache() -> None:
    rewritten = rewrite_command_for_docker(
        [HOSTEDTOOLCACHE_PYTHON, "harness.py"],
        python_executable=HOSTEDTOOLCACHE_PYTHON,
    )
    assert rewritten == [DOCKER_PYTHON, "harness.py"]
    assert "hostedtoolcache" not in " ".join(rewritten)


def test_docker_argv_uses_container_python() -> None:
    sandbox = Sandbox(python_executable=HOSTEDTOOLCACHE_PYTHON)
    sandbox.backend = "docker"
    argv = sandbox.docker_argv(Path("/tmp/work"), sandbox.python_argv())
    joined = " ".join(argv)
    assert "hostedtoolcache" not in joined
    assert HOSTEDTOOLCACHE_PYTHON not in argv
    assert DOCKER_IMAGE in argv
    image_at = argv.index(DOCKER_IMAGE)
    assert argv[image_at + 1 :] == [DOCKER_PYTHON, "harness.py"]


def test_docker_argv_rewrites_host_python_passed_by_callers() -> None:
    sandbox = Sandbox(python_executable=HOSTEDTOOLCACHE_PYTHON)
    sandbox.backend = "docker"
    argv = sandbox.docker_argv(Path("/tmp/work"), [HOSTEDTOOLCACHE_PYTHON, "run.py"])
    assert argv[-2:] == [DOCKER_PYTHON, "run.py"]


def test_subprocess_keeps_host_python() -> None:
    sandbox = Sandbox(python_executable=HOSTEDTOOLCACHE_PYTHON)
    sandbox.backend = "subprocess"
    assert sandbox.python_argv() == [HOSTEDTOOLCACHE_PYTHON, "harness.py"]
    assert sandbox.python_command == HOSTEDTOOLCACHE_PYTHON
