from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_defaults import validate_defaults  # noqa: E402


FIXTURE_PATHS = (
    "CHATGPT_PROJECT_INSTRUCTIONS.md",
    "CONTRIBUTING.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/pull_request_template.md",
    ".github/ISSUE_TEMPLATE/bug.yml",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    "scripts/validate_defaults.py",
    "tests/test_validate_defaults.py",
)


def copy_fixture() -> tuple[tempfile.TemporaryDirectory[str], Path]:
    temporary = tempfile.TemporaryDirectory(prefix="organization-defaults-")
    fixture = Path(temporary.name) / "repo"
    for relative in FIXTURE_PATHS:
        source = ROOT / relative
        if not source.exists():
            continue
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

    def test_semantically_equivalent_bootstrap_wording_is_accepted(self) -> None:
        temporary, fixture = copy_fixture()
        self.addCleanup(temporary.cleanup)
        path = fixture / "CHATGPT_PROJECT_INSTRUCTIONS.md"
        text = path.read_text(encoding="utf-8")
        if "and every applicable Superpowers skill" in text:
            text = text.replace(
                "and every applicable Superpowers skill",
                "then every applicable Superpowers skill",
            )
        else:
            text = text.replace(
                "then every applicable Superpowers skill",
                "and every applicable Superpowers skill",
            )
        path.write_text(text, encoding="utf-8")
        errors = validate_defaults(fixture)
        self.assertFalse(any("bootstrap" in error for error in errors), errors)

    def test_duplicate_pull_request_template_is_rejected(self) -> None:
        temporary, fixture = copy_fixture()
        self.addCleanup(temporary.cleanup)
        source = fixture / ".github/PULL_REQUEST_TEMPLATE.md"
        duplicate = fixture / ".github/pull_request_template.md"
        duplicate.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        errors = validate_defaults(fixture)
        self.assertTrue(
            any("multiple pull request templates" in error for error in errors),
            errors,
        )

    def test_duplicate_issue_form_purpose_is_rejected(self) -> None:
        temporary, fixture = copy_fixture()
        self.addCleanup(temporary.cleanup)
        source = fixture / ".github/ISSUE_TEMPLATE/bug.yml"
        duplicate = fixture / ".github/ISSUE_TEMPLATE/bug_report.yml"
        duplicate.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        errors = validate_defaults(fixture)
        self.assertTrue(
            any("duplicate issue form purpose" in error for error in errors),
            errors,
        )

    def test_duplicate_issue_field_id_is_rejected(self) -> None:
        temporary, fixture = copy_fixture()
        self.addCleanup(temporary.cleanup)
        path = fixture / ".github/ISSUE_TEMPLATE/bug.yml"
        text = path.read_text(encoding="utf-8")
        path.write_text(
            text.replace("    id: version", "    id: repository", 1),
            encoding="utf-8",
        )
        errors = validate_defaults(fixture)
        self.assertTrue(any("duplicate field id" in error for error in errors), errors)

    def test_pull_request_heading_order_is_not_policy(self) -> None:
        temporary, fixture = copy_fixture()
        self.addCleanup(temporary.cleanup)
        path = fixture / ".github/PULL_REQUEST_TEMPLATE.md"
        sections = path.read_text(encoding="utf-8").strip().split("\n\n")
        path.write_text("\n\n".join(reversed(sections)) + "\n", encoding="utf-8")
        self.assertEqual(validate_defaults(fixture), [])

    def test_workflow_file_is_rejected(self) -> None:
        temporary, fixture = copy_fixture()
        self.addCleanup(temporary.cleanup)
        workflow = fixture / ".github/workflows/ci.yml"
        workflow.parent.mkdir(parents=True, exist_ok=True)
        workflow.write_text("name: prohibited\n", encoding="utf-8")
        errors = validate_defaults(fixture)
        self.assertTrue(
            any("hosted GitHub workflow is prohibited" in error for error in errors),
            errors,
        )

    def test_mirrored_rule_is_rejected(self) -> None:
        temporary, fixture = copy_fixture()
        self.addCleanup(temporary.cleanup)
        path = fixture / "CHATGPT_PROJECT_INSTRUCTIONS.md"
        path.write_text(
            path.read_text(encoding="utf-8") + "\nSKILLS_INDEX.md\n",
            encoding="utf-8",
        )
        errors = validate_defaults(fixture)
        self.assertTrue(any("mirrors central policy" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
