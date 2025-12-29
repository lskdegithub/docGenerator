#!/bin/bash
# LaTeX 编译脚本（支持章节拆分、样式与内容分离）
# 用法: ./build.sh [文档名称]
# 示例:
#   ./build.sh              # 编译所有文档
#   ./build.sh test_plan    # 只编译测试大纲
#   ./build.sh test_detail  # 只编译测试细则
#   ./build.sh test_report  # 只编译测试报告

echo "======================================"
echo "  LaTeX 文档编译脚本"
echo "======================================"

# 创建输出目录
mkdir -p output/log

# 源文件目录
SOURCE_DIR="src/doc2tex-template"
OUTPUT_DIR="output"
LOG_DIR="output/log"

# 确定要编译的文档
if [ -z "$1" ]; then
    # 编译所有文档（使用下划线命名）
    DOCS=("test_plan" "test_detail" "test_report")
    echo ""
    echo "📄 编译所有文档..."
else
    # 编译指定文档
    DOCS=("$1")
    echo ""
    echo "📄 编译文档: $1"
fi

echo ""
echo "📁 源文件目录: $SOURCE_DIR/"
echo "📁 输出目录: $OUTPUT_DIR/"
echo "📋 日志目录: $LOG_DIR/"
echo ""

# 编译每个文档
SUCCESS_COUNT=0
FAIL_COUNT=0

for doc in "${DOCS[@]}"; do
    MAIN_FILE="$SOURCE_DIR/${doc}/main.tex"

    if [ ! -f "$MAIN_FILE" ]; then
        echo "⚠️  文件不存在: $MAIN_FILE"
        ((FAIL_COUNT++))
        continue
    fi

    echo "正在编译 $doc..."

    # 进入文档目录编译（解决\input路径问题）
    (cd "$SOURCE_DIR/${doc}" && xelatex -interaction=nonstopmode -output-directory="../../../${OUTPUT_DIR}" main.tex > /tmp/compile_${doc}.log 2>&1)
    EXIT_CODE=$?

    # 重命名PDF文件
    if [ -f "output/main.pdf" ]; then
        mv -f "output/main.pdf" "output/${doc}.pdf" 2>/dev/null
    fi

    if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ $doc 编译成功"
        ((SUCCESS_COUNT++))
    else
        echo "❌ $doc 编译失败"
        ((FAIL_COUNT++))
    fi
done

# 移动日志文件（无论编译成功与否）
mv -f "$OUTPUT_DIR"/*.log "$OUTPUT_DIR"/*.aux "$OUTPUT_DIR"/*.out "$OUTPUT_DIR"/*.toc "$OUTPUT_DIR"/*.fls "$OUTPUT_DIR"/*.fdb_latexmk "$OUTPUT_DIR"/*.synctex.gz "$LOG_DIR/" 2>/dev/null

echo ""
echo "======================================"
echo "  编译完成"
echo "======================================"
echo ""
echo "✅ 成功: $SUCCESS_COUNT 个"
echo "❌ 失败: $FAIL_COUNT 个"
echo ""
echo "📄 PDF 文件:"
ls -lh "$OUTPUT_DIR"/*.pdf 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
echo ""
echo "📋 日志文件: $LOG_DIR/"

if [ $FAIL_COUNT -gt 0 ]; then
    echo ""
    echo "❌ 部分文档编译失败，请查看日志文件"
    exit 1
fi