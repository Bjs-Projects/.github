from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_defaults import validate_defaults  # noqa: E402


BOOTSTRAP_REQUIRED = (
    "Repository: Bjs-Projects/REPOSITORY-NAME",
    "Before any response or action, invoke the installed Superpowers plugin's `using-superpowers` skill, then every applicable Superpowers skill.",
    "read the live `Bjs-Projects/docs/WORKFLOW.md` from `main`",
    "follow it as the sole Bjs-specific policy",
)

PR_HEADINGS = (
    "## Requested result",
    "## Repository and refs",
    "## Change summary",
    "## Verification evidence",
    "## Delivery",
    "## Limitations",
)

MIRRORED_RULES = (
    "SKILLS_INDEX.md",
    ".github/workflows",
    "Google Drive",
    "release-required",
    "release-exempt",
    "expected-head",
    "Final checklist",
    "branch head",
)


def copy_fixture() -> tuple[tempfile.TemporaryDirectory[str], Path]:
    temporary = tempfile.TemporaryDirectory(prefix="organization-defaults-")
    fixture = Path(temporary.name) / "repo"
    for relative in (
        "CHATGPT_PROJECT_INSTRUCTIONS.md",
        ".github/PULL_REQUEST_TEMPLATE.md",
        "scripts/validate_defaults.py",
        "tests/test_validate_defaults.py",
    ):
        source = ROOT / relative
        target = fixture / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return temporary, fixture


class OrganizationDefaultsTests(unittest.TestCase):
    def test_current_files_pass(self) -> None:
        self.assertEqual(validate_defaults(ROOT), [])

    def test_superpowers_precedes_central_workflow_read(self) -> None:
        bootstrap = (ROOT / "CHATGPT_PROJECT_INSTRUCTIONS.md").read_text(encoding="utf-8")
        self.assertLess(bootstrap.index("using-superpowers"), bootstrap.index("docs/WORKFLOW.md"))

    def test_bootstrap_is_minimal(self) -> None:
        bootstrap = (ROOT / "CHATGPT_PROJECT_INSTRUCTIONS.md").read_text(encoding="utf-8")
        for phrase in BOOTSTRAP_REQUIRED:
            self.assertIn(phrase, bootstrap)
        for phrase in MIRRORED_RULES:
            self.assertNotIn(phrase, bootstrap)

    def test_pull_request_template_is_evidence_only(self) -> None:
        template = (ROOT / ".github/PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")
        for heading in PR_HEADINGS:
            self.assertEqual(template.count(heading), 1)
        for phrase in MIRRORED_RULES + ("sole process authority", "Superpowers skill"):
            self.assertNotIn(phrase, template)

    def test_workflow_file_is_rejected(self) -> None:
        temporary, fixture = copy_fixture()
        self.addCleanup(temporary.cleanup)
        workflow = fixture / ".github/workflows/ci.yml"
        workflow.parent.mkdir(parents=True)
        workflow.write_text("name: prohibited\n", encoding="utf-8")
        errors = validate_defaults(fixture)
        self.assertTrue(any("hosted GitHub workflow is prohibited" in error for error in errors), errors)

    def test_mirrored_rule_is_rejected(self) -> None:
        for relative in (
            "CHATGPT_PROJECT_INSTRUCTIONS.md",
            ".github/PULL_REQUEST_TEMPLATE.md",
        ):
            with self.subTest(relative=relative):
                temporary, fixture = copy_fixture()
                self.addCleanup(temporary.cleanup)
                path = fixture / relative
                path.write_text(path.read_text(encoding="utf-8") + "\nSKILLS_INDEX.md\n", encoding="utf-8")
                errors = validate_defaults(fixture)
                self.assertTrue(any("mirrors central policy" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
