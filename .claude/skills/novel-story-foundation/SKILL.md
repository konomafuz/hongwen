---
name: novel-story-foundation
description: 番茄女频小说的故事底盘 Skill。Use when the user asks for 核心设定、人设、世界观、感情线、冲突体系、老梗侦查、设定避坑、设定优化、标签、简介、推荐语 or packaging a Chinese female-oriented web novel concept.
---

# 番茄女频故事底盘

负责把选题扩展成可持续写作的作品底盘：核心设定、人物关系、世界观、感情线、冲突体系、老梗诊断、标签简介和推荐语。

## 边界

- 做：步骤2核心设定、步骤2.5老梗侦查、步骤3标签简介。
- 不做：市场爬榜、分卷大纲、章节大纲、正文写作、正文审查。
- 如果用户没有选题或书名简介，先调用 `novel-market-topic` 生成选题方向。
- 如果用户要继续搭大纲，完成本 Skill 输出后显式调用 `novel-outline-builder`。

## 步骤

1. 根据用户输入判断要读取的参考：
   - 核心设定、人设、世界观、角色、感情线：读取 `references/step02-core-settings.md`。
   - 老梗、侦查、避坑、设定优化、设定审查：读取 `references/step02.5-cliche-detector.md`。
   - 标签、简介、推荐语、作品包装：读取 `references/step03-tags-synopsis.md`。
2. 生成核心设定时，优先保证后续可写性：
   - 女主目标要具体，男主功能不能只剩宠爱。
   - 主线冲突、感情线冲突、阶段性爽点要能支撑长篇。
   - 角色行为要能被欲望、创伤、利益或误解驱动。
3. 做老梗侦查时，不只指出老套，还要给出可执行的替换方案。
4. 做标签简介时，简介负责吸引读者，不能暴露所有剧情机关。

## 输出要求

- 核心设定要能直接交给 `novel-outline-builder` 使用。
- 老梗优化要保留原选题卖点，不要把类型核心改没。
- 标签简介要区分平台标签、核心元素、简介版本和一句话推荐语。
