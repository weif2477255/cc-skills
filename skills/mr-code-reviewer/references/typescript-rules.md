# TypeScript/JavaScript 代码检查规则

本文档提供 TypeScript 和 JavaScript 前端代码的详细检查规则和最佳实践。

## 目录

- [现代 JavaScript/TypeScript 模式](#现代-javascripttypescript-模式)
- [React/Vue 最佳实践](#reactvue-最佳实践)
- [前端安全检查](#前端安全检查)
- [性能优化](#性能优化)
- [代码异味](#代码异味)
- [重构模式](#重构模式)

## 现代 JavaScript/TypeScript 模式

### 类型安全

**使用严格的 TypeScript 配置**
```typescript
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,              // 启用所有严格检查
    "noImplicitAny": true,       // 禁止隐式 any
    "strictNullChecks": true,    // 严格空值检查
    "noUnusedLocals": true,      // 检查未使用的局部变量
    "noUnusedParameters": true   // 检查未使用的参数
  }
}
```

**避免 any 类型**
```typescript
// ❌ 避免：使用 any
function processData(data: any) {
  return data.value;  // 无类型安全
}

// ✅ 推荐：使用具体类型
interface UserData {
  id: string;
  name: string;
  email: string;
}

function processData(data: UserData) {
  return data.name;  // 类型安全
}

// ✅ 或使用泛型
function processData<T extends { value: string }>(data: T) {
  return data.value;
}
```

### 异步编程

**使用 async/await 替代回调**
```typescript
// ❌ 回调地狱
function fetchUserData(userId: string, callback: (data: User) => void) {
  fetchUser(userId, (user) => {
    fetchOrders(user.id, (orders) => {
      fetchOrderDetails(orders[0].id, (details) => {
        callback({ user, orders, details });
      });
    });
  });
}

// ✅ 使用 async/await
async function fetchUserData(userId: string): Promise<UserData> {
  const user = await fetchUser(userId);
  const orders = await fetchOrders(user.id);
  const details = await fetchOrderDetails(orders[0].id);
  return { user, orders, details };
}
```

**错误处理**
```typescript
// ❌ 忽略错误
async function fetchData() {
  const data = await api.get('/data');
  return data;
}

// ✅ 适当的错误处理
async function fetchData(): Promise<Data> {
  try {
    const response = await api.get('/data');
    return response.data;
  } catch (error) {
    if (error instanceof ApiError) {
      logger.error('API error:', error.message);
      throw new DataFetchError('Failed to fetch data', error);
    }
    throw error;
  }
}
```

### 不可变性

```typescript
// ❌ 直接修改对象
function updateUser(user: User, name: string) {
  user.name = name;  // 修改原对象
  return user;
}

// ✅ 返回新对象
function updateUser(user: User, name: string): User {
  return { ...user, name };  // 创建新对象
}

// ✅ 使用 Immer 处理复杂更新
import { produce } from 'immer';

function updateNestedData(state: State, value: string): State {
  return produce(state, draft => {
    draft.user.profile.name = value;
  });
}
```

## React/Vue 最佳实践

### React Hooks 最佳实践

**正确使用 useEffect**
```typescript
// ❌ 缺少依赖项
function UserProfile({ userId }: Props) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, []);  // ❌ 缺少 userId 依赖
}

// ✅ 完整的依赖项
function UserProfile({ userId }: Props) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    let cancelled = false;

    fetchUser(userId).then(data => {
      if (!cancelled) {
        setUser(data);
      }
    });

    return () => {
      cancelled = true;  // 清理函数
    };
  }, [userId]);  // ✅ 包含所有依赖
}
```

**避免不必要的重渲染**
```typescript
// ❌ 每次渲染都创建新函数
function TodoList({ todos }: Props) {
  return (
    <ul>
      {todos.map(todo => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={() => toggleTodo(todo.id)}  // ❌ 每次创建新函数
        />
      ))}
    </ul>
  );
}

// ✅ 使用 useCallback 缓存函数
function TodoList({ todos }: Props) {
  const handleToggle = useCallback((id: string) => {
    toggleTodo(id);
  }, []);

  return (
    <ul>
      {todos.map(todo => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={handleToggle}
        />
      ))}
    </ul>
  );
}
```

**使用 useMemo 优化计算**
```typescript
// ❌ 每次渲染都重新计算
function ExpensiveComponent({ items }: Props) {
  const total = items.reduce((sum, item) => sum + item.price, 0);  // 每次都计算
  return <div>Total: {total}</div>;
}

// ✅ 使用 useMemo 缓存计算结果
function ExpensiveComponent({ items }: Props) {
  const total = useMemo(
    () => items.reduce((sum, item) => sum + item.price, 0),
    [items]
  );
  return <div>Total: {total}</div>;
}
```

### Vue 3 Composition API

**正确使用响应式**
```typescript
// ❌ 解构丢失响应性
import { reactive } from 'vue';

const state = reactive({ count: 0 });
const { count } = state;  // ❌ count 不再是响应式

// ✅ 使用 toRefs 保持响应性
import { reactive, toRefs } from 'vue';

const state = reactive({ count: 0 });
const { count } = toRefs(state);  // ✅ count 保持响应式
```

**组合式函数（Composables）**
```typescript
// ✅ 可复用的组合式函数
export function useUser(userId: Ref<string>) {
  const user = ref<User | null>(null);
  const loading = ref(false);
  const error = ref<Error | null>(null);

  const fetchUser = async () => {
    loading.value = true;
    error.value = null;
    try {
      user.value = await api.getUser(userId.value);
    } catch (e) {
      error.value = e as Error;
    } finally {
      loading.value = false;
    }
  };

  watchEffect(() => {
    fetchUser();
  });

  return { user, loading, error, refetch: fetchUser };
}
```

## 前端安全检查

### XSS（跨站脚本攻击）防护

**危险的 HTML 注入**
```typescript
// ❌ 危险：直接插入 HTML
function UserComment({ comment }: Props) {
  return <div dangerouslySetInnerHTML={{ __html: comment }} />;  // ❌ XSS 风险
}

// ✅ 安全：使用文本内容
function UserComment({ comment }: Props) {
  return <div>{comment}</div>;  // React 自动转义
}

// ✅ 如果必须插入 HTML，使用 DOMPurify 清理
import DOMPurify from 'dompurify';

function UserComment({ comment }: Props) {
  const sanitized = DOMPurify.sanitize(comment);
  return <div dangerouslySetInnerHTML={{ __html: sanitized }} />;
}
```

**URL 注入防护**
```typescript
// ❌ 危险：未验证的 URL
function ExternalLink({ url }: Props) {
  return <a href={url}>Link</a>;  // ❌ 可能是 javascript: 协议
}

// ✅ 安全：验证 URL 协议
function ExternalLink({ url }: Props) {
  const isValidUrl = (url: string) => {
    try {
      const parsed = new URL(url);
      return ['http:', 'https:'].includes(parsed.protocol);
    } catch {
      return false;
    }
  };

  if (!isValidUrl(url)) {
    return null;
  }

  return <a href={url} rel="noopener noreferrer">Link</a>;
}
```

### CSRF（跨站请求伪造）防护

```typescript
// ✅ 在请求中包含 CSRF token
const api = axios.create({
  baseURL: '/api',
  headers: {
    'X-CSRF-Token': getCsrfToken(),
  },
});

// ✅ 使用 SameSite cookie
// 服务端设置：Set-Cookie: sessionId=...; SameSite=Strict; Secure
```

### 敏感信息泄露

```typescript
// ❌ 危险：在客户端存储敏感信息
localStorage.setItem('apiKey', 'sk_live_abc123');  // ❌ 不要这样做
localStorage.setItem('password', userPassword);     // ❌ 绝对不要

// ✅ 安全：仅存储非敏感信息
localStorage.setItem('theme', 'dark');
localStorage.setItem('language', 'en');

// ✅ 敏感信息使用 HttpOnly cookie（服务端设置）
// Set-Cookie: sessionId=...; HttpOnly; Secure; SameSite=Strict
```

## 性能优化

### 代码分割和懒加载

```typescript
// ❌ 一次性加载所有组件
import Dashboard from './Dashboard';
import Settings from './Settings';
import Reports from './Reports';

// ✅ 使用动态导入进行代码分割
const Dashboard = lazy(() => import('./Dashboard'));
const Settings = lazy(() => import('./Settings'));
const Reports = lazy(() => import('./Reports'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/reports" element={<Reports />} />
      </Routes>
    </Suspense>
  );
}
```

### 虚拟化长列表

```typescript
// ❌ 渲染大量 DOM 元素
function LargeList({ items }: { items: Item[] }) {
  return (
    <div>
      {items.map(item => (
        <ItemCard key={item.id} item={item} />
      ))}
    </div>
  );  // 10000+ 个元素会导致性能问题
}

// ✅ 使用虚拟化
import { FixedSizeList } from 'react-window';

function LargeList({ items }: { items: Item[] }) {
  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={80}
      width="100%"
    >
      {({ index, style }) => (
        <div style={style}>
          <ItemCard item={items[index]} />
        </div>
      )}
    </FixedSizeList>
  );
}
```

### 防抖和节流

```typescript
// ❌ 频繁触发搜索
function SearchInput() {
  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    searchAPI(e.target.value);  // 每次输入都调用 API
  };

  return <input onChange={handleChange} />;
}

// ✅ 使用防抖
import { debounce } from 'lodash';

function SearchInput() {
  const debouncedSearch = useMemo(
    () => debounce((value: string) => {
      searchAPI(value);
    }, 300),
    []
  );

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    debouncedSearch(e.target.value);
  };

  return <input onChange={handleChange} />;
}
```

### 图片优化

```typescript
// ❌ 加载原始大图
function ProductImage({ src }: Props) {
  return <img src={src} alt="Product" />;
}

// ✅ 响应式图片和懒加载
function ProductImage({ src, alt }: Props) {
  return (
    <img
      src={src}
      srcSet={`
        ${src}?w=400 400w,
        ${src}?w=800 800w,
        ${src}?w=1200 1200w
      `}
      sizes="(max-width: 600px) 400px, (max-width: 1200px) 800px, 1200px"
      loading="lazy"
      alt={alt}
    />
  );
}
```

## 代码异味

### 长函数

```typescript
// ❌ 长函数（>50 行）
function processCheckout(cart: Cart, user: User) {
  // 验证逻辑 20 行
  if (!cart.items.length) { /* ... */ }
  if (!user.address) { /* ... */ }

  // 计算逻辑 30 行
  let total = 0;
  for (const item of cart.items) { /* ... */ }

  // 支付逻辑 40 行
  const payment = processPayment(/* ... */);

  // 通知逻辑 20 行
  sendEmail(/* ... */);
}

// ✅ 提取函数
function processCheckout(cart: Cart, user: User) {
  validateCheckout(cart, user);
  const total = calculateTotal(cart);
  const payment = processPayment(total, user);
  sendNotifications(user, payment);
  return payment;
}
```

### 复杂的条件语句

```typescript
// ❌ 复杂的嵌套条件
function getDiscount(user: User, order: Order) {
  if (user.isPremium) {
    if (order.total > 1000) {
      if (user.loyaltyPoints > 500) {
        return 0.25;
      } else {
        return 0.15;
      }
    } else {
      return 0.10;
    }
  } else {
    if (order.total > 500) {
      return 0.05;
    } else {
      return 0;
    }
  }
}

// ✅ 提前返回简化逻辑
function getDiscount(user: User, order: Order): number {
  if (!user.isPremium) {
    return order.total > 500 ? 0.05 : 0;
  }

  if (order.total <= 1000) {
    return 0.10;
  }

  return user.loyaltyPoints > 500 ? 0.25 : 0.15;
}

// ✅ 或使用策略模式
const discountStrategies = {
  premium: (order: Order, points: number) => {
    if (order.total > 1000) {
      return points > 500 ? 0.25 : 0.15;
    }
    return 0.10;
  },
  regular: (order: Order) => order.total > 500 ? 0.05 : 0,
};

function getDiscount(user: User, order: Order): number {
  const strategy = user.isPremium ? discountStrategies.premium : discountStrategies.regular;
  return strategy(order, user.loyaltyPoints);
}
```

### 魔法数字和字符串

```typescript
// ❌ 魔法数字和字符串
function calculateShipping(weight: number, type: string) {
  if (type === 'express') {
    return weight * 10;
  } else if (type === 'standard') {
    return weight * 5;
  }
  return weight * 2;
}

// ✅ 使用常量
const SHIPPING_RATES = {
  EXPRESS: 10,
  STANDARD: 5,
  ECONOMY: 2,
} as const;

enum ShippingType {
  EXPRESS = 'express',
  STANDARD = 'standard',
  ECONOMY = 'economy',
}

function calculateShipping(weight: number, type: ShippingType): number {
  const rate = SHIPPING_RATES[type.toUpperCase() as keyof typeof SHIPPING_RATES];
  return weight * rate;
}
```

## 重构模式

### 自定义 Hook 提取

```typescript
// ❌ 重复的状态管理逻辑
function UserProfile() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    setLoading(true);
    fetchUser()
      .then(setUser)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  // ...
}

function OrderList() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    setLoading(true);
    fetchOrders()
      .then(setOrders)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  // ...
}

// ✅ 提取自定义 Hook
function useAsync<T>(asyncFn: () => Promise<T>, deps: DependencyList = []) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    asyncFn()
      .then(result => {
        if (!cancelled) {
          setData(result);
        }
      })
      .catch(err => {
        if (!cancelled) {
          setError(err);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, deps);

  return { data, loading, error };
}

// 使用
function UserProfile() {
  const { data: user, loading, error } = useAsync(fetchUser);
  // ...
}

function OrderList() {
  const { data: orders, loading, error } = useAsync(fetchOrders);
  // ...
}
```

### 组件组合

```typescript
// ❌ 大型单体组件
function UserDashboard({ userId }: Props) {
  // 200+ 行代码
  // 用户信息、订单列表、统计数据、设置...
}

// ✅ 组合小组件
function UserDashboard({ userId }: Props) {
  return (
    <div>
      <UserProfile userId={userId} />
      <UserStats userId={userId} />
      <OrderList userId={userId} />
      <UserSettings userId={userId} />
    </div>
  );
}
```

## 检查清单

使用以下清单检查 TypeScript/JavaScript 代码：

### 类型安全
- [ ] 启用 TypeScript strict 模式
- [ ] 避免使用 any 类型
- [ ] 所有函数都有返回类型
- [ ] 正确处理 null 和 undefined

### 安全
- [ ] 无 XSS 漏洞（正确转义用户输入）
- [ ] 无敏感信息泄露（不在客户端存储密钥）
- [ ] URL 验证（防止 javascript: 协议）
- [ ] 使用 CSRF token
- [ ] 使用 Content Security Policy

### 性能
- [ ] 使用代码分割和懒加载
- [ ] 长列表使用虚拟化
- [ ] 防抖/节流频繁操作
- [ ] 图片懒加载和响应式
- [ ] 避免不必要的重渲染

### React/Vue 特定
- [ ] useEffect 包含所有依赖项
- [ ] 使用 useCallback/useMemo 优化
- [ ] 组件拆分合理（< 200 行）
- [ ] 正确使用 key 属性
- [ ] 避免在渲染中创建函数

### 代码质量
- [ ] 函数长度 < 20 行
- [ ] 圈复杂度 < 10
- [ ] 无魔法数字和字符串
- [ ] 清晰的命名
- [ ] 适当的错误处理
- [ ] 无重复代码
