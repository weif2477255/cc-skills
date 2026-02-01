# 技能模板

本目录包含创建新技能的模板文件。

## 可用模板

### skill-template/

标准技能模板，包含：
- **SKILL.md**: 技能定义文件，包含必需的 YAML frontmatter 和 Markdown 指令

### plugin-template/

插件配置模板（已弃用）：
- **plugin.json**: 插件元数据配置

**注意**：当前项目使用扁平化的 skills/ 目录结构，不再需要创建独立的插件。所有技能直接放在 skills/ 目录下，并在 marketplace.json 中统一注册。

## 使用方式

### 创建新技能

1. 复制技能模板：
   ```bash
   cp -r templates/skill-template skills/my-skill
   ```

2. 编辑 `skills/my-skill/SKILL.md`：
   - 修改 frontmatter 中的 `name` 和 `description`
   - 填写核心能力和使用方式
   - 编写详细的工作流程
   - 添加参考资源（可选）

3. 在 `.claude-plugin/marketplace.json` 中注册技能：
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

4. 更新 `README.md` 中的技能列表

### 技能目录结构

```
skills/my-skill/
├── SKILL.md          # 必需：技能定义和指令
├── scripts/          # 可选：可执行脚本
├── references/       # 可选：参考文档
└── assets/           # 可选：模板和资源文件
```

## 最佳实践

### SKILL.md 编写指南

1. **Description 字段**：
   - 清晰描述技能的功能
   - 包含具体的触发条件
   - 示例：`"Use when the user asks to check data models or mentions model validation"`

2. **保持简洁**：
   - SKILL.md 主体建议少于 500 行
   - 详细内容放入 `references/` 目录
   - 采用渐进式披露原则

3. **使用祈使语气**：
   - 使用命令式语句：`"Extract text from PDF"`
   - 避免第一人称：~~`"I will help you extract text"`~~

### 目录组织

- **scripts/**: 存放可重复使用的脚本，避免 Claude 重复编写相同代码
- **references/**: 存放详细的参考文档，按需加载
- **assets/**: 存放模板文件、图片等输出资源

## 详细指南

查看 [CLAUDE.md](../CLAUDE.md) 获取完整的技能创建指南和 Agent Skills 规范。

## 相关资源

- [Agent Skills 规范](https://agentskills.io/specification)
- [Anthropic 官方技能示例](https://github.com/anthropics/skills)
- [创建自定义技能](https://support.claude.com/en/articles/12512198-creating-custom-skills)
