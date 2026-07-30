#!/usr/bin/env python3
"""Validate the minimal ChatGPT Web organization bootstrap."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = (
    "CHATGPT_PROJECT_INSTRUCTIONS.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/workflows/defaults-check.yml",
    "scripts/validate_defaults.py",
)

REMOVED_PATHS = (
    "workflow-templates/bjs-repository-contract.yml",
    "workflow-templates/bjs-repository-contract.properties.json",
)

CHECKOUT_PIN = "de0fac2e4500dabe0009e67214ff5f5447ce83dd"
SETUP_PYTHON_PIN = "a309ff8b426b58ec0e2a45f0f869d46889d02405"
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
USES_RE = re.compile(r"^\s*uses:\s*([^\s#]+)(?:\s+#\s*(.+))?$", re.MULTILINE)
AUTOMATIC_EVENT_RE = re.compile(
    r"^\s{2}(?:push|pull_request|pull_request_target|schedule|workflow_run|repository_dispatch):\s*$",
    re.MULTILINE,
)
DANGEROUS_AUTOMATION_RE = re.compile(
    r"(?:contents:\s*write|\bgit\s+(?:commit|push|update-ref)\b|\bgh\s+pr\s+create\b|create-pull-request@)",
    re.IGNORECASE,
)

REQUIRED_PR_HEADINGS = (
    "## Requested result",
    "## Repository and refs",
    "## Current change summary",
    "## Validation completed",
    "## Unavailable validation",
    "## Remaining work",
    "## Exact next action",
    "## Final checklist",
)

REQUIRED_PR_CHECKS = (
    "The GitHub connector verified the exact repository",
    "Every coherent change is committed and visible on the remote branch.",
    "Sandbox validation claims are limited to files and tools that were actually present and used.",
    "GitHub Actions was not used for preservation",
    "Any zero-step or no-log Actions failure is classified as infrastructure or quota failure",
)

REQUIRED_BOOTSTRAP = (
    "Repository: Bjs-Projects/REPOSITORY-NAME",
    "the first repository operation must use the GitHub connector",
    "read the live Bjs-Projects/docs/WORKFLOW.md from main",
    "Never use another repository as temporary storage, runner, build host, or fallback.",
    "Run sandbox checks only when the complete required files and tools are actually present.",
    "GitHub Actions is manual-only supplementary validation.",
    "A zero-step, no-log Actions failure is infrastructure or quota failure",
)


def read_text(path: Path, errors: list[str]) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"{path.relative_to(ROOT)}: cannot read: {exc}")
        return ""
    if text and not text.endswith("\n"):
        errors.append(f"{path.relative_to(ROOT)}: missing final newline")
    for number, line in enumerate(text.splitlines(), 1):
        if line.rstrip() != line:
            errors.append(f"{path.relative_to(ROOT)}:{number}: trailing whitespace")
    return text


def validate_action_pins(path: Path, text: str, errors: list[str]) -> None:
    for spec, comment in USES_RE.findall(text):
        if spec.startswith("./"):
            continue
        if "@" not in spec:
            errors.append(f"{path.relative_to(ROOT)}: external Action missing ref: {spec}")
            continue
        action, ref = spec.rsplit("@", 1)
        if not FULL_SHA_RE.fullmatch(ref):
            errors.append(f"{path.relative_to(ROOT)}: mutable Action ref: {action}@{ref}")
        if not comment.strip():
            errors.append(f"{path.relative_to(ROOT)}: Action pin lacks release comment: {spec}")


def require_snippets(name: str, text: str, snippets: tuple[str, ...], errors: list[str]) -> None:
    for snippet in snippets:
        if snippet not in text:
            errors.append(f"{name}: missing required snippet: {snippet}")


def main() -> int:
    errors: list[str] = []

    for name in REQUIRED_PATHS:
        if not (ROOT / name).is_file():
            errors.append(f"missing required path: {name}")
    for name in REMOVED_PATHS:
        if (ROOT / name).exists():
            errors.append(f"obsolete workflow template remains: {name}")

    bootstrap = read_text(ROOT / "CHATGPT_PROJECT_INSTRUCTIONS.md", errors)
    pr_template = read_text(ROOT / ".github/PULL_REQUEST_TEMPLATE.md", errors)
    workflow_path = ROOT / ".github/workflows/defaults-check.yml"
    workflow = read_text(workflow_path, errors)
    read_text(Path(__file__), errors)

    require_snippets("project instruction bootstrap", bootstrap, REQUIRED_BOOTSTRAP, errors)
    for heading in REQUIRED_PR_HEADINGS:
        if heading not in pr_template:
            errors.append(f"pull request template missing heading: {heading}")
    for checklist_item in REQUIRED_PR_CHECKS:
        if checklist_item not in pr_template:
            errors.append(f"pull request template missing final check: {checklist_item}")

    require_snippets(
        "defaults-check workflow",
        workflow,
        (
            "name: Manual organization defaults check",
            "workflow_dispatch:",
            "permissions:\n  contents: read",
            "cancel-in-progress: true",
            f"uses: actions/checkout@{CHECKOUT_PIN} # v6.0.2",
            f"uses: actions/setup-python@{SETUP_PYTHON_PIN} # v6.2.0",
            "python -m py_compile scripts/validate_defaults.py",
            "python scripts/validate_defaults.py",
        ),
        errors,
    )
    if AUTOMATIC_EVENT_RE.search(workflow):
        errors.append("defaults-check workflow contains an automatic trigger")
    if DANGEROUS_AUTOMATION_RE.search(workflow):
        errors.append("defaults-check workflow contains source-mutating automation")
    validate_action_pins(workflow_path, workflow, errors)

    if errors:
        print("Organization defaults validation failed:", file=sys.stderr)
        for error in sorted(set(errors)):
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Organization defaults validation passed: minimal connector-first bootstrap, sandbox-realistic "
        "claims, manual-only read-only Actions, and no copied repository-contract workflow."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
