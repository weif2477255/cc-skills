# Scenario Research Guide

## When to browse

出现以下情况时，主动做互联网调研：

- 用户明确要求结合互联网资料评判
- 业务术语或对象明显依赖行业背景
- 你怀疑不同制造模式下建模会不同
- 需要引用标准、行业实践或主流系统习惯用法来支撑结论

## Source priority

按以下优先级取证：

1. 用户提供的业务材料与当前工作区文档
2. 官方标准或官方标准解释资料
3. 行业组织资料
4. 主流 MOM/MES 厂商的结构化方法资料
5. 其他行业文章

优先选择：

- ISA / IEC 62264 相关官方说明
- MESA 等行业组织资料
- B2MML 等 ISA-95 对象模型资料
- 西门子、Rockwell、AVEVA、SAP Digital Manufacturing 等较成熟厂商的结构化说明

避免把只有营销语言、没有对象定义和流程边界的文章当成依据。

## How to use external evidence

外部资料只做三类用途：

- 确认某个业务场景是否落在 ISA-95 运行管理边界内
- 了解行业里常见的对象分层与关系模式
- 校正你对特定领域术语的理解

不要直接照搬外部系统对象名。优先抽取其背后的关系模式和分层思想。

## Evidence labeling

在报告中始终标记证据类型：

- `标准依据`：直接来自标准或官方解释
- `行业实践`：来自行业组织或成熟厂商资料
- `场景推断`：基于当前用户场景做出的结构推断

## Search patterns

### Generic

- `ISA-95 <domain> model`
- `IEC 62264 <domain> operations`
- `manufacturing <domain> work order execution traceability`
- `<domain> data model manufacturing MOM MES`

### Production operations

关注这些对象：

- work definition / recipe / routing
- operations schedule / production request
- job / dispatch / work order
- execution record / production response
- material consumption / genealogy / WIP
- performance / downtime / OEE

### Quality operations

关注这些对象：

- specification / inspection plan
- inspection request / task
- sample / characteristic / result
- nonconformance / disposition / rework / hold
- CAPA / deviation / release decision

### Maintenance operations

关注这些对象：

- asset / equipment / asset hierarchy
- maintenance strategy / procedure / task list
- maintenance request / work order / maintenance task
- failure event / downtime event
- spare part consumption / labor time / feedback
- MTBF / MTTR / asset health

### Inventory and material operations

关注这些对象：

- material definition / lot / batch / serial
- inventory unit / location / status
- movement / issue / return / transfer / reservation
- WIP tracking / genealogy / consumption and production links

## Research conclusions checklist

在吸收外部资料后，至少回答：

- 这个业务场景最少需要哪几个对象层次？
- 哪些对象必须区分，不能硬合并？
- 哪些关系必须能追溯？
- 哪些状态必须由事件支撑？
- 哪些指标只能放在分析层，不能混入事务主模型？

## Minimal citation behavior

如果用了互联网资料，在最终报告中至少提供：

- 来源名称
- 链接
- 该来源支持的关键判断点

如果外部资料并不足以支撑结论，明确写出“不足”，不要假装有标准依据。
