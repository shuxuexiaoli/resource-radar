# resource-radar

每日资源雷达，跑在 GitHub Actions 上，结果自动提交回本仓库。

## 任务

| 工作流 | 时间（北京时间） | 做什么 | 结果文件 |
| --- | --- | --- | --- |
| QX resource radar | 每天 07:30 | 监控四个上游 QX 仓库（deezertidal/QuantumultX-Rewrite、yqc007/QuantumultX、NobyDa/Script、Sliverkiss/QuantumultX）的新提交与新脚本；搜索 GitHub 上新的高星 QuantumultX 仓库 | `candidates/qx-candidates.md` |
| linux.do welfare radar | 每天 08:40 | 抓 linux.do 公开 RSS，按标题关键词（公益站、免费额度、免费订阅、机场、签到、注册送等）筛资源类新帖 | `candidates/welfare-candidates.md` |

## 说明

- 脚本只用 Python 标准库：`scripts/qx_radar.py`、`scripts/welfare_radar.py`。
- 去重状态存在 `state/`，由工作流每天随结果一起提交。
- 两个工作流都支持在 Actions 页手动触发（workflow_dispatch）。
- linux.do 的 RSS 若被 Cloudflare 拦截，福利雷达会记录警告并正常退出（工作流日志可见），不影响 QX 雷达。
