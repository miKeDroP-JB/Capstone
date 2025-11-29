#!/usr/bin/env python3
"""
SECURITY AGENT
Scans code for vulnerabilities and patches them.

Performs static analysis and AI-assisted security review.
"""
import os
import sys
import ast
import re
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


class Severity(Enum):
    """Vulnerability severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Vulnerability:
    """A detected vulnerability"""
    id: str
    severity: Severity
    category: str
    description: str
    line_number: int
    code_snippet: str
    fix_suggestion: str = ""
    cwe_id: Optional[str] = None


@dataclass
class SecurityReport:
    """Security scan report"""
    file_path: str
    scan_time: datetime
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    fixed: int = 0
    risk_score: float = 0.0

    @property
    def critical_count(self) -> int:
        return len([v for v in self.vulnerabilities if v.severity == Severity.CRITICAL])

    @property
    def high_count(self) -> int:
        return len([v for v in self.vulnerabilities if v.severity == Severity.HIGH])


class SecurityScanner:
    """
    Scans Python code for security vulnerabilities.

    Detection methods:
    - Pattern matching (known dangerous patterns)
    - AST analysis (dangerous function calls)
    - AI-assisted review (complex vulnerabilities)
    """

    # Dangerous patterns with severity and CWE references
    PATTERNS = [
        # Code injection
        (r"\beval\s*\(", Severity.CRITICAL, "code_injection", "CWE-94", "Use of eval() allows arbitrary code execution"),
        (r"\bexec\s*\(", Severity.CRITICAL, "code_injection", "CWE-94", "Use of exec() allows arbitrary code execution"),
        (r"\bcompile\s*\([^)]*,\s*['\"]exec['\"]", Severity.HIGH, "code_injection", "CWE-94", "Dynamic code compilation with exec mode"),

        # Command injection
        (r"\bos\.system\s*\(", Severity.CRITICAL, "command_injection", "CWE-78", "os.system() is vulnerable to command injection"),
        (r"\bos\.popen\s*\(", Severity.HIGH, "command_injection", "CWE-78", "os.popen() can be exploited for command injection"),
        (r"\bsubprocess\.call\s*\([^)]*shell\s*=\s*True", Severity.CRITICAL, "command_injection", "CWE-78", "subprocess with shell=True is dangerous"),
        (r"\bsubprocess\.Popen\s*\([^)]*shell\s*=\s*True", Severity.CRITICAL, "command_injection", "CWE-78", "Popen with shell=True allows command injection"),

        # SQL injection
        (r"execute\s*\([^)]*%[sd]", Severity.CRITICAL, "sql_injection", "CWE-89", "String formatting in SQL query - use parameterized queries"),
        (r"execute\s*\([^)]*\.format\s*\(", Severity.CRITICAL, "sql_injection", "CWE-89", "Format string in SQL query - use parameterized queries"),
        (r"execute\s*\([^)]*f['\"]", Severity.CRITICAL, "sql_injection", "CWE-89", "F-string in SQL query - use parameterized queries"),

        # Deserialization
        (r"\bpickle\.loads?\s*\(", Severity.HIGH, "deserialization", "CWE-502", "Pickle deserialization can execute arbitrary code"),
        (r"\byaml\.load\s*\([^)]*\)", Severity.HIGH, "deserialization", "CWE-502", "Use yaml.safe_load() instead of yaml.load()"),
        (r"\bmarshall\.loads?\s*\(", Severity.HIGH, "deserialization", "CWE-502", "Marshall deserialization is unsafe"),

        # Path traversal
        (r"open\s*\([^)]*\+[^)]*\)", Severity.MEDIUM, "path_traversal", "CWE-22", "Dynamic file path may allow path traversal"),
        (r"Path\s*\([^)]*\+[^)]*\)", Severity.MEDIUM, "path_traversal", "CWE-22", "Dynamic Path construction may allow traversal"),

        # Hardcoded secrets
        (r"['\"]password['\"\s]*[:=]\s*['\"][^'\"]+['\"]", Severity.HIGH, "hardcoded_secret", "CWE-798", "Hardcoded password detected"),
        (r"['\"]api_key['\"\s]*[:=]\s*['\"][^'\"]+['\"]", Severity.HIGH, "hardcoded_secret", "CWE-798", "Hardcoded API key detected"),
        (r"['\"]secret['\"\s]*[:=]\s*['\"][a-zA-Z0-9]{16,}['\"]", Severity.HIGH, "hardcoded_secret", "CWE-798", "Hardcoded secret detected"),

        # Weak crypto
        (r"\bmd5\s*\(", Severity.MEDIUM, "weak_crypto", "CWE-328", "MD5 is cryptographically weak - use SHA-256+"),
        (r"\bsha1\s*\(", Severity.MEDIUM, "weak_crypto", "CWE-328", "SHA1 is deprecated - use SHA-256+"),
        (r"DES\s*\(", Severity.HIGH, "weak_crypto", "CWE-327", "DES encryption is broken - use AES"),

        # Debug/development
        (r"\bbreakpoint\s*\(", Severity.LOW, "debug_code", None, "Breakpoint left in code"),
        (r"\bpdb\.\w+\s*\(", Severity.LOW, "debug_code", None, "Debugger code left in source"),
        (r"DEBUG\s*=\s*True", Severity.MEDIUM, "debug_code", None, "Debug mode enabled"),

        # Dangerous defaults
        (r"verify\s*=\s*False", Severity.HIGH, "ssl_bypass", "CWE-295", "SSL verification disabled"),
        (r"allow_redirects\s*=\s*True", Severity.LOW, "open_redirect", "CWE-601", "Unrestricted redirects enabled"),
    ]

    def __init__(self):
        self.ai = AIOrchestrator() if AI_AVAILABLE else None
        self.scans_completed = 0
        self.vulnerabilities_found = 0
        self.vulnerabilities_fixed = 0

    async def scan_file(self, file_path: str) -> SecurityReport:
        """Scan a file for security vulnerabilities"""
        path = Path(file_path)
        report = SecurityReport(
            file_path=str(path),
            scan_time=datetime.now()
        )

        if not path.exists():
            return report

        code = path.read_text()
        lines = code.split('\n')

        # Pattern-based scanning
        vuln_id = 0
        for pattern, severity, category, cwe, description in self.PATTERNS:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    vuln_id += 1
                    report.vulnerabilities.append(Vulnerability(
                        id=f"VULN-{vuln_id:04d}",
                        severity=severity,
                        category=category,
                        description=description,
                        line_number=i,
                        code_snippet=line.strip()[:100],
                        cwe_id=cwe
                    ))

        # AST-based analysis
        ast_vulns = await self._ast_analysis(code)
        for vuln in ast_vulns:
            vuln_id += 1
            vuln.id = f"VULN-{vuln_id:04d}"
            report.vulnerabilities.append(vuln)

        # AI-assisted review for complex issues
        if self.ai and len(code) < 10000:
            ai_vulns = await self._ai_review(code)
            for vuln in ai_vulns:
                vuln_id += 1
                vuln.id = f"VULN-{vuln_id:04d}"
                report.vulnerabilities.append(vuln)

        # Calculate risk score
        report.risk_score = self._calculate_risk(report.vulnerabilities)

        self.scans_completed += 1
        self.vulnerabilities_found += len(report.vulnerabilities)

        return report

    async def _ast_analysis(self, code: str) -> List[Vulnerability]:
        """Analyze AST for security issues"""
        vulnerabilities = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return vulnerabilities

        for node in ast.walk(tree):
            # Check for dangerous imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ['telnetlib', 'ftplib']:
                        vulnerabilities.append(Vulnerability(
                            id="",
                            severity=Severity.MEDIUM,
                            category="insecure_protocol",
                            description=f"Insecure protocol: {alias.name}",
                            line_number=node.lineno,
                            code_snippet=f"import {alias.name}",
                            cwe_id="CWE-319"
                        ))

            # Check for assert statements (can be disabled)
            if isinstance(node, ast.Assert):
                vulnerabilities.append(Vulnerability(
                    id="",
                    severity=Severity.LOW,
                    category="assert_usage",
                    description="Assert can be disabled with -O flag",
                    line_number=node.lineno,
                    code_snippet="assert ...",
                    cwe_id="CWE-617"
                ))

        return vulnerabilities

    async def _ai_review(self, code: str) -> List[Vulnerability]:
        """AI-assisted security review"""
        if not self.ai:
            return []

        prompt = f"""Review this Python code for security vulnerabilities:

```python
{code[:4000]}
```

Identify issues not caught by simple pattern matching:
- Logic flaws
- Race conditions
- Information disclosure
- Authentication/authorization issues
- Input validation gaps

For each issue found, respond in this exact format:
VULN|severity|category|line_number|description

Where severity is: critical, high, medium, or low
Only report real issues, not style concerns."""

        try:
            result = await self.ai.generate(prompt, task_type="analysis", complexity=0.8)
            if not result.get("success"):
                return []

            content = result.get("content", "")
            vulnerabilities = []

            for line in content.split('\n'):
                if line.startswith('VULN|'):
                    parts = line.split('|')
                    if len(parts) >= 5:
                        try:
                            vulnerabilities.append(Vulnerability(
                                id="",
                                severity=Severity(parts[1].lower().strip()),
                                category=parts[2].strip(),
                                description=parts[4].strip(),
                                line_number=int(parts[3]) if parts[3].isdigit() else 0,
                                code_snippet="[AI detected]"
                            ))
                        except (ValueError, KeyError):
                            pass

            return vulnerabilities

        except Exception:
            return []

    def _calculate_risk(self, vulnerabilities: List[Vulnerability]) -> float:
        """Calculate overall risk score (0-100)"""
        weights = {
            Severity.CRITICAL: 25,
            Severity.HIGH: 15,
            Severity.MEDIUM: 8,
            Severity.LOW: 3,
            Severity.INFO: 1,
        }

        score = sum(weights.get(v.severity, 0) for v in vulnerabilities)
        return min(100.0, score)

    async def fix_vulnerabilities(self, file_path: str, report: SecurityReport) -> Tuple[str, int]:
        """Attempt to fix vulnerabilities in file"""
        if not report.vulnerabilities:
            return "", 0

        path = Path(file_path)
        code = path.read_text()
        fixed_count = 0

        # Simple pattern-based fixes
        fixes = {
            r"yaml\.load\s*\(": ("yaml.safe_load(", "YAML deserialization"),
            r"os\.system\s*\(": ("subprocess.run(", "Command execution"),
            r"DEBUG\s*=\s*True": ("DEBUG = False  # Production", "Debug mode"),
        }

        for pattern, (replacement, desc) in fixes.items():
            if re.search(pattern, code):
                code = re.sub(pattern, replacement, code)
                fixed_count += 1

        # AI-assisted fixes for complex issues
        if self.ai and fixed_count < len(report.vulnerabilities):
            critical_vulns = [v for v in report.vulnerabilities
                           if v.severity in [Severity.CRITICAL, Severity.HIGH]]

            if critical_vulns:
                prompt = f"""Fix these security vulnerabilities in the code:

Vulnerabilities:
{chr(10).join(f'- Line {v.line_number}: {v.description}' for v in critical_vulns[:5])}

Code:
```python
{code[:4000]}
```

Return the complete fixed code, maintaining all functionality."""

                try:
                    result = await self.ai.generate(prompt, task_type="code", complexity=0.9)
                    if result.get("success"):
                        code = result.get("content", code)
                        fixed_count = len(critical_vulns)
                except Exception:
                    pass

        if fixed_count > 0:
            # Backup original
            backup = path.with_suffix('.py.insecure')
            backup.write_text(path.read_text())

            # Write fixed code
            path.write_text(code)

        self.vulnerabilities_fixed += fixed_count
        return code, fixed_count

    def get_stats(self) -> Dict[str, Any]:
        """Get scanner statistics"""
        return {
            "scans_completed": self.scans_completed,
            "vulnerabilities_found": self.vulnerabilities_found,
            "vulnerabilities_fixed": self.vulnerabilities_fixed,
            "fix_rate": self.vulnerabilities_fixed / max(1, self.vulnerabilities_found),
        }


# CLI
async def main():
    """CLI for security scanning"""
    import argparse

    parser = argparse.ArgumentParser(description="Scan Python code for security issues")
    parser.add_argument("file", help="Python file to scan")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix issues")

    args = parser.parse_args()

    scanner = SecurityScanner()
    report = await scanner.scan_file(args.file)

    print("\n" + "=" * 50)
    print("SECURITY SCAN REPORT")
    print("=" * 50)
    print(f"File: {report.file_path}")
    print(f"Scan Time: {report.scan_time}")
    print(f"Risk Score: {report.risk_score:.1f}/100")
    print(f"Critical: {report.critical_count}")
    print(f"High: {report.high_count}")
    print(f"Total: {len(report.vulnerabilities)}")

    if report.vulnerabilities:
        print("\nVulnerabilities:")
        for v in report.vulnerabilities:
            print(f"  [{v.severity.value.upper()}] Line {v.line_number}: {v.description}")
            if v.cwe_id:
                print(f"           {v.cwe_id}")

    if args.fix and report.vulnerabilities:
        print("\nAttempting fixes...")
        _, fixed = await scanner.fix_vulnerabilities(args.file, report)
        print(f"Fixed: {fixed} issues")


if __name__ == "__main__":
    asyncio.run(main())
