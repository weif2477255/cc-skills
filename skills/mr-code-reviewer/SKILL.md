---
name: mr-code-reviewer
description: "专业的 GitLab MR 代码审查技能，支持 Java 和 TypeScript/JavaScript，检查代码质量、安全漏洞、性能问题和 API 兼容性。采用两阶段策略：快速扫描识别明显问题，深度分析评估设计和架构。当用户要求审查 GitLab MR、检查代码质量、或评估代码变更时使用。"
allowed-tools: Bash, Read, Write, Glob, Grep
---

# MR Code Reviewer - GitLab MR 专业代码审查

专业的代码审查技能，专注于 GitLab Merge Request 的全面质量评估。

## 核心能力

### 两阶段检查策略

1. **快速扫描阶段** (3-5 分钟)
   - 自动识别常见代码异味
   - 检测明显的安全漏洞
   - 验证代码规范符合性
   - 快速反馈关键问题

2. **深度分析阶段** (10-15 分钟)
   - 设计模式和架构评估
   - 性能和可扩展性分析
   - API 兼容性和版本管理检查
   - 提供详细的重构建议

### 支持的语言和框架

- **Java 后端**: Spring Boot, JPA/Hibernate, Spring Security
- **TypeScript/JavaScript 前端**: React, Vue, Express, Node.js
- **通用**: 设计模式, SOLID 原则, API 设计

### 检查维度

| 维度 | 检查内容 |
|------|---------|
| **安全性** | OWASP Top 10, SQL注入, XSS, CSRF, 密钥泄露 |
| **性能** | N+1查询, 内存泄漏, 数据库优化, 缓存策略 |
| **质量** | 代码异味, 复杂度, 重复代码, 命名规范 |
| **架构** | SOLID原则, 设计模式, 依赖管理, 层次划分 |
| **兼容性** | API版本管理, 向后兼容性, 破坏性变更识别 |

## 使用方式

### 基本用法

```
请审查 MR !123
```

### 指定项目和 MR

```
请审查项目 12345 的 MR !42
```

### 高级选项

```
请深度审查 MR !123，重点关注：
- 安全漏洞
- API 兼容性
- 性能问题
```

### 提供 MR URL

```
请审查这个 MR: https://gitlab.com/myproject/repo/-/merge_requests/123
```

## 详细流程

### 阶段 0: 准备和信息收集

1. **获取 MR 信息**
   - 使用 `scripts/get-mr-changes.py` 获取变更文件列表
   - 获取每个文件的完整内容（不只是 diff）
   - 生成变更摘要

2. **环境准备**
   ```bash
   # 需要设置环境变量
   export GITLAB_URL=https://gitlab.com
   export GITLAB_TOKEN=your-access-token

   # 或在命令中指定
   python scripts/get-mr-changes.py \
     --url https://gitlab.com \
     --token glpat-xxx \
     --project-id 12345 \
     --mr-iid 42
   ```

3. **文件分类**
   - Java 文件: `.java`
   - TypeScript/JavaScript: `.ts`, `.tsx`, `.js`, `.jsx`, `.vue`
   - 配置文件: `.yml`, `.yaml`, `.json`, `.properties`
   - API 规范: `openapi.yaml`, `swagger.json`

### 阶段 1: 快速扫描（3-5 分钟）

#### 1.1 安全快速检查

使用 `references/security-checks.md` 作为检查清单：

**Critical 级别（必须立即修复）**:
- [ ] SQL/NoSQL 注入漏洞
- [ ] XSS 跨站脚本漏洞
- [ ] 硬编码密钥或密码
- [ ] 缺少认证的敏感操作
- [ ] 不安全的反序列化
- [ ] 服务端请求伪造 (SSRF)

**High 级别（高优先级）**:
- [ ] 缺少授权检查
- [ ] 弱加密算法（MD5、SHA1）
- [ ] 敏感信息泄露
- [ ] CSRF 防护缺失

#### 1.2 语言特定规则检查

**Java 文件** - 参考 `references/java-rules.md`:
- [ ] 使用构造函数注入而非字段注入
- [ ] 参数化查询防止 SQL 注入
- [ ] 正确的事务管理（@Transactional）
- [ ] 避免 N+1 查询问题
- [ ] 线程安全问题

**TypeScript/JavaScript 文件** - 参考 `references/typescript-rules.md`:
- [ ] 避免使用 `any` 类型
- [ ] useEffect 包含完整依赖项
- [ ] 防止 XSS（避免 dangerouslySetInnerHTML）
- [ ] 正确的错误处理
- [ ] 防抖/节流频繁操作

#### 1.3 代码异味检测

参考 `references/design-patterns.md` 的代码异味清单：

**方法级别警告** (立即标记):
- 行数 > 50（严重）
- 参数 > 5（严重）
- 圈复杂度 > 15（严重）
- 嵌套层级 > 4（严重）

**类级别警告** (立即标记):
- 行数 > 500（严重）
- 方法数 > 30（严重）
- 依赖数 > 10（严重）

#### 1.4 快速扫描输出

生成初步报告 `quick-scan-results.md`，包含 Critical 和 High 优先级问题。

### 阶段 2: 深度分析（10-15 分钟）

只有在快速扫描未发现 Critical 问题，或用户明确要求深度分析时才执行。

#### 2.1 架构和设计模式分析

参考 `references/design-patterns.md`:

1. **SOLID 原则检查**
   - 单一职责原则 (SRP): 类是否承担多个职责？
   - 开闭原则 (OCP): 是否通过扩展而非修改来添加功能？
   - 里氏替换原则 (LSP): 子类是否能替换父类？
   - 接口隔离原则 (ISP): 接口是否过于臃肿？
   - 依赖倒置原则 (DIP): 是否依赖抽象而非具体实现？

2. **设计模式应用**
   - 识别现有设计模式的使用
   - 建议合适的设计模式改进
   - 检测反模式 (Anti-patterns)

3. **依赖管理**
   - 循环依赖检测
   - 依赖方向合理性
   - 层次划分清晰性

#### 2.2 性能深度分析

**数据库性能**:
- N+1 查询检测
- 缺失索引识别
- 批量操作机会
- 连接池配置

**前端性能**:
- 不必要的重渲染
- 大列表虚拟化
- 代码分割和懒加载
- 图片优化

**并发和异步**:
- 死锁风险
- 竞态条件
- 资源泄漏

#### 2.3 API 兼容性检查

参考 `references/api-compatibility.md`:

1. **破坏性变更识别**
   - 删除或重命名字段
   - 改变字段类型
   - 增加必需参数
   - 移除端点

2. **版本控制策略**
   - URL 版本控制实现
   - API 规范更新
   - 废弃字段标记

3. **向后兼容性验证**
   - 旧客户端兼容性测试
   - 渐进式废弃策略
   - 迁移指南完整性

#### 2.4 重构建议

为识别的问题提供详细的重构方案：

1. **提供代码示例**
   - 重构前代码
   - 重构后代码
   - 逐步重构步骤

2. **影响范围评估**
   - 需要修改的文件列表
   - 依赖变更影响
   - 测试更新需求

3. **优先级排序**
   - Critical: 安全漏洞、数据损坏风险
   - High: 性能瓶颈、严重代码异味
   - Medium: 设计改进、可维护性
   - Low: 命名优化、样式统一

### 最终输出格式

生成完整的审查报告 `code-review-report.md`，包含：

- **执行摘要**: 审查时间、MR 信息、问题统计、总体评估
- **Critical 问题**: 必须立即修复的严重问题
- **High 优先级问题**: 合并前应处理的重要问题
- **Medium/Low 问题**: 后续改进建议
- **API 兼容性分析**: 破坏性变更识别和版本管理建议
- **重构优先级**: 按优先级排序的处理建议
- **测试建议**: 针对识别问题的测试用例建议

## 交互流程

1. **用户请求审查**
   ```
   用户: 请审查 MR !123
   ```

2. **确认信息**
   ```
   Claude: 我将审查 MR !123。需要以下信息：
   - GitLab URL（默认: https://gitlab.com）
   - 项目 ID
   - GitLab 访问令牌

   这些信息可以通过环境变量或直接提供。
   ```

3. **执行快速扫描**
   ```
   Claude: 正在执行快速扫描...
   - ✅ 获取 MR 变更文件（15 个文件）
   - ✅ 安全快速检查
   - ✅ 代码规范检查
   - ⚠️ 发现 2 个 Critical 问题

   是否继续深度分析？
   ```

4. **执行深度分析**（如果需要）
   ```
   Claude: 正在执行深度分析...
   - ✅ 架构和设计模式分析
   - ✅ 性能深度分析
   - ✅ API 兼容性检查
   - ✅ 生成重构建议
   ```

5. **提供审查报告**
   ```
   Claude: 审查完成！生成了以下文件：
   - code-review-report.md（完整报告）
   - quick-scan-results.md（快速扫描结果）

   **总结**:
   - 发现 23 个问题（2 Critical, 5 High, 10 Medium, 6 Low）
   - 建议修复 Critical 和 High 问题后合并
   - 预计修复时间：约 1 小时
   ```

## 配置和环境

### 环境变量

```bash
# GitLab 配置
export GITLAB_URL=https://gitlab.com
export GITLAB_TOKEN=glpat-your-token

# 可选：自定义检查规则
export CODE_REVIEW_STRICT_MODE=true  # 更严格的检查
export CODE_REVIEW_FOCUS=security    # 重点检查: security, performance, quality
```

### 辅助脚本

本技能包含辅助脚本 `scripts/get-mr-changes.py`，用于从 GitLab API 获取 MR 变更：

```bash
# 基本用法
python scripts/get-mr-changes.py \
  --project-id 12345 \
  --mr-iid 42

# 指定 GitLab 实例
python scripts/get-mr-changes.py \
  --url https://gitlab.company.com \
  --token glpat-xxx \
  --project-id 12345 \
  --mr-iid 42 \
  --save-files  # 保存单独文件

# 输出结构
mr_changes/
├── mr_changes.json      # 完整数据
├── SUMMARY.md           # 变更摘要
└── files/              # 单独文件（--save-files）
    ├── src/
    │   └── UserService.java
    └── ...
```

## 参考资源

本技能集成了以下参考文档，在审查过程中会根据文件类型和检查重点动态加载：

### 核心参考

- **[Java 代码检查规则](references/java-rules.md)**
  - Spring 框架最佳实践
  - 企业模式和依赖注入
  - JPA/Hibernate 优化
  - 并发和线程安全

- **[TypeScript/JavaScript 规则](references/typescript-rules.md)**
  - 现代 JavaScript/TypeScript 模式
  - React/Vue 最佳实践
  - 前端安全检查
  - 性能优化技巧

- **[设计模式和 SOLID 原则](references/design-patterns.md)**
  - SOLID 原则详解和示例
  - 常用设计模式（工厂、策略、观察者等）
  - 代码异味识别清单
  - 重构模式

### 专项参考

- **[安全检查规则](references/security-checks.md)**
  - OWASP Top 10 详细检查清单
  - 输入验证和清理
  - 认证和授权最佳实践
  - 加密和密钥管理

- **[API 兼容性检查规则](references/api-compatibility.md)**
  - API 版本控制策略
  - 破坏性变更识别
  - 向后兼容性原则
  - GraphQL 和 RESTful API 演进

## 高级特性

### 自定义检查重点

```
请审查 MR !123，重点检查：
1. 安全漏洞（OWASP Top 10）
2. API 向后兼容性
3. 数据库查询性能
```

### 增量审查

```
请只审查 MR !123 中新增和修改的代码，忽略删除的文件
```

### 对比审查

```
请对比 MR !123 和 MR !120 的代码质量改进情况
```

### 生成检查清单

```
为 MR !123 生成一个人工审查检查清单
```

## 最佳实践

1. **优先快速扫描**: 总是先执行快速扫描，发现 Critical 问题立即反馈
2. **分层报告**: 按严重程度组织问题，优先展示高优先级问题
3. **提供示例**: 每个问题都提供重构前后的代码示例
4. **考虑上下文**: 在审查时考虑业务逻辑和项目约束
5. **建设性反馈**: 不只指出问题，还要解释原因和提供解决方案
6. **追踪影响**: 评估每个变更对其他模块的影响
7. **测试建议**: 为识别的问题建议相应的测试用例

## 限制和注意事项

- **语言支持**: 目前仅支持 Java 和 TypeScript/JavaScript
- **框架覆盖**: 重点支持 Spring、React、Vue，其他框架覆盖有限
- **代码上下文**: 需要访问完整文件内容，仅基于 diff 的审查效果有限
- **业务逻辑**: 自动化审查无法完全理解业务需求，某些判断需要人工确认
- **性能测试**: 无法执行实际性能测试，仅基于代码分析识别潜在问题

## 持续改进

本技能会持续更新以支持：
- 更多编程语言（Python、Go、Rust）
- 更多框架（NestJS、Angular、Django）
- AI 辅助的代码异味检测
- 自动化的重构建议应用
- 与 CI/CD 流程集成
