---
name: tomato-novel-female
description: 网文多 Skill 主控路由（支持女频/男频/短篇/短剧）。Use when the user asks for 写网文、写小说、小说流程、完整创作链路、热点分析、选题、设定、大纲、正文、审查、RAG语感小抄、合并Word or any end-to-end Chinese web novel workflow. This skill routes to specialized novel-* skills instead of doing every step itself. Covers female_novel, male_novel, short_story, and short_drama based on book_type.
---

# 番茄女频网文主控路由

本 Skill 负责理解用户处在小说创作链路的哪一段，并显式调用对应的专项 Skill。不要把所有步骤都塞进本文件；具体提示词、脚本和输出规范由子 Skill 负责。

## 协作架构

```
tomato-novel-female
├── novel-market-topic       # 热点调研、趋势分析、选题仿写
├── novel-story-foundation   # 核心设定、老梗侦查、标签简介
├── novel-outline-builder    # 分卷大纲、情节单元、章节大纲
├── novel-rag-voice          # RAG语感小抄、热梗更新
├── novel-draft-writer       # 正文创作
├── novel-quality-review     # 大纲审查、正文审查
└── novel-export-word        # 章节合并、Word导出
```

## 路由规则

- 用户说“热点、趋势、热门题材、市场分析、热词、热门标签、热门人设、排行榜、爆款、仿写、类似选题”：调用 `novel-market-topic`。
- 用户说“设定、人设、世界观、角色、感情线、冲突体系、老梗、避坑、设定优化、标签、简介、推荐语”：调用 `novel-story-foundation`。
- 用户说“分卷、卷大纲、全书结构、情节单元、剧情单元、章节大纲、分章、细纲、黄金三章”：调用 `novel-outline-builder`。
- 用户说“RAG、语感小抄、口语句式、热梗、当下语感、更新热梗、联网搜热梗、整理inbox素材”：调用 `novel-rag-voice`。
- 用户说“正文、写内容、创作这一章、写第几章、续写”：先调用 `novel-rag-voice` 生成小抄，再调用 `novel-draft-writer`；如果用户明确不要 RAG，可直接调用 `novel-draft-writer`。
- 用户说“检查大纲、审查大纲、一致性、检查正文、审查正文、查问题、AI味、人设崩、逻辑审查”：调用 `novel-quality-review`。
- 用户说“合并Word、生成Word、导出Word、合并文档、导出文档”：调用 `novel-export-word`。

## 完整流程

当用户要从 0 到 1 完成一本番茄女频小说时，按下面顺序显式串联：

1. 调用 `novel-market-topic`：热点调研、选题仿写，产出题材方向、书名简介、核心卖点。
2. 调用 `novel-story-foundation`：核心设定、老梗侦查、标签简介，产出可写作的故事底盘。
3. 调用 `novel-outline-builder`：分卷大纲、情节单元、章节大纲，产出可执行结构。
4. 调用 `novel-quality-review`：审查大纲；如有严重问题，回到 `novel-outline-builder` 修改后重审。
5. 调用 `novel-rag-voice`：为目标章节生成【RAG小抄】。
6. 调用 `novel-draft-writer`：按章节大纲和小抄写正文。
7. 调用 `novel-quality-review`：审查正文；如有严重问题，回到 `novel-draft-writer` 修改后重审。
8. 调用 `novel-export-word`：章节完成后合并导出 Word。

## 核心原则

1. 每个子 Skill 只解决一类问题，主控只做路由和流程衔接。
2. 客观数据、RAG检索、Word合并等确定性工作优先交给脚本。
3. 稳定风格规则放在专项参考文件里，避免在主控重复堆提示词。
4. 子 Skill 输出必须能成为下一步输入，必要时明确“下一步建议调用哪个 Skill”。
5. 审查环节必须形成循环：发现严重问题时，先修再继续，不要带病写正文。

## 原始资源

旧版全流程参考文件和工具仍保留在本目录的 `references/` 与 `tools/` 中，作为兼容备份。新流程优先使用各 `novel-*` 子 Skill 自己目录下的资源。

## 小说创作控制台 CLI

项目根目录提供 `novel.py` 交互式控制台，可用于自动化写作流水线。用户明确要求使用 CLI、连续生成章节、查看状态、更新数据或导出时，再引导使用：

```powershell
python novel.py
```

常用命令包括 `status`、`init`、`write [N]`、`rag`、`update`、`review <章号>`、`kb`、`stats`、`export`。
