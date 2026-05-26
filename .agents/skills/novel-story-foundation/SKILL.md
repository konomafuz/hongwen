---
name: novel-story-foundation
description: 小说与剧本故事底盘创作 Skill。Use when the user asks for 核心设定、人设、世界观、感情线、冲突体系、老梗侦查、设定避坑、设定优化、标签、简介、推荐语 or packaging a web novel (male/female), short story, or short drama script concept.
---

# 故事底盘创作引擎

负责把选题和创意扩展为可持续写作的作品底盘：核心设定、人物关系、力量/世界观设定、标签、简介和一句话推荐语。支持男频、女频、精品短篇及竖屏短剧剧本。

## 边界

- 做：步骤2核心设定生成、步骤3标签简介包装、设定冲突诊断。
- 不做：分卷大纲、章节细纲、正文写作、正文审查。
- 如果用户没有选题或书名简介，先调用 `novel-market-topic` 生成选题方向。
- 如果用户要继续搭大纲，完成本 Skill 输出后显式调用 `novel-outline-builder`。

## 步骤

1. 根据当前项目的 `book_type` (保存于 `novel_project.json`)，读取对应题材的参考模板：
   - 核心设定、人设、世界观、角色：读取 `references/{book_type}/step02-core-settings.md`。
   - 标签、简介、推荐语、作品包装：读取 `references/{book_type}/step03-tags-synopsis.md`。
2. 生成核心设定时，根据全局配置 `book_types_config.json` 确定该题材的偏向与规则，确保角色动机、升级路线（男频）、冲突压迫（短剧）能支撑长篇或短篇结构。
3. 简介和标签设计需符合该体裁的市场点击爽点与推荐算法偏好。

## 输出要求

- 核心设定要能直接交给 `novel-outline-builder` 使用。
- 标签简介要区分平台标签、核心元素、简介版本和一句话推荐语。
