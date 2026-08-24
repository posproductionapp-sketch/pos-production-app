"""Executable checks for docs/architecture/CONTRACTS.md.

Uses only the Python standard library so the architecture gate can run before
an application framework/build stack is selected.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
CODE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".java", ".kt", ".go", ".rs", ".cs"}

DOMAIN_FORBIDDEN = ("openai", "anthropic", "langchain", "llamaindex", "sqlalchemy", "django.db", "prisma", "typeorm", "sequelize", "psycopg", "pymongo", "mongodb", "httpx", "requests")
AGENT_FORBIDDEN = ("sqlalchemy", "django.db", "prisma", "typeorm", "sequelize", "psycopg", "pymongo", "mongodb", "payment_gateway", "paymentgateway", "orm")
SERVICE_VENDOR_FORBIDDEN = ("openai", "anthropic", "langchain", "llamaindex", "boto3", "stripe", "paypal", "sqlalchemy", "django.db", "prisma", "typeorm", "sequelize", "psycopg", "pymongo")
IMPORT_RE = re.compile(r"(?im)^\s*(?:from|import|use|require\s*\()\s+([^\n;]+)")
SECRET_PATTERNS = (
    re.compile(r"(?i)\b(api[_-]?key|secret|password|passwd|token|private[_-]?key)\s*=\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"(?i)\b(sk-[A-Za-z0-9_-]{12,}|ghp_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{12,})\b"),
)


def source_files(root: Path):
    return [p for p in root.rglob("*") if p.is_file() and p.suffix in CODE_SUFFIXES] if root.exists() else []


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


class ArchitectureContracts(unittest.TestCase):
    def assert_no_imports(self, paths, forbidden, rule):
        violations = []
        for path in paths:
            content = text(path)
            for imported in IMPORT_RE.findall(content):
                imported_lower = imported.lower()
                for term in forbidden:
                    if term in imported_lower:
                        violations.append(f"{path.relative_to(ROOT)}: {term}")
        self.assertFalse(violations, rule + "\n" + "\n".join(violations))

    def test_domain_is_deterministic_and_vendor_independent(self):
        self.assert_no_imports(source_files(SRC / "domain"), DOMAIN_FORBIDDEN, "Domain must not depend on AI, database, HTTP, or vendor SDKs.")

    def test_agents_have_no_direct_persistence_dependency(self):
        self.assert_no_imports(source_files(SRC / "agents"), AGENT_FORBIDDEN, "Agents must not access persistence or infrastructure directly.")

    def test_services_do_not_import_vendor_implementations(self):
        self.assert_no_imports(source_files(SRC / "services"), SERVICE_VENDOR_FORBIDDEN, "Services must depend on explicit contracts rather than vendor SDKs.")

    def test_configuration_contains_no_committed_secrets(self):
        violations = []
        for path in source_files(SRC / "config"):
            if any(pattern.search(text(path)) for pattern in SECRET_PATTERNS):
                violations.append(str(path.relative_to(ROOT)))
        self.assertFalse(violations, "Configuration must be environment-driven and contain no committed secrets: " + ", ".join(violations))

    def test_database_phase_gate_remains_closed(self):
        database_root = SRC / "infrastructure" / "database"
        implementation_files = [
            p for p in database_root.rglob("*")
            if p.is_file() and p.name != ".gitkeep" and p.stat().st_size > 0
        ] if database_root.exists() else []
        self.assertFalse(implementation_files, "Database implementation is blocked until the Database Decision Gate is approved: " + ", ".join(str(p.relative_to(ROOT)) for p in implementation_files))


if __name__ == "__main__":
    unittest.main(verbosity=2)
