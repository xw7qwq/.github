# xw7 organization configuration

This repository maintains the [xw7 organization profile](profile/README.md), shared community files, and verifiable maintenance settings. Project-specific requirements take precedence; repositories without custom files inherit the defaults here.

- [Contributing](CONTRIBUTING.md): branches, commits, reviews, validation, and merging.
- [Support](SUPPORT.md): project, documentation, and issue links by use case.
- [Security](SECURITY.md): private vulnerability reporting for each repository.
- [Code of conduct](CODE_OF_CONDUCT.md): collaboration and handling concerns.
- [Repository maintenance](docs/maintenance.md): branch protection, required checks, and permanent branches.
- [Maintainer guide](docs/maintainer-guide.md): onboarding projects, checking settings, migrations, and archiving.
- [Repository registry](config/repositories.json): expected websites, topics, branches, and checks.
- [Organization profile](https://github.com/xw7qwq): project navigation.

After editing this repository, run:

```sh
python3 scripts/check_repository.py
python3 -m unittest discover -s scripts -p 'test_*.py'
```

CI validates local Markdown links and SVG syntax, then runs the configuration audit's offline tests. Maintainers with an authenticated GitHub CLI can run `python3 scripts/audit_organization.py` to check all remote settings covered by the registry. The manual **Organization audit (public)** workflow checks publicly visible settings; see the [maintainer guide](docs/maintainer-guide.md) for its scope.
