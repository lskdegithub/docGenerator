#!/bin/bash
# 构建测试计划文档（从模板和数据生成完整文档）
# 用法: ./scripts/build_test_plan.sh

set -e  # 遇到错误立即退出

echo "======================================"
echo "  构建测试计划文档"
echo "======================================"

XELATEX="xelatex"
if [ -x "/usr/local/texlive/2025/bin/x86_64-linux/xelatex" ]; then
  XELATEX="/usr/local/texlive/2025/bin/x86_64-linux/xelatex"
fi

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

cp "src/doc2tex-template/gjb438c-style.sty" "$OUTPUT_DIR/gjb438c-style.sty"
cp -r "src/doc2tex-template/common" "$OUTPUT_DIR/common"

echo "✅ 模板文件已复制"

# 步骤2: 生成1.2章节内容
echo ""
echo "步骤2: 生成1.2章节内容（覆盖性对照表）..."
python3 "$SCRIPT_DIR/generate_section_1_2.py"

# 步骤3: 将生成的1.2章节内容插入到chapter1.tex中
echo ""
echo "步骤3: 插入1.2章节内容到模板..."
python3 - <<'PY'
import os, re

chapter1_path = 'output/test_plan/chapters/chapter1.tex'
gen_path = 'output/test_plan/chapters/chapter1_2_generated.tex'

try:
    insert_content = open(gen_path, 'r', encoding='utf-8').read()
    if not os.path.exists(chapter1_path):
        print(f'错误：找不到 {chapter1_path}')
    else:
        template = open(chapter1_path, 'r', encoding='utf-8').read()

        # 如果模板已经包含input引用，则跳过
        if 'chapter1_2_generated.tex' in template:
            print('检测到新模板格式(包含input)，跳过物理插入。')
        else:
            # 替换从 1.2 系统概述 到 1.3 文档概述 之前的整段内容（保留 1.3 标题）
            start_token = '\\GjbSubsection{1.2 系统概述}'
            end_token = '\\GjbSubsection{1.3 文档概述}'
            start_idx = template.find(start_token)
            if start_idx != -1:
                end_idx = template.find(end_token, start_idx)
                if end_idx != -1 and start_idx < end_idx:
                    new_content = template[:start_idx] + insert_content + '\n\n' + template[end_idx:]
                    open(chapter1_path, 'w', encoding='utf-8').write(new_content)
                    print('已整体替换 1.2 章节，消除旧模板残留题注')
                else:
                    new_content = template.replace(start_token, insert_content)
                    open(chapter1_path, 'w', encoding='utf-8').write(new_content)
                    print('已替换 1.2 标题为生成内容')
            else:
                print('警告：在chapter1.tex中未找到 1.2 段落锚点')
except Exception as e:
    print(f'发生错误: {e}')
PY

# 步骤3.5: 生成4.1.5章节表格行数据（测试顺序表）
echo ""
echo "步骤3.5: 生成4.1.5章节表格行数据（测试顺序表）..."
python3 "$SCRIPT_DIR/generate_section_4_1_5.py" --template-dir "$OUTPUT_DIR/chapters"

# 步骤4: 生成4.2章节内容
echo ""
echo "步骤4: 生成4.2章节内容（计划执行的测试）..."
python3 "$SCRIPT_DIR/generate_section_4_2.py" --update-table --template-dir "$OUTPUT_DIR/chapters"

# 步骤5: 将生成的4.2章节内容插入到chapter4.tex中
echo ""
echo "步骤5: 插入4.2章节内容到模板..."
python3 - <<'PY'
import os

chapter4_path = 'output/test_plan/chapters/chapter4.tex'
gen_path = 'output/test_plan/chapters/chapter4_2_generated.tex'

try:
    insert_content = open(gen_path, 'r', encoding='utf-8').read()
    if not os.path.exists(chapter4_path):
        print(f'错误：找不到 {chapter4_path}')
    else:
        template = open(chapter4_path, 'r', encoding='utf-8').read()

        if 'chapter4_2_generated.tex' in template:
            print('检测到新模板格式(包含input)，跳过物理插入。')
        else:
            start_token = '\\subsection*{4.2 计划执行的测试}'
            start_idx = template.find(start_token)
            if start_idx == -1:
                start_token = '\\subsection*{计划执行的测试}'
                start_idx = template.find(start_token)

            if start_idx == -1:
                print('警告：在chapter4.tex中未找到 4.2 段落锚点，未进行插入。')
            else:
                end_token = '% =================== 第5章'
                end_idx = template.find(end_token, start_idx)
                if end_idx == -1:
                    end_idx = len(template)

                placeholder_token = '\\subsubsection*{4.2.1'
                placeholder_idx = template.find(placeholder_token, start_idx, end_idx)
                if placeholder_idx == -1:
                    placeholder_idx = end_idx

                new_content = template[:placeholder_idx] + insert_content + '\n\n' + template[end_idx:]
                open(chapter4_path, 'w', encoding='utf-8').write(new_content)
                print('已整体替换 4.2 小节的测试项详情内容')
except Exception as e:
    print(f'发生错误: {e}')
PY

# 步骤6: 生成第7章可追踪性表格行
echo ""
echo "步骤6: 生成第7章可追踪性表格行..."
TRACE_MAP="$OUTPUT_DIR/.trace_page_map.json"
python3 "$SCRIPT_DIR/generate_section_7.py" --trace-pass probe --trace-probe-piece-chars 60 --trace-enable-mark

# 步骤7: 将生成的第7章表格行插入到chapter7.tex中
echo ""
echo "步骤7: 插入第7章表格行到模板... (已改为使用 \input，跳过注入)"
# python3 - <<'PY'
# (Script removed as chapter7.tex now uses \input)
# PY

echo ""

# 步骤8: 编译文档（探测版）
echo "步骤8: 编译LaTeX文档（探测版）..."
mkdir -p output/log
rm -f output/test_plan.pdf output/test_plan_fresh.pdf 2>/dev/null || true

# 进入输出目录编译
JOBNAME="test_plan"
rm -f "output/log/${JOBNAME}.aux" "output/log/${JOBNAME}.toc" "output/log/${JOBNAME}.out" "output/log/${JOBNAME}.log" "output/log/${JOBNAME}.pdf"
set +e
(cd "$OUTPUT_DIR" && "$XELATEX" -interaction=nonstopmode -halt-on-error -jobname="${JOBNAME}" -output-directory="../../output/log" main.tex > ../../output/log/compile_test_plan_probe_pass1.log 2>&1)
PASS1_EXIT=$?
(cd "$OUTPUT_DIR" && "$XELATEX" -interaction=nonstopmode -halt-on-error -jobname="${JOBNAME}" -output-directory="../../output/log" main.tex > ../../output/log/compile_test_plan_probe.log 2>&1)
PASS2_EXIT=$?
set -e

if [ $PASS1_EXIT -ne 0 ] || [ $PASS2_EXIT -ne 0 ]; then
    echo "❌ 文档编译失败，请查看日志: output/log/compile_test_plan_probe.log"
    exit 1
fi

python3 "$SCRIPT_DIR/parse_trace_pages.py" --log "output/log/compile_test_plan_probe.log" --out "$TRACE_MAP"

echo ""
echo "步骤9: 生成第7章可追踪性表格行（按分页拆分）..."
echo "✅ 将进行最多 3 轮迭代，确保拆分点与最终分页一致"
ITER=1
while [ $ITER -le 3 ]; do
    python3 "$SCRIPT_DIR/generate_section_7.py" --trace-pass final --trace-probe-piece-chars 60 --trace-page-map "$TRACE_MAP" --trace-enable-mark

    echo ""
    echo "步骤10: 编译LaTeX文档（最终版，第 ${ITER} 轮）..."
    rm -f "output/log/${JOBNAME}.aux" "output/log/${JOBNAME}.toc" "output/log/${JOBNAME}.out" "output/log/${JOBNAME}.log" "output/log/${JOBNAME}.pdf"
    set +e
    (cd "$OUTPUT_DIR" && "$XELATEX" -interaction=nonstopmode -halt-on-error -jobname="${JOBNAME}" -output-directory="../../output/log" main.tex > ../../output/log/compile_test_plan_pass1.log 2>&1)
    PASS1_EXIT=$?
    (cd "$OUTPUT_DIR" && "$XELATEX" -interaction=nonstopmode -halt-on-error -jobname="${JOBNAME}" -output-directory="../../output/log" main.tex > ../../output/log/compile_test_plan.log 2>&1)
    PASS2_EXIT=$?
    set -e

    if [ $PASS1_EXIT -ne 0 ] || [ $PASS2_EXIT -ne 0 ]; then
        echo "❌ 文档编译失败，请查看日志: output/log/compile_test_plan.log"
        exit 1
    fi

    TMP_MAP="$OUTPUT_DIR/.trace_page_map_final.json"
    python3 "$SCRIPT_DIR/parse_trace_pages.py" --log "output/log/compile_test_plan.log" --out "$TMP_MAP"

    set +e
    python3 -c "import json,sys; a=json.load(open(sys.argv[1],'r',encoding='utf-8')); b=json.load(open(sys.argv[2],'r',encoding='utf-8')); sys.exit(0 if a==b else 1)" "$TRACE_MAP" "$TMP_MAP"
    SAME=$?
    set -e
    if [ $SAME -eq 0 ]; then
        break
    fi

    cp -f "$TMP_MAP" "$TRACE_MAP"
    ITER=$((ITER + 1))
done

# 重命名PDF文件
if [ -f "output/log/${JOBNAME}.pdf" ]; then
    mkdir -p output/generated
    cp -f "output/log/${JOBNAME}.pdf" "output/test_plan.pdf"
    cp -f "output/log/${JOBNAME}.pdf" "output/generated/test_plan.pdf"
    echo "✅ 文档编译成功: output/generated/test_plan.pdf"
else
    echo "❌ 文档编译失败，请查看日志: output/log/compile_test_plan.log"
    exit 1
fi

echo ""
echo "======================================"
echo "  构建完成"
echo "======================================"
