#!/bin/bash
# 构建测试报告文档（从模板和数据生成完整文档）
# 用法: ./scripts/build_test_report.sh

set -e

echo "======================================"
echo "  构建测试报告文档"
echo "======================================"

XELATEX="xelatex"
if [ -x "/usr/local/texlive/2025/bin/x86_64-linux/xelatex" ]; then
  XELATEX="/usr/local/texlive/2025/bin/x86_64-linux/xelatex"
fi

TEMPLATE_DIR="src/doc2tex-template/test_report"
OUTPUT_DIR="output/test_report"
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

# 步骤2: 生成1.2章节内容（覆盖性对照表）
echo ""
echo "步骤2: 生成1.2章节内容（覆盖性对照表）..."
python3 "$SCRIPT_DIR/generate_section_1_2.py" --out "$OUTPUT_DIR/chapters/chapter1_2_generated.tex" --doc-type test_report

# 步骤3: 将生成的1.2章节内容插入到chapter1.tex中
echo ""
echo "步骤3: 插入1.2章节内容到模板..."
python3 - <<'PY'
import os, re

chapter1_path = 'output/test_report/chapters/chapter1.tex'
gen_path = 'output/test_report/chapters/chapter1_2_generated.tex'

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
            # 替换从 \\GjbSubsection{1.2 系统概述} 到 \\GjbSubsection{1.3 文档概述} 之前的整段内容
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

echo ""
echo "步骤4: 复制test_detail的第4章内容到test_report（移除4.1与4.1.1之间的表格和统计）..."
# 确保test_detail已构建
if [ ! -f "output/test_detail/chapters/chapter4_generated.tex" ]; then
  echo "test_detail未构建，先构建test_detail..."
  ./scripts/build_test_detail.sh > /dev/null 2>&1
fi
# 复制并处理：移除4.1标题后到4.1.1子标题之间的内容（测试项列表表格和统计文字）
# 简单逻辑：每个表格结束后添加\clearpage
python3 - <<'PY'
import re

src_path = 'output/test_detail/chapters/chapter4_generated.tex'
dst_path = 'output/test_report/chapters/chapter4_generated.tex'

with open(src_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 步骤1: 移除4.1标题后到4.1.1之间的内容
pattern = r'(\\GjbSubsection\{4\.1 计划执行的测试\}\s*\n).*?(?=\s*\\GjbSubsubsection\{4\.1\.1)'
new_content = re.sub(pattern, r'\1', content, flags=re.DOTALL)

# 步骤2: 移除\Needspace{...}命令
new_content = re.sub(r'\\Needspace\{[^}]+\}\s*\n', '', new_content)

# 步骤3: 标题格式处理
# 注意：test_detail已经使用了智能换行方案（format_title_name_ident函数），
# 包括\parbox换行和保持一行的短标题，因此这里不需要额外处理。
# 直接使用test_detail的标题格式即可。
new_content = new_content  # 无需修改

# 步骤4: 在每个表格结束后添加\clearpage
# 匹配完整的表格结构: {\settablespacing ... \begin{longtblr} ... \end{longtblr} } \vspace{-6pt}
# 在 \vspace{-6pt} 后面添加 \clearpage
new_content = re.sub(
    r'(\{\\settablespacing\s+\\begin\{longtblr\}.*?\\end\{longtblr\}\s*\}\s*\\vspace\{-6pt\})',
    r'\1\n\\clearpage',
    new_content,
    flags=re.DOTALL
)

with open(dst_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print('✅ 第4章内容已复制：表格结束后换页，测试项标题格式优化')
PY

echo ""
echo "步骤5: 编译LaTeX文档..."
mkdir -p output/log
rm -f output/test_report.pdf 2>/dev/null || true
JOBNAME="test_report"
rm -f "output/log/${JOBNAME}.aux" "output/log/${JOBNAME}.toc" "output/log/${JOBNAME}.out" "output/log/${JOBNAME}.log" "output/log/${JOBNAME}.pdf"
set +e
(cd "$OUTPUT_DIR" && "$XELATEX" -interaction=nonstopmode -halt-on-error -jobname="${JOBNAME}" -output-directory="../../output/log" main.tex > ../../output/log/compile_test_report_pass1.log 2>&1)
PASS1_EXIT=$?
(cd "$OUTPUT_DIR" && "$XELATEX" -interaction=nonstopmode -halt-on-error -jobname="${JOBNAME}" -output-directory="../../output/log" main.tex > ../../output/log/compile_test_report.log 2>&1)
PASS2_EXIT=$?
set -e

if [ $PASS1_EXIT -ne 0 ] || [ $PASS2_EXIT -ne 0 ]; then
  echo "❌ 文档编译失败，请查看日志: output/log/compile_test_report.log"
  exit 1
fi

if [ -f "output/log/${JOBNAME}.pdf" ]; then
  mkdir -p output/generated
  cp -f "output/log/${JOBNAME}.pdf" "output/test_report.pdf"
  cp -f "output/log/${JOBNAME}.pdf" "output/generated/test_report.pdf"
  echo "✅ 文档编译成功: output/generated/test_report.pdf"
else
  echo "❌ 文档编译失败，请查看日志: output/log/compile_test_report.log"
  exit 1
fi
