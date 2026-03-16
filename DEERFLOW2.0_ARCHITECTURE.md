# 🦌 DeerFlow 2.0 完整项目架构文档

> 作者：Claude AI Assistant
> 日期：2026-03-16
> 版本：DeerFlow 2.0 (ground-up rewrite)

---

## 目录

1. [项目概述](#项目概述)
2. [系统架构](#系统架构)
3. [目录结构详解](#目录结构详解)
4. [后端架构](#后端架构)
5. [前端架构](#前端架构)
6. [核心配置](#核心配置)
7. [关键组件](#关键组件)
8. [数据流](#数据流)
9. [开发指南](#开发指南)
10. [最佳实践](#最佳实践)
11. [企业级全栈应用架构](#企业级全栈应用架构-deerflow-enterprise-project)

---

## 项目概述

### 什么是 DeerFlow 2.0？

DeerFlow (**D**eep **E**xploration and **E**fficient **R**esearch **Flow**) 是一个开源的 **超级 Agent 框架**，用于编排 **子 Agent**、**内存** 和 **沙箱环境** 来完成几乎任何任务。

**核心特点：**
- 基于 LangGraph + LangChain 构建
- 支持插件式 Skills（技能）
- 多种 Sandbox 执行模式
- 持久化长短期记忆
- 多渠道 IM 集成
- 文件上传与自动转换

**技术栈：**

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.12+, FastAPI, LangGraph, LangChain |
| 前端 | Next.js 16, React 19, TypeScript 5.8, Tailwind CSS 4 |
| 监控 | LangGraph Server, Gateway API, Nginx, Provisioner |

### 本文档包含的内容

本文档涵盖两个主要部分：

1. **DeerFlow 2.0 框架架构** (第1-10章) - 官方框架的核心架构和设计
2. **企业级全栈应用架构** (第11章) - 基于 DeerFlow 2.0 构建的生产级应用示例

**deerflow-enterprise-project** 是一个完整的企业级 AI Agent 管理平台，展示了如何在生产环境中使用 DeerFlow 2.0 构建全栈应用，包含 FastAPI 后端、Next.js 前端、PostgreSQL 数据库和 Docker 部署。

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                         用户层 (Clients)                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐     │
│  │ Web UI   │  │IM Channel│  │  Python  │  │ Claude Code      │     │
│  │ (3000)   │  │(Feishu/  │  │ Client   │  │ /claude-to-      │     │
│  │          │  │Slack/    │  │          │  │ deerflow         │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬─────────┘     │
│       │             │             │                  │              │
└───────┼─────────────┼─────────────┼──────────────────┼──────────────┘
        │             │             │                  │
        └─────────────┴─────────────┴──────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │       Nginx (2026)        │
                    │  Reverse Proxy / Router   │
                    └─────────────┬─────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐       ┌───────────────┐         ┌────────────────┐
│ LangGraph     │       │  Gateway API  │         │  Provisioner   │
│ Server (2024) │       │  (8001)       │         │  (8002, opt.)  │
│ - Lead Agent  │       │ - Models      │         │  (K8s only)    │
│ - Sub-Agents  │       │ - MCP         │         │                │
│ - Middleware  │       │ - Skills      │         │                │
│ - Tools       │       │ - Memory      │         │                │
│ - Skills      │       │ - Uploads     │         │                │
└───────────────┘       │ - Artifacts   │         └────────────────┘
                        └───────────────┘
                                  │
                          ┌───────┴───────┐
                          │  config.yaml  │
                          │  extensions_  │
                          │    config.json│
                          └───────────────┘
```

### 服务端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| Nginx (统一入口) | 2026 | 反向代理，路由到各个服务 |
| LangGraph Server | 2024 | Agent 运行时和工作流执行 |
| Gateway API | 8001 | REST API 服务 |
| Frontend | 3000 | Next.js Web 界面 |
| Provisioner | 8002 | 可选，Kubernetes 管理 |

---

## 目录结构详解

```
deer-flow/
├── README.md                              # 项目说明文档
├── config.example.yaml                    # 配置文件示例 (复制为 config.yaml)
├── extensions_config.example.json         # MCP/技能配置示例
├── CLAUDE.md                              # Claude Code 集成指南
├── Makefile                               # 根命令管理
├── .env.example                           # 环境变量示例
│
├── backend/                               # 后端应用
│   ├── Makefile                          # 后端命令
│   ├── pyproject.toml                    # Python 依赖
│   ├── langgraph.json                    # LangGraph 服务配置
│   ├── debug.py                          # 调试脚本
│   │
│   ├── app/                              # 应用层 (导入: app.*)
│   │   ├── __init__.py
│   │   ├── channels/                     # IM 渠道集成
│   │   │   ├── __init__.py
│   │   │   ├── base.py                   # 渠道基类
│   │   │   ├── manager.py                # 渠道管理器
│   │   │   ├── message_bus.py            # 消息总线 (发布/订阅)
│   │   │   ├── service.py                # 渠道服务
│   │   │   ├── store.py                  # 渠道-线程映射存储
│   │   │   ├── feishu.py                 # 飞书集成
│   │   │   ├── slack.py                  # Slack 集成
│   │   │   └── telegram.py               # Telegram 集成
│   │   │
│   │   └── gateway/                      # FastAPI Gateway API
│   │       ├── __init__.py
│   │       ├── app.py                    # FastAPI 应用
│   │       ├── config.py                 # Gateway 配置
│   │       ├── path_utils.py             # 路径工具
│   │       └── routers/                  # 路由模块
│   │           ├── __init__.py
│   │           ├── agents.py             # Agent 管理
│   │           ├── artifacts.py          # Artifact 服务
│   │           ├── channels.py           # 渠道状态
│   │           ├── mcp.py                # MCP 配置
│   │           ├── memory.py             # Memory 操作
│   │           ├── models.py             # 模型列表
│   │           ├── skills.py             # 技能管理
│   │           ├── suggestions.py        # 后续建议
│   │           ├── uploads.py            # 文件上传
│   │           └── threads.py            # 线程管理
│   │
│   └── packages/
│       └── harness/                      # DeerFlow 框架包
│           ├── pyproject.toml
│           └── deerflow/                 # 框架核心 (导入: deerflow.*)
│               ├── __init__.py
│               │
│               ├── agents/               # Agent 系统
│               │   ├── __init__.py
│               │   ├── checkpointer/     # 状态持久化
│               │   │   ├── __init__.py
│               │   │   ├── provider.py   # Checkpointer 接口
│               │   │   └── async_provider.py
│               │   ├── lead_agent/       # 主 Agent
│               │   │   ├── __init__.py
│               │   │   ├── agent.py      # Agent 构建逻辑
│               │   │   └── prompt.py     # 提示模板
│               │   ├── memory/           # 记忆系统
│               │   │   ├── __init__.py
│               │   │   ├── prompt.py     # 记忆提示
│               │   │   ├── queue.py      # 记忆更新队列
│               │   │   └── updater.py    # 记忆更新器
│               │   ├── middlewares/      # 11 个中间件
│               │   │   ├── __init__.py
│               │   │   ├── clarification_middleware.py
│               │   │   ├── dangling_tool_call_middleware.py
│               │   │   ├── loop_detection_middleware.py
│               │   │   ├── memory_middleware.py
│               │   │   ├── subagent_limit_middleware.py
│               │   │   ├── thread_data_middleware.py
│               │   │   ├── title_middleware.py
│               │   │   ├── todo_middleware.py
│               │   │   ├── tool_error_handling_middleware.py
│               │   │   ├── uploads_middleware.py
│               │   │   └── view_image_middleware.py
│               │   ├── thread_state.py   # 线程状态定义
│               │   └── __init__.py
│               │
│               ├── config/               # 配置系统
│               │   ├── __init__.py
│               │   ├── agents_config.py
│               │   ├── app_config.py     # 主配置 (核心)
│               │   ├── checkpointer_config.py
│               │   ├── extensions_config.py
│               │   ├── memory_config.py
│               │   ├── model_config.py
│               │   ├── paths.py
│               │   ├── sandbox_config.py
│               │   ├── skills_config.py
│               │   ├── subagents_config.py
│               │   ├── summarization_config.py
│               │   ├── title_config.py
│               │   ├── tool_config.py
│               │   └── tracing_config.py
│               │
│               ├── models/               # 模型工厂
│               │   ├── __init__.py
│               │   ├── factory.py        # 模型创建器
│               │   └── patched_deepseek.py
│               │
│               ├── mcp/                  # MCP 集成
│               │   ├── __init__.py
│               │   ├── cache.py
│               │   ├── client.py
│               │   ├── oauth.py          # OAuth 支持
│               │   └── tools.py
│               │
│               ├── sandbox/              # 沙箱系统
│               │   ├── __init__.py
│               │   ├── exceptions.py
│               │   ├── sandbox.py        # 沙箱接口
│               │   ├── sandbox_provider.py
│               │   ├── middleware.py     # 沙箱中间件
│               │   ├── tools.py          # 沙箱工具 (bash/ls/read/write)
│               │   └── local/            # 本地沙箱实现
│               │       ├── __init__.py
│               │       ├── list_dir.py
│               │       ├── local_sandbox.py
│               │       └── local_sandbox_provider.py
│               │
│               └── community/            # 社区工具
│                   ├── __init__.py
│                   ├── aio_sandbox/      # AIO 沙箱
│                   │   ├── __init__.py
│                   │   ├── aio_sandbox.py
│                   │   ├── aio_sandbox_provider.py
│                   │   ├── backend.py
│                   │   ├── local_backend.py
│                   │   ├── remote_backend.py
│                   │   └── sandbox_info.py
│                   ├── firecrawl/        # Firecrawl Web 爬虫
│                   │   └── tools.py
│                   ├── image_search/     # 图片搜索
│                   │   └── tools.py
│                   ├── infoquest/        # BytePlus InfoQuest
│                   │   ├── __init__.py
│                   │   ├── infoquest_client.py
│                   │   �└── tools.py
│                   ├── jina_ai/          # Jina AI Reader
│                   │   ├── __init__.py
│                   │   ├── jina_client.py
│                   │   └── tools.py
│                   └── tavily/           # Tavily Web 搜索
│                       └── tools.py
│               │
│               ├── reflection/           # 反射系统 (动态加载)
│               │   ├── __init__.py
│               │   └── resolvers.py      # resolve_variable, resolve_class
│               │
│               ├── skills/               # Skills 系统
│               │   ├── __init__.py
│               │   ├── loader.py         # 技能加载器
│               │   ├── parser.py         # SKILL.md 解析器
│               │   ├── types.py          # 技能类型定义
│               │   └── validation.py     # 技能验证
│               │
│               ├── subagents/            # 子 Agent 系统
│               │   ├── __init__.py
│               │   ├── config.py
│               │   ├── executor.py       # 子 Agent 执行器
│               │   ├── registry.py       # Agent 注册表
│               │   └── builtins/         # 内置子 Agent
│               │       ├── __init__.py
│               │       ├── general_purpose.py
│               │       └── bash_agent.py
│               │
│               ├── tools/                # 工具系统
│               │   ├── __init__.py
│               │   ├── tools.py          # 工具注册
│               │   └── builtins/         # 内置工具
│               │       ├── __init__.py
│               │       ├── clarification_tool.py
│               │       ├── present_file_tool.py
│               │       ├── setup_agent_tool.py
│               │       ├── task_tool.py
│               │       └── view_image_tool.py
│               │
│               └── utils/                # 工具函数
│                   ├── __init__.py
│                   ├── file_conversion.py
│                   ├── network.py
│                   └── readability.py
│               │
│               └── client.py             # 嵌入式 Python 客户端
│
│   └── tests/                            # 测试套件 (30+ 测试)
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_channel_file_attachments.py
│       ├── test_channels.py
│       ├── test_checkpointer.py
│       ├── test_client.py
│       ├── test_config_version.py
│       ├── test_custom_agent.py
│       ├── test_docker_sandbox_mode_detection.py
│       ├── test_harness_boundary.py
│       ├── test_loop_detection_middleware.py
│       ├── test_mcp_client_config.py
│       ├── test_memory_upload_filtering.py
│       ├── test_model_factory.py
│       ├── test_skills_loader.py
│       └── ... (更多测试)
│
│   └── docs/                             # 文档
│       ├── CONFIGURATION.md
│       ├── ARCHITECTURE.md
│       ├── API.md
│       ├── SETUP.md
│       └── ...
│
└── frontend/                             # 前端应用
    ├── package.json
    ├── pnpm-lock.yaml
    ├── next.config.js
    ├── tsconfig.json
    └── src/
        ├── app/                          # Next.js App Router
        │   ├── layout.tsx                # 根布局
        │   ├── page.tsx                  # 首页 (Landing)
        │   ├── workspace/                # 工作区
        │   │   ├── layout.tsx
        │   │   ├── page.tsx
        │   │   ├── chats/                # 聊天列表
        │   │   │   ├── page.tsx
        │   │   │   └── [thread_id]/      # 单个对话
        │   │   │       ├── layout.tsx
        │   │   │       └── page.tsx
        │   │   └── agents/               # Agent 管理
        │   │       ├── page.tsx
        │   │       ├── new/              # 新建 Agent
        │   │       │   └── page.tsx
        │   │       └── [agent_name]/     # Agent 详情
        │   │           └── chats/        # Agent 对话
        │   │               └── [thread_id]/
        │   │                   ├── layout.tsx
        │   │                   └── page.tsx
        │   ├── api/                      # API 路由
        │   │   └── auth/[...all]/        # 认证路由
        │   │       └── route.ts
        │   └── mock/                     # Mock API (开发用)
        │       └── api/
        │           ├── mcp/config/route.ts
        │           ├── models/route.ts
        │           ├── skills/route.ts
        │           └── threads/
        │               ├── search/route.ts
        │               └── [thread_id]/
        │                   ├── artifacts/[[...artifact_path]]/route.ts
        │                   └── history/route.ts
        │
        ├── components/                   # React 组件
        │   ├── ui/                       # Shadcn UI 组件 (47个)
        │   │   ├── button.tsx
        │   │   ├── card.tsx
        │   │   ├── dialog.tsx
        │   │   ├── input.tsx
        │   │   ├── select.tsx
        │   │   ├── tabs.tsx
        │   │   └── ... (其他 UI 组件)
        │   │
        │   ├── ai-elements/              # Vercel AI SDK 元素 (24个)
        │   │   ├── artifact.tsx
        │   │   ├── canvas.tsx
        │   │   ├── chain-of-thought.tsx
        │   │   ├── code-block.tsx
        │   │   ├── context.tsx
        │   │   ├── message.tsx
        │   │   ├── model-selector.tsx
        │   │   ├── plan.tsx
        │   │   ├── prompt-input.tsx
        │   │   ├── reasoning.tsx
        │   │   └── ... (其他 AI 元素)
        │   │
        │   ├── workspace/                # 工作区组件 (27个)
        │   │   ├── agents/               # Agent 组件
        │   │   │   ├── agent-card.tsx
        │   │   │   └── agent-gallery.tsx
        │   │   ├── artifacts/            # Artifact 组件
        │   │   │   ├── artifact-file-detail.tsx
        │   │   │   ├── artifact-file-list.tsx
        │   │   │   └── artifact-trigger.tsx
        │   │   ├── chats/                # 聊天组件
        │   │   │   ├── chat-box.tsx
        │   │   │   ├── use-chat-mode.ts
        │   │   │   └── use-thread-chat.ts
        │   │   ├── citations/            # 引用组件
        │   │   ├── messages/             # 消息组件
        │   │   │   ├── context.ts
        │   │   │   ├── markdown-content.tsx
        │   │   │   ├── message-group.tsx
        │   │   │   ├── message-list-item.tsx
        │   │   │   ├── message-list.tsx
        │   │   │   ├── skeleton.tsx
        │   │   │   └── subtask-card.tsx
        │   │   ├── settings/             # 设置组件 (13个)
        │   │   │   ├── about-settings-page.tsx
        │   │   │   ├── appearance-settings-page.tsx
        │   │   │   ├── memory-settings-page.tsx
        │   │   │   ├── notification-settings-page.tsx
        │   │   │   ├── settings-dialog.tsx
        │   │   │   ├── skill-settings-page.tsx
        │   │   │   └── tool-settings-page.tsx
        │   │   ├── code-editor.tsx
        │   │   ├── copy-button.tsx
        │   │   ├── input-box.tsx
        │   │   ├── recent-chat-list.tsx
        │   │   ├── streaming-indicator.tsx
        │   │   ├── thread-title.tsx
        │   │   ├── todo-list.tsx
        │   │   ├── welcome.tsx
        │   │   ├── workspace-container.tsx
        │   │   ├── workspace-header.tsx
        │   │   ├── workspace-sidebar.tsx
        │   │   └── ... (其他)
        │   │
        │   └── landing/                  # 首页组件 (8个)
        │       ├── footer.tsx
        │       ├── header.tsx
        │       ├── hero.tsx
        │       ├── progressive-skills-animation.tsx
        │       ├── section.tsx
        │       └── sections/
        │           ├── case-study-section.tsx
        │           ├── community-section.tsx
        │           ├── sandbox-section.tsx
        │           ├── skills-section.tsx
        │           └── whats-new-section.tsx
        │
        └── core/                         # 核心业务逻辑
            ├── agents/                   # Agent API 封装
            │   ├── api.ts
            │   ├── hooks.ts
            │   ├── index.ts
            │   └── types.ts
            │
            ├── api/                      # API 客户端
            │   ├── api-client.ts
            │   ├── index.ts
            │   ├── stream-mode.ts        # 流式响应处理
            │   └── stream-mode.test.ts
            │
            ├── artifacts/                # Artifact 管理
            │   ├── hooks.ts
            │   ├── index.ts
            │   ├── loader.ts
            │   └── utils.ts
            │
            ├── config/                   # 前端配置
            │   └── index.ts
            │
            ├── i18n/                     # 国际化 (en-US, zh-CN)
            │   ├── context.tsx
            │   ├── cookies.ts
            │   ├── hooks.ts
            │   ├── index.ts
            │   ├── locale.ts
            │   ├── locales/
            │   │   ├── index.ts
            │   │   ├── types.ts
            │   │   ├── en-US.ts
            │   │   └── zh-CN.ts
            │   └── server.ts
            │
            ├── mcp/                      # MCP 客户端
            │   ├── api.ts
            │   ├── hooks.ts
            │   ├── index.ts
            │   └── types.ts
            │
            ├── memory/                   # 内存系统
            │   ├── api.ts
            │   ├── hooks.ts
            │   ├── index.ts
            │   └── types.ts
            │
            ├── messages/                 # 消息处理
            │   └── utils.ts
            │
            ├── models/                   # 模型 API
            │   ├── api.ts
            │   ├── hooks.ts
            │   ├── index.ts
            │   └── types.ts
            │
            ├── notification/             # 通知系统
            │   └── hooks.ts
            │
            ├── rehype/                   # HTML 处理
            │   └── index.ts
            │
            ├── settings/                 # 设置管理
            │   ├── hooks.ts
            │   ├── index.ts
            │   └── local.ts
            │
            ├── skills/                   # 技能系统
            │   ├── api.ts
            │   ├── hooks.ts
            │   ├── index.ts
            │   └── type.ts
            │
            ├── streamdown/               # 流式渲染
            │   ├── index.ts
            │   └── plugins.ts
            │
            ├── tasks/                    # 任务系统
            │   ├── context.tsx
            │   ├── index.ts
            │   └── types.ts
            │
            ├── threads/                  # 对话线程 (核心)
            │   ├── hooks.ts              # useThreadStream, useSubmitThread
            │   ├── index.ts
            │   ├── types.ts
            │   └── utils.ts
            │
            ├── todos/                    # 待办事项
            │   ├── index.ts
            │   └── types.ts
            │
            ├── tools/                    # 工具
            │   └── utils.ts
            │
            ├── uploads/                  # 文件上传
            │   ├── api.ts
            │   ├── hooks.ts
            │   └── index.ts
            │
            └── utils/                    # 工具函数
                ├── datetime.ts
                ├── files.tsx
                ├── json.ts
                ├── markdown.ts
                └── uuid.ts
        │
        ├── hooks/                        # React Hooks
        │   └── use-mobile.ts
        │
        ├── lib/                          # 公共库
        │   └── utils.ts                  # cn() 工具
        │
        ├── server/                       # 服务端代码
        │   └── better-auth/              # Better Auth 配置
        │       ├── client.ts
        │       ├── config.ts
        │       ├── index.ts
        │       └── server.ts
        │
        └── styles/                       # 样式
            └── globals.css               # 全局样式
```

---

## 后端架构

### 1. 配置系统 (`config/`)

 DeerFlow 2.0 的配置分为两个文件：

#### config.yaml - 主配置文件

```yaml
# 配置版本控制 (用于检测过期配置)
config_version: 1

# 模型配置
models:
  - name: gpt-4
    display_name: GPT-4
    use: langchain_openai:ChatOpenAI
    model: gpt-4
    api_key: $OPENAI_API_KEY
    max_tokens: 4096
    temperature: 0.7
    supports_vision: true
    supports_thinking: true

# 工具组配置
tool_groups:
  - name: web
  - name: file:read
  - name: file:write
  - name: bash

# 工具配置
tools:
  - name: web_search
    group: web
    use: deerflow.community.tavily.tools:web_search_tool
    max_results: 5

# Sandbox 配置
sandbox:
  use: deerflow.sandbox.local:LocalSandboxProvider

# 技能配置
skills:
  container_path: /mnt/skills

# 标题生成配置
title:
  enabled: true
  max_words: 6
  max_chars: 60

# 摘要配置
summarization:
  enabled: true
  trigger:
    - type: tokens
      value: 15564
  keep:
    type: messages
    value: 10

# 记忆配置
memory:
  enabled: true
  storage_path: memory.json
  debounce_seconds: 30

# Checkpointer 配置 (状态持久化)
checkpointer:
  type: sqlite
  connection_string: checkpoints.db

# 渠道配置
channels:
  feishu:
    enabled: false
    app_id: $FEISHU_APP_ID
    app_secret: $FEISHU_APP_SECRET
```

#### extensions_config.json - 扩展配置

```json
{
  "mcpServers": {
    "server-name": {
      "enabled": true,
      "type": "sse",
      "url": "http://mcp-server:8000",
      "oauth": {
        "token_url": "http://auth:8000/token",
        "client_id": "client",
        "client_secret": "secret"
      }
    }
  },
  "skills": {
    "skill-name": {
      "enabled": true
    }
  }
}
```

### 2. Agent 系统 (`agents/`)

#### 主 Agent (Lead Agent)

```python
# packages/harness/deerflow/agents/lead_agent/agent.py

def make_lead_agent(config: RunnableConfig) -> CompiledGraph:
    """创建主 Agent"""
    # 1. 创建 LLM
    llm = create_chat_model(
        config.configurable.get("model_name"),
        config.configurable.get("thinking_enabled", False)
    )

    # 2. 获取可用工具
    tools = get_available_tools(
        subagent_enabled=config.configurable.get("subagent_enabled", False)
    )

    # 3. 应用提示模板
    system_prompt = apply_prompt_template(config)

    # 4. 构建调用链
    agent = (
        {"input": lambda x: x["messages"]}
        | system_prompt
        | llm.bind_tools(tools)
    )

    # 5. 构建中间件链 (执行顺序很重要!)
    middlewares = _build_middlewares(config)

    return agent | middlewares
```

#### 11 个中间件

| 中间件 | 顺序 | 作用 |
|--------|------|------|
| ThreadDataMiddleware | 1 | 创建线程目录 |
| UploadsMiddleware | 2 | 处理上传文件 |
| SandboxMiddleware | 3 | 获取沙箱环境 |
| DanglingToolCallMiddleware | 4 | 处理未完成的工具调用 |
| SummarizationMiddleware | 5 | 摘要超长对话 |
| TodoListMiddleware | 6 | 计划模式任务列表 |
| TitleMiddleware | 7 | 生成标题 |
| MemoryMiddleware | 8 | 记忆更新队列 |
| ViewImageMiddleware | 9 | 图像注入 |
| SubagentLimitMiddleware | 10 | 限制并发子 Agent |
| ClarificationMiddleware | 11 | 解释请求拦截 |

**中间件模式：**
```python
class Middleware(Protocol):
    def before_model(self, state: ThreadState) -> ThreadState: ...
    def after_model(self, state: ThreadState) -> ThreadState: ...
```

### 3. Sandbox 系统 (`sandbox/`)

沙箱提供隔离的执行环境，Agent 可以：

- 执行 bash 命令
- 读写文件
- 查看图片
- 列出目录

```python
# packages/harness/deerflow/sandbox/sandbox.py

class Sandbox(ABC):
    """沙箱抽象接口"""

    @abstractmethod
    async def execute_command(
        self, command: list[str], timeout: float | None = None
    ) -> tuple[str, str, int]:
        """执行命令，返回 (stdout, stderr, exit_code)"""
        pass

    @abstractmethod
    async def read_file(self, path: str) -> str:
        """读取文件"""
        pass

    @abstractmethod
    async def write_file(self, path: str, content: str) -> None:
        """写入文件"""
        pass

    @abstractmethod
    async def list_dir(self, path: str) -> str:
        """列出目录"""
        pass
```

**虚拟路径系统：**
```
Agent 看到的路径 (虚拟)         →    物理路径
/mnt/user-data/workspace/       →    .deer-flow/threads/{id}/user-data/workspace/
/mnt/user-data/uploads/         →    .deer-flow/threads/{id}/user-data/uploads/
/mnt/user-data/outputs/         →    .deer-flow/threads/{id}/user-data/outputs/
/mnt/skills/                    →    skills/
```

### 4. Tools 系统 (`tools/`)

工具分为四类：

#### 4.1 Config 定义的工具

```yaml
tools:
  - name: web_search
    group: web
    use: deerflow.community.tavily.tools:web_search_tool
    max_results: 5
```

#### 4.2 MCP 工具

```json
{
  "mcpServers": {
    "github": {
      "enabled": true,
      "type": "sse",
      "url": "https://mcp-github.server"
    }
  }
}
```

#### 4.3 内置工具

| 工具 | 说明 |
|------|------|
| `bash` | 执行命令 |
| `ls` | 列出目录 |
| `read_file` | 读取文件 |
| `write_file` | 写入文件 |
| `str_replace` | 字符串替换 |
| `present_files` | 公开输出文件 |
| `ask_clarification` | 请求澄清 |
| `view_image` | 查看图片 |

#### 4.4 Skill 工具

Skills 是预定义的工作流，每个 Skill 对应一个 `SKILL.md` 文件：

```markdown
---
name: research
description: Research and analyze information from the web
license: MIT
allowed-tools: [bash, read_file, write_file, web_search]
---

# Research Skill

This skill helps you research topics by:
1. Using web search to find information
2. Reading and analyzing the results
3. Writing a comprehensive report

## Usage
Ask the agent to "research X" and it will use this skill.
```

### 5. Sub-Agents 系统 (`subagents/`)

子 Agent 用于分解复杂任务：

```python
# packages/harness/deerflow/subagents/executor.py

class SubagentExecutor:
    """子 Agent 执行器"""

    def __init__(self):
        # 调度池 (3 workers) - 负责调度任务
        self._scheduler_pool = ThreadPoolExecutor(max_workers=3)
        # 执行池 (3 workers) - 负责执行任务
        self._execution_pool = ThreadPoolExecutor(max_workers=3)

    async def execute(
        self,
        task: str,
        agent_type: str = "general-purpose",
        max_turns: int = 50,
        timeout: float = 900.0  # 15 分钟
    ) -> dict:
        """执行子任务"""
        # 提交到执行池
        future = self._execution_pool.submit(self._run_agent, task, agent_type)

        # 轮询状态
        while not future.done():
            yield {"type": "task_running", "task_id": self.task_id}
            await asyncio.sleep(2)

        return future.result()
```

**内置子 Agent：**
- `general-purpose` - 通用 Agent (拥有所有工具)
- `bash` - Bash 命令专家

### 6. Memory 系统 (`agents/memory/`)

记忆系统存储用户上下文和偏好：

```python
# packages/harness/deerflow/agents/memory/updater.py

class MemoryUpdater:
    """记忆更新器"""

    def update_memory(self, messages: list[BaseMessage]) -> dict:
        """
        从对话中提取记忆：
        1. 用户上下文 (workContext, personalContext)
        2. 历史记录 (recentMonths, earlierContext)
        3. 原子事实 (facts with confidence score)
        """
        prompt = MEMORY_EXTRACTION_PROMPT.format(messages=messages)
        response = self_llm.invoke(prompt)

        return parse_memory_response(response)
```

**记忆存储格式：**
```json
{
  "userContext": {
    "workContext": "User works on backend engineering...",
    "personalContext": "Interested in AI agents...",
    "topOfMind": "Working on deerflow project..."
  },
  "history": {
    "recentMonths": ["Worked on project X", "Learned React..."],
    "earlierContext": ["Previously worked at Company Y..."],
    "longTermBackground": "Software engineer with 5 years experience..."
  },
  "facts": [
    {
      "id": "fact-1",
      "content": "User prefers TypeScript over JavaScript",
      "category": "preference",
      "confidence": 0.95,
      "createdAt": "2026-03-15T10:00:00Z",
      "source": "thread-123"
    }
  ]
}
```

---

## 前端架构

### 1. App Router 结构

```
/app
├── layout.tsx              # 根布局 (主题、i18n)
├── page.tsx                # Landing 页
├── workspace/              # 工作区
│   ├── layout.tsx
│   ├── page.tsx
│   ├── chats/              # 聊天
│   │   ├── [thread_id]/
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   └── page.tsx
│   └── agents/             # Agent
│       ├── [agent_name]/
│       │   └── chats/
│       │       └── [thread_id]/
│       │           ├── layout.tsx
│       │           └── page.tsx
│       ├── new/
│       │   └── page.tsx
│       └── page.tsx
└── mock/                   # Mock API
    └── api/
```

### 2. 核心业务逻辑 (`core/`)

#### Threads (对话线程)

```typescript
// core/threads/hooks.ts

export function useThreadStream(
  threadId: string,
  message: string,
  options?: StreamOptions
) {
  const { stream } = useAPIClient();

  // 流式调用 LangGraph
  const stream$ = stream(threadId, message, options);

  // 处理流式事件
  useEventSource(stream$, (event) => {
    switch (event.type) {
      case "messages-tuple":
        // 更新消息
        updateMessage(event.data);
        break;
      case "values":
        // 更新状态
        updateState(event.data);
        break;
      case "end":
        // 流完成
        completeStream();
        break;
    }
  });
}
```

#### API 客户端

```typescript
// core/api/api-client.ts

export class APIClient {
  private langgraphUrl: string;
  private backendUrl: string;

  // 流式调用
  async stream(
    threadId: string,
    message: string,
    options?: StreamOptions
  ): Promise<ReadableStream> {
    const res = await fetch(
      `${this.langgraphUrl}/threads/${threadId}/stream`,
      {
        method: "POST",
        body: JSON.stringify({ message, ...options }),
      }
    );
    return res.body!;
  }

  // 列表调用
  async listThreads(): Promise<ThreadsListResponse> {
    const res = await fetch(`${this.backendUrl}/threads`);
    return res.json();
  }
}
```

### 3. 组件系统

#### Workspace 组件

```
workspace/
├── workspace-container.tsx     # 主容器
├── workspace-header.tsx        # 头部 ( modeled, model selector, plan switch)
├── workspace-sidebar.tsx       # 侧边栏
├── workspace-nav-menu.tsx      # 导航菜单
├── recent-chat-list.tsx        # 最近对话列表
├── agent-welcome.tsx           # Agent 欢迎消息
└── input-box.tsx               # 输入框 (核心交互)
```

#### AI Elements 组件

```
ai-elements/
├── prompt-input.tsx            # 提示输入框 (带插入菜单)
├── message.tsx                 # 消息渲染
├── code-block.tsx              # 代码块
├── artifact.tsx                # Artifact 渲染
├── chain-of-thought.tsx        # 思考链显示
├── reasoning.tsx               # 推理过程
├── plan.tsx                    # 计划显示
├── model-selector.tsx          # 模型选择器
└── conversation.tsx            # 对话视图
```

### 4. 国际化 (i18n)

```typescript
// core/i18n/locales/en-US.ts
// core/i18n/locales/zh-CN.ts

export const enUS = {
  workspace: {
    title: "DeerFlow Workspace",
    newChat: "New Chat",
    agents: "Agents",
    chats: "Chats",
  },
  // ...
};

export const zhCN = {
  workspace: {
    title: "DeerFlow 工作区",
    newChat: "新对话",
    agents: "Agents",
    chats: "对话",
  },
  // ...
};
```

---

## 核心配置

### 配置加载流程

```python
# packages/harness/deerflow/config/app_config.py

def get_app_config() -> AppConfig:
    """获取配置 (单例模式)"""
    global _app_config
    if _app_config is None:
        _app_config = AppConfig.from_file()
    return _app_config

# 配置查找顺序
# 1. DEER_FLOW_CONFIG_PATH 环境变量
# 2. 当前目录 config.yaml
# 3. 父目录 config.yaml
```

### 环境变量

```bash
# .env

# API Keys
OPENAI_API_KEY=sk-xxxx
ANTHROPIC_API_KEY=sk-ant-xxxx
DEEPSEEK_API_KEY=sk-xxxx

# 渠道配置
FEISHU_APP_ID=cli_xxxx
FEISHU_APP_SECRET=xxxx
SLACK_BOT_TOKEN=xoxb-xxxx
SLACK_APP_TOKEN=xapp-xxxx
TELEGRAM_BOT_TOKEN=123456789:xxxx

# 沙箱配置
DOCKER_HOST=unix:///var/run/docker.sock

# LangGraph
LANGGRAPH_URL=http://localhost:2024
LANGGRAPH_API_KEY=xxxx
LANGGRAPH_GRAPH_ID=lead_agent
```

---

## 关键组件

### 1. ThreadState (线程状态)

```python
# packages/harness/deerflow/agents/thread_state.py

class ThreadState(AgentState):
    """线程状态 - 扩展自 AgentState"""

    messages: Annotated[list[BaseMessage], add_messages]

    # Thread 独有字段
    thread_id: str
    thread_data: dict
    sandbox: SandboxContext
    title: str | None
    artifacts: Annotated[list[Artifact], merge_artifacts]
    todos: Annotated[list[Todo], merge_todos]
    uploaded_files: Annotated[list[UploadedFile], merge_uploaded_files]
    viewed_images: Annotated[list[ImageContent], merge_viewed_images]
```

### 2. Agent 启动流程

```python
# LangGraph Server 启动
# 1. 读取配置
config = get_app_config()

# 2. 创建 Agent
agent = make_lead_agent(config)

# 3. 注册到 LangGraph
app = langgraph.create_app(agent)
```

### 3. Skills 加载

```python
# packages/harness/deerflow/skills/loader.py

def load_skills() -> list[Skill]:
    """递归扫描 skills 目录"""
    skills = []

    for skill_dir in ["skills/public", "skills/custom"]:
        for path in Path(skill_dir).rglob("SKILL.md"):
            skill = parse_skill(path)
            skills.append(skill)

    return skills

def parse_skill(path: Path) -> Skill:
    """解析 SKILL.md"""
    content = path.read_text()

    # 解析 YAML frontmatter
    frontmatter, readme = split_frontmatter(content)
    metadata = yaml.safe_load(frontmatter)

    return Skill(
        name=metadata["name"],
        description=metadata["description"],
        path=path.parent,
        readme=readme,
        # ...
    )
```

---

## 数据流

### 聊天流程

```
用户输入
    ↓
[前端] InputBox onSubmit()
    ↓
[前端] useThreadStream()
    ↓
[前端] APIClient.stream()
    ↓
[LangGraph] /threads/{id}/stream
    ↓
[Agent] make_lead_agent()
    ↓
    ├──→ ThreadDataMiddleware (创建目录)
    ├──→ UploadsMiddleware (处理文件)
    ├──→ SandboxMiddleware (获取沙箱)
    ├──→ Middlewares...
    │
    ↓
[LLM] ChatOpenAI / Claude / ...
    ↓
[Agent] 返回 AIMessage
    ↓
[Tool Calling] if tools needed
    ↓
[Tools] bash / read_file / web_search / ...
    ↓
[Tool Result] ToolMessage
    ↓
[Agent] 继续...
    ↓
[中间件] TitleMiddleware (生成标题)
[中间件] MemoryMiddleware (加入队列)
[中间件] ArtifactsMiddleware (收集输出)
    ↓
[Stream] SSE Events
    ↓
[前端] 更新 UI
```

### 文件上传流程

```
用户选择文件
    ↓
[前端] Upload files
    ↓
[Gateway] POST /api/threads/{id}/uploads
    ↓
[Document Conversion] PDF/PPT/Excel/Word → Markdown
    ↓
[Store] .deer-flow/threads/{id}/user-data/uploads/
    ↓
[Return] { success: true, files: [...] }
    ↓
[Middleware] UploadsMiddleware
    ↓
[Agent] Injection to system prompt
```

### Memory 更新流程

```
用户对话
    ↓
[Agent] AIMessage + UserMessage
    ↓
[Middleware] MemoryMiddleware
    ↓
[Queue] 添加到更新队列
    ↓
[Debounce] 等待 30秒 (debounce_seconds)
    ↓
[Batch] 批量处理 (deduplication)
    ↓
[LLM] 提取 facts and context
    ↓
[Store] atomically write to memory.json
    ↓
[Cache] invalidation
    ↓
[Next Chat] 注入到 system prompt
```

---

## 开发指南

### 环境搭建

```bash
# 克隆项目
git clone https://github.com/bytedance/deer-flow.git
cd deer-flow

# 生成配置
make config

# 安装依赖
make install

# 开发模式
make dev
```

### 后端开发

```bash
cd backend

# 运行 LangGraph Server
make dev

# 运行 Gateway API
make gateway

# 运行测试
make test

# Lint
make lint

# 格式化
make format
```

### 前端开发

```bash
cd frontend

# 开发
pnpm dev

# 构建
pnpm build

# 检查
pnpm check

# Lint
pnpm lint
```

---

## 最佳实践

### 1. 配置管理

- ✅ 使用 `.env` 文件存储 API keys
- ✅ 使用 `config.example.yaml` 作为模板
- ✅ 启动时检查 `config_version`
- ✅ 环境变量使用 `$VARIABLE_NAME` 语法

### 2. 代码规范

**后端：**
- Python 3.12+
- 使用类型提示
- 每个模块 < 800 行
- 遵循 PEP 8

**前端：**
- TypeScript 5.8+
- React 19 + Server Components
- 使用 `cn()` 工具类
- 遵循项目 ESLint 规则

### 3. 工具注册

```python
# 正确做法
@tool
def my_tool(param: str) -> str:
    """Tool description."""
    return f"Result: {param}"

# 注册到 tools list
tools = [my_tool]
```

### 4. 错误处理

```python
try:
    result = await sandbox.execute_command(["ls", "/tmp"])
except TimeoutError:
    logger.error("Command timeout")
    return "Error: Command timed out"
except SandboxError as e:
    logger.error(f"Sandbox error: {e}")
    return f"Error: {e}"

---

## 企业级全栈应用架构 (deerflow-enterprise-project)

除了 DeerFlow 2.0 框架本身，本项目还包含一个基于 DeerFlow 2.0 构建的**企业级全栈应用**，展示了如何在生产环境中使用 DeerFlow 2.0 构建完整的 AI Agent 系统。

### 项目概述

**deerflow-enterprise-project** 是一个生产就绪的企业 AI Agent 管理平台，包含：

- **后端**: FastAPI + SQLAlchemy + PostgreSQL + DeerFlow 2.0 Harness
- **前端**: Next.js 16 + React 19 + TypeScript + Tailwind CSS + Shadcn UI
- **基础设施**: Docker Compose + Redis + Nginx

### 系统架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         前端层 (Frontend Layer)                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    Next.js 16 Application                        │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │    │
│  │  │  Dashboard  │  │   Agents    │  │      Tasks/Memory       │  │    │
│  │  │   首页      │  │   管理      │  │      任务/记忆管理       │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────┘  │    │
│  │                                                                  │    │
│  │  技术栈: React 19 + TypeScript 5.8 + Tailwind CSS 4              │    │
│  │           React Query 5 + Shadcn UI + Radix UI                   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                  │                                      │
│                              HTTP/WebSocket                             │
└──────────────────────────────────┼──────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────────────┐
│                      API 网关层 (API Gateway Layer)                      │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    FastAPI 0.109 Application                     │    │
│  │                                                                  │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │    │
│  │  │ /auth    │ │ /agents  │ │ /tasks   │ │ /memory  │            │    │
│  │  │ 认证     │ │ Agent管理 │ │ 任务管理 │ │ 记忆系统 │            │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘            │    │
│  │                                                                  │    │
│  │  功能: JWT Auth + CORS + Pydantic 2.5 + 自动API文档              │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────┼──────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────────────┐
│                      服务层 (Service Layer)                              │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │    │
│  │  │ AuthService │  │AgentService │  │    TaskService          │  │    │
│  │  │  认证服务    │  │  Agent服务  │  │    任务服务              │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────┘  │    │
│  │                                                                  │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │    │
│  │  │MemoryService│  │ThreadService│  │   DeerFlow Harness      │  │    │
│  │  │  记忆服务    │  │  线程服务   │  │   DeerFlow 2.0 核心      │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────┼──────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────────────┐
│                      数据层 (Data Layer)                                 │
│  ┌─────────────────────────┐  ┌─────────────────────────────────────┐   │
│  │    PostgreSQL 15        │  │           Redis 7                   │   │
│  │  ┌─────────┐ ┌────────┐ │  │  ┌─────────┐ ┌─────────────────┐   │   │
│  │  │  users  │ │ agents │ │  │  │  cache  │ │  session store  │   │   │
│  │  │ 用户表  │ │Agent表 │ │  │  │  缓存   │ │   会话存储       │   │   │
│  │  └─────────┘ └────────┘ │  │  └─────────┘ └─────────────────┘   │   │
│  │  ┌─────────┐ ┌────────┐ │  └─────────────────────────────────────┘   │
│  │  │  tasks  │ │memory  │ │                                            │
│  │  │ 任务表  │ │记忆表  │ │  ORM: SQLAlchemy 2.0 + Alembic Migrations │   │
│  │  └─────────┘ └────────┘ │                                            │
│  └─────────────────────────┘                                            │
└─────────────────────────────────────────────────────────────────────────┘
```

### 目录结构

```
deerflow-enterprise-project/
├── README.md                          # 项目说明文档
├── CLAUDE.md                          # 开发指南
├── docker-compose.yml                 # Docker 编排配置
├── .env.example                       # 环境变量示例
│
├── backend/                           # 后端应用 (FastAPI)
│   ├── Dockerfile
│   ├── requirements.txt               # Python 依赖
│   ├── alembic.ini                    # Alembic 配置
│   ├── alembic/                       # 数据库迁移
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/                  # 迁移版本
│   │
│   ├── app/                           # 应用层
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI 入口
│   │   ├── deps.py                    # 依赖注入
│   │   │
│   │   ├── api/                       # API 路由
│   │   │   └── v1/
│   │   │       ├── api.py             # 路由组装
│   │   │       ├── auth.py            # 认证 API
│   │   │       ├── agents.py          # Agent 管理 API
│   │   │       ├── tasks.py           # 任务管理 API
│   │   │       ├── memory.py          # 记忆系统 API
│   │   │       └── threads.py         # 线程管理 API
│   │   │
│   │   ├── core/                      # 核心配置
│   │   │   ├── __init__.py
│   │   │   ├── config.py              # 应用配置
│   │   │   ├── database.py            # 数据库连接
│   │   │   └── security.py            # 安全工具 (JWT)
│   │   │
│   │   ├── models/                    # SQLAlchemy 模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py                # 用户模型
│   │   │   ├── agent.py               # Agent 模型
│   │   │   ├── task.py                # 任务模型
│   │   │   ├── memory.py              # 记忆模型
│   │   │   └── thread.py              # 线程模型
│   │   │
│   │   ├── schemas/                   # Pydantic 模式
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                # 认证模式
│   │   │   ├── agent.py               # Agent 模式
│   │   │   ├── task.py                # 任务模式
│   │   │   └── user.py                # 用户模式
│   │   │
│   │   └── services/                  # 业务逻辑层
│   │       ├── __init__.py
│   │       ├── auth_service.py        # 认证服务
│   │       ├── agent_service.py       # Agent 服务
│   │       └── task_service.py        # 任务服务
│   │
│   ├── packages/harness/              # DeerFlow 2.0 Harness
│   │   └── deerflow/                  # 框架核心
│   │
│   └── tests/                         # 测试套件
│
└── frontend/                          # 前端应用 (Next.js)
    ├── Dockerfile
    ├── package.json                   # Node.js 依赖
    ├── next.config.js                 # Next.js 配置
    ├── tsconfig.json                  # TypeScript 配置
    ├── tailwind.config.js             # Tailwind CSS 配置
    │
    ├── src/
    │   ├── app/                       # Next.js App Router
    │   │   ├── layout.tsx             # 根布局
    │   │   ├── page.tsx               # 首页 (Landing)
    │   │   │
    │   │   ├── (dashboard)/           # Dashboard 路由组
    │   │   │   ├── layout.tsx         # Dashboard 布局
    │   │   │   ├── page.tsx           # Dashboard 首页
    │   │   │   │
    │   │   │   ├── agents/            # Agent 管理
    │   │   │   │   ├── page.tsx       # Agent 列表
    │   │   │   │   └── new/           # 新建 Agent
    │   │   │   │       └── page.tsx
    │   │   │   │
    │   │   │   ├── tasks/             # 任务管理
    │   │   │   │   └── page.tsx
    │   │   │   │
    │   │   │   ├── memory/            # 记忆系统
    │   │   │   │   └── page.tsx
    │   │   │   │
    │   │   │   └── threads/           # 线程管理
    │   │   │       └── page.tsx
    │   │   │
    │   │   ├── login/                 # 登录页面
    │   │   │   └── page.tsx
    │   │   │
    │   │   └── register/              # 注册页面
    │   │       └── page.tsx
    │   │
    │   ├── components/                # React 组件
    │   │   ├── layout/                # 布局组件
    │   │   │   ├── Sidebar.tsx        # 侧边栏导航
    │   │   │   └── Header.tsx         # 顶部导航栏
    │   │   │
    │   │   ├── ui/                    # Shadcn UI 组件
    │   │   │   ├── button.tsx
    │   │   │   ├── input.tsx
    │   │   │   ├── card.tsx
    │   │   │   ├── dialog.tsx
    │   │   │   ├── dropdown-menu.tsx
    │   │   │   ├── avatar.tsx
    │   │   │   ├── alert.tsx
    │   │   │   ├── label.tsx
    │   │   │   └── badge.tsx
    │   │   │
    │   │   └── providers.tsx          # 全局 Provider
    │   │
    │   ├── lib/                       # 工具库
    │   │   ├── utils.ts               # 工具函数
    │   │   └── api/                   # API 客户端
    │   │       ├── client.ts          # API 基础客户端
    │   │       ├── auth.ts            # 认证 API
    │   │       ├── agents.ts          # Agent API
    │   │       └── hooks.ts           # React Query Hooks
    │   │
    │   ├── hooks/                     # 自定义 Hooks
    │   │   └── useAuth.ts             # 认证 Hook
    │   │
    │   └── styles/                    # 样式文件
    │       └── globals.css            # 全局样式
    │
    └── public/                        # 静态资源
```

### 后端架构详解

#### 1. 认证系统 (JWT)

```python
# app/core/security.py

from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """哈希密码"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """创建 JWT Token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

#### 2. API 路由结构

| 路由 | 功能 | 认证 |
|------|------|------|
| `POST /api/v1/auth/register` | 用户注册 | 否 |
| `POST /api/v1/auth/login` | 用户登录 | 否 |
| `GET /api/v1/auth/me` | 获取当前用户 | 是 |
| `GET /api/v1/agents` | 获取 Agent 列表 | 是 |
| `POST /api/v1/agents` | 创建 Agent | 是 |
| `GET /api/v1/agents/{id}` | 获取 Agent 详情 | 是 |
| `PUT /api/v1/agents/{id}` | 更新 Agent | 是 |
| `DELETE /api/v1/agents/{id}` | 删除 Agent | 是 |
| `GET /api/v1/tasks` | 获取任务列表 | 是 |
| `POST /api/v1/tasks` | 创建任务 | 是 |
| `GET /api/v1/memory` | 获取记忆列表 | 是 |
| `POST /api/v1/memory` | 创建记忆 | 是 |

#### 3. 数据库模型关系

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    users    │       │    agents   │       │    tasks    │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │◄──────┤ id (PK)     │       │ id (PK)     │
│ email       │       │ name        │       │ title       │
│ username    │       │ description │       │ status      │
│ hashed_pass │       │ config      │       │ agent_id(FK)│
│ is_active   │       │ owner_id(FK)│       │ owner_id(FK)│
│ created_at  │       │ created_at  │       │ created_at  │
└─────────────┘       └─────────────┘       └─────────────┘
        │                                            │
        │       ┌─────────────┐                      │
        └──────►│   memory    │◄─────────────────────┘
                ├─────────────┤
                │ id (PK)     │
                │ content     │
                │ user_id(FK) │
                │ created_at  │
                └─────────────┘
```

### 前端架构详解

#### 1. 页面路由

| 路由 | 页面 | 描述 |
|------|------|------|
| `/` | Landing Page | 产品介绍首页 |
| `/login` | 登录 | 用户登录页面 |
| `/register` | 注册 | 用户注册页面 |
| `/dashboard` | Dashboard | 仪表盘首页 |
| `/agents` | Agent 管理 | Agent 列表和创建 |
| `/tasks` | 任务管理 | 任务列表和状态 |
| `/memory` | 记忆系统 | 记忆浏览和管理 |
| `/threads` | 线程管理 | 对话线程列表 |

#### 2. 状态管理

```typescript
// 使用 React Query 进行服务端状态管理

// lib/api/hooks.ts
export function useAgents() {
  return useQuery({
    queryKey: ['agents'],
    queryFn: fetchAgents,
  });
}

export function useCreateAgent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createAgent,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
  });
}
```

#### 3. 组件层次

```
app/layout.tsx (Root Layout)
├── Providers (React Query, Auth Context)
└── (dashboard)/layout.tsx (Dashboard Layout)
    ├── Sidebar (导航)
    ├── Header (顶部栏)
    └── page.tsx (页面内容)
        ├── StatsCards (统计卡片)
        ├── RecentActivity (最近活动)
        └── QuickActions (快捷操作)
```

### Docker 部署架构

```yaml
# docker-compose.yml 服务定义

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: deerflow
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/deerflow
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: your-secret-key
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

### 技术栈对比

| 层级 | 框架版 (deer-flow) | 企业版 (deerflow-enterprise) |
|------|-------------------|------------------------------|
| **后端框架** | LangGraph Server | FastAPI + DeerFlow Harness |
| **前端框架** | Next.js 16 | Next.js 16 |
| **数据库** | 可选 PostgreSQL | PostgreSQL + Redis |
| **认证** | Better Auth | JWT + 自定义认证 |
| **ORM** | - | SQLAlchemy 2.0 |
| **部署** | LangGraph CLI | Docker Compose |
| **API 风格** | LangGraph 协议 | RESTful API |

### 适用场景

**DeerFlow 2.0 框架版** 适合：
- 快速原型开发
- 集成到现有系统
- 需要 LangGraph 生态
- 使用 Claude Code 等工具

**企业级全栈版** 适合：
- 生产环境部署
- 多用户管理系统
- 需要完整的 Web 界面
- 自定义业务逻辑
- 企业级安全和权限控制

---

## 总结

DeerFlow 2.0 是一个功能完善的 AI Agent 框架，主要特点：

| 特性 | 描述 |
|------|------|
| **LangGraph** | 基于 LangGraph 的 Agent 编排 |
| **Middleware** | 11 个中间件提供横切功能 |
| **Sandbox** | 隔离的文件系统和命令执行 |
| **Skills** | 插件式技能系统 |
| **Sub-Agents** | 任务分解和并行执行 |
| **Memory** | 长短期记忆系统 |
| **MCP** | Model Context Protocol 支持 |
| **IM Channels** | 飞书/Slack/Telegram 集成 |
| **Artifacts** | 文件输出和展示 |

这个架构设计清晰，模块化程度高，易于扩展和维护。

### 两种使用方式

**1. DeerFlow 2.0 框架版** (bytedance/deer-flow)
- 直接使用官方框架
- 适合快速原型和集成
- 使用 LangGraph CLI 部署

**2. 企业级全栈应用** (deerflow-enterprise-project)
- 基于框架构建的完整应用
- 包含用户管理、Web 界面、数据库
- 使用 Docker Compose 部署
- 适合生产环境

两种架构各有优势，可根据实际需求选择使用。

---

## 参考资料

- [DeerFlow 官方仓库](https://github.com/bytedance/deer-flow)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [LangChain 文档](https://python.langchain.com/)

---

*本文档由 Claude AI Assistant 生成，用于 DeerFlow 2.0 学习和研究。*
