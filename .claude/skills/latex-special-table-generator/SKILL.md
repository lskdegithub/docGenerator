---
name: latex-special-table-generator
description: Generate complex technical tables for LaTeX documents including hardware configs, software inventories, test schedules, and requirement traceability matrices. Follows GJB 438C-2021 standards. Use when creating specialized tables for military software test documents.
allowed-tools: Read, Write, Edit, Grep, Glob
---

# LaTeX Special Table Generator

为军用软件测试文档生成专业技术表格。

## 功能概述

该 Skill 专门用于生成复杂的技术表格，包括：
- 硬件配置表
- 软件清单表
- 测试进度表
- 需求追踪表
- 测试用例表
- 问题追踪表

## 表格类型及模板

### 类型1：硬件配置表

**用途**: 描述测试环境的硬件配置

**结构**: 序号 | 设备名称 | 型号/规格 | 数量 | 性能参数 | 备注

```latex
\vspace{-12pt}
\begin{center}
{\wuhaohei 表 X 测试环境硬件项}

{\settablespacing
\begin{tabular}{|p{0.5cm}|p{3cm}|p{3cm}|p{1.5cm}|p{3cm}|p{2cm}|}
\hline
\rowcolor{gray!20}
\multicolumn{1}{|c|}{{\xiaowuhei 序号}} &
\multicolumn{1}{c|}{{\xiaowuhei 设备名称}} &
\multicolumn{1}{c|}{{\xiaowuhei 型号/规格}} &
\multicolumn{1}{c|}{{\xiaowuhei 数量}} &
\multicolumn{1}{c|}{{\xiaowuhei 性能参数}} &
\multicolumn{1}{c|}{{\xiaowuhei 备注}} \\
\hline
\multicolumn{1}{|c|}{{\xiaowu 1}} &
{\xiaowu 服务器} &
{\xiaowu 飞腾FT-2000+} &
{\xiaowu 1台} &
{\xiaowu 64核，128GB内存} &
{\xiaowu 国产} \\
\hline
\multicolumn{1}{|c|}{{\xiaowu 2}} &
{\xiaowu 台式机} &
{\xiaowu 联想开天N8系列} &
{\xiaowu 2台} &
{\xiaowu Intel i7，16GB内存} &
{\xiaowu 客户端} \\
\hline
\end{tabular}
}
\end{center}
\vspace{6pt}
```

**列宽**: 0.5cm + 3cm + 3cm + 1.5cm + 3cm + 2cm = 13cm

### 类型2：软件清单表

**用途**: 列出测试环境中的软件及其版本

**结构**: 序号 | 软件名称 | 版本号 | 用途 | 供应商 | 备注

```latex
\vspace{-12pt}
\begin{center}
{\wuhaohei 表 X 测试环境被测软件}

{\settablespacing
\begin{tabular}{|p{0.5cm}|p{3cm}|p{2.5cm}|p{2.5cm}|p{2.5cm}|p{2cm}|}
\hline
\rowcolor{gray!20}
\multicolumn{1}{|c|}{{\xiaowuhei 序号}} &
\multicolumn{1}{c|}{{\xiaowuhei 软件名称}} &
\multicolumn{1}{c|}{{\xiaowuhei 版本号}} &
\multicolumn{1}{c|}{{\xiaowuhei 用途}} &
\multicolumn{1}{c|}{{\xiaowuhei 供应商}} &
\multicolumn{1}{c|}{{\xiaowuhei 备注}} \\
\hline
\multicolumn{1}{|c|}{{\xiaowu 1}} &
{\xiaowu xxxxxxxx系统} &
{\xiaowu V0.7.1} &
{\xiaowu 被测软件} &
{\xiaowu xxxxx} &
{\xiaowu } \\
\hline
\multicolumn{1}{|c|}{{\xiaowu 2}} &
{\xiaowu 银河麒麟服务器版} &
{\xiaowu V10} &
{\xiaowu 操作系统} &
{\xiaowu 麒麟软件} &
{\xiaowu 国产} \\
\hline
\multicolumn{1}{|c|}{{\xiaowu 3}} &
{\xiaowu 数据库系统} &
{\xiaowu V5.0} &
{\xiaowu 数据存储} &
{\xiaowu xxxxx} &
{\xiaowu } \\
\hline
\end{tabular}
}
\end{center}
\vspace{6pt}
```

**列宽**: 0.5cm + 3cm + 2.5cm + 2.5cm + 2.5cm + 2cm = 13cm

### 类型3：测试进度表

**用途**: 展示测试活动的进度安排

**结构**: 序号 | 测试活动 | 开始时间 | 结束时间 | 负责人 | 状态

```latex
\vspace{-12pt}
\begin{center}
{\wuhaohei 表 X 测试进度安排表}

{\settablespacing
\begin{tabular}{|p{0.5cm}|p{4cm}|p{2cm}|p{2cm}|p{2cm}|p{1.5cm}|}
\hline
\rowcolor{gray!20}
\multicolumn{1}{|c|}{{\xiaowuhei 序号}} &
\multicolumn{1}{c|}{{\xiaowuhei 测试活动}} &
\multicolumn{1}{c|}{{\xiaowuhei 开始时间}} &
\multicolumn{1}{c|}{{\xiaowuhei 结束时间}} &
\multicolumn{1}{c|}{{\xiaowuhei 负责人}} &
\multicolumn{1}{c|}{{\xiaowuhei 状态}} \\
\hline
\multicolumn{1}{|c|}{{\xiaowu 1}} &
{\xiaowu 测试环境准备} &
{\xiaowu 2025-09-01} &
{\xiaowu 2025-09-05} &
{\xiaowu 张三} &
{\xiaowu 计划} \\
\hline
\multicolumn{1}{|c|}{{\xiaowu 2}} &
{\xiaowu 功能测试} &
{\xiaowu 2025-09-06} &
{\xiaowu 2025-09-15} &
{\xiaowu 李四} &
{\xiaowu 计划} \\
\hline
\multicolumn{1}{|c|}{{\xiaowu 3}} &
{\xiaowu 性能测试} &
{\xiaowu 2025-09-16} &
{\xiaowu 2025-09-20} &
{\xiaowu 王五} &
{\xiaowu 计划} \\
\hline
\end{tabular}
}
\end{center}
\vspace{6pt}
```

**列宽**: 0.5cm + 4cm + 2cm + 2cm + 2cm + 1.5cm = 12cm

### 类型4：需求追踪表

**用途**: 追踪需求与测试项的覆盖关系

**结构**: 序号 | 需求编号 | 需求名称 | 测试项 | 测试方法 | 覆盖状态

```latex
\vspace{-12pt}
\begin{center}
{\wuhaohei 表 X 需求追踪表}

{\settablespacing
\begin{tabular}{|p{0.5cm}|p{2cm}|p{3cm}|p{3cm}|p{2cm}|p{1.5cm}|}
\hline
\rowcolor{gray!20}
\multicolumn{1}{|c|}{{\xiaowuhei 序号}} &
\multicolumn{1}{c|}{{\xiaowuhei 需求编号}} &
\multicolumn{1}{c|}{{\xiaowuhei 需求名称}} &
\multicolumn{1}{c|}{{\xiaowuhei 测试项}} &
\multicolumn{1}{c|}{{\xiaowuhei 测试方法}} &
\multicolumn{1}{c|}{{\xiaowuhei 覆盖状态}} \\
\hline
\multicolumn{1}{|c|}{{\xiaowu 1}} &
{\xiaowu REQ-001} &
{\xiaowu 用户登录功能} &
{\xiaowu 登录测试} &
{\xiaowu 自动化测试} &
{\xiaowu 已覆盖} \\
\hline
\multicolumn{1}{|c|}{{\xiaowu 2}} &
{\xiaowu REQ-002} &
{\xiaowu 数据导出功能} &
{\xiaowu 导出测试} &
{\xiaowu 手动测试} &
{\xiaowu 已覆盖} \\
\hline
\end{tabular}
}
\end{center}
\vspace{6pt}
```

**列宽**: 0.5cm + 2cm + 3cm + 3cm + 2cm + 1.5cm = 12cm

### 类型5：测试用例表

**用途**: 详细描述测试用例

**结构**: 序号 | 用例编号 | 用例名称 | 前置条件 | 测试步骤 | 预期结果

```latex
\vspace{-12pt}
\begin{center}
{\wuhaohei 表 X 测试用例表}

{\settablespacing
\begin{tabular}{|p{0.5cm}|p{1.5cm}|p{2.5cm}|p{2cm}|p{3.5cm}|p{2.5cm}|}
\hline
\rowcolor{gray!20}
\multicolumn{1}{|c|}{{\xiaowuhei 序号}} &
\multicolumn{1}{c|}{{\xiaowuhei 用例编号}} &
\multicolumn{1}{c|}{{\xiaowuhei 用例名称}} &
\multicolumn{1}{c|}{{\xiaowuhei 前置条件}} &
\multicolumn{1}{c|}{{\xiaowuhei 测试步骤}} &
\multicolumn{1}{c|}{{\xiaowuhei 预期结果}} \\
\hline
\multicolumn{1}{|c|}{{\xiaowu 1}} &
{\xiaowu TC-001} &
{\xiaowu 登录成功} &
{\xiaowu 用户已注册} &
{\xiaowu 输入用户名密码，点击登录} &
{\xiaowu 登录成功，进入主页} \\
\hline
\multicolumn{1}{|c|}{{\xiaowu 2}} &
{\xiaowu TC-002} &
{\xiaowu 登录失败} &
{\xiaowu 用户已注册} &
{\xiaowu 输入错误密码，点击登录} &
{\xiaowu 提示密码错误} \\
\hline
\end{tabular}
}
\end{center}
\vspace{6pt}
```

**列宽**: 0.5cm + 1.5cm + 2.5cm + 2cm + 3.5cm + 2.5cm = 12.5cm

### 类型6：问题追踪表

**用途**: 记录测试过程中发现的问题

**结构**: 序号 | 问题编号 | 问题描述 | 严重程度 | 发现时间 | 状态 | 修复情况

```latex
\vspace{-12pt}
\begin{center}
{\wuhaohei 表 X 问题追踪表}

{\settablespacing
\begin{tabular}{|p{0.5cm}|p{1.5cm}|p{4cm}|p{1.5cm}|p{2cm}|p{1.5cm}|p{2cm}|}
\hline
\rowcolor{gray!20}
\multicolumn{1}{|c|}{{\xiaowuhei 序号}} &
\multicolumn{1}{c|}{{\xiaowuhei 问题编号}} &
\multicolumn{1}{c|}{{\xiaowuhei 问题描述}} &
\multicolumn{1}{c|}{{\xiaowuhei 严重程度}} &
\multicolumn{1}{c|}{{\xiaowuhei 发现时间}} &
\multicolumn{1}{c|}{{\xiaowuhei 状态}} &
\multicolumn{1}{c|}{{\xiaowuhei 修复情况}} \\
\hline
\multicolumn{1}{|c|}{{\xiaowu 1}} &
{\xiaowu BUG-001} &
{\xiaowu 登录时系统无响应} &
{\xiaowu 严重} &
{\xiaowu 2025-09-10} &
{\xiaowu 已修复} &
{\xiaowu V0.7.2已修复} \\
\hline
\multicolumn{1}{|c|}{{\xiaowu 2}} &
{\xiaowu BUG-002} &
{\xiaowu 导出文件格式错误} &
{\xiaowu 中等} &
{\xiaowu 2025-09-12} &
{\xiaowu 待修复} &
{\xiaowu 计划V0.7.3修复} \\
\hline
\end{tabular}
}
\end{center}
\vspace{6pt}
```

**列宽**: 0.5cm + 1.5cm + 4cm + 1.5cm + 2cm + 1.5cm + 2cm = 13cm

## 使用方法

### 场景1：生成硬件配置表

**用户请求**: "帮我生成一个硬件配置表，包含服务器、网络设备等"

**执行步骤**:

1. **确认表格内容**
   - 设备类型和数量
   - 需要展示的参数

2. **选择合适的列格式**
   - 设备名称、型号、数量、性能参数、备注

3. **生成表格代码**
   - 使用类型1模板
   - 设置合适的列宽
   - 填充示例数据

4. **插入到指定位置**
   - 通常在 2.4 节（硬件和固件项）

### 场景2：生成软件清单表

**用户请求**: "生成软件清单表，包括操作系统、数据库、被测软件"

**执行步骤**:

1. **收集软件信息**
   - 软件名称
   - 版本号
   - 用途
   - 供应商

2. **选择列格式**
   - 使用类型2模板
   - 6列布局

3. **生成表格代码**
   - 添加表格编号
   - 填充占位符或实际数据

4. **插入到指定位置**
   - 通常在 2.3 节（软件项）

### 场景3：生成需求追踪表

**用户请求**: "根据需求文档生成需求追踪表"

**执行步骤**:

1. **分析需求文档**
   - 读取需求规格说明
   - 提取需求编号和名称

2. **确定测试项**
   - 根据需求确定对应测试项
   - 选择测试方法

3. **生成表格**
   - 使用类型4模板
   - 自动填充需求信息

4. **插入到文档**
   - 在第4章（测试项）

## 列宽计算规则

### 基本原则
- 序号列：0.5cm（固定）
- 编号列：1.5-2cm
- 名称/描述列：2.5-4cm（根据内容长度）
- 数值/状态列：1.5-2cm
- 备注列：2cm左右
- **总宽度控制在 14-15cm 以内**

### 列宽分配示例

**窄内容表**（6列）:
- 0.5 + 2 + 2.5 + 2.5 + 2.5 + 2 = 12cm

**标准内容表**（5列）:
- 0.5 + 3 + 3 + 1.5 + 3 + 2 = 13.5cm

**宽内容表**（3列）:
- 0.5 + 6.5 + 6.5 = 13.5cm

## 快速生成指南

### 步骤1：确定表格类型
根据用途选择合适的模板类型

### 步骤2：调整列格式
根据内容调整列数和列宽

### 步骤3：设置表头
- 使用 `\rowcolor{gray!20}` 设置灰色背景
- 使用 `\xiaowuhei` 设置小五号黑体
- 使用 `\multicolumn{1}{|c|}{}` 居中对齐

### 步骤4：填充内容
- 使用 `\xiaowu` 设置小五号宋体
- 根据需要调整对齐方式
- 序号列居中，内容列左对齐

### 步骤5：插入表格
- 确保在 `\subsection*` 内部
- 使用 `\vspace{-12pt}` 和 `\vspace{6pt}` 设置表格上下间距
- 包裹在 `{}` 中避免影响后续段落

## 调试技巧

### 表格溢出页面
- 减小列宽值
- 减少列数
- 使用 `\small` 或 `\footnotesize` 缩小字体

### 列内容溢出
- 增加该列宽度
- 减少其他列宽度
- 使用更简洁的表述

### 表头与内容不对齐
- 检查 `\multicolumn` 的列数
- 确认 `&` 分隔符数量一致
- 验证每行列数相同

### 表格样式不一致
- 复制已有表格的格式
- 检查 `\rowcolor` 是否在每行
- 确认 `\hline` 完整

## 注意事项

1. **表格编号**: 确保编号连续且唯一
2. **表题格式**: 五号黑体居中，格式为 "表 X 表格标题"
3. **表头格式**: 小五号黑体，灰色背景
4. **内容格式**: 小五号宋体
5. **行间距**: 使用 `\settablespacing` 保持一致
6. **总宽度**: 不超过 15cm
7. **边框**: 使用 `|` 确保完整的竖线
8. **对齐**: 序号列居中，文本列根据内容选择对齐方式

## 示例对话

**用户**: "帮我生成一个硬件配置表"

**响应**: "我将为您创建一个硬件配置表。请问表格中需要包含哪些设备类型？（如：服务器、客户端、网络设备等）"

**用户**: "包含服务器和客户端"

**响应**:
1. 创建硬件配置表（类型1）
2. 预设服务器和客户端示例行
3. 插入到 2.4 节
4. 返回表格位置和填充建议

**用户**: "生成软件清单，包括操作系统、数据库、被测软件"

**响应**:
1. 使用类型2模板（软件清单表）
2. 填充三个软件类别
3. 设置版本号和用途占位符
4. 插入到 2.3 节

**用户**: "创建一个需求追踪表，追踪REQ-001到REQ-010"

**响应**:
1. 使用类型4模板（需求追踪表）
2. 生成10行数据
3. 自动编号 REQ-001 到 REQ-010
4. 提供测试项和测试方法占位符
5. 插入到指定位置
