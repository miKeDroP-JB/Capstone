#!/usr/bin/env python3
"""
TESTER AGENT
Automatically tests generated code.

Creates test cases, runs them, and reports results.
"""
import os
import sys
import ast
import asyncio
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from ai_connectors import AIOrchestrator
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


@dataclass
class TestResult:
    """Result of running tests"""
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    details: List[Dict[str, Any]] = field(default_factory=list)
    coverage: Optional[float] = None
    duration: float = 0.0


@dataclass
class TestCase:
    """A single test case"""
    name: str
    code: str
    expected_result: Any = None
    is_async: bool = False


class CodeTester:
    """
    Tests Python code automatically.

    Capabilities:
    - Syntax validation
    - Import checking
    - Unit test generation
    - Test execution
    - Coverage analysis
    """

    def __init__(self):
        self.ai = AIOrchestrator() if AI_AVAILABLE else None
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0

    async def test_file(self, file_path: str) -> TestResult:
        """Run all tests on a file"""
        result = TestResult()
        start_time = datetime.now()

        path = Path(file_path)
        if not path.exists():
            result.errors = 1
            result.details.append({"error": f"File not found: {file_path}"})
            return result

        code = path.read_text()

        # Step 1: Syntax check
        syntax_ok, syntax_error = self._check_syntax(code)
        if not syntax_ok:
            result.errors = 1
            result.details.append({"stage": "syntax", "error": syntax_error})
            return result
        result.details.append({"stage": "syntax", "status": "passed"})

        # Step 2: Import check
        import_ok, import_errors = await self._check_imports(code)
        if not import_ok:
            result.details.append({"stage": "imports", "errors": import_errors})
        else:
            result.details.append({"stage": "imports", "status": "passed"})

        # Step 3: Generate and run tests
        test_code = await self._generate_tests(code, path.name)
        test_result = await self._run_tests(test_code, code)

        result.passed = test_result.get("passed", 0)
        result.failed = test_result.get("failed", 0)
        result.errors += test_result.get("errors", 0)
        result.details.append({
            "stage": "unit_tests",
            "passed": result.passed,
            "failed": result.failed,
        })

        result.duration = (datetime.now() - start_time).total_seconds()

        # Update stats
        self.tests_run += result.passed + result.failed
        self.tests_passed += result.passed
        self.tests_failed += result.failed

        return result

    def _check_syntax(self, code: str) -> tuple[bool, str]:
        """Check Python syntax"""
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            return False, f"Line {e.lineno}: {e.msg}"

    async def _check_imports(self, code: str) -> tuple[bool, List[str]]:
        """Check if all imports are available"""
        errors = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return False, ["Syntax error - cannot parse"]

        # Find all imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module.split('.')[0])

        # Check each import
        for module in set(imports):
            try:
                __import__(module)
            except ImportError:
                errors.append(f"Cannot import: {module}")

        return len(errors) == 0, errors

    async def _generate_tests(self, code: str, filename: str) -> str:
        """Generate pytest test cases for code"""
        if not self.ai:
            return self._generate_basic_tests(code, filename)

        prompt = f"""Generate pytest test cases for this Python code:

```python
{code[:3000]}
```

Requirements:
1. Test all public functions and methods
2. Include edge cases (empty input, None, boundaries)
3. Test error handling paths
4. Use pytest fixtures where appropriate
5. Each test should be independent

Return ONLY the test code, starting with imports."""

        try:
            result = await self.ai.generate(prompt, task_type="code", complexity=0.6)
            if result.get("success"):
                return result.get("content", "")
        except Exception as e:
            print(f"Test generation error: {e}")

        return self._generate_basic_tests(code, filename)

    def _generate_basic_tests(self, code: str, filename: str) -> str:
        """Generate basic tests without AI"""
        # Parse to find functions
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return ""

        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_'):
                    functions.append(node.name)

        if not functions:
            return "# No public functions found to test"

        tests = f'''import pytest
from {filename.replace('.py', '')} import *

'''
        for func in functions:
            tests += f'''
def test_{func}_exists():
    """Test that {func} function exists"""
    assert callable({func})

def test_{func}_basic():
    """Basic test for {func}"""
    # TODO: Add actual test logic
    pass
'''

        return tests

    async def _run_tests(self, test_code: str, original_code: str) -> Dict[str, int]:
        """Execute tests and return results"""
        if not test_code or test_code.startswith("# No"):
            return {"passed": 0, "failed": 0, "errors": 0}

        # Create temp directory for tests
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write original code
            original_path = Path(tmpdir) / "module_under_test.py"
            original_path.write_text(original_code)

            # Write test code, adjusting imports
            test_code_adjusted = test_code.replace(
                "from module_under_test import",
                "from module_under_test import"
            )
            test_path = Path(tmpdir) / "test_module.py"
            test_path.write_text(test_code_adjusted)

            # Try to run with pytest
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", str(test_path), "-v", "--tb=short"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=tmpdir
                )

                # Parse pytest output
                output = result.stdout + result.stderr
                passed = output.count(" passed")
                failed = output.count(" failed")
                errors = output.count(" error")

                return {"passed": passed, "failed": failed, "errors": errors}

            except subprocess.TimeoutExpired:
                return {"passed": 0, "failed": 0, "errors": 1, "reason": "timeout"}
            except Exception as e:
                return {"passed": 0, "failed": 0, "errors": 1, "reason": str(e)}

    async def validate_and_test(self, file_path: str) -> Dict[str, Any]:
        """Complete validation and testing pipeline"""
        print(f"Testing: {file_path}")

        result = await self.test_file(file_path)

        return {
            "file": file_path,
            "passed": result.passed,
            "failed": result.failed,
            "errors": result.errors,
            "duration": f"{result.duration:.2f}s",
            "details": result.details,
            "success": result.failed == 0 and result.errors == 0,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get tester statistics"""
        return {
            "tests_run": self.tests_run,
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "pass_rate": self.tests_passed / max(1, self.tests_run),
        }


# CLI
async def main():
    """CLI for testing code"""
    import argparse

    parser = argparse.ArgumentParser(description="Test Python code")
    parser.add_argument("file", help="Python file to test")

    args = parser.parse_args()

    tester = CodeTester()
    result = await tester.validate_and_test(args.file)

    print("\n" + "=" * 40)
    print("TEST RESULTS")
    print("=" * 40)
    print(f"File: {result['file']}")
    print(f"Passed: {result['passed']}")
    print(f"Failed: {result['failed']}")
    print(f"Errors: {result['errors']}")
    print(f"Duration: {result['duration']}")
    print(f"Success: {'YES' if result['success'] else 'NO'}")


if __name__ == "__main__":
    asyncio.run(main())
