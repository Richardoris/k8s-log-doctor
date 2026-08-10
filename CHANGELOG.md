# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [0.2.0] - 2026-08-11

### Added
- **`--json` 结构化输出参数**：新增 `--json` 命令行参数，输出包含 `checks`、`status`、`error_message`、`summary` 四个字段的结构化 JSON
- **摘要统计**：`--json` 输出的 `summary` 字段包含 `total_checks`、`issues_count`、`severity_breakdown`（按等级统计各严重程度的数量）
- **状态字段**：`status` 字段取值 `ok`（无问题）、`issues_found`（发现 CRITICAL/HIGH 问题）、`error`（工具出错）
- **错误信息字段**：`error_message` 在工具出错时提供具体错误描述，正常时为 `null`
- **CI 友好退出码**：统一退出码规范（0=无问题, 1=发现问题, 2=工具错误）
- **单元测试**：新增 `tests/` 目录，包含 21 个 pytest 测试用例，覆盖 JSON 输出、退出码、向后兼容性
- **README 文档更新**：新增 `--json` 使用说明、退出码章节、CI 集成示例（GitHub Actions、GitLab CI）

### Changed
- **退出码逻辑简化**：从基于严重程度分级（0=low/none, 1=high, 2=critical）改为 CI 友好的统一标准（0=无 CRITICAL/HIGH, 1=有 CRITICAL/HIGH, 2=工具错误）
- **版本号**：从 0.1.0 升级到 0.2.0

### Backward Compatibility
- `-o json`（旧版 JSON 输出）保持不变，仍输出数组格式
- `-o text`（文本输出）行为不变
- 所有原有命令行参数保持兼容

## [0.1.0] - Initial Release

### Added
- 初始版本发布
- 支持 10 种 K8s 常见错误模式识别
- 支持文件、kubectl、标准输入三种输入方式
- 支持 text 和 json（`-o json`）两种输出格式
- 严重程度分级（CRITICAL/HIGH/MEDIUM/LOW/INFO）
- 修复建议功能
