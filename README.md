# K8s Log Doctor 🔍

智能 Kubernetes 日志诊断工具 - 自动识别常见错误模式，给出修复建议

## ✨ 功能特性

- 🎯 **智能模式识别** - 自动识别 10+ 种常见 K8s 错误模式
- 📊 **严重程度分级** - CRITICAL/HIGH/MEDIUM/LOW 四级分类
- 💡 **修复建议** - 针对每个问题提供具体的解决方案
- 🔌 **多种输入方式** - 支持文件、kubectl、标准输入
- 📦 **开箱即用** - 零配置，单文件即可运行
- 🎨 **多格式输出** - 支持文本和 JSON 格式

## 🚀 快速开始

### 安装

```bash
# 方式1: 直接下载运行
curl -O https://raw.githubusercontent.com/yourusername/k8s-log-doctor/main/k8s_log_doctor.py
chmod +x k8s_log_doctor.py

# 方式2: pip 安装
pip install k8s-log-doctor
```

### 使用示例

```bash
# 1. 分析 Pod 日志
k8s-log-doctor -p my-pod -n my-namespace

# 2. 分析日志文件
k8s-log-doctor -f /var/log/pod.log

# 3. 从标准输入读取
kubectl logs my-pod | k8s-log-doctor

# 4. 输出 JSON 格式（便于集成）
k8s-log-doctor -f pod.log -o json

# 5. 指定容器（多容器 Pod）
k8s-log-doctor -p my-pod -c my-container
```

## 📋 支持的错误模式

| 模式 | 严重程度 | 说明 |
|------|---------|------|
| OOMKilled | 🔴 CRITICAL | 容器内存不足被杀死 |
| CrashLoopBackOff | 🔴 CRITICAL | 容器反复崩溃重启 |
| ImagePullError | 🟠 HIGH | 镜像拉取失败 |
| LivenessProbeFailed | 🟠 HIGH | 健康检查失败 |
| DiskPressure | 🔴 CRITICAL | 磁盘空间不足 |
| NetworkError | 🟠 HIGH | 网络连接问题 |
| PermissionDenied | 🟠 HIGH | 权限不足 |
| ConfigError | 🟡 MEDIUM | 配置错误 |
| Timeout | 🟡 MEDIUM | 请求超时 |
| PanicError | 🔴 CRITICAL | 程序崩溃 |

## 📊 输出示例

```
============================================================
🔍 K8s Log Doctor 诊断报告
============================================================

发现 2 个问题:

🔴 [1] OOMKilled
   严重程度: CRITICAL
   问题描述: 容器因内存不足被杀死
   置信度: 95%

   💡 建议:
      1. 增加Pod的memory limit
      2. 检查应用是否有内存泄漏
      3. 优化应用内存使用
      4. 考虑使用HPA自动扩缩容

   📝 相关日志 (前3行):
      2024-01-15 10:23:45 OOMKilled: container exceeded memory limit

🟠 [2] LivenessProbeFailed
   严重程度: HIGH
   问题描述: 健康检查失败
   置信度: 85%

   💡 建议:
      1. 检查应用是否正常启动
      2. 调整probe的timeout和period
      3. 验证健康检查端点
      4. 增加initialDelaySeconds

============================================================
```

## 🔧 高级用法

### 与 CI/CD 集成

```yaml
# GitHub Actions 示例
- name: Analyze logs
  run: |
    kubectl logs my-pod | k8s-log-doctor -o json > report.json
    
- name: Check for critical issues
  run: |
    k8s-log-doctor -f logs.txt
    if [ $? -eq 2 ]; then
      echo "Critical issues found!"
      exit 1
    fi
```

### 批量分析

```bash
# 分析多个 Pod
for pod in $(kubectl get pods -o name); do
  echo "Analyzing $pod..."
  k8s-log-doctor -p ${pod#pod/} -n production
done
```

## 💰 Pro 版本

免费版包含基础诊断功能，Pro 版本提供：

- 🤖 **AI 智能分析** - 基于大模型的深度诊断
- 📈 **趋势分析** - 历史日志趋势对比
- 🔔 **告警集成** - 自动发送告警到钉钉/飞书/企业微信
- 📊 **可视化报告** - 生成 HTML 诊断报告
- 🎯 **自定义规则** - 支持自定义错误模式
- 📞 **技术支持** - 专属技术支持群

**价格**: ¥29/月 或 ¥299/年

[👉 升级到 Pro 版本](https://your-payment-link.com)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👨‍💻 作者

由艾玛（AI助手）开发，为 K8s 运维人员而生 💪
