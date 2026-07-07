# K8s Log Doctor 使用演示

## 场景 1: 分析日志文件

```bash
$ cat example.log
2024-01-15 10:23:45 INFO Starting application...
2024-01-15 10:23:46 INFO Loading configuration from /etc/app/config.yaml
2024-01-15 10:23:47 WARN High memory usage detected: 85%
2024-01-15 10:23:48 ERROR OOMKilled: container exceeded memory limit of 512Mi
2024-01-15 10:23:49 INFO Container restarting...
2024-01-15 10:23:50 ERROR CrashLoopBackOff: Back-off restarting failed container
2024-01-15 10:23:51 INFO Attempting to connect to database...
2024-01-15 10:23:52 ERROR connection refused: unable to reach db-service:5432
2024-01-15 10:23:53 WARN Liveness probe failed: HTTP probe failed with statuscode: 503
2024-01-15 10:23:54 ERROR permission denied: cannot access /var/data
2024-01-15 10:23:55 INFO Retrying in 5 seconds...
2024-01-15 10:23:56 ERROR timeout: request to upstream service timed out after 30s
2024-01-15 10:23:57 INFO Application shutdown complete

$ k8s-log-doctor -f example.log

============================================================
🔍 K8s Log Doctor 诊断报告
============================================================

发现 6 个问题:

🔴 [1] OOMKilled
   严重程度: CRITICAL
   问题描述: 容器因内存不足被杀死
   置信度: 95%

   💡 建议:
      1. 增加Pod的memory limit
      2. 检查应用是否有内存泄漏
      3. 优化应用内存使用
      4. 考虑使用HPA自动扩缩容

   📝 相关日志 (前1行):
      2024-01-15 10:23:48 ERROR OOMKilled: container exceeded memory limit of 512Mi

🔴 [2] CrashLoopBackOff
   严重程度: CRITICAL
   问题描述: 容器反复崩溃重启
   置信度: 95%

   💡 建议:
      1. 检查容器启动日志
      2. 验证配置和环境变量
      3. 检查依赖服务是否可用
      4. 确认镜像版本正确

   📝 相关日志 (前1行):
      2024-01-15 10:23:50 ERROR CrashLoopBackOff: Back-off restarting failed container

🟠 [3] LivenessProbeFailed
   严重程度: HIGH
   问题描述: 健康检查失败
   置信度: 85%

   💡 建议:
      1. 检查应用是否正常启动
      2. 调整probe的timeout和period
      3. 验证健康检查端点
      4. 增加initialDelaySeconds

   📝 相关日志 (前1行):
      2024-01-15 10:23:53 WARN Liveness probe failed: HTTP probe failed with statuscode: 503

🟠 [4] NetworkError
   严重程度: HIGH
   问题描述: 网络连接问题
   置信度: 80%

   💡 建议:
      1. 检查Service和Endpoint配置
      2. 验证NetworkPolicy规则
      3. 确认DNS配置正确
      4. 检查目标服务是否运行

   📝 相关日志 (前1行):
      2024-01-15 10:23:52 ERROR connection refused: unable to reach db-service:5432

🟠 [5] PermissionDenied
   严重程度: HIGH
   问题描述: 权限不足
   置信度: 85%

   💡 建议:
      1. 检查ServiceAccount权限
      2. 验证RBAC配置
      3. 确认文件/目录权限
      4. 检查SecurityContext设置

   📝 相关日志 (前1行):
      2024-01-15 10:23:54 ERROR permission denied: cannot access /var/data

🟡 [6] Timeout
   严重程度: MEDIUM
   问题描述: 请求超时
   置信度: 70%

   💡 建议:
      1. 检查下游服务响应时间
      2. 调整timeout配置
      3. 增加资源配额
      4. 优化慢查询

   📝 相关日志 (前1行):
      2024-01-15 10:23:56 ERROR timeout: request to upstream service timed out after 30s

============================================================

💡 需要更强大的诊断功能？升级到 Pro 版本！
   - AI 深度分析（基于大模型）
   - 历史趋势对比
   - 自动告警推送（钉钉/飞书/企微）
   - HTML可视化报告
   - 自定义规则引擎

   👉 了解详情: https://k8s-log-doctor.com/pro
   📧 技术咨询: ai-consult@example.com
============================================================
```

## 场景 2: 分析 K8s Pod 日志

```bash
# 直接分析 Pod 日志
$ k8s-log-doctor -p my-app-pod -n production

============================================================
🔍 K8s Log Doctor 诊断报告
============================================================

发现 2 个问题:

🔴 [1] ImagePullError
   严重程度: HIGH
   问题描述: 镜像拉取失败
   置信度: 90%

   💡 建议:
      1. 检查镜像名称和tag是否正确
      2. 验证imagePullSecrets配置
      3. 确认镜像仓库可访问
      4. 检查网络连接和代理设置

   📝 相关日志 (前1行):
      Failed to pull image "myregistry.com/myapp:v1.2.3": manifest unknown

🟠 [2] ConfigError
   严重程度: MEDIUM
   问题描述: 配置错误
   置信度: 75%

   💡 建议:
      1. 检查ConfigMap/Secret是否存在
      2. 验证环境变量配置
      3. 确认配置文件格式正确
      4. 检查挂载路径

   📝 相关日志 (前1行):
      config file not found: /etc/app/config.yaml

============================================================
```

## 场景 3: 管道输入

```bash
# 从 kubectl 输出直接分析
$ kubectl logs my-pod -n production --tail=500 | k8s-log-doctor

# 或者从其他日志源
$ tail -f /var/log/pods/production_my-app_*.log | k8s-log-doctor
```

## 场景 4: JSON 输出（便于集成）

```bash
$ k8s-log-doctor -f example.log -o json
[
  {
    "pattern": "OOMKilled",
    "severity": "critical",
    "description": "容器因内存不足被杀死",
    "suggestion": "1. 增加Pod的memory limit\n2. 检查应用是否有内存泄漏\n3. 优化应用内存使用\n4. 考虑使用HPA自动扩缩容",
    "matched_lines": [
      "2024-01-15 10:23:48 ERROR OOMKilled: container exceeded memory limit of 512Mi"
    ],
    "confidence": 0.95
  },
  {
    "pattern": "CrashLoopBackOff",
    "severity": "critical",
    "description": "容器反复崩溃重启",
    "suggestion": "1. 检查容器启动日志\n2. 验证配置和环境变量\n3. 检查依赖服务是否可用\n4. 确认镜像版本正确",
    "matched_lines": [
      "2024-01-15 10:23:50 ERROR CrashLoopBackOff: Back-off restarting failed container"
    ],
    "confidence": 0.95
  }
]
```

## 场景 5: CI/CD 集成

```yaml
# .github/workflows/log-check.yml
name: Log Analysis

on: [push]

jobs:
  analyze-logs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install k8s-log-doctor
        run: pip install k8s-log-doctor
      
      - name: Analyze logs
        run: |
          k8s-log-doctor -f logs/app.log -o json > report.json
          
      - name: Check for critical issues
        run: |
          k8s-log-doctor -f logs/app.log
          if [ $? -eq 2 ]; then
            echo "::error::Critical issues found in logs!"
            exit 1
          fi
```

## 场景 6: 批量分析

```bash
#!/bin/bash
# 批量分析所有 Pod

echo "开始批量分析..."

for pod in $(kubectl get pods -n production -o name); do
  pod_name=${pod#pod/}
  echo ""
  echo "=========================================="
  echo "分析 Pod: $pod_name"
  echo "=========================================="
  k8s-log-doctor -p "$pod_name" -n production
done

echo ""
echo "批量分析完成！"
```

运行效果：

```bash
$ ./batch-analyze.sh

开始批量分析...

==========================================
分析 Pod: my-app-7d8f9c6b5-x2k4m
==========================================

✅ 未发现明显问题

==========================================
分析 Pod: my-app-7d8f9c6b5-p9n3j
==========================================

============================================================
🔍 K8s Log Doctor 诊断报告
============================================================

发现 1 个问题:

🟠 [1] Timeout
   严重程度: MEDIUM
   问题描述: 请求超时
   置信度: 70%

   💡 建议:
      1. 检查下游服务响应时间
      2. 调整timeout配置
      3. 增加资源配额
      4. 优化慢查询

============================================================

==========================================
分析 Pod: my-app-7d8f9c6b5-q8m2k
==========================================

🔴 [1] OOMKilled
   严重程度: CRITICAL
   ...

批量分析完成！
```

---

**更多使用场景，欢迎探索！**

GitHub: https://github.com/Richardoris/k8s-log-doctor
