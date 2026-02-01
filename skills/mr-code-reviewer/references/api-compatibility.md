# API 兼容性检查规则

本文档提供 API 设计和版本管理的最佳实践，重点关注向后兼容性和 API 演进策略。

## 目录

- [API 版本控制策略](#api-版本控制策略)
- [向后兼容性原则](#向后兼容性原则)
- [破坏性变更识别](#破坏性变更识别)
- [API 演进模式](#api-演进模式)
- [OpenAPI 规范](#openapi-规范)
- [GraphQL 兼容性](#graphql-兼容性)
- [弃用策略](#弃用策略)
- [测试和验证](#测试和验证)

## API 版本控制策略

### 语义化版本控制

遵循 [Semantic Versioning](https://semver.org/):
- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 向后兼容的功能新增
- **PATCH**: 向后兼容的问题修复

```
API v1.2.3
    │ │ └── PATCH: 修复 bug，不改变行为
    │ └──── MINOR: 新增字段/端点，兼容旧客户端
    └────── MAJOR: 移除字段/端点，破坏兼容性
```

### URL 版本控制

**推荐方式**:
```typescript
// ✅ 推荐：URL 路径版本
GET /api/v1/users
GET /api/v2/users

// ✅ 推荐：API 网关级别版本
GET /v1/users  // 路由到 users-service-v1
GET /v2/users  // 路由到 users-service-v2
```

**其他方式**:
```http
# Header 版本控制
GET /api/users
Accept: application/vnd.myapp.v1+json

# 查询参数版本控制（不推荐）
GET /api/users?version=1
```

**版本控制实现**:
```typescript
// Express.js 版本路由
import express from 'express';

const app = express();

// V1 API
const v1Router = express.Router();
v1Router.get('/users', (req, res) => {
  res.json({
    users: [
      { id: 1, name: 'Alice' }  // V1 格式
    ]
  });
});

// V2 API
const v2Router = express.Router();
v2Router.get('/users', (req, res) => {
  res.json({
    users: [
      {
        id: 1,
        firstName: 'Alice',  // V2: 拆分 name 为 firstName/lastName
        lastName: 'Smith',
        email: 'alice@example.com'  // V2: 新增字段
      }
    ]
  });
});

app.use('/api/v1', v1Router);
app.use('/api/v2', v2Router);
```

## 向后兼容性原则

### 兼容性黄金法则

**永远不要**:
1. 删除或重命名已有字段
2. 改变字段的数据类型
3. 改变字段的语义
4. 增加必需的请求参数
5. 移除端点
6. 改变错误响应的格式

**可以安全地**:
1. 添加新的可选字段
2. 添加新的端点
3. 添加新的可选参数
4. 扩展枚举类型（谨慎）
5. 放宽验证规则

### 兼容性变更示例

```typescript
// ❌ 破坏性变更：重命名字段
// V1
interface User {
  name: string;
}

// V2 - ❌ 破坏兼容性
interface User {
  fullName: string;  // 重命名了 name
}

// ✅ 兼容性变更：添加新字段，保留旧字段
// V2 - ✅ 保持兼容
interface User {
  name: string;        // 保留旧字段（标记为 @deprecated）
  firstName: string;   // 新增
  lastName: string;    // 新增
}
```

```java
// ❌ 破坏性变更：改变数据类型
// V1
public class Order {
    private String total;  // "19.99"
}

// V2 - ❌ 破坏兼容性
public class Order {
    private BigDecimal total;  // 客户端期望字符串，现在是数字
}

// ✅ 兼容性变更：添加新字段
// V2 - ✅ 保持兼容
public class Order {
    private String total;           // 保留旧格式
    private BigDecimal totalAmount; // 新增精确类型
}
```

### 渐进式废弃模式

```typescript
// ✅ 支持旧字段并发出警告
interface UserResponse {
  /** @deprecated Use firstName and lastName instead */
  name?: string;
  firstName: string;
  lastName: string;
}

function getUser(id: string): UserResponse {
  const user = fetchUserFromDB(id);

  return {
    // 同时返回新旧字段
    name: `${user.firstName} ${user.lastName}`,  // 向后兼容
    firstName: user.firstName,
    lastName: user.lastName,
    // 添加废弃警告头
    _deprecated: {
      name: 'Field "name" is deprecated. Use firstName and lastName.'
    }
  };
}
```

## 破坏性变更识别

### 请求破坏性变更

| 变更类型 | 示例 | 破坏性 | 说明 |
|---------|------|--------|------|
| 添加必需参数 | `name` 从可选变为必需 | ✅ 是 | 旧客户端请求会失败 |
| 删除可选参数 | 移除 `filter` 参数 | ✅ 是 | 使用该参数的客户端会出错 |
| 参数类型变更 | `age: string` → `age: number` | ✅ 是 | 客户端发送错误类型 |
| 收紧验证规则 | `name` 最大长度 100 → 50 | ✅ 是 | 之前有效的请求变为无效 |
| 添加可选参数 | 新增 `sort` 参数 | ❌ 否 | 旧客户端忽略即可 |
| 放宽验证规则 | `name` 最大长度 50 → 100 | ❌ 否 | 旧请求仍然有效 |

### 响应破坏性变更

| 变更类型 | 示例 | 破坏性 | 说明 |
|---------|------|--------|------|
| 删除字段 | 移除 `email` 字段 | ✅ 是 | 客户端期望该字段 |
| 重命名字段 | `name` → `fullName` | ✅ 是 | 客户端找不到字段 |
| 字段类型变更 | `id: number` → `id: string` | ✅ 是 | 客户端类型不匹配 |
| 改变嵌套结构 | `user.name` → `user.profile.name` | ✅ 是 | 路径变化 |
| 添加字段 | 新增 `createdAt` | ❌ 否 | 客户端可以忽略 |
| 字段变为可选 | `email!` → `email?` | ❌ 否 | 客户端应该处理 null |

### 破坏性变更检测工具

```bash
# OpenAPI 差异检测
npx openapi-diff oldspec.yaml newspec.yaml

# 输出示例
Breaking changes:
  - Removed field: GET /users response.email
  - Changed type: POST /users request.age (string → number)
```

## API 演进模式

### 模式 1: 扩展模式（推荐）

**原则**: 只增加，不删除或修改

```typescript
// ✅ V1 API
interface CreateUserRequest {
  name: string;
  email: string;
}

// ✅ V2 API - 扩展请求
interface CreateUserRequest {
  name: string;
  email: string;
  phone?: string;      // 新增可选字段
  preferences?: {      // 新增嵌套对象
    newsletter: boolean;
  };
}

// 服务端处理
function createUser(req: CreateUserRequest) {
  // V1 客户端：只发送 name 和 email
  // V2 客户端：可以发送所有字段
  const user = {
    name: req.name,
    email: req.email,
    phone: req.phone ?? null,           // 使用默认值
    preferences: req.preferences ?? {}  // 使用默认值
  };

  return saveUser(user);
}
```

### 模式 2: 版本化端点

```typescript
// V1 端点
app.get('/api/v1/users/:id', async (req, res) => {
  const user = await db.users.findById(req.params.id);
  res.json({
    id: user.id,
    name: user.name,
    email: user.email
  });
});

// V2 端点 - 完全独立
app.get('/api/v2/users/:id', async (req, res) => {
  const user = await db.users.findById(req.params.id);
  res.json({
    id: user.id,
    firstName: user.firstName,
    lastName: user.lastName,
    email: user.email,
    phone: user.phone,
    createdAt: user.createdAt
  });
});
```

### 模式 3: 内容协商

```typescript
// 使用 Accept header 选择版本
app.get('/api/users/:id', async (req, res) => {
  const user = await db.users.findById(req.params.id);

  const acceptHeader = req.get('Accept');

  if (acceptHeader?.includes('application/vnd.myapp.v2+json')) {
    // V2 响应
    res.json({
      id: user.id,
      firstName: user.firstName,
      lastName: user.lastName,
      email: user.email
    });
  } else {
    // V1 响应（默认）
    res.json({
      id: user.id,
      name: `${user.firstName} ${user.lastName}`,
      email: user.email
    });
  }
});
```

### 模式 4: 功能开关

```typescript
// 使用功能开关逐步推出变更
import { isFeatureEnabled } from './feature-flags';

app.get('/api/users', async (req, res) => {
  const users = await db.users.findAll();

  // 检查客户端是否启用新格式
  const useNewFormat = isFeatureEnabled('new-user-format', req.user);

  const response = users.map(user => {
    if (useNewFormat) {
      return {
        id: user.id,
        firstName: user.firstName,
        lastName: user.lastName,
        profile: {
          email: user.email,
          phone: user.phone
        }
      };
    } else {
      return {
        id: user.id,
        name: `${user.firstName} ${user.lastName}`,
        email: user.email
      };
    }
  });

  res.json(response);
});
```

## OpenAPI 规范

### 版本化 OpenAPI 规范

```yaml
# openapi-v1.yaml
openapi: 3.0.0
info:
  title: My API
  version: 1.0.0
  description: Version 1 of the API

paths:
  /users:
    get:
      summary: List users
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  users:
                    type: array
                    items:
                      $ref: '#/components/schemas/UserV1'

components:
  schemas:
    UserV1:
      type: object
      required:
        - id
        - name
        - email
      properties:
        id:
          type: integer
        name:
          type: string
        email:
          type: string
          format: email
```

```yaml
# openapi-v2.yaml
openapi: 3.0.0
info:
  title: My API
  version: 2.0.0
  description: Version 2 with enhanced user model

paths:
  /users:
    get:
      summary: List users
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  users:
                    type: array
                    items:
                      $ref: '#/components/schemas/UserV2'

components:
  schemas:
    UserV2:
      type: object
      required:
        - id
        - firstName
        - lastName
        - email
      properties:
        id:
          type: integer
        firstName:
          type: string
        lastName:
          type: string
        email:
          type: string
          format: email
        phone:
          type: string
          nullable: true
        name:
          type: string
          deprecated: true
          description: 'Deprecated: Use firstName and lastName instead'
```

### 标记废弃字段

```yaml
components:
  schemas:
    User:
      type: object
      properties:
        name:
          type: string
          deprecated: true
          description: |
            **Deprecated**: This field will be removed in v3.0.
            Use `firstName` and `lastName` instead.

            Migration guide: https://docs.example.com/migration/v2-to-v3
        firstName:
          type: string
        lastName:
          type: string
```

## GraphQL 兼容性

### GraphQL 演进优势

GraphQL 天然支持 API 演进:
- 客户端只请求需要的字段
- 添加新字段不影响现有查询
- 使用 `@deprecated` 指令标记废弃字段

### 安全的变更

```graphql
# ✅ 安全：添加新字段
type User {
  id: ID!
  name: String!
  email: String!
  phone: String        # 新增字段
  createdAt: DateTime  # 新增字段
}

# ✅ 安全：添加可选参数
type Query {
  users(
    limit: Int
    offset: Int
    filter: String  # 新增可选参数
  ): [User!]!
}

# ✅ 安全：扩展联合类型
union SearchResult = User | Post | Comment | Product  # 新增 Product
```

### 破坏性变更

```graphql
# ❌ 破坏性：删除字段
type User {
  id: ID!
  # name: String!  # 删除字段 - 破坏性
  email: String!
}

# ❌ 破坏性：改变字段类型
type User {
  id: ID!
  age: String!  # 之前是 Int! - 破坏性
}

# ❌ 破坏性：参数变为必需
type Query {
  user(id: ID!): User  # 之前 id 是可选 - 破坏性
}
```

### 使用 @deprecated 指令

```graphql
type User {
  id: ID!

  name: String! @deprecated(reason: "Use firstName and lastName instead")
  firstName: String!
  lastName: String!

  email: String!
}

# 查询时会收到警告
query {
  user(id: "1") {
    name  # Warning: Field 'name' is deprecated
    email
  }
}
```

### GraphQL 验证工具

```bash
# 使用 graphql-inspector 检测破坏性变更
npx graphql-inspector diff old-schema.graphql new-schema.graphql

# 输出示例
✖ Field 'User.name' was removed
✖ Field 'User.age' changed type from Int! to String!
✔ Field 'User.phone' was added
```

## 弃用策略

### 弃用生命周期

```
1. 公告阶段（0-3 个月）
   - 文档标记为 deprecated
   - 添加警告日志
   - 通知客户端开发者

2. 警告阶段（3-6 个月）
   - API 响应包含 Deprecation header
   - 提供迁移指南
   - 监控使用情况

3. 限制阶段（6-9 个月）
   - 对新客户端禁用
   - 现有客户端限流
   - 强制迁移通知

4. 移除阶段（9-12 个月）
   - 正式移除 API
   - 返回 410 Gone
```

### 弃用通知实现

```typescript
// ✅ 添加 Deprecation 响应头
app.get('/api/v1/users', (req, res) => {
  res.set({
    'Deprecation': 'true',
    'Sunset': 'Sat, 31 Dec 2024 23:59:59 GMT',  // 移除日期
    'Link': '<https://docs.example.com/migration>; rel="deprecation"'
  });

  // 记录使用废弃 API 的客户端
  logger.warn('Deprecated API used', {
    endpoint: '/api/v1/users',
    clientId: req.headers['x-client-id'],
    userAgent: req.headers['user-agent']
  });

  const users = getUsersV1();
  res.json(users);
});
```

```java
// ✅ 使用 @Deprecated 注解
@RestController
@RequestMapping("/api/v1")
public class UserControllerV1 {

    /**
     * @deprecated Use /api/v2/users instead. This endpoint will be removed on 2024-12-31.
     * Migration guide: https://docs.example.com/migration/v1-to-v2
     */
    @Deprecated(since = "2.0", forRemoval = true)
    @GetMapping("/users")
    public List<UserV1> getUsers(
        @RequestHeader(value = "X-Client-Id", required = false) String clientId
    ) {
        // 记录使用情况
        deprecationLogger.warn("Client {} using deprecated endpoint /api/v1/users", clientId);

        return userService.getUsersV1();
    }
}
```

### 迁移指南模板

```markdown
# API v1 to v2 Migration Guide

## Overview
Version 2 introduces a more flexible user model with separated name fields.

## Breaking Changes

### 1. User name field split

**Before (v1)**:
```json
{
  "id": 1,
  "name": "Alice Smith",
  "email": "alice@example.com"
}
```

**After (v2)**:
```json
{
  "id": 1,
  "firstName": "Alice",
  "lastName": "Smith",
  "email": "alice@example.com"
}
```

**Migration**:
```typescript
// Before
const userName = user.name;

// After
const userName = `${user.firstName} ${user.lastName}`;
```

## Timeline

- **2024-07-01**: v2 released, v1 marked deprecated
- **2024-10-01**: v1 rate limiting begins
- **2024-12-31**: v1 removed

## Support

For help migrating, contact api-support@example.com
```

## 测试和验证

### 契约测试

```typescript
// ✅ 使用 Pact 进行契约测试
import { Pact } from '@pact-foundation/pact';

describe('User API Contract', () => {
  const provider = new Pact({
    consumer: 'WebApp',
    provider: 'UserAPI',
  });

  it('returns user data in expected format', async () => {
    await provider.addInteraction({
      state: 'user exists',
      uponReceiving: 'a request for user data',
      withRequest: {
        method: 'GET',
        path: '/api/v1/users/1',
      },
      willRespondWith: {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
        body: {
          id: 1,
          name: 'Alice Smith',  // 契约保证这些字段存在
          email: 'alice@example.com',
        },
      },
    });

    const response = await api.getUser(1);
    expect(response).toHaveProperty('name');
    expect(response).toHaveProperty('email');
  });
});
```

### 向后兼容性测试

```typescript
// ✅ 测试旧客户端与新 API 的兼容性
describe('Backward Compatibility', () => {
  it('V1 client works with V2 API', async () => {
    // 模拟 V1 客户端请求
    const response = await fetch('/api/v2/users/1', {
      headers: {
        'Accept': 'application/json',  // V1 Accept header
      }
    });

    const user = await response.json();

    // V1 客户端期望的字段应该存在
    expect(user).toHaveProperty('name');
    expect(user).toHaveProperty('email');

    // V2 新增字段也应该存在
    expect(user).toHaveProperty('firstName');
    expect(user).toHaveProperty('lastName');
  });

  it('V1 request format works with V2 API', async () => {
    // V1 客户端发送旧格式
    const response = await fetch('/api/v2/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: 'Alice Smith',  // V1 格式
        email: 'alice@example.com'
      })
    });

    expect(response.status).toBe(201);
  });
});
```

### API 变更影响分析

```bash
# ✅ 分析 API 变更的影响范围
npx openapi-diff \
  --breaking-only \
  --format markdown \
  old-spec.yaml new-spec.yaml \
  > breaking-changes.md
```

```python
# ✅ 分析客户端使用情况
# scripts/analyze-api-usage.py
import json
from collections import Counter

def analyze_deprecated_endpoints(log_file):
    """分析废弃端点的使用情况"""
    endpoint_usage = Counter()
    client_usage = {}

    with open(log_file) as f:
        for line in f:
            log = json.loads(line)
            if log.get('deprecated'):
                endpoint = log['endpoint']
                client_id = log.get('client_id', 'unknown')

                endpoint_usage[endpoint] += 1

                if client_id not in client_usage:
                    client_usage[client_id] = Counter()
                client_usage[client_id][endpoint] += 1

    print("## Deprecated Endpoint Usage\n")
    for endpoint, count in endpoint_usage.most_common():
        print(f"- {endpoint}: {count} requests")

    print("\n## Top Clients Using Deprecated APIs\n")
    for client_id, endpoints in sorted(
        client_usage.items(),
        key=lambda x: sum(x[1].values()),
        reverse=True
    )[:10]:
        total = sum(endpoints.values())
        print(f"\n### {client_id} ({total} requests)")
        for endpoint, count in endpoints.most_common():
            print(f"  - {endpoint}: {count}")

if __name__ == '__main__':
    analyze_deprecated_endpoints('api-access.log')
```

## 检查清单

### 设计阶段

- [ ] 定义清晰的版本控制策略
- [ ] 编写 OpenAPI/GraphQL schema
- [ ] 识别潜在的破坏性变更
- [ ] 规划向后兼容性策略
- [ ] 准备迁移指南

### 实现阶段

- [ ] 实现版本化端点
- [ ] 添加废弃警告机制
- [ ] 保留旧字段（标记为 deprecated）
- [ ] 编写契约测试
- [ ] 更新 API 文档

### 发布阶段

- [ ] 运行兼容性测试套件
- [ ] 检查 OpenAPI diff
- [ ] 通知客户端开发者
- [ ] 监控错误率和使用情况
- [ ] 提供技术支持

### 维护阶段

- [ ] 定期检查废弃 API 使用情况
- [ ] 与客户端团队沟通迁移进度
- [ ] 执行弃用时间线
- [ ] 安全移除旧版本 API

## 最佳实践总结

1. **优先兼容性**: 默认保持向后兼容，只在绝对必要时引入破坏性变更
2. **渐进式演进**: 使用扩展模式，逐步添加新功能
3. **清晰沟通**: 提前公告变更，提供详细迁移指南
4. **自动化测试**: 使用契约测试和兼容性测试防止意外破坏
5. **监控使用**: 追踪 API 使用情况，了解迁移进度
6. **文档先行**: 在实现前更新 API 规范和文档
7. **灵活版本**: 支持多个版本并行运行，给客户端足够迁移时间
8. **明确时间线**: 为弃用和移除设定清晰的时间表
