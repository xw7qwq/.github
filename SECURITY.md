# Security policy

This is the default security policy for xw7qwq. A repository's own `SECURITY.md` takes precedence. Investigation and fixes target the current default branch; include the affected version or commit in your report.

## Private reporting

Keep valid tokens, cookies, personal status snapshots, and sensitive exploit details out of public issues. GitHub Private Vulnerability Reporting is enabled for every repository:

| Affected project | Private report |
| --- | --- |
| Organization configuration and workflows | [.github](https://github.com/xw7qwq/.github/security/advisories/new) |
| Competitive programming archive, reader, and documentation | [codeflare](https://github.com/xw7qwq/codeflare/security/advisories/new) |
| Solving activity synchronization and dashboard | [ojflare](https://github.com/xw7qwq/ojflare/security/advisories/new) |
| macOS collection and status API | [macflare](https://github.com/xw7qwq/macflare/security/advisories/new) |
| Blog and build pipeline | [nfuwari](https://github.com/xw7qwq/nfuwari/security/advisories/new) |

Include the trigger, a minimal reproduction, impact, affected deployment setup, and suggested mitigations. Use test credentials and synthetic data, and test only environments you own or are authorized to assess. Accessing real user data is unnecessary to demonstrate impact.

If private reporting is unavailable, open an issue without sensitive details asking the maintainer to restore the channel. GitHub's form requires sign-in; repository administrators can create a draft security advisory directly.

## Investigation and fixes

Maintainers verify impact and discuss fixes and disclosure in the private report. No fixed response time, bounty, or maintenance period for historical versions is promised. For ordinary usage questions, see [Support](https://github.com/xw7qwq/.github/blob/main/SUPPORT.md).

If credentials have leaked, revoke or rotate them at the relevant service first, then address copies in code, build logs, and history. Deleting the latest file does not invalidate old credentials. Third parties may also have retained public status or static data. Follow project-specific instructions for stopping collection, updating tokens, and retaining data.

Assess dependency alerts against parent dependencies, version constraints, and input paths. The blog's known remaining items are documented in the [dependency review](https://github.com/xw7qwq/nfuwari/blob/main/docs/DEPENDENCY-REVIEW.md). A limited impact assessment does not mean an unpatched dependency has no defects.
