---
name: novel-outline-builder
description: 番茄女频小说的大纲结构 Skill。Use when the user asks for 分卷大纲、全书结构、情节单元、剧情单元、章节大纲、分章细纲、黄金三章、细化大纲 or turning novel settings into structured plot plans.
---

# 番茄女频大纲结构

负责把作品底盘拆成可执行的长篇结构：分卷大纲、情节单元和章节大纲。

## 边界

- 做：步骤4分卷大纲、步骤5情节单元、步骤6章节大纲。
- 不做：核心设定创建、正文写作、RAG语感检索、审查报告、Word导出。
- 如果用户没有核心设定，先调用 `novel-story-foundation`。
- 如果用户要求检查大纲，完成大纲后显式调用 `novel-quality-review`。

## 步骤

1. 根据用户要的结构层级读取参考：
   - 分卷、全书结构、3-5卷规划：读取 `references/step04-volume-outline.md`。
   - 情节单元、拆解某一卷、3-7章小单元：读取 `references/step05-plot-units.md`。
   - 章节大纲、分章、细纲、黄金三章：读取 `references/step06-chapter-outline.md`。
2. 输出顺序保持从粗到细：
   - 先确认全书主线与每卷任务。
   - 再拆指定卷的情节单元。
   - 最后生成每章场景、冲突、爽点、钩子。
3. 章节大纲必须服务正文创作：
   - 每章有明确事件推进，不只写情绪。
   - 每章有读者期待、人物动作和章末钩子。
   - 黄金三章优先冲突、目标、悬念，不铺设过多背景。

## 输出要求

- 标明每卷/单元/章节的功能，避免只有剧情摘要。
- 大纲产物要能直接交给 `novel-quality-review` 审查。
- 若用户指定字数、卷数或章节范围，以用户约束优先。
