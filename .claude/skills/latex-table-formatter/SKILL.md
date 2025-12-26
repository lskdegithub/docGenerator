---
name: latex-table-formatter
description: Format and standardize LaTeX tables according to technical document standards. Handles table captions, column alignment, row spacing, cell padding, and header styling. Use when user needs to create, format, or fix tables in LaTeX documents, or mentions tables, alignment, or table formatting issues.
allowed-tools: Read, Write, Edit, Grep, Glob
---

# LaTeX Table Formatter

按照技术文档标准格式化 LaTeX 表格。

## 表格标准规范

### 基本结构
```latex
\vspace{-12pt}
\begin{center}
{\wuhaohei 表 X 表格标题}

{\settablespacing
\begin{tabular}{|列格式|}
\hline
\rowcolor{gray!20}
表头内容 \\
\hline
表格内容 \\
\hline
\end{tabular}
}
\end{center}
\vspace{6pt}
```

### 格式要求

#### 1. 表题格式
- 字体：五号黑体 (`\wuhaohei`)
- 对齐：居中
- 间距：表题与表格之间无空行
- 编号：使用 `\wuhaohei 表 X` 格式

#### 2. 表头格式
- 字体：小五号黑体 (`\xiaowuhei`)
- 背景：灰色 (`\rowcolor{gray!20}`)
- 对齐：居中 (`\multicolumn{1}{|c|}{内容}`)
- 边框：完整边框线

#### 3. 表格内容
- 字体：小五号宋体 (`\xiaowu`)
- 对齐：根据内容类型选择
  - 序号列：居中 `\multicolumn{1}{|c|}{{\xiaowu 内容}}`
  - 文字列：左对齐 `{\xiaowu 内容}`
  - 数值列：右对齐或居中

#### 4. 行间距
- 使用 `\settablespacing` 命令
- 默认值：`\arraystretch{1.0}`（在表格外定义）

#### 5. 列宽设置
- 使用 `p{宽度}` 参数列，例如：`p{3cm}`
- 总宽度建议：14.5cm（适合A4纸张）
- 列宽分配：根据内容比例分配

## 常见表格类型

### 类型1：三列对照表
```latex
\begin{tabular}{|p{0.5cm}|p{7cm}|p{7cm}|}
\hline
\rowcolor{gray!20}
\multicolumn{1}{|c|}{{\xiaowuhei 序号}} &
\multicolumn{1}{c|}{{\xiaowuhei 项目A}} &
\multicolumn{1}{c|}{{\xiaowuhei 项目B}} \\
\hline
\multicolumn{1}{|c|}{{\xiaowu 1}} &
{\xiaowu 内容A} &
{\xiaowu 内容B} \\
\hline
\end{tabular}
```

### 类型2：六列数据表
```latex
\begin{tabular}{|p{0.5cm}|p{2.5cm}|p{5.5cm}|p{2.5cm}|p{1.5cm}|p{2cm}|}
\hline
\rowcolor{gray!20}
\multicolumn{1}{|c|}{{\xiaowuhei 序号}} &
\multicolumn{1}{c|}{{\xiaowuhei 编号}} &
\multicolumn{1}{c|}{{\xiaowuhei 标题}} &
\multicolumn{1}{c|}{{\xiaowuhei 编写单位}} &
\multicolumn{1}{c|}{{\xiaowuhei 日期}} &
\multicolumn{1}{c|}{{\xiaowuhei 备注}} \\
\hline
\multicolumn{1}{|c|}{{\xiaowu 1}} &
{\xiaowu 内容1} &
{\xiaowu 内容2} &
{\xiaowu 内容3} &
{\xiaowu 内容4} &
{\xiaowu 内容5} \\
\hline
\end{tabular}
```

### 类型3：宽内容表
```latex
\begin{tabular}{|p{1cm}|p{12cm}|}
\hline
\rowcolor{gray!20}
\multicolumn{1}{|c|}{{\xiaowuhei 项目}} &
\multicolumn{1}{c|}{{\xiaowuhei 说明}} \\
\hline
\multicolumn{1}{|c|}{{\xiaowu 1}} &
{\xiaowu 这里是较长的内容描述，会自动换行} \\
\hline
\end{tabular}
```

## 使用方法

### 场景1：创建新表格

1. **询问表格类型**
   - 表格用途
   - 列数和每列内容类型
   - 行数（大致）

2. **生成表格代码**
   - 根据类型选择模板
   - 设置合适的列宽
   - 添加示例数据

3. **插入到文档**
   - 找到插入位置
   - 保持格式一致

### 场景2：修复现有表格

1. **读取表格代码**
   - 使用 Read 或 Grep 定位
   - 分析当前问题

2. **识别常见问题**
   - ❌ 缺少表头颜色
   - ❌ 表题未居中
   - ❌ 序号列未居中
   - ❌ 列宽不合理
   - ❌ 缺少 `\settablespacing`

3. **应用修正**
   - 使用 Edit 工具修改
   - 保持原内容不变
   - 只调整格式

### 场景3：批量格式化表格

1. **查找所有表格**
   ```bash
   grep -n "\\begin{tabular}" filename.tex
   ```

2. **逐个检查和修正**
   - 读取每个表格
   - 应用标准格式
   - 确保一致性

## 快速检查清单

格式化表格时，确保：

- [ ] 表题使用 `\wuhaohei` 和居中
- [ ] 表题前有 `\vspace{-12pt}`
- [ ] 表格包裹在 `{\settablespacing ... }` 中
- [ ] 表头使用 `\rowcolor{gray!20}`
- [ ] 表头使用 `\xiaowuhei` 字体
- [ ] 序号列使用 `\multicolumn{1}{|c|}{{\xiaowu 内容}}`
- [ ] 每行末尾有 `\\`
- [ ] 每行末尾有 `\hline`
- [ ] 表格后有 `\vspace{6pt}`

## 调试技巧

### 表格溢出页面
- 减小列宽值
- 减少列数
- 使用更小的字体

### 列内容不换行
- 确保使用 `p{宽度}` 而不是 `l/c/r`
- 增加列宽值

### 表题与表格间距不对
- 检查是否有空行
- 确保表题和表格在同一 center 环境中
- 移除不必要的 `\vspace`

### 表格宽度不一致
- 检查所有表格的总宽度
- 统一为标准宽度（推荐14.5cm）
- 重新分配列宽

## 表格宽度统一规则

### 标准宽度
**推荐总宽度：14.5cm**（适合A4纸张，页边距2.5cm）

### 统一方法

**步骤1：检查现有表格宽度**
```bash
# 查找所有表格定义
grep -n "\\begin{tabular}" document.tex

# 计算每个表格的总宽度
# 例如：{|p{0.5cm}|p{7cm}|p{7cm}|} = 0.5 + 7 + 7 = 14.5cm
```

**步骤2：记录标准表格宽度**
```
表1：14.5cm（三列表格）
  - 序号：0.5cm
  - 内容列1：7cm
  - 内容列2：7cm

表2：14.5cm（六列表格）
  - 序号：0.5cm
  - 编号：2.5cm
  - 标题：5.5cm
  - 编写单位：2.5cm
  - 日期：1.5cm
  - 备注：2cm
```

**步骤3：调整其他表格宽度**

**原则**：
- 序号列通常为：0.5-1.5cm
- 文字内容列：根据内容长度分配（2.5-7cm）
- 确保所有表格总宽度 = 14.5cm

**示例调整**：

原表格（12cm）：
```latex
\begin{tabular}{|p{2cm}|p{5cm}|p{3cm}|p{2cm}|}
% 2 + 5 + 3 + 2 = 12cm ❌
```

调整后（14.5cm）：
```latex
\begin{tabular}{|p{1.5cm}|p{6.5cm}|p{3.5cm}|p{3cm}|}
% 1.5 + 6.5 + 3.5 + 3 = 14.5cm ✅
```

**步骤4：验证调整**
```bash
# 编译检查
./build.sh

# 查看PDF，确认表格宽度一致
```

### 常见表格类型的标准宽度

**3列表格**（14.5cm）：
- 序号：0.5cm
- 内容列1：7cm
- 内容列2：7cm

**6列表格**（14.5cm）：
- 序号：0.5cm
- 文字列1：2.5-3.5cm
- 文字列2：2.5-3.5cm
- 文字列3：2.5-3.5cm
- 日期/数值列：1.5-2.5cm
- 备注列：2cm

**4列表格**（14.5cm）：
- 序号：1-1.5cm
- 主内容列：5-7cm
- 次内容列：3-4cm
- 备注/负责人列：2-3cm

### 快速宽度计算工具

创建脚本辅助计算：
```python
# 计算表格总宽度
widths = [0.5, 3.5, 3, 3, 2.5, 2]
total = sum(widths)
print(f"总宽度: {total}cm")
# 输出：总宽度: 14.5cm
```

## 示例对话

**用户**: "帮我创建一个3列的表格"

**响应流程**:
1. 询问表格用途和内容类型
2. 选择合适的三列表格模板
3. 设置列宽（如：序号0.5cm，内容列7cm）
4. 生成完整代码
5. 提供插入位置建议

**用户**: "这个表格格式不对，帮我修一下"

**响应流程**:
1. 读取表格代码
2. 识别问题（如：缺少表头颜色）
3. 应用标准格式
4. 使用 Edit 工具修改
5. 编译验证

**用户**: "将所有表格的宽度统一为14.5cm"

**响应流程**:
1. 查找所有表格定义
   ```bash
   grep -n "\\begin{tabular}" document.tex
   ```

2. 计算每个表格的当前宽度
   - 提取列宽参数
   - 计算总和

3. 调整列宽到14.5cm
   - 按比例增加各列宽度
   - 或根据内容重要性重新分配

4. 批量修改所有表格
   - 使用 Edit 工具逐个修改
   - 保持表格内容不变

5. 编译验证
   - 检查所有表格宽度一致
   - 确认PDF显示正常

## 注意事项

1. **保持表格总宽度统一**：所有表格应使用相同的总宽度（推荐14.5cm）
2. 保持表格总宽度在 14-15cm 以内
3. 表格内容过多时考虑分页
4. 避免表格跨页（使用 longtable 宏包）
5. 中文字符确保使用 ctex 宏包
6. 特殊字符需要转义（如 % # $ & 等）

**宽度一致性的重要性**：
- ✅ 文档整体视觉效果更专业
- ✅ 表格排版整齐划一
- ✅ 符合技术文档规范
- ❌ 宽度不一致会影响文档专业性
