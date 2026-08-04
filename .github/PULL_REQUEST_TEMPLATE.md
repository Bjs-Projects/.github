## Requested result

<!-- State the concrete repository or user-facing result. -->

## Delivery class

<!-- Choose exactly one: release-required or release-exempt. Explain the repository evidence for the classification. -->

## Repository and refs

<!-- Exact owner/repository, base SHA, branch, and current head SHA. -->

## Change summary

<!-- Summarize the complete change on this branch. -->

## Verification performed

<!-- List only commands, connector reads, builds, runtime checks, and inspections that actually ran against the current head. -->

## Required delivery

<!-- For release-exempt work, state "Integrated repository state". For release-required work, list the real expected artifacts and release verification. -->

## External prerequisite

<!-- Use "None" unless one user-owned secret, credential, license, destructive authorization, irreducible subjective input, or genuinely impossible output remains after all valid paths were exhausted. -->

## Final checklist

- [ ] The live `Bjs-Projects/docs/WORKFLOW.md` was used as the sole process authority.
- [ ] The repository root `AGENTS.md` matches the canonical project control file.
- [ ] Repository-local files were used only for project facts, exact commands, architecture, state, acceptance criteria, and release outputs.
- [ ] Matching pull requests and remote task branches were inspected before creating duplicate work.
- [ ] Every coherent change is committed and visible on the remote branch.
- [ ] The complete diff was reviewed against the intended base.
- [ ] Verification claims are limited to checks that actually ran.
- [ ] Unavailable optional checks were not treated as universal completion blockers.
- [ ] Release-required work includes the real consumer artifact and release evidence.
- [ ] Release-exempt work does not create a ceremonial tag or empty release.
- [ ] GitHub Actions was not run unless the current user request explicitly authorized it.
- [ ] No unauthorized Google Drive write, secret, cache, generated junk, continuation file, or unrelated change was added.
