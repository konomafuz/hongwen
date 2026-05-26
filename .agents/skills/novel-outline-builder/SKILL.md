---
name: novel-outline-builder
description: 小说与剧本大纲结构 Skill。Use when the user asks for 分卷大纲、全书结构、情节单元、剧情单元、章节大纲、分章细纲、黄金三章、细化大纲 or turning novel settings into structured plot plans (male/female novel, short story, or short drama).
---

# 大纲结构生成引擎

负责把作品设定拆解为可直接用于创作的章节或分集结构：分卷大纲、情节单元和章节/分集细纲。支持男频长篇、女频长篇、精品短篇（起承转合全篇）及短屏短剧剧本。

## 边界

- 做：大纲结构设计、分章/分集细纲生成、黄金三章（集）爆点规则落实。
- 不做：核心设定创建、正文写作、RAG语感检索、审查报告、Word导出。
- 如果用户没有核心设定，先调用 `novel-story-foundation`。
- 如果用户要求检查大纲，完成大纲后显式调用 `novel-quality-review`。

## 步骤

1. 依据当前项目的 `book_type` 读取对应的分章大纲设计模版：
   - 章节大纲、分章、细纲、黄金三章（集）卡点：读取 `references/{book_type}/step06-chapter-outline.md`。
2. 依据全局配置 `book_types_config.json` 规定的题材节奏与格式：
   - 男频：侧重力量体系等级、动作和近期爽点升级规划。
   - 女频：侧重感情交互、小打脸及人设张力拉丝。
   - 短篇：按起承转合 4 部分拆解 5000-10000 字全篇结构。
   - 短剧：以单集剧本（300-500字）为单元策划强冲突与集尾卡点钩子。
3. 章节大纲必须为随后的正文写作提供饱满的信息量（包含对话方向、动作和具体矛盾）。

## 输出要求

- 章节/分集标题有吸引力，标明每个单元的功能。
- 大纲产物要能直接交给 `novel-quality-review` 审查，并作为 `novel-draft-writer` 的写作骨架。
