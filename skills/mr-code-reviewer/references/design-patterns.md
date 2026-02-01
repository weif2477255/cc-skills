# 设计模式和 SOLID 原则

本文档提供 SOLID 原则概述和常用设计模式的简明指南。

## 目录

- [SOLID 原则](#solid-原则)
- [常用设计模式](#常用设计模式)
- [代码异味识别](#代码异味识别)

## SOLID 原则

### S - 单一职责原则 (SRP)

**定义**: 一个类应该只有一个引起变化的原因。

**示例**:
```python
# ❌ 违反 SRP：多个职责
class UserManager:
    def create_user(self, data):
        self.validate_data(data)      # 职责1：验证
        self.save_to_database(data)   # 职责2：持久化
        self.send_welcome_email(data) # 职责3：通知
        self.log_activity(data)       # 职责4：日志

# ✅ 符合 SRP：每个类一个职责
class UserValidator:
    def validate(self, data): pass

class UserRepository:
    def save(self, user): pass

class EmailService:
    def send_welcome_email(self, user): pass

class UserActivityLogger:
    def log_creation(self, user): pass
```

### O - 开闭原则 (OCP)

**定义**: 软件实体应该对扩展开放，对修改关闭。

**示例**:
```typescript
// ❌ 违反 OCP：添加新类型需要修改代码
class PaymentProcessor {
  process(type: string, amount: number) {
    if (type === 'credit') {
      // 信用卡逻辑
    } else if (type === 'paypal') {
      // PayPal 逻辑
    }
    // 添加新支付方式需要修改这个方法
  }
}

// ✅ 符合 OCP：通过扩展添加新类型
interface PaymentMethod {
  process(amount: number): void;
}

class CreditCardPayment implements PaymentMethod {
  process(amount: number) {
    // 信用卡逻辑
  }
}

class PayPalPayment implements PaymentMethod {
  process(amount: number) {
    // PayPal 逻辑
  }
}

class PaymentProcessor {
  process(method: PaymentMethod, amount: number) {
    method.process(amount);
  }
}
```

### L - 里氏替换原则 (LSP)

**定义**: 子类型必须能够替换其基类型。

**示例**:
```typescript
// ❌ 违反 LSP：Square 改变了 Rectangle 的行为
class Rectangle {
  constructor(protected width: number, protected height: number) {}

  setWidth(width: number) { this.width = width; }
  setHeight(height: number) { this.height = height; }
  area(): number { return this.width * this.height; }
}

class Square extends Rectangle {
  setWidth(width: number) {
    this.width = width;
    this.height = width;  // ❌ 改变了父类行为
  }
  setHeight(height: number) {
    this.width = height;
    this.height = height;  // ❌ 改变了父类行为
  }
}

// ✅ 符合 LSP：正确的抽象
interface Shape {
  area(): number;
}

class Rectangle implements Shape {
  constructor(private width: number, private height: number) {}
  area(): number { return this.width * this.height; }
}

class Square implements Shape {
  constructor(private side: number) {}
  area(): number { return this.side * this.side; }
}
```

### I - 接口隔离原则 (ISP)

**定义**: 客户端不应该依赖它不需要的接口。

**示例**:
```java
// ❌ 违反 ISP：胖接口
interface Worker {
    void work();
    void eat();
    void sleep();
}

class Robot implements Worker {
    public void work() { /* 工作 */ }
    public void eat() { /* 机器人不吃饭！ */ }
    public void sleep() { /* 机器人不睡觉！ */ }
}

// ✅ 符合 ISP：隔离接口
interface Workable {
    void work();
}

interface Eatable {
    void eat();
}

interface Sleepable {
    void sleep();
}

class Human implements Workable, Eatable, Sleepable {
    public void work() { /* 工作 */ }
    public void eat() { /* 吃饭 */ }
    public void sleep() { /* 睡觉 */ }
}

class Robot implements Workable {
    public void work() { /* 工作 */ }
}
```

### D - 依赖倒置原则 (DIP)

**定义**: 高层模块不应该依赖低层模块，两者都应该依赖抽象。

**示例**:
```python
# ❌ 违反 DIP：高层模块依赖低层模块
class MySQLDatabase:
    def save(self, data): pass

class OrderService:
    def __init__(self):
        self.db = MySQLDatabase()  # ❌ 紧耦合

    def create_order(self, order):
        self.db.save(order)

# ✅ 符合 DIP：依赖抽象
from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def save(self, data): pass

class MySQLDatabase(Database):
    def save(self, data): pass

class PostgresDatabase(Database):
    def save(self, data): pass

class OrderService:
    def __init__(self, db: Database):  # ✅ 依赖抽象
        self.db = db

    def create_order(self, order):
        self.db.save(order)
```

## 常用设计模式

### 工厂模式 (Factory Pattern)

**用途**: 创建对象时不指定具体类。

```typescript
interface Product {
  use(): void;
}

class ConcreteProductA implements Product {
  use() { console.log('Using Product A'); }
}

class ConcreteProductB implements Product {
  use() { console.log('Using Product B'); }
}

class ProductFactory {
  createProduct(type: string): Product {
    switch (type) {
      case 'A': return new ConcreteProductA();
      case 'B': return new ConcreteProductB();
      default: throw new Error('Unknown product type');
    }
  }
}
```

### 策略模式 (Strategy Pattern)

**用途**: 定义一系列算法，封装它们并使其可互换。

```python
from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, amount: float) -> float: pass

class NoDiscount(DiscountStrategy):
    def calculate(self, amount: float) -> float:
        return amount

class PercentageDiscount(DiscountStrategy):
    def __init__(self, percentage: float):
        self.percentage = percentage

    def calculate(self, amount: float) -> float:
        return amount * (1 - self.percentage)

class FixedDiscount(DiscountStrategy):
    def __init__(self, discount: float):
        self.discount = discount

    def calculate(self, amount: float) -> float:
        return max(0, amount - self.discount)

class PriceCalculator:
    def __init__(self, strategy: DiscountStrategy):
        self.strategy = strategy

    def calculate_price(self, amount: float) -> float:
        return self.strategy.calculate(amount)
```

### 观察者模式 (Observer Pattern)

**用途**: 定义对象间的一对多依赖，当一个对象状态改变时，所有依赖者都会收到通知。

```typescript
interface Observer {
  update(data: any): void;
}

class Subject {
  private observers: Observer[] = [];

  subscribe(observer: Observer) {
    this.observers.push(observer);
  }

  unsubscribe(observer: Observer) {
    this.observers = this.observers.filter(obs => obs !== observer);
  }

  notify(data: any) {
    this.observers.forEach(observer => observer.update(data));
  }
}

class EmailObserver implements Observer {
  update(data: any) {
    console.log('Sending email with:', data);
  }
}

class LogObserver implements Observer {
  update(data: any) {
    console.log('Logging:', data);
  }
}
```

### 装饰器模式 (Decorator Pattern)

**用途**: 动态地给对象添加职责。

```java
interface Coffee {
    double cost();
    String description();
}

class SimpleCoffee implements Coffee {
    public double cost() { return 2.0; }
    public String description() { return "Simple coffee"; }
}

abstract class CoffeeDecorator implements Coffee {
    protected Coffee coffee;

    public CoffeeDecorator(Coffee coffee) {
        this.coffee = coffee;
    }
}

class MilkDecorator extends CoffeeDecorator {
    public MilkDecorator(Coffee coffee) { super(coffee); }

    public double cost() { return coffee.cost() + 0.5; }
    public String description() { return coffee.description() + ", milk"; }
}

class SugarDecorator extends CoffeeDecorator {
    public SugarDecorator(Coffee coffee) { super(coffee); }

    public double cost() { return coffee.cost() + 0.2; }
    public String description() { return coffee.description() + ", sugar"; }
}

// 使用
Coffee coffee = new SimpleCoffee();
coffee = new MilkDecorator(coffee);
coffee = new SugarDecorator(coffee);
// cost: 2.7, description: "Simple coffee, milk, sugar"
```

### 模板方法模式 (Template Method Pattern)

**用途**: 定义算法骨架，将某些步骤延迟到子类。

```python
from abc import ABC, abstractmethod

class DataProcessor(ABC):
    def process(self):
        """模板方法"""
        self.read_data()
        self.validate_data()
        self.transform_data()
        self.save_data()

    @abstractmethod
    def read_data(self): pass

    @abstractmethod
    def validate_data(self): pass

    @abstractmethod
    def transform_data(self): pass

    def save_data(self):
        """默认实现，子类可以覆盖"""
        print("Saving data to database")

class CSVProcessor(DataProcessor):
    def read_data(self):
        print("Reading CSV file")

    def validate_data(self):
        print("Validating CSV data")

    def transform_data(self):
        print("Transforming CSV to records")

class JSONProcessor(DataProcessor):
    def read_data(self):
        print("Reading JSON file")

    def validate_data(self):
        print("Validating JSON schema")

    def transform_data(self):
        print("Parsing JSON objects")
```

### 仓储模式 (Repository Pattern)

**用途**: 封装数据访问逻辑，提供集合式接口。

```typescript
interface Repository<T> {
  findById(id: string): Promise<T | null>;
  findAll(): Promise<T[]>;
  save(entity: T): Promise<T>;
  delete(id: string): Promise<void>;
}

class UserRepository implements Repository<User> {
  async findById(id: string): Promise<User | null> {
    // 数据库查询逻辑
    return await db.users.findOne({ id });
  }

  async findAll(): Promise<User[]> {
    return await db.users.find();
  }

  async save(user: User): Promise<User> {
    return await db.users.save(user);
  }

  async delete(id: string): Promise<void> {
    await db.users.delete({ id });
  }
}
```

## 代码异味识别

### 常见代码异味清单

| 异味类型 | 描述 | 重构方法 |
|---------|------|---------|
| 长方法 | 方法超过 20 行 | 提取方法 |
| 大类 | 类超过 200 行 | 提取类 |
| 长参数列表 | 参数超过 3 个 | 引入参数对象 |
| 重复代码 | 相同代码出现多次 | 提取方法/类 |
| 发散式变化 | 一个类因不同原因多次修改 | 提取类 |
| 霰弹式修改 | 一个变化需要修改多个类 | 移动方法/字段 |
| 依恋情结 | 方法使用其他类的数据多于自己的 | 移动方法 |
| 数据泥团 | 相同数据项总是一起出现 | 提取类 |
| 基本类型偏执 | 过度使用基本类型 | 用对象替代基本类型 |
| Switch 语句 | 复杂的 switch 或 if-else | 用多态替代条件表达式 |
| 平行继承体系 | 为一个类添加子类时需要为另一个类添加子类 | 移动方法/字段 |
| 冗余类 | 类没有做足够的工作 | 内联类 |
| 纯稚的数据类 | 只有字段和getter/setter | 移动方法 |
| 被拒绝的遗赠 | 子类不使用继承的方法 | 用委托替代继承 |
| 过多的注释 | 注释用于解释复杂代码 | 提取方法/引入断言 |

### 快速识别指标

**方法级别**:
```
警告：
- 行数 > 20
- 参数 > 3
- 圈复杂度 > 10
- 嵌套层级 > 3

严重：
- 行数 > 50
- 参数 > 5
- 圈复杂度 > 15
- 嵌套层级 > 4
```

**类级别**:
```
警告：
- 行数 > 200
- 方法数 > 20
- 依赖数 > 5

严重：
- 行数 > 500
- 方法数 > 30
- 依赖数 > 10
```

### 重构优先级

1. **Critical**: 安全漏洞、数据损坏风险
2. **High**: 性能瓶颈、可维护性严重阻碍
3. **Medium**: 代码异味、中等复杂度
4. **Low**: 命名问题、样式不一致
