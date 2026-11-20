# TokenEconomizer：Windows 本地验证

这是 microsoft/TokenEconomizer 的学习验证 Fork，不是原创重写。保留原作者和 MIT LICENSE。固定上游提交 `1bfeccdcecf48333b22762ad1dd9e36c6dc065df`。

## 真实结果（2026-11-20，Windows / Python 3.13.5）

| 范围 | 通过 | 失败 | 跳过 |
|---|---:|---:|---:|
| 插件主测试 `tests/` 复测 | **1408** | **0** | **43** |
| 额外实验套件 `experiments/tests/` | 384 | **10** | 3 |

**不是整个项目全部通过。** 首轮主测试 29 项因 Windows 长路径失败，缩短临时目录、测试进程优先 Git Bash 后完整复跑成功，没有删除或跳过原失败测试。43 项跳过包含真实宿主 E2E、POSIX 权限、symlink、缺少可选 aider 等情况，详见 JUnit。

实验套件的 10 项失败仍保留：涉及 `/dev/null`、`os.getuid`、`SIGHUP`、Windows 路径/TOML 断言、空 workload 计划等。未运行真实 SWE-bench、Docker 或付费模型。

## 构建与限制

- Wheel 构建，在空白专用 venv 离线安装，CLI `--help` 和空状态 `status` 成功。
- 发现上游插件构建 ZIP 没有 MIT LICENSE；本地派生包仅补原始许可证和来源说明，未改运行时代码。此 Fork 不提交二进制构建包。
- 没有接入你的真实 Codex/Claude，也未读取真实会话历史。测试使用临时 home 和假数据。
- 没有测出你的实际省 Token 比例，不能用上游宣传数字代替验收。

## 独立环境复现

在仓库根目录：

```powershell
python -m venv .venv-local-validation
.\.venv-local-validation\Scripts\python.exe -m pip install -r validation/requirements-tests.txt
.\validation\verify.ps1 -PythonPath .\.venv-local-validation\Scripts\python.exe
```

需要 Git Bash；默认尝试测试机路径 `D:/Git/Git/bin`，其他路径设置 `$env:VALIDATION_GIT_BASH_DIR`。Windows 临时目录尽量短；脚本每次新建目录、不删除旧目录。专用环境不上传。

## 证据与边界

`validation/results.json` 和 `validation/evidence/` 保留首轮、复测、实验套件的 JUnit/日志及构建、CLI 证据。隔离 home/config、移除继承 API 环境变量和 offline/socket 限制不是 OS 沙箱或安全审计。未改上游运行时代码，未创建上游 PR。
