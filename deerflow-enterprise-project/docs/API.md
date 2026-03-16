# DeerFlow Enterprise - API 文档

本文档详细描述了 DeerFlow Enterprise 项目的后端 API 接口。

## 📋 目录

1. [认证 API](#认证-api)
2. [用户 API](#用户-api)
3. [Agent API](#agent-api)
4. [对话 API](#对话-api)
5. [任务 API](#任务-api)
6. [记忆 API](#记忆-api)
7. [错误处理](#错误处理)

## 认证 API

### 注册用户
- **POST** `/api/v1/auth/register`
- **描述**: 创建新用户账户
- **请求体**:
  ```json
  {
    "email": "string",
    "username": "string",
    "password": "string",
    "full_name": "string"
  }
  ```
- **响应**:
  ```json
  {
    "success": true,
    "data": {
      "id": "uuid",
      "email": "string",
      "username": "string",
      "full_name": "string",
      "created_at": "timestamp"
    }
  }
  ```

### 用户登录
- **POST** `/api/v1/auth/login`
- **描述**: 用户登录并获取 JWT 令牌
- **请求体**:
  ```
  username=user@example.com&password=password123
  ```
- **响应**:
  ```json
  {
    "access_token": "jwt_token_string",
    "token_type": "bearer",
    "user": {
      "id": "uuid",
      "email": "string",
      "username": "string",
      "full_name": "string"
    }
  }
  ```

### 获取当前用户
- **GET** `/api/v1/auth/me`
- **描述**: 获取当前认证用户的详细信息
- **认证**: Bearer Token
- **响应**:
  ```json
  {
    "id": "uuid",
    "email": "string",
    "username": "string",
    "full_name": "string",
    "created_at": "timestamp",
    "updated_at": "timestamp"
  }
  ```

### 更新用户信息
- **PUT** `/api/v1/auth/me`
- **描述**: 更新当前认证用户的信息
- **认证**: Bearer Token
- **请求体**:
  ```json
  {
    "full_name": "string",
    "username": "string"
  }
  ```
- **响应**:
  ```json
  {
    "id": "uuid",
    "email": "string",
    "username": "string",
    "full_name": "string",
    "updated_at": "timestamp"
  }
  ```

### 修改密码
- **POST** `/api/v1/auth/change-password`
- **描述**: 修改当前用户密码
- **认证**: Bearer Token
- **请求体**:
  ```json
  {
    "current_password": "string",
    "new_password": "string"
  }
  ```
- **响应**:
  ```json
  {
    "message": "Password changed successfully"
  }
  ```

### 获取用户列表（管理员）
- **GET** `/api/v1/auth/users`
- **描述**: 获取所有用户列表（仅限管理员）
- **认证**: Bearer Token
- **响应**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "uuid",
        "email": "string",
        "username": "string",
        "full_name": "string",
        "created_at": "timestamp"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 100
    }
  }
  ```

## 用户 API

所有用户相关的 API 都位于 `/api/v1/users` 路径下。

### 获取用户详情
- **GET** `/api/v1/users/{user_id}`
- **描述**: 获取指定用户的信息
- **认证**: Bearer Token
- **响应**:
  ```json
  {
    "id": "uuid",
    "email": "string",
    "username": "string",
    "full_name": "string",
    "created_at": "timestamp",
    "updated_at": "timestamp"
  }
  ```

## Agent API

### 获取 Agent 列表
- **GET** `/api/v1/agents`
- **描述**: 获取当前用户的所有 Agent
- **认证**: Bearer Token
- **参数**:
  - `page` (integer, 可选, 默认: 1)
  - `size` (integer, 可选, 默认: 20)
  - `search` (string, 可选)
- **响应**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "uuid",
        "name": "string",
        "slug": "string",
        "description": "string",
        "model_name": "string",
        "enabled_tools": ["string"],
        "enabled_skills": ["string"],
        "is_active": true,
        "created_at": "timestamp"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 10
    }
  }
  ```

### 创建 Agent
- **POST** `/api/v1/agents`
- **描述**: 创建新的 AI Agent
- **认证**: Bearer Token
- **请求体**:
  ```json
  {
    "name": "string",
    "slug": "string",
    "description": "string",
    "model_name": "string",
    "enabled_tools": ["string"],
    "enabled_skills": ["string"],
    "is_active": true
  }
  ```
- **响应**:
  ```json
  {
    "id": "uuid",
    "name": "string",
    "slug": "string",
    "description": "string",
    "model_name": "string",
    "enabled_tools": ["string"],
    "enabled_skills": ["string"],
    "is_active": true,
    "created_at": "timestamp",
    "updated_at": "timestamp"
  }
  ```

### 获取 Agent 详情
- **GET** `/api/v1/agents/{agent_id}`
- **描述**: 获取指定 Agent 的详细信息
- **认证**: Bearer Token
- **响应**:
  ```json
  {
    "id": "uuid",
    "name": "string",
    "slug": "string",
    "description": "string",
    "model_name": "string",
    "enabled_tools": ["string"],
    "enabled_skills": ["string"],
    "is_active": true,
    "created_at": "timestamp",
    "updated_at": "timestamp",
    "usage_stats": {
      "total_conversations": 150,
      "last_used": "timestamp"
    }
  }
  ```

### 更新 Agent
- **PUT** `/api/v1/agents/{agent_id}`
- **描述**: 更新 Agent 信息
- **认证**: Bearer Token
- **请求体**:
  ```json
  {
    "name": "string",
    "description": "string",
    "model_name": "string",
    "enabled_tools": ["string"],
    "enabled_skills": ["string"],
    "is_active": true
  }
  ```
- **响应**:
  ```json
  {
    "id": "uuid",
    "name": "string",
    "slug": "string",
    "description": "string",
    "model_name": "string",
    "enabled_tools": ["string"],
    "enabled_skills": ["string"],
    "is_active": true,
    "created_at": "timestamp",
    "updated_at": "timestamp"
  }
  ```

### 删除 Agent
- **DELETE** `/api/v1/agents/{agent_id}`
- **描述**: 删除指定 Agent
- **认证**: Bearer Token
- **响应**:
  ```json
  {
    "message": "Agent deleted successfully"
  }
  ```

## 对话 API

### 获取对话列表
- **GET** `/api/v1/threads`
- **描述**: 获取当前用户的所有对话线程
- **认证**: Bearer Token
- **参数**:
  - `page` (integer, 可选, 默认: 1)
  - `size` (integer, 可选, 默认: 20)
  - `agent_id` (string, 可选)
- **响应**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "uuid",
        "title": "string",
        "agent_id": "uuid",
        "status": "active|archived|pending",
        "message_count": 10,
        "created_at": "timestamp",
        "updated_at": "timestamp"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 50
    }
  }
  ```

### 创建对话
- **POST** `/api/v1/threads`
- **描述**: 创建新的对话线程
- **认证**: Bearer Token
- **请求体**:
  ```json
  {
    "title": "string",
    "agent_id": "uuid",
    "initial_message": "string" (可选)
  }
  ```
- **响应**:
  ```json
  {
    "id": "uuid",
    "title": "string",
    "agent_id": "uuid",
    "status": "active",
    "message_count": 0,
    "created_at": "timestamp",
    "updated_at": "timestamp"
  }
  ```

### 获取对话详情
- **GET** `/api/v1/threads/{thread_id}`
- **描述**: 获取指定对话的详细信息及消息历史
- **认证**: Bearer Token
- **响应**:
  ```json
  {
    "id": "uuid",
    "title": "string",
    "agent_id": "uuid",
    "status": "active|archived|pending",
    "message_count": 10,
    "created_at": "timestamp",
    "updated_at": "timestamp",
    "messages": [
      {
        "id": "uuid",
        "role": "user|assistant|system",
        "content": "string",
        "created_at": "timestamp"
      }
    ]
  }
  ```

### 更新对话
- **PUT** `/api/v1/threads/{thread_id}`
- **描述**: 更新对话信息
- **认证**: Bearer Token
- **请求体**:
  ```json
  {
    "title": "string",
    "status": "active|archived|pending"
  }
  ```
- **响应**:
  ```json
  {
    "id": "uuid",
    "title": "string",
    "agent_id": "uuid",
    "status": "active|archived|pending",
    "updated_at": "timestamp"
  }
  ```

### 删除对话
- **DELETE** `/api/v1/threads/{thread_id}`
- **描述**: 删除指定对话
- **认证**: Bearer Token
- **响应**:
  ```json
  {
    "message": "Thread deleted successfully"
  }
  ```

### 添加消息到对话
- **POST** `/api/v1/threads/{thread_id}/messages`
- **描述**: 向指定对话添加新消息
- **认证**: Bearer Token
- **请求体**:
  ```json
  {
    "content": "string",
    "role": "user|assistant|system"
  }
  ```
- **响应**:
  ```json
  {
    "id": "uuid",
    "content": "string",
    "role": "user|assistant|system",
    "created_at": "timestamp"
  }
  ```

## 任务 API

### 获取任务列表
- **GET** `/api/v1/tasks`
- **描述**: 获取当前用户的所有任务
- **认证**: Bearer Token
- **参数**:
  - `page` (integer, 可选, 默认: 1)
  - `size` (integer, 可选, 默认: 20)
  - `status` (string, 可选: pending, in_progress, completed, failed)
- **响应**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "uuid",
        "name": "string",
        "task_type": "string",
        "status": "pending|in_progress|completed|failed",
        "progress": 0-100,
        "parameters": {},
        "result": "any",
        "error": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 25
    }
  }
  ```

### 创建任务
- **POST** `/api/v1/tasks`
- **描述**: 创建新任务
- **认证**: Bearer Token
- **请求体**:
  ```json
  {
    "name": "string",
    "task_type": "string",
    "parameters": {}
  }
  ```
- **响应**:
  ```json
  {
    "id": "uuid",
    "name": "string",
    "task_type": "string",
    "status": "pending",
    "progress": 0,
    "parameters": {},
    "created_at": "timestamp",
    "updated_at": "timestamp"
  }
  ```

### 获取任务详情
- **GET** `/api/v1/tasks/{task_id}`
- **描述**: 获取指定任务的详细信息
- **认证**: Bearer Token
- **响应**:
  ```json
  {
    "id": "uuid",
    "name": "string",
    "task_type": "string",
    "status": "pending|in_progress|completed|failed",
    "progress": 0-100,
    "parameters": {},
    "result": "any",
    "error": "string",
    "created_at": "timestamp",
    "updated_at": "timestamp",
    "execution_log": [
      {
        "level": "info|warning|error",
        "message": "string",
        "timestamp": "timestamp"
      }
    ]
  }
  ```

### 更新任务状态
- **PUT** `/api/v1/tasks/{task_id}/status`
- **描述**: 更新任务状态
- **认证**: Bearer Token
- **请求体**:
  ```json
  {
    "status": "pending|in_progress|completed|failed",
    "progress": 0-100,
    "result": "any" (可选),
    "error": "string" (可选)
  }
  ```
- **响应**:
  ```json
  {
    "id": "uuid",
    "status": "pending|in_progress|completed|failed",
    "progress": 0-100,
    "updated_at": "timestamp"
  }
  ```

## 记忆 API

### 获取记忆列表
- **GET** `/api/v1/memory`
- **描述**: 获取当前用户的所有记忆记录
- **认证**: Bearer Token
- **参数**:
  - `page` (integer, 可选, 默认: 1)
  - `size` (integer, 可选, 默认: 20)
  - `category` (string, 可选)
  - `search` (string, 可选)
- **响应**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "uuid",
        "title": "string",
        "content": "string",
        "category": "string",
        "tags": ["string"],
        "user_id": "uuid",
        "created_at": "timestamp",
        "updated_at": "timestamp"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 100
    }
  }
  ```

### 创建记忆
- **POST** `/api/v1/memory`
- **描述**: 创建新的记忆记录
- **认证**: Bearer Token
- **请求体**:
  ```json
  {
    "title": "string",
    "content": "string",
    "category": "string",
    "tags": ["string"]
  }
  ```
- **响应**:
  ```json
  {
    "id": "uuid",
    "title": "string",
    "content": "string",
    "category": "string",
    "tags": ["string"],
    "user_id": "uuid",
    "created_at": "timestamp",
    "updated_at": "timestamp"
  }
  ```

### 搜索记忆
- **GET** `/api/v1/memory/search`
- **描述**: 搜索匹配的记忆记录
- **认证**: Bearer Token
- **参数**:
  - `q` (string, 必需)
  - `limit` (integer, 可选, 默认: 10)
- **响应**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "uuid",
        "title": "string",
        "content": "string",
        "category": "string",
        "similarity": 0.0-1.0
      }
    ]
  }
  ```

### 获取用户上下文
- **GET** `/api/v1/memory/context`
- **描述**: 获取当前用户的上下文记忆
- **认证**: Bearer Token
- **参数**:
  - `limit` (integer, 可选, 默认: 10)
  - `categories` (string[], 可选)
- **响应**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "uuid",
        "title": "string",
        "content": "string",
        "category": "string",
        "relevance_score": 0.0-1.0
      }
    ]
  }
  ```

## 错误处理

所有 API 端点在发生错误时都会返回标准的错误响应格式：

```json
{
  "success": false,
  "error": {
    "code": "string",
    "message": "string",
    "details": "any"
  }
}
```

常见的错误码包括：
- `AUTHENTICATION_REQUIRED` - 需要认证
- `PERMISSION_DENIED` - 权限不足
- `VALIDATION_ERROR` - 请求参数验证失败
- `RESOURCE_NOT_FOUND` - 资源未找到
- `INTERNAL_ERROR` - 内部服务器错误