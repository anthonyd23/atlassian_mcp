import pytest
from mcp_server.common.validation import (
    validate_issue_key,
    validate_project_key,
    validate_page_id,
    validate_space_key,
    validate_repo_slug,
    validate_pr_id,
    validate_non_empty
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
