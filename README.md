# CC-Skills

个人自定义 Claude Code 技能集合，涵盖需求澄清、评审分析、文档生成和 Prompt 工程等场景。

## 关于技能

技能是模块化、自包含的包，通过提供专业知识、工作流程和工具集成来扩展 Claude 的能力。将 Claude 从通用助手转变为配备特定领域程序性知识的专业助手。

## 快速开始

### 在 Claude Code 中使用

在 cc-skills 的**父目录**中运行以下命令添加本地市场：

```bash
/plugin marketplace add ./cc-skills
```

然后安装技能集：

```bash
/plugin install cc-skills-collection@cc-skills
```

或者通过菜单浏览安装：

```bash
/plugin menu
```

### 在 Claude.ai 中使用

1. 访问 Claude.ai 的技能管理页面
2. 上传技能文件夹或 .skill 文件
3. 开始使用技能

详细说明请参考 [Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)

## 技能列表

本仓库包含 **13 个技能**，按功能分类如下：

### 需求与协作 (2)

| 技能 | 描述 | 主要功能 |
|------|------|---------|
| [ask-clarify](skills/ask-clarify/) | 需求澄清与结构化 | 将模糊需求转化为结构化prompt，通过访谈澄清角色、任务、上下文、输出格式 |
| [mind-partner](skills/mind-partner/) | 私人AI协作伙伴 | 了解用户背景和思维偏好，接收碎片化想法，多轮迭代协作完成任务 |

### 评审与分析 (4)

| 技能 | 描述 | 主要功能 |
|------|------|---------|
| [datamodel-checker](skills/datamodel-checker/) | 数据模型检查 | 验证KMMOM数据模型规范符合性，检查7大维度，生成详细报告 |
| [interviewer-review-assistant](skills/interviewer-review-assistant/) | 面试官复盘助手 | 复盘面试官表现，检查提问覆盖、追问闭环和轮次目标匹配度 |
| [mr-code-reviewer](skills/mr-code-reviewer/) | GitLab MR 代码审查 | 两阶段检查策略，支持Java和TypeScript，检查代码质量、安全漏洞、性能问题 |
| [oss-scanner](skills/oss-scanner/) | 开源组件扫描与合规分析 | 扫描Maven/Gradle/npm依赖，检测许可证风险，生成合规报告 |

### 文档与报告 (6)

| 技能 | 描述 | 主要功能 |
|------|------|---------|
| [lowcode-biweekly-report](skills/lowcode-biweekly-report/) | 低代码平台双周日报助手 | 自动化生成低代码平台双周日报，包括数据清洗、交互式信息收集和报告生成 |
| [meeting-summarizer](skills/meeting-summarizer/) | 会议纪要总结器 | 将会议内容智能整理为规范的会议纪要文档，自动识别会议类型和行动项 |
| [ppt-reviewer](skills/ppt-reviewer/) | PPT 演讲评审器 | 先评审再成稿，输出受控的逐页PPT结构化文案 |
| [seed-sprout-report](skills/seed-sprout-report/) | 发芽报告助手 | 将一句记录或一段笔记发芽成带跨领域联想的新认知文本 |
| [team-monthly-evaluation](skills/team-monthly-evaluation/) | 团队月度评价 | 自动化生成团队月度综合评价，包括数据清洗、统计分析、绩效评估 |
| [week-report-assistant](skills/week-report-assistant/) | 双周汇报助手 | 从团队工作日志生成结构化的双周进展汇报，支持IPD标准 |

### Prompt 工程 (1)

| 技能 | 描述 | 主要功能 |
|------|------|---------|
| [prompt-optimizer](skills/prompt-optimizer/) | Prompt 优化器 | 使用57个经过验证的框架优化prompt，提供场景匹配和框架选择 |

## 创建技能

想要创建自己的技能？查看我们的 [贡献指南](CLAUDE.md)。

### 基本技能结构

技能是一个包含 `SKILL.md` 文件的文件夹：

```
skill-name/
├── SKILL.md          # 必需：技能定义和指令
├── scripts/          # 可选：可执行脚本
├── references/       # 可选：参考文档
└── assets/           # 可选：模板和资源文件
```

### 快速创建

直接在 `skills/` 下新建技能目录和 `SKILL.md`：

```bash
mkdir skills/my-skill
```

然后创建并编辑 `skills/my-skill/SKILL.md`，填写 frontmatter、工作流程和引用资源。

详细指南请参考 [CLAUDE.md](CLAUDE.md)。

## 目录结构

```
cc-skills/
├── .claude-plugin/
│   └── marketplace.json      # 市场配置
├── skills/                   # 所有技能
│   ├── ask-clarify/
│   ├── datamodel-checker/
│   ├── interviewer-review-assistant/
│   ├── mind-partner/
│   ├── ppt-reviewer/
│   ├── seed-sprout-report/
│   └── ...
├── README.md                 # 本文件
└── CLAUDE.md                 # 贡献指南
```

## 相关资源

### 官方文档

- [Agent Skills 规范](https://agentskills.io/specification) - 完整的技能格式规范
- [Claude Code 插件文档](https://code.claude.com/docs/en/plugins) - 插件系统文档
- [创建自定义技能](https://support.claude.com/en/articles/12512198-creating-custom-skills) - 官方创建指南

### 示例仓库

- [Anthropic 官方技能](https://github.com/anthropics/skills) - Anthropic 的技能示例集合
- [Agent Skills 网站](https://agentskills.io) - 技能标准和最佳实践

## 许可证

MIT License

---

**注意**：本仓库中的技能仅供演示和教育目的。在关键任务中使用前，请在您自己的环境中充分测试。
