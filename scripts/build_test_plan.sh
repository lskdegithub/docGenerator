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

# 步骤2: 生成1.2章节内容
echo ""
echo "步骤2: 生成1.2章节内容（覆盖性对照表）..."
python3 "$SCRIPT_DIR/generate_section_1_2.py"

# 步骤3: 将生成的1.2章节内容插入到chapter1.tex中
echo ""
echo "步骤3: 插入1.2章节内容到模板..."
python3 -c "
import re
import os

try:
    with open('$OUTPUT_DIR/chapters/chapter1_2_generated.tex', 'r', encoding='utf-8') as f:
        insert_content = f.read()
    
    chapter1_path = '$OUTPUT_DIR/chapters/chapter1.tex'
    if os.path.exists(chapter1_path):
        with open(chapter1_path, 'r', encoding='utf-8') as f:
            template = f.read()
            
        # 定义替换的锚点
        # 尝试匹配 \subsection*{1.2 系统概述} 或 \subsection*{系统概述}
        # 并替换为生成的内容
        
        # 策略：如果找到 \input{...1_2...}，说明是新模板，不做处理（或者替换input）
        if 'chapter1_2_generated.tex' in template:
            print('检测到新模板格式(包含input)，跳过物理插入。')
        else:
            # 旧模板逻辑：寻找标题并替换其后的内容，或者直接替换标题
            # 简单策略：替换 \subsection*{1.2 系统概述} 为 插入内容
            if '\\subsection*{1.2 系统概述}' in template:
                new_content = template.replace('\\subsection*{1.2 系统概述}', insert_content)
                with open(chapter1_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print('已将1.2内容插入chapter1.tex')
            elif '\\subsection*{系统概述}' in template:
                 # 适配可能的变体
                new_content = template.replace('\\subsection*{系统概述}', insert_content)
                with open(chapter1_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print('已将1.2内容插入chapter1.tex (匹配系统概述)')
            else:
                print('警告：在chapter1.tex中未找到锚点，未进行插入。')
    else:
        print(f'错误：找不到 {chapter1_path}')
except Exception as e:
    print(f'发生错误: {e}')
"

# 步骤4: 生成4.2章节内容
echo ""
echo "步骤4: 生成4.2章节内容（计划执行的测试）..."
python3 "$SCRIPT_DIR/generate_section_4_2.py"

# 步骤5: 将生成的4.2章节内容插入到chapter4.tex中
echo ""
echo "步骤5: 插入4.2章节内容到模板..."
python3 -c "
import re
import os

try:
    with open('$OUTPUT_DIR/chapters/chapter4_2_generated.tex', 'r', encoding='utf-8') as f:
        insert_content = f.read()
    
    chapter4_path = '$OUTPUT_DIR/chapters/chapter4.tex'
    if os.path.exists(chapter4_path):
        with open(chapter4_path, 'r', encoding='utf-8') as f:
            template = f.read()
            
        if 'chapter4_2_generated.tex' in template:
            print('检测到新模板格式(包含input)，跳过物理插入。')
        else:
            if '\\subsection*{4.2 计划执行的测试}' in template:
                new_content = template.replace('\\subsection*{4.2 计划执行的测试}', insert_content)
                with open(chapter4_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print('已将4.2内容插入chapter4.tex')
            elif '\\subsection*{计划执行的测试}' in template:
                new_content = template.replace('\\subsection*{计划执行的测试}', insert_content)
                with open(chapter4_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print('已将4.2内容插入chapter4.tex (匹配计划执行的测试)')
            else:
                print('警告：在chapter4.tex中未找到锚点，未进行插入。')
except Exception as e:
    print(f'发生错误: {e}')
"

echo ""

# 步骤6: 编译文档
echo "步骤6: 编译LaTeX文档..."
mkdir -p output/log

# 进入输出目录编译
(cd "$OUTPUT_DIR" && /usr/local/texlive/2025/bin/x86_64-linux/xelatex -interaction=nonstopmode -output-directory="../../output/log" main.tex > ../../output/log/compile_test_plan_pass1.log 2>&1) || true
(cd "$OUTPUT_DIR" && /usr/local/texlive/2025/bin/x86_64-linux/xelatex -interaction=nonstopmode -output-directory="../../output/log" main.tex > ../../output/log/compile_test_plan.log 2>&1) || true

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
