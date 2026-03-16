'use client';

import MainLayout from '@/components/layout/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Bot, MessageSquare, ListTodo, Brain, ArrowRight, Plus } from 'lucide-react';
import Link from 'next/link';

const stats = [
  { name: 'Total Agents', value: '12', icon: Bot, href: '/agents' },
  { name: 'Active Conversations', value: '8', icon: MessageSquare, href: '/conversations' },
  { name: 'Pending Tasks', value: '24', icon: ListTodo, href: '/tasks' },
  { name: 'Memory Entries', value: '156', icon: Brain, href: '/memory' },
];

const recentActivity = [
  { id: 1, action: 'New conversation started', agent: 'Research Assistant', time: '2 minutes ago' },
  { id: 2, action: 'Task completed', agent: 'Code Reviewer', time: '15 minutes ago' },
  { id: 3, action: 'Agent updated', agent: 'Data Analyzer', time: '1 hour ago' },
  { id: 4, action: 'Memory consolidated', agent: 'System', time: '2 hours ago' },
];

export default function DashboardPage() {
  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-muted-foreground">
              Welcome back! Here&apos;s an overview of your AI agents and activities.
            </p>
          </div>
          <Button asChild>
            <Link href="/conversations">
              <Plus className="mr-2 h-4 w-4" />
              New Conversation
            </Link>
          </Button>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
            <Card key={stat.name}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.name}
                </CardTitle>
                <stat.icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <Link
                  href={stat.href}
                  className="text-xs text-muted-foreground hover:text-foreground inline-flex items-center mt-1"
                >
                  View all
                  <ArrowRight className="ml-1 h-3 w-3" />
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Main Content Grid */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {/* Quick Actions */}
          <Card className="col-span-1">
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Common tasks you can perform</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button variant="outline" className="w-full justify-start" asChild>
                <Link href="/agents">
                  <Bot className="mr-2 h-4 w-4" />
                  Manage Agents
                </Link>
              </Button>
              <Button variant="outline" className="w-full justify-start" asChild>
                <Link href="/conversations">
                  <MessageSquare className="mr-2 h-4 w-4" />
                  View Conversations
                </Link>
              </Button>
              <Button variant="outline" className="w-full justify-start" asChild>
                <Link href="/tasks">
                  <ListTodo className="mr-2 h-4 w-4" />
                  Check Tasks
                </Link>
              </Button>
              <Button variant="outline" className="w-full justify-start" asChild>
                <Link href="/memory">
                  <Brain className="mr-2 h-4 w-4" />
                  Browse Memory
                </Link>
              </Button>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card className="col-span-1 md:col-span-2">
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>Latest actions across your agents</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentActivity.map((activity) => (
                  <div
                    key={activity.id}
                    className="flex items-center justify-between border-b pb-4 last:border-0 last:pb-0"
                  >
                    <div>
                      <p className="font-medium">{activity.action}</p>
                      <p className="text-sm text-muted-foreground">
                        via {activity.agent}
                      </p>
                    </div>
                    <span className="text-sm text-muted-foreground">
                      {activity.time}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Getting Started */}
        <Card>
          <CardHeader>
            <CardTitle>Getting Started</CardTitle>
            <CardDescription>
              New to DeerFlow? Here are some resources to help you get started.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <h3 className="font-semibold">1. Create an Agent</h3>
                <p className="text-sm text-muted-foreground">
                  Set up your first AI agent with custom tools and skills.
                </p>
                <Button variant="link" className="p-0" asChild>
                  <Link href="/agents">Create Agent →</Link>
                </Button>
              </div>
              <div className="space-y-2">
                <h3 className="font-semibold">2. Start a Conversation</h3>
                <p className="text-sm text-muted-foreground">
                  Interact with your agents through natural language.
                </p>
                <Button variant="link" className="p-0" asChild>
                  <Link href="/conversations">Start Chat →</Link>
                </Button>
              </div>
              <div className="space-y-2">
                <h3 className="font-semibold">3. Explore Memory</h3>
                <p className="text-sm text-muted-foreground">
                  Review and manage your agents&apos; learned knowledge.
                </p>
                <Button variant="link" className="p-0" asChild>
                  <Link href="/memory">View Memory →</Link>
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
