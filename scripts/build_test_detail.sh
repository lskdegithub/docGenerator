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
echo "✅ 模板文件已复制"

echo ""
echo "步骤2: 生成章节内容与追踪表行..."
TRACE_MAP="$OUTPUT_DIR/.trace_page_map.json"
python3 "$SCRIPT_DIR/generate_test_detail.py" --out "$OUTPUT_DIR" --data "$DATA_DIR" --trace-pass probe --trace-probe-piece-chars 60 --trace-enable-mark
echo "✅ 章节已生成（探测版）"

echo ""
echo "步骤3: 编译LaTeX文档（探测版）..."
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
echo "步骤4: 生成章节内容与追踪表行（按分页拆分）..."
echo "✅ 将进行最多 3 轮迭代，确保拆分点与最终分页一致"
ITER=1
while [ $ITER -le 3 ]; do
  python3 "$SCRIPT_DIR/generate_test_detail.py" --out "$OUTPUT_DIR" --data "$DATA_DIR" --trace-pass final --trace-probe-piece-chars 60 --trace-page-map "$TRACE_MAP" --trace-enable-mark
  echo "✅ 章节已生成（最终版，第 ${ITER} 轮）"

  echo ""
  echo "步骤5: 编译LaTeX文档（最终版，第 ${ITER} 轮）..."
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
