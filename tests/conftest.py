"""
pytest fixtures for k8s-log-doctor tests.
"""
import os
import tempfile
import pytest


@pytest.fixture
def sample_log_with_issues(tmp_path):
    """Create a sample log file containing CRITICAL and HIGH severity issues."""
    log_content = """2024-01-15 10:23:45 OOMKilled: container exceeded memory limit
2024-01-15 10:23:46 Back-off restarting failed container
2024-01-15 10:23:47 CrashLoopBackOff: restarting failed container
2024-01-15 10:23:48 ErrImagePull: failed to pull image nginx:latest
2024-01-15 10:23:49 Liveness probe failed: connection refused
2024-01-15 10:23:50 normal log line
2024-01-15 10:23:51 another normal log line
"""
    log_file = tmp_path / "issues.log"
    log_file.write_text(log_content, encoding="utf-8")
    return str(log_file)


@pytest.fixture
def sample_log_no_issues(tmp_path):
    """Create a sample log file containing only normal (no CRITICAL/HIGH) entries."""
    log_content = """2024-01-15 10:23:45 Application started successfully
2024-01-15 10:23:46 Server listening on port 8080
2024-01-15 10:23:47 Health check passed
2024-01-15 10:23:48 Processing request from 192.168.1.1
2024-01-15 10:23:49 Request completed in 15ms
"""
    log_file = tmp_path / "clean.log"
    log_file.write_text(log_content, encoding="utf-8")
    return str(log_file)


@pytest.fixture
def sample_log_medium_only(tmp_path):
    """Create a sample log file containing only MEDIUM severity issues (no CRITICAL/HIGH)."""
    log_content = """2024-01-15 10:23:45 missing config value for database.host
2024-01-15 10:23:46 request timed out after 30 seconds
2024-01-15 10:23:47 normal log line
"""
    log_file = tmp_path / "medium.log"
    log_file.write_text(log_content, encoding="utf-8")
    return str(log_file)


@pytest.fixture
def script_path():
    """Return the path to k8s_log_doctor.py."""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "k8s_log_doctor.py")
