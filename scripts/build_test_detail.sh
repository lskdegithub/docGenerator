#!/bin/bash
# 构建测试细则文档（从模板和数据生成完整文档）
# 用法: ./scripts/build_test_detail.sh

set -e

echo "======================================"
echo "  构建测试细则文档"
echo "======================================"

XELATEX="xelatex"
if [ -x "/usr/local/texlive/2025/bin/x86_64-linux/xelatex" ]; then
  XELATEX="/usr/local/texlive/2025/bin/x86_64-linux/xelatex"
fi

TEMPLATE_DIR="src/doc2tex-template/test_detail"
OUTPUT_DIR="output/test_detail"
DATA_DIR="data"
SCRIPT_DIR="scripts"

echo ""
echo "📁 模板目录: $TEMPLATE_DIR/"
echo "📁 输出目录: $OUTPUT_DIR/"
echo "📁 数据目录: $DATA_DIR/"
echo ""

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
python3 "$SCRIPT_DIR/generate_section_1_2.py" --out "$OUTPUT_DIR/chapters/chapter1_2_generated.tex" --doc-type test_detail

# 步骤3: 将生成的1.2章节内容插入到chapter1.tex中
echo ""
echo "步骤3: 插入1.2章节内容到模板..."
python3 - <<'PY'
import os, re

chapter1_path = 'output/test_detail/chapters/chapter1.tex'
gen_path = 'output/test_detail/chapters/chapter1_2_generated.tex'

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
            # 替换从 \\subsection{系统概述} 到 \\subsection{文档概述} 之前的整段内容
            start_token = '\\subsection{系统概述}'
            end_token = '\\subsection{文档概述}'
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

echo ""
echo "步骤4: 生成章节内容与追踪表行..."
TRACE_MAP="$OUTPUT_DIR/.trace_page_map.json"
python3 "$SCRIPT_DIR/generate_test_detail.py" --out "$OUTPUT_DIR" --data "$DATA_DIR" --trace-pass probe --trace-probe-piece-chars 60 --trace-enable-mark
echo "✅ 章节已生成（探测版）"

echo ""
echo "步骤5: 编译LaTeX文档（探测版）..."
mkdir -p output/log
rm -f output/test_detail.pdf output/test_detail_fresh.pdf 2>/dev/null || true
JOBNAME="test_detail"
rm -f "output/log/main.aux" "output/log/main.toc" "output/log/main.out" "output/log/main.log" "output/log/main.pdf"
rm -f "output/log/${JOBNAME}.aux" "output/log/${JOBNAME}.toc" "output/log/${JOBNAME}.out" "output/log/${JOBNAME}.log" "output/log/${JOBNAME}.pdf"
set +e
(cd "$OUTPUT_DIR" && "$XELATEX" -interaction=nonstopmode -halt-on-error -jobname="${JOBNAME}" -output-directory="../../output/log" main.tex > ../../output/log/compile_test_detail_probe_pass1.log 2>&1)
PASS1_EXIT=$?
(cd "$OUTPUT_DIR" && "$XELATEX" -interaction=nonstopmode -halt-on-error -jobname="${JOBNAME}" -output-directory="../../output/log" main.tex > ../../output/log/compile_test_detail_probe.log 2>&1)
PASS2_EXIT=$?
set -e

if [ $PASS1_EXIT -ne 0 ] || [ $PASS2_EXIT -ne 0 ]; then
  echo "❌ 文档编译失败，请查看日志: output/log/compile_test_detail_probe.log"
  exit 1
fi

python3 "$SCRIPT_DIR/parse_trace_pages.py" --log "output/log/compile_test_detail_probe.log" --out "$TRACE_MAP"

echo ""
echo "步骤6: 生成章节内容与追踪表行（按分页拆分）..."
echo "✅ 将进行最多 3 轮迭代，确保拆分点与最终分页一致"
ITER=1
while [ $ITER -le 3 ]; do
  python3 "$SCRIPT_DIR/generate_test_detail.py" --out "$OUTPUT_DIR" --data "$DATA_DIR" --trace-pass final --trace-probe-piece-chars 60 --trace-page-map "$TRACE_MAP" --trace-enable-mark
  echo "✅ 章节已生成（最终版，第 ${ITER} 轮）"

  echo ""
  echo "步骤7: 编译LaTeX文档（最终版，第 ${ITER} 轮）..."
  rm -f "output/log/${JOBNAME}.aux" "output/log/${JOBNAME}.toc" "output/log/${JOBNAME}.out" "output/log/${JOBNAME}.log" "output/log/${JOBNAME}.pdf"
  set +e
  (cd "$OUTPUT_DIR" && "$XELATEX" -interaction=nonstopmode -halt-on-error -jobname="${JOBNAME}" -output-directory="../../output/log" main.tex > ../../output/log/compile_test_detail_pass1.log 2>&1)
  PASS1_EXIT=$?
  (cd "$OUTPUT_DIR" && "$XELATEX" -interaction=nonstopmode -halt-on-error -jobname="${JOBNAME}" -output-directory="../../output/log" main.tex > ../../output/log/compile_test_detail.log 2>&1)
  PASS2_EXIT=$?
  set -e

  if [ $PASS1_EXIT -ne 0 ] || [ $PASS2_EXIT -ne 0 ]; then
    echo "❌ 文档编译失败，请查看日志: output/log/compile_test_detail.log"
    exit 1
  fi

  TMP_MAP="$OUTPUT_DIR/.trace_page_map_final.json"
  python3 "$SCRIPT_DIR/parse_trace_pages.py" --log "output/log/compile_test_detail.log" --out "$TMP_MAP"

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

if [ -f "output/log/${JOBNAME}.pdf" ]; then
  mkdir -p output/generated
  cp -f "output/log/${JOBNAME}.pdf" "output/test_detail.pdf"
  cp -f "output/log/${JOBNAME}.pdf" "output/generated/test_detail.pdf"
  echo "✅ 文档编译成功: output/generated/test_detail.pdf"
else
  echo "❌ 文档编译失败，请查看日志: output/log/compile_test_detail.log"
  exit 1
fi
