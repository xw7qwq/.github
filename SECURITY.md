# 安全问题报告

本说明是 xw7qwq 组织的默认安全入口；仓库已有 `SECURITY.md` 时，以项目专用说明为准。排查与修复以当前默认分支为基础，请提供受影响的版本或提交号。

## 私密报告

不要把有效 Token、Cookie、个人状态快照或可直接利用的敏感细节放进公开 Issue。各仓库已启用 GitHub Private Vulnerability Reporting：

| 受影响项目 | 私密报告入口 |
| --- | --- |
| 组织配置与工作流 | [.github](https://github.com/xw7qwq/.github/security/advisories/new) |
| 竞赛归档、阅读器与文档 | [codeflare](https://github.com/xw7qwq/codeflare/security/advisories/new) |
| 解题数据同步与看板 | [ojflare](https://github.com/xw7qwq/ojflare/security/advisories/new) |
| macOS 采集与状态 API | [macflare](https://github.com/xw7qwq/macflare/security/advisories/new) |
| 博客与构建链 | [nfuwari](https://github.com/xw7qwq/nfuwari/security/advisories/new) |

报告应包含触发条件、最小复现、影响、受影响部署方式及建议缓解措施。使用测试凭据和合成数据，只测试自己拥有或获得授权的环境；不需要为了证明影响提取真实用户数据。

入口暂时不可用时，可以在对应仓库创建不含敏感细节的 Issue，请求维护者恢复私密报告渠道。GitHub 的表单要求登录；有仓库管理权限的维护者可直接建立草稿安全公告。

## 处理与修复

维护者在私密报告中核实影响、讨论修复与披露方式。未承诺固定响应时限、奖金或历史版本的维护期限。普通使用问题请参阅[支持入口](https://github.com/xw7qwq/.github/blob/main/SUPPORT.md)。

若凭据已泄漏，应先在相应服务撤销或轮换，再处理代码、构建日志和历史中的副本。仅删除最新文件不能让旧凭据失效；公开状态和静态数据也可能已被第三方保存。项目专用的停止采集、令牌更新与数据保留步骤以各仓库文档为准。

依赖告警需要结合父依赖、版本约束和输入路径核实。当前博客的已知剩余项见[依赖复核记录](https://github.com/xw7qwq/nfuwari/blob/main/docs/DEPENDENCY-REVIEW.zh-CN.md)；记录适用范围不等于宣称未修补依赖没有缺陷。
