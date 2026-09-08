"""Read-only audit of the public repository policy in config/repositories.json.

Requires Python 3.10+ and an authenticated GitHub CLI. Every request is a GET to
github.com. No settings, branches, or pull requests are changed. The default full
scope includes merge settings; public scope explicitly omits those settings.
Exit codes: 0 = compliant, 1 = policy drift, 2 = incomplete audit / invalid input.
"""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import quote


ROOT = Path(__file__).resolve().parent.parent
ACTIONS_APP_ID = 15368
PAGE_SIZE = 100
MAX_PAGES = 10
MERGE_SETTINGS = {"delete_branch_on_merge": True, "allow_update_branch": True,
                  "squash_merge_commit_title": "PR_TITLE", "squash_merge_commit_message": "BLANK"}


class AuditError(Exception):
    """An audit cannot determine the requested state."""


class GitHubClient:
    """Bounded, GET-only gh client; injectable in offline tests."""

    def get(self, endpoint):
        environment = os.environ.copy()
        # A user's gh debugging preference must not expose HTTP authorization.
        environment.pop("GH_DEBUG", None)
        try:
            result = subprocess.run(
                ["gh", "api", "--hostname", "github.com", "--method", "GET",
                 "-H", "Accept: application/vnd.github+json",
                 "-H", "X-GitHub-Api-Version: 2022-11-28", endpoint],
                capture_output=True, text=True, timeout=30, env=environment,
                check=False,
            )
        except FileNotFoundError as error:
            raise AuditError("GitHub CLI (gh) is not installed") from error
        except subprocess.TimeoutExpired as error:
            raise AuditError(f"GET {endpoint}: timed out after 30 seconds") from error
        if result.returncode:
            # Do not echo arbitrary CLI output, which may include credentials.
            status = re.search(r"HTTP (\d{3})", result.stderr)
            detail = f"HTTP {status.group(1)}" if status else "gh request failed"
            raise AuditError(
                f"GET {endpoint}: {detail}; check gh authentication, network, "
                "API rate limits, and repository access"
            )
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as error:
            raise AuditError(f"GET {endpoint}: response is not valid JSON") from error

    def list(self, endpoint):
        items = []
        separator = "&" if "?" in endpoint else "?"
        for page in range(1, MAX_PAGES + 1):
            data = self.get(f"{endpoint}{separator}per_page={PAGE_SIZE}&page={page}")
            if not isinstance(data, list):
                raise AuditError(f"GET {endpoint}: expected a JSON array")
            items.extend(data)
            if len(data) < PAGE_SIZE:
                return items
        raise AuditError(
            f"GET {endpoint}: pagination exceeded {MAX_PAGES} pages; "
            "audit is incomplete"
        )


def validate_config(config):
    """Reject ambiguous or incomplete policy before making any requests."""
    if not isinstance(config, dict):
        raise AuditError("configuration must be a JSON object")
    organization = config.get("organization")
    if not isinstance(organization, str) or not re.fullmatch(r"[A-Za-z0-9-]+", organization):
        raise AuditError("configuration.organization must be a GitHub organization name")
    repositories = config.get("repositories")
    if not isinstance(repositories, list) or not 1 <= len(repositories) <= 50:
        raise AuditError("configuration.repositories must contain 1 to 50 repositories")
    names = set()
    for repo in repositories:
        if not isinstance(repo, dict):
            raise AuditError("each repository policy must be an object")
        name = repo.get("name")
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", name) or name in names:
            raise AuditError("repository names must be valid and unique")
        names.add(name)
        if not isinstance(repo.get("website"), str):
            raise AuditError(f"{name}: website must be a string (empty is allowed)")
        for field in ("topics", "required_checks"):
            validate_string_list(repo.get(field), f"{name}.{field}")
        default_branch = repo.get("default_branch")
        if not isinstance(default_branch, str) or not default_branch:
            raise AuditError(f"{name}: default_branch must be a nonempty string")
        branches = repo.get("branches")
        if not isinstance(branches, list) or not 1 <= len(branches) <= 50:
            raise AuditError(f"{name}: branches must contain 1 to 50 entries")
        branch_names = set()
        for branch in branches:
            if not isinstance(branch, dict):
                raise AuditError(f"{name}: each branch policy must be an object")
            branch_name = branch.get("name")
            if (not isinstance(branch_name, str) or not branch_name
                    or any(ord(char) < 32 for char in branch_name)
                    or branch_name in branch_names):
                raise AuditError(f"{name}: branch names must be nonempty and unique")
            branch_names.add(branch_name)
            if not isinstance(branch.get("prevent_force_push"), bool):
                raise AuditError(f"{name}/{branch_name}: prevent_force_push must be boolean")
            if "required_checks" in branch:
                validate_string_list(branch["required_checks"], f"{name}/{branch_name}.required_checks")
        if default_branch not in branch_names:
            raise AuditError(f"{name}: default branch must be included in branches")


def validate_string_list(value, label):
    if (not isinstance(value, list)
            or any(not isinstance(item, str) or not item for item in value)
            or len(value) != len(set(value))):
        raise AuditError(f"{label} must be an array of unique nonempty strings")


def audit_repository(organization, policy, client, scope):
    name = policy["name"]
    endpoint = f"repos/{quote(organization, safe='')}/{quote(name, safe='')}"
    report = {"name": name, "status": "passed", "violations": [], "errors": [],
              "branches": [], "temporary_branches": [], "open_pull_requests": []}

    def require(field, expected, actual):
        if actual != expected:
            report["violations"].append({"field": field, "expected": expected, "actual": actual})

    try:
        metadata = client.get(endpoint)
        if not isinstance(metadata, dict):
            raise AuditError(f"GET {endpoint}: expected a repository object")
        require("homepage", policy["website"], metadata.get("homepage") or "")
        require("default_branch", policy["default_branch"], metadata.get("default_branch"))
        missing_topics = sorted(set(policy["topics"]) - set(metadata.get("topics") or []))
        if missing_topics:
            report["violations"].append({"field": "topics", "missing": missing_topics})
        for field, expected in (MERGE_SETTINGS.items() if scope == "full" else []):
            if field not in metadata:
                report["errors"].append(
                    f"GET {endpoint}: {field} is not visible to this credential; "
                    "use a credential authorized to read repository settings"
                )
            else:
                require(field, expected, metadata[field])
    except AuditError as error:
        report["errors"].append(str(error))

    try:
        branches = client.list(f"{endpoint}/branches")
        if any(not isinstance(branch, dict) or not isinstance(branch.get("name"), str)
               for branch in branches):
            raise AuditError(f"GET {endpoint}/branches: invalid branch entry")
        by_name = {branch["name"]: branch for branch in branches}
        expected_names = {branch["name"] for branch in policy["branches"]}
        report["temporary_branches"] = sorted(set(by_name) - expected_names)
        for branch in policy["branches"]:
            branch_name = branch["name"]
            state = by_name.get(branch_name)
            require(f"branches.{branch_name}.exists", True, state is not None)
            if state is None:
                continue
            require(f"branches.{branch_name}.protected", True, state.get("protected"))
            branch_report = {"name": branch_name, "protected": state.get("protected")}
            report["branches"].append(branch_report)
            try:
                # This endpoint only returns active rules that actually apply,
                # including inherited rules. Disabled/evaluate rules do not count.
                rules = client.list(f"{endpoint}/rules/branches/{quote(branch_name, safe='')}")
                if any(not isinstance(rule, dict) or not isinstance(rule.get("type"), str)
                       or not isinstance(rule.get("parameters", {}), dict) for rule in rules):
                    raise AuditError(f"{name}/{branch_name}: invalid effective rule entry")
                types = {rule["type"] for rule in rules}
                branch_report["effective_rules"] = sorted(types)
                require(f"branches.{branch_name}.prevent_deletion", True, "deletion" in types)
                if branch["prevent_force_push"]:
                    require(f"branches.{branch_name}.prevent_force_push", True, "non_fast_forward" in types)
                checks = branch.get("required_checks", policy["required_checks"]
                                    if branch_name == policy["default_branch"] else [])
                if branch_name == policy["default_branch"] or "required_checks" in branch:
                    require(f"branches.{branch_name}.pull_request", True, "pull_request" in types)
                    resolved = any(rule["type"] == "pull_request" and
                                   rule.get("parameters", {}).get("required_review_thread_resolution") is True
                                   for rule in rules)
                    require(f"branches.{branch_name}.resolve_conversations", True, resolved)
                if checks:
                    status_rules = [rule.get("parameters", {}) for rule in rules
                                    if rule["type"] == "required_status_checks"]
                    if any(not isinstance(rule.get("required_status_checks"), list)
                           or any(not isinstance(check, dict) for check in rule["required_status_checks"])
                           for rule in status_rules):
                        raise AuditError(f"{name}/{branch_name}: invalid required status check entry")
                    strict = any(rule.get("strict_required_status_checks_policy") is True
                                 and rule.get("required_status_checks") for rule in status_rules)
                    require(f"branches.{branch_name}.strict_status_checks", True, bool(strict))
                    configured = {(check.get("context"), check.get("integration_id"))
                                  for rule in status_rules for check in rule.get("required_status_checks", [])}
                    for check in checks:
                        require(f"branches.{branch_name}.required_checks.{check}",
                                {"context": check, "integration_id": ACTIONS_APP_ID},
                                {"context": check, "integration_id": ACTIONS_APP_ID}
                                if (check, ACTIONS_APP_ID) in configured else None)
            except AuditError as error:
                report["errors"].append(str(error))
    except AuditError as error:
        report["errors"].append(str(error))

    try:
        pulls = client.list(f"{endpoint}/pulls?state=open")
        report["open_pull_requests"] = [
            {"number": pull["number"], "url": pull["html_url"],
             "base": pull["base"]["ref"], "head": pull["head"]["ref"],
             "draft": pull.get("draft", False)} for pull in pulls
        ]
    except (KeyError, TypeError) as error:
        report["errors"].append(f"GET {endpoint}/pulls: invalid pull request entry")
    except AuditError as error:
        report["errors"].append(str(error))

    report["status"] = "error" if report["errors"] else "drift" if report["violations"] else "passed"
    return report


def audit_organization(config, client=None, scope="full"):
    validate_config(config)
    if scope not in ("full", "public"):
        raise AuditError("scope must be full or public")
    client = client or GitHubClient()
    repositories = [audit_repository(config["organization"], policy, client, scope)
                    for policy in config["repositories"]]
    errors = sum(len(repo["errors"]) for repo in repositories)
    violations = sum(len(repo["violations"]) for repo in repositories)
    return {
        "organization": config["organization"],
        "scope": scope,
        "not_checked": list(MERGE_SETTINGS) if scope == "public" else [],
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "error" if errors else "drift" if violations else "passed",
        "summary": {"repositories": len(repositories), "violations": violations, "errors": errors,
                    "temporary_branches": sum(len(repo["temporary_branches"]) for repo in repositories),
                    "open_pull_requests": sum(len(repo["open_pull_requests"]) for repo in repositories)},
        "repositories": repositories,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config/repositories.json")
    parser.add_argument("--scope", choices=("full", "public"), default="full",
                        help="full also checks merge settings; public explicitly omits them")
    parser.add_argument("--output", type=Path, help="also write the JSON report to this local file")
    args = parser.parse_args(argv)
    try:
        config = json.loads(args.config.read_text(encoding="utf-8"))
        report = audit_organization(config, scope=args.scope)
    except (AuditError, OSError, json.JSONDecodeError) as error:
        report = {"scope": args.scope, "status": "error", "errors": [str(error)]}
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        try:
            args.output.write_text(rendered, encoding="utf-8")
        except OSError:
            report["status"] = "error"
            report.setdefault("errors", []).append("could not write the requested local report file")
            rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(rendered, end="")
    return {"passed": 0, "drift": 1, "error": 2}[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
