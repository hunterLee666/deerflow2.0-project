# 前端 API 集成文档

本文档描述了前端如何与后端 API 进行集成。

## 🚀 快速开始

### 安装依赖

```bash
cd frontend
npm install axios
# 或使用其他 HTTP 客户端库
```

### 基础 API 配置

```typescript
// lib/api.ts
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加认证令牌
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器 - 处理认证过期
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 清除本地存储的令牌
      localStorage.removeItem('access_token');
      // 重定向到登录页
      window.location.href = '/auth/login';
    }
    return Promise.reject(error);
  }
);
```

## 🔐 认证 API 集成

### 登录

```typescript
// lib/auth.ts
interface LoginCredentials {
  username: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export const login = async (credentials: LoginCredentials): Promise<LoginResponse> => {
  const response = await api.post('/auth/login', credentials);
  // 存储令牌
  localStorage.setItem('access_token', response.data.access_token);
  return response.data;
};
```

### 注册

```typescript
interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name: string;
}

export const register = async (data: RegisterData): Promise<User> => {
  const response = await api.post('/auth/register', data);
  return response.data;
};
```

### 获取当前用户

```typescript
export const getCurrentUser = async (): Promise<User> => {
  const response = await api.get('/auth/me');
  return response.data;
};
```

## 👤 用户 API 集成

### 获取用户列表（管理员）

```typescript
interface PaginationParams {
  page?: number;
  size?: number;
}

export const getUsers = async (params: PaginationParams = {}) => {
  const response = await api.get('/auth/users', { params });
  return response.data;
};
```

### 更新用户信息

```typescript
interface UpdateUserData {
  full_name?: string;
  username?: string;
}

export const updateUser = async (data: UpdateUserData) => {
  const response = await api.put('/auth/me', data);
  return response.data;
};
```

## 🤖 Agent API 集成

### 获取 Agent 列表

```typescript
interface AgentFilters {
  page?: number;
  size?: number;
  search?: string;
}

export const getAgents = async (filters: AgentFilters = {}) => {
  const response = await api.get('/agents', { params: filters });
  return response.data;
};
```

### 创建 Agent

```typescript
interface CreateAgentData {
  name: string;
  slug: string;
  description: string;
  model_name: string;
  enabled_tools: string[];
  enabled_skills: string[];
  is_active?: boolean;
}

export const createAgent = async (data: CreateAgentData) => {
  const response = await api.post('/agents', data);
  return response.data;
};
```

### 更新 Agent

```typescript
interface UpdateAgentData {
  name?: string;
  description?: string;
  model_name?: string;
  enabled_tools?: string[];
  enabled_skills?: string[];
  is_active?: boolean;
}

export const updateAgent = async (agentId: string, data: UpdateAgentData) => {
  const response = await api.put(`/agents/${agentId}`, data);
  return response.data;
};

export const deleteAgent = async (agentId: string) => {
  const response = await api.delete(`/agents/${agentId}`);
  return response.data;
};
```

## 💬 对话 API 集成

### 获取对话列表

```typescript
interface ThreadFilters {
  page?: number;
  size?: number;
  agent_id?: string;
}

export const getThreads = async (filters: ThreadFilters = {}) => {
  const response = await api.get('/threads', { params: filters });
  return response.data;
};
```

### 创建对话

```typescript
interface CreateThreadData {
  title: string;
  agent_id: string;
  initial_message?: string;
}

export const createThread = async (data: CreateThreadData) => {
  const response = await api.post('/threads', data);
  return response.data;
};

export const getThread = async (threadId: string) => {
  const response = await api.get(`/threads/${threadId}`);
  return response.data;
};
```

## 📋 任务 API 集成

### 获取任务列表

```typescript
interface TaskFilters {
  page?: number;
  size?: number;
  status?: string;
}

export const getTasks = async (filters: TaskFilters = {}) => {
  const response = await api.get('/tasks', { params: filters });
  return response.data;
};
```

### 创建任务

```typescript
interface CreateTaskData {
  name: string;
  task_type: string;
  parameters: Record<string, any>;
}

export const createTask = async (data: CreateTaskData) => {
  const response = await api.post('/tasks', data);
  return response.data;
};

export const getTask = async (taskId: string) => {
  const response = await api.get(`/tasks/${taskId}`);
  return response.data;
};
```

## 🧠 记忆 API 集成

### 获取记忆列表

```typescript
interface MemoryFilters {
  page?: number;
  size?: number;
  category?: string;
  search?: string;
}

export const getMemories = async (filters: MemoryFilters = {}) => {
  const response = await api.get('/memory', { params: filters });
  return response.data;
};
```

### 创建记忆

```typescript
interface CreateMemoryData {
  title: string;
  content: string;
  category: string;
  tags: string[];
}

export const createMemory = async (data: CreateMemoryData) => {
  const response = await api.post('/memory', data);
  return response.data;
};

export const searchMemories = async (query: string) => {
  const response = await api.get('/memory/search', { params: { q: query } });
  return response.data;
};
```

## ⚡ 使用 React Query 进行状态管理

```typescript
// hooks/useAgents.ts
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { getAgents, createAgent, updateAgent, deleteAgent } from '@/lib/agents';

export const useAgents = (filters = {}) => {
  return useQuery(['agents', filters], () => getAgents(filters), {
    staleTime: 5 * 60 * 1000, // 5分钟
  });
};

export const useCreateAgent = () => {
  const queryClient = useQueryClient();

  return useMutation(createAgent, {
    onSuccess: () => {
      queryClient.invalidateQueries('agents');
    },
  });
};

export const useUpdateAgent = () => {
  const queryClient = useQueryClient();

  return useMutation(({ agentId, data }) => updateAgent(agentId, data), {
    onSuccess: () => {
      queryClient.invalidateQueries('agents');
      queryClient.invalidateQueries(['agent', agentId]); // 如果有的话
    },
  });
};
```

## 📦 完整示例

```typescript
// components/AgentList.tsx
'use client';

import { useState, useEffect } from 'react';
import { useAgents, useCreateAgent } from '@/hooks/useAgents';

const AgentList = () => {
  const { data: agents, isLoading, isError, refetch } = useAgents();
  const createAgentMutation = useCreateAgent();

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    model_name: 'gpt-4'
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createAgentMutation.mutateAsync(formData);
      setFormData({ name: '', description: '', model_name: 'gpt-4' });
    } catch (error) {
      console.error('Failed to create agent:', error);
    }
  };

  if (isLoading) return <div>Loading agents...</div>;
  if (isError) return <div>Error loading agents</div>;

  return (
    <div>
      <h2>AI Agents</h2>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Agent Name"
          value={formData.name}
          onChange={(e) => setFormData({...formData, name: e.target.value})}
          required
        />
        <textarea
          placeholder="Description"
          value={formData.description}
          onChange={(e) => setFormData({...formData, description: e.target.value})}
        />
        <select
          value={formData.model_name}
          onChange={(e) => setFormData({...formData, model_name: e.target.value})}
        >
          <option value="gpt-4">GPT-4</option>
          <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
        </select>
        <button type="submit" disabled={createAgentMutation.isLoading}>
          {createAgentMutation.isLoading ? 'Creating...' : 'Create Agent'}
        </button>
      </form>

      <ul>
        {agents?.data.map((agent) => (
          <li key={agent.id}>
            <h3>{agent.name}</h3>
            <p>{agent.description}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default AgentList;
```

## 🛡️ 错误处理最佳实践

```typescript
// lib/errorHandler.ts
import { AxiosError } from 'axios';

export interface APIError {
  success: boolean;
  error: {
    code: string;
    message: string;
    details?: any;
  };
}

export const handleAPIError = (error: AxiosError<APIError>) => {
  if (error.response) {
    // 服务器响应了错误状态码
    const { data } = error.response;
    console.error(`API Error: ${data.error.code} - ${data.error.message}`);
    return data.error.message;
  } else if (error.request) {
    // 请求已发出但没有收到响应
    console.error('Network Error: No response received');
    return 'Network error. Please check your connection.';
  } else {
    // 其他错误
    console.error('Request Error:', error.message);
    return 'An unexpected error occurred.';
  }
};
```

## 📝 总结

- 使用统一的 API 客户端配置认证和其他公共头
- 利用 React Query 或 SWR 管理服务端状态
- 实现适当的错误处理和加载状态
- 遵循 TypeScript 类型安全最佳实践
- 在组件中合理利用自定义 hooks 封装 API 逻辑