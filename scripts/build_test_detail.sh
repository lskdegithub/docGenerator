#!/bin/bash
# 构建测试细则文档（从模板和数据生成完整文档）
# 用法: ./scripts/build_test_detail.sh

set -e

echo "======================================"
echo "  构建测试细则文档"
echo "======================================"

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
python3 "$SCRIPT_DIR/generate_test_detail.py" --out "$OUTPUT_DIR" --data "$DATA_DIR"
echo "✅ 章节已生成"

echo ""
echo "步骤3: 编译LaTeX文档..."
mkdir -p output/log
rm -f output/log/main.aux output/log/main.toc output/log/main.out output/log/main.log output/log/main.pdf
(cd "$OUTPUT_DIR" && xelatex -interaction=nonstopmode -halt-on-error -output-directory="../../output/log" main.tex > ../../output/log/compile_test_detail_pass1.log 2>&1) || true
(cd "$OUTPUT_DIR" && xelatex -interaction=nonstopmode -halt-on-error -output-directory="../../output/log" main.tex > ../../output/log/compile_test_detail.log 2>&1) || true

if [ -f "output/log/main.pdf" ]; then
  cp -f "output/log/main.pdf" "output/test_detail.pdf"
  echo "✅ 文档编译成功: output/test_detail.pdf"
else
  echo "❌ 文档编译失败，请查看日志: output/log/compile_test_detail.log"
  exit 1
fi
