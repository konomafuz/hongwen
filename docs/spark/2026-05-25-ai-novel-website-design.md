# AI小说生成工作流 - 网站化设计方案

**创建日期**: 2026-05-25
**项目**: 番茄小说女频网文创作工具网站化

---

## 1. 项目概述

### 1.1 背景
当前项目是一个基于 Claude Code 的 CLI 工具（番茄小说女频网文创作工作流），实现从热点调研到正文生成的完整链路。本次规划将其网站化，以扩大用户覆盖面并提升用户体验。

### 1.2 MVP 范围
- **核心功能**: 设定 → 大纲 → 正文完整写作链路
- **用户定位**: 引导模式（新人）+ 专家模式（老手）
- **产品关系**: 网站独立于CLI，视为全新产品
- **商业模式**: SaaS订阅制

---

## 2. 技术架构

### 2.1 推荐方案：经典全栈

| 层级 | 技术选型 | 理由 |
|------|---------|------|
| 前端 | Vue 3 + Element Plus | 与现有CLI最接近的学习曲线，文档丰富 |
| 后端 | FastAPI | 异步高性能，与Python AI逻辑天然兼容 |
| 数据库 | PostgreSQL | 强一致性，适合项目数据存储 |
| 缓存 | Redis | 会话、限流、热点数据缓存 |
| 部署 | Docker + 云服务器 | 成熟稳定 |
| AI调用 | DeepSeek API | 国内可访问、成本较低、适合中文 |

---

## 3. 用户权限设计

| 角色 | 项目数 | 字数限制 | 每日生成章节 | 功能 |
|------|--------|----------|-------------|------|
| 免费用户 | 1个 | 2万字 | 2章/天 | 基础创作工作流 |
| 普通会员 | 无限 | 无限 | 50章/天 | 基础功能 + 导出 |
| 高级会员 | 无限 | 无限 | 200章/天 | 全部功能 |

**高级会员专属功能**:
- 文风选择器（5种预设 + 自定义）
- 知识库可视化
- AI对话助手
- 进度仪表盘
- RAG语感检索
- 热点分析
- AI续写 / 章节润色 / 封面生成

---

## 4. 核心创作工作流

### 4.1 步骤设计

| 步骤 | 功能 | 数据产出 |
|------|------|----------|
| 1. 核心设定 | 世界观、人设、感情线、冲突体系 | settings.json |
| 2. 标签简介 | 热门标签 + 3版简介 + 推荐语 | tags.json, synopsis.json |
| 3. 分卷大纲 | 3-5卷结构规划 | volume_outline.json |
| 4. 情节单元 | 每卷3-7情节点 | plot_units.json |
| 5. 章节大纲 | 每章详细大纲 | chapter_outline.json |
| 6. 正文创作 | 1800-2200字/章，多风格 | chapters/*.md |

### 4.2 交互模式

| 模式 | 交互特点 |
|------|----------|
| **引导模式**（新人） | 每步提供详细模板、示例、填写提示；AI辅助生成后可编辑 |
| **专家模式**（老手） | 跳过生成，直接编辑；支持导入自有设定/大纲；辅助正文写作 |

**专家模式核心能力**:
- 导入设定（JSON/Markdown格式）
- 导入大纲（兼容标准格式）
- 辅助正文（RAG语感小抄、续写提示、润色建议）
- 自定义Prompt模板

---

## 5. 数据模型设计

### 5.1 核心表结构

```
users                    # 用户表
├── id
├── email
├── password_hash
├── nickname
├── role (free/vip/premium)
├── created_at
└── updated_at

projects                 # 项目表
├── id
├── user_id (FK)
├── title
├── mode (guide/expert)
├── status (drafting/completed)
├── word_count
├── created_at
└── updated_at

project_settings         # 核心设定
├── id
├── project_id (FK)
├── genre
├── world_view
├── characters (JSON)
├── relationship_map
├── conflict_system
└── raw_content

project_tags             # 标签简介
├── id
├── project_id (FK)
├── tags (JSON)
├── synopsis_versions (JSON)
├── recommendation
└── status

project_volumes          # 分卷大纲
├── id
├── project_id (FK)
├── volume_number
├── volume_title
├── summary
├── plot_arc
└── chapters_estimated

project_chapters         # 章节表
├── id
├── project_id (FK)
├── volume_id (FK)
├── chapter_number
├── title
├── outline
├── content
├── word_count
├── status (outline/drafting/reviewing/completed)
├── created_at
└── updated_at

project_versions         # 版本历史
├── id
├── project_id (FK)
├── step_name
├── version_number
├── content (JSON)
└── created_at
```

### 5.2 存储策略

| 数据类型 | 存储方式 | 理由 |
|----------|----------|------|
| 项目元数据 | PostgreSQL | 结构化查询，强一致性 |
| 正文内容 | PostgreSQL (初期) → 对象存储(后期) | 内容大，分离存储 |
| 用户素材 | PostgreSQL JSON字段 | 灵活度高 |
| 会话/缓存 | Redis | 快速访问 |

---

## 6. API 接口设计

### 6.1 核心API

| 模块 | 接口 | 方法 | 说明 |
|------|------|------|------|
| **认证** | /api/auth/register | POST | 注册 |
| | /api/auth/login | POST | 登录 |
| | /api/auth/refresh | POST | 刷新token |
| **用户** | /api/users/me | GET/PUT | 个人信息 |
| **项目** | /api/projects | GET/POST | 列表/创建 |
| | /api/projects/{id} | GET/PUT/DELETE | 详情/更新/删除 |
| | /api/projects/{id}/duplicate | POST | 复制项目 |
| **创作** | /api/projects/{id}/settings | GET/POST/PUT | 核心设定 |
| | /api/projects/{id}/tags | GET/POST | 标签简介 |
| | /api/projects/{id}/volumes | GET/POST/PUT | 分卷大纲 |
| | /api/projects/{id}/chapters | GET/POST | 章节 |
| | /api/projects/{id}/chapters/{ch_id} | GET/PUT/DELETE | 章节详情 |
| **AI** | /api/ai/generate | POST | 通用AI生成 |
| | /api/ai/settings | POST | 生成设定 |
| | /api/ai/draft | POST | 生成正文 |
| | /api/ai/rag | GET | RAG检索 |
| **导出** | /api/export/word | POST | 导出Word |
| | /api/export/epub | POST | 导出EPUB |
| **支付** | /api/payment/create-order | POST | 创建订单 |
| | /api/payment/callback | POST | 支付回调 |

---

## 7. 前端页面架构

### 7.1 页面结构

```
/                      # 首页
├── /login             # 登录
├── /register          # 注册
├── /dashboard         # 控制台/书架
├── /project/:id       # 项目主页
│   ├── settings       # 核心设定
│   ├── tags           # 标签简介
│   ├── volumes        # 分卷大纲
│   ├── chapters       # 章节管理
│   └── chapter/:ch_id # 章节编辑
├── /knowledge         # 知识库（高级会员）
├── /profile           # 个人中心
└── /pricing           # 定价页
```

### 7.2 布局设计

**左右分栏布局**：
```
┌──────────────┬─────────────────────────────────┐
│              │                                 │
│   左侧导航    │         右侧内容区              │
│   选择栏      │                                 │
│              │   - 当前步骤内容                │
│  · 项目设置  │   - AI生成按钮                  │
│  · 标签简介  │   - 编辑区                      │
│  · 分卷大纲  │   - 预览                        │
│  · 章节大纲  │                                 │
│  · 正文创作  │                                 │
│  · 导出      │                                 │
│              │                                 │
├──────────────┴─────────────────────────────────┤
│   [保存]                    [生成]  [下一步]    │
└─────────────────────────────────────────────────┘
```

---

## 8. 部署方案

### 8.1 基础设施

| 组件 | 规格 | 说明 |
|------|------|------|
| 云服务器 | 2核4G（初期） | 可弹性升降配 |
| 数据库 | PostgreSQL 2核4G | 云服务商托管版 |
| Redis | 1G | 缓存 + 会话 |
| 对象存储 | OSS/桶存储 | 正文/图片存储 |
| 域名 | 已备案域名 | 解析到服务器 |
| HTTPS | Let's Encrypt | 免费SSL证书 |

### 8.2 Docker 部署

```yaml
services:
  web:
    build: ./backend
    ports:
      - "8000:8000"
  frontend:
    build: ./frontend
    ports:
      - "80:80"
  postgres:
    image: postgres:15
  redis:
    image: redis:7-alpine
```

---

## 9. 实施计划

### MVP 开发阶段（12周）

| 阶段 | 时间 | 内容 |
|------|------|------|
| Week 1-2 | 2周 | 项目初始化、环境搭建、用户认证 |
| Week 3-4 | 2周 | 项目管理、左侧导航框架 |
| Week 5-6 | 2周 | 创作工作流前端 + API对接 |
| Week 7-8 | 2周 | 正文创作页面 + AI生成集成 |
| Week 9-10 | 2周 | 导出功能、基础VIP权益 |
| Week 11-12 | 2周 | 测试、bug修复、MVP上线 |

### MVP 交付清单

- ✅ 用户注册/登录
- ✅ 项目管理（1个项目，2万字）
- ✅ 核心设定 → 标签简介 → 分卷大纲 → 章节大纲 → 正文创作
- ✅ 引导模式 + 专家模式
- ✅ Word导出

### 上线后迭代

| 版本 | 内容 |
|------|------|
| v1.1 | 高级会员功能（文风选择、知识库、AI助手） |
| v1.2 | 会员体系、支付接入 |
| v1.3 | 增值服务（AI续写、润色、封面） |
| v2.0 | 团队协作、私有化部署 |

---

*本文档为设计方案，后续将根据此Spec进行开发规划。*
