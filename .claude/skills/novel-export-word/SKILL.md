---
name: novel-export-word
description: 番茄女频小说的 Word 导出 Skill。Use when the user asks for 合并Word、生成Word、导出Word、合并文档、导出文档、把章节合成docx or packaging chapter markdown files into a formatted novel Word document.
---

# 番茄女频 Word 导出

负责把已生成的章节 Markdown 文件合并成标准排版的 Word 文档。

## 边界

- 做：步骤10自动生成 Word、章节文件合并、基础排版。
- 不做：写正文、审查正文、改大纲。
- 如果章节内容还没有完成，先调用 `novel-draft-writer` 或等待用户提供章节文件。

## 步骤

1. 读取 `references/step10-merge-word.md`。
2. 确认章节文件位置和命名规则，默认查找工作区内的 `chapter_*.md`。
3. 优先使用确定性脚本 `tools/merge_to_word.py` 生成 `.docx`，不要手工拼接 Word。
4. 如果缺少 `python-docx` 等依赖，说明依赖并按当前环境规则处理。

## 输出要求

- 报告生成的 Word 文件路径。
- 简要说明合并了多少章、标题来源、是否发现缺章或命名异常。
- 如果无法生成，说明缺少的输入或依赖，不伪造成功结果。
