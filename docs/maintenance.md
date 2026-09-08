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

## 自动化例外

`ojflare` 的每日同步使用 GitHub Actions 应用身份直接向 `main` 写入 `data/sources/` 和 `public/data/dashboard.json`。它被允许绕过 PR 和必需状态检查的规则，以保留数据刷新流程；禁止删除、禁止强推的规则独立生效，没有此例外。人工代码改动仍需要 PR。

GitHub 的应用例外作用于该应用身份，并不按文件路径限制。通过审查工作流中的 `contents: write`、固定的 `git add` 路径和写入前测试来约束数据用途。不得新增工作流借此绕过人工改动流程，也不要把个人 Token 加为通用绕过者。

## 长期分支与清理

| 仓库 / 分支 | 用途 | 处理原则 |
| --- | --- | --- |
| 所有仓库 / `main` | 默认源码与配置 | 保留；禁止删除和强推 |
| `codeflare` / `docs/project-guide` | 独立文档源码与构建流程 | 保留；文档改动向此分支提交 PR，和 `main` 同步时保留 merge 祖先关系 |
| `codeflare` / `gh-pages` | 手工维护的网站源码及生成的 `docs/` | 保留；文档发布自动更新 `docs/`，网站改动遵循此分支 README 的验证要求 |
| 已完成的短期分支 | 功能、修复、文档、依赖或一次性数据导入 | PR 合并后自动删除；手动清理前核对远程 SHA、完整差异和未合并提交 |

不要把 `gh-pages` 合进 `main`，也不要为统一分支数量而删除部署源。已关闭但未合并的 PR 需要检查关闭原因和来源分支，关闭状态本身不能证明工作可以丢弃。

## 合并与发布

短期 PR 默认 squash，提交标题来自 PR 标题，正文来自 PR 正文；同步长期分支时允许普通 merge。仓库开启合并后自动删除来源分支及更新 PR 分支按钮。

合并后检查主分支 CI；有 Pages 发布的项目还需确认最新部署成功。历史失败或被后续运行替代的取消记录无需删除，维护依据应是当前代码的有效检查和部署。上游平台暂时失败时保留成功快照，按项目文档判断是否需要重新同步。

GitHub 配置参考：[规则集](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)、[组织默认社区文件](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file)。
