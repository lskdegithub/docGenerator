#!/bin/bash
# 构建测试计划文档（从模板和数据生成完整文档）
# 用法: ./scripts/build_test_plan.sh

set -e  # 遇到错误立即退出

echo "======================================"
echo "  构建测试计划文档"
echo "======================================"

# 目录配置
TEMPLATE_DIR="src/doc2tex-template/test_plan"
OUTPUT_DIR="output/test_plan"
DATA_DIR="data"
SCRIPT_DIR="scripts"

echo ""
echo "📁 模板目录: $TEMPLATE_DIR/"
echo "📁 输出目录: $OUTPUT_DIR/"
echo "📁 数据目录: $DATA_DIR/"
echo ""

# 步骤1: 清理并复制模板到输出目录
echo "步骤1: 复制模板文件到输出目录..."
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"
cp -r "$TEMPLATE_DIR"/* "$OUTPUT_DIR/"

# 修改main.tex中的样式文件路径，指向源目录的样式文件
sed -i 's|../gjb438c-style|../../src/doc2tex-template/gjb438c-style|g' "$OUTPUT_DIR/main.tex"

echo "✅ 模板文件已复制"

# 步骤2: 生成4.2章节内容
echo ""
echo "步骤2: 生成4.2章节内容..."
python3 "$SCRIPT_DIR/generate_section_4_2.py"

# 步骤3: 更新chapter4.tex文件
echo ""
echo "步骤3: 更新chapter4.tex文件..."

# 使用Python脚本来更新chapter4.tex
python3 << 'PYEOF'
import re

output_dir = 'output/test_plan'

# 读取chapter4.tex
with open(f'{output_dir}/chapters/chapter4.tex', 'r', encoding='utf-8') as f:
    content = f.read()

# 读取生成的4.2内容
with open(f'{output_dir}/chapters/chapter4_2_generated.tex', 'r', encoding='utf-8') as f:
    generated = f.read()

# 查找4.2章节的起始和结束标记
# 4.2章节从 \subsection*{4.2 计划执行的测试} 开始
# 到 % =================== 第5章 或文件结尾结束

start_pattern = r'\\subsection\*\{4\.2 计划执行的测试\}'
end_pattern = r'% =================== 第5章'

# 找到起始位置
start_match = re.search(start_pattern, content)
if not start_match:
    print("错误：找不到4.2章节的起始标记")
    exit(1)

# 找到结束位置
end_match = re.search(end_pattern, content)
if not end_match:
    end_pos = len(content)
    print("警告：找不到第5章标记，将替换到文件结尾")
else:
    end_pos = end_match.start()

# 提取各部分内容
before = content[:start_match.end()]  # 包含 \subsection*{4.2 计划执行的测试}
after = content[end_pos:]  # 从第5章开始的内容

# 组合新内容
new_content = before + '\n\n' + generated + '\n\n' + after

# 写回文件
with open(f'{output_dir}/chapters/chapter4.tex', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ chapter4.tex已更新")
PYEOF

echo ""

# 步骤4: 编译文档
echo "步骤4: 编译LaTeX文档..."
mkdir -p output/log

# 进入输出目录编译
(cd "$OUTPUT_DIR" && xelatex -interaction=nonstopmode -output-directory="../../output/log" main.tex > ../../output/log/compile_test_plan.log 2>&1)

# 重命名PDF文件
if [ -f "output/log/main.pdf" ]; then
    mv -f "output/log/main.pdf" "output/test_plan.pdf"
    echo "✅ 文档编译成功: output/test_plan.pdf"
else
    echo "❌ 文档编译失败，请查看日志: output/log/compile_test_plan.log"
    exit 1
fi

echo ""
echo "======================================"
echo "  构建完成"
echo "======================================"
echo ""
echo "📄 输出文件: output/test_plan.pdf"
echo "📋 完整源文件: $OUTPUT_DIR/"
echo "📋 日志文件: output/log/"
echo ""
