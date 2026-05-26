---
name: novel-quality-review
description: 番茄女频小说的大纲与正文审查 Skill。Use when the user asks for 检查大纲、审查大纲、一致性、检查正文、审查正文、查问题、AI味检测、人设是否崩、逻辑审查、修改建议 or quality review for Chinese female-oriented web novel outlines and chapters.
---

# 番茄女频质量审查

负责大纲和正文的质检：一致性、逻辑、人设、感情线、冗余、AI味、RAG使用是否自然。

## 边界

- 做：步骤7大纲审查、步骤9正文审查、修改优先级建议。
- 不做：从零写设定、大纲或正文；除非用户明确要求，否则只给审查和修改方向。
- 如果审查后用户要重写正文，显式调用 `novel-draft-writer`。
- 如果审查后用户要重搭结构，显式调用 `novel-outline-builder`。

## 步骤

1. 判断审查对象：
   - 大纲、分卷、情节单元、章节细纲、一致性：读取 `references/step07-check-outline.md`。
   - 正文、章节内容、AI味、人设崩、逻辑、冗余、RAG使用：读取 `references/step09-check-content.md`。
2. 审查必须给出证据：
   - 指出问题对应的设定、章节、行为、台词或叙事位置。
   - 区分“必须修改”和“建议优化”。
3. 如果发现严重问题，先给修改优先级，再给局部改法。
4. 如果整体通过，也要指出残余风险或可加强点。

## 输出要求

- 先给结论：通过、需小修、需大修。
- 再列严重问题、轻微问题、做得好的地方、修改优先级。
- 正文审查要特别检查 AI味、人物动机、对话自然度和 RAG 是否突兀。
