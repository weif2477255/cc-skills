# Java 代码检查规则

本文档提供 Java 后端代码的详细检查规则和最佳实践。

## 目录

- [企业模式和 Spring 框架](#企业模式和-spring-框架)
- [安全检查](#安全检查)
- [性能优化](#性能优化)
- [代码异味](#代码异味)
- [重构模式](#重构模式)

## 企业模式和 Spring 框架

### 依赖注入最佳实践

**推荐：构造函数注入**
```java
// 推荐：构造函数注入（不可变、易测试）
@Service
public class OrderService {
    private final OrderRepository repository;
    private final EmailService emailService;

    public OrderService(OrderRepository repository, EmailService emailService) {
        this.repository = repository;
        this.emailService = emailService;
    }
}
```

**避免：字段注入**
```java
// 避免：字段注入（难以测试、隐藏依赖）
@Service
public class OrderService {
    @Autowired
    private OrderRepository repository;  // ❌ 不推荐
}
```

### Repository 模式

```java
// 正确的 Repository 接口设计
public interface OrderRepository extends JpaRepository<Order, Long> {
    // 使用方法命名约定
    List<Order> findByCustomerIdAndStatus(Long customerId, OrderStatus status);

    // 复杂查询使用 @Query
    @Query("SELECT o FROM Order o WHERE o.total > :minTotal AND o.createdAt > :date")
    List<Order> findHighValueRecentOrders(@Param("minTotal") BigDecimal minTotal,
                                          @Param("date") LocalDateTime date);
}
```

### Service 层事务管理

```java
@Service
@Transactional(readOnly = true)  // 默认只读事务
public class OrderService {

    @Transactional  // 写操作覆盖为读写事务
    public Order createOrder(OrderRequest request) {
        // 事务边界清晰
        Order order = new Order();
        // ... 业务逻辑
        return orderRepository.save(order);
    }

    // 只读操作使用类级别的 readOnly=true
    public Order getOrder(Long id) {
        return orderRepository.findById(id)
            .orElseThrow(() -> new OrderNotFoundException(id));
    }
}
```

## 安全检查

### SQL 注入防护

**危险：字符串拼接**
```java
// ❌ 危险：SQL 注入风险
public List<User> findByName(String name) {
    String sql = "SELECT * FROM users WHERE name = '" + name + "'";
    return jdbcTemplate.query(sql, userRowMapper);
}
```

**安全：参数化查询**
```java
// ✅ 安全：使用参数化查询
public List<User> findByName(String name) {
    String sql = "SELECT * FROM users WHERE name = ?";
    return jdbcTemplate.query(sql, userRowMapper, name);
}

// ✅ 更好：使用 JPA
public interface UserRepository extends JpaRepository<User, Long> {
    List<User> findByName(String name);  // 自动参数化
}
```

### 序列化漏洞

```java
// ❌ 危险：不安全的反序列化
public Object deserialize(byte[] data) {
    ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(data));
    return ois.readObject();  // 可能执行恶意代码
}

// ✅ 安全：使用白名单验证
public Object deserialize(byte[] data, Class<?> expectedClass) {
    ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(data)) {
        @Override
        protected Class<?> resolveClass(ObjectStreamClass desc)
                throws IOException, ClassNotFoundException {
            if (!desc.getName().equals(expectedClass.getName())) {
                throw new InvalidClassException("Unauthorized deserialization attempt");
            }
            return super.resolveClass(desc);
        }
    };
    return ois.readObject();
}
```

### 密钥和配置安全

```java
// ❌ 危险：硬编码密钥
public class PaymentService {
    private static final String API_KEY = "sk_live_abc123";  // ❌ 不要这样做
}

// ✅ 安全：使用环境变量或配置管理
@Service
public class PaymentService {
    @Value("${payment.api.key}")
    private String apiKey;  // 从配置文件或环境变量读取
}
```

### 认证和授权

```java
// Spring Security 方法级别授权
@Service
public class OrderService {

    @PreAuthorize("hasRole('ADMIN') or #userId == authentication.principal.id")
    public Order getOrder(Long orderId, Long userId) {
        return orderRepository.findById(orderId)
            .orElseThrow(() -> new OrderNotFoundException(orderId));
    }

    @PreAuthorize("hasAuthority('ORDER:WRITE')")
    public Order createOrder(OrderRequest request) {
        // 只有有权限的用户才能创建订单
        return orderRepository.save(new Order(request));
    }
}
```

## 性能优化

### JVM 调优关注点

**内存泄漏检测**
```java
// ❌ 潜在内存泄漏：静态集合持续增长
public class CacheManager {
    private static final Map<String, Object> cache = new HashMap<>();  // ❌ 永不清理

    public void put(String key, Object value) {
        cache.put(key, value);
    }
}

// ✅ 使用有界缓存
public class CacheManager {
    private final Cache<String, Object> cache = CacheBuilder.newBuilder()
        .maximumSize(1000)
        .expireAfterWrite(10, TimeUnit.MINUTES)
        .build();
}
```

### 并发编程

**线程安全问题**
```java
// ❌ 不安全：共享可变状态
public class Counter {
    private int count = 0;

    public void increment() {
        count++;  // ❌ 非原子操作
    }
}

// ✅ 安全：使用原子类
public class Counter {
    private final AtomicInteger count = new AtomicInteger(0);

    public void increment() {
        count.incrementAndGet();
    }
}
```

**死锁预防**
```java
// ❌ 潜在死锁：锁顺序不一致
public void transfer(Account from, Account to, BigDecimal amount) {
    synchronized (from) {
        synchronized (to) {
            from.debit(amount);
            to.credit(amount);
        }
    }
}

// ✅ 避免死锁：统一锁顺序
public void transfer(Account from, Account to, BigDecimal amount) {
    Account first = from.getId() < to.getId() ? from : to;
    Account second = from.getId() < to.getId() ? to : from;

    synchronized (first) {
        synchronized (second) {
            from.debit(amount);
            to.credit(amount);
        }
    }
}
```

### 数据库查询优化

**N+1 查询问题**
```java
// ❌ N+1 查询问题
@Entity
public class Order {
    @OneToMany(mappedBy = "order")
    private List<OrderItem> items;  // 懒加载
}

// 使用时触发 N+1 查询
List<Order> orders = orderRepository.findAll();  // 1 次查询
for (Order order : orders) {
    order.getItems().size();  // N 次查询
}

// ✅ 使用 JOIN FETCH
@Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.status = :status")
List<Order> findOrdersWithItems(@Param("status") OrderStatus status);
```

**批量操作**
```java
// ❌ 逐条插入
for (Order order : orders) {
    orderRepository.save(order);  // N 次数据库往返
}

// ✅ 批量插入
orderRepository.saveAll(orders);  // 批量操作
entityManager.flush();
entityManager.clear();  // 清理持久化上下文
```

## 代码异味

### 长方法

```java
// ❌ 长方法（>50 行）
public void processOrder(Order order) {
    // 验证逻辑 20 行
    if (order.getCustomerId() == null) { /* ... */ }
    if (order.getItems().isEmpty()) { /* ... */ }
    // ...

    // 计算逻辑 30 行
    BigDecimal total = BigDecimal.ZERO;
    for (OrderItem item : order.getItems()) { /* ... */ }
    // ...

    // 通知逻辑 40 行
    emailService.send(/* ... */);
    smsService.send(/* ... */);
    // ...
}

// ✅ 提取方法
public void processOrder(Order order) {
    validateOrder(order);
    BigDecimal total = calculateTotal(order);
    sendNotifications(order, total);
}

private void validateOrder(Order order) { /* ... */ }
private BigDecimal calculateTotal(Order order) { /* ... */ }
private void sendNotifications(Order order, BigDecimal total) { /* ... */ }
```

### 大类

```java
// ❌ 大类（>500 行，多个职责）
public class OrderManager {
    public void createOrder() { /* ... */ }
    public void validateOrder() { /* ... */ }
    public void calculateTotal() { /* ... */ }
    public void sendEmail() { /* ... */ }
    public void updateInventory() { /* ... */ }
    public void processPayment() { /* ... */ }
    // ... 更多方法
}

// ✅ 分解为多个类
public class OrderService {
    private final OrderValidator validator;
    private final OrderCalculator calculator;
    private final NotificationService notificationService;
    private final InventoryService inventoryService;
    private final PaymentService paymentService;

    public Order createOrder(OrderRequest request) {
        validator.validate(request);
        Order order = new Order(request);
        calculator.calculateTotal(order);
        return order;
    }
}
```

### 重复代码

```java
// ❌ 重复代码
public void processOnlineOrder(Order order) {
    if (order.getTotal().compareTo(BigDecimal.ZERO) <= 0) {
        throw new InvalidOrderException("Total must be positive");
    }
    // ... 在线订单特定逻辑
}

public void processOfflineOrder(Order order) {
    if (order.getTotal().compareTo(BigDecimal.ZERO) <= 0) {
        throw new InvalidOrderException("Total must be positive");
    }
    // ... 线下订单特定逻辑
}

// ✅ 提取公共方法
private void validateOrderTotal(Order order) {
    if (order.getTotal().compareTo(BigDecimal.ZERO) <= 0) {
        throw new InvalidOrderException("Total must be positive");
    }
}

public void processOnlineOrder(Order order) {
    validateOrderTotal(order);
    // ... 在线订单特定逻辑
}

public void processOfflineOrder(Order order) {
    validateOrderTotal(order);
    // ... 线下订单特定逻辑
}
```

## 重构模式

### 策略模式替代条件语句

```java
// ❌ 复杂的条件语句
public BigDecimal calculateShipping(Order order, String shippingType) {
    if (shippingType.equals("standard")) {
        return order.getWeight().multiply(new BigDecimal("5"));
    } else if (shippingType.equals("express")) {
        return order.getWeight().multiply(new BigDecimal("10"));
    } else if (shippingType.equals("overnight")) {
        return order.getWeight().multiply(new BigDecimal("20"));
    }
    throw new IllegalArgumentException("Unknown shipping type");
}

// ✅ 策略模式
public interface ShippingStrategy {
    BigDecimal calculate(Order order);
}

public class StandardShipping implements ShippingStrategy {
    public BigDecimal calculate(Order order) {
        return order.getWeight().multiply(new BigDecimal("5"));
    }
}

public class ExpressShipping implements ShippingStrategy {
    public BigDecimal calculate(Order order) {
        return order.getWeight().multiply(new BigDecimal("10"));
    }
}

public class ShippingCalculator {
    private final Map<String, ShippingStrategy> strategies;

    public BigDecimal calculate(Order order, String shippingType) {
        ShippingStrategy strategy = strategies.get(shippingType);
        if (strategy == null) {
            throw new IllegalArgumentException("Unknown shipping type");
        }
        return strategy.calculate(order);
    }
}
```

### 工厂模式

```java
// ✅ 工厂模式创建复杂对象
public interface PaymentProcessor {
    PaymentResult process(Payment payment);
}

@Component
public class PaymentProcessorFactory {
    private final Map<PaymentMethod, PaymentProcessor> processors;

    public PaymentProcessorFactory(List<PaymentProcessor> processorList) {
        this.processors = processorList.stream()
            .collect(Collectors.toMap(
                PaymentProcessor::getSupportedMethod,
                Function.identity()
            ));
    }

    public PaymentProcessor getProcessor(PaymentMethod method) {
        PaymentProcessor processor = processors.get(method);
        if (processor == null) {
            throw new UnsupportedPaymentMethodException(method);
        }
        return processor;
    }
}
```

### 模板方法模式

```java
// ✅ 模板方法模式定义算法骨架
public abstract class OrderProcessor {

    public final Order process(OrderRequest request) {
        validate(request);
        Order order = createOrder(request);
        enrichOrder(order);
        save(order);
        sendNotification(order);
        return order;
    }

    protected abstract void validate(OrderRequest request);
    protected abstract Order createOrder(OrderRequest request);
    protected abstract void enrichOrder(Order order);

    protected void save(Order order) {
        orderRepository.save(order);
    }

    protected void sendNotification(Order order) {
        notificationService.send(order);
    }
}

public class OnlineOrderProcessor extends OrderProcessor {
    @Override
    protected void validate(OrderRequest request) {
        // 在线订单特定验证
    }

    @Override
    protected Order createOrder(OrderRequest request) {
        // 在线订单创建逻辑
    }

    @Override
    protected void enrichOrder(Order order) {
        // 添加在线订单特定信息
    }
}
```

## 检查清单

使用以下清单检查 Java 代码：

### 架构和设计
- [ ] 遵循分层架构（Controller → Service → Repository）
- [ ] 使用依赖注入（构造函数注入优先）
- [ ] 接口和实现分离
- [ ] 遵循 SOLID 原则

### 安全
- [ ] 无 SQL 注入风险（使用参数化查询）
- [ ] 无硬编码密钥或敏感信息
- [ ] 正确实现认证和授权
- [ ] 安全的反序列化实现
- [ ] 输入验证和清理

### 性能
- [ ] 无 N+1 查询问题
- [ ] 使用批量操作
- [ ] 适当的缓存策略
- [ ] 线程安全的并发代码
- [ ] 无内存泄漏风险

### 代码质量
- [ ] 方法长度 < 20 行
- [ ] 类长度 < 200 行
- [ ] 圈复杂度 < 10
- [ ] 无重复代码
- [ ] 清晰的命名
- [ ] 适当的异常处理

### 测试
- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试覆盖关键路径
- [ ] 测试边界条件和异常情况
