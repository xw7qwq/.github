# Repository maintenance

Start with the [contribution guidelines](../CONTRIBUTING.md). This page records differences in checks and automation across repositories; update it when workflows or branch rules change.

## Default branch rules

Every repository uses `main` as its default branch. Default branches normally block deletion and force pushes; the existing solutions/main exception is recorded below. Human changes go through PRs with an up-to-date branch, passing required checks, and resolved review discussions. Single-maintainer repositories require 0 approvals from other people; review and validation still apply.

| Repository | Required checks | Local validation |
| --- | --- | --- |
| `.github` | `check` | `python3 scripts/check_repository.py` and the offline audit tests |
| `solutions` | `check` | Run the offline archive tests and source integrity checks in its contribution guide |
| `oj` | `check` | `npm test`, `npm run build` |
| `macflare` | `check` (Worker and macOS jobs) | Run the Worker, site, and macOS checks in its contribution guide |
| `blog` | `check` | Use the specified Node and pnpm versions for lint, check, and build; verify post rendering after dependency updates |
| `panel` | `check` | `pnpm check` and a Wrangler dry run |
| `ui` | `check` | `pnpm check` |
| `health` | `check` | Run the release checks in its deployment guide |
| `ledger` | `check` | Run the jobs unit tests with synthetic example data |

At migration time, the main-branch rulesets in `solutions` were disabled. This migration retains that enforcement setting and renames their configured context to `check`; the documentation branch remains protected. The organization audit continues to report the default-branch exception.

GitHub Actions provides these checks. Review the Rules settings before renaming checks, adding path filters, or changing trigger branches so PRs do not wait for a check that will never run.

## Automated data updates

The daily `oj` sync reads code from `main` and the latest cache from `data/snapshots`. It writes updated `data/sources/` and `public/data/dashboard.json` to the data branch, then publishes the static site. The data branch stores snapshots and is not merged into `main`; data on `main` serves as a baseline for offline development.

Separate source and data branches let every `main` use the same PR and check requirements without a personal token or bot bypass actor. The data branch allows normal bot pushes while blocking deletion and force pushes. Review workflow write permissions and fixed data paths to keep source changes out of that branch.

## Permanent branches and cleanup

| Repository / branch | Purpose | Handling |
| --- | --- | --- |
| All repositories / `main` | Default source and configuration | Keep; block deletion and force pushes |
| `solutions` / `docs/project-guide` | Dedicated documentation source and build workflow | Keep; target documentation PRs here and preserve merge ancestry when synchronizing with `main` |
| `solutions` / `gh-pages` | Manually maintained website source and generated `docs/` | Keep; documentation publishing updates `docs/` automatically, while site changes follow this branch's README checks |
| `oj` / `data/snapshots` | Successful daily snapshots and request state | Keep; allow normal automated pushes, block deletion and force pushes, and do not merge into the default branch |
| Completed temporary branches | Features, fixes, documentation, dependencies, or one-time imports | Delete automatically after PR merge; before manual cleanup, check the remote SHA, full diff, and unmerged commits |

Keep `gh-pages` separate from `main`, and preserve deployment sources regardless of branch count. For closed, unmerged PRs, inspect the closure reason and source branch. A closed status alone does not mean the work can be discarded.

## Merge and publish

Temporary PRs use squash merges by default. The commit title comes from the PR title, and the PR body is not copied into the commit message. Details and validation evidence stay in the PR, preventing workflow control markers in the body from affecting post-merge CI. Regular merge commits are allowed when synchronizing permanent branches. Repositories enable automatic source branch deletion after merge and the update-branch button.

Check default-branch CI after merging. Projects using Pages must also have a successful latest deployment. Keep historical failures and superseded canceled runs; maintenance decisions should use valid checks and deployments for the current code. Preserve successful snapshots during temporary upstream failures and follow project guidance when deciding whether to rerun synchronization.

GitHub references: [Rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets), [default community health files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file).

## Registry and maintenance resources

[repositories.json](../config/repositories.json) records websites, topics, permanent branches, and check names. Update it when repository settings change, then follow the [maintainer guide](maintainer-guide.md) to run the applicable audit scope. See [Support](../SUPPORT.md) for usage questions and [Security](../SECURITY.md) for vulnerabilities.

## Known follow-up work

These items are documented in their projects and require a separate migration or external configuration change. They do not imply a current site outage or an unconfirmed deadline.

| Project | Follow-up | Completion criteria and reference |
| --- | --- | --- |
| blog | Migrate Astro content collections and related dependency versions to address remaining alerts | Upgrade parent dependencies using the [dependency review](https://github.com/xw7qwq/blog/blob/main/docs/DEPENDENCY-REVIEW.md). Verify posts, formulas, RSS, search, navigation, and image handling; reassess audit results and input paths |
| blog | Restore the GitHub Pages origin certificate | Follow the [deployment guide](https://github.com/xw7qwq/blog/blob/main/docs/DEPLOYMENT.md) to check domain validation and ESA origin settings. Confirm a valid origin certificate and public HTTPS; ESA currently serves the public site successfully |

## Naming, shared UI, and data boundaries

Use the purpose names `blog`, `oj`, `solutions`, `health`, `ledger`, `panel`, and `ui`. `macflare` keeps its agent name; `.github` holds organization-wide conventions. Repository renames do not rename production directories, environment variables, or public data hosts automatically.

`ui` owns shared tokens and Svelte components. Consumers pin a reviewed tag such as `v0.1.0`; never depend on a sibling checkout in published code. The panel is the common navigation destination. Public data endpoints remain compatible when old pages redirect.

The default-branch required CI context is `check`. It may aggregate multiple jobs, and it must fail if any dependency fails or is cancelled. Change workflows and GitHub branch rules together. The solutions documentation branch aggregates archive and documentation validation in the same `check` job.

Code licensed by this organization under MIT includes `panel`, `ui`, `ledger`, and `macflare`; existing third-party licenses still apply. `health` inherits upstream personal-use restrictions. `oj` and `solutions` do not gain a new blanket license: third-party statements, platform data, and imported code retain their owners' rights. Real health credentials and real ledger data never belong in public source repositories. `ledger-data` is private and uses a dedicated write-enabled deployment key; it is intentionally excluded from the public organization audit registry.
