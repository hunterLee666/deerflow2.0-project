'use client';

import { useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import Link from 'next/link';
import ChatInterface from '@/components/conversations/ChatInterface';
import MainLayout from '@/components/layout/MainLayout';

export default function ConversationsPage() {
  const searchParams = useSearchParams();
  const agentId = searchParams.get('agent');

  if (!agentId) {
    return (
      <MainLayout>
        <div className="container mx-auto p-4 max-w-2xl">
          <Card>
            <CardHeader>
              <CardTitle>Select an Agent</CardTitle>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertDescription>
                  No agent selected. Please choose an agent to start a conversation.
                </AlertDescription>
              </Alert>
              <div className="mt-6 flex justify-center">
                <Button asChild>
                  <Link href="/agents">
                    Browse Available Agents
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <main className="container mx-auto p-4 max-w-4xl">
        <h1 className="text-2xl font-bold mb-6">Agent Conversation</h1>
        <ChatInterface agentId={agentId} />
      </main>
    </MainLayout>
  );
}
