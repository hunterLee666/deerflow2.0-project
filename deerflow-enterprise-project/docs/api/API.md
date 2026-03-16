# API Documentation

## Overview

This document describes the REST API for the Enterprise AI Agent System.

## Authentication

All API endpoints require authentication via JWT tokens.

### Obtain Token

```
POST /api/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Use Token

Include the token in the Authorization header:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Agent Endpoints

### Chat with Agent

```
POST /api/agents/chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Hello, how can you help me?",
  "thread_id": "optional-thread-id"
}
```

Response:
```json
{
  "response": "Hello! I can help you with various tasks...",
  "thread_id": "thread-123"
}
```

### Stream Agent Response

```
POST /api/agents/stream
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Generate a complex analysis",
  "thread_id": "optional-thread-id"
}
```

Response (Server-Sent Events):
```
data: {"type": "text", "content": "Analyzing your request..."}

data: {"type": "tool_call", "name": "web_search", "input": {"query": "market trends"}}

data: {"type": "tool_result", "name": "web_search", "result": "Found 10 relevant articles"}

data: {"type": "text", "content": "Based on my analysis..."}

data: {"type": "end"}
```

### Get Agent Status

```
GET /api/agents/status
Authorization: Bearer <token>
```

Response:
```json
{
  "status": "ready",
  "active_threads": 5,
  "queue_length": 0
}
```

## Task Endpoints

### Create Task

```
POST /api/tasks
Authorization: Bearer <token>
Content-Type: application/json

{
  "description": "Analyze sales data",
  "priority": "medium",
  "deadline": "2026-12-31T23:59:59Z"
}
```

Response:
```json
{
  "task_id": "task-123",
  "status": "queued"
}
```

### Get Task Status

```
GET /api/tasks/{task_id}
Authorization: Bearer <token>
```

Response:
```json
{
  "task_id": "task-123",
  "description": "Analyze sales data",
  "status": "completed",
  "result": "Sales increased by 15% this quarter",
  "created_at": "2026-01-01T10:00:00Z",
  "completed_at": "2026-01-01T10:05:00Z"
}
```

### List Tasks

```
GET /api/tasks
Authorization: Bearer <token>
Query Parameters:
- status: Filter by status (optional)
- limit: Number of tasks to return (default: 10)
- offset: Offset for pagination (default: 0)
```

Response:
```json
{
  "tasks": [
    {
      "task_id": "task-123",
      "description": "Analyze sales data",
      "status": "completed",
      "created_at": "2026-01-01T10:00:00Z"
    }
  ],
  "total": 1
}
```

## Memory Endpoints

### Store Memory

```
POST /api/memory
Authorization: Bearer <token>
Content-Type: application/json

{
  "key": "user_preference",
  "value": {"theme": "dark", "language": "en"},
  "ttl": 86400
}
```

Response:
```json
{
  "success": true
}
```

### Retrieve Memory

```
GET /api/memory/{key}
Authorization: Bearer <token>
```

Response:
```json
{
  "key": "user_preference",
  "value": {"theme": "dark", "language": "en"},
  "expires_at": "2026-01-02T10:00:00Z"
}
```

### List Memories

```
GET /api/memory
Authorization: Bearer <token>
Query Parameters:
- prefix: Filter by key prefix (optional)
- limit: Number of items to return (default: 10)
```

Response:
```json
{
  "memories": [
    {
      "key": "user_preference",
      "value": {"theme": "dark", "language": "en"},
      "expires_at": "2026-01-02T10:00:00Z"
    }
  ]
}
```

## Skill Endpoints

### List Skills

```
GET /api/skills
Authorization: Bearer <token>
```

Response:
```json
{
  "skills": [
    {
      "name": "web_research",
      "description": "Perform web research on given topics",
      "version": "1.0.0",
      "enabled": true
    }
  ]
}
```

### Enable/Disable Skill

```
PUT /api/skills/{skill_name}
Authorization: Bearer <token>
Content-Type: application/json

{
  "enabled": true
}
```

Response:
```json
{
  "success": true
}
```

## Tool Endpoints

### List Tools

```
GET /api/tools
Authorization: Bearer <token>
```

Response:
```json
{
  "tools": [
    {
      "name": "web_search",
      "description": "Search the web for information",
      "category": "research"
    }
  ]
}
```

### Execute Tool

```
POST /api/tools/execute
Authorization: Bearer <token>
Content-Type: application/json

{
  "tool_name": "web_search",
  "parameters": {
    "query": "latest AI developments"
  }
}
```

Response:
```json
{
  "result": "Latest developments in AI include..."
}
```

## Error Responses

All endpoints may return the following error responses:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid request parameters",
    "details": "Missing required field: message"
  }
}
```

Common error codes:
- `INVALID_REQUEST`: Malformed request
- `UNAUTHORIZED`: Missing or invalid authentication
- `FORBIDDEN`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `INTERNAL_ERROR`: Server error