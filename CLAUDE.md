# 技能创建指南

本文档描述如何为 cc-skills 仓库创建和贡献新技能。

## 关于技能

技能是模块化、自包含的包，通过提供专业知识、工作流程和工具集成来扩展 Claude 的能力。将其视为特定领域或任务的"入职指南"——它们将 Claude 从通用助手转变为配备程序性知识的专业助手。

### 技能提供什么

1. **专业工作流程** - 特定领域的多步骤流程
2. **工具集成** - 使用特定文件格式或 API 的指令
3. **领域专业知识** - 公司特定知识、模式、业务逻辑
4. **捆绑资源** - 用于复杂和重复任务的脚本、参考文档和资源

## 核心原则

### 1. 简洁至上

上下文窗口是公共资源。技能与其他所有内容共享上下文窗口：系统提示、对话历史、其他技能的元数据和实际用户请求。

**默认假设：Claude 已经非常聪明。** 只添加 Claude 没有的上下文。质疑每条信息："Claude 真的需要这个解释吗？" 和 "这段文字值得它的 token 成本吗？"

优先使用简洁的示例而非冗长的解释。

### 2. 设置适当的自由度

根据任务的脆弱性和可变性匹配具体程度：

- **高自由度（基于文本的指令）**：当多种方法都有效、决策取决于上下文或启发式指导方法时使用
- **中等自由度（伪代码或带参数的脚本）**：当存在首选模式、可接受一些变化或配置影响行为时使用
- **低自由度（特定脚本，少量参数）**：当操作脆弱且容易出错、一致性至关重要或必须遵循特定顺序时使用

将 Claude 想象为探索路径：有悬崖的狭窄桥梁需要特定的护栏（低自由度），而开阔的田野允许多条路线（高自由度）。

### 3. 渐进式披露

技能使用三级加载系统来有效管理上下文：

1. **元数据（name + description）** - 始终在上下文中（~100 词）
2. **SKILL.md 主体** - 技能触发时（< 5k 词）
3. **捆绑资源** - Claude 按需加载（无限制，因为脚本可以在不读入上下文窗口的情况下执行）

**关键原则**：将 SKILL.md 主体保持在 500 行以下以最小化上下文膨胀。接近此限制时将内容拆分为单独的文件。

## 技能结构

### 基本结构

每个技能由必需的 SKILL.md 文件和可选的捆绑资源组成：

```
skill-name/
├── SKILL.md (必需)
│   ├── YAML frontmatter 元数据 (必需)
│   │   ├── name: (必需)
│   │   └── description: (必需)
│   └── Markdown 指令 (必需)
└── 捆绑资源 (可选)
    ├── scripts/          - 可执行代码 (Python/Bash/等)
    ├── references/       - 按需加载到上下文的文档
    └── assets/           - 输出中使用的文件 (模板、图标、字体等)
```

### SKILL.md (必需)

每个 SKILL.md 包含：

#### Frontmatter (YAML)

包含 `name` 和 `description` 字段。这些是 Claude 读取以确定何时使用技能的唯一字段，因此清晰全面地描述技能是什么以及何时应该使用它非常重要。

```yaml
---
name: skill-name
description: "Clear description of what this skill does and when to use it. Include both functionality and specific triggers/contexts."
---
```

**字段规范**：

| 字段 | 必需 | 约束 |
|------|------|------|
| `name` | 是 | 最多 64 字符。仅小写字母、数字和连字符。不得以连字符开头或结尾。 |
| `description` | 是 | 最多 1024 字符。非空。描述技能的功能和使用时机。 |
| `license` | 否 | 许可证名称或对捆绑许可证文件的引用。 |
| `compatibility` | 否 | 最多 500 字符。指示环境要求（预期产品、系统包、网络访问等）。 |
| `metadata` | 否 | 用于附加元数据的任意键值映射。 |
| `allowed-tools` | 否 | 技能可能使用的预批准工具的空格分隔列表。（实验性） |

**命名约定**：
- 使用 kebab-case：`datamodel-checker`、`api-designer`
- 优先使用动名词形式：`analyzing-contracts`、`generating-tests`
- 避免模糊名称：`helper`、`utils`、`misc`
- 避免保留字：`anthropic`、`claude`

**描述最佳实践**：
- 包含技能的功能和使用时机
- 包含所有"何时使用"信息 - 不在主体中。主体仅在触发后加载
- 示例：`"Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction. Use when Claude needs to work with professional documents (.docx files) for: (1) Creating new documents, (2) Modifying or editing content, (3) Working with tracked changes, (4) Adding comments, or any other document tasks"`

#### Body (Markdown)

frontmatter 后的 Markdown 主体包含技能指令。没有格式限制。编写任何有助于 Claude 有效执行任务的内容。

**推荐部分**：
- 核心能力
- 使用方式
- 分步说明
- 输入和输出示例
- 常见边缘情况

**编写指南**：
- 始终使用祈使/不定式形式
- 保持简洁（< 500 行）
- 将详细内容移至 references/

### 捆绑资源 (可选)

#### scripts/

用于需要确定性可靠性或重复重写的任务的可执行代码。

- **何时包含**：当相同的代码被重复重写或需要确定性可靠性时
- **示例**：用于 PDF 旋转任务的 `scripts/rotate_pdf.py`
- **优势**：token 高效、确定性、可能在不加载到上下文的情况下执行
- **注意**：脚本可能仍需要被 Claude 读取以进行修补或环境特定调整

#### references/

旨在按需加载到上下文中以告知 Claude 的流程和思考的文档和参考材料。

- **何时包含**：用于 Claude 在工作时应参考的文档
- **示例**：用于财务模式的 `references/finance.md`、用于公司 NDA 模板的 `references/mnda.md`、用于 API 规范的 `references/api_docs.md`
- **用例**：数据库模式、API 文档、领域知识、公司政策、详细工作流程指南
- **优势**：保持 SKILL.md 精简，仅在 Claude 确定需要时加载
- **最佳实践**：如果文件很大（> 10k 词），在 SKILL.md 中包含 grep 搜索模式
- **避免重复**：信息应存在于 SKILL.md 或 references 文件中，而不是两者都有

#### assets/

不打算加载到上下文中，而是在 Claude 生成的输出中使用的文件。

- **何时包含**：当技能需要将在最终输出中使用的文件时
- **示例**：用于品牌资产的 `assets/logo.png`、用于 PowerPoint 模板的 `assets/slides.pptx`、用于 HTML/React 样板的 `assets/frontend-template/`
- **用例**：模板、图像、图标、样板代码、字体、被复制或修改的示例文档
- **优势**：将输出资源与文档分离，使 Claude 能够使用文件而不将它们加载到上下文中

### 不应包含的内容

技能应仅包含直接支持其功能的基本文件。不要创建无关的文档或辅助文件，包括：

- README.md
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- CHANGELOG.md
- 等

技能应仅包含 AI 代理完成手头工作所需的信息。它不应包含有关创建它的过程、设置和测试程序、面向用户的文档等的辅助上下文。

## 渐进式披露模式

当技能支持多个变体、框架或选项时，仅在 SKILL.md 中保留核心工作流程和选择指导。将特定于变体的详细信息（模式、示例、配置）移至单独的参考文件。

### 模式 1：带参考的高级指南

```markdown
# PDF Processing

## Quick start

Extract text with pdfplumber:
[code example]

## Advanced features

- **Form filling**: See [FORMS.md](references/FORMS.md) for complete guide
- **API reference**: See [REFERENCE.md](references/REFERENCE.md) for all methods
- **Examples**: See [EXAMPLES.md](references/EXAMPLES.md) for common patterns
```

Claude 仅在需要时加载 FORMS.md、REFERENCE.md 或 EXAMPLES.md。

### 模式 2：特定于域的组织

对于具有多个域的技能，按域组织内容以避免加载不相关的上下文：

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── references/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

当用户询问销售指标时，Claude 仅读取 sales.md。

### 模式 3：条件详细信息

显示基本内容，链接到高级内容：

```markdown
# DOCX Processing

## Creating documents

Use docx-js for new documents. See [DOCX-JS.md](references/DOCX-JS.md).

## Editing documents

For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](references/REDLINING.md)
**For OOXML details**: See [OOXML.md](references/OOXML.md)
```

Claude 仅在用户需要这些功能时读取 REDLINING.md 或 OOXML.md。

**重要指南**：
- **避免深度嵌套的引用** - 保持引用从 SKILL.md 一级深。所有引用文件应直接从 SKILL.md 链接。
- **结构化较长的引用文件** - 对于超过 100 行的文件，在顶部包含目录，以便 Claude 在预览时可以看到完整范围。

## 创建技能流程

### 步骤 1：创建技能目录

```bash
mkdir -p skills/my-skill
```

### 步骤 2：编辑 SKILL.md

1. **更新 frontmatter**：
   - 设置唯一的 `name`（kebab-case）
   - 编写清晰的 `description`，包括功能和触发器
   - 添加 `allowed-tools`（如果需要）

2. **编写主体内容**：
   - 核心能力
   - 使用方式和示例
   - 详细工作流程
   - 引用捆绑资源

3. **保持简洁**：
   - 目标 < 500 行
   - 将详细内容移至 references/
   - 使用渐进式披露模式

### 步骤 3：添加捆绑资源（如果需要）

1. **scripts/**：添加可重复使用的脚本
   - 使用 PEP 723 内联依赖（Python）
   - 测试脚本以确保它们工作

   ```python
   # /// script
   # requires-python = ">=3.11"
   # dependencies = ["requests>=2.28"]
   # ///
   ```

2. **references/**：添加详细文档
   - 按域或功能组织
   - 包含目录（如果 > 100 行）
   - 从 SKILL.md 链接

3. **assets/**：添加模板和资源
   - 模板文件
   - 图像和图标
   - 样板代码

### 步骤 4：注册技能

在 `.claude-plugin/marketplace.json` 中添加技能：

```json
{
  "plugins": [
    {
      "name": "cc-skills-collection",
      "skills": [
        "./skills/my-skill",
        ...
      ]
    }
  ]
}
```

### 步骤 5：更新文档

在 `README.md` 中添加技能到适当的类别。

### 步骤 6：测试

1. **加载市场**：
   ```bash
   /plugin marketplace add ./cc-skills
   ```

2. **安装技能集**：
   ```bash
   /plugin install cc-skills-collection@cc-skills
   ```

3. **触发测试**：
   - 尝试触发技能描述中提到的场景
   - 验证 Claude 能正确识别何时使用

4. **功能测试**：
   - 执行完整工作流
   - 验证输出符合预期

### 步骤 7：迭代

根据实际使用反馈改进技能：

1. 在真实任务上使用技能
2. 注意困难或低效之处
3. 确定应如何更新 SKILL.md 或捆绑资源
4. 实施更改并再次测试

## 质量检查清单

### SKILL.md 必需元素

- [ ] YAML frontmatter 包含 name 和 description
- [ ] name 使用 kebab-case，≤ 64 字符
- [ ] description 是第三人称，包含触发条件
- [ ] allowed-tools 准确列出所需工具（如果使用）
- [ ] 包含"核心能力"部分
- [ ] 包含"使用方式"部分
- [ ] 包含"工作流程"或详细流程部分
- [ ] 引用路径都指向 references/ 中的文件
- [ ] 无硬编码绝对路径

### 描述质量

- [ ] 第三人称：`"Check data models"` 而非 `"I help you check data models"`
- [ ] 包含触发：`"Use when the user asks to check data models"`
- [ ] 具体明确：`"Check data model specification compliance"` 而非 `"Data model tool"`

### 文件组织

- [ ] SKILL.md < 500 行（建议）
- [ ] 详细内容拆分到 references/
- [ ] 引用深度 ≤ 1 层（SKILL.md → reference.md，不要链式引用）
- [ ] 无冗余文件（不需要 CHANGELOG、.gitignore 等）

### 脚本质量（如果包含）

- [ ] 脚本已测试并正常工作
- [ ] Python 脚本使用 PEP 723 内联依赖
- [ ] 脚本包含有用的错误消息
- [ ] 脚本优雅地处理边缘情况

## 常见问题

### Q: 技能描述太长会怎样？

A: 描述会在每次可能触发时加载到上下文，建议控制在 2-3 句话，100-200 字。

### Q: 可以在 SKILL.md 中直接写长篇参考文档吗？

A: 不建议。使用渐进式披露：SKILL.md 保持精简，详细内容放 references/，按需加载。

### Q: 何时使用 scripts/ 目录？

A: 当有确定性、可重复的代码逻辑时（如 PDF 处理、数据解析），使用 scripts/ 而非让 Claude 重复编写。

### Q: 如何避免技能触发冲突？

A: 编写具体的描述，明确"何时使用"和"何时不使用"。例如 datamodel-checker 明确说"当用户要求检查数据模型"。

### Q: 何时创建新技能 vs 更新现有技能？

A: 如果功能与现有技能密切相关，更新现有技能。如果是全新的用例或领域，创建新技能。

## 参考资源

### 官方文档

- [Agent Skills 规范](https://agentskills.io/specification) - 完整的格式规范
- [Agent Skills 文档索引](https://agentskills.io/llms.txt) - 发现所有可用页面
- [Claude Code 插件](https://code.claude.com/docs/en/plugins) - 插件系统文档
- [创建自定义技能](https://support.claude.com/en/articles/12512198-creating-custom-skills) - 官方指南

### 示例仓库

- [Anthropic 官方技能](https://github.com/anthropics/skills) - 官方技能示例集合
- [本仓库技能](skills/) - 本地技能示例

### 工具

- [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) - 验证技能的参考库

```bash
skills-ref validate ./my-skill
```

## 版本管理

使用语义化版本 MAJOR.MINOR.PATCH：

- **文件调整、修复** → PATCH (1.0.0 → 1.0.1)
- **新增技能** → MINOR (1.0.0 → 1.1.0)
- **重大重构** → MAJOR (1.0.0 → 2.0.0)

每次更新：
1. 更新 marketplace.json 中的 metadata.version
2. 在 git commit 中记录更改

## 获取帮助

- 查看 [现有技能](skills/) 获取灵感
- 参考现有技能目录结构快速开始
- 阅读 [Agent Skills 规范](https://agentskills.io/specification) 了解详细信息
