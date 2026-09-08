"""Offline regression cases for policy drift, effective rules, and API failures."""

from copy import deepcopy
import os
import subprocess
import unittest
from unittest.mock import patch

from audit_organization import AuditError, GitHubClient, audit_organization


CONFIG = {
    "organization": "example-org",
    "repositories": [{
        "name": "example", "website": "https://example.org", "topics": ["tools"],
        "default_branch": "main", "required_checks": ["build", "test"],
        "branches": [
            {"name": "main", "purpose": "source", "prevent_force_push": True},
            {"name": "docs/guide", "purpose": "documentation", "prevent_force_push": True,
             "required_checks": ["docs"]},
            {"name": "gh-pages", "purpose": "deployment", "prevent_force_push": False},
        ],
    }],
}
BASE = "repos/example-org/example"
FIXTURE = {
    BASE: {
        "homepage": "https://example.org", "topics": ["tools", "extra-topic"],
        "default_branch": "main", "delete_branch_on_merge": True,
        "allow_update_branch": True, "squash_merge_commit_title": "PR_TITLE",
        "squash_merge_commit_message": "BLANK",
    },
    BASE + "/branches": [
        {"name": "main", "protected": True},
        {"name": "docs/guide", "protected": True},
        {"name": "gh-pages", "protected": True},
        {"name": "fix/work-in-progress", "protected": False},
    ],
    BASE + "/rules/branches/main": [
        {"type": "deletion", "ruleset_source_type": "Organization"},
        {"type": "non_fast_forward", "ruleset_source_type": "Repository"},
        {"type": "pull_request", "parameters": {"required_review_thread_resolution": True}},
        {"type": "required_status_checks", "parameters": {
            "strict_required_status_checks_policy": True,
            "required_status_checks": [
                {"context": "build", "integration_id": 15368},
                {"context": "test", "integration_id": 15368},
            ],
        }},
    ],
    BASE + "/rules/branches/docs%2Fguide": [
        {"type": "deletion"}, {"type": "non_fast_forward"},
        {"type": "pull_request", "parameters": {"required_review_thread_resolution": True}},
        {"type": "required_status_checks", "parameters": {
            "strict_required_status_checks_policy": True,
            "required_status_checks": [{"context": "docs", "integration_id": 15368}],
        }},
    ],
    BASE + "/rules/branches/gh-pages": [{"type": "deletion"}],
    BASE + "/pulls?state=open": [
        {"number": 12, "html_url": "https://github.com/example-org/example/pull/12",
         "base": {"ref": "main"}, "head": {"ref": "fix/work-in-progress"}, "draft": True},
    ],
    # A ruleset's configured contents cannot substitute for its effective rules.
    BASE + "/rulesets": [{"id": 1, "enforcement": "disabled"}],
    BASE + "/rulesets/1": {"enforcement": "disabled", "rules": [{"type": "pull_request"}]},
}


class FixtureClient:
    def __init__(self, fixture=None):
        self.fixture = deepcopy(FIXTURE if fixture is None else fixture)
        self.calls = []

    def get(self, endpoint):
        self.calls.append(endpoint)
        result = self.fixture[endpoint]
        if isinstance(result, Exception):
            raise result
        return deepcopy(result)

    list = get


class OrganizationAuditTests(unittest.TestCase):
    def setUp(self):
        self.client = FixtureClient()

    def run_audit(self, scope="full"):
        return audit_organization(deepcopy(CONFIG), self.client, scope=scope)

    def fields(self, report):
        return {item["field"] for item in report["repositories"][0]["violations"]}

    def test_active_work_and_extra_topics_are_not_drift(self):
        report = self.run_audit()
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["summary"]["temporary_branches"], 1)
        self.assertEqual(report["summary"]["open_pull_requests"], 1)
        self.assertEqual(report["repositories"][0]["temporary_branches"], ["fix/work-in-progress"])

    def test_missing_required_check_is_drift(self):
        self.client.fixture[BASE + "/rules/branches/main"][-1]["parameters"]["required_status_checks"].pop()
        self.assertIn("branches.main.required_checks.test", self.fields(self.run_audit()))

    def test_same_check_name_from_wrong_app_is_drift(self):
        self.client.fixture[BASE + "/rules/branches/main"][-1]["parameters"]["required_status_checks"][0]["integration_id"] = 999
        self.assertIn("branches.main.required_checks.build", self.fields(self.run_audit()))

    def test_checks_must_require_an_updated_branch(self):
        self.client.fixture[BASE + "/rules/branches/main"][-1]["parameters"]["strict_required_status_checks_policy"] = False
        self.assertIn("branches.main.strict_status_checks", self.fields(self.run_audit()))

    def test_inactive_rulesets_do_not_satisfy_required_rules(self):
        self.client.fixture[BASE + "/rules/branches/main"] = []
        report = self.run_audit()
        self.assertEqual(report["status"], "drift")
        self.assertIn("branches.main.pull_request", self.fields(report))
        self.assertFalse(any("/rulesets" in endpoint for endpoint in self.client.calls))

    def test_inherited_effective_rules_count(self):
        report = self.run_audit()
        self.assertNotIn("branches.main.prevent_deletion", self.fields(report))

    def test_missing_long_term_branch_is_drift(self):
        self.client.fixture[BASE + "/branches"].pop(2)
        self.assertIn("branches.gh-pages.exists", self.fields(self.run_audit()))
        self.assertNotIn(BASE + "/rules/branches/gh-pages", self.client.calls)

    def test_branch_protected_flag_does_not_replace_concrete_rules(self):
        self.client.fixture[BASE + "/rules/branches/main"].pop(0)
        self.assertIn("branches.main.prevent_deletion", self.fields(self.run_audit()))

    def test_docs_branch_has_its_own_checks_and_requires_resolved_review(self):
        rules = self.client.fixture[BASE + "/rules/branches/docs%2Fguide"]
        rules[2]["parameters"]["required_review_thread_resolution"] = False
        rules[3]["parameters"]["required_status_checks"] = [{"context": "build", "integration_id": 15368}]
        fields = self.fields(self.run_audit())
        self.assertIn("branches.docs/guide.resolve_conversations", fields)
        self.assertIn("branches.docs/guide.required_checks.docs", fields)

    def test_merge_setting_drift_is_detected(self):
        self.client.fixture[BASE]["squash_merge_commit_message"] = "PR_BODY"
        self.assertIn("squash_merge_commit_message", self.fields(self.run_audit()))

    def test_public_scope_declares_omitted_merge_settings(self):
        for field in ("delete_branch_on_merge", "allow_update_branch",
                      "squash_merge_commit_title", "squash_merge_commit_message"):
            del self.client.fixture[BASE][field]
        report = self.run_audit(scope="public")
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["scope"], "public")
        self.assertEqual(len(report["not_checked"]), 4)
        self.assertIn("delete_branch_on_merge", report["not_checked"])
        self.assertIn(BASE + "/rules/branches/main", self.client.calls)

    def test_full_scope_cannot_pass_with_invisible_settings(self):
        del self.client.fixture[BASE]["delete_branch_on_merge"]
        report = self.run_audit()
        self.assertEqual(report["status"], "error")
        self.assertIn("delete_branch_on_merge is not visible", report["repositories"][0]["errors"][0])

    def test_api_failure_is_incomplete_audit_not_policy_drift(self):
        self.client.fixture[BASE + "/rules/branches/main"] = AuditError("GET rules/main: HTTP 403")
        report = self.run_audit()
        self.assertEqual(report["status"], "error")
        self.assertEqual(report["summary"]["violations"], 0)
        self.assertIn("HTTP 403", report["repositories"][0]["errors"][0])
        self.assertEqual(report["summary"]["open_pull_requests"], 1)

    def test_invalid_policy_makes_no_api_requests(self):
        config = deepcopy(CONFIG)
        config["repositories"][0]["branches"].pop(0)
        with self.assertRaisesRegex(AuditError, "default branch must be included"):
            audit_organization(config, self.client)
        self.assertEqual(self.client.calls, [])


class GitHubClientTests(unittest.TestCase):
    def test_get_method_is_explicit_and_debug_is_removed(self):
        result = subprocess.CompletedProcess([], 0, stdout="{}", stderr="")
        with patch.dict(os.environ, {"GH_DEBUG": "api"}), patch("subprocess.run", return_value=result) as run:
            self.assertEqual(GitHubClient().get(BASE), {})
        arguments = run.call_args.args[0]
        self.assertEqual(arguments[arguments.index("--method") + 1], "GET")
        self.assertEqual(arguments[arguments.index("--hostname") + 1], "github.com")
        self.assertNotIn("GH_DEBUG", run.call_args.kwargs["env"])

    def test_api_error_does_not_echo_credentials(self):
        result = subprocess.CompletedProcess([], 1, stdout="", stderr="HTTP 403; Bearer secret-test-value")
        with patch("subprocess.run", return_value=result), self.assertRaises(AuditError) as raised:
            GitHubClient().get(BASE)
        self.assertIn("HTTP 403", str(raised.exception))
        self.assertNotIn("secret-test-value", str(raised.exception))

    def test_pagination_includes_later_pages(self):
        client = GitHubClient()
        with patch.object(client, "get", side_effect=[[{"name": "one"}] * 100, [{"name": "last"}]]) as get:
            result = client.list(BASE + "/branches")
        self.assertEqual(len(result), 101)
        self.assertEqual(result[-1]["name"], "last")
        self.assertTrue(get.call_args.args[0].endswith("page=2"))

    def test_pagination_limit_is_an_error_not_silent_truncation(self):
        client = GitHubClient()
        with patch("audit_organization.MAX_PAGES", 2), patch.object(client, "get", return_value=[{}] * 100) as get:
            with self.assertRaisesRegex(AuditError, "pagination exceeded 2 pages"):
                client.list(BASE + "/branches")
        self.assertEqual(get.call_count, 2)


if __name__ == "__main__":
    unittest.main()
