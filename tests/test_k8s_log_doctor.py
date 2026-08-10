"""
Unit tests for k8s-log-doctor.

Covers:
- --json structured output (valid JSON, structure, summary statistics)
- Exit codes (0 = no issues, 1 = issues found, 2 = tool error)
- Backward compatibility (text output, -o json)
"""
import json
import subprocess
import sys
import os
import pytest


def run_script(script_path, args, stdin_data=None):
    """Run the k8s_log_doctor.py script as a subprocess and return the result."""
    cmd = [sys.executable, script_path] + args
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        input=stdin_data,
        timeout=30,
    )
    return proc


# ===========================================================================
# --json structured output tests
# ===========================================================================


class TestJsonOutput:
    """Tests for the --json structured output."""

    def test_json_output_valid(self, script_path, sample_log_with_issues):
        """验证 --json 输出是合法 JSON"""
        result = run_script(script_path, ["-f", sample_log_with_issues, "--json"])
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            pytest.fail(f"--json output is not valid JSON: {result.stdout!r}")
        assert isinstance(data, dict)

    def test_json_output_structure(self, script_path, sample_log_with_issues):
        """验证 JSON 包含 checks/status/error_message/summary 必需字段"""
        result = run_script(script_path, ["-f", sample_log_with_issues, "--json"])
        data = json.loads(result.stdout)

        # Required top-level keys
        for key in ("checks", "status", "error_message", "summary"):
            assert key in data, f"Missing required key: {key}"

        # checks must be a list
        assert isinstance(data["checks"], list)

        # Each check must have required sub-fields
        required_check_keys = {"pattern_name", "severity", "description", "suggestion", "matched_lines", "confidence"}
        for check in data["checks"]:
            assert isinstance(check, dict)
            assert required_check_keys.issubset(check.keys()), (
                f"Check missing keys: {required_check_keys - set(check.keys())}"
            )

        # status must be one of the valid values
        assert data["status"] in ("ok", "issues_found", "error")

        # error_message: null when no error
        if data["status"] != "error":
            assert data["error_message"] is None

        # summary must have required sub-keys
        required_summary_keys = {"total_checks", "issues_count", "severity_breakdown"}
        assert required_summary_keys.issubset(data["summary"].keys()), (
            f"Summary missing keys: {required_summary_keys - set(data['summary'].keys())}"
        )

    def test_json_summary_statistics(self, script_path, sample_log_with_issues):
        """验证 summary 统计数据正确"""
        result = run_script(script_path, ["-f", sample_log_with_issues, "--json"])
        data = json.loads(result.stdout)

        checks = data["checks"]
        summary = data["summary"]

        # total_checks should match the number of checks
        assert summary["total_checks"] == len(checks)
        # issues_count should match the number of checks
        assert summary["issues_count"] == len(checks)

        # severity_breakdown should be a dict with all severity levels
        breakdown = summary["severity_breakdown"]
        for level in ("critical", "high", "medium", "low", "info"):
            assert level in breakdown, f"Missing severity level in breakdown: {level}"
            assert isinstance(breakdown[level], int)

        # Sum of breakdown values should equal total_checks
        total_from_breakdown = sum(breakdown.values())
        assert total_from_breakdown == summary["total_checks"]

        # Verify counts match actual checks
        actual_counts = {}
        for check in checks:
            sev = check["severity"]
            actual_counts[sev] = actual_counts.get(sev, 0) + 1
        for level, count in actual_counts.items():
            assert breakdown[level] == count, (
                f"Breakdown for {level}: expected {count}, got {breakdown[level]}"
            )

    def test_json_status_issues_found(self, script_path, sample_log_with_issues):
        """有严重问题时 status 应为 issues_found"""
        result = run_script(script_path, ["-f", sample_log_with_issues, "--json"])
        data = json.loads(result.stdout)
        assert data["status"] == "issues_found"

    def test_json_status_ok(self, script_path, sample_log_no_issues):
        """无问题时 status 应为 ok"""
        result = run_script(script_path, ["-f", sample_log_no_issues, "--json"])
        data = json.loads(result.stdout)
        assert data["status"] == "ok"

    def test_json_error_on_tool_error(self, script_path, tmp_path):
        """工具出错时 status 应为 error，error_message 有值"""
        nonexistent = str(tmp_path / "nonexistent.log")
        result = run_script(script_path, ["-f", nonexistent, "--json"])
        data = json.loads(result.stdout)
        assert data["status"] == "error"
        assert data["error_message"] is not None
        assert len(data["error_message"]) > 0


# ===========================================================================
# Exit code tests
# ===========================================================================


class TestExitCodes:
    """Tests for CI-friendly exit codes."""

    def test_exit_code_no_issues(self, script_path, sample_log_no_issues):
        """无严重问题时退出码为 0"""
        result = run_script(script_path, ["-f", sample_log_no_issues])
        assert result.returncode == 0, (
            f"Expected exit code 0 for no issues, got {result.returncode}. "
            f"stderr: {result.stderr}"
        )

    def test_exit_code_no_issues_medium_only(self, script_path, sample_log_medium_only):
        """仅有 MEDIUM 级别问题时退出码仍为 0（非 CRITICAL/HIGH）"""
        result = run_script(script_path, ["-f", sample_log_medium_only])
        assert result.returncode == 0, (
            f"Expected exit code 0 for medium-only issues, got {result.returncode}. "
            f"stderr: {result.stderr}"
        )

    def test_exit_code_issues_found(self, script_path, sample_log_with_issues):
        """有严重问题（CRITICAL/HIGH）时退出码为 1"""
        result = run_script(script_path, ["-f", sample_log_with_issues])
        assert result.returncode == 1, (
            f"Expected exit code 1 for severe issues, got {result.returncode}. "
            f"stderr: {result.stderr}"
        )

    def test_exit_code_tool_error(self, script_path, tmp_path):
        """工具错误（文件不存在）时退出码为 2"""
        nonexistent = str(tmp_path / "nonexistent.log")
        result = run_script(script_path, ["-f", nonexistent])
        assert result.returncode == 2, (
            f"Expected exit code 2 for tool error, got {result.returncode}. "
            f"stderr: {result.stderr}"
        )

    def test_exit_code_json_no_issues(self, script_path, sample_log_no_issues):
        """--json 模式下无问题时退出码为 0"""
        result = run_script(script_path, ["-f", sample_log_no_issues, "--json"])
        assert result.returncode == 0

    def test_exit_code_json_issues_found(self, script_path, sample_log_with_issues):
        """--json 模式下有严重问题时退出码为 1"""
        result = run_script(script_path, ["-f", sample_log_with_issues, "--json"])
        assert result.returncode == 1

    def test_exit_code_json_tool_error(self, script_path, tmp_path):
        """--json 模式下工具错误时退出码为 2"""
        nonexistent = str(tmp_path / "nonexistent.log")
        result = run_script(script_path, ["-f", nonexistent, "--json"])
        assert result.returncode == 2


# ===========================================================================
# Backward compatibility tests
# ===========================================================================


class TestBackwardCompatibility:
    """Tests ensuring existing functionality is preserved."""

    def test_backward_compat_text_output(self, script_path, sample_log_with_issues):
        """文本输出格式不受影响"""
        result = run_script(script_path, ["-f", sample_log_with_issues])
        output = result.stdout

        # Text output should contain the report header
        assert "K8s Log Doctor" in output
        # Should contain severity indicators
        assert any(emoji in output for emoji in ("🔴", "🟠", "🟡"))
        # Should contain pattern names found in the log
        assert "OOMKilled" in output or "CrashLoopBackOff" in output
        # Should contain suggestions
        assert "建议" in output or "💡" in output

    def test_backward_compat_text_output_clean(self, script_path, sample_log_no_issues):
        """无问题时文本输出应显示正常信息"""
        result = run_script(script_path, ["-f", sample_log_no_issues])
        assert "未发现明显问题" in result.stdout

    def test_backward_compat_o_json(self, script_path, sample_log_with_issues):
        """-o json 仍然正常工作"""
        result = run_script(script_path, ["-f", sample_log_with_issues, "-o", "json"])
        output = result.stdout

        # Should be valid JSON
        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            pytest.fail(f"-o json output is not valid JSON: {output!r}")

        # -o json outputs a list (legacy format), not the structured format
        assert isinstance(data, list), (
            "-o json should output a list (legacy format), not a dict"
        )

        # Each item should have the legacy keys
        for item in data:
            assert "pattern" in item
            assert "severity" in item
            assert "description" in item

    def test_backward_compat_o_json_clean(self, script_path, sample_log_no_issues):
        """-o json 无问题时输出空列表"""
        result = run_script(script_path, ["-f", sample_log_no_issues, "-o", "json"])
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) == 0

    def test_backward_compat_o_text(self, script_path, sample_log_with_issues):
        """-o text 显式指定时与默认行为一致"""
        result_text = run_script(script_path, ["-f", sample_log_with_issues, "-o", "text"])
        result_default = run_script(script_path, ["-f", sample_log_with_issues])
        assert result_text.stdout == result_default.stdout


# ===========================================================================
# Direct function unit tests
# ===========================================================================


class TestDirectFunctions:
    """Direct unit tests for internal functions."""

    def test_format_structured_json_has_all_fields(self):
        """format_structured_json 应包含所有必需字段"""
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))
        from k8s_log_doctor import format_structured_json_output, DiagnosisResult, Severity

        results = [
            DiagnosisResult(
                pattern_name="OOMKilled",
                severity=Severity.CRITICAL,
                description="容器因内存不足被杀死",
                suggestion="增加memory limit",
                matched_lines=["OOMKilled at line 1"],
                confidence=0.95,
            ),
            DiagnosisResult(
                pattern_name="ConfigError",
                severity=Severity.MEDIUM,
                description="配置错误",
                suggestion="检查ConfigMap",
                matched_lines=["config not found"],
                confidence=0.75,
            ),
        ]

        output = format_structured_json_output(results)
        data = json.loads(output)

        assert data["status"] == "issues_found"
        assert data["error_message"] is None
        assert data["summary"]["total_checks"] == 2
        assert data["summary"]["severity_breakdown"]["critical"] == 1
        assert data["summary"]["severity_breakdown"]["medium"] == 1

    def test_format_structured_json_error_mode(self):
        """format_structured_json 带 error_message 时 status 为 error"""
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))
        from k8s_log_doctor import format_structured_json_output

        output = format_structured_json_output([], error_message="File not found")
        data = json.loads(output)

        assert data["status"] == "error"
        assert data["error_message"] == "File not found"
        assert data["checks"] == []
        assert data["summary"]["total_checks"] == 0

    def test_has_severe_issues(self):
        """has_severe_issues 正确判断"""
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))
        from k8s_log_doctor import has_severe_issues, DiagnosisResult, Severity

        critical_results = [
            DiagnosisResult("OOM", Severity.CRITICAL, "", "", [], 0.9),
        ]
        medium_results = [
            DiagnosisResult("Config", Severity.MEDIUM, "", "", [], 0.7),
        ]
        empty_results = []

        assert has_severe_issues(critical_results) is True
        assert has_severe_issues(medium_results) is False
        assert has_severe_issues(empty_results) is False
