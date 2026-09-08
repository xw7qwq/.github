# 仓库维护约定

维护入口是 [组织贡献规范](../CONTRIBUTING.md)。这里记录各仓库的检查与自动化差异，修改工作流或分支规则时需要同步更新。

## 主分支规则

所有仓库的默认分支都是 `main`。主分支禁止删除和强推；人工改动通过 PR，要求分支与最新主线兼容、必需检查通过，并解决全部审查讨论。单人维护不强制他人批准，因此批准数量为 0；这不免除审查与验证。

| 仓库 | 必需检查 | 本地验证 |
| --- | --- | --- |
| `.github` | `repository-check` | `python3 scripts/check_repository.py` |
| `codeflare` | `archive` | 按仓库贡献说明运行归档离线测试和来源完整性检查 |
| `ojflare` | `check` | `npm test`、`npm run build` |
| `macflare` | `worker`、`macos-agent` | 按仓库贡献说明运行 Worker、站点与 macOS 检查 |
| `nfuwari` | `Lint, check and build` | 按仓库指定的 Node / pnpm 版本执行 lint、check、build；依赖更新验证文章渲染 |

检查由 GitHub Actions 提供。改名、增加路径过滤或改变触发分支前，要同步检查 Rules 设置，避免 PR 永远等待一个不会运行的检查。

## 自动数据更新

`ojflare` 的每日同步读取 `main` 的代码和 `data/snapshots` 的最新缓存，将更新后的 `data/sources/` 与 `public/data/dashboard.json` 写回数据分支，再发布静态站点。数据分支只保存快照，不合回 `main`；主分支中的数据作为离线开发的基准快照。

源码与自动数据写入各用一个分支，使所有 `main` 都能执行相同的 PR 和检查要求，无需个人 Token 或机器人绕过者。数据分支保留机器人正常推送能力，同时禁止删除与强推；审查工作流的写权限与固定的数据路径，避免把代码写入数据分支。

## 长期分支与清理

| 仓库 / 分支 | 用途 | 处理原则 |
| --- | --- | --- |
| 所有仓库 / `main` | 默认源码与配置 | 保留；禁止删除和强推 |
| `codeflare` / `docs/project-guide` | 独立文档源码与构建流程 | 保留；文档改动向此分支提交 PR，和 `main` 同步时保留 merge 祖先关系 |
| `codeflare` / `gh-pages` | 手工维护的网站源码及生成的 `docs/` | 保留；文档发布自动更新 `docs/`，网站改动遵循此分支 README 的验证要求 |
| `ojflare` / `data/snapshots` | 每日同步的成功快照与请求状态 | 保留；自动化正常推送，禁止删除与强推；不合回主线 |
| 已完成的短期分支 | 功能、修复、文档、依赖或一次性数据导入 | PR 合并后自动删除；手动清理前核对远程 SHA、完整差异和未合并提交 |

不要把 `gh-pages` 合进 `main`，也不要为统一分支数量而删除部署源。已关闭但未合并的 PR 需要检查关闭原因和来源分支，关闭状态本身不能证明工作可以丢弃。

## 合并与发布

短期 PR 默认 squash，提交标题来自 PR 标题，默认不复制 PR 正文到提交消息；详细说明与验证证据保留在 PR 中，避免正文中的工作流控制标记影响合并后的 CI。同步长期分支时允许普通 merge。仓库开启合并后自动删除来源分支及更新 PR 分支按钮。

合并后检查主分支 CI；有 Pages 发布的项目还需确认最新部署成功。历史失败或被后续运行替代的取消记录无需删除，维护依据应是当前代码的有效检查和部署。上游平台暂时失败时保留成功快照，按项目文档判断是否需要重新同步。

GitHub 配置参考：[规则集](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)、[组织默认社区文件](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file)。

## 配置清单与维护入口

[repositories.json](../config/repositories.json)记录各项目的网站、标签、长期分支和检查名。修改仓库配置时同步更新清单，并按[维护者操作指南](maintainer-guide.md)运行适用范围的核验。项目使用问题见[支持入口](../SUPPORT.md)，漏洞见[安全报告](../SECURITY.md)。

## 已知后续工作

这里跟踪已在项目文档中确认、需要独立迁移或外部配置的事项，不代表当前站点故障，也不设置未经确认的期限。

| 项目 | 后续工作 | 完成条件与依据 |
| --- | --- | --- |
| nfuwari | 迁移 Astro 内容集合与相关依赖版本线，处理剩余依赖告警 | 按[依赖复核记录](https://github.com/xw7qwq/nfuwari/blob/main/docs/DEPENDENCY-REVIEW.zh-CN.md)升级父依赖；保留文章、公式、RSS、搜索、导航与图片处理的验证，重新核对审计结果与输入路径 |
| nfuwari | 恢复 GitHub Pages 源站证书 | 依照[部署说明](https://github.com/xw7qwq/nfuwari/blob/main/docs/DEPLOYMENT.zh-CN.md)核对域名验证与 ESA 回源配置；源站证书状态恢复正常并验证公网 HTTPS，当前公网访问由 ESA 正常提供 |
