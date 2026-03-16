'use client';

import { useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Plus, Play, Pause, RotateCcw, CheckCircle, Clock, AlertCircle } from 'lucide-react';

interface Task {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  agent: string;
  createdAt: string;
  progress?: number;
}

const mockTasks: Task[] = [
  {
    id: '1',
    name: 'Research AI Trends',
    description: 'Research the latest AI trends in 2026',
    status: 'running',
    agent: 'Research Assistant',
    createdAt: '2026-03-15T10:00:00Z',
    progress: 65,
  },
  {
    id: '2',
    name: 'Code Review',
    description: 'Review pull request #234',
    status: 'completed',
    agent: 'Code Reviewer',
    createdAt: '2026-03-15T09:00:00Z',
  },
  {
    id: '3',
    name: 'Data Analysis',
    description: 'Analyze Q1 sales data',
    status: 'pending',
    agent: 'Data Analyzer',
    createdAt: '2026-03-15T08:00:00Z',
  },
  {
    id: '4',
    name: 'Document Generation',
    description: 'Generate technical documentation',
    status: 'failed',
    agent: 'Writer Agent',
    createdAt: '2026-03-14T16:00:00Z',
  },
];

const statusConfig = {
  pending: { label: 'Pending', color: 'bg-yellow-500', icon: Clock },
  running: { label: 'Running', color: 'bg-blue-500', icon: Play },
  completed: { label: 'Completed', color: 'bg-green-500', icon: CheckCircle },
  failed: { label: 'Failed', color: 'bg-red-500', icon: AlertCircle },
};

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>(mockTasks);

  const handleAction = (taskId: string, action: 'run' | 'pause' | 'retry') => {
    setTasks(tasks.map(task => {
      if (task.id === taskId) {
        switch (action) {
          case 'run':
            return { ...task, status: 'running' };
          case 'pause':
            return { ...task, status: 'pending' };
          case 'retry':
            return { ...task, status: 'running', progress: 0 };
          default:
            return task;
        }
      }
      return task;
    }));
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Tasks</h1>
            <p className="text-muted-foreground">
              Manage and monitor your agent tasks.
            </p>
          </div>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New Task
          </Button>
        </div>

        {/* Task Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          {Object.entries(statusConfig).map(([status, config]) => {
            const count = tasks.filter(t => t.status === status).length;
            return (
              <Card key={status}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    {config.label}
                  </CardTitle>
                  <config.icon className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{count}</div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Tasks List */}
        <Card>
          <CardHeader>
            <CardTitle>All Tasks</CardTitle>
            <CardDescription>
              A list of all tasks across your agents.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {tasks.map((task) => {
                const status = statusConfig[task.status];
                return (
                  <div
                    key={task.id}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold">{task.name}</h3>
                        <Badge className={status.color}>
                          {status.label}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">
                        {task.description}
                      </p>
                      <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                        <span>Agent: {task.agent}</span>
                        <span>Created: {new Date(task.createdAt).toLocaleString()}</span>
                      </div>
                      {task.status === 'running' && task.progress !== undefined && (
                        <div className="mt-2">
                          <div className="h-2 bg-gray-200 rounded-full">
                            <div
                              className="h-2 bg-blue-500 rounded-full transition-all"
                              style={{ width: `${task.progress}%` }}
                            />
                          </div>
                          <span className="text-xs text-muted-foreground">
                            {task.progress}%
                          </span>
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      {task.status === 'pending' && (
                        <Button
                          size="sm"
                          onClick={() => handleAction(task.id, 'run')}
                        >
                          <Play className="h-4 w-4" />
                        </Button>
                      )}
                      {task.status === 'running' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAction(task.id, 'pause')}
                        >
                          <Pause className="h-4 w-4" />
                        </Button>
                      )}
                      {task.status === 'failed' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAction(task.id, 'retry')}
                        >
                          <RotateCcw className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
