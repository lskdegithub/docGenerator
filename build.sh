#!/bin/bash
# LaTeX 编译脚本
# 用法: ./build.sh

echo "======================================"
echo "  LaTeX 文档编译脚本"
echo "======================================"

# 创建输出目录
mkdir -p output/log

# 源文件和输出目录
SOURCE_FILE="src/doc2tex-template/str-captain-1.tex"
OUTPUT_DIR="output"
LOG_DIR="output/log"

echo ""
echo "📄 源文件: $SOURCE_FILE"
echo "📁 输出目录: $OUTPUT_DIR/"
echo "📋 日志目录: $LOG_DIR/"
echo ""
echo "正在编译..."

# 编译到 output 目录
xelatex -interaction=nonstopmode -output-directory="$OUTPUT_DIR" "$SOURCE_FILE" > /dev/null 2>&1
EXIT_CODE=$?

# 移动日志文件（无论编译成功与否）
mv -f "$OUTPUT_DIR"/*.log "$OUTPUT_DIR"/*.aux "$OUTPUT_DIR"/*.out "$OUTPUT_DIR"/*.toc "$OUTPUT_DIR"/*.fls "$OUTPUT_DIR"/*.fdb_latexmk "$OUTPUT_DIR"/*.synctex.gz "$LOG_DIR/" 2>/dev/null

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 编译成功！"
    echo ""
    echo "📄 PDF 文件:"
    ls -lh "$OUTPUT_DIR"/*.pdf 2>/dev/null || echo "  未找到 PDF 文件"
    echo ""
    echo "📋 日志文件: $LOG_DIR/"
    ls -lh "$LOG_DIR/" | grep -E "\.(log|aux)$" | tail -5
else
    echo "❌ 编译失败！"
    echo ""
    echo "查看错误日志: cat $LOG_DIR/str-captain-1.log"
    exit 1
fi