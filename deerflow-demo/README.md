# DeerFlow 2.0 应用开发案例集

本目录包含 23 个完整的 DeerFlow 2.0 应用开发案例，涵盖从基础使用到企业级部署的各个层面。

## 目录结构

```
deeflow-demo/
├── README.md                 # 本文件
├── examples/                 # 案例代码目录
│   ├── case01_basic_usage.py         # 基础客户端使用
│   ├── case02_advanced_config.py     # 高级配置使用
│   ├── case03_fastapi_integration.py # FastAPI Web服务
│   ├── case04_multi_agent.py         # 多Agent协作系统
│   ├── case05_websocket_chat.py      # WebSocket实时对话
│   ├── case06_mcp_config.py          # MCP配置管理
│   ├── case07_database_integration.py # 数据库集成
│   ├── case08_file_upload.py         # 文件上传处理
│   ├── case09_custom_tool.py         # 自定义工具开发
│   ├── case10_task_scheduler.py      # 任务调度系统
│   ├── case11_memory_system.py       # 记忆系统增强
│   ├── case12_multimodal.py          # 多模态内容生成
│   ├── case13_api_gateway.py         # API网关
│   ├── case14_monitoring.py          # 监控与日志
│   ├── case15_ab_testing.py          # A/B测试框架
│   ├── case16_cache_optimization.py  # 缓存优化
│   ├── case17_distributed.py         # 分布式部署
│   ├── case18_data_pipeline.py       # 数据管道集成
│   ├── case19_security.py            # 安全加固方案
│   ├── case20_performance.py         # 性能优化技巧
│   ├── case21_testing.py             # 测试策略
│   ├── case22_cicd.py                # CI/CD集成
│   └── case23_kubernetes.py          # 容器化部署
```

## 案例分类

### 基础使用 (案例 1-3)

| 案例 | 名称 | 描述 |
|-----|------|------|
| 案例 1 | 基础客户端使用 | DeerFlowClient 基础用法、流式输出 |
| 案例 2 | 高级配置使用 | 自定义配置、模型选择、技能管理 |
| 案例 3 | FastAPI Web服务 | RESTful API、SSE流式输出 |

### 高级功能 (案例 4-6)

| 案例 | 名称 | 描述 |
|-----|------|------|
| 案例 4 | 多Agent协作系统 | 研究员、写作者、审核员、程序员协作 |
| 案例 5 | WebSocket实时对话 | 实时双向通信、在线聊天界面 |
| 案例 6 | MCP配置管理 | 模型上下文协议、MCP服务器配置 |

### 数据与存储 (案例 7-8)

| 案例 | 名称 | 描述 |
|-----|------|------|
| 案例 7 | 数据库集成 | PostgreSQL、SQLAlchemy、对话持久化 |
| 案例 8 | 文件上传处理 | 多格式支持、文档解析、批量上传 |

### 工具与扩展 (案例 9-11)

| 案例 | 名称 | 描述 |
|-----|------|------|
| 案例 9 | 自定义工具开发 | 天气、计算器、文件管理、翻译、代码分析 |
| 案例 10 | 任务调度系统 | 定时任务、工作流调度、批处理 |
| 案例 11 | 记忆系统增强 | 长期记忆、上下文管理、记忆整合 |

### 多模态与内容 (案例 12)

| 案例 | 名称 | 描述 |
|-----|------|------|
| 案例 12 | 多模态内容生成 | 图像处理、文档分析、多模态响应 |

### 企业级特性 (案例 13-16)

| 案例 | 名称 | 描述 |
|-----|------|------|
| 案例 13 | API网关 | 统一入口、认证、限流、OpenAI兼容接口 |
| 案例 14 | 监控与日志 | 指标收集、告警、追踪、监控面板 |
| 案例 15 | A/B测试框架 | 模型对比、效果评估、流量分配 |
| 案例 16 | 缓存优化 | 内存缓存、Redis、缓存策略、性能提升 |

### 运维与部署 (案例 17-23)

| 案例 | 名称 | 描述 |
|-----|------|------|
| 案例 17 | 分布式部署 | 服务发现、负载均衡、熔断器 |
| 案例 18 | 数据管道集成 | ETL、数据转换、批处理 |
| 案例 19 | 安全加固方案 | 输入验证、输出过滤、PII保护 |
| 案例 20 | 性能优化技巧 | 连接池、批量处理、异步优化、内存管理 |
| 案例 21 | 测试策略 | 单元测试、集成测试、性能测试、Mock |
| 案例 22 | CI/CD集成 | GitHub Actions、Docker、自动化部署 |
| 案例 23 | 容器化部署 | Kubernetes、Helm、Istio服务网格 |

## 快速开始

### 环境要求

- Python 3.9+
- DeerFlow 2.0 已安装
- 相关依赖包（各案例有具体说明）

### 安装依赖

```bash
# 基础依赖
pip install deerflow

# Web服务相关
pip install fastapi uvicorn websockets

# 数据库相关
pip install sqlalchemy psycopg2-binary

# 缓存相关
pip install redis

# 测试相关
pip install pytest pytest-asyncio

# 其他工具
pip install pyyaml aiohttp
```

### 运行案例

```bash
# 进入案例目录
cd deerflow-demo/examples

# 运行基础使用案例
python case01_basic_usage.py

# 运行 FastAPI 服务
python case03_fastapi_integration.py

# 运行 WebSocket 服务
python case05_websocket_chat.py
```

## 核心概念

### DeerFlowClient

所有案例都基于 `DeerFlowClient` 类，这是 DeerFlow 2.0 的核心客户端：

```python
from deerflow.client import DeerFlowClient

# 基础初始化
client = DeerFlowClient()

# 高级初始化
client = DeerFlowClient(
    config_path="./config.yaml",
    model_name="gpt-4",
    thinking_enabled=True,
    subagent_enabled=True,
    plan_mode=True
)
```

### 流式输出

```python
# 流式对话
for event in client.stream("Hello", thread_id="demo"):
    if event.type == "messages-tuple":
        print(event.data.get("content", ""), end="")
    elif event.type == "end":
        print("\n对话结束")
```

### 多轮对话

```python
thread_id = "my-conversation-001"

# 第一轮
response1 = client.chat("什么是AI？", thread_id=thread_id)

# 第二轮（自动保持上下文）
response2 = client.chat("它有哪些应用？", thread_id=thread_id)
```

## 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                        应用层                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ Web应用  │ │ 定时任务 │ │ 数据处理 │ │ API服务  │       │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘       │
├───────┼────────────┼────────────┼────────────┼─────────────┤
│       │            │            │            │              │
│  ┌────┴────────────┴────────────┴────────────┴─────┐        │
│  │              DeerFlow 2.0 核心层                │        │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐        │        │
│  │  │ Lead Agent│ │ Subagents│ │  Tools   │        │        │
│  │  └──────────┘ └──────────┘ └──────────┘        │        │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐        │        │
│  │  │  Memory  │ │  Skills  │ │  MCP     │        │        │
│  │  └──────────┘ └──────────┘ └──────────┘        │        │
│  └─────────────────────────────────────────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                        基础设施层                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │  数据库  │ │   缓存   │ │  消息队列│ │  存储    │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## 最佳实践

### 1. 错误处理

```python
try:
    response = client.chat("Hello")
except Exception as e:
    logger.error(f"Chat failed: {e}")
    # 降级处理
```

### 2. 超时控制

```python
import asyncio

try:
    response = await asyncio.wait_for(
        asyncio.get_event_loop().run_in_executor(None, client.chat, "Hello"),
        timeout=30.0
    )
except asyncio.TimeoutError:
    print("Request timeout")
```

### 3. 资源管理

```python
# 使用连接池
pool = ConnectionPool(pool_size=10)

# 使用上下文管理器
async with pool.acquire() as client:
    response = await client.chat("Hello")
```

### 4. 监控与日志

```python
# 记录请求日志
logger.info(f"Request: {message[:50]}...")

# 记录性能指标
metrics.record_latency(time.time() - start_time)
```

## 常见问题

### Q: 如何处理长对话的上下文限制？

A: 使用记忆系统（案例 11）定期总结和压缩上下文，或开启 `plan_mode` 让 Agent 自动管理。

### Q: 如何优化高并发场景？

A: 参考案例 17（分布式部署）和案例 20（性能优化），使用连接池、负载均衡和缓存。

### Q: 如何保护敏感信息？

A: 参考案例 19（安全加固），使用输入验证、输出过滤和 PII 检测。

### Q: 如何部署到生产环境？

A: 参考案例 22（CI/CD）和案例 23（Kubernetes），使用容器化和自动化部署。

## 贡献指南

欢迎提交新的案例或改进现有案例！请遵循以下规范：

1. 每个案例一个独立的 Python 文件
2. 包含完整的文档字符串和注释
3. 提供使用示例和测试代码
4. 更新本 README 的相关章节

## 许可证

MIT License

## 相关资源

- [DeerFlow 官方文档](https://github.com/bytedance/deer-flow)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)

---

**注意**: 本案例集基于 DeerFlow 2.0 版本编写，部分 API 可能随版本更新而变化。请参考官方文档获取最新信息。
