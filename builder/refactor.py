#!/usr/bin/env python3
"""
REFACTOR AGENT
Improves code quality, readability, and performance.

Applies best practices and design patterns.
"""
import os
import sys
import ast
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from ai_connectors import AIOrchestrator
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


class RefactorType(Enum):
    """Types of refactoring"""
    READABILITY = "readability"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DOCUMENTATION = "documentation"
    TYPE_HINTS = "type_hints"
    PATTERNS = "patterns"
    ALL = "all"


@dataclass
class RefactorSuggestion:
    """A suggested refactoring"""
    type: RefactorType
    description: str
    line_start: int
    line_end: int
    original: str
    suggested: str
    impact: str  # low, medium, high
    auto_fixable: bool = True


@dataclass
class RefactorResult:
    """Result of refactoring"""
    file_path: str
    original_code: str
    refactored_code: str
    suggestions_applied: int
    suggestions_skipped: int
    improvements: List[str] = field(default_factory=list)
    metrics_before: Dict[str, Any] = field(default_factory=dict)
    metrics_after: Dict[str, Any] = field(default_factory=dict)


class CodeRefactorer:
    """
    Refactors Python code for quality improvement.

    Capabilities:
    - Improve readability
    - Add type hints
    - Enhance documentation
    - Apply design patterns
    - Optimize performance
    """

    def __init__(self):
        self.ai = AIOrchestrator() if AI_AVAILABLE else None
        self.refactors_completed = 0
        self.lines_improved = 0

    async def refactor(
        self,
        file_path: str,
        refactor_types: List[RefactorType] = None
    ) -> RefactorResult:
        """Refactor a file"""
        refactor_types = refactor_types or [RefactorType.ALL]

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        original_code = path.read_text()
        metrics_before = self._calculate_metrics(original_code)

        result = RefactorResult(
            file_path=file_path,
            original_code=original_code,
            refactored_code=original_code,
            suggestions_applied=0,
            suggestions_skipped=0,
            metrics_before=metrics_before
        )

        # Collect suggestions
        suggestions = []

        if RefactorType.ALL in refactor_types or RefactorType.READABILITY in refactor_types:
            suggestions.extend(await self._analyze_readability(original_code))

        if RefactorType.ALL in refactor_types or RefactorType.TYPE_HINTS in refactor_types:
            suggestions.extend(await self._analyze_type_hints(original_code))

        if RefactorType.ALL in refactor_types or RefactorType.DOCUMENTATION in refactor_types:
            suggestions.extend(await self._analyze_documentation(original_code))

        if RefactorType.ALL in refactor_types or RefactorType.PERFORMANCE in refactor_types:
            suggestions.extend(await self._analyze_performance(original_code))

        # Apply AI-assisted comprehensive refactoring
        if self.ai:
            refactored = await self._ai_refactor(original_code, refactor_types)
            if refactored and refactored != original_code:
                result.refactored_code = refactored
                result.suggestions_applied = len(suggestions)
                result.improvements.append("AI-assisted refactoring applied")

        # Calculate improvement metrics
        result.metrics_after = self._calculate_metrics(result.refactored_code)
        result.improvements.extend(self._compare_metrics(metrics_before, result.metrics_after))

        # Save refactored code
        if result.refactored_code != original_code:
            # Backup original
            backup = path.with_suffix('.py.original')
            backup.write_text(original_code)

            # Write refactored
            path.write_text(result.refactored_code)

            self.refactors_completed += 1
            self.lines_improved += abs(
                len(result.refactored_code.split('\n')) -
                len(original_code.split('\n'))
            )

        return result

    def _calculate_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate code metrics"""
        lines = code.split('\n')

        # Basic metrics
        total_lines = len(lines)
        blank_lines = len([l for l in lines if not l.strip()])
        comment_lines = len([l for l in lines if l.strip().startswith('#')])
        code_lines = total_lines - blank_lines - comment_lines

        # Complexity estimation
        try:
            tree = ast.parse(code)
            functions = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
            classes = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
            imports = len([n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))])
        except SyntaxError:
            functions = classes = imports = 0

        # Docstring coverage
        docstrings = code.count('"""') // 2 + code.count("'''") // 2

        return {
            "total_lines": total_lines,
            "code_lines": code_lines,
            "blank_lines": blank_lines,
            "comment_lines": comment_lines,
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "docstrings": docstrings,
            "avg_line_length": sum(len(l) for l in lines) / max(1, total_lines),
        }

    def _compare_metrics(self, before: Dict, after: Dict) -> List[str]:
        """Compare metrics and generate improvement notes"""
        improvements = []

        if after.get("docstrings", 0) > before.get("docstrings", 0):
            improvements.append(f"Added {after['docstrings'] - before['docstrings']} docstrings")

        if after.get("avg_line_length", 0) < before.get("avg_line_length", 0):
            improvements.append("Improved line length distribution")

        if after.get("code_lines", 0) < before.get("code_lines", 0):
            reduction = before["code_lines"] - after["code_lines"]
            improvements.append(f"Reduced code by {reduction} lines")

        return improvements

    async def _analyze_readability(self, code: str) -> List[RefactorSuggestion]:
        """Analyze code for readability issues"""
        suggestions = []
        lines = code.split('\n')

        for i, line in enumerate(lines, 1):
            # Long lines
            if len(line) > 100:
                suggestions.append(RefactorSuggestion(
                    type=RefactorType.READABILITY,
                    description="Line too long (>100 chars)",
                    line_start=i,
                    line_end=i,
                    original=line,
                    suggested="[Split into multiple lines]",
                    impact="low"
                ))

            # Complex comprehensions
            if line.count('[') > 2 or line.count('{') > 2:
                suggestions.append(RefactorSuggestion(
                    type=RefactorType.READABILITY,
                    description="Complex nested comprehension",
                    line_start=i,
                    line_end=i,
                    original=line,
                    suggested="[Consider extracting to function]",
                    impact="medium"
                ))

        return suggestions

    async def _analyze_type_hints(self, code: str) -> List[RefactorSuggestion]:
        """Analyze code for missing type hints"""
        suggestions = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return suggestions

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check return type
                if node.returns is None and node.name != '__init__':
                    suggestions.append(RefactorSuggestion(
                        type=RefactorType.TYPE_HINTS,
                        description=f"Missing return type hint for '{node.name}'",
                        line_start=node.lineno,
                        line_end=node.lineno,
                        original=f"def {node.name}(...)",
                        suggested=f"def {node.name}(...) -> ReturnType:",
                        impact="low"
                    ))

                # Check argument types
                for arg in node.args.args:
                    if arg.annotation is None and arg.arg != 'self':
                        suggestions.append(RefactorSuggestion(
                            type=RefactorType.TYPE_HINTS,
                            description=f"Missing type hint for argument '{arg.arg}'",
                            line_start=node.lineno,
                            line_end=node.lineno,
                            original=arg.arg,
                            suggested=f"{arg.arg}: Type",
                            impact="low"
                        ))

        return suggestions

    async def _analyze_documentation(self, code: str) -> List[RefactorSuggestion]:
        """Analyze code for documentation issues"""
        suggestions = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return suggestions

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                docstring = ast.get_docstring(node)
                if not docstring:
                    suggestions.append(RefactorSuggestion(
                        type=RefactorType.DOCUMENTATION,
                        description=f"Missing docstring for '{node.name}'",
                        line_start=node.lineno,
                        line_end=node.lineno,
                        original=f"def/class {node.name}",
                        suggested="[Add docstring]",
                        impact="medium"
                    ))

        return suggestions

    async def _analyze_performance(self, code: str) -> List[RefactorSuggestion]:
        """Analyze code for performance issues"""
        suggestions = []
        lines = code.split('\n')

        patterns = [
            (r'\+ \[\]', "List concatenation in loop - use extend()"),
            (r'\.append\([^)]+\) for ', "Consider list comprehension"),
            (r'range\(len\(', "Use enumerate() instead of range(len())"),
            (r'dict\(\)', "Use {} for empty dict literal"),
            (r'list\(\)', "Use [] for empty list literal"),
        ]

        import re
        for i, line in enumerate(lines, 1):
            for pattern, description in patterns:
                if re.search(pattern, line):
                    suggestions.append(RefactorSuggestion(
                        type=RefactorType.PERFORMANCE,
                        description=description,
                        line_start=i,
                        line_end=i,
                        original=line.strip(),
                        suggested="[See description]",
                        impact="medium"
                    ))

        return suggestions

    async def _ai_refactor(self, code: str, types: List[RefactorType]) -> Optional[str]:
        """Use AI for comprehensive refactoring"""
        if not self.ai:
            return None

        type_names = [t.value for t in types]

        prompt = f"""Refactor this Python code for these improvements: {', '.join(type_names)}

```python
{code[:4000]}
```

Requirements:
1. Maintain exact functionality
2. Add type hints where missing
3. Add docstrings to functions/classes
4. Improve readability
5. Apply Python best practices
6. Use modern Python features (3.10+)

Return ONLY the refactored code, no explanations."""

        try:
            result = await self.ai.generate(prompt, task_type="code", complexity=0.7)
            if result.get("success"):
                refactored = result.get("content", "")
                # Validate the refactored code
                try:
                    ast.parse(refactored)
                    return refactored
                except SyntaxError:
                    return None
        except Exception:
            pass

        return None

    def get_stats(self) -> Dict[str, Any]:
        """Get refactorer statistics"""
        return {
            "refactors_completed": self.refactors_completed,
            "lines_improved": self.lines_improved,
        }


# CLI
async def main():
    """CLI for refactoring"""
    import argparse

    parser = argparse.ArgumentParser(description="Refactor Python code")
    parser.add_argument("file", help="Python file to refactor")
    parser.add_argument("-t", "--types", nargs="+", default=["all"],
                       choices=["readability", "performance", "documentation", "type_hints", "all"])

    args = parser.parse_args()

    refactorer = CodeRefactorer()
    types = [RefactorType(t) for t in args.types]

    print(f"Refactoring: {args.file}")
    result = await refactorer.refactor(args.file, types)

    print("\n" + "=" * 40)
    print("REFACTOR RESULT")
    print("=" * 40)
    print(f"File: {result.file_path}")
    print(f"Suggestions Applied: {result.suggestions_applied}")
    print(f"Improvements: {', '.join(result.improvements) if result.improvements else 'None'}")
    print(f"\nMetrics Before: {result.metrics_before}")
    print(f"Metrics After: {result.metrics_after}")


if __name__ == "__main__":
    asyncio.run(main())
