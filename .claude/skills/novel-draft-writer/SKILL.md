---
name: novel-draft-writer
description: 番茄女频小说的正文创作 Skill。Use when the user asks for 正文、写内容、创作这一章、写第几章、续写、根据章节大纲写小说正文、切换文风写作、模仿文风写作 or drafting 1800-2200 Chinese web novel chapter content with optional style references and optional RAG小抄.
---

# 番茄女频正文创作

负责根据核心设定、前情、章节大纲、选中文风和可选 RAG 小抄写出单章正文。

## 边界

- 做：步骤8正文创作、章节续写、按大纲生成1800-2200字正文。
- 不做：大纲审查、正文审查、热梗库更新、Word导出。
- 如果用户需要 RAG 或流程中已有【RAG小抄】，读取 `novel-rag-voice` 的小抄和使用规则。
- 正文完成后，如用户要求检查或自动质检，显式调用 `novel-quality-review`。

## 步骤

1. 确认输入是否足够：
   - 核心设定或人物设定。
   - 前情摘要。
   - 本章章节大纲。
   - 可选【RAG小抄】。
2. 读取 `references/step08-write-content.md`，这是正文基础规则。
3. 读取 `references/styles/style-index.md`，选择本次正文文风：
   - 默认读取工作区根目录 `styles_config.json` 的 `current_style`，再读取对应文风 reference。
   - 如果用户明确指定文风，优先读取用户指定的文风 reference。
   - 如果用户粘贴文章或要求模仿某段文本，读取 `references/styles/custom-style-template.md`，先提炼临时文风，再用于正文。
4. 只有用户需要 RAG、已提供【RAG小抄】、或上游流程已经生成【RAG小抄】时，读取：
   - `novel-rag-voice/references/step07.5-rag-retrieve.md`
   - `novel-rag-voice/references/rag-usage-rules.md`
5. 正文 prompt 组合顺序固定为：
   - 正文基础规则：`references/step08-write-content.md`
   - 选中文风：`references/styles/*.md`
   - 可选 RAG：`novel-rag-voice` 的【RAG小抄】和使用规则
6. 写作时优先做到：
   - 对话推动关系和冲突。
   - 动作、选择、误会、利益推动剧情。
   - 章末留下清晰钩子。
   - 避免说教总结、上帝视角、AI味套话。

## 输出要求

- 默认输出一章完整正文，不夹杂长篇解释。
- 如用户要求，可附简短“本章钩子/爽点说明”。
- 未选择 RAG 时，不要自行编造【RAG小抄】。
