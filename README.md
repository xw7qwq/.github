# xw7qwq 的组织配置

这个仓库维护 [xw7 组织主页](profile/README.md)、共享社区文件和可核验的维护配置。各项目自己的约定优先；没有自定义文件的仓库使用这里的组织默认说明与模板。

- [贡献规范](CONTRIBUTING.md)：分支、提交、审查、验证与合并。
- [使用与支持](SUPPORT.md)：按场景选择项目、文档和反馈入口。
- [安全报告](SECURITY.md)：各仓库的私密漏洞报告渠道。
- [协作行为准则](CODE_OF_CONDUCT.md)：交流与问题处理方式。
- [仓库维护约定](docs/maintenance.md)：保护规则、必需检查和长期分支。
- [维护者操作指南](docs/maintainer-guide.md)：新项目登记、配置核验、迁移与归档。
- [项目配置清单](config/repositories.json)：网站、标签、分支与检查的预期配置。
- [组织主页](https://github.com/xw7qwq)：项目入口。

修改本仓库后运行：

```sh
python3 scripts/check_repository.py
python3 -m unittest discover -s scripts -p 'test_*.py'
```

CI 会校验本地 Markdown 链接、SVG 格式并运行配置核验工具的离线测试。已登录 GitHub CLI 的维护者还可以运行 `python3 scripts/audit_organization.py` 完整检查本清单约定的远程配置；Actions 中的 **Organization audit (public)** 手动检查公开可见的配置，具体覆盖范围见[操作指南](docs/maintainer-guide.md)。
