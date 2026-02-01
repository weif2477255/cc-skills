# 安全检查规则

本文档提供全面的安全检查规则，基于 OWASP Top 10 和现代安全最佳实践。

## 目录

- [OWASP Top 10 检查清单](#owasp-top-10-检查清单)
- [输入验证和清理](#输入验证和清理)
- [认证和授权](#认证和授权)
- [加密和密钥管理](#加密和密钥管理)
- [会话管理](#会话管理)
- [API 安全](#api-安全)
- [容器和基础设施安全](#容器和基础设施安全)
- [安全配置](#安全配置)

## OWASP Top 10 检查清单

### A01:2021 - 访问控制失效 (Broken Access Control)

**风险**: 未经授权的用户可以访问敏感数据或执行特权操作。

**检查项**:
```typescript
// ❌ 危险：缺少授权检查
@Get('/users/:id')
async getUser(@Param('id') id: string) {
  return this.userService.findById(id);  // 任何人都可以访问
}

// ✅ 安全：基于资源的访问控制
@Get('/users/:id')
@UseGuards(AuthGuard, ResourceGuard)
async getUser(@Param('id') id: string, @CurrentUser() user: User) {
  // ResourceGuard 验证 user 是否有权访问该资源
  return this.userService.findById(id);
}
```

**Java 示例**:
```java
// ✅ 使用 Spring Security 方法级授权
@PreAuthorize("hasRole('ADMIN') or #userId == authentication.principal.id")
public User getUser(Long userId) {
    return userRepository.findById(userId)
        .orElseThrow(() -> new UserNotFoundException(userId));
}
```

**检查清单**:
- [ ] 所有敏感操作都有授权检查
- [ ] 使用基于资源的访问控制（而非仅基于角色）
- [ ] 默认拒绝访问（白名单模式）
- [ ] 验证用户只能访问自己的资源
- [ ] 防止水平权限提升（访问同级用户数据）
- [ ] 防止垂直权限提升（访问更高权限功能）

### A02:2021 - 加密失败 (Cryptographic Failures)

**风险**: 敏感数据未加密或使用弱加密算法。

**检查项**:
```python
# ❌ 危险：使用弱哈希算法
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()  # MD5 不安全

# ✅ 安全：使用现代密码哈希
from argon2 import PasswordHasher
ph = PasswordHasher()
password_hash = ph.hash(password)  # Argon2id 是推荐算法

# 验证
try:
    ph.verify(password_hash, password)
except:
    # 密码错误
    pass
```

**传输安全**:
```typescript
// ❌ 危险：HTTP 传输敏感数据
axios.post('http://api.example.com/login', {
  username: username,
  password: password  // 明文传输
});

// ✅ 安全：HTTPS + 额外加密
axios.post('https://api.example.com/login', {
  username: username,
  password: password  // HTTPS 加密传输
}, {
  headers: {
    'Strict-Transport-Security': 'max-age=31536000'
  }
});
```

**检查清单**:
- [ ] 敏感数据传输使用 TLS 1.2+
- [ ] 密码使用 Argon2id、bcrypt 或 PBKDF2 哈希
- [ ] 数据库中敏感字段加密存储
- [ ] 不使用弱算法（MD5、SHA1、DES）
- [ ] 加密密钥独立管理（不在代码中）
- [ ] 实施密钥轮换策略

### A03:2021 - 注入攻击 (Injection)

**风险**: SQL、NoSQL、OS 命令、LDAP 注入。

#### SQL 注入防护

```java
// ❌ 危险：字符串拼接
public List<User> findByName(String name) {
    String sql = "SELECT * FROM users WHERE name = '" + name + "'";
    return jdbcTemplate.query(sql, userRowMapper);
    // 攻击: name = "admin' OR '1'='1"
}

// ✅ 安全：参数化查询
public List<User> findByName(String name) {
    String sql = "SELECT * FROM users WHERE name = ?";
    return jdbcTemplate.query(sql, userRowMapper, name);
}

// ✅ 更好：使用 JPA
public interface UserRepository extends JpaRepository<User, Long> {
    List<User> findByName(String name);  // 自动参数化
}
```

#### NoSQL 注入防护

```javascript
// ❌ 危险：直接拼接查询
async function findUser(username) {
  const query = { username: username };  // 如果 username 是对象会有问题
  return db.users.findOne(query);
  // 攻击: username = { $ne: null }  // 返回任意用户
}

// ✅ 安全：类型验证
async function findUser(username) {
  if (typeof username !== 'string') {
    throw new Error('Invalid username type');
  }
  return db.users.findOne({ username: username });
}
```

#### OS 命令注入防护

```python
# ❌ 危险：使用 shell=True
import subprocess
filename = request.args.get('file')
subprocess.run(f"cat {filename}", shell=True)  # 命令注入风险

# ✅ 安全：参数化命令
import subprocess
import shlex
filename = request.args.get('file')
# 验证文件名
if not re.match(r'^[a-zA-Z0-9_.-]+$', filename):
    raise ValueError('Invalid filename')
subprocess.run(['cat', filename], shell=False)
```

**检查清单**:
- [ ] 所有数据库查询使用参数化
- [ ] ORM/框架的查询构建器使用正确
- [ ] 避免动态构建 SQL/NoSQL 查询
- [ ] 系统命令调用避免 shell 执行
- [ ] 输入验证（白名单优于黑名单）
- [ ] 使用最小权限数据库账户

### A04:2021 - 不安全设计 (Insecure Design)

**风险**: 缺少安全控制或安全控制设计不当。

**安全设计模式**:

```typescript
// ✅ 速率限制防止暴力破解
import rateLimit from 'express-rate-limit';

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 分钟
  max: 5,  // 最多 5 次尝试
  message: 'Too many login attempts, please try again later',
  standardHeaders: true,
  legacyHeaders: false,
});

app.post('/login', loginLimiter, loginHandler);
```

```java
// ✅ 防重放攻击
public class NonceValidator {
    private final Cache<String, Boolean> usedNonces;

    public NonceValidator() {
        this.usedNonces = CacheBuilder.newBuilder()
            .maximumSize(10000)
            .expireAfterWrite(5, TimeUnit.MINUTES)
            .build();
    }

    public void validateNonce(String nonce, Instant timestamp) {
        // 检查时间戳（防止过期请求）
        if (timestamp.isBefore(Instant.now().minus(5, ChronoUnit.MINUTES))) {
            throw new SecurityException("Request expired");
        }

        // 检查 nonce 是否已使用
        if (usedNonces.getIfPresent(nonce) != null) {
            throw new SecurityException("Nonce already used");
        }

        usedNonces.put(nonce, true);
    }
}
```

**检查清单**:
- [ ] 实施速率限制
- [ ] 防重放攻击机制
- [ ] 安全的密码重置流程
- [ ] 多因素认证支持
- [ ] 会话超时和并发会话控制
- [ ] 安全的文件上传限制

### A05:2021 - 安全配置错误 (Security Misconfiguration)

**风险**: 默认配置、详细错误信息泄露、未禁用的调试功能。

```typescript
// ❌ 危险：详细错误信息
app.use((err, req, res, next) => {
  res.status(500).json({
    error: err.message,
    stack: err.stack,  // ❌ 泄露堆栈信息
    query: req.query   // ❌ 泄露查询参数
  });
});

// ✅ 安全：通用错误信息
app.use((err, req, res, next) => {
  logger.error('Application error', {
    error: err,
    user: req.user?.id,
    path: req.path
  });

  res.status(500).json({
    error: 'Internal server error',
    requestId: req.id  // 用于追踪
  });
});
```

**安全头配置**:
```javascript
// ✅ 安全响应头
const helmet = require('helmet');

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", 'data:', 'https:'],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  },
  frameguard: { action: 'deny' },
  noSniff: true,
  xssFilter: true
}));
```

**检查清单**:
- [ ] 生产环境禁用调试模式
- [ ] 不返回详细错误信息
- [ ] 移除默认账户和密码
- [ ] 配置安全响应头
- [ ] 禁用不必要的服务和端口
- [ ] 保持依赖包更新

### A06:2021 - 易受攻击和过时的组件 (Vulnerable and Outdated Components)

**检查工具**:
```bash
# Node.js
npm audit
npm audit fix

# Python
pip-audit
safety check

# Java
mvn dependency-check:check
```

**依赖管理**:
```json
// package.json - 使用精确版本
{
  "dependencies": {
    "express": "4.18.2",  // ✅ 精确版本
    "helmet": "^7.0.0"    // 允许补丁更新
  },
  "devDependencies": {
    "npm-check-updates": "^16.0.0"
  }
}
```

**检查清单**:
- [ ] 定期运行安全扫描
- [ ] 及时更新依赖包
- [ ] 移除未使用的依赖
- [ ] 使用 lock 文件锁定版本
- [ ] 监控安全公告
- [ ] 评估第三方库的安全性

### A07:2021 - 身份识别和身份验证失败 (Identification and Authentication Failures)

**密码策略**:
```typescript
// ✅ 强密码验证
function validatePassword(password: string): boolean {
  const minLength = 12;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

  return (
    password.length >= minLength &&
    hasUpperCase &&
    hasLowerCase &&
    hasNumbers &&
    hasSpecialChar
  );
}
```

**会话管理**:
```java
// ✅ 安全的会话配置
@Configuration
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .sessionManagement()
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
                .maximumSessions(1)  // 限制并发会话
                .maxSessionsPreventsLogin(true)
            .and()
            .sessionFixation()
                .newSession()  // 登录后创建新会话
            .and()
            .rememberMe()
                .tokenValiditySeconds(86400)  // 1 天
                .useSecureCookie(true);

        return http.build();
    }
}
```

**检查清单**:
- [ ] 实施强密码策略
- [ ] 防止暴力破解（速率限制）
- [ ] 安全的密码恢复流程
- [ ] 会话固定攻击防护
- [ ] 登录后重新生成会话 ID
- [ ] 安全的"记住我"功能

### A08:2021 - 软件和数据完整性失败 (Software and Data Integrity Failures)

**依赖完整性验证**:
```yaml
# .gitlab-ci.yml - 使用 SRI 验证
script:
  - |
    # 验证下载文件的校验和
    curl -O https://example.com/package.tar.gz
    echo "expected-sha256-hash  package.tar.gz" | sha256sum -c -
```

**代码签名**:
```bash
# 验证 Docker 镜像签名
docker trust verify myregistry/myimage:tag
```

**检查清单**:
- [ ] 使用代码签名
- [ ] 验证依赖包完整性
- [ ] 使用安全的 CI/CD 流程
- [ ] 防止反序列化攻击
- [ ] 验证更新包的签名

### A09:2021 - 安全日志和监控失败 (Security Logging and Monitoring Failures)

**安全日志**:
```typescript
// ✅ 结构化安全日志
import winston from 'winston';

const logger = winston.createLogger({
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'security.log' })
  ]
});

function logSecurityEvent(event: string, details: any) {
  logger.warn({
    timestamp: new Date().toISOString(),
    event: event,
    userId: details.userId,
    ip: details.ip,
    userAgent: details.userAgent,
    result: details.result
  });
}

// 记录安全事件
app.post('/login', async (req, res) => {
  const result = await authenticateUser(req.body);

  logSecurityEvent('LOGIN_ATTEMPT', {
    userId: req.body.username,
    ip: req.ip,
    userAgent: req.get('user-agent'),
    result: result.success ? 'SUCCESS' : 'FAILURE'
  });

  // ... 处理登录
});
```

**需要记录的事件**:
- 登录成功/失败
- 权限提升尝试
- 敏感数据访问
- 配置更改
- 异常错误
- 账户锁定/解锁

**检查清单**:
- [ ] 记录所有安全相关事件
- [ ] 日志包含足够的上下文
- [ ] 日志不包含敏感信息（密码、token）
- [ ] 集中式日志管理
- [ ] 实时告警机制
- [ ] 日志完整性保护

### A10:2021 - 服务端请求伪造 (Server-Side Request Forgery - SSRF)

**SSRF 防护**:
```python
# ❌ 危险：未验证的 URL 请求
@app.route('/fetch')
def fetch_url():
    url = request.args.get('url')
    response = requests.get(url)  # ❌ SSRF 风险
    return response.content

# ✅ 安全：URL 白名单验证
from urllib.parse import urlparse

ALLOWED_HOSTS = ['api.example.com', 'cdn.example.com']
BLOCKED_IPS = ['127.0.0.1', '0.0.0.0', '169.254.169.254']  # 防止访问内网

@app.route('/fetch')
def fetch_url():
    url = request.args.get('url')

    # 解析 URL
    parsed = urlparse(url)

    # 验证协议
    if parsed.scheme not in ['http', 'https']:
        return 'Invalid protocol', 400

    # 验证主机名
    if parsed.hostname not in ALLOWED_HOSTS:
        return 'Host not allowed', 403

    # 解析 IP 并检查是否为内网
    import socket
    try:
        ip = socket.gethostbyname(parsed.hostname)
        if ip in BLOCKED_IPS or ip.startswith('10.') or ip.startswith('192.168.'):
            return 'Internal IP not allowed', 403
    except socket.gaierror:
        return 'Invalid hostname', 400

    response = requests.get(url, timeout=5)
    return response.content
```

**检查清单**:
- [ ] URL 白名单验证
- [ ] 禁止访问内网地址
- [ ] 验证协议（仅允许 http/https）
- [ ] DNS 重绑定攻击防护
- [ ] 设置请求超时
- [ ] 限制响应大小

## 输入验证和清理

### 通用原则

1. **白名单优于黑名单**
2. **在服务端验证，不要仅依赖客户端**
3. **验证数据类型、长度、格式、范围**

### 输入验证示例

```typescript
// ✅ 全面的输入验证
import Joi from 'joi';

const userSchema = Joi.object({
  username: Joi.string()
    .alphanum()
    .min(3)
    .max(30)
    .required(),

  email: Joi.string()
    .email()
    .required(),

  age: Joi.number()
    .integer()
    .min(18)
    .max(120)
    .required(),

  website: Joi.string()
    .uri()
    .optional()
});

function createUser(req, res) {
  const { error, value } = userSchema.validate(req.body);

  if (error) {
    return res.status(400).json({ error: error.details[0].message });
  }

  // 使用验证后的 value
  userService.create(value);
}
```

### 特殊字符转义

```javascript
// ✅ HTML 转义
function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// ✅ SQL 转义（使用参数化查询更好）
// ✅ JavaScript 转义
function escapeJavaScript(unsafe) {
  return unsafe
    .replace(/\\/g, '\\\\')
    .replace(/'/g, "\\'")
    .replace(/"/g, '\\"')
    .replace(/\n/g, '\\n')
    .replace(/\r/g, '\\r');
}
```

## 认证和授权

### JWT 最佳实践

```typescript
// ✅ 安全的 JWT 实现
import jwt from 'jsonwebtoken';
import crypto from 'crypto';

const JWT_SECRET = process.env.JWT_SECRET;  // 从环境变量读取
const JWT_EXPIRY = '15m';  // 短期 token
const REFRESH_TOKEN_EXPIRY = '7d';

interface TokenPayload {
  userId: string;
  role: string;
  tokenId: string;  // 用于撤销
}

function generateTokens(userId: string, role: string) {
  const tokenId = crypto.randomUUID();

  const accessToken = jwt.sign(
    { userId, role, tokenId },
    JWT_SECRET,
    {
      expiresIn: JWT_EXPIRY,
      algorithm: 'HS256',
      issuer: 'your-app',
      audience: 'your-app-api'
    }
  );

  const refreshToken = jwt.sign(
    { userId, tokenId, type: 'refresh' },
    JWT_SECRET,
    { expiresIn: REFRESH_TOKEN_EXPIRY }
  );

  // 存储 tokenId 以支持撤销
  redisClient.setex(`token:${tokenId}`, 15 * 60, 'active');

  return { accessToken, refreshToken };
}

function verifyToken(token: string): TokenPayload {
  try {
    const payload = jwt.verify(token, JWT_SECRET, {
      issuer: 'your-app',
      audience: 'your-app-api'
    }) as TokenPayload;

    // 检查 token 是否已被撤销
    const isValid = redisClient.get(`token:${payload.tokenId}`);
    if (!isValid) {
      throw new Error('Token revoked');
    }

    return payload;
  } catch (error) {
    throw new Error('Invalid token');
  }
}
```

### OAuth 2.0 实现

```java
// ✅ Spring Security OAuth2 配置
@Configuration
@EnableWebSecurity
public class OAuth2SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .oauth2Login()
                .authorizationEndpoint()
                    .baseUri("/oauth2/authorize")
                .and()
                .redirectionEndpoint()
                    .baseUri("/oauth2/callback/*")
                .and()
                .userInfoEndpoint()
                    .userService(customOAuth2UserService);

        http
            .authorizeHttpRequests()
                .requestMatchers("/public/**").permitAll()
                .requestMatchers("/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated();

        return http.build();
    }
}
```

## 加密和密钥管理

### 密钥存储

```bash
# ✅ 使用环境变量或密钥管理服务
export DATABASE_PASSWORD="secret-password"
export API_KEY="sk_live_abc123"

# ✅ 使用 AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id prod/database/password
```

```python
# ✅ 从环境变量读取
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
if not DATABASE_PASSWORD:
    raise ValueError('DATABASE_PASSWORD not set')
```

### 数据加密

```typescript
// ✅ AES-256-GCM 加密
import crypto from 'crypto';

const ALGORITHM = 'aes-256-gcm';
const KEY = Buffer.from(process.env.ENCRYPTION_KEY!, 'hex');  // 32 字节

function encrypt(plaintext: string): string {
  const iv = crypto.randomBytes(12);  // GCM 推荐 12 字节 IV
  const cipher = crypto.createCipheriv(ALGORITHM, KEY, iv);

  let ciphertext = cipher.update(plaintext, 'utf8', 'hex');
  ciphertext += cipher.final('hex');

  const authTag = cipher.getAuthTag();

  // 返回: iv + authTag + ciphertext
  return iv.toString('hex') + authTag.toString('hex') + ciphertext;
}

function decrypt(encrypted: string): string {
  const iv = Buffer.from(encrypted.slice(0, 24), 'hex');
  const authTag = Buffer.from(encrypted.slice(24, 56), 'hex');
  const ciphertext = encrypted.slice(56);

  const decipher = crypto.createDecipheriv(ALGORITHM, KEY, iv);
  decipher.setAuthTag(authTag);

  let plaintext = decipher.update(ciphertext, 'hex', 'utf8');
  plaintext += decipher.final('utf8');

  return plaintext;
}
```

## 检查清单模板

### Critical 级别（必须修复）

- [ ] SQL/NoSQL 注入漏洞
- [ ] XSS 跨站脚本漏洞
- [ ] 硬编码密钥或密码
- [ ] 缺少认证的敏感操作
- [ ] 不安全的反序列化
- [ ] 服务端请求伪造 (SSRF)

### High 级别（高优先级）

- [ ] 缺少授权检查
- [ ] 弱加密算法（MD5、SHA1）
- [ ] 敏感信息泄露
- [ ] CSRF 防护缺失
- [ ] 不安全的随机数生成
- [ ] 路径遍历漏洞

### Medium 级别（中优先级）

- [ ] 缺少速率限制
- [ ] 详细错误信息泄露
- [ ] 缺少安全响应头
- [ ] 会话管理不当
- [ ] 输入验证不充分
- [ ] 过时的依赖包

### Low 级别（低优先级）

- [ ] 日志记录不完整
- [ ] 缺少输入长度限制
- [ ] 不安全的 Cookie 设置
- [ ] 缺少内容安全策略 (CSP)
- [ ] HTTP 而非 HTTPS（开发环境除外）
