---
name: novel-draft-writer
description: 正文与剧本内容创作 Skill。Use when the user asks for 正文、写内容、创作这一章、写第几章、续写、写剧本、分段写作 or drafting chapter/episode content with optional styles and RAG elements (male/female, short story, short drama).
---

# 正文与剧本创作引擎

负责根据核心设定、前情提要、章节/分集细纲、选中文风和可选 RAG 语感小抄，创作出高质量的正文或剧本初稿。支持男频、女频、精品短篇（分段拼接模式）及短屏短剧剧本（标准剧本版面）。

## 边界

- 做：正文初稿撰写、剧本分幕台词撰写、字数区间与排版严格控制。
- 不做：大纲策划、正文质量审查、Word合并导出。
- 正文完成后，如用户要求检查或自动质检，显式调用 `novel-quality-review`。

## 步骤

1. 确认输入是否足够（包含核心设定、前情、细纲及可选 RAG 语感小抄）。
2. 获取当前项目的 `book_type`，动态加载写作准则和禁区模版：
   - 写作核心准则与禁用词：读取 `references/{book_type}/step08-write-content.md`。
3. 从全局配置 `book_types_config.json` 加载字数限制（`chapter_word_limit`）与排版样式：
   - **小说模式 (female_novel / male_novel)**：控制段落行数，控制短句行数（女频不超过15行），注重情绪物化。
   - **分段模式 (short_story)**：按“起、承、转、合”各部分顺序生成，每部分 1500-2000 字，最终拼接。
   - **剧本模式 (short_drama)**：输出标准的 `第X幕：【场景】`、`（动作指示）`、`角色：台词` 格式，杜绝小说旁白，严格控制在 300-500 字，集尾卡点。

## 输出要求

- 严格符合对应题材的格式规范，直接给出正文/剧本定稿，不要有长篇废话前言。
- 严防 AI 常用词及说教式升华结尾。
