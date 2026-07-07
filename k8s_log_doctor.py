#!/usr/bin/env python3
"""
K8s Log Doctor - 智能Kubernetes日志诊断工具
自动识别常见错误模式，给出修复建议

作者: 艾玛（AI助手）
版本: 0.1.0
"""

import re
import sys
import json
import argparse
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """错误严重程度"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class DiagnosisResult:
    """诊断结果"""
    pattern_name: str
    severity: Severity
    description: str
    suggestion: str
    matched_lines: List[str]
    confidence: float  # 0-1


class ErrorPattern:
    """错误模式识别器"""
    
    PATTERNS = [
        {
            "name": "OOMKilled",
            "regex": r"OOMKilled|Out of memory|Cannot allocate memory|memory cgroup out of memory",
            "severity": Severity.CRITICAL,
            "description": "容器因内存不足被杀死",
            "suggestion": "1. 增加Pod的memory limit\n2. 检查应用是否有内存泄漏\n3. 优化应用内存使用\n4. 考虑使用HPA自动扩缩容",
            "confidence": 0.95
        },
        {
            "name": "CrashLoopBackOff",
            "regex": r"CrashLoopBackOff|Back-off restarting failed container",
            "severity": Severity.CRITICAL,
            "description": "容器反复崩溃重启",
            "suggestion": "1. 检查容器启动日志\n2. 验证配置和环境变量\n3. 检查依赖服务是否可用\n4. 确认镜像版本正确",
            "confidence": 0.95
        },
        {
            "name": "ImagePullError",
            "regex": r"ErrImagePull|ImagePullBackOff|failed to pull image|manifest unknown|not found",
            "severity": Severity.HIGH,
            "description": "镜像拉取失败",
            "suggestion": "1. 检查镜像名称和tag是否正确\n2. 验证imagePullSecrets配置\n3. 确认镜像仓库可访问\n4. 检查网络连接和代理设置",
            "confidence": 0.90
        },
        {
            "name": "LivenessProbeFailed",
            "regex": r"Liveness probe failed|Readiness probe failed|Health check failed",
            "severity": Severity.HIGH,
            "description": "健康检查失败",
            "suggestion": "1. 检查应用是否正常启动\n2. 调整probe的timeout和period\n3. 验证健康检查端点\n4. 增加initialDelaySeconds",
            "confidence": 0.85
        },
        {
            "name": "DiskPressure",
            "regex": r"DiskPressure|no space left on device|No disk space|disk full",
            "severity": Severity.CRITICAL,
            "description": "磁盘空间不足",
            "suggestion": "1. 清理无用的日志和临时文件\n2. 增加PV/PVC容量\n3. 配置日志轮转\n4. 检查emptyDir使用情况",
            "confidence": 0.90
        },
        {
            "name": "NetworkError",
            "regex": r"connection refused|connection timeout|network unreachable|DNS.*error|resolve.*failed",
            "severity": Severity.HIGH,
            "description": "网络连接问题",
            "suggestion": "1. 检查Service和Endpoint配置\n2. 验证NetworkPolicy规则\n3. 确认DNS配置正确\n4. 检查目标服务是否运行",
            "confidence": 0.80
        },
        {
            "name": "PermissionDenied",
            "regex": r"permission denied|forbidden|unauthorized|access denied|RBAC",
            "severity": Severity.HIGH,
            "description": "权限不足",
            "suggestion": "1. 检查ServiceAccount权限\n2. 验证RBAC配置\n3. 确认文件/目录权限\n4. 检查SecurityContext设置",
            "confidence": 0.85
        },
        {
            "name": "ConfigError",
            "regex": r"config.*not found|missing.*config|invalid.*config|configuration error",
            "severity": Severity.MEDIUM,
            "description": "配置错误",
            "suggestion": "1. 检查ConfigMap/Secret是否存在\n2. 验证环境变量配置\n3. 确认配置文件格式正确\n4. 检查挂载路径",
            "confidence": 0.75
        },
        {
            "name": "Timeout",
            "regex": r"timeout|timed out|deadline exceeded",
            "severity": Severity.MEDIUM,
            "description": "请求超时",
            "suggestion": "1. 检查下游服务响应时间\n2. 调整timeout配置\n3. 增加资源配额\n4. 优化慢查询",
            "confidence": 0.70
        },
        {
            "name": "PanicError",
            "regex": r"panic:|fatal error:|SIGSEGV|segmentation fault",
            "severity": Severity.CRITICAL,
            "description": "程序崩溃",
            "suggestion": "1. 检查代码bug\n2. 查看完整堆栈信息\n3. 验证依赖库版本\n4. 考虑降级版本",
            "confidence": 0.95
        }
    ]
    
    @classmethod
    def analyze(cls, logs: List[str]) -> List[DiagnosisResult]:
        """分析日志，返回诊断结果"""
        results = []
        logs_text = "\n".join(logs)
        
        for pattern in cls.PATTERNS:
            matches = re.findall(pattern["regex"], logs_text, re.IGNORECASE)
            if matches:
                # 找到匹配的行
                matched_lines = [
                    line for line in logs 
                    if re.search(pattern["regex"], line, re.IGNORECASE)
                ]
                
                results.append(DiagnosisResult(
                    pattern_name=pattern["name"],
                    severity=pattern["severity"],
                    description=pattern["description"],
                    suggestion=pattern["suggestion"],
                    matched_lines=matched_lines[:5],  # 最多显示5行
                    confidence=pattern["confidence"]
                ))
        
        # 按严重程度排序
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFO: 4
        }
        results.sort(key=lambda x: severity_order[x.severity])
        
        return results


class LogAnalyzer:
    """日志分析器"""
    
    def __init__(self):
        self.pattern_analyzer = ErrorPattern()
    
    def analyze_from_file(self, filepath: str) -> List[DiagnosisResult]:
        """从文件分析日志"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                logs = f.readlines()
            return self.pattern_analyzer.analyze(logs)
        except Exception as e:
            print(f"❌ 读取文件失败: {e}", file=sys.stderr)
            return []
    
    def analyze_from_stdin(self) -> List[DiagnosisResult]:
        """从标准输入分析日志"""
        logs = sys.stdin.readlines()
        return self.pattern_analyzer.analyze(logs)
    
    def analyze_from_kubectl(self, pod_name: str, namespace: str = "default", 
                             container: str = None, tail: int = 1000) -> List[DiagnosisResult]:
        """从kubectl获取日志并分析"""
        import subprocess
        
        cmd = ["kubectl", "logs", pod_name, "-n", namespace, f"--tail={tail}"]
        if container:
            cmd.extend(["-c", container])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print(f"❌ kubectl命令失败: {result.stderr}", file=sys.stderr)
                return []
            
            logs = result.stdout.splitlines()
            return self.pattern_analyzer.analyze(logs)
        except subprocess.TimeoutExpired:
            print("❌ kubectl命令超时", file=sys.stderr)
            return []
        except Exception as e:
            print(f"❌ 执行失败: {e}", file=sys.stderr)
            return []


def format_output(results: List[DiagnosisResult], output_format: str = "text") -> str:
    """格式化输出结果"""
    if output_format == "json":
        return json.dumps([
            {
                "pattern": r.pattern_name,
                "severity": r.severity.value,
                "description": r.description,
                "suggestion": r.suggestion,
                "matched_lines": r.matched_lines,
                "confidence": r.confidence
            }
            for r in results
        ], indent=2, ensure_ascii=False)
    
    # 文本格式
    if not results:
        return "✅ 未发现明显问题"
    
    output = []
    output.append("=" * 60)
    output.append("🔍 K8s Log Doctor 诊断报告")
    output.append("=" * 60)
    output.append(f"\n发现 {len(results)} 个问题:\n")
    
    severity_emoji = {
        Severity.CRITICAL: "🔴",
        Severity.HIGH: "🟠",
        Severity.MEDIUM: "🟡",
        Severity.LOW: "🟢",
        Severity.INFO: "ℹ️"
    }
    
    for i, result in enumerate(results, 1):
        emoji = severity_emoji[result.severity]
        output.append(f"{emoji} [{i}] {result.pattern_name}")
        output.append(f"   严重程度: {result.severity.value.upper()}")
        output.append(f"   问题描述: {result.description}")
        output.append(f"   置信度: {result.confidence*100:.0f}%")
        output.append(f"\n   💡 建议:")
        for line in result.suggestion.split('\n'):
            output.append(f"      {line}")
        
        if result.matched_lines:
            output.append(f"\n   📝 相关日志 (前{len(result.matched_lines)}行):")
            for line in result.matched_lines[:3]:
                output.append(f"      {line.strip()}")
        
        output.append("")
    
    output.append("=" * 60)
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="K8s Log Doctor - 智能Kubernetes日志诊断工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 分析日志文件
  k8s-log-doctor -f /var/log/pod.log
  
  # 分析kubectl日志
  k8s-log-doctor -p my-pod -n my-namespace
  
  # 从标准输入读取
  kubectl logs my-pod | k8s-log-doctor
  
  # 输出JSON格式
  k8s-log-doctor -f pod.log -o json
        """
    )
    
    parser.add_argument("-f", "--file", help="日志文件路径")
    parser.add_argument("-p", "--pod", help="Pod名称")
    parser.add_argument("-n", "--namespace", default="default", help="命名空间 (默认: default)")
    parser.add_argument("-c", "--container", help="容器名称 (多容器Pod时使用)")
    parser.add_argument("-t", "--tail", type=int, default=1000, help="获取最近N行日志 (默认: 1000)")
    parser.add_argument("-o", "--output", choices=["text", "json"], default="text", 
                       help="输出格式 (默认: text)")
    
    args = parser.parse_args()
    
    analyzer = LogAnalyzer()
    
    # 确定日志来源
    if args.file:
        results = analyzer.analyze_from_file(args.file)
    elif args.pod:
        results = analyzer.analyze_from_kubectl(
            args.pod, args.namespace, args.container, args.tail
        )
    elif not sys.stdin.isatty():
        results = analyzer.analyze_from_stdin()
    else:
        parser.print_help()
        sys.exit(1)
    
    # 输出结果
    print(format_output(results, args.output))
    
    # 根据严重程度返回退出码
    if any(r.severity == Severity.CRITICAL for r in results):
        sys.exit(2)
    elif any(r.severity == Severity.HIGH for r in results):
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
