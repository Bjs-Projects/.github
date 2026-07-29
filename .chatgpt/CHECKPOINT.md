---
schema: bjs-checkpoint-v4
repository: Bjs-Projects/.github
workstream_id: 20260729T194600Z-organization-workflow-contract-b4d2
branch: work/20260729T194600Z-organization-workflow-contract-b4d2
base_main_sha: 3f2d070928b471ed4a29255495d07c692e6d0cb5
workspace_kind: capability-orchestrated
workspace_id: chatgpt-web-20260729T194600Z-b4d2
execution_surface: chatgpt-web
local_checkout: unavailable
worktree_path: not-applicable
started_utc: 2026-07-29T19:46:00Z
updated_utc: 2026-07-29T20:24:00Z
status: validation
---

# Task

## Requested outcome

Provide organization-owned workflow defaults that enforce immutable Action pins, real Git LFS object checks, file-size guards, least privilege, and clear capability evidence without modifying project repositories.

## Acceptance criteria

- [x] Workflow template exists with pinned Actions and real LFS object validation.
- [x] Template metadata is valid by the committed validator contract.
- [x] Organization defaults repository validates its own templates through a hosted workflow.
- [x] Pull request template captures capabilities used, unavailable checks, LFS pointer/object evidence, and releases.
- [ ] Hosted validation passes on the final branch head.

## Editable scope

- Changed: `Bjs-Projects/.github`.
- Read-only references: `Bjs-Projects/docs` and registered project workflows.

## Capabilities used

- GitHub connector: exact repository reads, branch creation, SHA-safe writes, readback, pull request and CI operations.
- GitHub Actions: hosted validation of the public organization defaults repository.
- Web: current official GitHub workflow-template metadata and availability requirements, Action releases, and Git LFS release/hash verification.
- Local authenticated checkout and linked worktree: unavailable; not claimed.

## Completed

- Added `workflow-templates/bjs-repository-contract.yml` with immutable Action pins, verified Git LFS 3.7.1 installation, LFS pull/hash/fsck, submodules, regular-blob size gate, and Action-pin gate.
- Added matching workflow-template metadata.
- Added `scripts/validate_defaults.py` and `.github/workflows/defaults-check.yml`.
- Expanded the inherited pull request template with capability and evidence sections.

## Pending

- Open pull request, inspect hosted validation, fix failures, remove this branch-only checkpoint, merge, and verify final `main`.

## Recovery notes

- Continue only on this exact branch after reading the checkpoint and branch head.
- Do not modify project repositories.
