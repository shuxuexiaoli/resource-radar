# resource-radar

每日资源雷达，跑在 GitHub Actions 上，结果自动提交回本仓库。

## 任务

| 工作流 | 时间（北京时间） | 做什么 | 结果文件 |
| --- | --- | --- | --- |
| QX resource radar | 每天 07:30 | 监控四个上游 QX 仓库（deezertidal/QuantumultX-Rewrite、yqc007/QuantumultX、NobyDa/Script、Sliverkiss/QuantumultX）的新提交与新脚本；搜索 GitHub 上新的高星 QuantumultX 仓库 | `candidates/qx-candidates.md` |

## 说明

- 脚本只用 Python 标准库：`scripts/qx_radar.py`。
- 去重状态存在 `state/`，由工作流每天随结果一起提交。
- 工作流支持在 Actions 页手动触发（workflow_dispatch）。
