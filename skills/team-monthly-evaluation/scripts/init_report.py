#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
团队月度评价报告初始化脚本

功能：
1. 读取清洗后的JSON文件
2. 生成包含完整结构的月度评价Markdown模板
3. 使用TODO标记指示需要填充的部分

使用方法：
    python init_report.py <input.json> <output.md>
    python init_report.py 2026-01_工作日志.json 2026-01团队月度评价.md
"""

import json
import sys
from pathlib import Path
from typing import Dict, List


class ReportInitializer:
    """月度评价报告初始化器"""

    def __init__(self):
        pass

    def load_json(self, json_path: Path) -> dict:
        """
        加载JSON文件

        Args:
            json_path: JSON文件路径

        Returns:
            JSON数据
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def generate_template(self, data: dict) -> str:
        """
        生成月度评价模板

        Args:
            data: 清洗后的JSON数据

        Returns:
            Markdown模板内容
        """
        summary = data.get('summary', {})
        month = summary.get('month', 'yyyy-mm')
        person_count = summary.get('person_count', 0)

        scoring_ref = data.get('scoring_reference', {})
        # 获取所有成员姓名，按姓名排序
        members = sorted(scoring_ref.keys())

        template = f"""# {month} MOM事业部产品开发团队月度评价

## 一、团队整体评分

<!-- TODO: 填充团队整体评分 -->
<!-- 分析团队整体表现，填充以下表格 -->

| 维度 | 权重 | 得分 | 评价 |
|------|------|------|------|
| 工作量 | 20% | X/20 | TODO: 评价说明 |
| 工作深度 | 30% | X/30 | TODO: 评价说明 |
| 工作成果 | 30% | X/30 | TODO: 评价说明 |
| 协作贡献 | 20% | X/20 | TODO: 评价说明 |
| 总分 | 100% | X/100 | TODO: 评级 |

## 二、团队成员评分

<!-- TODO: 填充团队成员评分表格 -->
<!-- 重要提示：
1. 表格必须按总分从高到低排序
2. 只输出评分表格，不需要详细的评分依据
3. 评分分析在内部完成，不输出到报告中
4. 填充完成后立即清除本部分的所有<!-- -->注释
-->

| 序号 | 姓名 | 职责 | 工作量(20) | 深度(30) | 成果(30) | 协作(20) | 总分 | 建议评级 |
|------|------|------|-----------|---------|---------|---------|------|----------|
"""

        # 为每个成员添加一行占位符
        for idx, member in enumerate(members, start=1):
            template += f"| {idx} | {member} | TODO | TODO | TODO | TODO | TODO | TODO | TODO |\n"

        template += """
**评分说明**：本评分为AI基于工作日志分析的建议，最终评分需负责人确认。

## 三、优秀成员事迹（S、A+、A评级）

<!-- TODO: 填充优秀成员事迹 -->
<!-- 只为S、A+、A评级的成员填写详细事迹 -->

### 成员姓名（S评级）
- 突出贡献1：TODO
- 突出贡献2：TODO
- 综合评价：TODO

### 成员姓名（A+评级）
- 突出贡献1：TODO
- 突出贡献2：TODO
- 综合评价：TODO

### 成员姓名（A评级）
- 突出贡献1：TODO
- 突出贡献2：TODO
- 综合评价：TODO

## 四、其他成员综合评价

<!-- TODO: 填充其他成员综合评价 -->
<!-- 评价结构为"肯定优点 + 指出不足 + 改进建议" -->
<!-- 只为非S/A+/A评级的成员填写 -->

| 序号 | 姓名 | 综合评价 |
|------|------|----------|
"""

        # 为每个成员添加占位行（AI后续会根据评级决定是否填充）
        for idx, member in enumerate(members, start=1):
            template += f"| {idx} | {member} | TODO |\n"

        template += """
## 五、团队改进建议

<!-- TODO: 填充团队改进建议 -->
<!-- 团队层面2-3条，个别成员3-5人（原因分析 + 改进建议） -->

### 团队层面
1. **问题描述**：TODO。建议：TODO
2. **问题描述**：TODO。建议：TODO

### 个别成员改进重点
- **成员姓名1**：问题描述。建议：TODO
- **成员姓名2**：问题描述。建议：TODO
- **成员姓名3**：问题描述。建议：TODO
"""

        return template

    def write_template(self, template: str, output_path: Path):
        """
        将模板写入文件

        Args:
            template: 模板内容
            output_path: 输出文件路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(template)


def main():
    """主函数"""
    # 解析命令行参数
    if len(sys.argv) < 3:
        print("使用方法: python init_report.py <input.json> <output.md>")
        print("\n示例:")
        print("  python init_report.py 2026-01_工作日志.json 2026-01团队月度评价.md")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    # 检查输入文件是否存在
    if not input_path.exists():
        print(f"错误: 输入文件不存在: {input_path}")
        sys.exit(1)

    # 创建初始化器
    initializer = ReportInitializer()

    try:
        # 加载JSON数据
        print(f"正在读取: {input_path}")
        data = initializer.load_json(input_path)

        # 生成模板
        print("正在生成模板...")
        template = initializer.generate_template(data)

        # 写入文件
        print(f"正在写入: {output_path}")
        initializer.write_template(template, output_path)

        print("\n" + "="*50)
        print("模板生成完成！")
        print("="*50)
        print(f"输入文件: {input_path}")
        print(f"输出文件: {output_path}")
        print(f"\n月份: {data['summary']['month']}")
        print(f"人员数: {data['summary']['person_count']}")
        print(f"工作日数: {data['summary']['work_days']}")
        print("="*50)
        print("\n下一步: 使用Claude填充模板中的TODO标记部分")

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
