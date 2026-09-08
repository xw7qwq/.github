# Maintainer guide

[Contributing](../CONTRIBUTING.md) covers the everyday PR process, and [repository maintenance](maintenance.md) records current branches and checks. Use this guide when adding a project, changing deployment, or investigating configuration drift.

## Add a repository

1. Document its purpose, runtime requirements, validation commands, deployed URL, and feedback channel. Determine its license from the code's provenance and authors' permissions.
2. Add the tests or builds the project needs, with stable check names for every PR targeting the default branch. Introduce service accounts, private credentials, and scheduled tasks only when needed.
3. Protect the default branch against force pushes and deletion. Require PRs, resolved review discussions, and checks. Keep required approvals at 0 for a single maintainer. Confirm that checks actually run before making them mandatory.
4. Use dedicated permanent branches when automated data or published artifacts must be written to Git. Allow the normal writes they need without granting blanket bypass access to the default branch.
5. Enable private vulnerability reporting and verify that shared support, security, and conduct files are inherited, or provide project-specific files.
6. Register the name, website, topics, permanent branches, and required checks in [repositories.json](../config/repositories.json). Update the [organization profile](../profile/README.md) and [support navigation](../SUPPORT.md).

## Check repository settings

Local checks require Python 3.11+ and an authenticated GitHub CLI:

```sh
python3 scripts/check_repository.py
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/audit_organization.py
```

You can also manually run **Organization audit (public)** from this repository's Actions tab. It runs `python3 scripts/audit_organization.py --scope public` to check publicly visible websites, topics, branches, and effective rules. Cross-repository token permissions limit access to merge settings, so those settings are explicitly listed in `not_checked`. Use the local command above with an existing administrator GitHub CLI login to include them. No new token or secret is needed.

Both scopes are read-only: they do not change permissions, branches, or content, run on a schedule, or fail because normal development has temporary branches or open PRs.

The tool checks registered repository URLs and topics, merge settings, permanent branches, and GitHub's effective rules. `full` means all checks defined by this tool. It is not a code review, production availability check, or security audit. Verify ruleset bypass actors, classic branch protection details, member permissions, and private security settings separately in GitHub. API and permission errors are reported separately and never treated as passing checks.

## Rename, migrate, and deploy

- After renaming a repository, update source links, READMEs, OpenAPI documents, site navigation, badges, installation commands, and workflow URLs. Avoid relying on redirects indefinitely.
- When renaming a check, update the workflow, branch rules, registry, and maintenance documentation together. Verify the gate with a real PR afterward.
- When changing a domain, check repository About settings, Pages or Worker configuration, DNS and proxies, site canonical URLs, and public API documentation. Metadata checks do not replace TLS or live verification.
- Complete applicable checks before deployment. Afterward, verify the run, affected routes, and data version. On failure, retain the latest successful data or artifacts and use logs to distinguish code defects, upstream failures, and temporary platform issues.
- Revert shared source through a revert PR. Use the hosting platform's existing deployment history for production rollbacks. Keep compatible readers or document recovery steps when migrating data formats.

## Archive a project

Update the README and support links to explain its maintenance status or replacement. Resolve open PRs and unmerged work, then check domains, publishing jobs, and active clients. Archive only after confirming that further writes are unnecessary. Preserve repositories and permanent branches.
