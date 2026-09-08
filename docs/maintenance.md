# Repository maintenance

Start with the [contribution guidelines](../CONTRIBUTING.md). This page records differences in checks and automation across repositories; update it when workflows or branch rules change.

## Default branch rules

Every repository uses `main` as its default branch. Deletion and force pushes are blocked. Human changes go through PRs with an up-to-date branch, passing required checks, and resolved review discussions. Single-maintainer repositories require 0 approvals from other people; review and validation still apply.

| Repository | Required checks | Local validation |
| --- | --- | --- |
| `.github` | `repository-check` | `python3 scripts/check_repository.py` and the offline audit tests |
| `codeflare` | `archive` | Run the offline archive tests and source integrity checks in its contribution guide |
| `ojflare` | `check` | `npm test`, `npm run build` |
| `macflare` | `worker`, `macos-agent` | Run the Worker, site, and macOS checks in its contribution guide |
| `nfuwari` | `Lint, check and build` | Use the specified Node and pnpm versions for lint, check, and build; verify post rendering after dependency updates |

GitHub Actions provides these checks. Review the Rules settings before renaming checks, adding path filters, or changing trigger branches so PRs do not wait for a check that will never run.

## Automated data updates

The daily `ojflare` sync reads code from `main` and the latest cache from `data/snapshots`. It writes updated `data/sources/` and `public/data/dashboard.json` to the data branch, then publishes the static site. The data branch stores snapshots and is not merged into `main`; data on `main` serves as a baseline for offline development.

Separate source and data branches let every `main` use the same PR and check requirements without a personal token or bot bypass actor. The data branch allows normal bot pushes while blocking deletion and force pushes. Review workflow write permissions and fixed data paths to keep source changes out of that branch.

## Permanent branches and cleanup

| Repository / branch | Purpose | Handling |
| --- | --- | --- |
| All repositories / `main` | Default source and configuration | Keep; block deletion and force pushes |
| `codeflare` / `docs/project-guide` | Dedicated documentation source and build workflow | Keep; target documentation PRs here and preserve merge ancestry when synchronizing with `main` |
| `codeflare` / `gh-pages` | Manually maintained website source and generated `docs/` | Keep; documentation publishing updates `docs/` automatically, while site changes follow this branch's README checks |
| `ojflare` / `data/snapshots` | Successful daily snapshots and request state | Keep; allow normal automated pushes, block deletion and force pushes, and do not merge into the default branch |
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
| nfuwari | Migrate Astro content collections and related dependency versions to address remaining alerts | Upgrade parent dependencies using the [dependency review](https://github.com/xw7qwq/nfuwari/blob/main/docs/DEPENDENCY-REVIEW.md). Verify posts, formulas, RSS, search, navigation, and image handling; reassess audit results and input paths |
| nfuwari | Restore the GitHub Pages origin certificate | Follow the [deployment guide](https://github.com/xw7qwq/nfuwari/blob/main/docs/DEPLOYMENT.md) to check domain validation and ESA origin settings. Confirm a valid origin certificate and public HTTPS; ESA currently serves the public site successfully |
