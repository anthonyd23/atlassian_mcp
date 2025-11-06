import pytest
from mcp_server.common.validation import (
    validate_issue_key,
    validate_project_key,
    validate_page_id,
    validate_space_key,
    validate_repo_slug,
    validate_pr_id,
    validate_non_empty,
    validate_account_id,
    validate_transition_id,
    validate_board_id,
    validate_sprint_id,
    validate_version_number,
    validate_time_spent,
    validate_priority,
    validate_label,
    validate_cql,
    validate_jql,
    validate_username,
    validate_url,
    validate_pr_state,
    validate_events_list
)


def test_validate_issue_key_valid():
    valid, error = validate_issue_key("TEST-123")
    assert valid is True
    assert error == ""


def test_validate_issue_key_invalid_format():
    valid, error = validate_issue_key("test-123")
    assert valid is False
    assert "Invalid issue_key format" in error


def test_validate_issue_key_empty():
    valid, error = validate_issue_key("")
    assert valid is False
    assert "required" in error


def test_validate_project_key_valid():
    valid, error = validate_project_key("TEST")
    assert valid is True
    assert error == ""


def test_validate_project_key_invalid():
    valid, error = validate_project_key("test")
    assert valid is False
    assert "Invalid project_key format" in error


def test_validate_page_id_valid():
    valid, error = validate_page_id("12345")
    assert valid is True
    assert error == ""


def test_validate_page_id_invalid():
    valid, error = validate_page_id("abc")
    assert valid is False
    assert "must be numeric" in error


def test_validate_space_key_valid():
    valid, error = validate_space_key("TEST")
    assert valid is True
    assert error == ""


def test_validate_space_key_invalid():
    valid, error = validate_space_key("test-space")
    assert valid is False
    assert "Invalid space_key format" in error


def test_validate_repo_slug_valid():
    valid, error = validate_repo_slug("test-repo")
    assert valid is True
    assert error == ""


def test_validate_repo_slug_invalid():
    valid, error = validate_repo_slug("TEST_REPO")
    assert valid is False
    assert "Invalid repo_slug format" in error


def test_validate_pr_id_valid():
    valid, error = validate_pr_id(123)
    assert valid is True
    assert error == ""


def test_validate_pr_id_invalid():
    valid, error = validate_pr_id(-1)
    assert valid is False
    assert "must be a positive integer" in error


def test_validate_pr_id_none():
    valid, error = validate_pr_id(None)
    assert valid is False
    assert "required" in error


def test_validate_non_empty_valid():
    valid, error = validate_non_empty("value", "field")
    assert valid is True
    assert error == ""


def test_validate_non_empty_invalid():
    valid, error = validate_non_empty("", "field")
    assert valid is False
    assert "field is required" in error


def test_validate_account_id_valid():
    valid, error = validate_account_id("5b10ac8d82e05b22cc7d4ef5")
    assert valid is True
    assert error == ""


def test_validate_account_id_empty():
    valid, error = validate_account_id("")
    assert valid is False
    assert "required" in error


def test_validate_transition_id_valid():
    valid, error = validate_transition_id("21")
    assert valid is True
    assert error == ""


def test_validate_transition_id_invalid():
    valid, error = validate_transition_id("abc")
    assert valid is False
    assert "must be numeric" in error


def test_validate_board_id_valid():
    valid, error = validate_board_id(123)
    assert valid is True
    assert error == ""


def test_validate_board_id_invalid():
    valid, error = validate_board_id(-1)
    assert valid is False
    assert "must be a positive integer" in error


def test_validate_sprint_id_valid():
    valid, error = validate_sprint_id(456)
    assert valid is True
    assert error == ""


def test_validate_sprint_id_invalid():
    valid, error = validate_sprint_id(0)
    assert valid is False
    assert "must be a positive integer" in error


def test_validate_version_number_valid():
    valid, error = validate_version_number(5)
    assert valid is True
    assert error == ""


def test_validate_version_number_invalid():
    valid, error = validate_version_number(None)
    assert valid is False
    assert "required" in error


def test_validate_time_spent_valid():
    valid, error = validate_time_spent("2h")
    assert valid is True
    assert error == ""
    
    valid, error = validate_time_spent("1d 4h")
    assert valid is True
    assert error == ""


def test_validate_time_spent_invalid():
    valid, error = validate_time_spent("2 hours")
    assert valid is False
    assert "Invalid time_spent format" in error


def test_validate_priority_valid():
    valid, error = validate_priority("High")
    assert valid is True
    assert error == ""


def test_validate_priority_empty():
    valid, error = validate_priority("")
    assert valid is False
    assert "required" in error


def test_validate_label_valid():
    valid, error = validate_label("bug-fix")
    assert valid is True
    assert error == ""


def test_validate_label_invalid():
    valid, error = validate_label("bug fix")
    assert valid is False
    assert "alphanumeric" in error


def test_validate_cql_valid():
    valid, error = validate_cql("type=page AND space=DEV")
    assert valid is True
    assert error == ""


def test_validate_cql_empty():
    valid, error = validate_cql("")
    assert valid is False
    assert "required" in error


def test_validate_jql_valid():
    valid, error = validate_jql("project=TEST AND status=Open")
    assert valid is True
    assert error == ""


def test_validate_jql_empty():
    valid, error = validate_jql("")
    assert valid is False
    assert "required" in error


def test_validate_username_valid():
    valid, error = validate_username("john.doe")
    assert valid is True
    assert error == ""


def test_validate_username_empty():
    valid, error = validate_username("")
    assert valid is False
    assert "required" in error


def test_validate_url_valid():
    valid, error = validate_url("https://example.com/webhook")
    assert valid is True
    assert error == ""


def test_validate_url_invalid():
    valid, error = validate_url("ftp://example.com")
    assert valid is False
    assert "must start with http" in error


def test_validate_pr_state_valid():
    valid, error = validate_pr_state("OPEN")
    assert valid is True
    assert error == ""


def test_validate_pr_state_invalid():
    valid, error = validate_pr_state("INVALID")
    assert valid is False
    assert "must be one of" in error


def test_validate_events_list_valid():
    valid, error = validate_events_list(["repo:push", "pr:created"])
    assert valid is True
    assert error == ""


def test_validate_events_list_invalid():
    valid, error = validate_events_list([])
    assert valid is False
    assert "non-empty list" in error
