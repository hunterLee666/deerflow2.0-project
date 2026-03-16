import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Loader2, Plus } from 'lucide-react';
import { useAgentList } from '@/lib/api/agents';
import Link from 'next/link';

export default function AgentList() {
  const { data: agents, isLoading, error } = useAgentList();

  if (error) {
    return (
      <div className="text-red-500">
        Error loading agents: {(error as Error).message}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Agent Management</h1>
        <Button asChild>
          <Link href="/agents/new">
            <Plus className="mr-2 h-4 w-4" /> Create Agent
          </Link>
        </Button>
      </div>

      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      ) : agents && agents.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <Card key={agent.id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle>{agent.name}</CardTitle>
                    <CardDescription>{agent.description}</CardDescription>
                  </div>
                  <Badge
                    variant={
                      agent.status === 'online'
                        ? 'default'
                        : agent.status === 'busy'
                          ? 'secondary'
                          : 'outline'
                    }
                  >
                    {agent.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {agent.capabilities.map((capability) => (
                    <Badge key={capability} variant="outline">
                      {capability}
                    </Badge>
                  ))}
                </div>
                <div className="mt-4">
                  <Button asChild className="w-full">
                    <Link href={`/conversations?agent=${agent.id}`}>Start Conversation</Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-500">No agents available. Create your first agent to get started.</p>
        </div>
      )}
    </div>
  );
}