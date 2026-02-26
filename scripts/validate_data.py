"""
数据验证工具（增强版）

此脚本验证 data/ 目录中的 YAML 文件是否符合规范，包括：
1. 验证目录结构
2. 验证 YAML 文件格式
3. 验证必需字段
4. 提供结构改进建议

特别注意与原生生成器兼容性的处理。
"""

import os
import sys
import re
import yaml
from pathlib import Path
from typing import List, Dict, Any, Tuple
import json


def load_yaml_compatible(file_path: Path):
    """
    加载YAML文件，使用与原始生成脚本兼容的方式
    处理中英文冒号兼容性问题
    """
    content = file_path.read_text(encoding="utf-8")

    # 预处理以解决多行文本问题
    # 先备份可能的多行文本内容，避免它们被错误解析
    lines = content.split('\n')
    processed_lines = []
    in_list_item = False

    for line in lines:
        stripped = line.lstrip()

        # 检查是否是列表项开始
        if stripped.startswith('-') or stripped.startswith('-测试'):
            in_list_item = True
            processed_lines.append(line)
        # 如果当前行看起来像多行文本（没有冒号结尾），且前一行是列表项或有内容
        elif in_list_item and not stripped.endswith(':') and ':' in stripped and not stripped.startswith('#'):
            # 这可能是多行文本的一部分，用特殊标记处理
            # 实际上我们应该保持原样，但需要确保YAML结构正确
            processed_lines.append(line)
        else:
            processed_lines.append(line)

    content = '\n'.join(processed_lines)

    # 处理中英文冒号兼容性问题
    content = content.replace("：", ":")
    # 在冒号后添加空格（如果没有的话）
    content = re.sub(r"(^\s*[^:\n]+):(?!\s)", r"\1: ", content, flags=re.MULTILINE)

    try:
        return yaml.safe_load(content) or {}
    except yaml.YAMLError:
        # 如果常规解析失败，使用更宽容的方法
        # 这里模拟原始加载器的处理方式
        return parse_plan_yaml_flexible(file_path)


def parse_plan_yaml_flexible(file_path: Path):
    """
    灵活解析plan.yaml文件，模仿原始加载器的处理方式
    """
    content = file_path.read_text(encoding="utf-8")
    content = content.replace("：", ":")

    def pick(pattern: str):
        match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
        return match.group(1).strip() if match else ""

    # 提取各个字段
    result = {
        "测试项名称": pick(r"测试项名称:\s*(.+?)(?:\n|$)"),
        "标识": pick(r"标识:\s*(.+?)(?:\n|$)"),
        "测试要求": pick(r"测试要求:\s*(.+?)(?:\n|$)"),
        "测试策略与方法": pick(r"测试策略与方法:\s*((?:\n\s*[-\w].*?)*)(?=\n\w|$)"),
        "假设与约束": pick(r"假设与约束:\s*((?:\n\s*[-\w].*?)*)(?=\n\w|$)"),
        "优先级": pick(r"优先级:\s*(.+?)(?:\n|$)"),
        "测试终止条件": pick(r"测试终止条件:\s*(.+?)(?:\n|$)"),
        "需求追踪关系": pick(r"(?:需求追踪关系|需求的追踪关系):\s*(.+?)(?:\n|$)"),
        "type": pick(r"^type:\s*(.+?)(?:\n|$)"),
        "需规章节": pick(r"需规章节:\s*(.+?)(?:\n|$)"),
    }

    # 移除空字段
    result = {k: v for k, v in result.items() if v}

    return result


class DataValidator:
    """数据验证器"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.errors = []
        self.warnings = []
        self.metrics_count = 0
        self.modules_count = 0
        self.items_count = 0
        self.cases_count = 0

    def add_error(self, path: str, message: str):
        """添加错误信息"""
        self.errors.append(f"{path}: {message}")

    def add_warning(self, path: str, message: str):
        """添加警告信息"""
        self.warnings.append(f"{path}: {message}")

    def validate_metric_dir(self, metric_path: Path) -> bool:
        """验证测试指标目录"""
        # 检查目录名格式
        if not re.match(r'^\d{3}-test-metric$', metric_path.name):
            self.add_error(str(metric_path), f"指标目录名格式不正确，应为 'NNN-test-metric'，当前为 '{metric_path.name}'")
            return False

        self.metrics_count += 1

        # 检查是否存在对应的指标定义文件
        expected_file = metric_path / f"{metric_path.name[:-len('-test-metric')]}-metric.yaml"
        if not expected_file.exists():
            self.add_error(str(metric_path), f"缺少指标定义文件: {expected_file.name}")
            return False

        # 验证指标定义文件
        self.validate_metric_file(expected_file)

        # 检查子目录（模块目录）
        module_dirs = [d for d in metric_path.iterdir() if d.is_dir() and re.match(r'^\d{3}-module$', d.name)]
        for module_dir in module_dirs:
            self.validate_module_dir(module_dir)

        # 检查是否有模块
        if not module_dirs:
            self.add_warning(str(metric_path), f"指标 '{metric_path.name}' 下没有定义任何模块")

        return True

    def validate_metric_file(self, file_path: Path):
        """验证指标定义文件"""
        try:
            data = load_yaml_compatible(file_path)

            if data is None:
                self.add_error(str(file_path), "YAML 文件为空")
                return

            # 检查是否为字典类型
            if not isinstance(data, dict):
                self.add_error(str(file_path), f"YAML 文件内容应为字典格式，当前为 {type(data)}")
                return

            # 检查必需字段
            required_fields = ['index', 'source', 'title']
            for field in required_fields:
                if field not in data or not data.get(field):
                    self.add_error(str(file_path), f"缺少必需字段: {field}")

            # 验证 index 字段格式
            if 'index' in data:
                index_val = str(data.get('index'))
                if not re.match(r'^\d+$', index_val):
                    self.add_error(str(file_path), f"index 字段格式不正确，应为纯数字，当前为 '{index_val}'")

            # 检查 content 字段（如果存在）
            if 'content' in data and data.get('content') is not None:
                if not isinstance(data.get('content'), str):
                    self.add_error(str(file_path), f"content 字段应为字符串类型，当前为 {type(data.get('content'))}")

        except Exception as e:
            self.add_error(str(file_path), f"处理文件时出错: {str(e)}")

    def validate_module_dir(self, module_path: Path):
        """验证模块目录"""
        # 检查目录名格式
        if not re.match(r'^\d{3}-module$', module_path.name):
            self.add_error(str(module_path), f"模块目录名格式不正确，应为 'NNN-module'，当前为 '{module_path.name}'")
            return False

        self.modules_count += 1

        # 检查是否存在 metadata.yaml
        metadata_file = module_path / "metadata.yaml"
        if not metadata_file.exists():
            self.add_error(str(module_path), f"缺少 metadata.yaml 文件")
            return False

        # 验证 metadata.yaml 文件
        self.validate_module_file(metadata_file)

        # 检查子目录（测试项目录）
        item_dirs = [d for d in module_path.iterdir() if d.is_dir() and re.match(r'^\d{3}-item\d+', d.name)]
        for item_dir in item_dirs:
            self.validate_item_dir(item_dir)

        # 检查是否有测试项
        if not item_dirs:
            self.add_warning(str(module_path), f"模块 '{module_path.name}' 下没有定义任何测试项")

        return True

    def validate_module_file(self, file_path: Path):
        """验证模块元数据文件"""
        try:
            data = load_yaml_compatible(file_path)

            if data is None:
                self.add_error(str(file_path), "YAML 文件为空")
                return

            # 检查是否为字典类型
            if not isinstance(data, dict):
                self.add_error(str(file_path), f"YAML 文件内容应为字典格式，当前为 {type(data)}")
                return

            # 检查必需字段
            required_fields = ['MODULE_NAME']
            for field in required_fields:
                if field not in data or not data.get(field):
                    self.add_error(str(file_path), f"缺少必需字段: {field}")

            # MODULE_ID 是可选的，但如果有，则应为字符串
            if 'MODULE_ID' in data and data.get('MODULE_ID') is not None:
                if not isinstance(data.get('MODULE_ID'), str):
                    self.add_error(str(file_path), f"MODULE_ID 字段应为字符串类型，当前为 {type(data.get('MODULE_ID'))}")

        except Exception as e:
            self.add_error(str(file_path), f"处理文件时出错: {str(e)}")

    def validate_item_dir(self, item_path: Path):
        """验证测试项目录"""
        # 检查目录名格式
        if not re.match(r'^\d{3}-item\d+$', item_path.name):
            self.add_error(str(item_path), f"测试项目录名格式不正确，应为 'NNN-itemX'，当前为 '{item_path.name}'")
            return False

        self.items_count += 1

        # 检查是否存在 plan.yaml
        plan_file = item_path / "plan.yaml"
        if not plan_file.exists():
            self.add_error(str(item_path), f"缺少 plan.yaml 文件")
            return False

        # 验证 plan.yaml 文件
        self.validate_item_file(plan_file)

        # 检查 test_case 目录
        test_case_dir = item_path / "test_case"
        if test_case_dir.exists():
            case_files = [f for f in test_case_dir.iterdir() if f.suffix.lower() == '.yaml']
            for case_file in case_files:
                self.validate_case_file(case_file)
                self.cases_count += 1
        else:
            self.add_warning(str(item_path), f"测试项 '{item_path.name}' 下没有 test_case 目录")

        return True

    def validate_item_file(self, file_path: Path):
        """验证测试项计划文件"""
        try:
            # 使用专门的flexible解析方法来处理可能有问题的plan.yaml文件
            data = parse_plan_yaml_flexible(file_path)

            if data is None:
                self.add_error(str(file_path), "YAML 文件为空")
                return

            # 检查是否为字典类型
            if not isinstance(data, dict):
                self.add_error(str(file_path), f"YAML 文件内容应为字典格式，当前为 {type(data)}")
                return

            # 检查必需字段
            required_fields = ['测试项名称', '标识', '测试要求', '测试策略与方法', '假设与约束', '优先级', '测试终止条件', '需求追踪关系', 'type']
            for field in required_fields:
                if field not in data or not data.get(field):
                    self.add_error(str(file_path), f"缺少必需字段: {field}")

            # 验证测试策略与方法的格式（这部分使用更宽松的检查）
            if '测试策略与方法' in data:
                strategy_methods = data.get('测试策略与方法')
                # 不再强制要求为列表，因为数据文件可能是文本而不是结构化列表

                # 我们只是检查格式是否符合规范要求（包含测试策略和测试方法）
                if isinstance(strategy_methods, str):
                    # 如果是字符串，检查是否包含相关的关键词
                    if "测试策略" not in strategy_methods and "测试方法" not in strategy_methods:
                        self.add_warning(str(file_path), f"测试策略与方法 字段应包含测试策略和测试方法信息")

                elif isinstance(strategy_methods, list):
                    for item in strategy_methods:
                        if isinstance(item, dict):
                            for key in item.keys():
                                if key not in ['测试策略', '测试方法']:
                                    self.add_warning(str(file_path), f"测试策略与方法 中发现未知字段: {key}")

            # 验证假设与约束的格式
            if '假设与约束' in data:
                constraints = data.get('假设与约束')
                if isinstance(constraints, str):
                    # 如果是字符串，检查是否包含相关的关键词
                    if "假设" not in constraints and "约束" not in constraints:
                        self.add_warning(str(file_path), f"假设与约束 字段应包含假设和约束信息")

                elif isinstance(constraints, list):
                    for item in constraints:
                        if isinstance(item, dict):
                            for key in item.keys():
                                if key not in ['假设', '约束']:
                                    self.add_warning(str(file_path), f"假设与约束 中发现未知字段: {key}")

            # 验证优先级
            if '优先级' in data:
                priority = data.get('优先级')
                if priority not in ['高', '中', '低']:
                    self.add_warning(str(file_path), f"优先级 建议使用 '高', '中', '低'，当前为 '{priority}'")

            # 验证 type
            if 'type' in data:
                test_type = data.get('type')
                valid_types = ['functional', 'interface', 'reliability', 'performance']
                if test_type not in valid_types:
                    self.add_warning(str(file_path), f"type 建议使用 {'/'.join(valid_types)}，当前为 '{test_type}'")

        except Exception as e:
            self.add_error(str(file_path), f"处理文件时出错: {str(e)}")

    def validate_case_file(self, file_path: Path):
        """验证测试用例文件"""
        try:
            data = load_yaml_compatible(file_path)

            if data is None:
                self.add_error(str(file_path), "YAML 文件为空")
                return

            # 检查是否为字典类型
            if not isinstance(data, dict):
                self.add_error(str(file_path), f"YAML 文件内容应为字典格式，当前为 {type(data)}")
                return

            # 检查必需字段
            required_fields = ['测试用例名称', '标识', '测试步骤']
            for field in required_fields:
                if field not in data or not data.get(field):
                    self.add_error(str(file_path), f"缺少必需字段: {field}")

            # 验证测试步骤
            if '测试步骤' in data:
                steps = data.get('测试步骤')
                if not isinstance(steps, list):
                    self.add_error(str(file_path), f"测试步骤 应为列表格式")
                else:
                    for idx, step in enumerate(steps):
                        if not isinstance(step, dict):
                            self.add_error(str(file_path), f"测试步骤[{idx}] 应为字典格式")
                        else:
                            step_required = ['序号', '输入及操作', '期望结果']
                            for step_field in step_required:
                                if step_field not in step or not step.get(step_field):
                                    self.add_error(str(file_path), f"测试步骤[{idx}] 缺少字段: {step_field}")

        except Exception as e:
            self.add_error(str(file_path), f"处理文件时出错: {str(e)}")

    def validate_directory_structure(self):
        """验证整个数据目录结构"""
        if not self.data_dir.exists():
            self.add_error(str(self.data_dir), "数据目录不存在")
            return False

        # 遍历数据目录下的所有测试指标目录
        metric_dirs = [d for d in self.data_dir.iterdir() if d.is_dir() and re.match(r'^\d{3}-test-metric$', d.name)]

        if not metric_dirs:
            self.add_warning(str(self.data_dir), "没有找到任何测试指标目录")

        # 按数字顺序验证
        metric_dirs_sorted = sorted(metric_dirs, key=lambda x: int(x.name.split('-')[0]))

        # 验证每个指标目录
        for metric_dir in metric_dirs_sorted:
            self.validate_metric_dir(metric_dir)

        # 检查指标编号是否连续
        expected_indices = list(range(1, len(metric_dirs_sorted) + 1))
        actual_indices = [int(d.name.split('-')[0]) for d in metric_dirs_sorted]

        if actual_indices != expected_indices:
            missing_indices = [i for i in expected_indices if i not in actual_indices]
            extra_indices = [i for i in actual_indices if i not in expected_indices]

            if missing_indices:
                self.add_warning(str(self.data_dir), f"缺少指标编号: {missing_indices} (建议保持连续编号)")
            if extra_indices:
                self.add_warning(str(self.data_dir), f"多余的指标编号: {extra_indices} (可能影响生成顺序)")

        return len(self.errors) == 0

    def print_summary(self):
        """打印验证摘要"""
        print("=" * 60)
        print("数据验证摘要")
        print("=" * 60)
        print(f"测试指标数量: {self.metrics_count}")
        print(f"模块数量: {self.modules_count}")
        print(f"测试项数量: {self.items_count}")
        print(f"测试用例数量: {self.cases_count}")
        print("-" * 60)

        if self.errors:
            print(f"错误 ({len(self.errors)}):")
            for error in self.errors:
                print(f"  ❌ {error}")
            print()

        if self.warnings:
            print(f"警告 ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")
            print()

        if not self.errors and not self.warnings:
            print("✅ 所有验证通过！数据结构完整且符合规范。")
        elif not self.errors:
            print("✅ 没有错误，但存在一些警告需要关注。")
        else:
            print("❌ 存在错误，需要修复后才能正常生成文档。")

    def run_validation(self):
        """运行验证"""
        print("开始验证数据目录结构...")
        is_valid = self.validate_directory_structure()
        self.print_summary()
        return is_valid


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="验证 data/ 目录中的 YAML 文件是否符合规范")
    parser.add_argument("--data-dir", default="data", help="数据目录路径 (默认: data)")

    args = parser.parse_args()

    validator = DataValidator(args.data_dir)
    is_valid = validator.run_validation()

    # 如果存在错误，退出码设为 1
    if validator.errors:
        sys.exit(1)

    # 如果只有警告，退出码设为 0，但提醒用户
    if validator.warnings:
        print("\n注意: 存在警告，建议修复以确保最佳效果。")


if __name__ == "__main__":
    main()