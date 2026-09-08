# Contributing

These conventions apply to repositories under xw7qwq. Read the target repository's README, CONTRIBUTING file, and relevant development documentation first; project-specific technical requirements take precedence.

## Language

Use English for documentation, Issues, pull requests, and commit messages. Preserve the original language of archived source material and imported records when it is part of their provenance.

## Branches and commits

- `main` contains verified work. Start manual changes from the latest `main` on a short-lived branch, such as `feat/submission-filter`, `fix/date-boundary`, `docs/api-guide`, or `chore/ci`.
- Keep each branch and PR focused on one problem. Start commit titles with `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`, or `build(deps):`, followed by a concrete description of the change.
- Do not commit secrets, login cookies, local configuration, or build artifacts that do not belong in the repository. Do not rewrite shared branch history.
- See the [maintenance conventions](docs/maintenance.md) for retaining `gh-pages`, dedicated documentation sources, and data synchronization branches. Branch age or inactivity alone is not a reason to delete a branch.

## Pull requests

Use the PR title to describe the final change. Explain the problem, resulting behavior, and validation in the description. Include screenshots for interface changes. Update the relevant documentation when changing public APIs, deployment, data formats, or configuration.

Before merging:

1. Read the complete diff, existing discussion, and the target repository's check results.
2. Run the required tests and builds; resolve failures before proceeding. For documentation-only changes, run the applicable documentation checks.
3. When the base branch changes, update the branch and rerun checks. Resolve conflicts and outstanding review discussions.
4. Confirm that unrelated work is excluded. For dependency updates, also review release notes, runtime requirements, and lockfiles.

Use **Squash and merge** by default for short-lived feature, fix, documentation, and dependency PRs, so each main-branch commit represents one reversible change. Merge commits are allowed when synchronizing long-lived branches to preserve ancestry; do not repeatedly squash those branches. Delete completed short-lived source branches after merging. Retain unmerged branches with unique content.

A repository with a single maintainer does not require approval from another person when that is impractical. It still requires a PR, passing required checks, and resolved review discussions. Apply the same validation process to Dependabot updates; bot authorship alone is not a reason to merge.

## Reporting issues

Open an Issue in the relevant project with reproduction steps, environment details, actual results, and expected results. Redact sensitive information from logs and screenshots. Feature requests should explain the use case and desired behavior; a complete implementation proposal is not required.

Each repository's existing license applies. These guidelines do not grant a license to otherwise unlicensed code or platform data.
