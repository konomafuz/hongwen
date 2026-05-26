---
name: novel-rag-voice
description: 番茄女频小说的 RAG 语感增强 Skill。Use when the user asks for RAG检索、语感小抄、热梗、口语句式、当下语感、更新热梗、联网搜热梗、整理inbox素材 or wants voice/style references before writing a chapter.
---

# 番茄女频 RAG 语感小抄

负责正文前的语感增强：从本地知识库检索热梗、口语句式、写作模式，也可在用户明确要求时联网更新热梗资料，并提供【RAG小抄】进入正文的使用规则。

## 边界

- 做：步骤7.5 RAG语感小抄、热梗更新、inbox素材整理。
- 不做：正文创作、正文审查、章节大纲生成。
- 如果用户要写正文，先生成小抄，再显式调用 `novel-draft-writer`。

## 步骤

1. 读取 `references/step07.5-rag-retrieve.md`。
2. 需要把【RAG小抄】交给正文创作时，同时读取 `references/rag-usage-rules.md`。
3. 默认执行“检索小抄”模式：
   - 使用核心设定、前情、章节大纲、题材标签组织查询。
   - 优先运行 `tools/rag_retrieve.py` 从 `C:\Users\xiong\novel-rag-kb` 检索。
4. 只有用户明确说“更新热梗、联网搜热梗、这周热梗、整理inbox素材”时，执行“更新热梗”模式：
   - 使用 `tools/rag_update_trends.py`。
   - 如果需要联网或 API key，先说明依赖。
5. 小抄只给正文提供低频点缀，不要强行把热梗塞进严肃、古早或不匹配的场景。

## 输出要求

- 输出【RAG小抄】，包含可用口语、可借鉴句式、可点缀热梗、禁用/慎用提醒。
- 明确哪些内容适合本章，哪些只是参考。
- 当小抄和人设、时代背景、剧情冲突时，优先服从正文设定。
