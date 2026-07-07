# 开源了一个 K8s 日志诊断工具，帮你 5 分钟定位问题

## 😩 你是否也遇到过这些场景？

- 凌晨 3 点被叫起来，Pod 又 CrashLoopBackOff 了
- 看着几百行日志，眼花缭乱找不到重点
- OOMKilled、ImagePullBackOff、LivenessProbeFailed... 每次都靠 Google 排查
- 新人接手 K8s，面对日志一脸懵逼

**我懂这种痛苦。**

作为一个运维老兵，我每天都在和 K8s 日志打交道。有时候一个简单的问题，翻日志就要花半小时。

## 🎯 所以我做了这个工具

**K8s Log Doctor** - 一个智能日志诊断工具，自动识别常见错误模式，给出修复建议。

### ✨ 核心能力

- 🔍 **10+ 种错误模式识别** - OOMKilled、CrashLoopBackOff、镜像拉取失败、健康检查失败...
- 📊 **严重程度分级** - CRITICAL/HIGH/MEDIUM/LOW 四级分类，优先处理关键问题
- 💡 **一键修复建议** - 不只是告诉你"错了"，还告诉你"怎么改"
- 🔌 **多种输入方式** - 文件、kubectl、管道，怎么用都方便
- 📦 **开箱即用** - 单文件，零配置，Python 3.7+ 即可运行

## 🚀 5 分钟上手

### 安装

```bash
# 方式1: 直接下载
curl -O https://raw.githubusercontent.com/Richardoris/k8s-log-doctor/main/k8s_log_doctor.py
chmod +x k8s_log_doctor.py

# 方式2: pip 安装（推荐）
pip install k8s-log-doctor
```

### 使用

```bash
# 分析 Pod 日志
k8s-log-doctor -p my-pod -n production

# 分析日志文件
k8s-log-doctor -f /var/log/pod.log

# 从标准输入读取
kubectl logs my-pod | k8s-log-doctor
```

### 效果展示

```
============================================================
🔍 K8s Log Doctor 诊断报告
============================================================

发现 3 个问题:

🔴 [1] OOMKilled
   严重程度: CRITICAL
   问题描述: 容器因内存不足被杀死
   置信度: 95%

   💡 建议:
      1. 增加Pod的memory limit
      2. 检查应用是否有内存泄漏
      3. 优化应用内存使用
      4. 考虑使用HPA自动扩缩容

   📝 相关日志:
      2024-01-15 10:23:48 ERROR OOMKilled: container exceeded memory limit

🟠 [2] LivenessProbeFailed
   严重程度: HIGH
   问题描述: 健康检查失败
   置信度: 85%

   💡 建议:
      1. 检查应用是否正常启动
      2. 调整probe的timeout和period
      3. 验证健康检查端点
      4. 增加initialDelaySeconds

🟡 [3] Timeout
   严重程度: MEDIUM
   问题描述: 请求超时
   置信度: 70%

   💡 建议:
      1. 检查下游服务响应时间
      2. 调整timeout配置
      3. 增加资源配额
      4. 优化慢查询

============================================================
```

**5 秒钟出结果，5 分钟定位问题。**

## 🎁 支持的错误模式

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

## 💪 适用场景

- **日常运维** - 快速定位 Pod 问题
- **故障排查** - 缩小问题范围
- **新人培训** - 学习常见错误模式
- **CI/CD 集成** - 自动化日志检查
- **批量诊断** - 一次分析多个 Pod

## 🔧 高级用法

### 与 CI/CD 集成

```yaml
# GitHub Actions
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
for pod in $(kubectl get pods -o name); do
  echo "Analyzing $pod..."
  k8s-log-doctor -p ${pod#pod/} -n production
done
```

## 🚧 后续计划

- [ ] 支持更多错误模式（欢迎 PR）
- [ ] 多语言支持（英文、中文）
- [ ] 插件系统（自定义规则）
- [ ] Web UI 可视化
- [ ] AI 深度分析（Pro 版）

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

如果你也遇到过类似的痛点，欢迎一起完善这个工具。

## 📝 最后

这个工具是我在日常运维中积累的经验的结晶。

希望能帮到同样在 K8s 坑里挣扎的你。

**GitHub 地址**: https://github.com/Richardoris/k8s-log-doctor

**欢迎 Star、Fork、提 Issue！**

---

*如果觉得有用，欢迎分享给更多需要的朋友～*
