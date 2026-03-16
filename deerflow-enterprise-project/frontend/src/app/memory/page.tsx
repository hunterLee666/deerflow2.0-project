'use client';

import { useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Search, Brain, Clock, Star, Trash2, Download } from 'lucide-react';

interface MemoryEntry {
  id: string;
  type: 'fact' | 'preference' | 'context' | 'summary';
  content: string;
  agent: string;
  importance: number;
  createdAt: string;
  accessCount: number;
}

const mockMemories: MemoryEntry[] = [
  {
    id: '1',
    type: 'fact',
    content: 'User prefers Python for data analysis tasks',
    agent: 'Research Assistant',
    importance: 8,
    createdAt: '2026-03-10T10:00:00Z',
    accessCount: 15,
  },
  {
    id: '2',
    type: 'preference',
    content: 'User likes concise responses with bullet points',
    agent: 'All Agents',
    importance: 9,
    createdAt: '2026-03-08T14:00:00Z',
    accessCount: 42,
  },
  {
    id: '3',
    type: 'context',
    content: 'Current project: AI-powered analytics dashboard',
    agent: 'Code Assistant',
    importance: 7,
    createdAt: '2026-03-15T09:00:00Z',
    accessCount: 8,
  },
  {
    id: '4',
    type: 'summary',
    content: 'Previous conversation summarized: User is building an enterprise AI system',
    agent: 'System',
    importance: 6,
    createdAt: '2026-03-14T16:00:00Z',
    accessCount: 5,
  },
];

const typeColors = {
  fact: 'bg-blue-500',
  preference: 'bg-green-500',
  context: 'bg-yellow-500',
  summary: 'bg-purple-500',
};

export default function MemoryPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [memories] = useState<MemoryEntry[]>(mockMemories);

  const filteredMemories = memories.filter(
    (m) =>
      m.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.agent.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getImportanceStars = (importance: number) => {
    return Array(5)
      .fill(0)
      .map((_, i) => (
        <Star
          key={i}
          className={`h-3 w-3 ${
            i < importance / 2 ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
          }`}
        />
      ));
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Memory</h1>
            <p className="text-muted-foreground">
              Browse and manage your agents&apos; learned knowledge.
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline">
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
          </div>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search memories..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Memory Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Entries</CardTitle>
              <Brain className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{memories.length}</div>
            </CardContent>
          </Card>
          {Object.entries(typeColors).map(([type, color]) => {
            const count = memories.filter((m) => m.type === type).length;
            return (
              <Card key={type}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium capitalize">
                    {type}s
                  </CardTitle>
                  <div className={`h-2 w-2 rounded-full ${color}`} />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{count}</div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Memory Tabs */}
        <Tabs defaultValue="all" className="space-y-4">
          <TabsList>
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="fact">Facts</TabsTrigger>
            <TabsTrigger value="preference">Preferences</TabsTrigger>
            <TabsTrigger value="context">Context</TabsTrigger>
            <TabsTrigger value="summary">Summaries</TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>All Memories</CardTitle>
                <CardDescription>
                  Complete list of learned information.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {filteredMemories.map((memory) => (
                    <div
                      key={memory.id}
                      className="p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge className={typeColors[memory.type]}>
                              {memory.type}
                            </Badge>
                            <span className="text-sm text-muted-foreground">
                              {memory.agent}
                            </span>
                          </div>
                          <p className="text-sm">{memory.content}</p>
                          <div className="flex items-center gap-4 mt-3 text-xs text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {new Date(memory.createdAt).toLocaleDateString()}
                            </div>
                            <div className="flex items-center gap-1">
                              <span>Accessed {memory.accessCount} times</span>
                            </div>
                            <div className="flex items-center gap-0.5">
                              Importance:
                              {getImportanceStars(memory.importance)}
                            </div>
                          </div>
                        </div>
                        <Button variant="ghost" size="icon" className="text-red-500">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {['fact', 'preference', 'context', 'summary'].map((type) => (
            <TabsContent key={type} value={type} className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="capitalize">{type}s</CardTitle>
                  <CardDescription>
                    {type === 'fact' && 'Factual information learned by agents.'}
                    {type === 'preference' && 'User preferences and settings.'}
                    {type === 'context' && 'Contextual information for conversations.'}
                    {type === 'summary' && 'Summarized conversation content.'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {filteredMemories
                      .filter((m) => m.type === type)
                      .map((memory) => (
                        <div
                          key={memory.id}
                          className="p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <span className="text-sm text-muted-foreground">
                                  {memory.agent}
                                </span>
                              </div>
                              <p className="text-sm">{memory.content}</p>
                              <div className="flex items-center gap-4 mt-3 text-xs text-muted-foreground">
                                <div className="flex items-center gap-1">
                                  <Clock className="h-3 w-3" />
                                  {new Date(memory.createdAt).toLocaleDateString()}
                                </div>
                                <div className="flex items-center gap-0.5">
                                  Importance:
                                  {getImportanceStars(memory.importance)}
                                </div>
                              </div>
                            </div>
                            <Button variant="ghost" size="icon" className="text-red-500">
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          ))}
        </Tabs>
      </div>
    </MainLayout>
  );
}
