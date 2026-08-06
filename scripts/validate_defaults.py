#!/usr/bin/env python3
"""Validate the minimal organization defaults."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = (
    "CHATGPT_PROJECT_INSTRUCTIONS.md",
    "CONTRIBUTING.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/bug.yml",
    ".github/ISSUE_TEMPLATE/feature.yml",
    "scripts/validate_defaults.py",
    "tests/test_validate_defaults.py",
)

REQUIRED_BOOTSTRAP_CONCEPTS = (
    "Repository: Bjs-Projects/REPOSITORY-NAME",
    "using-superpowers",
    "Bjs-Projects/docs/WORKFLOW.md",
    "sole Bjs-specific policy",
)

REQUIRED_PR_HEADINGS = {
    "requested result",
    "repository and refs",
    "change summary",
    "verification evidence",
    "delivery",
    "limitations",
}

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

HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
FORM_NAME_RE = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)
FORM_ID_RE = re.compile(r"^\s+id:\s*([A-Za-z0-9_-]+)\s*$", re.MULTILINE)


def read_text(root: Path, relative: str, errors: list[str]) -> str:
    path = root / relative
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"{relative}: cannot read: {exc}")
        return ""

    if text and not text.endswith("\n"):
        errors.append(f"{relative}: missing final newline")
    for line_number, line in enumerate(text.splitlines(), 1):
        if line.rstrip() != line:
            errors.append(f"{relative}:{line_number}: trailing whitespace")
    return text


def reject_mirrors(name: str, text: str, errors: list[str]) -> None:
    for snippet in MIRRORED_RULES:
        if snippet in text:
            errors.append(f"{name}: mirrors central policy: {snippet}")


def validate_pull_request_template(root: Path, errors: list[str]) -> None:
    github_root = root / ".github"
    templates = sorted(
        path
        for path in github_root.rglob("*")
        if path.is_file() and path.name.lower() == "pull_request_template.md"
    )
    if len(templates) > 1:
        names = ", ".join(path.relative_to(root).as_posix() for path in templates)
        errors.append(f"multiple pull request templates: {names}")

    canonical = root / ".github/PULL_REQUEST_TEMPLATE.md"
    if not canonical.is_file():
        return

    text = read_text(root, ".github/PULL_REQUEST_TEMPLATE.md", errors)
    headings = [heading.strip().lower() for heading in HEADING_RE.findall(text)]
    missing = sorted(REQUIRED_PR_HEADINGS - set(headings))
    for heading in missing:
        errors.append(f"pull request template: missing heading: {heading}")
    for heading, count in Counter(headings).items():
        if heading in REQUIRED_PR_HEADINGS and count > 1:
            errors.append(f"pull request template: duplicate heading: {heading}")
    reject_mirrors("pull request template", text, errors)


def issue_form_purpose(name: str) -> str:
    normalized = name.strip().lower()
    if normalized.startswith("bug"):
        return "bug"
    if normalized.startswith("feature"):
        return "feature"
    return normalized


def validate_issue_forms(root: Path, errors: list[str]) -> None:
    forms_root = root / ".github/ISSUE_TEMPLATE"
    form_paths = sorted(
        path
        for path in forms_root.glob("*.yml")
        if path.is_file() and path.name != "config.yml"
    )

    names: Counter[str] = Counter()
    purposes: Counter[str] = Counter()
    for path in form_paths:
        relative = path.relative_to(root).as_posix()
        text = read_text(root, relative, errors)
        match = FORM_NAME_RE.search(text)
        if match is None or not match.group(1).strip():
            errors.append(f"{relative}: missing issue form name")
            continue

        name = match.group(1).strip().lower()
        purpose = issue_form_purpose(name)
        names[name] += 1
        purposes[purpose] += 1

        ids = FORM_ID_RE.findall(text)
        for field_id, count in Counter(ids).items():
            if count > 1:
                errors.append(f"{relative}: duplicate field id: {field_id}")

    for name, count in names.items():
        if count > 1:
            errors.append(f"duplicate issue form name: {name}")
    for purpose, count in purposes.items():
        if count > 1:
            errors.append(f"duplicate issue form purpose: {purpose}")
    for purpose in ("bug", "feature"):
        if purposes[purpose] != 1:
            errors.append(f"issue forms: expected exactly one {purpose} form")


def validate_defaults(root: Path = ROOT) -> list[str]:
    root = root.resolve()
    errors: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (root / relative).is_file():
            errors.append(f"missing required path: {relative}")

    workflow_root = root / ".github/workflows"
    if workflow_root.exists():
        for path in sorted(item for item in workflow_root.rglob("*") if item.is_file()):
            errors.append(
                f"hosted GitHub workflow is prohibited: {path.relative_to(root)}"
            )

    bootstrap = read_text(root, "CHATGPT_PROJECT_INSTRUCTIONS.md", errors)
    contributing = read_text(root, "CONTRIBUTING.md", errors)
    read_text(root, "scripts/validate_defaults.py", errors)
    read_text(root, "tests/test_validate_defaults.py", errors)

    for concept in REQUIRED_BOOTSTRAP_CONCEPTS:
        if concept not in bootstrap:
            errors.append(f"project instruction bootstrap: missing concept: {concept}")

    superpowers_position = bootstrap.find("using-superpowers")
    workflow_position = bootstrap.find("Bjs-Projects/docs/WORKFLOW.md")
    if (
        superpowers_position < 0
        or workflow_position < 0
        or superpowers_position >= workflow_position
    ):
        errors.append(
            "project instruction bootstrap: using-superpowers must precede the central workflow read"
        )

    if "Bjs-Projects/docs/WORKFLOW.md" not in contributing:
        errors.append("CONTRIBUTING.md: missing central workflow pointer")

    reject_mirrors("project instruction bootstrap", bootstrap, errors)
    reject_mirrors("CONTRIBUTING.md", contributing, errors)
    validate_pull_request_template(root, errors)
    validate_issue_forms(root, errors)

    return sorted(set(errors))


def main() -> int:
    errors = validate_defaults(ROOT)
    if errors:
        print("Organization defaults validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Organization defaults validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
