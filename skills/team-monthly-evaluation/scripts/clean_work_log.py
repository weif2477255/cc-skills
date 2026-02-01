#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
团队工作日志清洗脚本

功能：
1. 读取原始txt格式的工作日志
2. 清洗无效内容（农历、天气、金句、明日计划、本月计划等）
3. 保留日期段落之间的所有有效内容
4. 输出json格式的清洗后日志

清洗规则：
- 保留：每个日期段落之间的有效内容
- 不保留：
  1. 本月计划区域（从"本月计划"或包含"月"的计划行到下个日期）
  2. 农历天气描述（如：乙巳年 腊月初五 周五 晴）
  3. 从"每日金句"开始到下个日期之间的所有内容
  4. 从"明日计划"开始到下个日期之间的所有内容
  5. 括号中有多个姓名的日志条目

使用方法：
    python clean_work_log.py input.txt output.json
    python clean_work_log.py input.txt output.json --verbose
"""

import re
import sys
import json
from pathlib import Path
from enum import Enum
from typing import Dict, List, Tuple, Optional


class State(Enum):
    """处理状态"""
    READING_CONTENT = "reading"  # 读取日期后的内容
    SKIPPING = "skipping"  # 跳过"每日金句"、"明日计划"、"本月计划"区域


class WorkLogCleaner:
    """工作日志清洗器"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

        # 日期格式：yyyy-mm-dd
        self.date_pattern = r'^\d{4}-\d{2}-\d{2}'

        # 农历和天气描述（如：乙巳年 腊月十二 周五 小雨）
        self.lunar_weather_pattern = r'[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]年\s+\S+\s+周[一二三四五六日]\s+\S+'

        # []标签
        self.bracket_pattern = r'\[\]'

        # 触发跳过的关键词
        self.skip_triggers = ['每日金句', '明日计划', '本月计划', '月计划']

        # 姓名提取正则（支持全角和半角括号）
        self.name_pattern = r'[（(]([^）)]+)[）)]'

        # 非姓名词汇过滤列表（技术术语、通用词汇等）
        # 以及需要忽略的人员名单
        self.non_name_words = {
            '操作', '资源', '主从', '进度', '已完成', '完成',
            '例如', '如', '等', '或', '和', '与', '及',
            '待处理', '处理', '优化', '调整', '修复', '开发',
            # 忽略的人员
            '蔡青', '陈聪', '杨勇', '宋珮', '喻洁', '程博'
        }

        # 评分关键词配置（方便扩展和修改规则）
        # 结构：{维度: {级别: {'weight': 权重, 'keywords': [关键词列表]}}}
        self.keywords_config = {
            'depth': {
                'high': {
                    'weight': 2,
                    'keywords': [
                        # 架构设计类
                        '架构', '重构', '设计模式', '系统设计', '架构设计',
                        # 性能优化类
                        '优化', '性能', '调优', '瓶颈', '性能优化',
                        # 技术难度类
                        '算法', '分布式', '高并发', '并发', '多线程', '异步',
                        # 安全和底层类
                        '安全', '底层', '内核', '框架', '中间件', '引擎'
                    ]
                },
                'medium': {
                    'weight': 1,
                    'keywords': [
                        # 模块开发类
                        '模块', '组件', '插件', '扩展', '功能模块',
                        # 接口集成类
                        '接口', '集成', 'API', '对接', '接口开发', '接口设计',
                        # 配置部署类
                        '配置', '部署', '迁移', '升级', '安装', '环境'
                    ]
                }
            },
            'result': {
                'high': {
                    'weight': 2,
                    'keywords': [
                        # 交付类
                        '完成', '交付', '发布', '上线', '投产', '提交',
                        # 里程碑类
                        '里程碑', '版本', '正式环境', '生产环境', '发版',
                        # 客户价值类
                        '客户', '用户', '需求', '验收', '客户需求', '用户需求'
                    ]
                },
                'medium': {
                    'weight': 1,
                    'keywords': [
                        # 开发类
                        '开发', '实现', '编码', '编写', '功能开发',
                        # 测试类
                        '测试通过', '测试', '验证', '联调', '集成', '集成测试'
                    ]
                }
            },
            'collab': {
                'high': {
                    'weight': 2,
                    'keywords': [
                        # 协作类
                        '协作', '合作', '配合', '协同', '团队协作',
                        # 分享类
                        '讨论', '分享', '培训', '讲解', '教学', '技术分享',
                        # 支持类
                        '支持', '帮助', '协助', '指导', '审查', 'Review', 'Code Review', '代码审查'
                    ]
                },
                'medium': {
                    'weight': 1,
                    'keywords': [
                        # 沟通类
                        '沟通', '对接', '协调', '确认', '同步', '会议', '评审', '汇报'
                    ]
                }
            }
        }

    def log(self, message: str):
        """输出日志信息"""
        if self.verbose:
            print(f"[INFO] {message}")

    def is_date_line(self, line: str) -> bool:
        """判断是否为日期行"""
        return bool(re.match(self.date_pattern, line.strip()))

    def extract_date(self, line: str) -> str:
        """从行中提取日期"""
        match = re.match(self.date_pattern, line.strip())
        if match:
            return match.group(0)
        return ""

    def should_skip(self, line: str) -> bool:
        """判断是否应该进入跳过状态"""
        line = line.strip()
        for trigger in self.skip_triggers:
            if trigger in line:
                return True
        return False

    def clean_line(self, line: str) -> str:
        """清洗单行内容"""
        # 移除农历天气描述
        line = re.sub(self.lunar_weather_pattern, '', line)
        # 移除[]标签
        line = re.sub(self.bracket_pattern, '', line)
        return line.strip()

    def extract_names(self, line: str) -> List[str]:
        """
        提取括号中的姓名（支持全角和半角括号）
        返回姓名列表
        """
        matches = re.findall(self.name_pattern, line)

        if not matches:
            return []

        # 取最后一个匹配的括号内容
        names_str = matches[-1].strip()

        # 按顿号、逗号分隔姓名
        names = re.split(r'[、,，]', names_str)

        # 过滤掉非姓名内容（如日期、数字、技术术语等）
        valid_names = []
        for name in names:
            name = name.strip()
            # 简单判断：姓名通常是2-4个汉字
            if name and 2 <= len(name) <= 4 and all('\u4e00' <= c <= '\u9fff' for c in name):
                # 过滤掉非姓名词汇
                if name not in self.non_name_words:
                    valid_names.append(name)

        return valid_names

    def process_line(self, line: str, current_date: str,
                    details: Dict[str, Dict[str, List[str]]]):
        """
        处理单行日志

        Args:
            line: 当前行内容
            current_date: 当前日期
            details: 明细数据（按人员→日期→工作内容）
        """
        # 1. 清洗内容（移除农历天气、[]标签等）
        cleaned_line = self.clean_line(line)
        if not cleaned_line:
            return

        # 2. 提取姓名列表
        names = self.extract_names(cleaned_line)

        # 3. 根据姓名数量，决定如何处理
        if len(names) == 1:
            # 单个姓名 → 归入该人的明细区
            name = names[0]

            # 去掉姓名后缀（如"（蔡青）"）
            content = re.sub(self.name_pattern, '', cleaned_line).strip()
            # 去掉末尾可能多余的分号
            content = content.rstrip('；;')

            if name not in details:
                details[name] = {}
            if current_date not in details[name]:
                details[name][current_date] = []
            details[name][current_date].append(content)
            self.log(f"归入明细区 [{name}][{current_date}]: {content[:50]}...")

        elif len(names) > 1:
            # 多个姓名 → 跳过，不提取
            self.log(f"跳过多人日志: {cleaned_line[:50]}...")

        else:
            # 没有姓名 → 跳过，不提取
            self.log(f"跳过无姓名内容: {cleaned_line[:50]}...")

    def clean_log(self, input_path: Path) -> Tuple[dict, dict]:
        """
        清洗工作日志

        返回：
            (cleaned_data, stats)
            cleaned_data: {summary, details}
            stats: 统计信息
        """
        self.log(f"开始读取文件: {input_path}")

        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            # 尝试GBK编码
            self.log("UTF-8解码失败，尝试GBK编码")
            with open(input_path, 'r', encoding='gbk') as f:
                lines = f.readlines()

        self.log(f"共读取 {len(lines)} 行")

        # 初始化数据结构
        details = {}  # {姓名: {日期: [工作内容列表]}}

        current_date = None
        state = State.SKIPPING  # 初始状态为跳过（直到遇到第一个日期）

        total_lines = len(lines)
        valid_lines = 0
        skipped_lines = 0

        for i, line in enumerate(lines):
            original_line = line
            line = line.strip()

            # 检查是否为日期行
            if self.is_date_line(line):
                current_date = self.extract_date(line)
                state = State.READING_CONTENT  # 遇到日期，进入读取状态
                self.log(f"发现日期: {current_date}，进入READING_CONTENT状态")
                continue

            # 如果还没有遇到日期，跳过
            if current_date is None:
                skipped_lines += 1
                continue

            # 检查是否应该进入跳过状态
            if state == State.READING_CONTENT and self.should_skip(line):
                state = State.SKIPPING
                self.log(f"遇到跳过触发词，进入SKIPPING状态: {line[:30]}...")
                skipped_lines += 1
                continue

            # 根据状态处理
            if state == State.READING_CONTENT:
                # 处理有效内容
                before_count = sum(len(logs) for dates in details.values() for logs in dates.values())

                self.process_line(line, current_date, details)

                after_count = sum(len(logs) for dates in details.values() for logs in dates.values())

                if after_count > before_count:
                    valid_lines += 1
                else:
                    skipped_lines += 1

            elif state == State.SKIPPING:
                skipped_lines += 1
                self.log(f"跳过内容: {line[:50]}...")

        # 统计汇总信息
        summary = self.calculate_summary(details)

        # 计算评分参考数据
        scoring_reference = self.calculate_scoring_reference(details, summary['work_days'])

        # 统计信息
        stats = {
            'total_lines': total_lines,
            'valid_lines': valid_lines,
            'skipped_lines': skipped_lines,
            'person_count': summary['person_count'],
            'work_days': summary['work_days'],
            'total_entries': sum(ref['entries'] for ref in scoring_reference.values())
        }

        self.log(f"清洗完成: {stats['person_count']} 个人员, {stats['work_days']} 个工作日, {stats['total_entries']} 条有效内容")

        cleaned_data = {
            "summary": summary,
            "details": details,
            "scoring_reference": scoring_reference
        }

        return cleaned_data, stats

    def calculate_summary(self, details: Dict[str, Dict[str, List[str]]]) -> dict:
        """
        计算汇总信息

        Args:
            details: 明细数据

        Returns:
            汇总信息字典
        """
        # 统计月份（从第一个日期提取）
        all_dates = set()
        for person_dates in details.values():
            all_dates.update(person_dates.keys())

        month = ""
        if all_dates:
            first_date = sorted(all_dates)[0]
            month = first_date[:7]  # yyyy-mm

        # 统计人数
        person_count = len(details)

        # 统计有效天数（有工作日志的天数）
        work_days = len(all_dates)

        return {
            "month": month,
            "person_count": person_count,
            "work_days": work_days
        }

    def count_keywords(self, text: str, keywords: List[str]) -> Dict[str, int]:
        """
        统计文本中关键词出现次数

        Args:
            text: 要统计的文本
            keywords: 关键词列表

        Returns:
            关键词及其出现次数的字典
        """
        keyword_count = {}
        for keyword in keywords:
            count = text.count(keyword)
            if count > 0:
                keyword_count[keyword] = count
        return keyword_count

    def count_keywords_by_config(self, text: str, dimension: str, level: str) -> Dict[str, int]:
        """
        根据配置统计关键词出现次数

        Args:
            text: 要统计的文本
            dimension: 维度名称（depth/result/collab）
            level: 级别（high/medium）

        Returns:
            关键词及其出现次数的字典
        """
        keywords = self.keywords_config[dimension][level]['keywords']
        return self.count_keywords(text, keywords)

    def calculate_weighted_keyword_count(self, text: str) -> Tuple[int, Dict[str, int]]:
        """
        计算关键词加权总数

        根据scoring-guide.md的公式：
        加权总数 = (depth_high × 2 + depth_medium × 1)
                 + (result_high × 2 + result_medium × 1)
                 + (collab_high × 2 + collab_medium × 1)

        Args:
            text: 要统计的文本

        Returns:
            (加权总数, 各维度统计详情)
        """
        stats = {}
        weighted_total = 0

        for dimension in ['depth', 'result', 'collab']:
            for level in ['high', 'medium']:
                keyword_counts = self.count_keywords_by_config(text, dimension, level)
                count = sum(keyword_counts.values())
                weight = self.keywords_config[dimension][level]['weight']
                weighted_count = count * weight

                stats[f'{dimension}_{level}_count'] = count
                stats[f'{dimension}_{level}_weighted'] = weighted_count
                weighted_total += weighted_count

        stats['weighted_total'] = weighted_total
        return weighted_total, stats

    def keywords_to_string(self, keyword_dict: Dict[str, int]) -> str:
        """
        将关键词字典转换为字符串格式

        Args:
            keyword_dict: 关键词及其出现次数的字典

        Returns:
            格式化的字符串，如 "架构:3 | 优化:2"
        """
        if not keyword_dict:
            return ""
        return " | ".join(f"{k}:{v}" for k, v in keyword_dict.items())

    def calculate_workload_score(self, weighted_total: int, work_days_covered: int,
                                 total_work_days: int) -> Tuple[float, int, str]:
        """
        计算工作量评分

        根据scoring-guide.md的标准：
        - 关键词加权总数
        - 工作分布（覆盖天数百分比）

        Args:
            weighted_total: 关键词加权总数
            work_days_covered: 实际工作天数
            total_work_days: 总工作日数

        Returns:
            (工作分布百分比, 建议分数, 评分说明)
        """
        # 计算工作分布百分比
        coverage = work_days_covered / total_work_days if total_work_days > 0 else 0

        # 根据加权总数和工作分布计算建议分数
        # 参考scoring-guide.md (按21个工作日计)：
        # 18-20分：加权总数≥80，覆盖≥16天（≥75%）
        # 15-17分：加权总数60-79，覆盖12-15天（55-70%）
        # 12-14分：加权总数40-59，覆盖8-11天（40-50%）
        # <12分：加权总数<40，覆盖<8天（<40%）

        if weighted_total >= 80 and coverage >= 0.75:
            score = 18 + min(2, (weighted_total - 80) // 10)  # 18-20分
            reason = f"加权总数{weighted_total}≥80，覆盖率{coverage:.0%}≥75%"
        elif weighted_total >= 60 and coverage >= 0.55:
            score = 15 + min(2, (weighted_total - 60) // 10)  # 15-17分
            reason = f"加权总数{weighted_total}≥60，覆盖率{coverage:.0%}≥55%"
        elif weighted_total >= 40 and coverage >= 0.40:
            score = 12 + min(2, (weighted_total - 40) // 10)  # 12-14分
            reason = f"加权总数{weighted_total}≥40，覆盖率{coverage:.0%}≥40%"
        else:
            # 低于标准，按比例计算
            score = min(11, int(weighted_total / 40 * 12))
            reason = f"加权总数{weighted_total}<40或覆盖率{coverage:.0%}<40%"

        return round(coverage, 2), score, reason

    def calculate_scoring_reference(self, details: Dict[str, Dict[str, List[str]]],
                                   work_days: int) -> dict:
        """
        计算评分参考数据

        Args:
            details: 明细数据
            work_days: 工作日数

        Returns:
            评分参考数据
        """
        scoring_ref = {}

        for name, dates in details.items():
            # 合并所有日志内容
            all_logs = []
            for logs in dates.values():
                all_logs.extend(logs)

            all_text = " ".join(all_logs)

            # 统计日志条目数
            entries = len(all_logs)

            # 统计实际工作天数
            work_days_covered = len(dates)

            # 计算关键词加权总数
            weighted_total, keyword_stats = self.calculate_weighted_keyword_count(all_text)

            # 计算工作量评分
            coverage, workload_score, workload_reason = self.calculate_workload_score(
                weighted_total, work_days_covered, work_days
            )

            # 统计各维度关键词（用于详细展示）
            depth_high = self.count_keywords_by_config(all_text, 'depth', 'high')
            depth_medium = self.count_keywords_by_config(all_text, 'depth', 'medium')
            result_high = self.count_keywords_by_config(all_text, 'result', 'high')
            result_medium = self.count_keywords_by_config(all_text, 'result', 'medium')
            collab_high = self.count_keywords_by_config(all_text, 'collab', 'high')
            collab_medium = self.count_keywords_by_config(all_text, 'collab', 'medium')

            scoring_ref[name] = {
                # 基础统计
                "entries": entries,
                "work_days_covered": work_days_covered,
                "coverage": coverage,

                # 关键词加权统计
                "weighted_total": weighted_total,
                "depth_high_count": keyword_stats['depth_high_count'],
                "depth_medium_count": keyword_stats['depth_medium_count'],
                "result_high_count": keyword_stats['result_high_count'],
                "result_medium_count": keyword_stats['result_medium_count'],
                "collab_high_count": keyword_stats['collab_high_count'],
                "collab_medium_count": keyword_stats['collab_medium_count'],

                # 工作量评分
                "workload_score": workload_score,
                "workload_reason": workload_reason,

                # 关键词详细列表（用于查看具体关键词）
                "depth_high": self.keywords_to_string(depth_high),
                "depth_medium": self.keywords_to_string(depth_medium),
                "result_high": self.keywords_to_string(result_high),
                "result_medium": self.keywords_to_string(result_medium),
                "collab_high": self.keywords_to_string(collab_high),
                "collab_medium": self.keywords_to_string(collab_medium)
            }

        return scoring_ref

    def convert_details_to_array(self, details: Dict[str, Dict[str, List[str]]]) -> Dict[str, List[str]]:
        """
        将 details 从嵌套字典格式转换为数组格式

        Args:
            details: 原始格式 {name: {date: [logs]}}

        Returns:
            数组格式 {name: ["date: log"]}
        """
        array_details = {}

        for name, dates in details.items():
            entries = []
            # 按日期排序
            for date in sorted(dates.keys(), reverse=True):  # 倒序，最新的在前
                logs = dates[date]
                # 合并同一天的多条日志
                combined_log = "；".join(logs)
                entries.append(f"{date}: {combined_log}")

            array_details[name] = entries

        return array_details

    def write_json(self, cleaned_data: dict, output_path: Path):
        """
        将清洗后的数据写入json文件

        Args:
            cleaned_data: 清洗后的数据
            output_path: 输出文件路径
        """
        self.log(f"开始写入文件: {output_path}")

        # 转换 details 格式为数组格式
        array_details = self.convert_details_to_array(cleaned_data['details'])

        # 构建输出数据
        output_data = {
            "summary": cleaned_data['summary'],
            "details": array_details,
            "scoring_reference": cleaned_data['scoring_reference']
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        self.log(f"写入完成")


def main():
    """主函数"""
    # 解析命令行参数
    if len(sys.argv) < 3:
        print("使用方法: python clean_work_log.py <input.txt> <output.json> [--verbose]")
        print("\n示例:")
        print("  python clean_work_log.py 2025-1月-工作日志.txt 2025-01_工作日志.json")
        print("  python clean_work_log.py input.txt output.json --verbose")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    # 检查输入文件是否存在
    if not input_path.exists():
        print(f"错误: 输入文件不存在: {input_path}")
        sys.exit(1)

    # 创建清洗器
    cleaner = WorkLogCleaner(verbose=verbose)

    try:
        # 清洗日志
        cleaned_data, stats = cleaner.clean_log(input_path)

        # 写入json
        cleaner.write_json(cleaned_data, output_path)

        # 输出统计信息
        print("\n" + "="*50)
        print("清洗完成！")
        print("="*50)
        print(f"输入文件: {input_path}")
        print(f"输出文件: {output_path}")
        print(f"\n统计信息:")
        print(f"  总行数: {stats['total_lines']}")
        print(f"  有效行数: {stats['valid_lines']}")
        print(f"  跳过行数: {stats['skipped_lines']}")
        print(f"  人员数: {stats['person_count']}")
        print(f"  工作日数: {stats['work_days']}")
        print(f"  有效内容条数: {stats['total_entries']}")
        print("="*50)

    except Exception as e:
        print(f"\n错误: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
