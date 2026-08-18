from open_reason.verification.sandbox import PYTHON_HARNESS, Sandbox


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
