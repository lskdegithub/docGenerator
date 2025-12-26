#!/bin/bash
# 快速编译脚本
echo "正在编译 LaTeX 文件..."
xelatex -output-directory=output src/doc2tex-template/str-captain-1.tex
if [ $? -eq 0 ]; then
    echo "✅ 编译成功！PDF文件已生成到 output/ 目录"
    ls -la output/*.pdf
else
    echo "❌ 编译失败！请检查错误信息"
fi