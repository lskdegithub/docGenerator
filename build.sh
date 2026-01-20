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

# 优先使用较新的 TeX Live（避免 ctex/expl3 版本过旧导致编译中断）
XELATEX="xelatex"
if [ -x "/usr/local/texlive/2025/bin/x86_64-linux/xelatex" ]; then
    XELATEX="/usr/local/texlive/2025/bin/x86_64-linux/xelatex"
fi

# 创建输出目录
mkdir -p output/log

# 源文件目录
SOURCE_DIR="src/doc2tex-template"
OUTPUT_DIR="output"
LOG_DIR="output/log"
BUILD_DIR="/tmp/latex-test-build"
mkdir -p "$BUILD_DIR"

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
    if [ "$doc" = "test_detail" ]; then
        echo "正在构建 $doc..."
        bash "scripts/build_test_detail.sh" </dev/null 2>&1 | tee "/tmp/compile_${doc}.log"
        EXIT_CODE=${PIPESTATUS[0]}

        if [ -f "output/${doc}.pdf" ]; then
            cp -f "/tmp/compile_${doc}.log" "output/log/${doc}.log" 2>/dev/null || true
        fi

        if [ $EXIT_CODE -eq 0 ]; then
            echo "✅ $doc 编译成功"
            ((SUCCESS_COUNT++))
        else
            echo "❌ $doc 编译失败"
            ((FAIL_COUNT++))
        fi
        continue
    fi

    MAIN_FILE="$SOURCE_DIR/${doc}/main.tex"

    if [ ! -f "$MAIN_FILE" ]; then
        echo "⚠️  文件不存在: $MAIN_FILE"
        ((FAIL_COUNT++))
        continue
    fi

    echo "正在编译 $doc..."

    # 进入文档目录编译（解决\input路径问题）
    JOBNAME="${doc}_build"
    DOC_BUILD_DIR="${BUILD_DIR}/${JOBNAME}"
    rm -rf "$DOC_BUILD_DIR" 2>/dev/null || true
    mkdir -p "$DOC_BUILD_DIR"
    (cd "$SOURCE_DIR/${doc}" && TEXINPUTS="..//:" "$XELATEX" -interaction=nonstopmode -halt-on-error -jobname="${JOBNAME}" -output-directory="${DOC_BUILD_DIR}" main.tex </dev/null 2>&1 | tee "/tmp/compile_${doc}.log")
    EXIT_CODE=${PIPESTATUS[0]}

    if [ -f "${DOC_BUILD_DIR}/${JOBNAME}.pdf" ]; then
        cp -f "${DOC_BUILD_DIR}/${JOBNAME}.pdf" "output/${doc}.pdf" 2>/dev/null || true
        cp -f "${DOC_BUILD_DIR}/${JOBNAME}.pdf" "output/${doc}_fresh.pdf" 2>/dev/null || true
        cp -f "${DOC_BUILD_DIR}/${JOBNAME}.log" "output/log/${doc}.log" 2>/dev/null || true
        cp -f "${DOC_BUILD_DIR}/${JOBNAME}.aux" "output/log/${doc}.aux" 2>/dev/null || true
        cp -f "${DOC_BUILD_DIR}/${JOBNAME}.toc" "output/log/${doc}.toc" 2>/dev/null || true
    fi

    if [ $EXIT_CODE -eq 0 ]; then
        echo "✅ $doc 编译成功"
        ((SUCCESS_COUNT++))
    else
        echo "❌ $doc 编译失败"
        ((FAIL_COUNT++))
    fi
done

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
