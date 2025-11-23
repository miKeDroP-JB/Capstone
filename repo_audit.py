#!/usr/bin/env python3
"""
REPO AUDIT - Complete Security & Optimization Check
====================================================
Scans entire repository for:
- Security vulnerabilities
- Code quality issues
- Integration gaps
- Performance opportunities
- Missing error handling

Love • Loyalty • Honor • Everybody Eats
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

class RepoAuditor:
    """Audits entire repository"""

    def __init__(self):
        self.repo_root = Path("/home/user/Capstone")
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "files_scanned": 0,
            "security_issues": [],
            "code_quality": [],
            "integration_gaps": [],
            "performance_opportunities": [],
            "recommendations": []
        }

    def audit(self):
        """Run complete audit"""

        print(f"\n{'='*60}")
        print("🔍 COMPLETE REPO AUDIT")
        print(f"{'='*60}\n")

        # Find all Python files
        py_files = list(self.repo_root.glob("**/*.py"))

        print(f"Found {len(py_files)} Python files\n")

        for py_file in py_files:
            # Skip virtual envs and build directories
            if any(skip in str(py_file) for skip in ['.venv', 'venv', '__pycache__', 'build', 'node_modules']):
                continue

            self._audit_file(py_file)
            self.results["files_scanned"] += 1

        # Generate report
        self._generate_report()

    def _audit_file(self, file_path: Path):
        """Audit single file"""

        try:
            with open(file_path, 'r') as f:
                content = f.read()
                lines = content.split('\n')

            # Security checks
            self._check_security(file_path, content, lines)

            # Code quality
            self._check_code_quality(file_path, content, lines)

            # Integration
            self._check_integration(file_path, content)

            # Performance
            self._check_performance(file_path, content)

        except Exception as e:
            self.results["security_issues"].append({
                "file": str(file_path),
                "issue": f"Failed to audit: {e}",
                "severity": "low"
            })

    def _check_security(self, file_path: Path, content: str, lines: List[str]):
        """Check for security issues"""

        # 1. Hardcoded secrets
        secret_patterns = [
            (r'password\s*=\s*["\'](?!.*\$\{)(?!.*getenv)([^"\']+)["\']', "Hardcoded password"),
            (r'api[_-]?key\s*=\s*["\'](?!.*\$\{)(?!.*getenv)([^"\']+)["\']', "Hardcoded API key"),
            (r'secret\s*=\s*["\'](?!.*\$\{)(?!.*getenv)([^"\']+)["\']', "Hardcoded secret"),
            (r'token\s*=\s*["\'](?!.*\$\{)(?!.*getenv)([^"\']+)["\']', "Hardcoded token"),
        ]

        for pattern, issue_type in secret_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # Skip if it's in comments or examples
                line_num = content[:match.start()].count('\n') + 1
                if line_num < len(lines) and '//' in lines[line_num-1]:
                    continue

                self.results["security_issues"].append({
                    "file": str(file_path.relative_to(self.repo_root)),
                    "line": line_num,
                    "issue": issue_type,
                    "severity": "high"
                })

        # 2. SQL injection risks
        if re.search(r'execute\s*\([^?]*%s', content) or re.search(r'execute\s*\([^?]*\+\s*', content):
            self.results["security_issues"].append({
                "file": str(file_path.relative_to(self.repo_root)),
                "issue": "Potential SQL injection (string concatenation in execute)",
                "severity": "high"
            })

        # 3. Command injection risks
        if 'os.system(' in content or 'subprocess.call(' in content:
            if 'shell=True' in content:
                self.results["security_issues"].append({
                    "file": str(file_path.relative_to(self.repo_root)),
                    "issue": "Command injection risk (shell=True with user input)",
                    "severity": "high"
                })

        # 4. Unsafe deserialization
        if 'pickle.load' in content and 'rb' in content:
            self.results["security_issues"].append({
                "file": str(file_path.relative_to(self.repo_root)),
                "issue": "Unsafe deserialization (pickle.load on untrusted data)",
                "severity": "medium"
            })

        # 5. Missing input validation on FastAPI endpoints
        if 'FastAPI' in content or '@app.post' in content or '@app.get' in content:
            if 'Depends' not in content and 'HTTPException' not in content:
                self.results["security_issues"].append({
                    "file": str(file_path.relative_to(self.repo_root)),
                    "issue": "API endpoints may lack input validation",
                    "severity": "medium"
                })

    def _check_code_quality(self, file_path: Path, content: str, lines: List[str]):
        """Check code quality"""

        # 1. Long functions (>50 lines)
        function_pattern = r'^\s*def\s+(\w+)'
        in_function = False
        function_start = 0
        function_name = ""

        for i, line in enumerate(lines):
            func_match = re.match(function_pattern, line)
            if func_match:
                # Check previous function
                if in_function and (i - function_start) > 50:
                    self.results["code_quality"].append({
                        "file": str(file_path.relative_to(self.repo_root)),
                        "line": function_start,
                        "issue": f"Long function '{function_name}' ({i - function_start} lines)",
                        "severity": "low"
                    })

                in_function = True
                function_start = i + 1
                function_name = func_match.group(1)

        # 2. Missing docstrings
        if 'def ' in content:
            # Count functions
            func_count = len(re.findall(r'^\s*def\s+\w+', content, re.MULTILINE))
            # Count docstrings
            docstring_count = len(re.findall(r'^\s*""".*?"""', content, re.MULTILINE | re.DOTALL))

            if func_count > 3 and docstring_count < func_count * 0.5:
                self.results["code_quality"].append({
                    "file": str(file_path.relative_to(self.repo_root)),
                    "issue": f"Missing docstrings ({docstring_count}/{func_count} functions documented)",
                    "severity": "low"
                })

        # 3. Too many dependencies in single file
        import_count = len(re.findall(r'^\s*import\s+|^\s*from\s+', content, re.MULTILINE))
        if import_count > 20:
            self.results["code_quality"].append({
                "file": str(file_path.relative_to(self.repo_root)),
                "issue": f"Too many imports ({import_count}) - consider refactoring",
                "severity": "low"
            })

        # 4. Bare excepts
        if 'except:' in content or 'except Exception:' in content:
            bare_excepts = len(re.findall(r'except\s*:', content))
            if bare_excepts > 0:
                self.results["code_quality"].append({
                    "file": str(file_path.relative_to(self.repo_root)),
                    "issue": f"Bare except clauses ({bare_excepts}) - should catch specific exceptions",
                    "severity": "medium"
                })

    def _check_integration(self, file_path: Path, content: str):
        """Check for integration gaps"""

        # Key files and their expected integrations
        integrations = {
            "brain_os.py": ["FastAPI", "ekosystem", "glyph_core"],
            "ekosystem.py": ["brain_os", "ai_connectors"],
            "instant_builder.py": ["brain_os", "ekosystem", "ai_connectors"],
            "MASTER.py": ["client_management_system", "attack_engine", "research_agent"],
        }

        file_name = file_path.name
        if file_name in integrations:
            expected = integrations[file_name]
            missing = []

            for integration in expected:
                if integration not in content:
                    missing.append(integration)

            if missing:
                self.results["integration_gaps"].append({
                    "file": str(file_path.relative_to(self.repo_root)),
                    "missing": missing,
                    "severity": "medium"
                })

    def _check_performance(self, file_path: Path, content: str):
        """Check for performance issues"""

        # 1. Nested loops
        if re.search(r'for\s+.*:\s*\n\s+for\s+.*:', content):
            self.results["performance_opportunities"].append({
                "file": str(file_path.relative_to(self.repo_root)),
                "issue": "Nested loops detected - consider optimization",
                "type": "algorithmic"
            })

        # 2. Loading entire files into memory
        if 'read()' in content and not 'with' in content:
            self.results["performance_opportunities"].append({
                "file": str(file_path.relative_to(self.repo_root)),
                "issue": "File read without context manager - potential memory leak",
                "type": "memory"
            })

        # 3. No async in I/O heavy code
        if any(pattern in content for pattern in ['requests.get', 'requests.post', 'open(']):
            if 'async' not in content and 'await' not in content:
                if file_path.name in ['api', 'agent', 'caller', 'fetcher']:
                    self.results["performance_opportunities"].append({
                        "file": str(file_path.relative_to(self.repo_root)),
                        "issue": "I/O operations without async - consider asyncio",
                        "type": "concurrency"
                    })

    def _generate_report(self):
        """Generate final report"""

        print(f"\n{'='*60}")
        print("📊 AUDIT RESULTS")
        print(f"{'='*60}\n")

        print(f"Files scanned: {self.results['files_scanned']}\n")

        # Security issues
        if self.results["security_issues"]:
            print(f"🔒 SECURITY ISSUES ({len(self.results['security_issues'])})")
            print("─" * 60)

            by_severity = {"high": [], "medium": [], "low": []}
            for issue in self.results["security_issues"]:
                by_severity[issue["severity"]].append(issue)

            for severity in ["high", "medium", "low"]:
                if by_severity[severity]:
                    print(f"\n{severity.upper()}:")
                    for issue in by_severity[severity][:5]:  # Show top 5
                        print(f"  ⚠️  {issue['file']}")
                        print(f"     {issue['issue']}")

            if len(self.results["security_issues"]) > 15:
                print(f"\n  ... and {len(self.results['security_issues']) - 15} more")

        else:
            print("✅ NO SECURITY ISSUES FOUND\n")

        # Code quality
        if self.results["code_quality"]:
            print(f"\n📝 CODE QUALITY ({len(self.results['code_quality'])})")
            print("─" * 60)
            for issue in self.results["code_quality"][:5]:
                print(f"  💡 {issue['file']}")
                print(f"     {issue['issue']}")

            if len(self.results["code_quality"]) > 5:
                print(f"\n  ... and {len(self.results['code_quality']) - 5} more")

        # Integration gaps
        if self.results["integration_gaps"]:
            print(f"\n🔗 INTEGRATION GAPS ({len(self.results['integration_gaps'])})")
            print("─" * 60)
            for gap in self.results["integration_gaps"]:
                print(f"  🔌 {gap['file']}")
                print(f"     Missing: {', '.join(gap['missing'])}")

        # Performance
        if self.results["performance_opportunities"]:
            print(f"\n⚡ PERFORMANCE OPPORTUNITIES ({len(self.results['performance_opportunities'])})")
            print("─" * 60)
            for opp in self.results["performance_opportunities"][:5]:
                print(f"  🚀 {opp['file']}")
                print(f"     {opp['issue']}")

        # Overall recommendations
        self._generate_recommendations()

        if self.results["recommendations"]:
            print(f"\n💡 KEY RECOMMENDATIONS")
            print("─" * 60)
            for i, rec in enumerate(self.results["recommendations"], 1):
                print(f"{i}. {rec}")

        # Save report
        report_file = self.repo_root / "audit_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n✓ Full report saved: {report_file}")
        print()

    def _generate_recommendations(self):
        """Generate overall recommendations"""

        recs = []

        # Based on findings
        high_security = len([i for i in self.results["security_issues"] if i["severity"] == "high"])
        if high_security > 0:
            recs.append(f"🔒 URGENT: Fix {high_security} high-severity security issues")

        if len(self.results["integration_gaps"]) > 0:
            recs.append(f"🔗 Connect {len(self.results['integration_gaps'])} integration gaps for full system flow")

        if len(self.results["performance_opportunities"]) > 5:
            recs.append(f"⚡ Optimize {len(self.results['performance_opportunities'])} performance hotspots for scale")

        # General recommendations
        recs.append("📝 Add comprehensive error handling to all API endpoints")
        recs.append("🧪 Add unit tests for core business logic")
        recs.append("📊 Add monitoring/logging for production debugging")
        recs.append("🔐 Use environment variables for all secrets")
        recs.append("🚀 Consider containerization (Docker) for deployment")

        self.results["recommendations"] = recs


if __name__ == "__main__":
    auditor = RepoAuditor()
    auditor.audit()
